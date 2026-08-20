from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from backend.core.config import settings


class KnowledgeStoreError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class KnowledgeSourceClaim:
    source_id: str
    source_hash: str
    owner_token: str | None
    status: str
    chunk_count: int = 0


@dataclass(frozen=True)
class KnowledgeParentRecord:
    parent_id: str
    block_index: int
    content: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class KnowledgeChunkRecord:
    chunk_id: str
    parent_id: str
    chunk_index: int
    content: str
    metadata: dict[str, Any]
    bm25_tokens: list[str]
    embedding: list[float]


_FILTER_KEY_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]{1,64}$")


def _require_url() -> str:
    if not settings.POSTGRES_URL:
        raise KnowledgeStoreError("KNOWLEDGE_STORE_UNAVAILABLE", "PostgreSQL 未配置，知识库不可用。")
    return settings.POSTGRES_URL


def _vector_dimension() -> int:
    dimension = int(settings.EMBEDDING_DIMENSIONS)
    if dimension <= 0 or dimension > 4096:
        raise KnowledgeStoreError("KNOWLEDGE_VECTOR_DIMENSION_INVALID", "知识库向量维度配置无效。")
    return dimension


def _vector_literal(vector: Iterable[float]) -> str:
    values = [float(value) for value in vector]
    if len(values) != _vector_dimension():
        raise KnowledgeStoreError("KNOWLEDGE_VECTOR_DIMENSION_MISMATCH", "知识库向量维度不匹配。")
    return "[" + ",".join(format(value, ".17g") for value in values) + "]"


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _source_type(source_name: str, metadata: dict[str, Any]) -> str:
    value = str(metadata.get("source_type") or "").strip().lower()
    if value:
        return value[:32]
    suffix = source_name.rsplit(".", 1)[-1].lower() if "." in source_name else "text"
    return suffix[:32]


def _connect(*, row_factory=None):
    kwargs: dict[str, Any] = {}
    if row_factory is not None:
        kwargs["row_factory"] = row_factory
    return psycopg.connect(_require_url(), **kwargs)


