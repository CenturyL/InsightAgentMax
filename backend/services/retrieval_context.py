from __future__ import annotations

import hashlib
import uuid
from contextvars import ContextVar
from dataclasses import dataclass


@dataclass
class RetrievalRequestContext:
    request_key: str
    client_ip: str
    counter: list[int]


_context_var: ContextVar[RetrievalRequestContext | None] = ContextVar(
    "retrieval_request_context",
    default=None,
)


def set_retrieval_request_context(request_key: str, client_ip: str):
    context = RetrievalRequestContext(
        request_key=(request_key or uuid.uuid4().hex).strip(),
        client_ip=(client_ip or "unknown").strip(),
        counter=[0],
    )
    return _context_var.set(context)


def reset_retrieval_request_context(token) -> None:
    _context_var.reset(token)


def next_retrieval_operation_id(kind: str, payload_hash: str) -> tuple[str, str, str]:
    context = _context_var.get()
    if context is None:
        context = RetrievalRequestContext(
            request_key=f"internal-{uuid.uuid4().hex}",
            client_ip="internal",
            counter=[0],
        )
    context.counter[0] += 1
    raw = f"{context.request_key}:{context.counter[0]}:{kind}:{payload_hash}:{uuid.uuid4().hex}"
    operation_id = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return operation_id, context.request_key, context.client_ip
