from __future__ import annotations

"""Planner node: turn a natural-language task into a small structured step list."""

import json
import re

from pydantic import BaseModel, Field, TypeAdapter

from local_agent_api.agents.state import OrchestratorState, PlanStep
from local_agent_api.core.llm import advanced_model


PLANNER_PROMPT = """你是一个复杂任务规划器。请根据用户目标，输出一个简洁、可执行的计划。

要求：
1. 仅输出 JSON 数组
2. 最多 4 个步骤
3. 每个元素必须包含字段：
   step_id, goal, reason, required_capability, expected_output, status
4. status 固定填 "pending"
5. 步骤要具体，可直接执行，避免空泛措辞

用户目标：
{query}

任务模式：
{task_mode}

显式过滤条件：
{metadata_filters}
"""


class PlannerStepSchema(BaseModel):
    step_id: str = Field(default="")
    goal: str
    reason: str
    required_capability: str = Field(default="retrieval")
    expected_output: str = Field(default="步骤结果")
    status: str = Field(default="pending")


PLANNER_STEPS_ADAPTER = TypeAdapter(list[PlannerStepSchema])

# 兜底，返回固定通用prompt
def _fallback_plan(query: str) -> list[PlanStep]:
    """Return a safe default plan when the model output cannot be parsed."""
    return [
        {
            "step_id": "step_1",
            "goal": "定位与问题最相关的政策或招投标资料",
            "reason": "先确定证据来源，避免后续分析无依据",
            "required_capability": "retrieval",
            "expected_output": "相关文档片段和核心来源列表",
            "status": "pending",
        },
        {
            "step_id": "step_2",
            "goal": "抽取能够回答问题的关键字段或关键信息",
            "reason": "将非结构化内容转成可分析的中间结果",
            "required_capability": "extraction",
            "expected_output": "按主题整理的关键事实",
            "status": "pending",
        },
        {
            "step_id": "step_3",
            "goal": f"围绕用户问题完成综合分析：{query[:50]}",
            "reason": "结合证据形成最终回答",
            "required_capability": "synthesis",
            "expected_output": "结构化最终答案与结论",
            "status": "pending",
        },
    ]

# 从模型回复里提取并初步处理 JSON 块或数组
def _extract_json_block(raw: str) -> str:
    """Pull the most likely JSON array out of a model response with prose/fences."""
    raw = raw.strip() # 去首尾空格
    # 优先找 ```json ... ``` ,再找 ``` ... ```
    fenced_match = re.search(r"```(?:json)?\s*(\[.*\])\s*```", raw, flags=re.S)
    if fenced_match:
        return fenced_match.group(1)
    # 再找最外层 [...] 或 {...}
    array_match = re.search(r"(\[.*\])", raw, flags=re.S)
    if array_match:
        return array_match.group(1)
    # 啥也没有，原样返回
    return raw

# LLM回复 校验与标准化
def _normalize_plan(raw: str, query: str) -> list[PlanStep]:
    """Parse, validate, and normalize planner output into executor-ready steps."""
    # 先把json变成内存字典python对象（调用初步处理）
    parsed = json.loads(_extract_json_block(raw))
    # 格式校验（TypeAdapter）
    validated = PLANNER_STEPS_ADAPTER.validate_python(parsed)
    # 定义最终标准化 空壳结果
    normalized: list[PlanStep] = []
    # 动态补齐缺失数据&塞进结果
    for idx, item in enumerate(validated[:4], start=1):
        normalized.append(
            {
                "step_id": item.step_id or f"step_{idx}",
                "goal": item.goal or f"完成第 {idx} 步任务",
                "reason": item.reason or "补充中间推理所需证据",
                "required_capability": item.required_capability or "retrieval",
                "expected_output": item.expected_output or "步骤结果",
                "status": "pending",
            }
        )

    return normalized or _fallback_plan(query)

# planner主函数，直接显式用advanced_model
async def planner_node(state: OrchestratorState) -> OrchestratorState:
    """Generate a structured execution plan for the complex-task graph."""
    # 拿最后一个query
    query = str(state["messages"][-1].content) if state.get("messages") else ""
    # 组装prompt
    prompt = PLANNER_PROMPT.format(
        query=query,
        task_mode=state.get("task_mode", "qa"),
        metadata_filters=state.get("metadata_filters", {}),
    )

    try:
        # 拿回复&标准化
        response = await advanced_model.ainvoke(prompt)
        raw = response.content.strip()
        normalized = _normalize_plan(raw, query)
    except Exception:
        normalized = _fallback_plan(query)

    return {
        **state,
        "plan": normalized,
        "current_step": 0,
        "step_results": [],
    }
