from __future__ import annotations

"""本地沙盒后端：subprocess + tempdir + wallclock timeout。

设计取舍：
- 每个 thread_id 绑定一个独立的工作目录（`~/tmp/insightagent-sandbox/<thread_id>`），
  这样同一个会话里的多次 `code_execute` 可以互相看到上次生成的文件
- 不做 CPU/内存硬隔离（生产请用 e2b），只做 wallclock timeout 和临时目录隔离
- 仅在本机开发用；如需更强隔离请切 `SANDBOX_BACKEND=e2b`
"""

import asyncio
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

from backend.runtime.sandbox.base import SandboxBackend, SandboxResult


def _safe_thread_key(thread_id: str) -> str:
    key = "".join(ch for ch in (thread_id or "default") if ch.isalnum() or ch in {"-", "_"})
    return key or "default"


class LocalSubprocessBackend(SandboxBackend):
    name = "local"

    def __init__(self) -> None:
        self._root = Path(tempfile.gettempdir()) / "insightagent-sandbox"
        self._root.mkdir(parents=True, exist_ok=True)

    def _workdir(self, thread_id: str) -> Path:
        path = self._root / _safe_thread_key(thread_id)
        path.mkdir(parents=True, exist_ok=True)
        return path

    async def _run(
        self,
        cmd: list[str],
        *,
        cwd: Path,
        timeout: int,
        stdin_data: str | None = None,
    ) -> SandboxResult:
        started = time.time()
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(cwd),
                stdin=asyncio.subprocess.PIPE if stdin_data is not None else None,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
        except FileNotFoundError as e:
            return SandboxResult(ok=False, error=f"无法启动子进程：{e}", exit_code=-1)

        try:
            stdin_bytes = stdin_data.encode("utf-8") if stdin_data else None
            stdout_b, stderr_b = await asyncio.wait_for(
                proc.communicate(stdin_bytes), timeout=timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            try:
                await proc.wait()
            except Exception:
                pass
            duration = int((time.time() - started) * 1000)
            return SandboxResult(
                ok=False,
                error=f"执行超时（{timeout}s 已被强制终止）。",
                exit_code=-9,
                duration_ms=duration,
            )

        duration = int((time.time() - started) * 1000)
        stdout = (stdout_b or b"").decode("utf-8", errors="replace")
        stderr = (stderr_b or b"").decode("utf-8", errors="replace")
        return SandboxResult(
            ok=(proc.returncode == 0),
            stdout=stdout,
            stderr=stderr,
            exit_code=proc.returncode,
            duration_ms=duration,
        )

    async def run_python(
        self,
        code: str,
        *,
        thread_id: str = "",
        timeout: int = 30,
    ) -> SandboxResult:
        cwd = self._workdir(thread_id)
        script_path = cwd / "_snippet.py"
        script_path.write_text(code, encoding="utf-8")
        return await self._run(
            [sys.executable, "-I", str(script_path)],
            cwd=cwd,
            timeout=timeout,
        )

    async def run_shell(
        self,
        command: str,
        *,
        thread_id: str = "",
        timeout: int = 30,
    ) -> SandboxResult:
        cwd = self._workdir(thread_id)
        return await self._run(
            ["/bin/sh", "-c", command],
            cwd=cwd,
            timeout=timeout,
        )

    async def read_file(self, path: str, *, thread_id: str = "") -> SandboxResult:
        cwd = self._workdir(thread_id)
        target = (cwd / path).resolve()
        if not str(target).startswith(str(cwd.resolve())):
            return SandboxResult(ok=False, error="禁止访问工作目录之外的路径。", exit_code=-1)
        if not target.exists():
            return SandboxResult(ok=False, error=f"文件不存在：{path}", exit_code=-1)
        try:
            content = target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return SandboxResult(ok=False, error=f"文件不是 UTF-8 文本：{path}", exit_code=-1)
        return SandboxResult(ok=True, stdout=content, exit_code=0)

    async def write_file(
        self,
        path: str,
        content: str,
        *,
        thread_id: str = "",
    ) -> SandboxResult:
        cwd = self._workdir(thread_id)
        target = (cwd / path).resolve()
        if not str(target).startswith(str(cwd.resolve())):
            return SandboxResult(ok=False, error="禁止写入工作目录之外的路径。", exit_code=-1)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return SandboxResult(
            ok=True,
            stdout=f"已写入 {target.relative_to(cwd)}（{len(content)} 字节）。",
            exit_code=0,
        )

    async def close(self) -> None:
        try:
            shutil.rmtree(self._root, ignore_errors=True)
        except Exception:
            pass
