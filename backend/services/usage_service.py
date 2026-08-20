from __future__ import annotations

"""PostgreSQL-backed request quota, idempotency and thread-lock state."""

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

import psycopg
from psycopg.rows import dict_row

from backend.core.config import settings


class UsageServiceError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class RequestReservation:
    key: str
    request_hash: str
    status: str
    turn_id: str | None = None
    response: list[dict[str, Any]] | None = None


_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS model_usage_daily (
    usage_date DATE NOT NULL,
    bucket TEXT NOT NULL,
    model_calls_used INTEGER NOT NULL DEFAULT 0,
    reserved_calls INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (usage_date, bucket)
);

CREATE TABLE IF NOT EXISTS model_call_reservations (
    idempotency_key TEXT PRIMARY KEY,
    request_hash TEXT NOT NULL,
    client_ip TEXT NOT NULL,
    thread_id TEXT,
    status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'released', 'expired')),
    reserved_calls INTEGER NOT NULL DEFAULT 1,
    model_calls INTEGER NOT NULL DEFAULT 0,
    response_json JSONB,
    error_code TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);
ALTER TABLE model_call_reservations
    ADD COLUMN IF NOT EXISTS turn_id TEXT;
ALTER TABLE model_call_reservations
    ADD COLUMN IF NOT EXISTS model_id TEXT;
ALTER TABLE model_call_reservations
    ADD COLUMN IF NOT EXISTS reserved_tokens INTEGER NOT NULL DEFAULT 0;
ALTER TABLE model_call_reservations
    ADD COLUMN IF NOT EXISTS total_tokens INTEGER NOT NULL DEFAULT 0;
ALTER TABLE model_call_reservations
    ADD COLUMN IF NOT EXISTS reserved_cost_microunits BIGINT NOT NULL DEFAULT 0;
ALTER TABLE model_call_reservations
    ADD COLUMN IF NOT EXISTS total_cost_microunits BIGINT NOT NULL DEFAULT 0;
CREATE INDEX IF NOT EXISTS idx_model_call_reservations_expiry
ON model_call_reservations (status, expires_at);

CREATE TABLE IF NOT EXISTS model_usage_daily_by_model (
    usage_date DATE NOT NULL,
    bucket TEXT NOT NULL,
    model_id TEXT NOT NULL,
    input_tokens BIGINT NOT NULL DEFAULT 0,
    cache_hit_tokens BIGINT NOT NULL DEFAULT 0,
    cache_miss_tokens BIGINT NOT NULL DEFAULT 0,
    output_tokens BIGINT NOT NULL DEFAULT 0,
    total_tokens BIGINT NOT NULL DEFAULT 0,
    cost_microunits BIGINT NOT NULL DEFAULT 0,
    reserved_tokens BIGINT NOT NULL DEFAULT 0,
    reserved_cost_microunits BIGINT NOT NULL DEFAULT 0,
    model_calls_used INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (usage_date, bucket, model_id)
);

CREATE TABLE IF NOT EXISTS model_call_usage (
    id BIGSERIAL PRIMARY KEY,
    idempotency_key TEXT NOT NULL,
    turn_id TEXT,
    call_index INTEGER NOT NULL,
    model_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    input_tokens BIGINT NOT NULL DEFAULT 0,
    cache_hit_tokens BIGINT NOT NULL DEFAULT 0,
    cache_miss_tokens BIGINT NOT NULL DEFAULT 0,
    output_tokens BIGINT NOT NULL DEFAULT 0,
    total_tokens BIGINT NOT NULL DEFAULT 0,
    cost_microunits BIGINT NOT NULL DEFAULT 0,
    price_input_microunits BIGINT NOT NULL DEFAULT 0,
    price_output_microunits BIGINT NOT NULL DEFAULT 0,
    usage_source TEXT NOT NULL CHECK (usage_source IN ('provider', 'estimated', 'unknown')),
    status TEXT NOT NULL DEFAULT 'settled',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (idempotency_key, call_index)
);
ALTER TABLE model_call_usage
    ADD COLUMN IF NOT EXISTS price_input_microunits BIGINT NOT NULL DEFAULT 0;
ALTER TABLE model_call_usage
    ADD COLUMN IF NOT EXISTS price_output_microunits BIGINT NOT NULL DEFAULT 0;

CREATE TABLE IF NOT EXISTS request_thread_locks (
    thread_id TEXT PRIMARY KEY,
    request_key TEXT NOT NULL,
    acquired_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);
