from __future__ import annotations

"""Per-request tool context shared through ContextVar instead of global state."""

from contextvars import ContextVar
from typing import Any


_metadata_filters_var: ContextVar[dict[str, Any] | None] = ContextVar(
    "tool_metadata_filters",
    default=None,
)


def set_tool_metadata_filters(metadata_filters: dict[str, Any] | None):
    """Store request-scoped metadata filters so tools can reuse them implicitly."""
    return _metadata_filters_var.set(metadata_filters or None)


def reset_tool_metadata_filters(token) -> None:
    """Restore the previous request context after streaming finishes."""
    _metadata_filters_var.reset(token)


def get_tool_metadata_filters() -> dict[str, Any] | None:
    """Read the current request-scoped metadata filters inside a tool function."""
    return _metadata_filters_var.get()
