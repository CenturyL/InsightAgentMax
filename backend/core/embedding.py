from __future__ import annotations

import hashlib
import json
import time
from typing import Any

import httpx
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings

from backend.core.config import settings
from backend.services.retrieval_context import next_retrieval_operation_id
from backend.services.retrieval_usage_service import (
    reserve_retrieval_call,
    settle_retrieval_call,
)


class RetrievalProviderError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


_embedding_instance: Embeddings | None = None
_reranker_instance: HuggingFaceCrossEncoder | None = None
_http_client: httpx.Client | None = None


def _resolve_device(preferred: str) -> str:
    preferred = (preferred or "auto").strip().lower()
    if preferred != "auto":
        return preferred
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_built() and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


def _provider() -> str:
    provider = (settings.RETRIEVAL_MODEL_PROVIDER or "local").strip().lower()
    if provider not in {"local", "siliconflow"}:
        raise RetrievalProviderError("RETRIEVAL_PROVIDER_INVALID", "检索模型提供方配置无效。")
    return provider


def _siliconflow_api_key() -> str:
    api_key = (settings.SILICONFLOW_API_KEY or "").strip()
    if not api_key:
        raise RetrievalProviderError("RETRIEVAL_API_KEY_MISSING", "线上检索模型尚未配置 API Key。")
    return api_key


def _client() -> httpx.Client:
    global _http_client
    if _http_client is None:
        timeout = max(settings.EMBEDDING_TIMEOUT_SECONDS, settings.RERANKER_TIMEOUT_SECONDS)
        _http_client = httpx.Client(timeout=httpx.Timeout(timeout))
    return _http_client


