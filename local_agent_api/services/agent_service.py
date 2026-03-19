"""
agent_service.py — 智能体服务

V2 设计：
1. 唯一主循环：ReAct
2. PAE 作为高级工具 run_plan_and_execute 被主循环调用
3. runtime 统一提供动态 prompt、硬触发 PAE、工具上下文
4. thread_id 仍驱动短期记忆，user_id 驱动长期记忆写回
"""
from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator
from typing_extensions import TypedDict

from langchain.agents import create_agent
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from local_agent_api.core.config import settings
from local_agent_api.core.llm import deepseek_model, get_model_label, local_model
from local_agent_api.core.middleware import (
    bind_selected_model,
    handle_tool_errors,
    inject_runtime_context,
)
from local_agent_api.runtime.engine import (
    RuntimeRequest,
    react_recursion_limit,
    should_force_pae,
)
from local_agent_api.runtime.workflow import run_plan_and_execute_once, stream_plan_and_execute
from local_agent_api.services.tool_context import (
    consume_last_pae_result,
    drain_tool_trace,
    get_tool_trace_queue,
    reset_tool_request_context,
    set_tool_request_context,
)
from local_agent_api.services.tools import AGENT_TOOLS


class AgentState(TypedDict):
    messages: list[BaseMessage]
    user_id: str
    plan_mode: str
    model_choice: str


_agent = None
_checkpointer = None
_connection_pool = None


def _should_suppress_stream_chunk(chunk) -> bool:
    tool_call_chunks = getattr(chunk, "tool_call_chunks", None)
    if tool_call_chunks:
        return True
    chunk_content = getattr(chunk, "content", None)
    if not isinstance(chunk_content, str):
        return False
    stripped = chunk_content.strip()
    if not stripped:
        return False
    if stripped in {"[", "]", "{", "}", ":", ","}:
        return True
    if any(marker in stripped for marker in ('"step_id"', '"required_capability"', '"expected_output"', '"status"')):
        return True
    return False


def _build_agent(checkpointer):
    """构建唯一主循环 Agent。"""
    return create_agent(
        model=local_model,
        tools=AGENT_TOOLS,
        middleware=[
            inject_runtime_context,
            bind_selected_model,
            handle_tool_errors,
        ],
        checkpointer=checkpointer,
        state_schema=AgentState,
        system_prompt=(
            "你是 InsightAgentPro，一个通用智能体平台中的主执行智能体。"
            "默认在 ReAct 主循环中工作。"
            "如果任务涉及比较、提取多个字段、生成报告/方案、多步研究、需要多工具协作、"
            "或你无法确定单轮工具调用就能稳定完成，则必须先调用 run_plan_and_execute，禁止直接尝试一次性回答。"
        ),
    )


async def initialize() -> None:
    """初始化 Agent 及 checkpointer。"""
    global _agent, _checkpointer, _connection_pool

    if settings.POSTGRES_URL:
        try:
            from psycopg_pool import AsyncConnectionPool
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

            _connection_pool = AsyncConnectionPool(
                conninfo=settings.POSTGRES_URL,
                max_size=10,
                open=False,
                kwargs={"autocommit": True, "prepare_threshold": 0},
            )
            await _connection_pool.open()

            _checkpointer = AsyncPostgresSaver(_connection_pool)
            await _checkpointer.setup()
            print("✅ [Checkpointer] 已连接 PostgreSQL，使用 AsyncPostgresSaver")
        except Exception as e:
            print(f"⚠️ [Checkpointer] PostgreSQL 连接失败（{e}），降级为 MemorySaver")
            _checkpointer = MemorySaver()
    else:
        _checkpointer = MemorySaver()
        print("ℹ️ [Checkpointer] 未配置 POSTGRES_URL，使用 MemorySaver（进程内短期记忆）")

    _agent = _build_agent(_checkpointer)
    print("✅ [Agent] 初始化完成")


async def cleanup() -> None:
    """关闭数据库连接池。"""
    global _connection_pool
    if _connection_pool:
        await _connection_pool.close()
        print("🔒 [Agent] 数据库连接池已关闭")


def _get_agent():
    """同步获取 Agent 单例。"""
    global _agent, _checkpointer
    if _agent is None:
        _checkpointer = MemorySaver()
        _agent = _build_agent(_checkpointer)
    return _agent


async def _extract_and_save_memories(thread_id: str, user_id: str) -> None:
    """对话结束后，异步提取长期记忆。"""
    if not user_id or not settings.POSTGRES_URL:
        return
    try:
        agent = _get_agent()
        state = await agent.aget_state({"configurable": {"thread_id": thread_id}})
        messages = state.values.get("messages", [])
        recent = messages[-6:] if len(messages) > 6 else messages
        conversation = "\n".join(
            f"{'用户' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
            for m in recent
            if hasattr(m, "content") and m.content
        )
        if not conversation.strip():
            return

        extraction_prompt = (
            "从以下对话中提取关于用户的关键信息，如偏好、身份、重要事项等。"
            "每行一条，只输出信息本身，不要编号或多余说明，无有效信息则输出空。\n\n"
            f"{conversation}"
        )
        response = await deepseek_model.ainvoke(extraction_prompt)
        facts = [line.strip() for line in response.content.splitlines() if line.strip()]

        from local_agent_api.core.memory import long_term_memory
        for fact in facts:
            long_term_memory.save(user_id, fact)
        if facts:
            print(f"💾 [长期记忆] 为 {user_id} 保存了 {len(facts)} 条记忆")
    except Exception as e:
        print(f"⚠️ [长期记忆] 记忆提取失败（{e}），跳过")


