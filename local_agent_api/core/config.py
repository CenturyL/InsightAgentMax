from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

# .env 文件与本文件同目录（local_agent_api/），无论从哪个目录启动都能找到
_ENV_FILE = Path(__file__).parent.parent / ".env"
_PROJECT_ROOT = Path(__file__).parent.parent

# 自动读取环境变量，类型转换与校验
class Settings(BaseSettings):
    # 默认配置：如果环境变量里没有设置，就用这些默认值
    PROJECT_NAME: str = "Local Knowledge Agent API"
    OLLAMA_BASE_URL: str = "http://10.144.144.7:11434" # Ollama 远程(本地部署)服务配置
    LLM_MODEL: str = "qwen3.5:9b"
    
    # 【新增】DeepSeek 官方 API 配置 (完全兼容 OpenAI SDK)
    # 必须在 .env 文件中设置：DEEPSEEK_API_KEY=your_real_key_here
    # 禁止在代码中硬编码 API Key，否则提交 git 会造成密钥泄露
    DEEPSEEK_API_KEY: str  # 无默认值，强制从环境变量/.env 文件读取
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat" # 也可以换成 deepseek-reasoner
    
    # RAG 向量数据库与模型配置
    VECTOR_STORE_PATH: str = str(_PROJECT_ROOT / "data" / "chroma_db")
    PARENT_STORE_PATH: str = str(_PROJECT_ROOT / "data" / "parent_store")
    # 这里选择一个在 Mac 本地跑得快、且对中文友好的轻量级开源 Embedding 模型
    EMBEDDING_MODEL: str = "shibing624/text2vec-base-chinese" 
    EMBEDDING_DEVICE: str = "auto"
    
    # 【工业级新增】本地重排 (Reranker) 模型
    # BAAI (智源研究院) 的 bge-reranker 目前是开源中最顶尖的中文重排模型之一
    RERANKER_MODEL: str = "BAAI/bge-reranker-base"
    RERANKER_DEVICE: str = "auto"

    # ── 长期记忆 & 持久化 Checkpointer（可选）────────────────────────────────
    # 格式：postgresql://用户名:密码@主机:端口/数据库名
    # 配置后：① 对话历史跨重启保留（PostgresSaver）② 用户事实跨会话记忆（pgvector）
    # 不配置则自动降级：① MemorySaver（进程内）② 长期记忆功能关闭
    POSTGRES_URL: Optional[str] = None
    
    # 内部配置类：使用绝对路径定位 .env，避免因工作目录不同而读取失败
    class Config:
        env_file = str(_ENV_FILE)
        env_file_encoding = "utf-8"

# 实例化一个全局配置对象
settings = Settings()
