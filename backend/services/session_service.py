from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from backend.core.config import settings


class SessionOwnershipError(RuntimeError):
    """Raised when a thread is accessed by a different user."""

    code = "THREAD_OWNERSHIP_MISMATCH"


class SessionEventLimitError(RuntimeError):
    """Raised when a turn has reached its persisted event limit."""

    code = "SESSION_EVENT_LIMIT"


_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS agent_sessions (
    thread_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_message_preview TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_user_updated
ON agent_sessions (user_id, updated_at DESC);

CREATE TABLE IF NOT EXISTS agent_session_messages (
    id BIGSERIAL PRIMARY KEY,
    thread_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_agent_session_messages_thread_created
ON agent_session_messages (thread_id, created_at ASC);

ALTER TABLE agent_session_messages
    ADD COLUMN IF NOT EXISTS turn_id TEXT;
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'agent_session_messages_turn_role_unique'
    ) THEN
        ALTER TABLE agent_session_messages
            ADD CONSTRAINT agent_session_messages_turn_role_unique UNIQUE (thread_id, turn_id, role);
    END IF;
END $$;
CREATE INDEX IF NOT EXISTS idx_agent_session_messages_turn
ON agent_session_messages (turn_id, created_at ASC);

CREATE TABLE IF NOT EXISTS agent_session_turns (
    turn_id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'failed', 'cancelled', 'expired')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_agent_session_turns_thread_created
ON agent_session_turns (thread_id, created_at ASC);

CREATE TABLE IF NOT EXISTS agent_session_events (
    event_id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    turn_id TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    event_key TEXT,
    event_type TEXT NOT NULL,
    tool_name TEXT,
    tool_call_id TEXT,
    content TEXT NOT NULL DEFAULT '',
    payload_json JSONB,
    status TEXT NOT NULL DEFAULT 'emitted',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (turn_id, sequence)
);
ALTER TABLE agent_session_events
    ADD COLUMN IF NOT EXISTS event_key TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS idx_agent_session_events_turn_event_key
ON agent_session_events (turn_id, event_key)
WHERE event_key IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_agent_session_events_thread_sequence
ON agent_session_events (thread_id, sequence ASC);
CREATE INDEX IF NOT EXISTS idx_agent_session_events_turn_sequence
ON agent_session_events (turn_id, sequence ASC);
"""


def _require_postgres_url() -> str:
    if not settings.POSTGRES_URL:
        raise RuntimeError("当前环境未启用 PostgreSQL，无法使用历史会话功能。")
    return settings.POSTGRES_URL


async def initialize_session_store() -> None:
    conn = await psycopg.AsyncConnection.connect(_require_postgres_url(), autocommit=True)
    try:
        async with conn.cursor() as cur:
            await cur.execute(_CREATE_TABLE_SQL)
    finally:
        await conn.close()


def _normalize_whitespace(text: str) -> str:
    return " ".join((text or "").split()).strip()


def _truncate(text: str, limit: int) -> str:
    normalized = _normalize_whitespace(text)
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def build_session_title(text: str) -> str:
    title = _truncate(text, 56)
    return title or "新会话"


def build_message_preview(text: str) -> str:
    return _truncate(text, 110)


def _serialize_session_row(row: dict) -> dict:
    return {
        "thread_id": row["thread_id"],
        "user_id": row["user_id"],
        "title": row["title"],
        "created_at": row["created_at"].isoformat() if isinstance(row["created_at"], datetime) else str(row["created_at"]),
        "updated_at": row["updated_at"].isoformat() if isinstance(row["updated_at"], datetime) else str(row["updated_at"]),
        "last_message_preview": row["last_message_preview"],
    }


async def list_sessions(user_id: str) -> list[dict]:
    if not user_id.strip():
        return []
    conn = await psycopg.AsyncConnection.connect(_require_postgres_url(), autocommit=True, row_factory=dict_row)
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT thread_id, user_id, title, created_at, updated_at, last_message_preview
                FROM agent_sessions
                WHERE user_id = %s
                ORDER BY updated_at DESC
                """,
                (user_id.strip(),),
            )
            rows = await cur.fetchall()
            return [_serialize_session_row(row) for row in rows]
    finally:
        await conn.close()


