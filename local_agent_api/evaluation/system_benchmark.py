from __future__ import annotations

"""System-level benchmark for retrieval latency and simple/complex request timing."""

import asyncio
import json
import statistics
import time
import tracemalloc
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from local_agent_api.retrieval.pipeline import retrieve_knowledge_bundle
from local_agent_api.services.agent_service import get_agent_stream


class BenchmarkQueryConfig(BaseModel):
    """One benchmark request definition passed into the live agent pipeline."""
    query: str
    task_mode: str | None = None
    metadata_filters: dict[str, Any] | None = None


class SystemBenchmarkMetrics(BaseModel):
    """High-level latency and memory metrics surfaced in the benchmark panel."""
    retrieval_dataset_size: int
    retrieval_avg_latency_ms: float
    retrieval_p95_latency_ms: float
    simple_request_latency_ms: float
    complex_request_latency_ms: float
    simple_output_chars: int
    complex_output_chars: int
    peak_python_memory_mb: float


def _load_jsonl(path: str) -> list[dict[str, Any]]:
    """Load benchmark inputs from JSONL without imposing a stricter schema."""
    rows = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


async def _run_agent_once(config: BenchmarkQueryConfig) -> tuple[float, int]:
    """Measure one end-to-end streamed agent run and count its output length."""
    start = time.perf_counter()
    chunks = []
    async for chunk in get_agent_stream(
        config.query,
        task_mode=config.task_mode,
        metadata_filters=config.metadata_filters,
    ):
        chunks.append(chunk)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return elapsed_ms, len("".join(chunks))


def _p95(values: list[float]) -> float:
    """Tail latency helper for benchmark reporting."""
    if len(values) == 1:
        return values[0]
    return statistics.quantiles(values, n=100)[94]


async def run_system_benchmark(
    retrieval_dataset_path: str,
    simple_query: BenchmarkQueryConfig,
    complex_query: BenchmarkQueryConfig,
    candidate_k: int = 8,
) -> SystemBenchmarkMetrics:
    """Measure retrieval throughput plus one simple and one complex live request."""
    rows = _load_jsonl(retrieval_dataset_path)
    retrieval_latencies = []

    tracemalloc.start()
    for row in rows:
        start = time.perf_counter()
        retrieve_knowledge_bundle(
            row["query"],
            k=3,
            candidate_k=candidate_k,
            metadata_filters=row.get("metadata_filters"),
        )
        retrieval_latencies.append((time.perf_counter() - start) * 1000)

    simple_latency_ms, simple_chars = await _run_agent_once(simple_query)
    complex_latency_ms, complex_chars = await _run_agent_once(complex_query)
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return SystemBenchmarkMetrics(
        retrieval_dataset_size=len(rows),
        retrieval_avg_latency_ms=round(sum(retrieval_latencies) / max(len(retrieval_latencies), 1), 2),
        retrieval_p95_latency_ms=round(_p95(retrieval_latencies), 2),
        simple_request_latency_ms=round(simple_latency_ms, 2),
        complex_request_latency_ms=round(complex_latency_ms, 2),
        simple_output_chars=simple_chars,
        complex_output_chars=complex_chars,
        peak_python_memory_mb=round(peak_bytes / 1024 / 1024, 2),
    )
