from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
import json
import re
from typing import Any

from backend.core.config import settings
from backend.core.llm import get_router_model
from backend.runtime.budget import invoke_model


@dataclass
class RuntimeRequest:
    query: str
    thread_id: str
    user_id: str
    plan_mode: str | None
    model_choice: str
    metadata_filters: dict | None


@dataclass
class RuntimeRouteDecision:
    pae_action: str
    pae_reason: str
    selected_skills: list[dict[str, str]]


_ROUTE_CACHE: "OrderedDict[str, RuntimeRouteDecision]" = OrderedDict()
_ROUTE_CACHE_SIZE = 128


def _extract_json_object(text: str) -> dict:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except Exception:
        return {}


def _normalize_route_payload(payload: dict[str, Any]) -> tuple[str, str, list[Any]]:
    pae_action = str(payload.get("pae_action", "") or payload.get("p", "")).strip()
    pae_reason = str(payload.get("pae_reason", "") or payload.get("r", "")).strip()
    selected_skills = payload.get("selected_skills")
    if selected_skills is None:
        selected_skills = payload.get("s", [])
    return pae_action, pae_reason, selected_skills


def classify_complexity(query: str, plan_mode: str | None) -> str:
    qlen = len(query or "")
    if qlen >= 160:
        return "high"
    if qlen >= 80:
        return "medium"
    return "low"


# ── 本地（确定性）路由规则 ────────────────────────────────────────────────
# 目标：在把请求交给 LLM 路由之前，用极少量模式匹配消除两类明显情况：
#   1. 明显是"单步 / 测试 / 重复调用"的请求 → direct_or_simple_tools
#   2. 明显是"对比多实体 / 生成报告 / 链式研究"的请求 → run_plan_and_execute
# 其余模糊情况才交给 LLM 路由器，LLM 也被要求默认 direct。

# "我在测试同一个工具"类表述：禁止进 PAE
_TEST_REPEAT_MARKERS = (
    "连续执行", "连续调用", "连续 ", "连续使用", "重复调用", "重复执行",
    "不要停", "不要改参数", "不变参数", "同一工具", "同样的查询",
    "同样的参数", "调试", "测试一下", "压测",
)

# 闲聊、身份和定义类问题不需要计划执行。
_DIRECT_CONVERSATIONAL_PATTERNS = (
    r"^(你好|您好|嗨|哈喽|hello|hi|hey)[!！。,.， ]*$",
    r"^(你是谁|你叫什么|你叫什么名字|介绍一下你自己|你能做什么|你会什么)[?？。！! ]*$",
    r"^(你好吗|谢谢|感谢|再见|拜拜)[?？。！! ]*$",
    r"^(什么是|请解释一下|解释一下|简单说说).{1,48}$",
)

# 典型的单步意图起手词
_SINGLE_STEP_TRIGGERS = (
    "查一下", "搜一下", "列一下", "列出", "读一下", "读取",
    "打开", "截图", "截个图", "帮我查", "帮我搜", "帮我看",
    "现在几点", "现在的时间", "现在时间", "告诉我时间", "告诉我现在",
    "what time", "list the", "read the", "open the", "fetch ",
)

# 多步/对比/报告的强信号（任一命中即进 PAE）
_PAE_HARD_MARKERS = (
    "生成报告", "生成一份报告", "写一份报告", "出一份报告",
    "写方案", "生成方案", "制定方案", "建议书", "可行性分析",
    "选型建议", "选型方案",
    "ppt 大纲", "ppt大纲", "技术方案",
    "分别对比", "分别比较", "逐一对比",
    "先.*再.*", "先.*然后", "一步一步", "step by step",
    "综合分析", "多维度", "多方面", "全方位分析",
)

# 明确的 plan_mode（前端或用户指定）直接拍板
_HARD_PAE_PLAN_MODES = {"strict_plan", "compare", "extract", "report", "research"}
_HARD_DIRECT_PLAN_MODES = {"direct", "direct_or_simple_tools", "simple"}


def _match_any(text: str, patterns: tuple[str, ...]) -> bool:
    import re as _re
    for pat in patterns:
        if "." in pat or "*" in pat:
            if _re.search(pat, text):
                return True
        elif pat in text:
            return True
    return False