def initialize_knowledge_store() -> None:
    dimension = _vector_dimension()
    schema_sql = f"""
    CREATE EXTENSION IF NOT EXISTS vector;

    CREATE TABLE IF NOT EXISTS knowledge_index_versions (
        id UUID PRIMARY KEY,
        version_name TEXT UNIQUE NOT NULL,
        provider TEXT NOT NULL,
        embedding_model TEXT NOT NULL,
        embedding_dimensions INTEGER NOT NULL,
        distance_strategy TEXT NOT NULL CHECK (distance_strategy = 'cosine'),
        status TEXT NOT NULL CHECK (status IN ('building', 'active', 'failed')),
        document_count INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE UNIQUE INDEX IF NOT EXISTS uq_knowledge_index_one_active
    ON knowledge_index_versions (status) WHERE status = 'active';

    CREATE TABLE IF NOT EXISTS knowledge_sources (
        id UUID PRIMARY KEY,
        source_hash TEXT UNIQUE NOT NULL,
        source_name TEXT NOT NULL,
        upload_name TEXT,
        source_type TEXT NOT NULL,
        metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
        status TEXT NOT NULL CHECK (status IN ('processing', 'ready', 'failed', 'deleting', 'deleted')),
        owner_token TEXT,
        lease_expires_at TIMESTAMPTZ,
        attempt_count INTEGER NOT NULL DEFAULT 0,
        parent_count INTEGER NOT NULL DEFAULT 0,
        chunk_count INTEGER NOT NULL DEFAULT 0,
        last_error_code TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE INDEX IF NOT EXISTS idx_knowledge_sources_status
    ON knowledge_sources (status, lease_expires_at);

    CREATE TABLE IF NOT EXISTS knowledge_parents (
        parent_id TEXT PRIMARY KEY,
        source_id UUID NOT NULL REFERENCES knowledge_sources(id) ON DELETE CASCADE,
        block_index INTEGER NOT NULL,
        content TEXT NOT NULL,
        content_hash TEXT NOT NULL,
        metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (source_id, block_index)
    );

    CREATE TABLE IF NOT EXISTS knowledge_chunks (
        index_version_id UUID NOT NULL REFERENCES knowledge_index_versions(id) ON DELETE CASCADE,
        chunk_id TEXT NOT NULL,
        source_id UUID NOT NULL REFERENCES knowledge_sources(id) ON DELETE CASCADE,
        parent_id TEXT NOT NULL REFERENCES knowledge_parents(parent_id) ON DELETE CASCADE,
        chunk_index INTEGER NOT NULL,
        content TEXT NOT NULL,
        content_hash TEXT NOT NULL,
        metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
        bm25_tokens TEXT[] NOT NULL DEFAULT '{{}}',
        embedding vector({dimension}) NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        PRIMARY KEY (index_version_id, chunk_id),
        UNIQUE (source_id, index_version_id, chunk_index)
    );
    CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_embedding_hnsw
    ON knowledge_chunks USING hnsw (embedding vector_cosine_ops);
    CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_metadata_gin
    ON knowledge_chunks USING gin (metadata jsonb_path_ops);
    CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_source
    ON knowledge_chunks (source_id, index_version_id);
    """
    with _connect() as conn:
        with conn.transaction():
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT pg_advisory_xact_lock(hashtextextended('knowledge-store-init', 0))")
                cur.execute(schema_sql)
                cur.execute(
                    "SELECT * FROM knowledge_index_versions WHERE status = 'active' FOR UPDATE"
                )
                active = cur.fetchone()
                if active is None:
                    cur.execute(
                        """
                        INSERT INTO knowledge_index_versions
                        (id, version_name, provider, embedding_model, embedding_dimensions,
                         distance_strategy, status)
                        VALUES (%s, %s, %s, %s, %s, 'cosine', 'active')
                        ON CONFLICT (version_name) DO NOTHING
                        RETURNING *
                        """,
                        (
                            uuid.uuid4(),
                            settings.KNOWLEDGE_INDEX_VERSION,
                            settings.RETRIEVAL_MODEL_PROVIDER,
                            settings.EMBEDDING_MODEL,
                            dimension,
                        ),
                    )
                    active = cur.fetchone()
                    if active is None:
                        cur.execute(
                            "SELECT * FROM knowledge_index_versions WHERE version_name = %s FOR UPDATE",
                            (settings.KNOWLEDGE_INDEX_VERSION,),
                        )
                        active = cur.fetchone()
                        if active and active["status"] != "active":
                            raise KnowledgeStoreError("KNOWLEDGE_INDEX_NOT_READY", "知识索引重建未完成，拒绝自动激活。")
                _validate_active_version(active)


def _validate_active_version(active: dict[str, Any] | None) -> None:
    if active is None:
        raise KnowledgeStoreError("KNOWLEDGE_INDEX_NOT_READY", "知识索引尚未初始化。")
    expected = {
        "version_name": settings.KNOWLEDGE_INDEX_VERSION,
        "provider": settings.RETRIEVAL_MODEL_PROVIDER,
        "embedding_model": settings.EMBEDDING_MODEL,
        "embedding_dimensions": _vector_dimension(),
        "distance_strategy": "cosine",
    }
    if any(str(active[key]) != str(value) for key, value in expected.items()):
        raise KnowledgeStoreError("KNOWLEDGE_INDEX_MODEL_MISMATCH", "知识索引与当前 Embedding 配置不匹配。")


def get_active_index_version() -> dict[str, Any]:
    active = get_active_index_version_unchecked()
    _validate_active_version(active)
    return active