async def create_empty_session(user_id: str, *, thread_id: str | None = None) -> dict:
    normalized_user = user_id.strip()
    if not normalized_user:
        raise RuntimeError("user_id 不能为空。")
    thread = thread_id or str(uuid.uuid4())
    conn = await psycopg.AsyncConnection.connect(_require_postgres_url(), autocommit=True, row_factory=dict_row)
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO agent_sessions (thread_id, user_id, title, last_message_preview)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (thread_id) DO NOTHING
                """,
                (thread, normalized_user, "新会话", ""),
            )
            await cur.execute(
                """
                SELECT thread_id, user_id, title, created_at, updated_at, last_message_preview
                FROM agent_sessions
                WHERE thread_id = %s
                """,
                (thread,),
            )
            row = await cur.fetchone()
            if row is None:
                raise RuntimeError("创建会话失败。")
            if row["user_id"] != normalized_user:
                raise SessionOwnershipError("该会话不属于当前用户。")
            return _serialize_session_row(row)
    finally:
        await conn.close()


async def bootstrap_sessions(user_id: str) -> dict:
    sessions = await list_sessions(user_id)
    current = await create_empty_session(user_id)
    refreshed = await list_sessions(user_id)
    return {
        "sessions": refreshed or [current],
        "current_thread_id": current["thread_id"],
    }


async def get_session(thread_id: str, user_id: str) -> dict | None:
    conn = await psycopg.AsyncConnection.connect(_require_postgres_url(), autocommit=True, row_factory=dict_row)
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT thread_id, user_id, title, created_at, updated_at, last_message_preview
                FROM agent_sessions
                WHERE thread_id = %s AND user_id = %s
                """,
                (thread_id, user_id.strip()),
            )
            row = await cur.fetchone()
            return _serialize_session_row(row) if row else None
    finally:
        await conn.close()


async def ensure_session_started(thread_id: str, user_id: str, initial_query: str) -> None:
    normalized_user = user_id.strip()
    if not normalized_user:
        return
    title = build_session_title(initial_query)
    preview = build_message_preview(initial_query)
    conn = await psycopg.AsyncConnection.connect(_require_postgres_url(), row_factory=dict_row)
    try:
        async with conn.transaction():
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT user_id FROM agent_sessions WHERE thread_id = %s FOR UPDATE",
                    (thread_id,),
                )
                existing = await cur.fetchone()
                if existing and existing["user_id"] != normalized_user:
                    raise SessionOwnershipError("该会话不属于当前用户。")
                if existing:
                    await cur.execute(
                        """
                        UPDATE agent_sessions
                        SET updated_at = NOW(),
                            title = CASE WHEN title = '新会话' THEN %s ELSE title END,
                            last_message_preview = CASE
                                WHEN last_message_preview = '' THEN %s
                                ELSE last_message_preview
                            END
                        WHERE thread_id = %s AND user_id = %s
                        """,
                        (title, preview, thread_id, normalized_user),
                    )
                else:
                    await cur.execute(
                        """
                        INSERT INTO agent_sessions (thread_id, user_id, title, last_message_preview)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (thread_id, normalized_user, title, preview),
                    )
    finally:
        await conn.close()


async def touch_session_after_reply(thread_id: str, user_id: str, query: str, answer: str) -> None:
    normalized_user = user_id.strip()
    if not normalized_user:
        return
    title = build_session_title(query)
    preview = build_message_preview(answer or query)
    conn = await psycopg.AsyncConnection.connect(_require_postgres_url(), autocommit=True)
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE agent_sessions
                SET
                  updated_at = NOW(),
                  title = CASE
                    WHEN title = '新会话' THEN %s
                    ELSE title
                  END,
                  last_message_preview = %s
                WHERE thread_id = %s AND user_id = %s
                """,
                (title, preview, thread_id, normalized_user),
            )
    finally:
        await conn.close()


async def append_session_message(
    thread_id: str,
    user_id: str,
    role: str,
    content: str,
    *,
    turn_id: str | None = None,
) -> None:
    normalized_user = user_id.strip()
    normalized_content = _normalize_whitespace(content)
    normalized_role = role.strip().lower()
    if not normalized_user or not normalized_content or normalized_role not in {"user", "assistant"}:
        return
    conn = await psycopg.AsyncConnection.connect(_require_postgres_url(), row_factory=dict_row)
    try:
        async with conn.transaction():
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT user_id FROM agent_sessions WHERE thread_id = %s FOR UPDATE",
                    (thread_id,),
                )
                owner = await cur.fetchone()
                if owner and owner["user_id"] != normalized_user:
                    raise SessionOwnershipError("该会话不属于当前用户。")
                await cur.execute(
                    """
                    INSERT INTO agent_session_messages (thread_id, user_id, turn_id, role, content)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (thread_id, turn_id, role) DO NOTHING
                    """,
                    (thread_id, normalized_user, turn_id, normalized_role, normalized_content),
                )
    finally:
        await conn.close()


