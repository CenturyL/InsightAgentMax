from __future__ import annotations

"""Execute planner-produced steps by querying the shared retrieval pipeline."""

from local_agent_api.agents.state import OrchestratorState, StepResult
from local_agent_api.retrieval.pipeline import retrieve_knowledge_bundle


def _build_step_query(user_query: str, step_goal: str) -> str:
    """Convert a broad user task into a narrower step-specific retrieval query."""
    return f"{user_query}\n\n请优先完成该子任务：{step_goal}"


# 对每个 step 构造更具体的检索 query，然后检索
async def executor_node(state: OrchestratorState) -> OrchestratorState:
    """Run each planned step and persist step-level evidence back into state.

    The executor is intentionally retrieval-centric in this project: each plan
    step is mapped to a more focused query, then the unified retrieval bundle
    is used to fetch documents, context text, and citations for later nodes.
    """
    # 先取每个step&原始提问，再定义变量
    plan = state.get("plan", [])
    user_query = str(state["messages"][-1].content) if state.get("messages") else ""
    results: list[StepResult] = []
    collected_docs = []
    citations: list[dict] = []

    for step in plan:
        # 拼 原始query + step query
        step_query = _build_step_query(user_query, step["goal"])
        try:
            # 调用统一检索链
            bundle = retrieve_knowledge_bundle(
                step_query,
                k=3,
                metadata_filters=state.get("metadata_filters"),
            )
            # 取出检索结果&拼到result
            evidence = bundle.context_text if bundle.docs else "未检索到足够证据。"
            status = "completed" if bundle.docs else "partial"
            step["status"] = status
            results.append(
                {
                    "step_id": step["step_id"],
                    "goal": step["goal"],
                    "query": step_query,
                    "evidence": evidence,
                    "status": status,
                }
            )
            collected_docs.extend(bundle.docs)
            citations.extend(bundle.citations)
        except Exception as exc:
            step["status"] = "failed"
            results.append(
                {
                    "step_id": step["step_id"],
                    "goal": step["goal"],
                    "query": step_query,
                    "evidence": f"步骤执行失败：{exc}",
                    "status": "failed",
                }
            )

    return {
        **state,
        "plan": plan,
        "step_results": results,
        "retrieved_docs": collected_docs,
        "citations": citations,
        "current_step": len(plan),
    }