def get_active_index_version_unchecked() -> dict[str, Any]:
    with _connect(row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM knowledge_index_versions WHERE status = 'active'")
            active = cur.fetchone()
    if active is None:
        raise KnowledgeStoreError("KNOWLEDGE_INDEX_NOT_READY", "知识索引尚未初始化。")
    return dict(active)


def create_building_index_version(
    version_name: str,
    provider: str,
    embedding_model: str,
    embedding_dimensions: int,
) -> dict[str, Any]:
    if embedding_dimensions != _vector_dimension():
        raise KnowledgeStoreError("KNOWLEDGE_VECTOR_DIMENSION_MISMATCH", "当前知识表不支持不同维度的原地重建。")
    with _connect(row_factory=dict_row) as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("SELECT pg_advisory_xact_lock(hashtextextended('knowledge-reindex', 0))")
                cur.execute(
                    "SELECT * FROM knowledge_index_versions WHERE version_name = %s FOR UPDATE",
                    (version_name,),
                )
                row = cur.fetchone()
                if row:
                    if row["status"] == "active":
                        return dict(row)
                    if (
                        row["provider"] != provider
                        or row["embedding_model"] != embedding_model
                        or row["embedding_dimensions"] != embedding_dimensions
                        or row["distance_strategy"] != "cosine"
                    ):
                        raise KnowledgeStoreError("KNOWLEDGE_INDEX_VERSION_CONFLICT", "索引版本名与已有模型签名冲突。")
                    cur.execute(
                        "UPDATE knowledge_index_versions SET status = 'building', updated_at = NOW() WHERE id = %s RETURNING *",
                        (row["id"],),
                    )
                    return dict(cur.fetchone())
                cur.execute(
                    """
                    INSERT INTO knowledge_index_versions
                    (id, version_name, provider, embedding_model, embedding_dimensions,
                     distance_strategy, status)
                    VALUES (%s, %s, %s, %s, %s, 'cosine', 'building')
                    RETURNING *
                    """,
                    (uuid.uuid4(), version_name, provider, embedding_model, embedding_dimensions),
                )
                return dict(cur.fetchone())


def list_active_chunks_for_reindex() -> list[dict[str, Any]]:
    active = get_active_index_version_unchecked()
    with _connect(row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.chunk_id, c.source_id, c.parent_id, c.chunk_index, c.content,
                       c.content_hash, c.metadata, c.bm25_tokens
                FROM knowledge_chunks c
                JOIN knowledge_sources s ON s.id = c.source_id
                WHERE c.index_version_id = %s AND s.status = 'ready'
                ORDER BY c.source_id, c.chunk_index
                """,
                (active["id"],),
            )
            return [dict(row) for row in cur.fetchall()]


def get_index_chunk_ids(index_version_id: str) -> set[str]:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT chunk_id FROM knowledge_chunks WHERE index_version_id = %s", (index_version_id,))
            return {row[0] for row in cur.fetchall()}


def upsert_reindexed_chunks(
    index_version_id: str,
    rows: list[dict[str, Any]],
    embeddings: list[list[float]],
) -> int:
    if len(rows) != len(embeddings):
        raise KnowledgeStoreError("KNOWLEDGE_REINDEX_BATCH_INVALID", "重建批次的文档与向量数量不一致。")
    inserted = 0
    with _connect(row_factory=dict_row) as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT status FROM knowledge_index_versions WHERE id = %s FOR UPDATE",
                    (index_version_id,),
                )
                version = cur.fetchone()
                if not version or version["status"] != "building":
                    raise KnowledgeStoreError("KNOWLEDGE_REINDEX_NOT_BUILDING", "目标知识索引不处于 building 状态。")
                for row, embedding in zip(rows, embeddings):
                    cur.execute(
                        """
                        INSERT INTO knowledge_chunks
                        (index_version_id, chunk_id, source_id, parent_id, chunk_index,
                         content, content_hash, metadata, bm25_tokens, embedding)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector)
                        ON CONFLICT (index_version_id, chunk_id) DO NOTHING
                        """,
                        (
                            index_version_id,
                            row["chunk_id"],
                            row["source_id"],
                            row["parent_id"],
                            row["chunk_index"],
                            row["content"],
                            row["content_hash"],
                            Jsonb(row["metadata"] or {}),
                            list(row["bm25_tokens"] or []),
                            _vector_literal(embedding),
                        ),
                    )
                    inserted += cur.rowcount
    return inserted


def activate_rebuilt_index(index_version_id: str, expected_chunk_ids: set[str]) -> None:
    with _connect(row_factory=dict_row) as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("SELECT pg_advisory_xact_lock(hashtextextended('knowledge-reindex', 0))")
                cur.execute("SELECT pg_advisory_xact_lock(hashtextextended('knowledge-index-switch', 0))")
                cur.execute(
                    "SELECT * FROM knowledge_index_versions WHERE id = %s FOR UPDATE",
                    (index_version_id,),
                )
                target = cur.fetchone()
                if not target:
                    raise KnowledgeStoreError("KNOWLEDGE_INDEX_NOT_FOUND", "目标知识索引不存在。")
                if target["status"] == "active":
                    return
                if target["status"] != "building":
                    raise KnowledgeStoreError("KNOWLEDGE_REINDEX_NOT_BUILDING", "目标知识索引不处于 building 状态。")
                cur.execute("SELECT id FROM knowledge_index_versions WHERE status = 'active' FOR UPDATE")
                active = cur.fetchone()
                if not active:
                    raise KnowledgeStoreError("KNOWLEDGE_INDEX_NOT_READY", "知识索引尚未初始化。")
                cur.execute(
                    """
                    SELECT c.chunk_id
                    FROM knowledge_chunks c
                    JOIN knowledge_sources s ON s.id = c.source_id
                    WHERE c.index_version_id = %s AND s.status = 'ready'
                    """,
                    (active["id"],),
                )
                current_chunk_ids = {row["chunk_id"] for row in cur.fetchall()}
                if current_chunk_ids != expected_chunk_ids:
                    raise KnowledgeStoreError("KNOWLEDGE_REINDEX_SOURCE_CHANGED", "重建期间知识源发生变化，请继续增量重建。")
                cur.execute(
                    "SELECT chunk_id FROM knowledge_chunks WHERE index_version_id = %s",
                    (index_version_id,),
                )
                actual_chunk_ids = {row["chunk_id"] for row in cur.fetchall()}
                if actual_chunk_ids != expected_chunk_ids:
                    raise KnowledgeStoreError("KNOWLEDGE_REINDEX_INCOMPLETE", "目标知识索引的 Chunk 集合不完整。")
                cur.execute(
                    "UPDATE knowledge_index_versions SET status = 'failed', updated_at = NOW() WHERE id = %s",
                    (active["id"],),
                )
                cur.execute(
                    """
                    UPDATE knowledge_index_versions
                    SET status = 'active', document_count = %s, updated_at = NOW()
                    WHERE id = %s
                    """,
                    (len(expected_chunk_ids), index_version_id),
                )
                if active and str(active["id"]) != str(index_version_id):
                    cur.execute("DELETE FROM knowledge_index_versions WHERE id = %s", (active["id"],))


def claim_source(source_hash: str, source_name: str, metadata: dict[str, Any]) -> KnowledgeSourceClaim:
    normalized_hash = source_hash.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", normalized_hash):
        raise KnowledgeStoreError("KNOWLEDGE_SOURCE_HASH_INVALID", "知识源哈希格式无效。")
    normalized_name = source_name.strip() or normalized_hash
    owner_token = uuid.uuid4().hex
    with _connect(row_factory=dict_row) as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))", (normalized_hash,))
                cur.execute(
                    "SELECT * FROM knowledge_sources WHERE source_hash = %s FOR UPDATE",
                    (normalized_hash,),
                )
                row = cur.fetchone()
                if row and row["status"] == "ready":
                    return KnowledgeSourceClaim(str(row["id"]), normalized_hash, None, "ready", row["chunk_count"])
                if row and row["status"] == "processing" and row["lease_expires_at"] and row["lease_expires_at"] > datetime.now(row["lease_expires_at"].tzinfo):
                    raise KnowledgeStoreError("KNOWLEDGE_IMPORT_IN_PROGRESS", "相同文件正在录入，请稍后重试。")
                if row:
                    cur.execute(
                        """
                        UPDATE knowledge_sources
                        SET source_name = %s, upload_name = %s, source_type = %s,
                            metadata = %s, status = 'processing', owner_token = %s,
                            lease_expires_at = NOW() + (%s * INTERVAL '1 second'),
                            attempt_count = attempt_count + 1, last_error_code = NULL,
                            updated_at = NOW()
                        WHERE id = %s
                        RETURNING id
                        """,
                        (
                            normalized_name,
                            str(metadata.get("upload_name") or "") or None,
                            _source_type(normalized_name, metadata),
                            Jsonb(metadata),
                            owner_token,
                            settings.KNOWLEDGE_IMPORT_LEASE_SECONDS,
                            row["id"],
                        ),
                    )
                    source_id = str(cur.fetchone()["id"])
                else:
                    source_id = str(uuid.uuid4())
                    cur.execute(
                        """
                        INSERT INTO knowledge_sources
                        (id, source_hash, source_name, upload_name, source_type, metadata,
                         status, owner_token, lease_expires_at, attempt_count)
                        VALUES (%s, %s, %s, %s, %s, %s, 'processing', %s,
                                NOW() + (%s * INTERVAL '1 second'), 1)
                        """,
                        (
                            source_id,
                            normalized_hash,
                            normalized_name,
                            str(metadata.get("upload_name") or "") or None,
                            _source_type(normalized_name, metadata),
                            Jsonb(metadata),
                            owner_token,
                            settings.KNOWLEDGE_IMPORT_LEASE_SECONDS,
                        ),
                    )
    return KnowledgeSourceClaim(source_id, normalized_hash, owner_token, "processing")


def mark_source_failed(claim: KnowledgeSourceClaim, error_code: str) -> None:
    if not claim.owner_token:
        return
    with _connect() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE knowledge_sources
                    SET status = 'failed', owner_token = NULL, lease_expires_at = NULL,
                        last_error_code = %s, updated_at = NOW()
                    WHERE id = %s AND status = 'processing' AND owner_token = %s
                    """,
                    (error_code[:100], claim.source_id, claim.owner_token),
                )


