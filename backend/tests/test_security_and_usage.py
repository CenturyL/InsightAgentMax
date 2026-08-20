from __future__ import annotations

import asyncio
import json
import uuid
from types import SimpleNamespace

import pytest
from langchain.agents.middleware.types import ModelResponse
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph

from backend.api.schemas import ChatRequest
from backend.api import routes
from backend.core.config import settings
from backend.core.memory import (
    LongTermMemoryManager,
    ensure_pgvector_ready,
    memory_document_id,
    normalize_memory_fact,
)
from backend.runtime.budget import BudgetExceeded, RequestBudget
from backend.runtime import engine
from backend.runtime.engine import judge_runtime_route, local_route_hint
from backend.core import middleware
from backend.runtime.tool_registry import get_runtime_tools
from backend.core.llm import (
    DEFAULT_MODEL_ID,
    get_canonical_model_id,
    get_model_by_choice,
    get_model_pricing,
    get_model_registry_id,
    get_router_model,
    get_runtime_models,
    get_summary_model,
    is_model_available,
)
from backend.services import usage_service
from backend.services.agent_service import (
    AgentState,
    _build_memory_extraction_conversation,
    _normalize_memory_facts,
)


def test_public_tool_allowlist_excludes_host_capabilities():
    names = {tool.name for tool in get_runtime_tools()}
    assert names == {
        "rag_search",
        "rag_search_uploaded",
        "get_current_time",
        "run_plan_and_execute",
        "ask_user",
    }
    assert not names.intersection({"code_execute", "shell_execute", "sandbox_read_file", "sandbox_write_file"})


def test_pgvector_extension_is_ready_for_long_term_memory():
    if not settings.POSTGRES_URL:
        pytest.skip("POSTGRES_URL 未配置")
    version = ensure_pgvector_ready()
    assert tuple(int(part) for part in version.split(".")) >= (0, 8, 1)


def test_memory_extraction_uses_user_messages_and_deduplicates():
    conversation = _build_memory_extraction_conversation(
        [
            HumanMessage(content="我叫小明，请记住。"),
            AIMessage(content="好的，你叫小明。"),
            HumanMessage(content="我叫什么名字？"),
        ]
    )
    assert "AI:" not in conversation
    assert "好的，你叫小明" not in conversation
    assert normalize_memory_fact("用户姓名：什么名字") is None
    assert _normalize_memory_facts(["用户姓名：小明", "用户姓名：小明", "用户姓名：什么名字"]) == ["用户姓名：小明"]


def test_long_term_memory_save_is_idempotent():
    saved_ids: list[str] = []

    class FakeStore:
        def add_documents(self, _documents, ids):
            saved_ids.extend(ids)

    manager = LongTermMemoryManager()
    manager._store = FakeStore()
    manager.save("user-1", "用户姓名：小明")
    manager.save("user-1", "用户姓名：小明")
    expected = memory_document_id("user-1", "用户姓名：小明")
    assert saved_ids == [expected, expected]


def test_chat_request_rejects_external_model_and_oversized_input():
    assert ChatRequest(query="ok").model_choice == DEFAULT_MODEL_ID
    assert ChatRequest(query="ok", model_choice="local_qwen").model_choice == "local_qwen"
    assert not is_model_available("local_qwen")
    with pytest.raises(ValueError):
        ChatRequest(query="x" * (settings.MAX_QUERY_LENGTH + 1))


def test_runtime_model_registry_only_exposes_deepseek_models():
    models = get_runtime_models()
    ids = [model["id"] for model in models]
    assert ids == ["deepseek-v4-flash", "deepseek-v4-pro"]
    assert all({"id", "label", "available", "remote"} <= set(model) for model in models)
    assert all(model["remote"] for model in models)


def test_internal_models_use_flash_without_public_local_fallback():
    with pytest.raises(ValueError):
        get_model_by_choice("local_qwen")
    assert get_model_registry_id(get_model_by_choice(DEFAULT_MODEL_ID)) == DEFAULT_MODEL_ID
    assert get_model_registry_id(get_router_model()) == DEFAULT_MODEL_ID
    assert get_model_registry_id(get_summary_model()) == DEFAULT_MODEL_ID
    assert get_router_model().temperature == 0.0
    assert get_summary_model().temperature == 0.0
    assert get_model_pricing(DEFAULT_MODEL_ID) == (440_000, 1_320_000)
    assert get_canonical_model_id("deepseek") == DEFAULT_MODEL_ID
    with pytest.raises(ValueError):
        get_model_registry_id(object())


