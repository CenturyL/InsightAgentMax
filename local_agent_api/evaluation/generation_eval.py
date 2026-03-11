from __future__ import annotations

"""Offline answer-quality evaluation driven by real agent output plus an LLM judge."""

import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, TypeAdapter

from local_agent_api.core.llm import advanced_model
from local_agent_api.retrieval.pipeline import retrieve_knowledge_bundle
from local_agent_api.services.agent_service import get_agent_stream


class GenerationEvalItem(BaseModel):
    """One generation test case with optional gold answer and keyword hints."""
    query: str
    expected_answer: str | None = None
    expected_keywords: list[str] = Field(default_factory=list)
    task_mode: str | None = None
    metadata_filters: dict[str, Any] | None = None


class GenerationJudgeResult(BaseModel):
    """Judge-model output for one generated answer."""
    answer_relevance: float = Field(ge=0.0, le=1.0)
    faithfulness: float = Field(ge=0.0, le=1.0)
    citation_accuracy: float = Field(ge=0.0, le=1.0)
    rationale: str


class GenerationEvalMetrics(BaseModel):
    """Aggregate generation-quality metrics with per-sample rationale and evidence."""
    dataset_size: int
    avg_answer_relevance: float
    avg_faithfulness: float
    avg_citation_accuracy: float
    avg_keyword_coverage: float
    details: list[dict[str, Any]]


JUDGE_PROMPT = """你是一个严格的生成质量评估器。请根据用户问题、标准答案、模型答案和参考证据，评估答案质量。

输出要求：
1. 只输出 JSON 对象
2. 字段必须包含：
   answer_relevance, faithfulness, citation_accuracy, rationale
3. 所有分数范围为 0 到 1
4. 若答案与证据不一致，faithfulness 必须降低
5. 若答案声称有依据但和证据来源不匹配，citation_accuracy 必须降低

用户问题：
{query}

标准答案：
{expected_answer}

模型答案：
{model_answer}

参考证据：
{evidence}
"""


JUDGE_RESULT_ADAPTER = TypeAdapter(GenerationJudgeResult)
LOG_LINE_PREFIXES = ("🧭", "🛠️", "✅")


def _extract_json_object(raw: str) -> str:
    """Recover the JSON body even when the judge wraps it in prose or code fences."""
    raw = raw.strip()
    fenced_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, flags=re.S)
    if fenced_match:
        return fenced_match.group(1)
    object_match = re.search(r"(\{.*\})", raw, flags=re.S)
    if object_match:
        return object_match.group(1)
    return raw


def _keyword_coverage(answer: str, expected_keywords: list[str]) -> float:
    """Cheap lexical coverage score to complement model-based judging."""
    if not expected_keywords:
        return 1.0
    hits = sum(1 for keyword in expected_keywords if keyword and keyword in answer)
    return hits / len(expected_keywords)


def _sanitize_agent_answer(answer: str) -> str:
    """Remove internal trace lines before sending the answer to the judge model."""
    lines = []
    for line in answer.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(LOG_LINE_PREFIXES):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def load_generation_eval_dataset(dataset_path: str) -> list[GenerationEvalItem]:
    """Load JSONL generation-eval cases."""
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"generation eval dataset not found: {dataset_path}")

    items = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
                items.append(GenerationEvalItem.model_validate(payload))
            except Exception as exc:
                raise ValueError(f"invalid generation eval dataset line {line_no}: {exc}") from exc
    return items


async def _collect_agent_answer(
    query: str,
    task_mode: str | None = None,
    metadata_filters: dict[str, Any] | None = None,
) -> str:
    """Run the real agent stream end-to-end and merge chunks into one answer string."""
    chunks = []
    async for chunk in get_agent_stream(
        query,
        task_mode=task_mode,
        metadata_filters=metadata_filters,
    ):
        chunks.append(chunk)
    return _sanitize_agent_answer("".join(chunks).strip())


async def _judge_generation(
    query: str,
    expected_answer: str,
    model_answer: str,
    evidence: str,
) -> GenerationJudgeResult:
    """Ask the advanced model to score a generated answer against evidence/gold text."""
    prompt = JUDGE_PROMPT.format(
        query=query,
        expected_answer=expected_answer or "无标准答案，仅根据问题和证据进行评估",
        model_answer=model_answer,
        evidence=evidence or "无",
    )
    response = await advanced_model.ainvoke(prompt)
    payload = json.loads(_extract_json_object(response.content))
    return JUDGE_RESULT_ADAPTER.validate_python(payload)


async def run_generation_eval(dataset_path: str, candidate_k: int = 15) -> GenerationEvalMetrics:
    """Run generation evaluation across the labeled dataset and aggregate scores."""
    items = load_generation_eval_dataset(dataset_path)
    if not items:
        return GenerationEvalMetrics(
            dataset_size=0,
            avg_answer_relevance=0.0,
            avg_faithfulness=0.0,
            avg_citation_accuracy=0.0,
            avg_keyword_coverage=0.0,
            details=[],
        )

    details: list[dict[str, Any]] = []
    answer_relevance_sum = 0.0
    faithfulness_sum = 0.0
    citation_accuracy_sum = 0.0
    keyword_coverage_sum = 0.0

    for item in items:
        bundle = retrieve_knowledge_bundle(
            item.query,
            k=3,
            candidate_k=candidate_k,
            metadata_filters=item.metadata_filters,
        )
        model_answer = await _collect_agent_answer(
            item.query,
            task_mode=item.task_mode,
            metadata_filters=item.metadata_filters,
        )
        judge_result = await _judge_generation(
            query=item.query,
            expected_answer=item.expected_answer or "",
            model_answer=model_answer,
            evidence=bundle.context_text,
        )
        keyword_coverage = _keyword_coverage(model_answer, item.expected_keywords)

        answer_relevance_sum += judge_result.answer_relevance
        faithfulness_sum += judge_result.faithfulness
        citation_accuracy_sum += judge_result.citation_accuracy
        keyword_coverage_sum += keyword_coverage

        details.append(
            {
                "query": item.query,
                "task_mode": item.task_mode or "qa",
                "model_answer": model_answer,
                "expected_answer": item.expected_answer,
                "expected_keywords": item.expected_keywords,
                "keyword_coverage": round(keyword_coverage, 4),
                "answer_relevance": round(judge_result.answer_relevance, 4),
                "faithfulness": round(judge_result.faithfulness, 4),
                "citation_accuracy": round(judge_result.citation_accuracy, 4),
                "rationale": judge_result.rationale,
                "retrieved_sources": [citation["source"] for citation in bundle.citations],
                "retrieved_citations": bundle.citations,
                "evidence_preview": bundle.context_text[:500],
                "applied_filters": bundle.applied_filters,
            }
        )

    dataset_size = len(items)
    return GenerationEvalMetrics(
        dataset_size=dataset_size,
        avg_answer_relevance=round(answer_relevance_sum / dataset_size, 4),
        avg_faithfulness=round(faithfulness_sum / dataset_size, 4),
        avg_citation_accuracy=round(citation_accuracy_sum / dataset_size, 4),
        avg_keyword_coverage=round(keyword_coverage_sum / dataset_size, 4),
        details=details,
    )