def _match_regex(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def local_route_hint(query: str, plan_mode: str | None) -> str | None:
    """返回 'direct_or_simple_tools' / 'run_plan_and_execute' / None（交给 LLM）。"""
    mode = (plan_mode or "auto").lower().strip()
    if mode in _HARD_DIRECT_PLAN_MODES:
        return "direct_or_simple_tools"
    if mode in _HARD_PAE_PLAN_MODES:
        return "run_plan_and_execute"

    q = (query or "").strip()
    if not q:
        return "direct_or_simple_tools"
    q_lower = q.lower()

    # 1) 闲聊、身份、定义和礼貌回应 → 直接由主循环回答，不查工具、不进 PAE
    if _match_regex(q, _DIRECT_CONVERSATIONAL_PATTERNS):
        return "direct_or_simple_tools"

    # 2) 测试/调试/重复调用同一工具 → 永远直行主循环
    if _match_any(q, _TEST_REPEAT_MARKERS):
        return "direct_or_simple_tools"

    # 3) 强多步信号 → PAE
    if _match_any(q_lower, _PAE_HARD_MARKERS):
        return "run_plan_and_execute"

    # 4) 极短 & 单步起手词 → direct
    if len(q) < 40 or _match_any(q_lower, _SINGLE_STEP_TRIGGERS):
        return "direct_or_simple_tools"

    # 模糊情况交给 LLM 路由器
    return None


def _tool_summary(available_tool_names: list[str]) -> str:
    names = available_tool_names or []
    parts: list[str] = []
    if "run_plan_and_execute" in names:
        parts.append("pae")
    if any(name.startswith("mcp__filesystem__") for name in names):
        parts.append("mcp:filesystem")
    if any(name.startswith("mcp__fetch__") for name in names):
        parts.append("mcp:fetch")
    if "rag_search" in names or "rag_search_uploaded" in names:
        parts.append("rag")
    if "web_search" in names:
        parts.append("web")
    if "search_long_term_memory" in names:
        parts.append("memory")
    if "get_current_time" in names:
        parts.append("time")
    if "code_execute" in names:
        parts.append("sandbox:code")
    if "shell_execute" in names:
        parts.append("sandbox:shell")
    if "ask_user" in names:
        parts.append("ask_user")
    if any(name.startswith("mcp__playwright") for name in names):
        parts.append("mcp:playwright")
    if any(name.startswith("mcp__git") for name in names):
        parts.append("mcp:git")
    if any(name.startswith("mcp__sequential-thinking") for name in names):
        parts.append("mcp:thinking")
    if any(name.startswith("mcp__time") for name in names):
        parts.append("mcp:time")
    return ", ".join(parts) or "none"


def _catalog_summary(skill_catalog_rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], str]:
    compact_rows: list[dict[str, str]] = []
    digest_parts: list[str] = []
    for row in skill_catalog_rows:
        name = str(row.get("name", "")).strip()
        description = str(row.get("description", "")).strip().replace("\n", " ")
        path = str(row.get("path", "")).strip()
        if not name or not description:
            continue
        compact_desc = description[:96]
        compact_rows.append({"name": name, "description": compact_desc, "path": path})
        digest_parts.append(f"{name}:{compact_desc}:{path}")
    return compact_rows, "|".join(digest_parts)