def test_simple_conversation_stays_out_of_pae():
    for query in ("你是谁", "介绍一下你自己。", "你好", "什么是向量检索？"):
        assert local_route_hint(query, "auto") == "direct_or_simple_tools"
    assert local_route_hint("比较 ChromaDB 和 pgvector 的优缺点并给出选型建议", "auto") == "run_plan_and_execute"
    assert local_route_hint("你好，请先介绍你自己，再比较两个模型并写一份报告", "auto") == "run_plan_and_execute"


def test_runtime_route_short_circuits_simple_query_without_router_model(monkeypatch):
    async def fail_router(*args, **kwargs):
        raise AssertionError("simple conversation must not invoke the router model")

    async def run():
        monkeypatch.setattr("backend.runtime.engine.invoke_model", fail_router)
        engine._ROUTE_CACHE.clear()
        decision = await judge_runtime_route(
            query="你是谁",
            plan_mode="auto",
            complexity="low",
            available_tool_names=[],
            skill_catalog_rows=[],
        )
        assert decision.pae_action == "direct_or_simple_tools"

    asyncio.run(run())


def test_runtime_route_provider_failure_degrades_to_direct(monkeypatch):
    async def fail_router(*args, **kwargs):
        raise RuntimeError("router unavailable")

    async def run():
        monkeypatch.setattr("backend.runtime.engine.invoke_model", fail_router)
        decision = await judge_runtime_route(
            query=f"请结合当前项目中的若干背景信息，说明你认为最重要的风险、影响和后续处理方向，并解释判断依据。{uuid.uuid4().hex}",
            plan_mode="auto",
            complexity="high",
            available_tool_names=[],
            skill_catalog_rows=[],
        )
        assert decision.pae_action == "direct_or_simple_tools"
        assert "降级" in decision.pae_reason

    asyncio.run(run())


def test_request_budget_stops_model_calls(monkeypatch):
    calls = 0

    async def fake_consume(_key: str):
        nonlocal calls
        calls += 1

    monkeypatch.setattr("backend.runtime.budget.consume_model_call", fake_consume)
    monkeypatch.setattr(settings, "MAX_MODEL_CALLS_PER_REQUEST", 2)
    async def run():
        budget = RequestBudget("budget-test")
        await budget.consume_model_call()
        await budget.consume_model_call()
        with pytest.raises(BudgetExceeded) as exc_info:
            await budget.consume_model_call()
        assert exc_info.value.code == "MODEL_CALL_LIMIT"
        assert calls == 2

    asyncio.run(run())


def test_react_model_middleware_records_provider_usage(monkeypatch):
    recorded: dict = {}

    async def fake_consume():
        return 2

    async def fake_record(**kwargs):
        recorded.update(kwargs)

    async def handler(_request):
        return ModelResponse(
            result=[
                AIMessage(
                    content="ok",
                    usage_metadata={"input_tokens": 12, "output_tokens": 3, "total_tokens": 15},
                )
            ]
        )

    monkeypatch.setattr(middleware, "consume_model_call_if_active", fake_consume)
    monkeypatch.setattr(middleware, "record_model_response_usage", fake_record)

    async def run():
        request = SimpleNamespace(
            state={"model_choice": DEFAULT_MODEL_ID},
            system_message=None,
            messages=[],
        )
        response = await middleware.enforce_model_budget.awrap_model_call(request, handler)
        assert response.result[0].content == "ok"
        assert recorded["model_id"] == DEFAULT_MODEL_ID
        assert recorded["call_index"] == 2
        assert recorded["response"].usage_metadata["total_tokens"] == 15

    asyncio.run(run())


def test_agent_state_merges_parallel_tool_messages():
    graph = StateGraph(AgentState)
    graph.add_node("left", lambda _state: {"messages": [AIMessage(content="left", id="left")]})
    graph.add_node("right", lambda _state: {"messages": [AIMessage(content="right", id="right")]})
    graph.add_edge(START, "left")
    graph.add_edge(START, "right")
    graph.add_edge("left", END)
    graph.add_edge("right", END)

    result = graph.compile().invoke({"messages": [HumanMessage(content="start", id="start")]})
    assert [message.content for message in result["messages"]] == ["start", "left", "right"]


