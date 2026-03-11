"""Pydantic request models shared by FastAPI routes."""

from typing import Any, Optional
from pydantic import BaseModel, Field

# 用Pydantic定义传入参数规范，FastAPI靠它来拦截所有非法请求
class ChatRequest(BaseModel):
    """Unified chat payload used by both direct chat and agent endpoints."""
    query: str = Field(..., description="用户的提问内容")
    temperature: float = Field(default=0.7, description="模型生成的温度值，越高越有创造性")
    # P1-7：会话 ID，传入相同 thread_id 可保持多轮对话记忆
    # 不传则每次独立（自动分配 UUID），传固定值则持续累积历史
    thread_id: Optional[str] = Field(default=None, description="会话ID，相同ID保持多轮记忆，不传则每次独立")
    # 长期记忆：用户唯一标识（如用户名/邮箱），用于 pgvector 按用户隔离存取历史记忆
    # 不传则不启用长期记忆功能
    user_id: Optional[str] = Field(default=None, description="用户ID，用于长期记忆隔离；不传则跳过长期记忆")
    task_mode: Optional[str] = Field(default=None, description="可选任务模式：qa、compare、extract、report")
    metadata_filters: Optional[dict[str, Any]] = Field(default=None, description="可选元数据过滤条件，如 region、year、source_type")


class RetrievalEvalRequest(BaseModel):
    """Input schema for retrieval eval and retrieval baseline comparison endpoints."""
    dataset_path: Optional[str] = Field(
        default=None,
        description="离线检索评估数据集路径，默认读取 local_agent_api/data/eval/retrieval_eval_dataset.jsonl",
    )
    top_k: int = Field(default=3, ge=1, le=20, description="计算 Precision@k / Recall@k 的 top-k")
    candidate_k: int = Field(default=15, ge=1, le=100, description="候选召回数量")
    strategy: str = Field(default="hybrid_rerank", description="检索策略：dense_only、dense_rerank、hybrid_only、hybrid_rerank")


class GenerationEvalRequest(BaseModel):
    """Input schema for generation-quality evaluation."""
    dataset_path: Optional[str] = Field(
        default=None,
        description="离线生成评估数据集路径，默认读取 local_agent_api/data/eval/generation_eval_dataset.jsonl",
    )
    candidate_k: int = Field(default=15, ge=1, le=100, description="检索候选数量")


class RebuildTestEnvRequest(BaseModel):
    """Options for rebuilding the demo corpus and optional post-rebuild evaluation."""
    force_download: bool = Field(default=False, description="是否强制重新下载公开测试文档")
    run_retrieval_eval: bool = Field(default=True, description="是否在重建完成后自动跑一次检索评估")


class SystemBenchmarkRequest(BaseModel):
    """Input schema for the system-level benchmark route."""
    retrieval_dataset_path: Optional[str] = Field(
        default=None,
        description="检索 benchmark 数据集路径，默认读取 local_agent_api/data/eval/retrieval_eval_dataset.jsonl",
    )
    candidate_k: int = Field(default=8, ge=1, le=100, description="检索候选数量")
