from __future__ import annotations

"""Compare multiple retrieval strategies against the same labeled dataset."""

from pydantic import BaseModel

from local_agent_api.evaluation.retrieval_eval import RetrievalEvalMetrics, run_retrieval_eval
from local_agent_api.retrieval.pipeline import SearchStrategy


BASELINE_STRATEGIES: list[SearchStrategy] = [
    "dense_only",
    "dense_rerank",
    "hybrid_only",
    "hybrid_rerank",
]


class RetrievalCompareReport(BaseModel):
    """Bundle all baseline reports plus lift/delta summaries for the frontend."""
    dataset_size: int
    top_k: int
    candidate_k: int
    baselines: list[RetrievalEvalMetrics]
    summary: dict[str, dict[str, float]]


def run_retrieval_compare(
    dataset_path: str,
    top_k: int = 3,
    candidate_k: int = 15,
) -> RetrievalCompareReport:
    """Run all baseline strategies so their metrics can be compared side by side."""
    reports = [
        run_retrieval_eval(
            dataset_path=dataset_path,
            top_k=top_k,
            candidate_k=candidate_k,
            strategy=strategy,
        )
        for strategy in BASELINE_STRATEGIES
    ]
    baseline = reports[0] if reports else None
    summary: dict[str, dict[str, float]] = {}
    for report in reports:
        summary[report.strategy] = {
            "recall_lift_vs_dense_only": round(report.avg_recall_at_k - (baseline.avg_recall_at_k if baseline else 0.0), 4),
            "mrr_lift_vs_dense_only": round(report.mrr - (baseline.mrr if baseline else 0.0), 4),
            "latency_delta_ms_vs_dense_only": round(report.avg_query_latency_ms - (baseline.avg_query_latency_ms if baseline else 0.0), 2),
        }
    return RetrievalCompareReport(
        dataset_size=reports[0].dataset_size if reports else 0,
        top_k=top_k,
        candidate_k=candidate_k,
        baselines=reports,
        summary=summary,
    )
