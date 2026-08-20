import asyncio
from typing import Callable

from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call, wrap_tool_call
from langchain_core.messages import SystemMessage, ToolMessage

from backend.core.config import settings
from backend.core.llm import get_canonical_model_id, get_model_by_choice
from backend.runtime.conversation_memory import maybe_compact_conversation
from backend.runtime.context_builder import build_runtime_context
from backend.runtime.tool_registry import get_runtime_tools, get_tool_names
from backend.services.tool_context import (
    append_tool_trace,
    get_guard_fired,
    get_tool_call_history,
    record_tool_call,
    set_guard_fired,
)
from backend.runtime.budget import (
    consume_model_call_if_active,
    consume_tool_call_if_active,
    record_model_response_usage,
)
from backend.services.retrieval_usage_service import RetrievalUsageError


"""
Middleware 设计说明：
  runtime 不是一个“单独的大对象”，而是一层能力编排：
  - context_builder：决定当前请求要收集哪些上下文原材料
  - prompt_manager：决定这些原材料最终怎么拼成 prompt
  - middleware：把 runtime 生成的动态 prompt 真正接到每一次 LLM 调用前

  因此关系是：
    agent_service.create_agent(...)
      -> 注册 wrap_model_call middleware
      -> middleware 在每次模型调用前调用 build_runtime_context(...)
      -> build_runtime_context(...) 查询长期记忆 / markdown memory / skills
      -> prompt_manager 拼出动态 system prompt
      -> middleware 把它追加到基础 system prompt 后面一起发给 LLM

  好处：
    ✓ ReAct 主循环每一轮都会拿到最新上下文
    ✓ PAE 子流程复用同一套 runtime 逻辑
    ✓ service 层不用手写 prompt 拼接
"""


@wrap_tool_call
async def handle_tool_errors(request, handler):
    try:
        return await handler(request)
    except RetrievalUsageError as exc:
        return ToolMessage(
            content=f"检索服务已停止：{exc.message}",
            tool_call_id=request.tool_call["id"],
        )
    except Exception:
        return ToolMessage(
            content="工具调用失败，请换个方式提问或跳过此步骤。",
            tool_call_id=request.tool_call["id"],
        )


@wrap_tool_call
async def record_tool_call_mw(request, handler):
    """把每次 tool 调用的签名写入 per-request 历史，供 loop_guard 读。"""
    tool_name = ""
    try:
        tool_call = request.tool_call
        tool_name = tool_call.get("name") if isinstance(tool_call, dict) else getattr(tool_call, "name", "")
        tool_args = tool_call.get("args") if isinstance(tool_call, dict) else getattr(tool_call, "args", {})
        if tool_name:
            record_tool_call(tool_name, tool_args)
    except Exception:
        pass
    if tool_name:
        await consume_tool_call_if_active()
    return await handler(request)


@wrap_model_call
async def enforce_model_budget(request: ModelRequest, handler: Callable) -> ModelResponse:
    call_index = await consume_model_call_if_active()
    response = await asyncio.wait_for(handler(request), timeout=settings.MODEL_CALL_TIMEOUT_SECONDS)
    if call_index is not None and response.result:
        model_id = get_canonical_model_id(request.state.get("model_choice", "deepseek-v4-flash"))
        await record_model_response_usage(
            model_id=model_id,
            prompt=[request.system_message, *request.messages],
            response=response.result[-1],
            call_index=call_index,
        )
    return response


def _detect_guard_phase(history: list[dict]) -> tuple[str, str] | None:
    """返回 (phase, reason) 或 None。"""
    if not history:
        return None
    total = len(history)
    if total > max(settings.REACT_MAX_TOOL_CALLS, 1):
        return (
            "budget_exceeded",
            f"工具调用已达上限 {settings.REACT_MAX_TOOL_CALLS} 次。",
        )
    threshold = max(settings.LOOP_GUARD_REPEAT_THRESHOLD, 2)
    if total >= threshold:
        tail = history[-threshold:]
        first = tail[0]
        same_tool = all(item.get("tool") == first.get("tool") for item in tail)
        same_args = all(item.get("args_hash") == first.get("args_hash") for item in tail)
        if same_tool and same_args:
            return (
                "repeat_detected",
                f"连续 {threshold} 次以相同参数调用 {first.get('tool')}。",
            )
    return None


_GUARD_DIRECTIVES = {
    "repeat_detected": (
        "【循环守卫】你刚刚重复以相同参数调用了同一个工具多次且没有获得新信息。"
        "立即停止再调用任何工具，直接基于已掌握的信息给出最终答案，"
        "如果信息不足则明确告知用户缺少什么，并建议下一步如何提供。"
    ),
    "budget_exceeded": (
        "【循环守卫】本轮工具调用次数已达上限。"
        "不要再调用任何工具，立即基于已有信息给出最终答案；"
        "如果尚未得到结论，请坦诚说明并给出后续建议。"
    ),
}


@wrap_model_call
async def loop_guard(
    request: ModelRequest,
    handler: Callable,
) -> ModelResponse:
    """检测重复工具调用 / 预算超限，注入强制收敛指令。"""
    already = get_guard_fired()
    history = get_tool_call_history()
    print(f"🔍 [loop_guard] already={already!r}, history_len={len(history)}, history={history[-5:]}")
    phase_reason = _detect_guard_phase(history) if not already else None
    if phase_reason is not None or already:
        phase = phase_reason[0] if phase_reason is not None else already
        reason = phase_reason[1] if phase_reason is not None else "守卫已触发"
        if phase_reason is not None:
            set_guard_fired(phase)
            append_tool_trace(f"🛑 [循环守卫] {reason} 已强制收敛。")
        directive = _GUARD_DIRECTIVES.get(phase, _GUARD_DIRECTIVES["repeat_detected"])
        messages = list(request.messages)
        messages.append(SystemMessage(content=directive))
        updated_state = {
            **request.state,
            "fsm_phase": "abort_with_summary",
            "guard_reason": reason,
            # bind_selected_model 读这个 flag 后会绑定空工具集，
            # 物理上杜绝模型在后续轮次再调工具
            "guard_disable_tools": True,
        }
        request = request.override(messages=messages, state=updated_state)
    return await handler(request)


