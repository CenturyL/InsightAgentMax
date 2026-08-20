from __future__ import annotations

import asyncio
import uuid

import pytest

from backend.core.config import settings
from backend.services.session_service import (
    SessionOwnershipError,
    append_session_message,
    create_empty_session,
    delete_session,
    emit_session_event,
    ensure_session_started,
    initialize_session_store,
    load_session_replay,
    start_session_turn,
)


pytestmark = pytest.mark.skipif(not settings.POSTGRES_URL, reason="POSTGRES_URL 未配置")


def test_session_owner_event_idempotency_concurrency_and_replay():
    async def run():
        await initialize_session_store()
        thread_id = f"pytest-session-{uuid.uuid4().hex}"
        user_id = f"pytest-user-{uuid.uuid4().hex}"
        turn_id = f"pytest-turn-{uuid.uuid4().hex}"
        key = f"pytest-turn-key-{uuid.uuid4().hex}"
        try:
            await create_empty_session(user_id, thread_id=thread_id)
            with pytest.raises(SessionOwnershipError):
                await ensure_session_started(thread_id, "another-user", "越权访问")

            await ensure_session_started(thread_id, user_id, "第一条消息")
            actual_turn_id = await start_session_turn(
                thread_id=thread_id,
                user_id=user_id,
                turn_id=turn_id,
                idempotency_key=key,
            )
            assert actual_turn_id == turn_id

            duplicate_results = await asyncio.gather(
                *(emit_session_event(
                    turn_id=turn_id,
                    event_type="tool_start",
                    event_key="tool-call-1",
                    tool_name="rag_search",
                    content="开始检索",
                ) for _ in range(8))
            )
            assert {result["sequence"] for result in duplicate_results} == {2}
            assert sum(result["inserted"] for result in duplicate_results) == 1

            concurrent_results = await asyncio.gather(
                *(emit_session_event(
                    turn_id=turn_id,
                    event_type="trace",
                    event_key=f"trace-{index}",
                    content=f"trace-{index}",
                ) for index in range(12))
            )
            sequences = sorted(result["sequence"] for result in concurrent_results)
            assert sequences == list(range(3, 15))

            await append_session_message(thread_id, user_id, "user", "第一条消息", turn_id=turn_id)
            await append_session_message(thread_id, user_id, "user", "第一条消息", turn_id=turn_id)
            await append_session_message(thread_id, user_id, "assistant", "完成", turn_id=turn_id)
            await append_session_message(thread_id, user_id, "assistant", "完成", turn_id=turn_id)
            replay = await load_session_replay(thread_id, user_id)
            assert [(item["role"], item["content"]) for item in replay] == [
                ("user", "第一条消息"),
                ("assistant", "完成"),
            ]
            assert replay[0]["events"] == []
            assert [event["sequence"] for event in replay[1]["events"]] == list(range(1, 15))
        finally:
            await delete_session(thread_id, user_id)

    asyncio.run(run())
