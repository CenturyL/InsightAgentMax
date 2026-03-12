"""FastAPI 路由层：把 HTTP 接口映射到聊天、入库和评估服务。"""

import os
import uuid
import shutil
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from local_agent_api.api.schemas import (
    ChatRequest,
    GenerationEvalRequest,
    RebuildTestEnvRequest,
    RetrievalEvalRequest,
    SystemBenchmarkRequest,
)
from langchain_core.messages import HumanMessage
from local_agent_api.retrieval.pipeline import process_and_store_document
from local_agent_api.services.eval_service import (
    run_generation_eval_job,
    run_retrieval_compare_job,
    run_retrieval_eval_job,
    run_system_benchmark_job,
)
from local_agent_api.services.agent_service import get_agent_stream
from local_agent_api.services.test_env_service import rebuild_test_environment
from langchain_ollama import ChatOllama
from local_agent_api.core.config import settings

router = APIRouter()


@router.post("/chat/stream", summary="基础流式对话接口(不借用知识库)")
async def chat_stream(request: ChatRequest):
    """
    与本地 Qwen 模型进行直接流式对话。
    """
    # 按请求中的 temperature 动态创建模型实例（轻量，不缓存）
    llm = ChatOllama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.LLM_MODEL,
        temperature=request.temperature,
    )

    # 2. 构建消息体
    messages = [HumanMessage(content=request.query)]

    # 3. 定义异步生成器实现流式 (Streaming) 输出
    async def generate_chat():
        # astream() 是 LangChain 核心的异步流式 API
        # 它会在收到模型的每个 token 时理解 yield 出来，而不是等全句生成完
        async for chunk in llm.astream(messages):
            yield chunk.content

    # 4. 使用 FastAPI 的 StreamingResponse 返回数据流
    return StreamingResponse(generate_chat(), media_type="text/plain")


@router.post("/chat/agent", summary="全能动态智能体 Agent 接口（含 RAG + 工具 + 多轮记忆）")
async def chat_agent_endpoint(request: ChatRequest):
    """
    统一智能体入口：自动在 Qwen / DeepSeek 间路由，调度知识库检索或计算工具。
    - 传入 thread_id 可保持多轮对话记忆（相同 ID 自动拼接历史）
    - 不传 thread_id 则每次独立会话
    - RAG 检索已收敛至 search_company_rules 工具，无需单独调用 /chat/rag
    """
    # 未指定 thread_id 时自动分配 UUID，保证无状态调用的隔离性
    thread_id = request.thread_id or str(uuid.uuid4())
    # user_id 不传则为空串，inject_long_term_memory 中间件会跳过记忆读写
    user_id = request.user_id or ""

    async def generate_agent_output():
        async for chunk in get_agent_stream(
                request.query,
                thread_id=thread_id,
                user_id=user_id,
                task_mode=request.task_mode,
                metadata_filters=request.metadata_filters,
        ):
            yield chunk

    return StreamingResponse(generate_agent_output(), media_type="text/plain")


@router.post("/eval/retrieval", summary="运行离线检索评估")
async def run_retrieval_eval_endpoint(request: RetrievalEvalRequest):
    """离线检索评估接口封装。"""
    try:
        metrics = run_retrieval_eval_job(
            dataset_path=request.dataset_path,
            top_k=request.top_k,
            candidate_k=request.candidate_k,
            strategy=request.strategy,
        )
        return {"code": 200, "message": "评估完成", "metrics": metrics.model_dump()}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"检索评估失败: {exc}")


@router.post("/eval/retrieval/compare", summary="运行检索 baseline 对比")
async def run_retrieval_compare_endpoint(request: RetrievalEvalRequest):
    """检索 baseline 对比接口封装。"""
    try:
        report = run_retrieval_compare_job(
            dataset_path=request.dataset_path,
            top_k=request.top_k,
            candidate_k=request.candidate_k,
        )
        return {"code": 200, "message": "对比完成", "report": report.model_dump()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"检索对比失败: {exc}")


@router.post("/eval/generation", summary="运行离线生成评估")
async def run_generation_eval_endpoint(request: GenerationEvalRequest):
    """生成质量评估接口封装。"""
    try:
        metrics = await run_generation_eval_job(
            dataset_path=request.dataset_path,
            candidate_k=request.candidate_k,
        )
        return {"code": 200, "message": "评估完成", "metrics": metrics.model_dump()}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"生成评估失败: {exc}")


@router.post("/testing/rebuild", summary="一键重建本地测试环境")
async def rebuild_test_env_endpoint(request: RebuildTestEnvRequest):
    """重建前端演示用测试语料和 benchmark 数据集。"""
    try:
        result = rebuild_test_environment(
            force_download=request.force_download,
            run_retrieval_eval=request.run_retrieval_eval,
        )
        return {"code": 200, "message": "测试环境重建完成", "result": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"测试环境重建失败: {exc}")


@router.post("/eval/benchmark", summary="运行系统 benchmark")
async def run_system_benchmark_endpoint(request: SystemBenchmarkRequest):
    """运行系统级 benchmark，测默认场景下的端到端时延。"""
    try:
        metrics = await run_system_benchmark_job(
            retrieval_dataset_path=request.retrieval_dataset_path,
            candidate_k=request.candidate_k,
        )
        return {"code": 200, "message": "benchmark 完成", "metrics": metrics.model_dump()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"benchmark 失败: {exc}")


@router.post("/knowledge/upload", summary="上传文件并录入本地知识库")
async def upload_knowledge(file: UploadFile = File(...)):
    """
    接收用户上传的 TXT / MD / PDF / HTML / CSV / 图片文件，
    进行结构化切块、Embedding 与入库，最终保存到本地 Chroma 向量库。
    """
    os.makedirs("local_agent_api/data/temp", exist_ok=True)
    temp_file_path = f"local_agent_api/data/temp/{file.filename}"

    # 1. 临时保存文件
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 2. 调用存库逻辑，并保留原始上传文件名作为知识库 source
        chunks_count = process_and_store_document(
            temp_file_path,
            metadata_overrides={
                "source": file.filename,
                "upload_name": file.filename,
            },
        )
        return {
            "code": 200,
            "message": "录入成功！",
            "filename": file.filename,
            "source": file.filename,
            "chunks_inserted": chunks_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")
    finally:
        # 3. 擦屁股：存进向量库后删掉服务器上的临时原文件
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