def test_same_idempotency_key_is_single_winner():
    if not settings.POSTGRES_URL:
        pytest.skip("POSTGRES_URL 未配置")
    async def run():
        await usage_service.initialize_usage_store()
        key = f"pytest-{uuid.uuid4().hex}"
        ip = "198.51.100.78"

        async def attempt():
            try:
                return await usage_service.begin_request(
                    idempotency_key=key,
                    request_hash="same-body",
                    client_ip=ip,
                    thread_id="pytest-thread",
                )
            except usage_service.UsageServiceError as exc:
                return exc.code

        try:
            results = await asyncio.gather(*(attempt() for _ in range(20)))
            assert sum(getattr(result, "status", None) == "pending" for result in results) == 1
            assert results.count("REQUEST_IN_PROGRESS") == 19
            await usage_service.finish_request(key, response=[{"type": "answer", "content": "ok"}], success=True)
            replay = await usage_service.begin_request(
                idempotency_key=key,
                request_hash="same-body",
                client_ip=ip,
                thread_id="pytest-thread",
            )
            assert replay.status == "completed"
            assert replay.response == [{"type": "answer", "content": "ok"}]
        finally:
            await usage_service.purge_request_usage([key])

    asyncio.run(run())


def test_model_usage_is_idempotent_and_releases_reservation(monkeypatch):
    if not settings.POSTGRES_URL:
        pytest.skip("POSTGRES_URL 未配置")
    monkeypatch.setattr(settings, "USAGE_LIMIT_ENABLED", True)

    async def run():
        await usage_service.initialize_usage_store()
        key = f"pytest-usage-{uuid.uuid4().hex}"
        ip = "198.51.100.81"
        try:
            reservation = await usage_service.begin_request(
                idempotency_key=key,
                request_hash="usage-body",
                client_ip=ip,
                thread_id="pytest-usage-thread",
                model_id="deepseek-v4-flash",
                estimated_tokens=120,
                price_input_microunits=440_000,
                price_output_microunits=1_320_000,
            )
            assert reservation.status == "pending"
            import psycopg
            conn = await psycopg.AsyncConnection.connect(settings.POSTGRES_URL, autocommit=True)
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT reserved_cost_microunits FROM model_call_reservations WHERE idempotency_key = %s",
                        (key,),
                    )
                    assert await cur.fetchone() == (158,)
            finally:
                await conn.close()
            call_index = await usage_service.consume_model_call(key)
            await usage_service.record_model_usage(
                key,
                call_index=call_index,
                model_id="deepseek-v4-flash",
                provider="deepseek",
                input_tokens=80,
                output_tokens=20,
                usage_source="provider",
            )
            await usage_service.record_model_usage(
                key,
                call_index=call_index,
                model_id="deepseek-v4-flash",
                provider="deepseek",
                input_tokens=999,
                output_tokens=999,
                usage_source="provider",
            )
            await usage_service.finish_request(key, response=[], success=True)

            conn = await psycopg.AsyncConnection.connect(settings.POSTGRES_URL, autocommit=True)
            try:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT COUNT(*), SUM(total_tokens) FROM model_call_usage WHERE idempotency_key = %s", (key,))
                    assert await cur.fetchone() == (1, 100)
                    await cur.execute(
                        "SELECT reserved_tokens, reserved_cost_microunits FROM model_call_reservations WHERE idempotency_key = %s",
                        (key,),
                    )
                    assert await cur.fetchone() == (0, 0)
            finally:
                await conn.close()
        finally:
            await usage_service.purge_request_usage([key])

    asyncio.run(run())


