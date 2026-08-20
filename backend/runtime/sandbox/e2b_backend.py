from __future__ import annotations

"""E2B 云端沙盒后端。

需要安装 `e2b-code-interpreter` 并设置 `E2B_API_KEY`。
同一个 thread_id 内复用同一个 sandbox 实例，空闲超过 `E2B_IDLE_MINUTES` 自动关闭并在下次重建。
"""

import asyncio
import time
from typing import Any

from backend.core.config import settings
from backend.runtime.sandbox.base import SandboxBackend, SandboxResult


class E2BBackend(SandboxBackend):
    name = "e2b"

    def __init__(self) -> None:
        try:
            from e2b_code_interpreter import AsyncSandbox  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "E2B 后端不可用：请先安装 `e2b-code-interpreter` 并设置 E2B_API_KEY。"
                f" 底层错误：{e}"
            )
        self._sandbox_cls = AsyncSandbox
        self._sessions: dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._idle_seconds = max(60, int(getattr(settings, "SANDBOX_IDLE_MINUTES", 5)) * 60)

    async def _get_session(self, thread_id: str) -> Any:
        key = thread_id or "default"
        async with self._lock:
            entry = self._sessions.get(key)
            now = time.time()
            if entry and (now - entry["last_used"] > self._idle_seconds):
                try:
                    await entry["sandbox"].kill()
                except Exception:
                    pass
                entry = None
            if entry is None:
                sandbox = await self._sandbox_cls.create(api_key=settings.E2B_API_KEY or None)
                entry = {"sandbox": sandbox, "last_used": now}
                self._sessions[key] = entry
            entry["last_used"] = now
            return entry["sandbox"]

    async def run_python(
        self,
        code: str,
        *,
        thread_id: str = "",
        timeout: int = 30,
    ) -> SandboxResult:
        started = time.time()
        try:
            sandbox = await self._get_session(thread_id)
            execution = await asyncio.wait_for(
                sandbox.run_code(code), timeout=timeout
            )
        except asyncio.TimeoutError:
            return SandboxResult(
                ok=False,
                error=f"执行超时（{timeout}s）。",
                exit_code=-9,
                duration_ms=int((time.time() - started) * 1000),
            )
        except Exception as e:
            return SandboxResult(ok=False, error=f"E2B 执行失败：{e}", exit_code=-1)

        duration = int((time.time() - started) * 1000)
        stdout = "".join(getattr(execution.logs, "stdout", []) or [])
        stderr = "".join(getattr(execution.logs, "stderr", []) or [])
        error_text = ""
        err = getattr(execution, "error", None)
        if err:
            error_text = f"{getattr(err, 'name', 'Error')}: {getattr(err, 'value', '')}"
        text_result = ""
        results = getattr(execution, "results", []) or []
        if results:
            first = results[0]
            text_result = getattr(first, "text", None) or ""
        return SandboxResult(
            ok=(not error_text),
            stdout=(stdout + ("\n" + text_result if text_result else "")).strip(),
            stderr=stderr.strip(),
            exit_code=0 if not error_text else 1,
            duration_ms=duration,
            error=error_text,
        )

    async def run_shell(
        self,
        command: str,
        *,
        thread_id: str = "",
        timeout: int = 30,
    ) -> SandboxResult:
        started = time.time()
        try:
            sandbox = await self._get_session(thread_id)
            proc = await asyncio.wait_for(
                sandbox.commands.run(command), timeout=timeout
            )
        except asyncio.TimeoutError:
            return SandboxResult(
                ok=False,
                error=f"执行超时（{timeout}s）。",
                exit_code=-9,
                duration_ms=int((time.time() - started) * 1000),
            )
        except Exception as e:
            return SandboxResult(ok=False, error=f"E2B shell 执行失败：{e}", exit_code=-1)

        duration = int((time.time() - started) * 1000)
        stdout = getattr(proc, "stdout", "") or ""
        stderr = getattr(proc, "stderr", "") or ""
        exit_code = getattr(proc, "exit_code", 0)
        return SandboxResult(
            ok=(exit_code == 0),
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            duration_ms=duration,
        )

    async def read_file(self, path: str, *, thread_id: str = "") -> SandboxResult:
        try:
            sandbox = await self._get_session(thread_id)
            content = await sandbox.files.read(path)
        except Exception as e:
            return SandboxResult(ok=False, error=f"读取失败：{e}", exit_code=-1)
        if isinstance(content, bytes):
            try:
                content = content.decode("utf-8")
            except Exception:
                return SandboxResult(ok=False, error="文件不是 UTF-8 文本。", exit_code=-1)
        return SandboxResult(ok=True, stdout=content, exit_code=0)

    async def write_file(
        self,
        path: str,
        content: str,
        *,
        thread_id: str = "",
    ) -> SandboxResult:
        try:
            sandbox = await self._get_session(thread_id)
            await sandbox.files.write(path, content)
        except Exception as e:
            return SandboxResult(ok=False, error=f"写入失败：{e}", exit_code=-1)
        return SandboxResult(ok=True, stdout=f"已写入 {path}（{len(content)} 字节）。", exit_code=0)

    async def close(self) -> None:
        async with self._lock:
            for entry in self._sessions.values():
                try:
                    await entry["sandbox"].kill()
                except Exception:
                    pass
            self._sessions.clear()