def commit_source_documents(
    claim: KnowledgeSourceClaim,
    parents: list[KnowledgeParentRecord],
    chunks: list[KnowledgeChunkRecord],
) -> int:
    if not claim.owner_token:
        return claim.chunk_count
    if not parents or not chunks:
        raise KnowledgeStoreError("KNOWLEDGE_DOCUMENT_EMPTY", "文档没有可写入的有效内容。")
    parent_ids = {parent.parent_id for parent in parents}
    if len(parent_ids) != len(parents):
        raise KnowledgeStoreError("KNOWLEDGE_PARENT_DUPLICATED", "Parent ID 重复。")
    if any(chunk.parent_id not in parent_ids for chunk in chunks):
        raise KnowledgeStoreError("KNOWLEDGE_PARENT_MISSING", "Chunk 引用了不存在的 Parent。")
    if len({chunk.chunk_id for chunk in chunks}) != len(chunks):
        raise KnowledgeStoreError("KNOWLEDGE_CHUNK_DUPLICATED", "Chunk ID 重复。")

    with _connect(row_factory=dict_row) as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("SELECT pg_advisory_xact_lock_shared(hashtextextended('knowledge-index-switch', 0))")
                cur.execute("SELECT * FROM knowledge_index_versions WHERE status = 'active'")
                active = cur.fetchone()
                _validate_active_version(active)
                cur.execute(
                    "SELECT status, owner_token FROM knowledge_sources WHERE id = %s FOR UPDATE",
                    (claim.source_id,),
                )
                source = cur.fetchone()
                if not source or source["status"] != "processing" or source["owner_token"] != claim.owner_token:
                    raise KnowledgeStoreError("KNOWLEDGE_IMPORT_LOST", "知识导入处理权已失效。")

                for parent in parents:
                    cur.execute(
                        """
                        INSERT INTO knowledge_parents
                        (parent_id, source_id, block_index, content, content_hash, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (parent_id) DO NOTHING
                        """,
                        (
                            parent.parent_id,
                            claim.source_id,
                            parent.block_index,
                            parent.content,
                            _content_hash(parent.content),
                            Jsonb(parent.metadata),
                        ),
                    )
                    if cur.rowcount == 0:
                        cur.execute(
                            "SELECT source_id, content_hash FROM knowledge_parents WHERE parent_id = %s",
                            (parent.parent_id,),
                        )
                        existing = cur.fetchone()
                        if not existing or str(existing["source_id"]) != claim.source_id or existing["content_hash"] != _content_hash(parent.content):
                            raise KnowledgeStoreError("KNOWLEDGE_PARENT_CONFLICT", "Parent ID 与现有内容冲突。")

                for chunk in chunks:
                    metadata = dict(chunk.metadata)
                    metadata["chunk_id"] = chunk.chunk_id
                    metadata["parent_id"] = chunk.parent_id
                    metadata["source_hash"] = claim.source_hash
                    cur.execute(
                        """
                        INSERT INTO knowledge_chunks
                        (index_version_id, chunk_id, source_id, parent_id, chunk_index,
                         content, content_hash, metadata, bm25_tokens, embedding)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector)
                        ON CONFLICT (index_version_id, chunk_id) DO NOTHING
                        """,
                        (
                            active["id"],
                            chunk.chunk_id,
                            claim.source_id,
                            chunk.parent_id,
                            chunk.chunk_index,
                            chunk.content,
                            _content_hash(chunk.content),
                            Jsonb(metadata),
                            chunk.bm25_tokens,
                            _vector_literal(chunk.embedding),
                        ),
                    )
                    if cur.rowcount == 0:
                        cur.execute(
                            """
                            SELECT source_id, parent_id, content_hash
                            FROM knowledge_chunks
                            WHERE index_version_id = %s AND chunk_id = %s
                            """,
                            (active["id"], chunk.chunk_id),
                        )
                        existing = cur.fetchone()
                        if (
                            not existing
                            or str(existing["source_id"]) != claim.source_id
                            or existing["parent_id"] != chunk.parent_id
                            or existing["content_hash"] != _content_hash(chunk.content)
                        ):
                            raise KnowledgeStoreError("KNOWLEDGE_CHUNK_CONFLICT", "Chunk ID 与现有内容冲突。")

                cur.execute(
                    """
                    UPDATE knowledge_sources
                    SET status = 'ready', owner_token = NULL, lease_expires_at = NULL,
                        parent_count = %s, chunk_count = %s, last_error_code = NULL,
                        updated_at = NOW()
                    WHERE id = %s AND status = 'processing' AND owner_token = %s
                    """,
                    (len(parents), len(chunks), claim.source_id, claim.owner_token),
                )
                if cur.rowcount != 1:
                    raise KnowledgeStoreError("KNOWLEDGE_IMPORT_LOST", "知识导入提交时处理权已失效。")
                cur.execute(
                    """
                    UPDATE knowledge_index_versions
                    SET document_count = (
                        SELECT COUNT(*) FROM knowledge_chunks WHERE index_version_id = %s
                    ), updated_at = NOW()
                    WHERE id = %s
                    """,
                    (active["id"], active["id"]),
                )
    return len(chunks)