async def load_session_messages(thread_id: str, user_id: str) -> list[dict]:
    conn = await psycopg.AsyncConnection.connect(_require_postgres_url(), autocommit=True, row_factory=dict_row)
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT turn_id, role, content, created_at
                FROM agent_session_messages
                WHERE thread_id = %s AND user_id = %s
                ORDER BY created_at ASC, id ASC
                """,
                (thread_id, user_id.strip()),
            )
            rows = await cur.fetchall()
            return [
                {
                    "turn_id": row["turn_id"],
                    "role": row["role"],
                    "content": row["content"],
                    "created_at": row["created_at"].isoformat() if isinstance(row["created_at"], datetime) else str(row["created_at"]),
                }
                for row in rows
            ]
    finally:
        await conn.close()


async def delete_session(thread_id: str, user_id: str) -> bool:
    normalized_user = user_id.strip()
    if not normalized_user or not thread_id.strip():
        return False
    conn = await psycopg.AsyncConnection.connect(_require_postgres_url(), autocommit=True)
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM agent_session_events WHERE thread_id = %s AND user_id = %s",
                (thread_id, normalized_user),
            )
            await cur.execute(
                "DELETE FROM agent_session_turns WHERE thread_id = %s AND user_id = %s",
                (thread_id, normalized_user),
            )
            await cur.execute(
                """
                DELETE FROM agent_session_messages
                WHERE thread_id = %s AND user_id = %s
                """,
                (thread_id, normalized_user),
            )
            await cur.execute(
                """
                DELETE FROM agent_sessions
                WHERE thread_id = %s AND user_id = %s
                """,
                (thread_id, normalized_user),
            )
            return cur.rowcount > 0
    finally:
        await conn.close()


async def start_session_turn(
    *,
    thread_id: str,
    user_id: str,
    turn_id: str,
    idempotency_key: str,
) -> str:
    """Create or recover a turn after the request reservation wins."""
    normalized_user = user_id.strip()
    conn = await psycopg.AsyncConnection.connect(_require_postgres_url(), row_factory=dict_row)
    try:
        async with conn.transaction():
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT user_id FROM agent_sessions WHERE thread_id = %s FOR UPDATE",
                    (thread_id,),
                )
                owner = await cur.fetchone()
                if owner and owner["user_id"] != normalized_user:
                    raise SessionOwnershipError("该会话不属于当前用户。")
                await cur.execute(
                    """
                    INSERT INTO agent_session_turns
                    (turn_id, thread_id, user_id, idempotency_key, status)
                    VALUES (%s, %s, %s, %s, 'running')
                    ON CONFLICT (idempotency_key) DO UPDATE SET updated_at = NOW()
                    RETURNING turn_id
                    """,
                    (turn_id, thread_id, normalized_user, idempotency_key),
                )
                row = await cur.fetchone()
                actual_turn_id = row["turn_id"]
                await cur.execute(
                    "SELECT thread_id, user_id FROM agent_session_turns WHERE turn_id = %s",
                    (actual_turn_id,),
                )
                actual = await cur.fetchone()
                if actual["thread_id"] != thread_id or actual["user_id"] != normalized_user:
                    raise SessionOwnershipError("幂等键已绑定到其他会话。")
                await cur.execute(
                    """
                    INSERT INTO agent_session_events
                    (event_id, thread_id, user_id, turn_id, sequence, event_key, event_type, content, payload_json)
                    VALUES (%s, %s, %s, %s, 1, 'turn_start', 'turn_start', '', %s)
                    ON CONFLICT (turn_id, sequence) DO NOTHING
                    """,
                    (str(uuid.uuid4()), thread_id, normalized_user, actual_turn_id, Jsonb({"status": "running"})),
                )
                return actual_turn_id
    finally:
        await conn.close()


async def finish_session_turn(turn_id: str, status: str) -> None:
    if status not in {"completed", "failed", "cancelled", "expired"}:
        raise ValueError("不支持的 turn 状态。")
    conn = await psycopg.AsyncConnection.connect(_require_postgres_url(), autocommit=True)
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE agent_session_turns SET status = %s, updated_at = NOW() WHERE turn_id = %s AND status = 'running'",
                (status, turn_id),
            )
    finally:
        await conn.close()


async def emit_session_event(
    *,
    turn_id: str,
    event_type: str,
    content: str = "",
    tool_name: str | None = None,
    tool_call_id: str | None = None,
    event_key: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Persist one bounded, idempotent event and return its sequence."""
    conn = await psycopg.AsyncConnection.connect(_require_postgres_url(), row_factory=dict_row)
    try:
        async with conn.transaction():
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT thread_id, user_id FROM agent_session_turns WHERE turn_id = %s FOR UPDATE",
                    (turn_id,),
                )
                turn = await cur.fetchone()
                if not turn:
                    return None
                if event_key:
                    await cur.execute(
                        "SELECT sequence FROM agent_session_events WHERE turn_id = %s AND event_key = %s",
                        (turn_id, event_key[:200]),
                    )
                    existing = await cur.fetchone()
                    if existing:
                        return {"sequence": existing["sequence"], "inserted": False}
                await cur.execute(
                    "SELECT COALESCE(MAX(sequence), 0) AS sequence, COUNT(*) AS event_count FROM agent_session_events WHERE turn_id = %s",
                    (turn_id,),
                )
                state = await cur.fetchone()
                if state["event_count"] >= 200:
                    raise SessionEventLimitError("该轮 Trace 已达到保存上限。")
                sequence = int(state["sequence"]) + 1
                bounded_content = _truncate(content, 4000)
                bounded_payload = dict(payload or {})
                if isinstance(bounded_payload.get("args"), str):
                    bounded_payload["args"] = _truncate(bounded_payload["args"], 2000)
                if isinstance(bounded_payload.get("result"), str):
                    bounded_payload["result"] = _truncate(bounded_payload["result"], 4000)
                await cur.execute(
                    """
                    INSERT INTO agent_session_events
                    (event_id, thread_id, user_id, turn_id, sequence, event_key, event_type, tool_name, tool_call_id, content, payload_json)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (turn_id, sequence) DO NOTHING
                    RETURNING sequence
                    """,
                    (
                        str(uuid.uuid4()), turn["thread_id"], turn["user_id"], turn_id,
                        sequence, event_key[:200] if event_key else None, event_type, tool_name, tool_call_id,
                        bounded_content, Jsonb(bounded_payload),
                    ),
                )
                inserted = await cur.fetchone()
                return {"sequence": sequence, "inserted": inserted is not None}
    finally:
        await conn.close()


