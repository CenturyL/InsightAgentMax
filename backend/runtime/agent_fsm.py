from __future__ import annotations

"""Agent 主循环的显式有限状态机（FSM）。

FSM 本身不替换 LangGraph 的调度，而是在 AgentState 上加一个 `fsm_phase`
字段，由 loop_guard middleware 与 tool_context 协作维护，用于：
  1. 让主循环能明确区分"正常推理""工具调用""强制收敛""等待用户"等阶段
  2. 给前端 trace 提供稳定的状态标签
  3. 让 loop_guard 根据当前阶段决定是否注入强制收敛指令

状态转移图：

  INIT → ROUTING → REACTING ⇄ TOOL_CALLING
                      ↓
                 FINALIZING → DONE

  异常分支：
    REACTING / TOOL_CALLING → REPEAT_DETECTED   → ABORT_WITH_SUMMARY → DONE
    REACTING / TOOL_CALLING → BUDGET_EXCEEDED   → ABORT_WITH_SUMMARY → DONE
    REACTING                → STAGNANT          → ASK_USER           → WAITING_USER → DONE
"""

from dataclasses import dataclass
from typing import Literal


FSMPhase = Literal[
    "init",
    "routing",
    "reacting",
    "tool_calling",
    "finalizing",
    "repeat_detected",
    "budget_exceeded",
    "stagnant",
    "abort_with_summary",
    "ask_user",
    "waiting_user",
    "done",
]


TERMINAL_PHASES: set[FSMPhase] = {"done", "waiting_user"}
ABORTING_PHASES: set[FSMPhase] = {
    "repeat_detected",
    "budget_exceeded",
    "abort_with_summary",
}


@dataclass
class GuardDecision:
    """loop_guard 的单次判定结果。"""

    phase: FSMPhase
    reason: str
    directive: str = ""
    trace_line: str = ""

    @property
    def should_force_converge(self) -> bool:
        return self.phase in ABORTING_PHASES or self.phase == "ask_user"


def initial_phase() -> FSMPhase:
    return "init"


def phase_label(phase: FSMPhase) -> str:
    mapping: dict[FSMPhase, str] = {
        "init": "初始化",
        "routing": "路由",
        "reacting": "推理",
        "tool_calling": "工具调用",
        "finalizing": "收尾",
        "repeat_detected": "重复工具调用",
        "budget_exceeded": "超出工具预算",
        "stagnant": "停滞",
        "abort_with_summary": "强制收敛",
        "ask_user": "请求澄清",
        "waiting_user": "等待用户",
        "done": "完成",
    }
    return mapping.get(phase, phase)