def _metadata_filter_sql(metadata_filters: dict[str, Any] | None) -> tuple[str, list[Any]]:
    clauses: list[str] = []
    params: list[Any] = []
    for key, value in (metadata_filters or {}).items():
        if key.startswith("_") or value is None or value == "":
            continue
        if not _FILTER_KEY_PATTERN.fullmatch(key):
            raise KnowledgeStoreError("KNOWLEDGE_FILTER_INVALID", "知识库过滤字段不合法。")
        if isinstance(value, (dict, list, tuple, set)):
            raise KnowledgeStoreError("KNOWLEDGE_FILTER_INVALID", "知识库过滤值只支持标量。")
        clauses.append("c.metadata ->> %s = %s")
        params.extend((key, str(value)))
    return (" AND " + " AND ".join(clauses)) if clauses else "", params


def dense_search_rows(
    query_embedding: list[float],
    *,
    limit: int,
    metadata_filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    active = get_active_index_version()
    filter_sql, filter_params = _metadata_filter_sql(metadata_filters)
    vector = _vector_literal(query_embedding)
    with _connect(row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT c.chunk_id, c.parent_id, c.content, c.metadata,
                       c.embedding <=> %s::vector AS distance
                FROM knowledge_chunks c
                JOIN knowledge_sources s ON s.id = c.source_id
                WHERE s.status = 'ready' AND c.index_version_id = %s
                {filter_sql}
                ORDER BY c.embedding <=> %s::vector
                LIMIT %s
                """,
                [vector, active["id"], *filter_params, vector, max(1, int(limit))],
            )
            return [dict(row) for row in cur.fetchall()]


def lexical_corpus_rows(metadata_filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    active = get_active_index_version()
    filter_sql, filter_params = _metadata_filter_sql(metadata_filters)
    max_chunks = max(1, int(settings.BM25_MAX_CORPUS_CHUNKS))
    with _connect(row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT c.chunk_id, c.parent_id, c.content, c.metadata, c.bm25_tokens
                FROM knowledge_chunks c
                JOIN knowledge_sources s ON s.id = c.source_id
                WHERE s.status = 'ready' AND c.index_version_id = %s
                {filter_sql}
                ORDER BY c.chunk_id
                LIMIT %s
                """,
                [active["id"], *filter_params, max_chunks + 1],
            )
            rows = [dict(row) for row in cur.fetchall()]
    if len(rows) > max_chunks:
        raise KnowledgeStoreError("KNOWLEDGE_BM25_CORPUS_TOO_LARGE", "关键词检索语料超过安全上限。")
    return rows


def get_documents_by_source_rows(source: str, limit: int) -> list[dict[str, Any]]:
    active = get_active_index_version()
    with _connect(row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.chunk_id, c.parent_id, c.content, c.metadata
                FROM knowledge_chunks c
                JOIN knowledge_sources s ON s.id = c.source_id
                WHERE s.status = 'ready' AND c.index_version_id = %s
                  AND (c.metadata ->> 'source' = %s OR c.metadata ->> 'upload_name' = %s)
                ORDER BY c.chunk_index
                LIMIT %s
                """,
                (active["id"], source, source, max(1, int(limit))),
            )
            return [dict(row) for row in cur.fetchall()]


def has_document_source_value(source: str) -> bool:
    active = get_active_index_version()
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM knowledge_chunks c
                JOIN knowledge_sources s ON s.id = c.source_id
                WHERE s.status = 'ready' AND c.index_version_id = %s
                  AND c.metadata ->> 'source' = %s
                LIMIT 1
                """,
                (active["id"], source),
            )
            return cur.fetchone() is not None


def get_parent_rows(parent_ids: list[str]) -> list[dict[str, Any]]:
    ordered_ids = list(dict.fromkeys(parent_id for parent_id in parent_ids if parent_id))
    if not ordered_ids:
        return []
    with _connect(row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT parent_id, content, metadata
                FROM knowledge_parents
                WHERE parent_id = ANY(%s)
                """,
                (ordered_ids,),
            )
            found = {row["parent_id"]: dict(row) for row in cur.fetchall()}
    return [found[parent_id] for parent_id in ordered_ids if parent_id in found]


def reconcile_expired_imports() -> int:
    with _connect() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE knowledge_sources
                    SET status = 'failed', owner_token = NULL, lease_expires_at = NULL,
                        last_error_code = 'KNOWLEDGE_IMPORT_EXPIRED', updated_at = NOW()
                    WHERE status = 'processing' AND lease_expires_at < NOW()
                    """
                )
                return cur.rowcount


def knowledge_store_stats() -> dict[str, Any]:
    active = get_active_index_version()
    with _connect(row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM knowledge_sources WHERE status = 'ready') AS source_count,
                    (SELECT COUNT(*) FROM knowledge_parents) AS parent_count,
                    (SELECT COUNT(*) FROM knowledge_chunks WHERE index_version_id = %s) AS chunk_count
                """,
                (active["id"],),
            )
            row = dict(cur.fetchone())
    row["index_version"] = active["version_name"]
    row["embedding_model"] = active["embedding_model"]
    row["embedding_dimensions"] = active["embedding_dimensions"]
    return row


def purge_source_by_hash(source_hash: str) -> None:
    normalized_hash = source_hash.strip().lower()
    with _connect(row_factory=dict_row) as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))", (normalized_hash,))
                cur.execute("SELECT pg_advisory_xact_lock_shared(hashtextextended('knowledge-index-switch', 0))")
                cur.execute("DELETE FROM knowledge_sources WHERE source_hash = %s", (normalized_hash,))
                cur.execute(
                    """
                    UPDATE knowledge_index_versions v
                    SET document_count = counts.chunk_count, updated_at = NOW()
                    FROM (
                        SELECT v2.id, COUNT(c.chunk_id)::integer AS chunk_count
                        FROM knowledge_index_versions v2
                        LEFT JOIN knowledge_chunks c ON c.index_version_id = v2.id
                        GROUP BY v2.id
                    ) counts
                    WHERE v.id = counts.id
                    """
                )
