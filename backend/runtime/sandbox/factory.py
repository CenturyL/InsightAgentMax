from __future__ import annotations

"""Sandbox 后端工厂：按 settings.SANDBOX_BACKEND 返回单例实现。"""

from backend.core.config import settings
from backend.runtime.sandbox.base import SandboxBackend


_INSTANCE: SandboxBackend | None = None
_INIT_ERROR: str = ""


def is_sandbox_enabled() -> bool:
    return (settings.SANDBOX_BACKEND or "disabled").lower() != "disabled"


def get_sandbox_backend() -> SandboxBackend | None:
    """懒加载。E2B 不可用时自动降级为 local。"""
    global _INSTANCE, _INIT_ERROR
    if _INSTANCE is not None:
        return _INSTANCE

    backend_name = (settings.SANDBOX_BACKEND or "disabled").lower()
    if backend_name == "disabled":
        return None

    if backend_name == "e2b":
        try:
            from backend.runtime.sandbox.e2b_backend import E2BBackend

            _INSTANCE = E2BBackend()
            _INIT_ERROR = ""
            return _INSTANCE
        except Exception as e:
            _INIT_ERROR = f"E2B 初始化失败，已降级为 local：{e}"

    from backend.runtime.sandbox.local_backend import LocalSubprocessBackend

    _INSTANCE = LocalSubprocessBackend()
    return _INSTANCE


def last_init_error() -> str:
    return _INIT_ERROR


async def close_all_sandboxes() -> None:
    global _INSTANCE
    if _INSTANCE is not None:
        try:
            await _INSTANCE.close()
        except Exception:
            pass
        _INSTANCE = None
