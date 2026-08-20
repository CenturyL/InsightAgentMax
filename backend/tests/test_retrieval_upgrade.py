from __future__ import annotations

import concurrent.futures
import hashlib
import uuid

import httpx
import psycopg
import pytest
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from backend.core.config import settings
from backend.core import embedding as embedding_module
from backend.retrieval import pipeline
from backend.retrieval.reindex import rebuild_vector_collection
from backend.retrieval.postgres_store import (
    KnowledgeStoreError,
    activate_rebuilt_index,
    claim_source,
    create_building_index_version,
    get_active_index_version_unchecked,
    initialize_knowledge_store,
    list_active_chunks_for_reindex,
    mark_source_failed,
    purge_source_by_hash,
)
from backend.services import retrieval_usage_service


class KeywordEmbeddings(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)

    @staticmethod
    def _vector(text: str) -> list[float]:
        lowered = text.lower()
        return [
            1.0 if "上海" in lowered or "高新" in lowered else 0.0,
            1.0 if "北京" in lowered else 0.0,
            1.0 if "采购" in lowered else 0.0,
        ]


class DatabaseKeywordEmbeddings(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)

    @staticmethod
    def _vector(text: str) -> list[float]:
        vector = [0.0] * settings.EMBEDDING_DIMENSIONS
        lowered = text.lower()
        vector[0] = 1.0 if "上海" in lowered or "高新" in lowered else 0.0
        vector[1] = 1.0 if "北京" in lowered else 0.0
        vector[2] = 1.0 if "采购" in lowered else 0.0
        return vector


