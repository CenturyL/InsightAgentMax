from __future__ import annotations

"""Planner 节点：把自然语言任务转换为结构化步骤列表。"""

import json
import re

from pydantic import BaseModel, Field, TypeAdapter

from local_agent_api.agents.state import OrchestratorState, PlanStep
from local_agent_api.core.llm import get_model_by_choice


PLANNER_PROMPT = """你是一个复杂任务规划器。请根据用户目标，输出一个简洁、可执行的计划。

要求：
1. 仅输出 JSON 数组，不要输出任何额外说明、思考过程、解释、Markdown、代码块或表格
2. 最多 4 个步骤
3. 每个元素必须包含字段：
   step_id, goal, reason, required_capability, expected_output, status
4. status 固定填 "pending"
5. 步骤要具体，可直接执行，避免空泛措辞
6. required_capability 必须优先从以下能力中选择：
   rag_search, rag_search_uploaded, web_search, search_long_term_memory, get_current_time, analysis, synthesis
7. 如果你想解释你的推理过程，也必须省略，最终只返回 JSON 数组本身

用户目标：
{query}

计划模式：
{plan_mode}

显式过滤条件：
{metadata_filters}

补充上下文（人格 / skill / 记忆 / 提示词）：
{runtime_context}

Skill Planner Hints：
{planner_hints}
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
    """当模型输出无法解析时，返回一份可执行的保底计划。"""
    return [
        {
            "step_id": "step_1",
            "goal": "定位与问题最相关的通用知识、文档证据或外部信息源",
            "reason": "先确定证据基础，避免后续分析脱离事实依据",
            "required_capability": "rag_search",
            "expected_output": "相关证据片段、来源和可用上下文摘要",
            "status": "pending",
        },
        {
            "step_id": "step_2",
            "goal": "抽取能够回答问题的关键字段或关键信息",
            "reason": "将非结构化内容转成可分析的中间结果",
            "required_capability": "analysis",
            "expected_output": "按主题整理的关键事实",
            "status": "pending",
        },
        {
            "step_id": "step_3",
            "goal": f"围绕用户问题完成综合分析：{query[:50]}",
            "reason": "结合证据形成最终回答或方案",
            "required_capability": "synthesis",
            "expected_output": "结构化最终答案与结论",
            "status": "pending",
        },
    ]

# 从模型回复里提取并初步处理 JSON 块或数组
def _extract_json_block(raw: str) -> str:
    """从可能带解释文字或代码块的模型回复中提取最像 JSON 的数组部分。"""
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
    """解析、校验并标准化 planner 输出，使其可被 executor 直接消费。"""
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
    """为复杂任务工作流生成结构化执行计划。"""
    # 拿最后一个query
    query = str(state["messages"][-1].content) if state.get("messages") else ""
    # 组装prompt
    prompt = PLANNER_PROMPT.format(
        query=query,
        plan_mode=state.get("plan_mode", "auto"),
        metadata_filters=state.get("metadata_filters", {}),
        runtime_context=state.get("runtime_system_prompt", "无"),
        planner_hints="\n".join(state.get("planner_hints", [])) or "无",
    )

    try:
        # 拿回复&标准化
        model = get_model_by_choice(state.get("model_choice", "deepseek"))
        response = await model.ainvoke(prompt)
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
