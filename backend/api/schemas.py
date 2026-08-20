"""FastAPI 路由共享的 Pydantic 请求模型。"""

from typing import Any, Optional
from pydantic import BaseModel, Field, model_validator

from backend.core.config import settings

# 用Pydantic定义传入参数规范，FastAPI靠它来拦截所有非法请求
class ChatRequest(BaseModel):
    """统一聊天请求体，供直连 chat 和 agent 接口复用。"""
    query: str = Field(..., min_length=1, max_length=settings.MAX_QUERY_LENGTH, description="用户的提问内容")
    temperature: float = Field(default=0.7, ge=0, le=1.5, description="模型生成的温度值，越高越有创造性")
    # 会话 ID，传入相同 thread_id 可保持多轮对话记忆
    # 不传则每次独立（自动分配 UUID），传固定值则持续累积历史
    thread_id: Optional[str] = Field(default=None, min_length=1, max_length=128, description="会话ID，相同ID保持多轮记忆，不传则每次独立")
    # 长期记忆：用户唯一标识（如用户名/邮箱），用于 pgvector 按用户隔离存取历史记忆
    # 不传则不启用长期记忆功能
    user_id: Optional[str] = Field(default=None, max_length=128, description="用户ID，用于长期记忆隔离；不传则跳过长期记忆")
    plan_mode: Optional[str] = Field(default=None, description="可选计划模式：auto、compare、extract、report、research、strict_plan")
    task_mode: Optional[str] = Field(default=None, description="旧字段兼容：将被映射为 plan_mode")
    model_choice: str = Field(default="deepseek-v4-flash", min_length=1, max_length=64, description="模型注册表中的模型 ID")
    metadata_filters: Optional[dict[str, Any]] = Field(default=None, description="可选元数据过滤条件，如 region、year、source_type")

    @model_validator(mode="after")
    def validate_metadata_filters(self):
        def walk(value: Any, depth: int) -> None:
            if depth > 3:
                raise ValueError("metadata_filters 嵌套层级不能超过 3 层")
            if isinstance(value, dict):
                if len(value) > 20:
                    raise ValueError("metadata_filters 字段数量不能超过 20 个")
                for key, item in value.items():
                    if len(str(key)) > 64:
                        raise ValueError("metadata_filters 字段名过长")
                    walk(item, depth + 1)
            elif isinstance(value, list):
                if len(value) > 20:
                    raise ValueError("metadata_filters 数组长度不能超过 20")
                for item in value:
                    walk(item, depth + 1)
            elif isinstance(value, str) and len(value) > 256:
                raise ValueError("metadata_filters 字符串值过长")

        if self.metadata_filters is not None:
            walk(self.metadata_filters, 0)
        return self


class RuntimeSkillAsset(BaseModel):
    """前端可编辑的 Skill 文件。"""
    filename: str = Field(..., description="skill 文件名，如 research.md")
    content: str = Field(..., description="skill 文件内容")
    source: str = Field(default="claude", description="skill 来源")


class RuntimeAssetsResponse(BaseModel):
    """运行时资产读取结果。"""
    insight_md: str = Field(default="", description="当前用户的 insight.md 内容（persona + style + memory 合一）")
    skills: list[RuntimeSkillAsset] = Field(default_factory=list, description="skills 目录下的 markdown skills")


class RuntimeAssetsUpdateRequest(BaseModel):
    """运行时资产更新请求。"""
    insight_md: str = Field(default="", description="insight.md 新内容")
    skills: list[RuntimeSkillAsset] = Field(default_factory=list, description="需要保存的技能文件内容")


class RuntimeModel(BaseModel):
    id: str
    label: str
    available: bool = False
    remote: bool = False


class RuntimeModelsResponse(BaseModel):
    models: list[RuntimeModel] = Field(default_factory=list)


class RuntimeMCPServerStatus(BaseModel):
    server_name: str
    transport: str
    connected: bool = False
    tool_names: list[str] = Field(default_factory=list)


class RuntimeMCPServerConfig(BaseModel):
    server_name: str
    transport: str
    command: Optional[str] = None
    args: list[str] = Field(default_factory=list)
    cwd: Optional[str] = None
    url: Optional[str] = None
    headers: dict[str, str] = Field(default_factory=dict)


class RuntimeMCPConfigResponse(BaseModel):
    config_text: str = Field(default="", description=".mcp.json 原始文本")
    servers: list[RuntimeMCPServerConfig] = Field(default_factory=list, description="解析后的 MCP servers")
    status: list[RuntimeMCPServerStatus] = Field(default_factory=list, description="当前 MCP 连接状态")


class RuntimeMCPConfigUpdateRequest(BaseModel):
    config_text: str = Field(..., description=".mcp.json 新内容")


class SessionRequest(BaseModel):
    user_id: str = Field(..., description="用户ID，直接作为历史会话归属键")


class SessionSummary(BaseModel):
    thread_id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    last_message_preview: str


class SessionBootstrapResponse(BaseModel):
    sessions: list[SessionSummary] = Field(default_factory=list)
    current_thread_id: str


class SessionListResponse(BaseModel):
    sessions: list[SessionSummary] = Field(default_factory=list)


class SessionMessage(BaseModel):
    turn_id: Optional[str] = None
    role: str
    content: str
    created_at: Optional[str] = None
    events: list[dict[str, Any]] = Field(default_factory=list)


class SessionMessagesResponse(BaseModel):
    thread_id: str
    messages: list[SessionMessage] = Field(default_factory=list)