"""


def request_body_hash(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _require_url() -> str:
    if not settings.POSTGRES_URL:
        raise UsageServiceError("USAGE_STORE_UNAVAILABLE", "额度服务暂不可用，请稍后再试。")
    return settings.POSTGRES_URL


async def initialize_usage_store() -> None:
    conn = await psycopg.AsyncConnection.connect(_require_url(), autocommit=True)
    try:
        async with conn.cursor() as cur:
            await cur.execute(_CREATE_SQL)
    finally:
        await conn.close()


async def _connect():
    return await psycopg.AsyncConnection.connect(_require_url(), row_factory=dict_row)


async def _release_expired_reservations(cur, now: datetime | None = None) -> None:
    await cur.execute(
        """
        SELECT idempotency_key, client_ip, reserved_calls, model_id, reserved_tokens, reserved_cost_microunits
        FROM model_call_reservations
        WHERE status = 'pending' AND expires_at < NOW()
        FOR UPDATE
        """,
    )
    expired = await cur.fetchall()
    for row in expired:
        if row["reserved_calls"] > 0:
            await cur.execute(
                """
                UPDATE model_usage_daily
                SET reserved_calls = GREATEST(reserved_calls - 1, 0), updated_at = NOW()
                WHERE usage_date = CURRENT_DATE AND bucket IN ('__global__', %s)
                """,
                (row["client_ip"],),
            )
        if row["model_id"] and (row["reserved_tokens"] or row["reserved_cost_microunits"]):
            await cur.execute(
                """
                UPDATE model_usage_daily_by_model
                SET reserved_tokens = GREATEST(reserved_tokens - %s, 0),
                    reserved_cost_microunits = GREATEST(reserved_cost_microunits - %s, 0),
                    updated_at = NOW()
                WHERE usage_date = CURRENT_DATE AND model_id = %s AND bucket IN ('__global__', %s)
                """,
                (row["reserved_tokens"], row["reserved_cost_microunits"], row["model_id"], row["client_ip"]),
            )
        await cur.execute(
            """
            UPDATE model_call_reservations
            SET status = 'expired', reserved_calls = 0, reserved_tokens = 0, reserved_cost_microunits = 0,
                updated_at = NOW(), error_code = 'REQUEST_EXPIRED'
            WHERE idempotency_key = %s
            """,
            (row["idempotency_key"],),
        )


async def begin_request(
    *,
    idempotency_key: str,
    request_hash: str,
    client_ip: str,
    thread_id: str | None,
    model_id: str | None = None,
    estimated_tokens: int = 0,
    price_input_microunits: int | None = None,
    price_output_microunits: int | None = None,
) -> RequestReservation:
    """Atomically validate idempotency and reserve the first model-call slot."""
    if len(idempotency_key) > 200:
        raise UsageServiceError("INVALID_IDEMPOTENCY_KEY", "幂等键长度不合法。")
    conn = await _connect()
    now = datetime.now(timezone.utc)
    try:
        async with conn.transaction():
            async with conn.cursor() as cur:
                requested_tokens = max(0, int(estimated_tokens))
                if requested_tokens > settings.MODEL_REQUEST_TOKEN_LIMIT:
                    raise UsageServiceError("MODEL_TOKEN_LIMIT_EXCEEDED", "本次请求预估 token 已超过上限。")
                estimated_tokens = requested_tokens
                estimated_cost = (
                    estimated_tokens
                    * max(
                        settings.MODEL_INPUT_PRICE_MICROUSD_PER_MILLION
                        if price_input_microunits is None
                        else max(0, price_input_microunits),
                        settings.MODEL_OUTPUT_PRICE_MICROUSD_PER_MILLION
                        if price_output_microunits is None
                        else max(0, price_output_microunits),
                    )
                ) // 1_000_000
                if estimated_cost > settings.MODEL_REQUEST_COST_MICROUSD_LIMIT:
                    raise UsageServiceError("MODEL_COST_LIMIT_EXCEEDED", "本次请求预估费用已超过上限。")
                await cur.execute(
                    "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                    (idempotency_key,),
                )
                await _release_expired_reservations(cur, now)
                await cur.execute(
                    "SELECT * FROM model_call_reservations WHERE idempotency_key = %s FOR UPDATE",
                    (idempotency_key,),
                )
                existing = await cur.fetchone()
                if existing:
                    if existing["request_hash"] != request_hash:
                        raise UsageServiceError("IDEMPOTENCY_KEY_REUSED", "幂等键已用于另一份请求。")
                    if existing["status"] == "completed":
                        return RequestReservation(
                            idempotency_key,
                            request_hash,
                            "completed",
                            existing["turn_id"],
                            existing["response_json"] or [],
                        )
                    if existing["status"] == "pending":
                        raise UsageServiceError("REQUEST_IN_PROGRESS", "相同请求正在处理中，请稍后重试。")
                    raise UsageServiceError("REQUEST_NOT_REPLAYABLE", "该请求已结束且不能重放，请生成新的幂等键。")

                if model_id:
                    await cur.execute(
                        """
                        INSERT INTO model_usage_daily_by_model (usage_date, bucket, model_id)
                        VALUES (CURRENT_DATE, '__global__', %s), (CURRENT_DATE, %s, %s)
                        ON CONFLICT DO NOTHING
                        """,
                        (model_id, client_ip, model_id),
                    )
                    await cur.execute(
                        """
                        SELECT bucket, total_tokens, reserved_tokens, cost_microunits, reserved_cost_microunits
                        FROM model_usage_daily_by_model
                        WHERE usage_date = CURRENT_DATE AND model_id = %s AND bucket IN ('__global__', %s)
                        FOR UPDATE
                        """,
                        (model_id, client_ip),
                    )
                    model_buckets = {row["bucket"]: row for row in await cur.fetchall()}
                    token_limits = {
                        "__global__": settings.MODEL_DAILY_TOKEN_LIMIT,
                        client_ip: settings.MODEL_DAILY_TOKEN_LIMIT_PER_IP,
                    }
                    cost_limits = {
                        "__global__": settings.MODEL_DAILY_COST_MICROUSD_LIMIT,
                        client_ip: settings.MODEL_DAILY_COST_MICROUSD_LIMIT_PER_IP,
                    }
                    if settings.USAGE_LIMIT_ENABLED:
                        if any(
                            row["total_tokens"] + row["reserved_tokens"] + estimated_tokens > token_limits[bucket]
                            or row["cost_microunits"] + row["reserved_cost_microunits"] + estimated_cost > cost_limits[bucket]
                            for bucket, row in model_buckets.items()
                        ):
                            raise UsageServiceError("DAILY_MODEL_LIMIT_EXCEEDED", "所选模型今日 token 或费用额度已用完。")
                        await cur.execute(
                            """
                            UPDATE model_usage_daily_by_model
                            SET reserved_tokens = reserved_tokens + %s,
                                reserved_cost_microunits = reserved_cost_microunits + %s,
                                updated_at = NOW()
                            WHERE usage_date = CURRENT_DATE AND model_id = %s AND bucket IN ('__global__', %s)
                            """,
                            (estimated_tokens, estimated_cost, model_id, client_ip),
                        )

                await cur.execute(
                    """
                    INSERT INTO model_usage_daily (usage_date, bucket)
                    VALUES (CURRENT_DATE, '__global__'), (CURRENT_DATE, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (client_ip,),
                )
                await cur.execute(
                    """
                    SELECT bucket, model_calls_used, reserved_calls
                    FROM model_usage_daily
                    WHERE usage_date = CURRENT_DATE AND bucket IN ('__global__', %s)
                    ORDER BY bucket
                    FOR UPDATE
                    """,
                    (client_ip,),
                )
                buckets = {row["bucket"]: row for row in await cur.fetchall()}
                limits = {"__global__": settings.DAILY_MODEL_CALL_LIMIT, client_ip: settings.DAILY_MODEL_CALL_LIMIT_PER_IP}
                if settings.USAGE_LIMIT_ENABLED:
                    if any(
                        row["model_calls_used"] + row["reserved_calls"] >= limits[bucket]
                        for bucket, row in buckets.items()
                    ):
                        raise UsageServiceError("DAILY_LIMIT_EXCEEDED", "今日模型额度已用完，请明天再试。")
                    await cur.execute(
                        """
                        UPDATE model_usage_daily
                        SET reserved_calls = reserved_calls + 1, updated_at = NOW()
                        WHERE usage_date = CURRENT_DATE AND bucket IN ('__global__', %s)
                        """,
                        (client_ip,),
                    )
                turn_id = str(uuid.uuid4()) if thread_id else None
                await cur.execute(
                    """
                    INSERT INTO model_call_reservations
                    (idempotency_key, request_hash, client_ip, thread_id, turn_id, status, reserved_calls, expires_at)
                    VALUES (%s, %s, %s, %s, %s, 'pending', %s, NOW() + (%s * INTERVAL '1 second'))
                    """,
                    (
                        idempotency_key,
                        request_hash,
                        client_ip,
                        thread_id,
                        turn_id,
                        1 if settings.USAGE_LIMIT_ENABLED else 0,
                        settings.IDEMPOTENCY_PENDING_TIMEOUT_SECONDS,
                    ),
                )
                await cur.execute(
                    """
                    UPDATE model_call_reservations
                    SET model_id = %s, reserved_tokens = %s, reserved_cost_microunits = %s
                    WHERE idempotency_key = %s
                    """,
                    (
                        model_id,
                        estimated_tokens if settings.USAGE_LIMIT_ENABLED else 0,
                        estimated_cost if settings.USAGE_LIMIT_ENABLED else 0,
                        idempotency_key,
                    ),
                )
                return RequestReservation(idempotency_key, request_hash, "pending", turn_id)
    finally:
        await conn.close()


