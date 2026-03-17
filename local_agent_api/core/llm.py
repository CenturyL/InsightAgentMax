from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from local_agent_api.core.config import settings

# ============================================================
# 模块级单例：全项目共享同一个模型实例，避免重复创建
# middleware 的 request.override(model=...) 会在运行时动态切换，
# 这里只负责提供"默认底座"和"高级底座"两个对象
# ============================================================

def _resolve_basic_model_config() -> tuple[str, str, str]:
    """
    统一解析基础模型配置。

    兼容两套配置来源：
    1. 新配置：BASIC_MODEL_PROVIDER / BASIC_MODEL_BASE_URL / BASIC_MODEL_NAME
    2. 旧配置：OLLAMA_BASE_URL / LLM_MODEL
    """
    provider = settings.BASIC_MODEL_PROVIDER.strip().lower()
    if provider not in {"ollama", "openai_compatible"}:
        raise ValueError(f"不支持的 BASIC_MODEL_PROVIDER: {settings.BASIC_MODEL_PROVIDER}")

    if settings.OLLAMA_BASE_URL and provider == "ollama":
        base_url = settings.OLLAMA_BASE_URL
    else:
        base_url = settings.BASIC_MODEL_BASE_URL

    if settings.LLM_MODEL and provider == "ollama":
        model_name = settings.LLM_MODEL
    else:
        model_name = settings.BASIC_MODEL_NAME

    return provider, base_url, model_name


def create_basic_model(temperature: float = 0.7):
    """按配置创建基础模型实例，支持 Ollama 或 OpenAI 兼容接口（如 vLLM）。"""
    provider, base_url, model_name = _resolve_basic_model_config()

    if provider == "ollama":
        return ChatOllama(
            base_url=base_url,
            model=model_name,
            temperature=temperature,
        )

    return ChatOpenAI(
        api_key=settings.BASIC_MODEL_API_KEY,
        base_url=base_url,
        model=model_name,
        temperature=temperature,
        streaming=True,
    )


# 默认底座：本地模型部署（支持 Ollama 或 OpenAI 兼容服务）
basic_model = create_basic_model()

# 高级底座：云端 DeepSeek（兼容 OpenAI 规范）
advanced_model = ChatOpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url=settings.DEEPSEEK_BASE_URL,
    model=settings.DEEPSEEK_MODEL,
    temperature=0.7,
    streaming=True,
)
