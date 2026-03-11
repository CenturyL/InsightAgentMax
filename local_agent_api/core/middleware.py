from typing import Callable
from langchain.agents.middleware import wrap_model_call, wrap_tool_call, ModelRequest, ModelResponse
from langchain_core.messages import ToolMessage
from local_agent_api.core.llm import basic_model, advanced_model
from local_agent_api.core.config import settings

"""Middleware hooks for simple-path tool recovery, memory injection, and model routing."""


# tool calling 错误处理
# 截胡工具调用，替他执行
# 如果报错就造一个空的返回去，不让agent崩掉
@wrap_tool_call
async def handle_tool_errors(request, handler):
    """捕获工具执行异常，以友好消息返回给 Agent 继续推理。"""
    try:
        return await handler(request)
    except Exception as e:
        return ToolMessage(
            content=f"工具调用失败，请换个方式提问或跳过此步骤。错误详情：{str(e)}",
            tool_call_id=request.tool_call["id"],
        )


# 向prompt注入长期记忆
# 模型调用前，根据user_id + 当前问题检索最相关事实，并注入 system prompt
@wrap_model_call
async def inject_long_term_memory(
    request: ModelRequest,
    handler: Callable,
) -> ModelResponse:
    """
    每次 LLM 调用前，检索该用户的长期记忆并注入 system_prompt。
    利用向量相似度只注入与当前问题最相关的记忆，避免 prompt 膨胀。
    POSTGRES_URL 未配置或检索失败时静默跳过，不影响主流程。
    """
    user_id = request.state.get("user_id", "")
    if user_id and settings.POSTGRES_URL:
        messages = request.state.get("messages", [])
        # 取message中的人工提问（取前先检验）
        human_msgs = [
            m for m in messages
            if hasattr(m, "type") and m.type == "human"
        ]
        # 如果有，取最后一条（过滤掉工具调用中间轮次）
        if human_msgs:
            query = human_msgs[-1].content
            # 尝试导入长期记忆管理器并search
            try:
                from local_agent_api.core.memory import long_term_memory
                memories = long_term_memory.search(user_id, query, k=3)
                if memories:
                    memory_text = "\n".join(f"- {m}" for m in memories)
                    current_prompt = request.system_prompt or ""
                    new_prompt = (
                        current_prompt
                        + f"\n\n【关于该用户的长期记忆（历史会话积累）】\n{memory_text}"
                    )
                    request = request.override(system_prompt=new_prompt)
                    print(f"💡 [长期记忆] 已为 {user_id} 注入 {len(memories)} 条记忆")
            except Exception:
                pass  # 记忆注入失败不影响主流程

    return await handler(request)


# 动态模型路由
@wrap_model_call
async def dynamic_model_selection(
    request: ModelRequest,
    handler: Callable
) -> ModelResponse:
    """
    基于用户问题的复杂度和对话轮次，动态选择使用本地 Qwen 还是 云端 DeepSeek。
    这一步将在中间件层拦截模型请求并进行重定向。

    注意：若消息历史中已包含 ToolMessage（即本轮是工具调用后的续算），
    则不切换模型，保持上一轮的模型继续执行，避免 400 invalid_request_error。
    """
    from langchain_core.messages import ToolMessage
    messages = request.state.get("messages", [])

    # 关键保护：工具调用续算(含ToolMessage)时，禁止切换模型
    in_tool_continuation = any(isinstance(m, ToolMessage) for m in messages)
    if in_tool_continuation:
        return await handler(request)

    # 第一步：规则判定
    is_complex = False
    # 规则A：对话轮次大于2
    if len(messages) > 2:
        is_complex = True
    # 规则B：最新一句话非常长
    if len(messages) > 0 and len(messages[-1].content) > 50:
        is_complex = True
    # 规则C：触发某些特定词汇
    if len(messages) > 0 and any(keyword in messages[-1].content for keyword in
            ["总结", "分析", "比较", "对比", "政策", "招标", "投标", "公告", "提取", "报告", "公司内部", "请假", "WIFI", "时间", "几点"]):
        is_complex = True

    # 第二步：路由指派
    from local_agent_api.services.tools import AGENT_TOOLS
    if is_complex:
        print("🔀 [路由判定]：复杂意图/深层状态 -> 切换至 DeepSeek")
        model = advanced_model.bind_tools(AGENT_TOOLS)
    else:
        print("🔀 [路由判定]：简单对话 -> 降级为本地 Qwen")
        model = basic_model.bind_tools(AGENT_TOOLS)

    # 第三部：override新model返回
    return await handler(request.override(model=model))