async def load_session_replay(thread_id: str, user_id: str) -> list[dict]:
    conn = await psycopg.AsyncConnection.connect(_require_postgres_url(), row_factory=dict_row)
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id, turn_id, role, content, created_at
                FROM agent_session_messages
                WHERE thread_id = %s AND user_id = %s
                ORDER BY created_at ASC, id ASC
                """,
                (thread_id, user_id.strip()),
            )
            messages = await cur.fetchall()
            turn_ids = [row["turn_id"] for row in messages if row["turn_id"]]
            events_by_turn: dict[str, list[dict]] = {}
            if turn_ids:
                await cur.execute(
                    """
                    SELECT turn_id, sequence, event_type, tool_name, tool_call_id,
                           content, payload_json, status
                    FROM agent_session_events
                    WHERE turn_id = ANY(%s)
                    ORDER BY turn_id, sequence ASC
                    """,
                    (turn_ids,),
                )
                for row in await cur.fetchall():
                    events_by_turn.setdefault(row["turn_id"], []).append(
                        {
                            "sequence": row["sequence"],
                            "event_type": row["event_type"],
                            "tool_name": row["tool_name"],
                            "tool_call_id": row["tool_call_id"],
                            "content": row["content"],
                            "payload": row["payload_json"] or {},
                            "status": row["status"],
                        }
                    )
            replay = []
            assistant_turns = {row["turn_id"] for row in messages if row["turn_id"] and row["role"] == "assistant"}
            for row in messages:
                replay.append(
                    {
                        "turn_id": row["turn_id"],
                        "role": row["role"],
                        "content": row["content"],
                        "created_at": row["created_at"].isoformat() if isinstance(row["created_at"], datetime) else str(row["created_at"]),
                        "events": events_by_turn.get(row["turn_id"], []) if row["role"] == "assistant" else [],
                    }
                )
            known_turns = {row["turn_id"] for row in messages if row["turn_id"]}
            for turn_id, events in events_by_turn.items():
                if turn_id not in known_turns or turn_id not in assistant_turns:
                    await cur.execute(
                        "SELECT updated_at FROM agent_session_turns WHERE turn_id = %s",
                        (turn_id,),
                    )
                    turn = await cur.fetchone()
                    replay.append(
                        {
                            "turn_id": turn_id,
                            "role": "assistant",
                            "content": "",
                            "created_at": turn["updated_at"].isoformat() if turn and isinstance(turn["updated_at"], datetime) else "",
                            "events": events,
                        }
                    )
            return replay
    finally:
        await conn.close()
