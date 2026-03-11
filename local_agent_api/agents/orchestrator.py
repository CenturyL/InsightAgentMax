from __future__ import annotations

"""Wire planner / executor / reflection / synthesis into one complex-task graph."""

from typing import Literal

from langgraph.graph import END, START, StateGraph

from local_agent_api.agents.executor import executor_node
from local_agent_api.agents.planner import planner_node
from local_agent_api.agents.reflection import reflection_node
from local_agent_api.agents.react_agent import react_passthrough_node
from local_agent_api.agents.router import complexity_router_node
from local_agent_api.agents.state import OrchestratorState
from local_agent_api.core.llm import advanced_model
from local_agent_api.retrieval.citation import format_citations


SYNTHESIZER_PROMPT = """你是一个政策与招投标情报分析助手。请基于给定执行计划和每一步的证据，生成最终答案。

要求：
1. 明确回答用户问题
2. 优先使用检索证据，不要编造
3. 若证据不足，要明确指出
4. 输出格式必须遵循任务模式要求
5. 在答案末尾追加“证据来源”小节，列出来源路径或标识

用户问题：
{query}

任务模式：
{task_mode}

输出格式要求：
{format_instruction}

执行计划：
{plan_text}

步骤结果：
{results_text}

证据来源：
{sources_text}
"""


def _route_after_complexity(state: OrchestratorState) -> Literal["react_agent", "planner"]:
    """Choose the simple pass-through path or the complex planning path."""
    return "planner" if state.get("is_complex") else "react_agent"


def _format_instruction_for_mode(task_mode: str | None) -> str:
    """Provide answer-shape guidance so synthesis matches the requested task mode."""
    mode = task_mode or "qa"
    if mode == "compare":
        return "使用“结论 / 对比维度 / 差异摘要 / 建议”结构，尽量用表格表达核心差异。"
    if mode == "extract":
        return "使用“字段名: 字段值”或 JSON 风格的结构化结果，并在字段缺失时明确标注未找到。"
    if mode == "report":
        return "使用“摘要 / 关键发现 / 详细分析 / 风险与不确定性 / 下一步建议”结构。"
    return "优先使用清晰分点回答；若信息较多，可以补充短表格。"


def build_synthesizer_prompt(state: OrchestratorState) -> str:
    """Assemble the final prompt from plan, step evidence, and citations."""
    query = str(state["messages"][-1].content) if state.get("messages") else ""
    task_mode = state.get("task_mode", "qa")
    plan_lines = [
        f"{item['step_id']}: {item['goal']} ({item['status']})"
        for item in state.get("plan", [])
    ]
    result_lines = [
        f"{item['step_id']} | {item['status']} | {item['evidence']}"
        for item in state.get("step_results", [])
    ]
    return SYNTHESIZER_PROMPT.format(
        query=query,
        task_mode=task_mode,
        format_instruction=_format_instruction_for_mode(task_mode),
        plan_text="\n".join(plan_lines) or "无",
        results_text="\n\n".join(result_lines) or "无",
        sources_text=format_citations(state.get("citations", [])) if state.get("citations") else "无",
    )


async def synthesizer_node(state: OrchestratorState) -> OrchestratorState:
    """Generate the final user-facing answer from intermediate execution state."""
    task_mode = state.get("task_mode", "qa")
    prompt = build_synthesizer_prompt(state)
    plan_lines = [
        f"{item['step_id']}: {item['goal']} ({item['status']})"
        for item in state.get("plan", [])
    ]
    result_lines = [
        f"{item['step_id']} | {item['status']} | {item['evidence']}"
        for item in state.get("step_results", [])
    ]

    try:
        response = await advanced_model.ainvoke(prompt)
        final_answer = response.content.strip()
    except Exception:
        fallback_sections = [
            "已进入 Plan-and-Execute 模式。",
            f"任务模式：{task_mode}",
            "",
            "计划步骤：",
            "\n".join(plan_lines) or "无",
            "",
            "步骤结果：",
            "\n\n".join(result_lines) or "无",
            "",
            "证据来源：",
            format_citations(state.get("citations", [])) if state.get("citations") else "无",
        ]
        final_answer = "\n".join(fallback_sections)

    return {
        **state,
        "final_answer": final_answer,
    }


def build_orchestrator():
    """Compile the LangGraph workflow used by complex requests."""
    graph = StateGraph(OrchestratorState)
    graph.add_node("complexity_router", complexity_router_node)
    graph.add_node("react_agent", react_passthrough_node)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("reflection", reflection_node)
    graph.add_node("synthesizer", synthesizer_node)

    graph.add_edge(START, "complexity_router")
    graph.add_conditional_edges(
        "complexity_router",
        _route_after_complexity,
        {
            "react_agent": "react_agent",
            "planner": "planner",
        },
    )
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "reflection")
    graph.add_edge("reflection", "synthesizer")
    graph.add_edge("react_agent", END)
    graph.add_edge("synthesizer", END)
    return graph.compile()


orchestrator_graph = build_orchestrator()