def _route_cache_key(
    *,
    query: str,
    plan_mode: str | None,
    complexity: str,
    tool_summary: str,
    catalog_digest: str,
) -> str:
    return json.dumps(
        {
            "q": query.strip(),
            "m": (plan_mode or "auto").strip().lower(),
            "c": complexity,
            "t": tool_summary,
            "s": catalog_digest,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def _route_cache_get(key: str) -> RuntimeRouteDecision | None:
    cached = _ROUTE_CACHE.get(key)
    if cached is None:
        return None
    _ROUTE_CACHE.move_to_end(key)
    return cached


def _route_cache_set(key: str, decision: RuntimeRouteDecision) -> None:
    _ROUTE_CACHE[key] = decision
    _ROUTE_CACHE.move_to_end(key)
    while len(_ROUTE_CACHE) > _ROUTE_CACHE_SIZE:
        _ROUTE_CACHE.popitem(last=False)


async def judge_runtime_route(
    *,
    query: str,
    plan_mode: str | None,
    complexity: str,
    available_tool_names: list[str],
    skill_catalog_rows: list[dict[str, str]],
) -> RuntimeRouteDecision:
    compact_catalog_rows, catalog_digest = _catalog_summary(skill_catalog_rows)
    tool_summary = _tool_summary(available_tool_names)
    cache_key = _route_cache_key(
        query=query,
        plan_mode=plan_mode,
        complexity=complexity,
        tool_summary=tool_summary,
        catalog_digest=catalog_digest,
    )
    cached = _route_cache_get(cache_key)
    if cached is not None:
        return cached

    # 先用本地规则短路；只有模糊情况才花 LLM token 去判
    local_hint = local_route_hint(query, plan_mode)
    if local_hint is not None:
        reason = (
            "本地规则：测试/单步/短查询 → 直行主循环"
            if local_hint == "direct_or_simple_tools"
            else "本地规则：命中多步/对比/报告关键词"
        )
        decision = RuntimeRouteDecision(
            pae_action=local_hint,
            pae_reason=reason,
            selected_skills=[],
        )
        _route_cache_set(cache_key, decision)
        return decision

    prompt = (
        "你是路由器。默认选 direct_or_simple_tools。只有同时满足以下至少一条时，才改判 run_plan_and_execute：\n"
        "(a) 对比两个或更多具名实体并要求结构化差异输出；\n"
        "(b) 生成多章节报告 / 方案 / 建议书 / PPT 大纲 / 技术方案；\n"
        "(c) 明确的链式多步研究——必须先完成 A，再用 A 的结果做 B。\n"
        "以下情况一律 direct_or_simple_tools：\n"
        "- 单步可验证任务（查时间、列目录、读文件、抓页面、搜一下）；\n"
        "- 重复调用同一个工具（测试/调试/连续 N 次 / 不改参数）；\n"
        "- 模糊请求（应调 ask_user 澄清而非 PAE）；\n"
        "- 需要沙盒跑代码但无多步规划的单一任务。\n"
        "skill 只看元数据，明显相关才选最多 3 个；普通请求不要选 creator/builder；单步任务通常不选 general。\n"
        "只输出 JSON，短键：p=PAE动作，r=一句原因，s=skills。\n"
        '{"p":"run_plan_and_execute|direct_or_simple_tools","r":"一句话","s":[{"name":"skill-name","reason":"一句话"}]}\n'
        f"q:{query}\n"
        f"m:{plan_mode or 'auto'}\n"
        f"c:{complexity}\n"
        f"t:{tool_summary}\n"
        f"s:{json.dumps(compact_catalog_rows, ensure_ascii=False, separators=(',', ':'))}"
    )
    try:
        response = await invoke_model(get_router_model(), prompt)
    except Exception as exc:
        # 路由模型不是最终答案的事实源；供应商瞬时失败时安全直行，
        # 但带有稳定 code 的额度/请求预算异常必须继续向上抛出。
        if getattr(exc, "code", None):
            raise
        decision = RuntimeRouteDecision(
            pae_action="direct_or_simple_tools",
            pae_reason="路由模型暂时不可用，安全降级为直接主循环。",
            selected_skills=[],
        )
        _route_cache_set(cache_key, decision)
        return decision
    payload = _extract_json_object(str(response.content))
    pae_action, pae_reason, selected_skills = _normalize_route_payload(payload)

    if pae_action not in {"run_plan_and_execute", "direct_or_simple_tools"}:
        pae_action = "direct_or_simple_tools"
    if not pae_reason:
        pae_reason = "统一路由器未返回明确原因。"
    if not isinstance(selected_skills, list):
        selected_skills = []

    normalized: list[dict[str, str]] = []
    for row in selected_skills:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name", "")).strip()
        reason = str(row.get("reason", "")).strip() or "LLM 认为该 skill 与当前请求相关"
        if not name:
            continue
        normalized.append({"name": name, "reason": reason})

    decision = RuntimeRouteDecision(
        pae_action=pae_action,
        pae_reason=pae_reason,
        selected_skills=normalized,
    )
    _route_cache_set(cache_key, decision)
    return decision


def react_recursion_limit() -> int:
    return max(4, settings.REACT_MAX_TOOL_CALLS * 2)
