from __future__ import annotations

"""Offline retrieval metrics used to compare recall/precision/ranking quality."""

import json
import statistics
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from local_agent_api.retrieval.pipeline import SearchStrategy, retrieve_knowledge_bundle


class RetrievalEvalItem(BaseModel):
    """One gold query with relevant sources and optional metadata filters."""
    query: str
    relevant_sources: list[str] = Field(default_factory=list)
    metadata_filters: dict[str, Any] | None = None


class RetrievalEvalMetrics(BaseModel):
    """Aggregate retrieval metrics plus per-query diagnostic details."""
    dataset_size: int
    top_k: int
    strategy: str
    avg_precision_at_k: float
    avg_recall_at_k: float
    mrr: float
    ndcg_at_k: float
    hit_rate: float
    avg_query_latency_ms: float
    p95_query_latency_ms: float
    details: list[dict[str, Any]]


def _normalize_source(source: str) -> str:
    """Compare sources by basename to avoid path-prefix differences across machines."""
    return Path(source).name.lower().strip()


def _match_relevance(retrieved_sources: list[str], relevant_sources: list[str]) -> int:
    """Count unique source-level hits rather than duplicated chunk-level hits."""
    normalized_relevant = {_normalize_source(source) for source in relevant_sources}
    seen = set()
    hits = 0
    for source in retrieved_sources:
        normalized_source = _normalize_source(source)
        if normalized_source in seen:
            continue
        seen.add(normalized_source)
        if normalized_source in normalized_relevant:
            hits += 1
    return hits


def _first_relevant_rank(retrieved_sources: list[str], relevant_sources: list[str]) -> int | None:
    """Return the first unique hit rank for reciprocal-rank style metrics."""
    normalized_relevant = {_normalize_source(source) for source in relevant_sources}
    seen = set()
    for idx, source in enumerate(retrieved_sources, start=1):
        normalized_source = _normalize_source(source)
        if normalized_source in seen:
            continue
        seen.add(normalized_source)
        if normalized_source in normalized_relevant:
            return idx
    return None


def _dcg(relevance_flags: list[int]) -> float:
    """Compute discounted cumulative gain for the current ranking."""
    score = 0.0
    for idx, rel in enumerate(relevance_flags, start=1):
        if rel:
            score += rel / __import__("math").log2(idx + 1)
    return score


def _unique_retrieved_sources(retrieved_sources: list[str]) -> list[str]:
    """Collapse multiple chunks from the same source into one evaluation item."""
    unique = []
    seen = set()
    for source in retrieved_sources:
        normalized_source = _normalize_source(source)
        if normalized_source in seen:
            continue
        seen.add(normalized_source)
        unique.append(source)
    return unique


def _p95(values: list[float]) -> float:
    """Small helper for the latency tail metric shown in benchmark panels."""
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    return statistics.quantiles(values, n=100)[94]


def load_retrieval_eval_dataset(dataset_path: str) -> list[RetrievalEvalItem]:
    """Load JSONL retrieval labels from disk into typed eval items."""
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"retrieval eval dataset not found: {dataset_path}")

    items = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
                items.append(RetrievalEvalItem.model_validate(payload))
            except Exception as exc:
                raise ValueError(f"invalid eval dataset line {line_no}: {exc}") from exc
    return items


def run_retrieval_eval(
    dataset_path: str,
    top_k: int = 3,
    candidate_k: int = 15,
    strategy: SearchStrategy = "hybrid_rerank",
) -> RetrievalEvalMetrics:
    """Run one retrieval strategy against the gold dataset and summarize metrics."""
    items = load_retrieval_eval_dataset(dataset_path)
    if not items:
        return RetrievalEvalMetrics(
            dataset_size=0,
            top_k=top_k,
            strategy=strategy,
            avg_precision_at_k=0.0,
            avg_recall_at_k=0.0,
            mrr=0.0,
            ndcg_at_k=0.0,
            hit_rate=0.0,
            avg_query_latency_ms=0.0,
            p95_query_latency_ms=0.0,
            details=[],
        )

    details: list[dict[str, Any]] = []
    precision_sum = 0.0
    recall_sum = 0.0
    reciprocal_rank_sum = 0.0
    ndcg_sum = 0.0
    hit_count = 0
    latencies_ms: list[float] = []

    for item in items:
        start = time.perf_counter()
        bundle = retrieve_knowledge_bundle(
            item.query,
            k=top_k,
            candidate_k=candidate_k,
            metadata_filters=item.metadata_filters,
            strategy=strategy,
        )
        latency_ms = (time.perf_counter() - start) * 1000
        latencies_ms.append(latency_ms)
        retrieved_sources = [citation["source"] for citation in bundle.citations]
        unique_retrieved_sources = _unique_retrieved_sources(retrieved_sources)
        relevant_count = max(len(item.relevant_sources), 1)
        hits = _match_relevance(unique_retrieved_sources, item.relevant_sources)
        precision = hits / max(len(unique_retrieved_sources), 1)
        recall = hits / relevant_count
        first_rank = _first_relevant_rank(unique_retrieved_sources, item.relevant_sources)
        reciprocal_rank = 1 / first_rank if first_rank else 0.0
        normalized_relevant = {_normalize_source(s) for s in item.relevant_sources}
        relevance_flags = [
            1 if _normalize_source(source) in normalized_relevant else 0
            for source in unique_retrieved_sources
        ]
        ideal_flags = [1] * min(len(item.relevant_sources), len(unique_retrieved_sources))
        dcg = _dcg(relevance_flags)
        idcg = _dcg(ideal_flags) or 1.0
        ndcg = dcg / idcg
        hit = hits > 0

        precision_sum += precision
        recall_sum += recall
        reciprocal_rank_sum += reciprocal_rank
        ndcg_sum += ndcg
        hit_count += int(hit)

        details.append(
            {
                "query": item.query,
                "retrieved_sources": unique_retrieved_sources,
                "relevant_sources": item.relevant_sources,
                "hits": hits,
                "precision_at_k": round(precision, 4),
                "recall_at_k": round(recall, 4),
                "reciprocal_rank": round(reciprocal_rank, 4),
                "ndcg_at_k": round(ndcg, 4),
                "first_relevant_rank": first_rank,
                "hit": hit,
                "query_latency_ms": round(latency_ms, 2),
                "applied_filters": bundle.applied_filters,
            }
        )

    dataset_size = len(items)
    return RetrievalEvalMetrics(
        dataset_size=dataset_size,
        top_k=top_k,
        strategy=strategy,
        avg_precision_at_k=round(precision_sum / dataset_size, 4),
        avg_recall_at_k=round(recall_sum / dataset_size, 4),
        mrr=round(reciprocal_rank_sum / dataset_size, 4),
        ndcg_at_k=round(ndcg_sum / dataset_size, 4),
        hit_rate=round(hit_count / dataset_size, 4),
        avg_query_latency_ms=round(sum(latencies_ms) / dataset_size, 2),
        p95_query_latency_ms=round(_p95(latencies_ms), 2),
        details=details,
    )
