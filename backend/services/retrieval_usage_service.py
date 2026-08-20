from __future__ import annotations

import math
from dataclasses import dataclass

import psycopg
from psycopg.rows import dict_row

from backend.core.config import settings


class RetrievalUsageError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class RetrievalReservation:
    operation_id: str
    status: str


_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS retrieval_usage_daily (
    usage_date DATE NOT NULL,
    bucket TEXT NOT NULL,
    model_id TEXT NOT NULL,
    calls_used BIGINT NOT NULL DEFAULT 0,
    tokens_used BIGINT NOT NULL DEFAULT 0,
    cost_microusd BIGINT NOT NULL DEFAULT 0,
    reserved_calls BIGINT NOT NULL DEFAULT 0,
    reserved_tokens BIGINT NOT NULL DEFAULT 0,
    reserved_cost_microusd BIGINT NOT NULL DEFAULT 0,
    price_microusd_per_million BIGINT NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (usage_date, bucket, model_id)
);

CREATE TABLE IF NOT EXISTS retrieval_call_usage (
    operation_id TEXT PRIMARY KEY,
    request_key TEXT NOT NULL,
    client_ip TEXT NOT NULL,
    provider TEXT NOT NULL,
    operation_kind TEXT NOT NULL CHECK (operation_kind IN ('embedding', 'rerank')),
    model_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'settled', 'failed_estimated')),
    estimated_tokens BIGINT NOT NULL DEFAULT 0,
    reserved_cost_microusd BIGINT NOT NULL DEFAULT 0,
    actual_tokens BIGINT NOT NULL DEFAULT 0,
    actual_cost_microusd BIGINT NOT NULL DEFAULT 0,
    usage_source TEXT NOT NULL DEFAULT 'estimated',
    usage_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '180 seconds'
);
ALTER TABLE retrieval_call_usage
    ADD COLUMN IF NOT EXISTS usage_date DATE NOT NULL DEFAULT CURRENT_DATE;
ALTER TABLE retrieval_call_usage
    ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '180 seconds';
ALTER TABLE retrieval_call_usage
    ADD COLUMN IF NOT EXISTS price_microusd_per_million BIGINT NOT NULL DEFAULT 0;
