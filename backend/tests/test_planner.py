from __future__ import annotations

from backend.agents.planner import _normalize_plan


def test_normalize_plan_accepts_numeric_step_id():
    plan = _normalize_plan(
        '[{"step_id": 1, "goal": "查找资料", "reason": "获取证据", '
        '"required_capability": "rag_search", "expected_output": "资料", "status": "pending"}]',
        "查找资料",
    )

    assert plan[0]["step_id"] == "1"
    assert plan[0]["goal"] == "查找资料"


def test_normalize_plan_fills_missing_step_id_without_overwriting_fields():
    plan = _normalize_plan(
        '[{"goal": "整理结论", "reason": "形成回答", '
        '"required_capability": "synthesis", "expected_output": "结论", "status": "pending"}]',
        "整理结论",
    )

    assert plan == [
        {
            "step_id": "step_1",
            "goal": "整理结论",
            "reason": "形成回答",
            "required_capability": "synthesis",
            "expected_output": "结论",
            "status": "pending",
        }
    ]


def test_normalize_plan_rejects_empty_plan():
    try:
        _normalize_plan("[]", "空计划回归")
    except ValueError as exc:
        assert "空计划" in str(exc)
    else:
        raise AssertionError("empty planner output must fail")
