from __future__ import annotations

"""Retry weak or failed steps after the first execution pass."""

from local_agent_api.agents.state import OrchestratorState
from local_agent_api.retrieval.pipeline import retrieve_knowledge_bundle


def _needs_reflection(state: OrchestratorState) -> bool:
    """Only trigger reflection when at least one step is partial or failed."""
    results = state.get("step_results", [])
    if not results:
        return False
    return any(result["status"] in {"failed", "partial"} for result in results)


async def reflection_node(state: OrchestratorState) -> OrchestratorState:
    """Expand recall for weak steps and update the plan/result status in place."""
    if not _needs_reflection(state):
        return state

    updated_results = []
    updated_plan = list(state.get("plan", []))
    citations = list(state.get("citations", []))
    retrieved_docs = list(state.get("retrieved_docs", []))

    for result in state.get("step_results", []):
        if result["status"] == "completed":
            updated_results.append(result)
            continue

        retry_query = f"{result['goal']}\n请扩大召回范围，优先补充可直接回答该步骤的证据。"
        try:
            bundle = retrieve_knowledge_bundle(
                retry_query,
                k=2,
                candidate_k=20,
                metadata_filters=state.get("metadata_filters"),
            )
            if bundle.docs:
                result = {
                    **result,
                    "query": retry_query,
                    "evidence": bundle.context_text,
                    "status": "completed",
                }
                citations.extend(bundle.citations)
                retrieved_docs.extend(bundle.docs)
            else:
                result = {
                    **result,
                    "query": retry_query,
                    "status": "partial",
                    "evidence": result["evidence"] + "\n\n[reflection] 扩大召回后仍未找到足够证据。",
                }
        except Exception as exc:
            result = {
                **result,
                "status": "failed",
                "evidence": result["evidence"] + f"\n\n[reflection] 重试失败：{exc}",
            }

        updated_results.append(result)

        for plan_step in updated_plan:
            if plan_step["step_id"] == result["step_id"]:
                plan_step["status"] = result["status"]
                break

    return {
        **state,
        "plan": updated_plan,
        "step_results": updated_results,
        "citations": citations,
        "retrieved_docs": retrieved_docs,
    }