async def get_agent_stream(
    query: str,
    thread_id: str = "default",
    user_id: str = "",
    plan_mode: str | None = None,
    model_choice: str = "local_qwen",
    metadata_filters: dict[str, Any] | None = None,
) -> AsyncGenerator[str, None]:
    """
    唯一智能体主入口：始终走 ReAct 主循环，必要时由模型自行调用 run_plan_and_execute。
    """
    agent = _get_agent()
    request = RuntimeRequest(
        query=query,
        thread_id=thread_id,
        user_id=user_id,
        plan_mode=plan_mode or "auto",
        model_choice=model_choice,
        metadata_filters=metadata_filters or {},
    )
    context_tokens = set_tool_request_context(
        thread_id=thread_id,
        user_id=user_id,
        plan_mode=request.plan_mode,
        model_choice=request.model_choice,
        metadata_filters=request.metadata_filters,
    )
    tool_trace_queue = get_tool_trace_queue(context_tokens)
    inputs: AgentState = {
        "messages": [HumanMessage(content=query)],
        "user_id": user_id,
        "plan_mode": request.plan_mode,
        "model_choice": request.model_choice,
    }
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": react_recursion_limit(),
    }

    try:
        model_label = get_model_label(request.model_choice)
        yield f"> 模型来源：{model_label}\n\n"
        yield f"🧠 [主循环] 已进入 ReAct 主循环。plan_mode={request.plan_mode}\n\n"

        if should_force_pae(query, request.plan_mode):
            yield "🧭 [硬触发] 当前请求满足计划执行条件，直接进入 PAE。\n\n"
            final_result = None
            async for line, result in stream_plan_and_execute(
                query=query,
                thread_id=thread_id,
                user_id=user_id,
                plan_mode=request.plan_mode,
                model_choice=request.model_choice,
                metadata_filters=request.metadata_filters,
            ):
                if line:
                    yield f"{line}\n\n"
                if result is not None:
                    final_result = result
            yield "\n"
            if final_result:
                yield final_result.get("final_answer", "")
            if user_id:
                asyncio.ensure_future(_extract_and_save_memories(thread_id, user_id))
            return

        stream_had_content = False
        emitted_trace_lines: set[str] = set()
        event_queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()
        pae_tool_invoked = False

        async def _pump_events() -> None:
            async for event in agent.astream_events(inputs, config=config, version="v2"):
                await event_queue.put(event)
            await event_queue.put(None)

        pump_task = asyncio.create_task(_pump_events())
        event_stream_done = False

        try:
            while not event_stream_done:
                pending = []
                event_task = asyncio.create_task(event_queue.get())
                pending.append(event_task)
                trace_task = None
                if tool_trace_queue is not None:
                    trace_task = asyncio.create_task(tool_trace_queue.get())
                    pending.append(trace_task)

                done, pending_tasks = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
                for task in pending_tasks:
                    task.cancel()

                if trace_task is not None and trace_task in done:
                    line = trace_task.result()
                    if line:
                        emitted_trace_lines.add(line)
                        yield f"{line}\n\n"
                    continue

                if event_task not in done:
                    continue

                event = event_task.result()
                if event is None:
                    event_stream_done = True
                    break

                kind = event["event"]

                if kind == "on_chat_model_stream":
                    if pae_tool_invoked:
                        continue
                    chunk = event["data"]["chunk"]
                    if _should_suppress_stream_chunk(chunk):
                        continue
                    chunk_content = chunk.content
                    if chunk_content:
                        stream_had_content = True
                        yield chunk_content

                elif kind == "on_tool_start":
                    tool_name = event["name"]
                    if tool_name == "run_plan_and_execute":
                        pae_tool_invoked = True
                        yield "\n\n🧭 [PAE调用] 主循环决定进入 Plan-and-Execute 子流程。\n\n"
                    else:
                        yield f"\n\n🛠️ [工具调用] 决定调用工具：【{tool_name}】...\n\n"

                elif kind == "on_tool_end":
                    tool_name = event["name"]
                    if tool_name == "run_plan_and_execute":
                        for line in drain_tool_trace():
                            if line not in emitted_trace_lines:
                                emitted_trace_lines.add(line)
                                yield f"{line}\n\n"
                        final_result = consume_last_pae_result()
                        yield "\n✅ [PAE完成] Plan-and-Execute 子流程执行完成，已直接输出最终结果。\n\n"
                        if final_result and final_result.get("final_answer"):
                            stream_had_content = True
                            yield final_result["final_answer"]
                        event_stream_done = True
                        break
                    else:
                        yield f"\n✅ [工具完成] 工具【{tool_name}】执行完成，正在继续推理...\n\n"
        finally:
            if not pump_task.done():
                pump_task.cancel()

        if stream_had_content and user_id:
            asyncio.ensure_future(_extract_and_save_memories(thread_id, user_id))
    finally:
        reset_tool_request_context(context_tokens)
