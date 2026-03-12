# langchain的组装与Parser
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
# 模型
from langchain_ollama import ChatOllama
# 本地文件
from local_agent_api.core.config import settings
from local_agent_api.retrieval.citation import format_citations
from local_agent_api.retrieval.pipeline import (
    retrieve_knowledge_bundle,
)

# 异步流串联各功能
async def get_rag_chain_stream(query: str, temperature: float = 0.7):
    """
    RAG 生成链核心逻辑：检索 (Retrieval) -> 结合 Prompt -> 喂给模型生成 (Generation)
    """
    # 在Chroma检索
    bundle = retrieve_knowledge_bundle(query, k=3)
    docs = bundle.docs
    context_text = bundle.context_text

    # 按请求的 temperature 创建 LLM 实例（RAG 链独立调用，不依赖 Agent 单例）
    llm = ChatOllama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.LLM_MODEL,
        temperature=temperature,
    )

    # 构建 RAG 专属系统提示词 (Prompt Template)
    template = """你是一个面向政策通知、招投标公告和本地知识资料分析的 AI 助手。请利用以下提供的参考信息来回答用户的问题。
如果你在提供的参考信息中找不到答案，请诚实地回答“根据当前知识库无法提供准确答案”，绝对不要编造。

【参考信息开始】
{context}
【参考信息结束】

【引用来源】
{citations}

用户问题：{question}
请输出最终的答案："""
    
    prompt = PromptTemplate.from_template(template)

    # 组装 LangChain LCEL 链 (LangChain Expression Language)
    # 这短一行让数据按管道流转: prompt -> 大模型 -> 输出字符串解析器
    chain = prompt | llm | StrOutputParser()

    # 先推一下前置信息给前端，制造酷炫的用户体验
    yield f"🔍 [系统日志：在本地知识库中检索到 {len(docs)} 个相关片段]\n\n"
    if bundle.applied_filters:
        yield f"🧩 [检索过滤] 已应用元数据过滤：{bundle.applied_filters}\n\n"
    
    # 异步流式 astream，把大模型的逐字思考喷吐给前端
    async for chunk in chain.astream(
        {
            "context": context_text,
            "citations": format_citations(bundle.citations),
            "question": query,
        }
    ):
        yield chunk