@wrap_model_call
async def compact_conversation_context(
    request: ModelRequest,
    handler: Callable,
) -> ModelResponse:
    messages = request.state.get("messages", [])
    decision = await maybe_compact_conversation(
        messages=messages,
        conversation_summary=request.state.get("conversation_summary", ""),
        summary_upto=request.state.get("summary_upto", 0),
    )
    if decision.should_compact or decision.effective_messages is not messages:
        updated_state = {
            **request.state,
            "conversation_summary": decision.summary,
            "summary_upto": decision.summary_upto,
        }
        request = request.override(messages=decision.effective_messages, state=updated_state)
    return await handler(request)


@wrap_model_call
async def inject_runtime_context(
    request: ModelRequest,
    handler: Callable,
) -> ModelResponse:
    """
    在 LLM 被求情体的每一次调用前，拦截并注入动态上下文。
    
    拦截时机：
      不是路由层或 service 层初化时，而是 LLM.ainvoke() 被真正调用前。
      这样可以确保：
        ✓ Agent 主循环中的每次中間推理卿都能拦截
        ✓ PAE 子流程中的每次求且也能拦截
        ✓ 不需要告诉 service/agent 。middleware 自动化
    
    注入的内容：
      动态 prompt = Skill + Memory + 人格 + 上下文
      都是根据当前请求（user_id, query, plan_mode）实时计算
    """
    # 这里运行在“每次模型调用之前”，而不是只在请求入口执行一次。
    # 因此：
    # - ReAct 主循环每一轮推理都会重新注入最新的 persona / skills / memory / prompt
    # - 主循环里 tool 调完后的下一轮推理，也会拿到更新后的上下文
    user_id = request.state.get("user_id", "")
    messages = request.messages
    human_msgs = [m for m in messages if hasattr(m, "type") and m.type == "human"]
    if human_msgs:
        query = str(human_msgs[-1].content)
        # ⚡关键：在即将獻辐的一刻之前，根据当前 user_id + query 实时计算最新的能力
        # 这样高效率且永远是最新的
        # build_runtime_context 会统一把：
        # - 长期记忆
        # - Markdown 显式记忆
        # - persona
        # - skills
        # - 当前任务复杂度与推荐动作
        # 拼成新的 runtime system prompt
        runtime_route = request.state.get("runtime_route") or {}
        runtime_context = await build_runtime_context(
            query=query,
            user_id=user_id,
            plan_mode=request.state.get("plan_mode"),
            available_tool_names=get_tool_names(),
            route_decision=runtime_route if isinstance(runtime_route, dict) and runtime_route else None,
        )
        # 这里不是覆盖掉 _build_agent() 里写死的基础 system_prompt，
        # 而是在其后面追加 runtime 生成的动态 prompt。
        # 所以最终送给 LLM 的 system prompt 结构大致是：
        #   基础 system_prompt + persona/skills/memory/plan_mode 等动态上下文
        #
        # 这会带来一定“语义重复”的可能，例如基础 prompt 说“你是主执行智能体”，
        # persona 文件里也可能再次描述身份。但这种重复目前是可控的：
        # - 基础 prompt 负责稳定规则
        # - persona / memory 负责补充更具体、可编辑的上下文
        # 如果后面发现冲突，应优先收敛 persona 文本，而不是移除基础 prompt。
        current_prompt = request.system_prompt or ""
        updated_state = {
            **request.state,
            "activated_skill_names": [item.package.metadata.name for item in runtime_context.activated_skills],
            "planner_hints": runtime_context.skill_effects.planner_hints,
            "executor_hints": runtime_context.skill_effects.executor_hints,
            "output_format_hints": runtime_context.skill_effects.output_format_hints,
        }
        if runtime_context.activated_skills:
            skill_names = ", ".join(item.package.metadata.name for item in runtime_context.activated_skills)
            append_tool_trace(f"🧩 [Skill激活] {skill_names}")
        request = request.override(
            system_prompt=current_prompt + "\n\n" + runtime_context.system_prompt,
            state=updated_state,
        )
    return await handler(request)


@wrap_model_call
async def bind_selected_model(
    request: ModelRequest,
    handler: Callable,
) -> ModelResponse:
    """
    下一个 middleware：根据君主选择的 model_choice，动态绑定正确的模型实例。
    
    设计：
      不是 hardcode 一个东幸的模型，而是每次调用前按 model_choice 刚刚好。
      比如：AgentPass request.state["model_choice"] = "deepseek"，
          下次 LLM 调用前，middleware 会自动切为 deepseek_model。
    """
    model_choice = request.state.get("model_choice", "deepseek-v4-flash")
    # 主循环的模型不是在 service 里硬编码的，而是在每次模型调用前动态绑定。
    # 当前只允许在 DeepSeek V4 Flash / Pro 之间切换，不再静默回退到本地模型。
    raw = get_model_by_choice(model_choice)
    if request.state.get("guard_disable_tools"):
        # loop_guard 命中后，本次及之后的推理都不再给模型看到任何 tool
        model = raw
    else:
        model = raw.bind_tools(get_runtime_tools())
    return await handler(request.override(model=model))
