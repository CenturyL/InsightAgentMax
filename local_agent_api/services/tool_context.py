from __future__ import annotations

"""基于 ContextVar 的请求级工具上下文，避免使用全局共享状态。"""

import asyncio
from contextvars import ContextVar
from typing import Any


_metadata_filters_var: ContextVar[dict[str, Any] | None] = ContextVar(
    "tool_metadata_filters",
    default=None,
)
_thread_id_var: ContextVar[str] = ContextVar("tool_thread_id", default="")
_user_id_var: ContextVar[str] = ContextVar("tool_user_id", default="")
_plan_mode_var: ContextVar[str | None] = ContextVar("tool_plan_mode", default=None)
_model_choice_var: ContextVar[str] = ContextVar("tool_model_choice", default="local_qwen")
_in_pae_var: ContextVar[bool] = ContextVar("tool_in_pae", default=False)
_tool_trace_var: ContextVar[list[str]] = ContextVar("tool_trace", default=[])
_tool_trace_queue_var: ContextVar[asyncio.Queue[str] | None] = ContextVar("tool_trace_queue", default=None)
_last_pae_result_var: ContextVar[dict[str, Any] | None] = ContextVar("last_pae_result", default=None)


def set_tool_metadata_filters(metadata_filters: dict[str, Any] | None):
    """保存当前请求的 metadata_filters，供工具函数隐式复用。"""
    return _metadata_filters_var.set(metadata_filters or None)


def reset_tool_metadata_filters(token) -> None:
    """在流式输出结束后恢复上一个请求上下文。"""
    _metadata_filters_var.reset(token)


def get_tool_metadata_filters() -> dict[str, Any] | None:
    """在工具函数内部读取当前请求的 metadata_filters。"""
    return _metadata_filters_var.get()


def set_tool_request_context(
    *,
    thread_id: str,
    user_id: str,
    plan_mode: str | None,
    model_choice: str,
    metadata_filters: dict[str, Any] | None,
    in_pae: bool = False,
) -> dict[str, Any]:
    """一次性设置当前请求的工具上下文。"""
    trace_queue: asyncio.Queue[str] = asyncio.Queue()
    return {
        "metadata": _metadata_filters_var.set(metadata_filters or None),
        "thread_id": _thread_id_var.set(thread_id),
        "user_id": _user_id_var.set(user_id),
        "plan_mode": _plan_mode_var.set(plan_mode),
        "model_choice": _model_choice_var.set(model_choice),
        "in_pae": _in_pae_var.set(in_pae),
        "trace": _tool_trace_var.set([]),
        "trace_queue": _tool_trace_queue_var.set(trace_queue),
        "trace_queue_obj": trace_queue,
        "last_pae_result": _last_pae_result_var.set(None),
    }


def reset_tool_request_context(tokens: dict[str, Any]) -> None:
    """恢复之前的工具上下文。"""
    _metadata_filters_var.reset(tokens["metadata"])
    _thread_id_var.reset(tokens["thread_id"])
    _user_id_var.reset(tokens["user_id"])
    _plan_mode_var.reset(tokens["plan_mode"])
    _model_choice_var.reset(tokens["model_choice"])
    _in_pae_var.reset(tokens["in_pae"])
    _tool_trace_var.reset(tokens["trace"])
    _tool_trace_queue_var.reset(tokens["trace_queue"])
    _last_pae_result_var.reset(tokens["last_pae_result"])


def get_tool_thread_id() -> str:
    return _thread_id_var.get()


def get_tool_user_id() -> str:
    return _user_id_var.get()


def get_tool_plan_mode() -> str | None:
    return _plan_mode_var.get()


def get_tool_model_choice() -> str:
    return _model_choice_var.get()


def is_in_pae() -> bool:
    return _in_pae_var.get()


def append_tool_trace(line: str) -> None:
    traces = list(_tool_trace_var.get())
    traces.append(line)
    _tool_trace_var.set(traces)
    queue = _tool_trace_queue_var.get()
    if queue is not None:
        queue.put_nowait(line)


def drain_tool_trace() -> list[str]:
    traces = list(_tool_trace_var.get())
    _tool_trace_var.set([])
    return traces


def get_tool_trace_queue(tokens: dict[str, Any]) -> asyncio.Queue[str] | None:
    return tokens.get("trace_queue_obj")


def set_last_pae_result(result: dict[str, Any]) -> None:
    _last_pae_result_var.set(result)


def consume_last_pae_result() -> dict[str, Any] | None:
    result = _last_pae_result_var.get()
    _last_pae_result_var.set(None)
    return result