def _payload_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _estimate_tokens(texts: list[str]) -> int:
    return max(1, sum(max(1, len(text) // 3) for text in texts))


def _usage_tokens(payload: dict[str, Any], fallback: int) -> tuple[int, str]:
    meta = payload.get("meta") or {}
    usage = payload.get("usage") or payload.get("tokens") or meta.get("billed_units") or meta.get("tokens") or {}
    tokens = int(
        usage.get("total_tokens")
        or (
            int(usage.get("input_tokens") or usage.get("prompt_tokens") or 0)
            + int(usage.get("output_tokens") or 0)
            + int(usage.get("image_tokens") or 0)
        )
        or 0
    )
    return (tokens, "provider") if tokens > 0 else (fallback, "estimated")


def _post_json(path: str, payload: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
    url = f"{settings.SILICONFLOW_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    retry_statuses = {429, 503, 504}
    last_error: Exception | None = None
    for attempt in range(settings.RETRIEVAL_PROVIDER_MAX_RETRIES + 1):
        try:
            response = _client().post(
                url,
                headers={
                    "Authorization": f"Bearer {_siliconflow_api_key()}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=timeout_seconds,
            )
            if response.status_code < 400:
                try:
                    data = response.json()
                except ValueError as exc:
                    raise RetrievalProviderError("RETRIEVAL_PROVIDER_RESPONSE_INVALID", "检索服务返回格式异常。") from exc
                if not isinstance(data, dict):
                    raise RetrievalProviderError("RETRIEVAL_PROVIDER_RESPONSE_INVALID", "检索服务返回格式异常。")
                return data
            if response.status_code not in retry_statuses or attempt >= settings.RETRIEVAL_PROVIDER_MAX_RETRIES:
                code = "RETRIEVAL_PROVIDER_RATE_LIMITED" if response.status_code == 429 else "RETRIEVAL_PROVIDER_UNAVAILABLE"
                raise RetrievalProviderError(code, "线上检索服务暂不可用，请稍后重试。")
        except RetrievalProviderError:
            raise
        except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError) as exc:
            last_error = exc
            if attempt >= settings.RETRIEVAL_PROVIDER_MAX_RETRIES:
                break
        time.sleep(min(0.25 * (2 ** attempt), 1.0))
    raise RetrievalProviderError("RETRIEVAL_PROVIDER_UNAVAILABLE", "线上检索服务暂不可用，请稍后重试。") from last_error


class SiliconFlowEmbeddings(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors: list[list[float]] = []
        batch_size = min(32, max(1, settings.EMBEDDING_BATCH_SIZE))
        for start in range(0, len(texts), batch_size):
            batch = [str(text) for text in texts[start:start + batch_size]]
            vectors.extend(self._embed_batch(batch))
        return vectors

    def embed_query(self, text: str) -> list[float]:
        vectors = self._embed_batch([str(text)])
        return vectors[0]

    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        payload = {
            "model": settings.EMBEDDING_MODEL,
            "input": texts,
            "encoding_format": "float",
            "dimensions": settings.EMBEDDING_DIMENSIONS,
        }
        estimated_tokens = _estimate_tokens(texts)
        operation_id, request_key, client_ip = next_retrieval_operation_id("embedding", _payload_hash(payload))
        reserve_retrieval_call(
            operation_id=operation_id,
            request_key=request_key,
            client_ip=client_ip,
            provider="siliconflow",
            operation_kind="embedding",
            model_id=settings.EMBEDDING_MODEL,
            estimated_tokens=estimated_tokens,
            price_per_million=settings.EMBEDDING_PRICE_MICROUSD_PER_MILLION,
        )
        try:
            response = _post_json("embeddings", payload, settings.EMBEDDING_TIMEOUT_SECONDS)
            rows = response.get("data") or []
            if not isinstance(rows, list) or len(rows) != len(texts):
                raise RetrievalProviderError("EMBEDDING_RESPONSE_INVALID", "Embedding 返回数量不一致。")
            indices = [int(row.get("index", -1)) for row in rows]
            if sorted(indices) != list(range(len(texts))):
                raise RetrievalProviderError("EMBEDDING_RESPONSE_INVALID", "Embedding 返回索引异常。")
            ordered = sorted(rows, key=lambda row: int(row["index"]))
            vectors = [row.get("embedding") for row in ordered]
            if any(not isinstance(vector, list) or len(vector) != settings.EMBEDDING_DIMENSIONS for vector in vectors):
                raise RetrievalProviderError("EMBEDDING_DIMENSION_MISMATCH", "Embedding 返回维度与配置不一致。")
            actual_tokens, usage_source = _usage_tokens(response, estimated_tokens)
            settle_retrieval_call(
                operation_id,
                actual_tokens=actual_tokens,
                price_per_million=settings.EMBEDDING_PRICE_MICROUSD_PER_MILLION,
                usage_source=usage_source,
            )
            return vectors
        except Exception:
            settle_retrieval_call(
                operation_id,
                actual_tokens=estimated_tokens,
                price_per_million=settings.EMBEDDING_PRICE_MICROUSD_PER_MILLION,
                usage_source="estimated",
                failed=True,
            )
            raise


def get_embedding_model() -> Embeddings:
    global _embedding_instance
    if _embedding_instance is None:
        if _provider() == "siliconflow":
            _embedding_instance = SiliconFlowEmbeddings()
        else:
            device = _resolve_device(settings.EMBEDDING_DEVICE)
            _embedding_instance = HuggingFaceEmbeddings(
                model_name=settings.LOCAL_EMBEDDING_MODEL,
                model_kwargs={"device": device},
                encode_kwargs={"normalize_embeddings": True},
            )
    return _embedding_instance


def get_reranker_model() -> HuggingFaceCrossEncoder:
    global _reranker_instance
    if _reranker_instance is None:
        device = _resolve_device(settings.RERANKER_DEVICE)
        _reranker_instance = HuggingFaceCrossEncoder(
            model_name=settings.LOCAL_RERANKER_MODEL,
            model_kwargs={"device": device},
        )
    return _reranker_instance


def rerank_documents(query: str, documents: list[Document], top_n: int) -> list[Document]:
    if not documents:
        return []
    top_n = max(1, min(top_n, len(documents)))
    limited_documents = documents[: settings.RERANKER_MAX_DOCUMENTS]
    if _provider() == "local":
        scores = get_reranker_model().score([(query, doc.page_content) for doc in limited_documents])
        ranked = sorted(zip(limited_documents, scores), key=lambda item: float(item[1]), reverse=True)
        return [doc for doc, _ in ranked[:top_n]]

    texts = [doc.page_content[: settings.RERANKER_MAX_DOCUMENT_CHARS] for doc in limited_documents]
    payload = {
        "model": settings.RERANKER_MODEL,
        "query": query,
        "documents": texts,
        "top_n": top_n,
        "return_documents": False,
    }
    estimated_tokens = _estimate_tokens([query, *texts])
    operation_id, request_key, client_ip = next_retrieval_operation_id("rerank", _payload_hash(payload))
    reserve_retrieval_call(
        operation_id=operation_id,
        request_key=request_key,
        client_ip=client_ip,
        provider="siliconflow",
        operation_kind="rerank",
        model_id=settings.RERANKER_MODEL,
        estimated_tokens=estimated_tokens,
        price_per_million=settings.RERANKER_PRICE_MICROUSD_PER_MILLION,
    )
    try:
        response = _post_json("rerank", payload, settings.RERANKER_TIMEOUT_SECONDS)
        results = response.get("results") or []
        if not isinstance(results, list):
            raise RetrievalProviderError("RERANK_RESPONSE_INVALID", "Rerank 返回格式异常。")
        ranked: list[Document] = []
        seen: set[int] = set()
        for row in results:
            index = int(row.get("index", -1))
            if index < 0 or index >= len(limited_documents) or index in seen:
                raise RetrievalProviderError("RERANK_RESPONSE_INVALID", "Rerank 返回索引异常。")
            seen.add(index)
            ranked.append(limited_documents[index])
        if len(ranked) < top_n:
            raise RetrievalProviderError("RERANK_RESPONSE_INVALID", "Rerank 返回结果数量不足。")
        actual_tokens, usage_source = _usage_tokens(response, estimated_tokens)
        settle_retrieval_call(
            operation_id,
            actual_tokens=actual_tokens,
            price_per_million=settings.RERANKER_PRICE_MICROUSD_PER_MILLION,
            usage_source=usage_source,
        )
        return ranked[:top_n]
    except Exception:
        settle_retrieval_call(
            operation_id,
            actual_tokens=estimated_tokens,
            price_per_million=settings.RERANKER_PRICE_MICROUSD_PER_MILLION,
            usage_source="estimated",
            failed=True,
        )
        raise


def reset_retrieval_model_clients() -> None:
    global _embedding_instance, _reranker_instance, _http_client
    _embedding_instance = None
    _reranker_instance = None
    if _http_client is not None:
        _http_client.close()
    _http_client = None