CREATE INDEX IF NOT EXISTS idx_retrieval_call_usage_created
ON retrieval_call_usage (created_at, status);
"""


def _require_url() -> str:
    if not settings.POSTGRES_URL:
        raise RetrievalUsageError("RETRIEVAL_USAGE_STORE_UNAVAILABLE", "检索额度服务暂不可用。")
    return settings.POSTGRES_URL


def initialize_retrieval_usage_store() -> None:
    if not settings.RETRIEVAL_QUOTA_ENABLED:
        return
    stale_ids: list[str] = []
    with psycopg.connect(_require_url(), autocommit=True, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(_CREATE_SQL)
            cur.execute(
                "SELECT operation_id FROM retrieval_call_usage WHERE status = 'pending' AND expires_at < NOW()"
            )
            stale_ids = [row["operation_id"] for row in cur.fetchall()]
    for operation_id in stale_ids:
        settle_retrieval_call(
            operation_id,
            actual_tokens=0,
            price_per_million=0,
            usage_source="estimated",
            failed=True,
        )


def estimate_cost_microusd(tokens: int, price_per_million: int) -> int:
    return int(math.ceil(max(0, tokens) * max(0, price_per_million) / 1_000_000))


def reserve_retrieval_call(
    *,
    operation_id: str,
    request_key: str,
    client_ip: str,
    provider: str,
    operation_kind: str,
    model_id: str,
    estimated_tokens: int,
    price_per_million: int,
) -> RetrievalReservation:
    if not settings.RETRIEVAL_QUOTA_ENABLED:
        return RetrievalReservation(operation_id=operation_id, status="pending")
    estimated_tokens = max(1, int(estimated_tokens))
    reserved_cost = estimate_cost_microusd(estimated_tokens, price_per_million)
    with psycopg.connect(_require_url(), row_factory=dict_row) as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT status FROM retrieval_call_usage WHERE operation_id = %s FOR UPDATE",
                    (operation_id,),
                )
                existing = cur.fetchone()
                if existing:
                    if existing["status"] == "pending":
                        raise RetrievalUsageError("RETRIEVAL_CALL_IN_PROGRESS", "相同检索调用正在执行。")
                    raise RetrievalUsageError("RETRIEVAL_CALL_ALREADY_SETTLED", "相同检索调用已完成。")

                cur.execute(
                    """
                    INSERT INTO retrieval_usage_daily (usage_date, bucket, model_id)
                    VALUES (CURRENT_DATE, '__global__', %s), (CURRENT_DATE, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (model_id, client_ip, model_id),
                )
                cur.execute(
                    """
                    SELECT bucket, calls_used, tokens_used, cost_microusd,
                           reserved_calls, reserved_tokens, reserved_cost_microusd
                    FROM retrieval_usage_daily
                    WHERE usage_date = CURRENT_DATE AND model_id = %s
                      AND bucket IN ('__global__', %s)
                    ORDER BY bucket
                    FOR UPDATE
                    """,
                    (model_id, client_ip),
                )
                rows = {row["bucket"]: row for row in cur.fetchall()}
                call_limits = {
                    "__global__": settings.RETRIEVAL_DAILY_CALL_LIMIT,
                    client_ip: settings.RETRIEVAL_DAILY_CALL_LIMIT_PER_IP,
                }
                token_limits = {
                    "__global__": settings.RETRIEVAL_DAILY_TOKEN_LIMIT,
                    client_ip: settings.RETRIEVAL_DAILY_TOKEN_LIMIT_PER_IP,
                }
                cost_limits = {
                    "__global__": settings.RETRIEVAL_DAILY_COST_MICROUSD_LIMIT,
                    client_ip: settings.RETRIEVAL_DAILY_COST_MICROUSD_LIMIT_PER_IP,
                }
                if settings.USAGE_LIMIT_ENABLED:
                    for bucket, row in rows.items():
                        if row["calls_used"] + row["reserved_calls"] + 1 > call_limits[bucket]:
                            raise RetrievalUsageError("RETRIEVAL_DAILY_CALL_LIMIT", "今日检索模型调用额度已用完。")
                        if row["tokens_used"] + row["reserved_tokens"] + estimated_tokens > token_limits[bucket]:
                            raise RetrievalUsageError("RETRIEVAL_DAILY_TOKEN_LIMIT", "今日检索模型 token 额度已用完。")
                        if row["cost_microusd"] + row["reserved_cost_microusd"] + reserved_cost > cost_limits[bucket]:
                            raise RetrievalUsageError("RETRIEVAL_DAILY_COST_LIMIT", "今日检索模型费用额度已用完。")

                    cur.execute(
                        """
                        UPDATE retrieval_usage_daily
                        SET reserved_calls = reserved_calls + 1,
                            reserved_tokens = reserved_tokens + %s,
                            reserved_cost_microusd = reserved_cost_microusd + %s,
                            updated_at = NOW()
                        WHERE usage_date = CURRENT_DATE AND model_id = %s
                          AND bucket IN ('__global__', %s)
                        """,
                        (estimated_tokens, reserved_cost, model_id, client_ip),
                    )
                else:
                    reserved_cost = 0
                cur.execute(
                    """
                    INSERT INTO retrieval_call_usage
                    (operation_id, request_key, client_ip, provider, operation_kind, model_id,
                     status, estimated_tokens, reserved_cost_microusd, price_microusd_per_million, expires_at)
                    VALUES (%s, %s, %s, %s, %s, %s, 'pending', %s, %s,
                            %s, NOW() + (%s * INTERVAL '1 second'))
                    """,
                    (
                        operation_id,
                        request_key,
                        client_ip,
                        provider,
                        operation_kind,
                        model_id,
                        estimated_tokens,
                        reserved_cost,
                        price_per_million,
                        settings.RETRIEVAL_RESERVATION_TIMEOUT_SECONDS,
                    ),
                )
    return RetrievalReservation(operation_id=operation_id, status="pending")