async def consume_model_call(idempotency_key: str) -> int:
    """Convert the admission reservation or atomically consume another slot."""
    conn = await _connect()
    try:
        async with conn.transaction():
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT client_ip, status, reserved_calls FROM model_call_reservations WHERE idempotency_key = %s FOR UPDATE",
                    (idempotency_key,),
                )
                reservation = await cur.fetchone()
                if not reservation or reservation["status"] != "pending":
                    raise UsageServiceError("REQUEST_NOT_ACTIVE", "请求已结束，不能继续调用模型。")
                await cur.execute(
                    """
                    INSERT INTO model_usage_daily (usage_date, bucket)
                    VALUES (CURRENT_DATE, '__global__'), (CURRENT_DATE, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (reservation["client_ip"],),
                )
                await cur.execute(
                    """
                    SELECT bucket, model_calls_used, reserved_calls
                    FROM model_usage_daily
                    WHERE usage_date = CURRENT_DATE AND bucket IN ('__global__', %s)
                    ORDER BY bucket
                    FOR UPDATE
                    """,
                    (reservation["client_ip"],),
                )
                buckets = {row["bucket"]: row for row in await cur.fetchall()}
                limits = {"__global__": settings.DAILY_MODEL_CALL_LIMIT, reservation["client_ip"]: settings.DAILY_MODEL_CALL_LIMIT_PER_IP}
                if reservation["reserved_calls"] > 0:
                    await cur.execute(
                        """
                        UPDATE model_usage_daily
                        SET reserved_calls = GREATEST(reserved_calls - 1, 0), model_calls_used = model_calls_used + 1, updated_at = NOW()
                        WHERE usage_date = CURRENT_DATE AND bucket IN ('__global__', %s)
                        """,
                        (reservation["client_ip"],),
                    )
                    await cur.execute(
                        "UPDATE model_call_reservations SET reserved_calls = 0, model_calls = model_calls + 1, updated_at = NOW() WHERE idempotency_key = %s",
                        (idempotency_key,),
                    )
                    await cur.execute(
                        "SELECT model_calls FROM model_call_reservations WHERE idempotency_key = %s",
                        (idempotency_key,),
                    )
                    return (await cur.fetchone())["model_calls"]
                if settings.USAGE_LIMIT_ENABLED and any(row["model_calls_used"] >= limits[bucket] for bucket, row in buckets.items()):
                    raise UsageServiceError("DAILY_LIMIT_EXCEEDED", "今日模型额度已用完，请明天再试。")
                await cur.execute(
                    """
                    UPDATE model_usage_daily
                    SET model_calls_used = model_calls_used + 1, updated_at = NOW()
                    WHERE usage_date = CURRENT_DATE AND bucket IN ('__global__', %s)
                    """,
                    (reservation["client_ip"],),
                )
                await cur.execute(
                    "UPDATE model_call_reservations SET model_calls = model_calls + 1, updated_at = NOW() WHERE idempotency_key = %s",
                    (idempotency_key,),
                )
                await cur.execute(
                    "SELECT model_calls FROM model_call_reservations WHERE idempotency_key = %s",
                    (idempotency_key,),
                )
                return (await cur.fetchone())["model_calls"]
    finally:
        await conn.close()


async def record_model_usage(
    idempotency_key: str,
    *,
    call_index: int,
    model_id: str,
    provider: str,
    input_tokens: int = 0,
    cache_hit_tokens: int = 0,
    cache_miss_tokens: int = 0,
    output_tokens: int = 0,
    usage_source: str = "unknown",
    cost_microunits: int = 0,
    price_input_microunits: int | None = None,
    price_output_microunits: int | None = None,
) -> None:
    """Persist one provider usage record; retries are idempotent by call index."""
    if usage_source not in {"provider", "estimated", "unknown"}:
        usage_source = "unknown"
    total_tokens = max(0, input_tokens) + max(0, output_tokens)
    conn = await _connect()
    try:
        async with conn.transaction():
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT client_ip, turn_id, status FROM model_call_reservations WHERE idempotency_key = %s FOR UPDATE",
                    (idempotency_key,),
                )
                reservation = await cur.fetchone()
                if not reservation or reservation["status"] != "pending":
                    return
                await cur.execute(
                    """
                    INSERT INTO model_call_usage
                    (idempotency_key, turn_id, call_index, model_id, provider,
                     input_tokens, cache_hit_tokens, cache_miss_tokens, output_tokens,
                     total_tokens, cost_microunits, price_input_microunits,
                     price_output_microunits, usage_source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (idempotency_key, call_index) DO NOTHING
                    RETURNING id
                    """,
                    (
                        idempotency_key, reservation["turn_id"], call_index, model_id, provider,
                        max(0, input_tokens), max(0, cache_hit_tokens), max(0, cache_miss_tokens),
                        max(0, output_tokens), total_tokens, max(0, cost_microunits),
                        max(0, price_input_microunits if price_input_microunits is not None else settings.MODEL_INPUT_PRICE_MICROUSD_PER_MILLION),
                        max(0, price_output_microunits if price_output_microunits is not None else settings.MODEL_OUTPUT_PRICE_MICROUSD_PER_MILLION),
                        usage_source,
                    ),
                )
                if await cur.fetchone() is None:
                    return
                await cur.execute(
                    """
                    INSERT INTO model_usage_daily_by_model (usage_date, bucket, model_id)
                    VALUES (CURRENT_DATE, '__global__', %s), (CURRENT_DATE, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (model_id, reservation["client_ip"], model_id),
                )
                await cur.execute(
                    """
                    UPDATE model_usage_daily_by_model
                    SET input_tokens = input_tokens + %s,
                        cache_hit_tokens = cache_hit_tokens + %s,
                        cache_miss_tokens = cache_miss_tokens + %s,
                        output_tokens = output_tokens + %s,
                        total_tokens = total_tokens + %s,
                        cost_microunits = cost_microunits + %s,
                        model_calls_used = model_calls_used + 1,
                        updated_at = NOW()
                    WHERE usage_date = CURRENT_DATE AND model_id = %s AND bucket IN ('__global__', %s)
                    """,
                    (
                        max(0, input_tokens), max(0, cache_hit_tokens), max(0, cache_miss_tokens),
                        max(0, output_tokens), total_tokens, max(0, cost_microunits),
                        model_id, reservation["client_ip"],
                    ),
                )
                await cur.execute(
                    """
                    UPDATE model_call_reservations
                    SET total_tokens = total_tokens + %s,
                        total_cost_microunits = total_cost_microunits + %s,
                        updated_at = NOW()
                    WHERE idempotency_key = %s
                    """,
                    (total_tokens, max(0, cost_microunits), idempotency_key),
                )
    finally:
        await conn.close()


async def finish_request(idempotency_key: str, *, response: list[dict[str, Any]] | None, success: bool) -> None:
    conn = await _connect()
    try:
        async with conn.transaction():
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT client_ip, model_id, reserved_tokens, reserved_cost_microunits, reserved_calls, status FROM model_call_reservations WHERE idempotency_key = %s FOR UPDATE",
                    (idempotency_key,),
                )
                row = await cur.fetchone()
                if not row or row["status"] != "pending":
                    return
                if row["reserved_calls"] > 0:
                    await cur.execute(
                        """
                        UPDATE model_usage_daily
                        SET reserved_calls = GREATEST(reserved_calls - 1, 0), updated_at = NOW()
                        WHERE usage_date = CURRENT_DATE AND bucket IN ('__global__', %s)
                        """,
                        (row["client_ip"],),
                    )
                if row["model_id"] and (row["reserved_tokens"] or row["reserved_cost_microunits"]):
                    await cur.execute(
                        """
                        UPDATE model_usage_daily_by_model
                        SET reserved_tokens = GREATEST(reserved_tokens - %s, 0),
                            reserved_cost_microunits = GREATEST(reserved_cost_microunits - %s, 0),
                            updated_at = NOW()
                        WHERE usage_date = CURRENT_DATE AND model_id = %s AND bucket IN ('__global__', %s)
                        """,
                        (row["reserved_tokens"], row["reserved_cost_microunits"], row["model_id"], row["client_ip"]),
                    )
                await cur.execute(
                    """
                    UPDATE model_call_reservations
                    SET status = %s, reserved_calls = 0, reserved_tokens = 0, reserved_cost_microunits = 0,
                        response_json = %s, updated_at = NOW(), error_code = %s
                    WHERE idempotency_key = %s
                    """,
                    ("completed" if success else "failed", json.dumps(response or [], ensure_ascii=False), None if success else "REQUEST_FAILED", idempotency_key),
                )
    finally:
        await conn.close()


async def purge_request_usage(idempotency_keys: list[str] | tuple[str, ...]) -> None:
    """Delete selected requests and exactly reverse their daily aggregates.

    This is intended for tests and operator cleanup. It is idempotent: keys that
    no longer exist have no effect, and aggregate updates are derived from the
    reservation/usage fact rows locked in the same transaction.
    """
    keys = list(dict.fromkeys(key.strip() for key in idempotency_keys if key and key.strip()))
    if not keys:
        return
    conn = await _connect()
    try:
        async with conn.transaction():
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT idempotency_key, client_ip, created_at::date AS usage_date,
                           model_calls, reserved_calls, model_id, reserved_tokens,
                           reserved_cost_microunits
                    FROM model_call_reservations
                    WHERE idempotency_key = ANY(%s)
                    FOR UPDATE
                    """,
                    (keys,),
                )
                reservations = await cur.fetchall()
                if not reservations:
                    await cur.execute("DELETE FROM request_thread_locks WHERE request_key = ANY(%s)", (keys,))
                    return

                reservation_by_key = {row["idempotency_key"]: row for row in reservations}
                daily_deltas: dict[tuple[date, str], list[int]] = {}
                model_deltas: dict[tuple[date, str, str], list[int]] = {}

                for row in reservations:
                    for bucket in ("__global__", row["client_ip"]):
                        daily_delta = daily_deltas.setdefault((row["usage_date"], bucket), [0, 0])
                        daily_delta[0] += row["model_calls"]
                        daily_delta[1] += row["reserved_calls"]
                        if row["model_id"]:
                            model_delta = model_deltas.setdefault(
                                (row["usage_date"], bucket, row["model_id"]),
                                [0] * 9,
                            )
                            model_delta[6] += row["reserved_tokens"]
                            model_delta[7] += row["reserved_cost_microunits"]

                await cur.execute(
                    """
                    SELECT idempotency_key, created_at::date AS usage_date, model_id,
                           SUM(input_tokens) AS input_tokens,
                           SUM(cache_hit_tokens) AS cache_hit_tokens,
                           SUM(cache_miss_tokens) AS cache_miss_tokens,
                           SUM(output_tokens) AS output_tokens,
                           SUM(total_tokens) AS total_tokens,
                           SUM(cost_microunits) AS cost_microunits,
                           COUNT(*) AS model_calls_used
                    FROM model_call_usage
                    WHERE idempotency_key = ANY(%s)
                    GROUP BY idempotency_key, created_at::date, model_id
                    """,
                    (keys,),
                )
                for row in await cur.fetchall():
                    reservation = reservation_by_key.get(row["idempotency_key"])
                    if reservation is None:
                        continue
                    for bucket in ("__global__", reservation["client_ip"]):
                        model_delta = model_deltas.setdefault(
                            (row["usage_date"], bucket, row["model_id"]),
                            [0] * 9,
                        )
                        model_delta[0] += row["input_tokens"]
                        model_delta[1] += row["cache_hit_tokens"]
                        model_delta[2] += row["cache_miss_tokens"]
                        model_delta[3] += row["output_tokens"]
                        model_delta[4] += row["total_tokens"]
                        model_delta[5] += row["cost_microunits"]
                        model_delta[8] += row["model_calls_used"]

                for (usage_date, bucket), (model_calls, reserved_calls) in daily_deltas.items():
                    await cur.execute(
                        """
                        UPDATE model_usage_daily
                        SET model_calls_used = model_calls_used - %s,
                            reserved_calls = reserved_calls - %s,
                            updated_at = NOW()
                        WHERE usage_date = %s AND bucket = %s
                          AND model_calls_used >= %s AND reserved_calls >= %s
                        """,
                        (model_calls, reserved_calls, usage_date, bucket, model_calls, reserved_calls),
                    )
                    if cur.rowcount != 1:
                        raise UsageServiceError("USAGE_AGGREGATE_DRIFT", "额度聚合与请求事实不一致，需要先执行对账。")

                for (usage_date, bucket, model_id), delta in model_deltas.items():
                    await cur.execute(
                        """
                        UPDATE model_usage_daily_by_model
                        SET input_tokens = input_tokens - %s,
                            cache_hit_tokens = cache_hit_tokens - %s,
                            cache_miss_tokens = cache_miss_tokens - %s,
                            output_tokens = output_tokens - %s,
                            total_tokens = total_tokens - %s,
                            cost_microunits = cost_microunits - %s,
                            reserved_tokens = reserved_tokens - %s,
                            reserved_cost_microunits = reserved_cost_microunits - %s,
                            model_calls_used = model_calls_used - %s,
                            updated_at = NOW()
                        WHERE usage_date = %s AND bucket = %s AND model_id = %s
                          AND input_tokens >= %s AND cache_hit_tokens >= %s
                          AND cache_miss_tokens >= %s AND output_tokens >= %s
                          AND total_tokens >= %s AND cost_microunits >= %s
                          AND reserved_tokens >= %s AND reserved_cost_microunits >= %s
                          AND model_calls_used >= %s
                        """,
                        (*delta, usage_date, bucket, model_id, *delta),
                    )
                    if cur.rowcount != 1:
                        raise UsageServiceError("USAGE_AGGREGATE_DRIFT", "模型额度聚合与调用事实不一致，需要先执行对账。")

                await cur.execute("DELETE FROM request_thread_locks WHERE request_key = ANY(%s)", (keys,))
                await cur.execute("DELETE FROM model_call_usage WHERE idempotency_key = ANY(%s)", (keys,))
                await cur.execute("DELETE FROM model_call_reservations WHERE idempotency_key = ANY(%s)", (keys,))
                await cur.execute(
                    """
                    DELETE FROM model_usage_daily
                    WHERE bucket <> '__global__' AND model_calls_used = 0 AND reserved_calls = 0
                    """
                )
                await cur.execute(
                    """
                    DELETE FROM model_usage_daily_by_model
                    WHERE bucket <> '__global__' AND input_tokens = 0 AND cache_hit_tokens = 0
                      AND cache_miss_tokens = 0 AND output_tokens = 0 AND total_tokens = 0
                      AND cost_microunits = 0 AND reserved_tokens = 0
                      AND reserved_cost_microunits = 0 AND model_calls_used = 0
                    """
                )
    finally:
        await conn.close()


async def reconcile_usage_aggregates(usage_date: date | None = None) -> None:
    """Rebuild one day's aggregate quota rows from reservation and usage facts."""
    target_date = usage_date or datetime.now(timezone.utc).date()
    conn = await _connect()
    try:
        async with conn.transaction():
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    LOCK TABLE model_call_reservations, model_call_usage,
                               model_usage_daily, model_usage_daily_by_model
                    IN SHARE ROW EXCLUSIVE MODE
                    """
                )
                await cur.execute("DELETE FROM model_usage_daily WHERE usage_date = %s", (target_date,))
                await cur.execute(
                    """
                    WITH per_ip AS (
                        SELECT client_ip AS bucket,
                               COALESCE(SUM(model_calls), 0)::integer AS model_calls_used,
                               COALESCE(SUM(CASE WHEN status = 'pending' THEN reserved_calls ELSE 0 END), 0)::integer AS reserved_calls
                        FROM model_call_reservations
                        WHERE created_at::date = %s
                        GROUP BY client_ip
                    ), all_usage AS (
                        SELECT '__global__'::text AS bucket,
                               COALESCE(SUM(model_calls), 0)::integer AS model_calls_used,
                               COALESCE(SUM(CASE WHEN status = 'pending' THEN reserved_calls ELSE 0 END), 0)::integer AS reserved_calls
                        FROM model_call_reservations
                        WHERE created_at::date = %s
                    )
                    INSERT INTO model_usage_daily (usage_date, bucket, model_calls_used, reserved_calls)
                    SELECT %s, bucket, model_calls_used, reserved_calls FROM all_usage
                    UNION ALL
                    SELECT %s, bucket, model_calls_used, reserved_calls FROM per_ip
                    """,
                    (target_date, target_date, target_date, target_date),
                )

                await cur.execute("DELETE FROM model_usage_daily_by_model WHERE usage_date = %s", (target_date,))
                await cur.execute(
                    """
                    WITH usage_scoped AS (
                        SELECT scope.bucket, u.model_id, u.input_tokens, u.cache_hit_tokens,
                               u.cache_miss_tokens, u.output_tokens, u.total_tokens,
                               u.cost_microunits
                        FROM model_call_usage u
                        LEFT JOIN model_call_reservations r USING (idempotency_key)
                        CROSS JOIN LATERAL (
                            SELECT '__global__'::text AS bucket
                            UNION ALL
                            SELECT r.client_ip WHERE r.client_ip IS NOT NULL
                        ) scope
                        WHERE u.created_at::date = %s
                    ), usage_totals AS (
                        SELECT bucket, model_id,
                               SUM(input_tokens)::bigint AS input_tokens,
                               SUM(cache_hit_tokens)::bigint AS cache_hit_tokens,
                               SUM(cache_miss_tokens)::bigint AS cache_miss_tokens,
                               SUM(output_tokens)::bigint AS output_tokens,
                               SUM(total_tokens)::bigint AS total_tokens,
                               SUM(cost_microunits)::bigint AS cost_microunits,
                               COUNT(*)::integer AS model_calls_used
                        FROM usage_scoped
                        GROUP BY bucket, model_id
                    ), reservation_scoped AS (
                        SELECT scope.bucket, r.model_id, r.reserved_tokens,
                               r.reserved_cost_microunits
                        FROM model_call_reservations r
                        CROSS JOIN LATERAL (
                            VALUES ('__global__'::text), (r.client_ip)
                        ) scope(bucket)
                        WHERE r.created_at::date = %s AND r.status = 'pending' AND r.model_id IS NOT NULL
                    ), reservation_totals AS (
                        SELECT bucket, model_id,
                               SUM(reserved_tokens)::bigint AS reserved_tokens,
                               SUM(reserved_cost_microunits)::bigint AS reserved_cost_microunits
                        FROM reservation_scoped
                        GROUP BY bucket, model_id
                    )
                    INSERT INTO model_usage_daily_by_model (
                        usage_date, bucket, model_id, input_tokens, cache_hit_tokens,
                        cache_miss_tokens, output_tokens, total_tokens, cost_microunits,
                        reserved_tokens, reserved_cost_microunits, model_calls_used
                    )
                    SELECT %s, COALESCE(u.bucket, r.bucket), COALESCE(u.model_id, r.model_id),
                           COALESCE(u.input_tokens, 0), COALESCE(u.cache_hit_tokens, 0),
                           COALESCE(u.cache_miss_tokens, 0), COALESCE(u.output_tokens, 0),
                           COALESCE(u.total_tokens, 0), COALESCE(u.cost_microunits, 0),
                           COALESCE(r.reserved_tokens, 0), COALESCE(r.reserved_cost_microunits, 0),
                           COALESCE(u.model_calls_used, 0)
                    FROM usage_totals u
                    FULL OUTER JOIN reservation_totals r USING (bucket, model_id)
                    """,
                    (target_date, target_date, target_date),
                )
    finally:
        await conn.close()


async def acquire_thread_lock(thread_id: str, request_key: str) -> bool:
    conn = await _connect()
    try:
        async with conn.transaction():
            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM request_thread_locks WHERE expires_at < NOW()")
                await cur.execute(
                    """
                    INSERT INTO request_thread_locks (thread_id, request_key, expires_at)
                    VALUES (%s, %s, NOW() + (%s * INTERVAL '1 second'))
                    ON CONFLICT (thread_id) DO NOTHING
                    RETURNING thread_id
                    """,
                    (thread_id, request_key, settings.THREAD_LOCK_TIMEOUT_SECONDS),
                )
                return await cur.fetchone() is not None
    finally:
        await conn.close()


async def release_thread_lock(thread_id: str, request_key: str) -> None:
    conn = await _connect()
    try:
        async with conn.transaction():
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM request_thread_locks WHERE thread_id = %s AND request_key = %s",
                    (thread_id, request_key),
                )
    finally:
        await conn.close()
