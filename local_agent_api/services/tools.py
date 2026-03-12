import datetime
from langchain_core.tools import tool
from local_agent_api.retrieval.pipeline import retrieve_knowledge_bundle
from local_agent_api.services.tool_context import get_tool_metadata_filters

# 工具1：【通用知识检索】
# response_format="content_and_artifact"：
#   - 返回 tuple[str, list]，str 进入 LLM 上下文，list(Documents) 作为 artifact 保留原始来源
#   - 这样 Agent 在引用时可以携带文档出处，便于后续实现 citation 功能
@tool(response_format="content_and_artifact")
def search_policy_and_tender_knowledge(query: str) -> tuple[str, list]:
    """搜索政策通知、招投标公告、申报指南、附件材料以及知识库中的其他本地资料。
    当用户的问题需要事实依据、文档证据、政策条款、招标条件或结构化来源时，优先调用此工具。"""

    bundle = retrieve_knowledge_bundle(query, k=3, metadata_filters=get_tool_metadata_filters())
    if not bundle.docs:
        return "未能在当前知识库中找到相关信息。", []

    return bundle.context_text, bundle.docs

@tool(response_format="content_and_artifact")
def search_company_rules(query: str) -> tuple[str, list]:
    """搜索公司内部制度、办公规则、WIFI 密码等内部知识。
    这是辅助工具，仅在用户明确询问内部制度、办公安排、请假规则等公司专属信息时调用。"""

    bundle = retrieve_knowledge_bundle(query, k=3, metadata_filters=get_tool_metadata_filters())
    if not bundle.docs:
        return "未能在内部知识范围内找到相关信息。", []

    return bundle.context_text, bundle.docs


# 工具3：【实时增强：时间提供器】
# 纯本地大模型不知道当前的现实时间，我们以此弥补它的短板
@tool
def get_current_time(timezone: str = "Asia/Shanghai") -> str:
    """获取当前的系统准确时间和日期。
    当用户问及“现在几点了”或有时间概念的计算（如“明天是几月几号”）需要作为锚点时使用。"""
    
    now = datetime.datetime.now()
    return f"当前时间是: {now.strftime('%Y-%m-%d %H:%M:%S')}"


# 我们将写好的所有工具以列表形式暴露出去，给智能体挂载使用
AGENT_TOOLS = [search_policy_and_tender_knowledge, search_company_rules, get_current_time]
