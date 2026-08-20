from __future__ import annotations

"""Request-scoped hard budget shared by ReAct and PAE."""

import asyncio
import time
from contextvars import ContextVar

from backend.core.config import settings
from backend.services.usage_service import consume_model_call, record_model_usage


class BudgetExceeded(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class RequestBudget:
    def __init__(self, idempotency_key: str):
        self.idempotency_key = idempotency_key
        self.started_at = time.monotonic()
        self.model_calls = 0
        self.tool_calls = 0
        self.pae_calls = 0
        self.pae_steps = 0
        self.reflection_calls = 0
        self._lock = asyncio.Lock()

    def check_time(self) -> None:
        if time.monotonic() - self.started_at >= settings.REQUEST_TIMEOUT_SECONDS:
            raise BudgetExceeded("REQUEST_TIMEOUT", "请求处理超时，请缩小问题范围后重试。")

    async def consume_model_call(self) -> int:
        async with self._lock:
            self.check_time()
            if self.model_calls >= settings.MAX_MODEL_CALLS_PER_REQUEST:
                raise BudgetExceeded("MODEL_CALL_LIMIT", "本次请求的模型调用次数已达上限。")
            call_index = await asyncio.wait_for(
                consume_model_call(self.idempotency_key),
                timeout=settings.MODEL_CALL_TIMEOUT_SECONDS,
            )
            self.model_calls += 1
            return call_index

    async def consume_tool_call(self) -> None:
        async with self._lock:
            self.check_time()
            if self.tool_calls >= settings.REACT_MAX_TOOL_CALLS:
                raise BudgetExceeded("TOOL_CALL_LIMIT", "本次请求的工具调用次数已达上限。")
            self.tool_calls += 1

    async def consume_pae(self) -> None:
        async with self._lock:
            self.check_time()
            if self.pae_calls >= settings.PAE_MAX_CALLS_PER_REQUEST:
                raise BudgetExceeded("PAE_LIMIT", "本次请求只能执行一次计划流程。")
            self.pae_calls += 1

    async def consume_pae_step(self) -> None:
        async with self._lock:
            self.check_time()
            if self.pae_steps >= settings.MAX_PAE_STEPS_PER_REQUEST:
                raise BudgetExceeded("PAE_STEP_LIMIT", "计划步骤数已达上限。")
            self.pae_steps += 1

    async def consume_reflection(self) -> None:
        async with self._lock:
            self.check_time()
            if self.reflection_calls >= settings.MAX_REFLECTION_CALLS_PER_REQUEST:
                raise BudgetExceeded("REFLECTION_LIMIT", "反思重试次数已达上限。")
            self.reflection_calls += 1


_budget_var: ContextVar[RequestBudget | None] = ContextVar("request_budget", default=None)


def set_request_budget(budget: RequestBudget):
    return _budget_var.set(budget)


def reset_request_budget(token) -> None:
    _budget_var.reset(token)


def get_request_budget() -> RequestBudget | None:
    return _budget_var.get()


async def consume_model_call_if_active() -> int | None:
    budget = get_request_budget()
    if budget is not None:
        return await budget.consume_model_call()
    return None


async def record_model_response_usage(
    *,
    model_id: str,
    prompt,
    response,
    call_index: int | None,
) -> None:
    budget = get_request_budget()
    if budget is None or call_index is None:
        return

    from backend.core.llm import get_model_pricing, get_model_provider

    usage = getattr(response, "usage_metadata", None) or {}
    response_metadata = getattr(response, "response_metadata", None) or {}
    token_usage = response_metadata.get("token_usage") or response_metadata.get("usage") or {}
    input_tokens = int(usage.get("input_tokens") or token_usage.get("prompt_tokens") or 0)
    output_tokens = int(usage.get("output_tokens") or token_usage.get("completion_tokens") or 0)
    total_tokens = int(usage.get("total_tokens") or token_usage.get("total_tokens") or 0)
    cache_hit_tokens = int(
        usage.get("input_token_details", {}).get("cache_read", 0)
        or token_usage.get("prompt_tokens_details", {}).get("cached_tokens", 0)
        or 0
    )
    if not input_tokens and total_tokens and output_tokens:
        input_tokens = max(0, total_tokens - output_tokens)
    if not total_tokens:
        input_tokens = max(input_tokens, len(str(prompt)) // 4)
        output_tokens = max(output_tokens, len(str(getattr(response, "content", "") or "")) // 4)
        usage_source = "unknown"
    else:
        usage_source = "provider"
    input_price, output_price = get_model_pricing(model_id)
    cost = (input_tokens * input_price + output_tokens * output_price) // 1_000_000
    await record_model_usage(
        budget.idempotency_key,
        call_index=call_index,
        model_id=model_id,
        provider=get_model_provider(model_id),
        input_tokens=input_tokens,
        cache_hit_tokens=cache_hit_tokens,
        cache_miss_tokens=max(0, input_tokens - cache_hit_tokens),
        output_tokens=output_tokens,
        usage_source=usage_source,
        cost_microunits=cost,
        price_input_microunits=input_price,
        price_output_microunits=output_price,
    )


async def invoke_model(model, prompt):
    budget = get_request_budget()
    call_index = await budget.consume_model_call() if budget is not None else None
    response = await asyncio.wait_for(
        model.ainvoke(prompt),
        timeout=settings.MODEL_CALL_TIMEOUT_SECONDS,
    )
    if budget is not None and call_index is not None:
        from backend.core.llm import get_model_registry_id

        await record_model_response_usage(
            model_id=get_model_registry_id(model),
            prompt=prompt,
            response=response,
            call_index=call_index,
        )
    return response


async def consume_tool_call_if_active() -> None:
    budget = get_request_budget()
    if budget is not None:
        await budget.consume_tool_call()


async def consume_pae_if_active() -> None:
    budget = get_request_budget()
    if budget is not None:
        await budget.consume_pae()


async def consume_pae_step_if_active() -> None:
    budget = get_request_budget()
    if budget is not None:
        await budget.consume_pae_step()


async def consume_reflection_if_active() -> None:
    budget = get_request_budget()
    if budget is not None:
        await budget.consume_reflection()
