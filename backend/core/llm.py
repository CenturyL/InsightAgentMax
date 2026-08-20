from __future__ import annotations

from langchain_openai import ChatOpenAI

from backend.core.config import settings


DEFAULT_MODEL_ID = "deepseek-v4-flash"
ROUTER_MODEL_ID = DEFAULT_MODEL_ID
SUMMARY_MODEL_ID = DEFAULT_MODEL_ID

MODEL_REGISTRY = {
    "deepseek-v4-flash": {
        "label": "DeepSeek V4 Flash",
        "provider": "deepseek",
        "remote": True,
        "model_name": settings.DEEPSEEK_FLASH_MODEL,
        "input_price_microusd_per_million": settings.DEEPSEEK_FLASH_INPUT_PRICE_MICROUSD_PER_MILLION,
        "output_price_microusd_per_million": settings.DEEPSEEK_FLASH_OUTPUT_PRICE_MICROUSD_PER_MILLION,
    },
    "deepseek-v4-pro": {
        "label": "DeepSeek V4 Pro",
        "provider": "deepseek",
        "remote": True,
        "model_name": settings.DEEPSEEK_PRO_MODEL,
        "input_price_microusd_per_million": settings.DEEPSEEK_PRO_INPUT_PRICE_MICROUSD_PER_MILLION,
        "output_price_microusd_per_million": settings.DEEPSEEK_PRO_OUTPUT_PRICE_MICROUSD_PER_MILLION,
    },
}

_PUBLIC_ALIASES = {
    "deepseek": DEFAULT_MODEL_ID,
    "deepseek_chat": DEFAULT_MODEL_ID,
}
def create_deepseek_model(
    temperature: float = 0.7,
    model_name: str | None = None,
    *,
    streaming: bool = True,
):
    if not settings.DEEPSEEK_API_KEY:
        raise ValueError("未配置 DEEPSEEK_API_KEY")
    return ChatOpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_BASE_URL,
        model=model_name or settings.DEEPSEEK_FLASH_MODEL,
        temperature=temperature,
        streaming=streaming,
        timeout=settings.MODEL_CALL_TIMEOUT_SECONDS,
        max_retries=settings.DEEPSEEK_MAX_RETRIES,
        max_tokens=settings.MODEL_MAX_OUTPUT_TOKENS,
    )


deepseek_flash_model = (
    create_deepseek_model(model_name=settings.DEEPSEEK_FLASH_MODEL)
    if settings.DEEPSEEK_API_KEY
    else None
)
deepseek_pro_model = (
    create_deepseek_model(model_name=settings.DEEPSEEK_PRO_MODEL)
    if settings.DEEPSEEK_API_KEY
    else None
)
deepseek_router_model = (
    create_deepseek_model(
        temperature=0.0,
        model_name=settings.DEEPSEEK_FLASH_MODEL,
        streaming=False,
    )
    if settings.DEEPSEEK_API_KEY
    else None
)
deepseek_summary_model = (
    create_deepseek_model(
        temperature=0.0,
        model_name=settings.DEEPSEEK_FLASH_MODEL,
        streaming=False,
    )
    if settings.DEEPSEEK_API_KEY
    else None
)

_MODEL_INSTANCES = {
    "deepseek-v4-flash": deepseek_flash_model,
    "deepseek-v4-pro": deepseek_pro_model,
}


def _normalize_model_choice(choice: str | None) -> str:
    normalized = (choice or DEFAULT_MODEL_ID).strip().lower()
    return _PUBLIC_ALIASES.get(normalized, normalized)


def get_model_by_choice(choice: str):
    normalized = _normalize_model_choice(choice)
    model = _MODEL_INSTANCES.get(normalized)
    if model is None:
        raise ValueError("所选模型当前不可用，请切换其他模型。")
    return model


def get_canonical_model_id(choice: str) -> str:
    normalized = _normalize_model_choice(choice)
    if normalized not in MODEL_REGISTRY:
        raise ValueError(f"未注册的模型 ID: {choice}")
    return normalized


def get_default_model():
    return get_model_by_choice(DEFAULT_MODEL_ID)


def get_summary_model():
    if deepseek_summary_model is None:
        raise ValueError("未配置 DEEPSEEK_API_KEY，摘要模型不可用。")
    return deepseek_summary_model


def get_router_model():
    if deepseek_router_model is None:
        raise ValueError("未配置 DEEPSEEK_API_KEY，路由模型不可用。")
    return deepseek_router_model


def get_model_label(choice: str) -> str:
    normalized = _normalize_model_choice(choice)
    details = MODEL_REGISTRY.get(normalized)
    return str(details["label"]) if details else normalized


def get_runtime_models() -> list[dict[str, object]]:
    return [
        {
            "id": model_id,
            "label": details["label"],
            "available": _MODEL_INSTANCES[model_id] is not None,
            "remote": details["remote"],
        }
        for model_id, details in MODEL_REGISTRY.items()
    ]


def is_model_available(choice: str) -> bool:
    normalized = _normalize_model_choice(choice)
    return normalized in MODEL_REGISTRY and _MODEL_INSTANCES[normalized] is not None


def get_model_registry_id(model) -> str:
    raw_name = str(getattr(model, "model_name", None) or getattr(model, "model", None) or "")
    for model_id, details in MODEL_REGISTRY.items():
        if raw_name == details["model_name"]:
            return model_id
    raise ValueError(f"未注册的模型实例: {raw_name or '<unknown>'}")


def get_model_provider(model_or_choice) -> str:
    model_id = model_or_choice if isinstance(model_or_choice, str) else get_model_registry_id(model_or_choice)
    normalized = _normalize_model_choice(model_id)
    details = MODEL_REGISTRY.get(normalized)
    if not details:
        raise ValueError(f"未注册的模型 ID: {model_id}")
    return str(details["provider"])


def get_model_pricing(model_or_choice) -> tuple[int, int]:
    model_id = model_or_choice if isinstance(model_or_choice, str) else get_model_registry_id(model_or_choice)
    normalized = _normalize_model_choice(model_id)
    details = MODEL_REGISTRY.get(normalized)
    if not details:
        raise ValueError(f"未注册的模型 ID: {model_id}")
    return (
        int(details["input_price_microusd_per_million"]),
        int(details["output_price_microusd_per_million"]),
    )