def _set_remote_defaults(monkeypatch) -> None:
    monkeypatch.setattr(settings, "RETRIEVAL_MODEL_PROVIDER", "siliconflow")
    monkeypatch.setattr(settings, "SILICONFLOW_API_KEY", "test-key")
    monkeypatch.setattr(settings, "SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
    monkeypatch.setattr(settings, "EMBEDDING_DIMENSIONS", 3)
    monkeypatch.setattr(settings, "RETRIEVAL_PROVIDER_MAX_RETRIES", 1)
    monkeypatch.setattr(settings, "RETRIEVAL_QUOTA_ENABLED", False)
    embedding_module.reset_retrieval_model_clients()


def test_siliconflow_embedding_batches_retries_and_validates(monkeypatch):
    _set_remote_defaults(monkeypatch)
    calls = 0
    reservations: list[str] = []
    settlements: list[tuple[str, bool]] = []
    monkeypatch.setattr(
        embedding_module,
        "reserve_retrieval_call",
        lambda **kwargs: reservations.append(kwargs["operation_id"]),
    )
    monkeypatch.setattr(
        embedding_module,
        "settle_retrieval_call",
        lambda operation_id, **kwargs: settlements.append((operation_id, bool(kwargs.get("failed")))),
    )

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        assert request.url.path == "/v1/embeddings"
        if calls == 1:
            return httpx.Response(429, json={"message": "busy"})
        return httpx.Response(
            200,
            json={
                "data": [
                    {"index": 0, "embedding": [1.0, 0.0, 0.0]},
                    {"index": 1, "embedding": [0.0, 1.0, 0.0]},
                ],
                "usage": {"total_tokens": 8},
            },
        )

    embedding_module._http_client = httpx.Client(transport=httpx.MockTransport(handler))
    monkeypatch.setattr(embedding_module.time, "sleep", lambda _: None)
    model = embedding_module.SiliconFlowEmbeddings()
    assert model.embed_documents(["上海", "北京"]) == [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    assert calls == 2
    assert len(reservations) == 1
    assert settlements == [(reservations[0], False)]


def test_siliconflow_reranker_restores_document_order(monkeypatch):
    _set_remote_defaults(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/rerank"
        return httpx.Response(
            200,
            json={
                "results": [
                    {"index": 1, "relevance_score": 0.9},
                    {"index": 0, "relevance_score": 0.7},
                ],
                "meta": {"billed_units": {"input_tokens": 12, "output_tokens": 1}},
            },
        )

    embedding_module._http_client = httpx.Client(transport=httpx.MockTransport(handler))
    docs = [Document(page_content="A"), Document(page_content="B"), Document(page_content="C")]
    assert [doc.page_content for doc in embedding_module.rerank_documents("query", docs, 2)] == ["B", "A"]


def test_bm25_chinese_recall_and_rrf(monkeypatch):
    rows = [
        {
            "content": "上海市高新技术企业认定申请条件和材料清单",
            "metadata": {"chunk_id": "shanghai"},
            "bm25_tokens": pipeline._tokenize_for_bm25("上海市高新技术企业认定申请条件和材料清单"),
        },
        {
            "content": "广州天气预报和交通信息",
            "metadata": {"chunk_id": "guangzhou"},
            "bm25_tokens": pipeline._tokenize_for_bm25("广州天气预报和交通信息"),
        },
        {
            "content": "北京市政府采购项目公告",
            "metadata": {"chunk_id": "beijing"},
            "bm25_tokens": pipeline._tokenize_for_bm25("北京市政府采购项目公告"),
        },
    ]
    monkeypatch.setattr(pipeline, "lexical_corpus_rows", lambda _filters=None: rows)
    results = pipeline.lexical_search_knowledge("上海高新技术企业申请条件", k=2, candidate_k=3)
    assert results[0].metadata["chunk_id"] == "shanghai"
    assert results[0].metadata["bm25_score"] > 0

    shared = Document(page_content="shared", metadata={"chunk_id": "shared"})
    fused = pipeline.reciprocal_rank_fusion(
        [
            [Document(page_content="dense", metadata={"chunk_id": "dense"}), shared],
            [shared, Document(page_content="lexical", metadata={"chunk_id": "lexical"})],
        ],
        limit=3,
    )
    assert fused[0].metadata["chunk_id"] == "shared"


def test_hybrid_search_reranks_rrf_candidates_once(monkeypatch):
    dense = [Document(page_content="dense", metadata={"chunk_id": "dense"})]
    lexical = [Document(page_content="lexical", metadata={"chunk_id": "lexical"})]
    rerank_calls: list[list[str]] = []
    monkeypatch.setattr(pipeline, "dense_search_knowledge", lambda *args, **kwargs: dense)
    monkeypatch.setattr(pipeline, "lexical_search_knowledge", lambda *args, **kwargs: lexical)
    monkeypatch.setattr(pipeline, "get_documents_by_source", lambda *args, **kwargs: [])

    def fake_rerank(_query: str, docs: list[Document], top_n: int) -> list[Document]:
        rerank_calls.append([doc.page_content for doc in docs])
        return list(reversed(docs))[:top_n]

    monkeypatch.setattr(pipeline, "rerank_documents", fake_rerank)
    results = pipeline.search_knowledge("query", k=2, candidate_k=10, strategy="hybrid_rerank")
    assert [doc.page_content for doc in results] == ["lexical", "dense"]
    assert len(rerank_calls) == 1


def test_multi_page_documents_have_unique_parent_ids(tmp_path):
    pages = [
        Document(page_content="第一页：生产变更需要审批。", metadata={"page": 0}),
        Document(page_content="第二页：生产变更需要回滚。", metadata={"page": 1}),
    ]
    parents, children = pipeline._build_chunk_documents(
        pages,
        str(tmp_path / "multi-page.pdf"),
        "a" * 64,
    )
    parent_ids = [str(parent.metadata["parent_id"]) for parent in parents]
    assert len(parent_ids) == len(set(parent_ids))
    assert all(child.metadata["parent_id"] in set(parent_ids) for child in children)


def test_markdown_headings_do_not_confuse_numbered_sentences():
    assert pipeline._heading_level("## 4. 留存与销毁") == "4. 留存与销毁"
    assert pipeline._heading_level("4. 留存与销毁") == "4. 留存与销毁"
    assert pipeline._heading_level("4. 测试数据应使用虚构实体，并通过稳定文档编号支持回归测试。") is None


@pytest.mark.skipif(not settings.POSTGRES_URL, reason="POSTGRES_URL 未配置")
def test_postgres_knowledge_ingest_is_idempotent_and_searchable(monkeypatch, tmp_path):
    initialize_knowledge_store()
    source = tmp_path / "shanghai-policy.txt"
    source.write_text("上海市高新技术企业申请条件和材料清单。企业需要提交研发证明。", encoding="utf-8")
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    monkeypatch.setattr(settings, "RETRIEVAL_QUOTA_ENABLED", False)
    monkeypatch.setattr(pipeline, "get_embedding_model", lambda: DatabaseKeywordEmbeddings())
    monkeypatch.setattr(pipeline, "rerank_documents", lambda _query, docs, top_n: docs[:top_n])
    try:
        first = pipeline.process_and_store_document(
            str(source),
            metadata_overrides={
                "source": source.name,
                "upload_name": source.name,
                "region": "上海",
                "source_type": "text",
            },
        )
        second = pipeline.process_and_store_document(
            str(source),
            metadata_overrides={
                "source": source.name,
                "upload_name": source.name,
                "region": "上海",
                "source_type": "text",
            },
        )
        assert first > 0
        assert second == 0
        bundle = pipeline.retrieve_knowledge_bundle(
            "上海高新技术企业申请条件",
            k=3,
            metadata_filters={"region": "上海", "source": source.name},
            strategy="hybrid_rerank",
        )
        assert bundle.docs
        assert bundle.parent_docs
        assert all(doc.metadata["region"] == "上海" for doc in bundle.docs)
    finally:
        purge_source_by_hash(source_hash)


@pytest.mark.skipif(not settings.POSTGRES_URL, reason="POSTGRES_URL 未配置")
def test_postgres_source_claim_has_single_concurrent_winner():
    initialize_knowledge_store()
    source_hash = hashlib.sha256(uuid.uuid4().bytes).hexdigest()

    def attempt():
        try:
            return claim_source(source_hash, "concurrent.txt", {"source_type": "text"})
        except KnowledgeStoreError as exc:
            return exc.code

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(lambda _: attempt(), range(20)))
        winners = [result for result in results if not isinstance(result, str)]
        assert len(winners) == 1
        assert results.count("KNOWLEDGE_IMPORT_IN_PROGRESS") == 19
        mark_source_failed(winners[0], "PYTEST_CLEANUP")
    finally:
        purge_source_by_hash(source_hash)


@pytest.mark.skipif(not settings.POSTGRES_URL, reason="POSTGRES_URL 未配置")
def test_postgres_reindex_is_idempotent_for_active_version():
    initialize_knowledge_store()
    result = rebuild_vector_collection(target_name=settings.KNOWLEDGE_INDEX_VERSION, batch_size=2)
    assert result["target"] == settings.KNOWLEDGE_INDEX_VERSION
    assert result["source_count"] == result["target_count"]
    assert result["embedded_count"] == 0


@pytest.mark.skipif(not settings.POSTGRES_URL, reason="POSTGRES_URL 未配置")
def test_postgres_reindex_rejects_source_drift(monkeypatch, tmp_path):
    initialize_knowledge_store()
    active = get_active_index_version_unchecked()
    expected_ids = {row["chunk_id"] for row in list_active_chunks_for_reindex()}
    version_name = f"pytest-reindex-{uuid.uuid4().hex}"
    target = create_building_index_version(
        version_name,
        settings.RETRIEVAL_MODEL_PROVIDER,
        settings.EMBEDDING_MODEL,
        settings.EMBEDDING_DIMENSIONS,
    )
    source = tmp_path / "reindex-drift.txt"
    source.write_text("重建并发漂移测试文档。", encoding="utf-8")
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    monkeypatch.setattr(settings, "RETRIEVAL_QUOTA_ENABLED", False)
    monkeypatch.setattr(pipeline, "get_embedding_model", lambda: DatabaseKeywordEmbeddings())
    try:
        assert pipeline.process_and_store_document(str(source), {"source": source.name}) > 0
        with pytest.raises(KnowledgeStoreError) as exc_info:
            activate_rebuilt_index(str(target["id"]), expected_ids)
        assert exc_info.value.code == "KNOWLEDGE_REINDEX_SOURCE_CHANGED"
        assert get_active_index_version_unchecked()["id"] == active["id"]
    finally:
        purge_source_by_hash(source_hash)
        with psycopg.connect(settings.POSTGRES_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM knowledge_index_versions WHERE id = %s AND status = 'building'", (target["id"],))


@pytest.mark.skipif(not settings.POSTGRES_URL, reason="POSTGRES_URL 未配置")
def test_retrieval_quota_is_atomic_and_settlement_idempotent(monkeypatch):
    model_id = f"pytest-retrieval-{uuid.uuid4().hex}"
    client_ip = f"pytest-ip-{uuid.uuid4().hex}"
    request_key = f"pytest-request-{uuid.uuid4().hex}"
    monkeypatch.setattr(settings, "RETRIEVAL_QUOTA_ENABLED", True)
    monkeypatch.setattr(settings, "USAGE_LIMIT_ENABLED", True)
    monkeypatch.setattr(settings, "RETRIEVAL_DAILY_CALL_LIMIT", 1)
    monkeypatch.setattr(settings, "RETRIEVAL_DAILY_CALL_LIMIT_PER_IP", 1)
    monkeypatch.setattr(settings, "RETRIEVAL_DAILY_TOKEN_LIMIT", 1000)
    monkeypatch.setattr(settings, "RETRIEVAL_DAILY_TOKEN_LIMIT_PER_IP", 1000)
    monkeypatch.setattr(settings, "RETRIEVAL_DAILY_COST_MICROUSD_LIMIT", 1000)
    monkeypatch.setattr(settings, "RETRIEVAL_DAILY_COST_MICROUSD_LIMIT_PER_IP", 1000)
    retrieval_usage_service.initialize_retrieval_usage_store()

    operation_ids = [f"pytest-op-{uuid.uuid4().hex}" for _ in range(8)]

    def attempt(operation_id: str):
        try:
            return retrieval_usage_service.reserve_retrieval_call(
                operation_id=operation_id,
                request_key=request_key,
                client_ip=client_ip,
                provider="siliconflow",
                operation_kind="embedding",
                model_id=model_id,
                estimated_tokens=100,
                price_per_million=10_000,
            )
        except retrieval_usage_service.RetrievalUsageError as exc:
            return exc.code

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(attempt, operation_ids))
        winners = [result for result in results if isinstance(result, retrieval_usage_service.RetrievalReservation)]
        assert len(winners) == 1
        assert results.count("RETRIEVAL_DAILY_CALL_LIMIT") == 7
        winner_id = winners[0].operation_id
        retrieval_usage_service.settle_retrieval_call(
            winner_id,
            actual_tokens=80,
            price_per_million=10_000,
            usage_source="provider",
        )
        retrieval_usage_service.settle_retrieval_call(
            winner_id,
            actual_tokens=80,
            price_per_million=10_000,
            usage_source="provider",
        )
        with psycopg.connect(settings.POSTGRES_URL, row_factory=psycopg.rows.dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT calls_used, tokens_used, reserved_calls
                    FROM retrieval_usage_daily
                    WHERE usage_date = CURRENT_DATE AND bucket = '__global__' AND model_id = %s
                    """,
                    (model_id,),
                )
                row = cur.fetchone()
                assert row == {"calls_used": 1, "tokens_used": 80, "reserved_calls": 0}
    finally:
        retrieval_usage_service.purge_retrieval_usage_by_request_keys([request_key])
        retrieval_usage_service.purge_retrieval_usage_by_request_keys([request_key])


@pytest.mark.skipif(not settings.POSTGRES_URL, reason="POSTGRES_URL 未配置")
def test_retrieval_cost_limit_and_stale_reservation_recovery(monkeypatch):
    model_id = f"pytest-retrieval-stale-{uuid.uuid4().hex}"
    client_ip = f"pytest-ip-{uuid.uuid4().hex}"
    operation_id = f"pytest-op-{uuid.uuid4().hex}"
    request_key = f"pytest-request-{uuid.uuid4().hex}"
    monkeypatch.setattr(settings, "RETRIEVAL_QUOTA_ENABLED", True)
    monkeypatch.setattr(settings, "USAGE_LIMIT_ENABLED", True)
    monkeypatch.setattr(settings, "RETRIEVAL_DAILY_CALL_LIMIT", 10)
    monkeypatch.setattr(settings, "RETRIEVAL_DAILY_CALL_LIMIT_PER_IP", 10)
    monkeypatch.setattr(settings, "RETRIEVAL_DAILY_TOKEN_LIMIT", 1000)
    monkeypatch.setattr(settings, "RETRIEVAL_DAILY_TOKEN_LIMIT_PER_IP", 1000)
    monkeypatch.setattr(settings, "RETRIEVAL_DAILY_COST_MICROUSD_LIMIT", 0)
    monkeypatch.setattr(settings, "RETRIEVAL_DAILY_COST_MICROUSD_LIMIT_PER_IP", 0)
    retrieval_usage_service.initialize_retrieval_usage_store()
    try:
        with pytest.raises(retrieval_usage_service.RetrievalUsageError) as exc_info:
            retrieval_usage_service.reserve_retrieval_call(
                operation_id=operation_id,
                request_key=request_key,
                client_ip=client_ip,
                provider="siliconflow",
                operation_kind="rerank",
                model_id=model_id,
                estimated_tokens=100,
                price_per_million=10_000,
            )
        assert exc_info.value.code == "RETRIEVAL_DAILY_COST_LIMIT"

        monkeypatch.setattr(settings, "RETRIEVAL_DAILY_COST_MICROUSD_LIMIT", 1000)
        monkeypatch.setattr(settings, "RETRIEVAL_DAILY_COST_MICROUSD_LIMIT_PER_IP", 1000)
        monkeypatch.setattr(settings, "RETRIEVAL_RESERVATION_TIMEOUT_SECONDS", 0)
        retrieval_usage_service.reserve_retrieval_call(
            operation_id=operation_id,
            request_key=request_key,
            client_ip=client_ip,
            provider="siliconflow",
            operation_kind="rerank",
            model_id=model_id,
            estimated_tokens=100,
            price_per_million=10_000,
        )
        retrieval_usage_service.initialize_retrieval_usage_store()
        with psycopg.connect(settings.POSTGRES_URL, row_factory=psycopg.rows.dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT status, actual_tokens FROM retrieval_call_usage WHERE operation_id = %s",
                    (operation_id,),
                )
                assert cur.fetchone() == {"status": "failed_estimated", "actual_tokens": 100}
    finally:
        retrieval_usage_service.purge_retrieval_usage_by_request_keys([request_key])