def test_expired_model_reservation_is_reconciled_before_next_request():
    if not settings.POSTGRES_URL:
        pytest.skip("POSTGRES_URL 未配置")

    async def run():
        await usage_service.initialize_usage_store()
        old_key = f"pytest-expired-{uuid.uuid4().hex}"
        new_key = f"pytest-after-expired-{uuid.uuid4().hex}"
        ip = "198.51.100.82"
        try:
            await usage_service.begin_request(
                idempotency_key=old_key,
                request_hash="expired-body",
                client_ip=ip,
                thread_id="pytest-expired-thread",
                model_id="deepseek-v4-flash",
                estimated_tokens=200,
            )
            import psycopg
            conn = await psycopg.AsyncConnection.connect(settings.POSTGRES_URL, autocommit=True)
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "UPDATE model_call_reservations SET expires_at = NOW() - INTERVAL '1 second' WHERE idempotency_key = %s",
                        (old_key,),
                    )
            finally:
                await conn.close()

            reservation = await usage_service.begin_request(
                idempotency_key=new_key,
                request_hash="new-body",
                client_ip=ip,
                thread_id="pytest-new-thread",
                model_id="deepseek-v4-flash",
                estimated_tokens=200,
            )
            assert reservation.status == "pending"

            conn = await psycopg.AsyncConnection.connect(settings.POSTGRES_URL, autocommit=True)
            try:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT status, reserved_tokens FROM model_call_reservations WHERE idempotency_key = %s", (old_key,))
                    assert await cur.fetchone() == ("expired", 0)
            finally:
                await conn.close()
        finally:
            await usage_service.purge_request_usage([old_key, new_key])

    asyncio.run(run())


def test_model_token_limit_is_scoped_per_ip(monkeypatch):
    if not settings.POSTGRES_URL:
        pytest.skip("POSTGRES_URL 未配置")
    monkeypatch.setattr(settings, "USAGE_LIMIT_ENABLED", True)
    monkeypatch.setattr(settings, "MODEL_DAILY_TOKEN_LIMIT", 1_000_000)
    monkeypatch.setattr(settings, "MODEL_DAILY_TOKEN_LIMIT_PER_IP", 100)

    async def run():
        await usage_service.initialize_usage_store()
        first_key = f"pytest-ip-limit-1-{uuid.uuid4().hex}"
        second_key = f"pytest-ip-limit-2-{uuid.uuid4().hex}"
        ip = "198.51.100.87"
        try:
            await usage_service.begin_request(
                idempotency_key=first_key,
                request_hash="one",
                client_ip=ip,
                thread_id="ip-limit-1",
                model_id="deepseek-v4-flash",
                estimated_tokens=80,
            )
            with pytest.raises(usage_service.UsageServiceError) as exc_info:
                await usage_service.begin_request(
                    idempotency_key=second_key,
                    request_hash="two",
                    client_ip=ip,
                    thread_id="ip-limit-2",
                    model_id="deepseek-v4-flash",
                    estimated_tokens=30,
                )
            assert exc_info.value.code == "DAILY_MODEL_LIMIT_EXCEEDED"
        finally:
            await usage_service.purge_request_usage([first_key, second_key])

    asyncio.run(run())


def test_model_daily_limit_disabled_allows_local_development(monkeypatch):
    if not settings.POSTGRES_URL:
        pytest.skip("POSTGRES_URL 未配置")
    monkeypatch.setattr(settings, "USAGE_LIMIT_ENABLED", False)
    monkeypatch.setattr(settings, "MODEL_DAILY_TOKEN_LIMIT_PER_IP", 1)

    async def run():
        await usage_service.initialize_usage_store()
        keys = [f"pytest-local-unlimited-{uuid.uuid4().hex}" for _ in range(2)]
        try:
            for index, key in enumerate(keys):
                reservation = await usage_service.begin_request(
                    idempotency_key=key,
                    request_hash=f"local-{index}",
                    client_ip="198.51.100.88",
                    thread_id=f"local-limit-{index}",
                    model_id="deepseek-v4-flash",
                    estimated_tokens=10_000,
                    price_input_microunits=0,
                    price_output_microunits=0,
                )
                assert reservation.status == "pending"
        finally:
            await usage_service.purge_request_usage(keys)

    asyncio.run(run())


