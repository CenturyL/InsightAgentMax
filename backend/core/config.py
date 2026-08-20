from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# .env 文件与本文件同目录（backend/），无论从哪个目录启动都能找到
_ENV_FILE = Path(__file__).parent.parent / ".env"
_PROJECT_ROOT = Path(__file__).parent.parent

# 自动读取环境变量，类型转换与校验
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 默认配置：如果环境变量里没有设置，就用这些默认值
    PROJECT_NAME: str = "InsightAgentPro API"
    AGENT_NAME: str = "InsightAgentPro"
    WORKSPACE_ROOT: str = str(_PROJECT_ROOT.parent)
    BACKEND_ROOT: str = str(_PROJECT_ROOT)
    
    # 【新增】DeepSeek 官方 API 配置 (完全兼容 OpenAI SDK)
    # 必须在 .env 文件中设置：DEEPSEEK_API_KEY=your_real_key_here
    # 禁止在代码中硬编码 API Key，否则提交 git 会造成密钥泄露
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_FLASH_MODEL: str = "deepseek-v4-flash"
    DEEPSEEK_PRO_MODEL: str = "deepseek-v4-pro"
    DEEPSEEK_MAX_RETRIES: int = 2
    DEEPSEEK_FLASH_INPUT_PRICE_MICROUSD_PER_MILLION: int = 440_000
    DEEPSEEK_FLASH_OUTPUT_PRICE_MICROUSD_PER_MILLION: int = 1_320_000
    DEEPSEEK_PRO_INPUT_PRICE_MICROUSD_PER_MILLION: int = 1_320_000
    DEEPSEEK_PRO_OUTPUT_PRICE_MICROUSD_PER_MILLION: int = 3_960_000
    MINIMAX_API_KEY: Optional[str] = None
    MINIMAX_BASE_URL: str = "https://api.minimax.io/v1"
    MINIMAX_MODEL: str = "MiniMax-M2.5"
    MIMO_API_KEY: Optional[str] = None
    MIMO_BASE_URL: str = "https://api.xiaomimimo.com/v1"
    MIMO_MODEL: str = "mimo-v2-flash"
    MIMO_PRO_MODEL: str = "mimo-v2-pro"
    
    # RAG 知识库与模型配置
    KNOWLEDGE_INDEX_VERSION: str = "qwen3_embedding_4b_v1"
    KNOWLEDGE_IMPORT_LEASE_SECONDS: int = 300
    BM25_MAX_CORPUS_CHUNKS: int = 10000
    RETRIEVAL_MODEL_PROVIDER: str = "local"
    SILICONFLOW_API_KEY: Optional[str] = None
    SILICONFLOW_BASE_URL: str = "https://api.siliconflow.cn/v1"
    EMBEDDING_MODEL: str = "Qwen/Qwen3-Embedding-4B"
    EMBEDDING_DIMENSIONS: int = 1024
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_TIMEOUT_SECONDS: float = 20.0
    RETRIEVAL_PROVIDER_MAX_RETRIES: int = 2
    LOCAL_EMBEDDING_MODEL: str = "shibing624/text2vec-base-chinese"
    EMBEDDING_DEVICE: str = "auto"
    RERANKER_MODEL: str = "Qwen/Qwen3-Reranker-0.6B"
    RERANKER_TOP_N: int = 3
    RERANKER_MAX_DOCUMENTS: int = 20
    RERANKER_MAX_DOCUMENT_CHARS: int = 8000
    RERANKER_TIMEOUT_SECONDS: float = 20.0
    LOCAL_RERANKER_MODEL: str = "BAAI/bge-reranker-base"
    RERANKER_DEVICE: str = "auto"
    BM25_CANDIDATE_K: int = 30
    BM25_K1: float = 1.5
    BM25_B: float = 0.75
    RRF_K: int = 60
    RETRIEVAL_QUOTA_ENABLED: bool = True
    RETRIEVAL_RESERVATION_TIMEOUT_SECONDS: int = 180
    RETRIEVAL_DAILY_CALL_LIMIT: int = 500
    RETRIEVAL_DAILY_CALL_LIMIT_PER_IP: int = 100
    RETRIEVAL_DAILY_TOKEN_LIMIT: int = 2_000_000
    RETRIEVAL_DAILY_TOKEN_LIMIT_PER_IP: int = 500_000
    RETRIEVAL_DAILY_COST_MICROUSD_LIMIT: int = 100_000
    RETRIEVAL_DAILY_COST_MICROUSD_LIMIT_PER_IP: int = 20_000
    EMBEDDING_PRICE_MICROUSD_PER_MILLION: int = 20_000
    RERANKER_PRICE_MICROUSD_PER_MILLION: int = 10_000
    REACT_MAX_TOOL_CALLS: int = 8
    REACT_MAX_NO_PROGRESS_CALLS: int = 3
    # loop_guard：同一个 (tool, args_hash) 连续触发多少次判定为重复循环
    LOOP_GUARD_REPEAT_THRESHOLD: int = 3
    # loop_guard：连续多少次模型调用都没有产生新的工具调用判定为停滞
    LOOP_GUARD_STAGNATION_THRESHOLD: int = 4
    PAE_MAX_CALLS_PER_REQUEST: int = 1
    CONTEXT_COMPRESSION_ENABLED: bool = True
    CONTEXT_COMPRESSION_MAX_MESSAGES: int = 14
    CONTEXT_COMPRESSION_MAX_CHARS: int = 12000
    CONTEXT_COMPRESSION_RECENT_TURNS: int = 4
    CONTEXT_COMPRESSION_MIN_DELTA_MESSAGES: int = 4
    # 执行沙盒：`local`（默认，本机 subprocess）/ `e2b`（云端 Firecracker）/ `disabled`
    SANDBOX_BACKEND: str = "disabled"
    SANDBOX_TIMEOUT_SECONDS: int = 30
    SANDBOX_IDLE_MINUTES: int = 5
    E2B_API_KEY: Optional[str] = None
    MCP_ENABLED: bool = False
    MCP_CONFIG_PATH: Optional[str] = None
    SKILL_COMPAT_MODE: str = "claude"

    # ── 长期记忆 & 持久化 Checkpointer（可选）────────────────────────────────
    # 格式：postgresql://用户名:密码@主机:端口/数据库名
    # 配置后：① 对话历史跨重启保留（PostgresSaver）② 用户事实跨会话记忆（pgvector）
    # 不配置则自动降级：① MemorySaver（进程内）② 长期记忆功能关闭
    POSTGRES_URL: Optional[str] = None
    LONG_TERM_MEMORY_ENABLED: bool = True
    LONG_TERM_MEMORY_COLLECTION_NAME: str = "agent_long_term_memory"

    # ── 请求预算与演示额度 ────────────────────────────────────────────────
    # 本机开发默认只记录 usage，不执行每日额度拦截；部署环境通过 .env 开启。
    USAGE_LIMIT_ENABLED: bool = False
    REQUEST_TIMEOUT_SECONDS: int = 60
    MAX_MODEL_CALLS_PER_REQUEST: int = 8
    MAX_PAE_STEPS_PER_REQUEST: int = 4
    MAX_REFLECTION_CALLS_PER_REQUEST: int = 1
    MODEL_CALL_TIMEOUT_SECONDS: int = 15
    DAILY_MODEL_CALL_LIMIT: int = 100
    DAILY_MODEL_CALL_LIMIT_PER_IP: int = 20
    MODEL_DAILY_TOKEN_LIMIT: int = 2_000_000
    MODEL_DAILY_TOKEN_LIMIT_PER_IP: int = 500_000
    MODEL_REQUEST_TOKEN_LIMIT: int = 100_000
    MODEL_MAX_OUTPUT_TOKENS: int = 4096
    MODEL_DAILY_COST_MICROUSD_LIMIT: int = 1_000_000
    MODEL_DAILY_COST_MICROUSD_LIMIT_PER_IP: int = 200_000
    MODEL_REQUEST_COST_MICROUSD_LIMIT: int = 50_000
    MODEL_INPUT_PRICE_MICROUSD_PER_MILLION: int = 0
    MODEL_OUTPUT_PRICE_MICROUSD_PER_MILLION: int = 0
    IDEMPOTENCY_PENDING_TIMEOUT_SECONDS: int = 180
    THREAD_LOCK_TIMEOUT_SECONDS: int = 180
    MAX_AGENT_CONCURRENCY: int = 4
    MAX_QUERY_LENGTH: int = 8000
    MAX_METADATA_KEYS: int = 20
    MAX_METADATA_DEPTH: int = 3
    MAX_METADATA_VALUE_LENGTH: int = 256
    MAX_UPLOAD_BYTES: int = 10 * 1024 * 1024

# 实例化一个全局配置对象
settings = Settings()