def settle_retrieval_call(
    operation_id: str,
    *,
    actual_tokens: int,
    price_per_million: int,
    usage_source: str,
    failed: bool = False,
) -> None:
    if not settings.RETRIEVAL_QUOTA_ENABLED:
        return
    actual_tokens = max(0, int(actual_tokens))
    with psycopg.connect(_require_url(), row_factory=dict_row) as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM retrieval_call_usage WHERE operation_id = %s FOR UPDATE",
                    (operation_id,),
                )
                row = cur.fetchone()
                if not row or row["status"] != "pending":
                    return
                price_snapshot = int(row["price_microusd_per_million"] or price_per_million)
                actual_cost = estimate_cost_microusd(actual_tokens, price_snapshot)
                settled_tokens = actual_tokens or int(row["estimated_tokens"])
                settled_cost = actual_cost or int(row["reserved_cost_microusd"])
                cur.execute(
                    """
                    UPDATE retrieval_usage_daily
                    SET reserved_calls = GREATEST(reserved_calls - 1, 0),
                        reserved_tokens = GREATEST(reserved_tokens - %s, 0),
                        reserved_cost_microusd = GREATEST(reserved_cost_microusd - %s, 0),
                        calls_used = calls_used + 1,
                        tokens_used = tokens_used + %s,
                        cost_microusd = cost_microusd + %s,
                        updated_at = NOW()
                    WHERE usage_date = %s AND model_id = %s
                      AND bucket IN ('__global__', %s)
                    """,
                    (
                        row["estimated_tokens"],
                        row["reserved_cost_microusd"],
                        settled_tokens,
                        settled_cost,
                        row["usage_date"],
                        row["model_id"],
                        row["client_ip"],
                    ),
                )
                cur.execute(
                    """
                    UPDATE retrieval_call_usage
                    SET status = %s, actual_tokens = %s, actual_cost_microusd = %s,
                        usage_source = %s, updated_at = NOW()
                    WHERE operation_id = %s
                    """,
                    (
                        "failed_estimated" if failed else "settled",
                        settled_tokens,
                        settled_cost,
                        usage_source,
                        operation_id,
                    ),
                )


def purge_retrieval_usage_by_request_keys(request_keys: list[str] | tuple[str, ...]) -> None:
    keys = list(dict.fromkeys(key.strip() for key in request_keys if key and key.strip()))
    if not keys or not settings.RETRIEVAL_QUOTA_ENABLED:
        return
    with psycopg.connect(_require_url(), row_factory=dict_row) as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM retrieval_call_usage WHERE request_key = ANY(%s) FOR UPDATE",
                    (keys,),
                )
                rows = cur.fetchall()
                deltas: dict[tuple, list[int]] = {}
                for row in rows:
                    for bucket in ("__global__", row["client_ip"]):
                        delta = deltas.setdefault((row["usage_date"], bucket, row["model_id"]), [0] * 6)
                        if row["status"] == "pending":
                            delta[3] += 1
                            delta[4] += row["estimated_tokens"]
                            delta[5] += row["reserved_cost_microusd"]
                        else:
                            delta[0] += 1
                            delta[1] += row["actual_tokens"]
                            delta[2] += row["actual_cost_microusd"]
                for (usage_date, bucket, model_id), delta in deltas.items():
                    cur.execute(
                        """
                        UPDATE retrieval_usage_daily
                        SET calls_used = calls_used - %s,
                            tokens_used = tokens_used - %s,
                            cost_microusd = cost_microusd - %s,
                            reserved_calls = reserved_calls - %s,
                            reserved_tokens = reserved_tokens - %s,
                            reserved_cost_microusd = reserved_cost_microusd - %s,
                            updated_at = NOW()
                        WHERE usage_date = %s AND bucket = %s AND model_id = %s
                          AND calls_used >= %s AND tokens_used >= %s AND cost_microusd >= %s
                          AND reserved_calls >= %s AND reserved_tokens >= %s
                          AND reserved_cost_microusd >= %s
                        """,
                        (*delta, usage_date, bucket, model_id, *delta),
                    )
                    if cur.rowcount != 1:
                        raise RetrievalUsageError("RETRIEVAL_USAGE_AGGREGATE_DRIFT", "检索额度聚合与调用事实不一致。")
                cur.execute("DELETE FROM retrieval_call_usage WHERE request_key = ANY(%s)", (keys,))
                for usage_date, bucket, model_id in deltas:
                    cur.execute(
                        """
                        DELETE FROM retrieval_usage_daily
                        WHERE usage_date = %s AND bucket = %s AND model_id = %s
                          AND calls_used = 0 AND tokens_used = 0 AND cost_microusd = 0
                          AND reserved_calls = 0 AND reserved_tokens = 0
                          AND reserved_cost_microusd = 0
                        """,
                        (usage_date, bucket, model_id),
                    )