def test_agent_route_replays_completed_stream():
    async def run():
        original_stream = routes.get_agent_stream

        async def fake_stream(*args, **kwargs):
            yield {"type": "answer", "content": "mock answer"}

        async def read_response(response):
            parts = []
            async for part in response.body_iterator:
                parts.append(part if isinstance(part, bytes) else part.encode())
            return b"".join(parts)

        key = f"pytest-route-{uuid.uuid4().hex}"
        thread_id = f"pytest-route-thread-{uuid.uuid4().hex}"
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/api/v3/chat/agent",
            "headers": [(b"idempotency-key", key.encode())],
            "client": ("198.51.100.79", 1234),
            "query_string": b"",
            "scheme": "http",
            "server": ("test", 80),
            "root_path": "",
            "http_version": "1.1",
        }
        body = ChatRequest(query="hello", thread_id=thread_id)
        routes.get_agent_stream = fake_stream
        try:
            first = await routes.chat_agent_endpoint(body, routes.Request(scope))
            first_content = await read_response(first)
            replay = await routes.chat_agent_endpoint(body, routes.Request(scope))
            assert await read_response(replay) == first_content
        finally:
            routes.get_agent_stream = original_stream
            await usage_service.purge_request_usage([key])

    if not settings.POSTGRES_URL:
        pytest.skip("POSTGRES_URL 未配置")
    asyncio.run(run())


def test_agent_route_emits_terminal_trace_on_budget_timeout():
    async def run():
        original_stream = routes.get_agent_stream

        async def fake_stream(*args, **kwargs):
            raise BudgetExceeded("REQUEST_TIMEOUT", "请求处理超时，请缩小问题范围后重试。")
            yield  # pragma: no cover

        async def read_response(response):
            parts = []
            async for part in response.body_iterator:
                parts.append(part if isinstance(part, bytes) else part.encode())
            return b"".join(parts)

        key = f"pytest-route-timeout-{uuid.uuid4().hex}"
        thread_id = f"pytest-route-timeout-thread-{uuid.uuid4().hex}"
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/api/v3/chat/agent",
            "headers": [(b"idempotency-key", key.encode())],
            "client": ("198.51.100.80", 1234),
            "query_string": b"",
            "scheme": "http",
            "server": ("test", 80),
            "root_path": "",
            "http_version": "1.1",
        }
        body = ChatRequest(query="强制 PAE 超时回归", thread_id=thread_id)
        routes.get_agent_stream = fake_stream
        try:
            response = await routes.chat_agent_endpoint(body, routes.Request(scope))
            payload = await read_response(response)
            lines = [json.loads(line) for line in payload.decode().splitlines() if line.strip()]
            assert any(item.get("type") == "trace" and "请求终止" in item.get("content", "") for item in lines)
            assert any(item.get("type") == "error" and item.get("code") == "REQUEST_TIMEOUT" for item in lines)
        finally:
            routes.get_agent_stream = original_stream
            await usage_service.purge_request_usage([key])

    if not settings.POSTGRES_URL:
        pytest.skip("POSTGRES_URL 未配置")
    asyncio.run(run())


def test_agent_route_emits_terminal_trace_on_async_timeout():
    async def run():
        original_stream = routes.get_agent_stream

        async def fake_stream(*args, **kwargs):
            raise asyncio.TimeoutError()
            yield  # pragma: no cover

        async def read_response(response):
            parts = []
            async for part in response.body_iterator:
                parts.append(part if isinstance(part, bytes) else part.encode())
            return b"".join(parts)

        key = f"pytest-route-async-timeout-{uuid.uuid4().hex}"
        thread_id = f"pytest-route-async-timeout-thread-{uuid.uuid4().hex}"
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/api/v3/chat/agent",
            "headers": [(b"idempotency-key", key.encode())],
            "client": ("198.51.100.83", 1234),
            "query_string": b"",
            "scheme": "http",
            "server": ("test", 80),
            "root_path": "",
            "http_version": "1.1",
        }
        body = ChatRequest(query="强制 PAE 异步超时回归", thread_id=thread_id)
        routes.get_agent_stream = fake_stream
        try:
            response = await routes.chat_agent_endpoint(body, routes.Request(scope))
            payload = await read_response(response)
            lines = [json.loads(line) for line in payload.decode().splitlines() if line.strip()]
            assert any(item.get("type") == "trace" and "请求终止" in item.get("content", "") for item in lines)
            assert any(item.get("type") == "error" and item.get("code") == "REQUEST_TIMEOUT" for item in lines)
        finally:
            routes.get_agent_stream = original_stream
            await usage_service.purge_request_usage([key])

    if not settings.POSTGRES_URL:
        pytest.skip("POSTGRES_URL 未配置")
    asyncio.run(run())
