from __future__ import annotations

"""Sandbox 抽象基类。

所有后端（local / e2b / 未来可能加的 docker）都遵守同一份接口：
  - run_python(code, timeout) -> SandboxResult
  - run_shell(command, timeout) -> SandboxResult
  - read_file(path) / write_file(path, content)
  - close()

工具层只依赖这个接口，不关心底层实现。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class SandboxResult:
    """统一的沙盒执行返回结构。"""

    ok: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    duration_ms: int = 0
    artifacts: list[str] = field(default_factory=list)
    error: str = ""

    def as_tool_text(self, max_len: int = 4000) -> str:
        parts: list[str] = []
        if self.stdout:
            parts.append("stdout:\n" + self.stdout.strip())
        if self.stderr:
            parts.append("stderr:\n" + self.stderr.strip())
        if self.error:
            parts.append("error:\n" + self.error.strip())
        parts.append(f"exit_code={self.exit_code} duration_ms={self.duration_ms}")
        text = "\n\n".join(parts)
        if len(text) > max_len:
            text = text[:max_len] + f"\n...[截断，原始长度 {len(text)}]"
        return text


class SandboxBackend(ABC):
    """所有沙盒实现必须满足的接口。"""

    name: str = "abstract"

    @abstractmethod
    async def run_python(
        self,
        code: str,
        *,
        thread_id: str = "",
        timeout: int = 30,
    ) -> SandboxResult: ...

    @abstractmethod
    async def run_shell(
        self,
        command: str,
        *,
        thread_id: str = "",
        timeout: int = 30,
    ) -> SandboxResult: ...

    @abstractmethod
    async def read_file(self, path: str, *, thread_id: str = "") -> SandboxResult: ...

    @abstractmethod
    async def write_file(
        self,
        path: str,
        content: str,
        *,
        thread_id: str = "",
    ) -> SandboxResult: ...

    async def close(self) -> None:
        """清理资源。默认 no-op，子类按需重写。"""
        return None
