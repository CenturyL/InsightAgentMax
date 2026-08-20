"""FastAPI 路由层：把 HTTP 接口映射到聊天、入库和评估服务。"""

import asyncio
import json
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
from backend.api.schemas import (
    ChatRequest,
    RuntimeAssetsResponse,
    RuntimeAssetsUpdateRequest,
    RuntimeModelsResponse,
    SessionBootstrapResponse,
    SessionListResponse,
    SessionMessagesResponse,
    SessionRequest,
    SessionSummary,
)
from langchain_core.messages import HumanMessage
from backend.retrieval.pipeline import process_and_store_document
from backend.core.embedding import RetrievalProviderError
from backend.retrieval.postgres_store import KnowledgeStoreError
from backend.services.agent_service import get_agent_stream
from backend.services.runtime_assets_service import (
    load_runtime_assets,
    save_runtime_assets,
)
from backend.services.session_service import (
    bootstrap_sessions,
    create_empty_session,
    delete_session,
    emit_session_event,
    ensure_session_started,
    finish_session_turn,
    get_session,
    list_sessions,
    load_session_replay,
    SessionEventLimitError,
    SessionOwnershipError,
    start_session_turn,
)
from backend.core.llm import (
    DEFAULT_MODEL_ID,
    get_canonical_model_id,
    get_model_by_choice,
    get_model_pricing,
    get_model_provider,
    get_runtime_models,
    is_model_available,
)
from backend.core.config import settings
from backend.runtime.budget import BudgetExceeded, RequestBudget, consume_model_call_if_active, reset_request_budget, set_request_budget
from backend.services.usage_service import (
    RequestReservation,
    UsageServiceError,
    acquire_thread_lock,
    begin_request,
    finish_request,
    release_thread_lock,
    request_body_hash,
    record_model_usage,
)
from backend.services.retrieval_context import reset_retrieval_request_context, set_retrieval_request_context
from backend.services.retrieval_usage_service import RetrievalUsageError

router = APIRouter()
_agent_concurrency = asyncio.Semaphore(settings.MAX_AGENT_CONCURRENCY)


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _estimate_request_tokens(payload: dict) -> int:
    query = str(payload.get("query") or "")
    return min(settings.MODEL_REQUEST_TOKEN_LIMIT, max(0, len(query) // 4 + settings.MODEL_MAX_OUTPUT_TOKENS))


async def _begin(request: Request, payload: dict, thread_id: str | None) -> tuple[str, RequestReservation, str]:
    key = request.headers.get("Idempotency-Key") or str(uuid.uuid4())
    try:
        model_id = get_canonical_model_id(str(payload.get("model_choice") or DEFAULT_MODEL_ID))
        input_price, output_price = get_model_pricing(model_id)
        reservation = await begin_request(
            idempotency_key=key,
            request_hash=request_body_hash(payload),
            client_ip=_client_ip(request),
            thread_id=thread_id,
            model_id=model_id,
            estimated_tokens=_estimate_request_tokens(payload),
            price_input_microunits=input_price,
            price_output_microunits=output_price,
        )
        return key, reservation, _client_ip(request)
    except UsageServiceError as exc:
        status = 409 if exc.code in {"REQUEST_IN_PROGRESS", "IDEMPOTENCY_KEY_REUSED", "REQUEST_NOT_REPLAYABLE"} else 429 if exc.code in {"DAILY_LIMIT_EXCEEDED", "DAILY_MODEL_LIMIT_EXCEEDED", "MODEL_TOKEN_LIMIT_EXCEEDED", "MODEL_COST_LIMIT_EXCEEDED"} else 503
        raise HTTPException(status_code=status, detail={"code": exc.code, "message": exc.message}) from exc


def _stream_cached(rows: list[dict], media_type: str) -> StreamingResponse:
    if media_type == "text/plain":
        return StreamingResponse((str(row.get("content", "")) for row in rows), media_type=media_type)
    return StreamingResponse(
        (json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        media_type=media_type,
    )


# 不走 RAG、不走 Tool、不走 Agent，直接调用所选 DeepSeek 模型
@router.post("/chat/stream", summary="基础流式对话接口(不借用知识库)")
async def chat_stream(body: ChatRequest, request: Request):
    """
    与所选 DeepSeek 模型进行直接流式对话。
    """
    if not is_model_available(body.model_choice):
        raise HTTPException(status_code=400, detail={"code": "MODEL_UNAVAILABLE", "message": "所选模型当前不可用，请切换其他模型。"})
    key, reservation, _ = await _begin(request, body.model_dump(), None)
    if reservation.status == "completed":
        return _stream_cached(reservation.response or [], "text/plain")
    try:
        llm = get_model_by_choice(body.model_choice)
    except Exception as exc:
        await finish_request(key, response=None, success=False)
        raise HTTPException(status_code=503, detail={"code": "MODEL_UNAVAILABLE", "message": "当前模型暂时不可用，请稍后重试。"}) from exc

    # 2. 构建消息体
    messages = [HumanMessage(content=body.query)]

    # 3. 定义异步生成器实现流式 (Streaming) 输出
    async def generate_chat():
        chunks: list[dict] = []
        budget_token = set_request_budget(RequestBudget(key))
        success = False
        call_index: int | None = None
        output_parts: list[str] = []
        provider_usage: dict = {}
        try:
            async with asyncio.timeout(settings.REQUEST_TIMEOUT_SECONDS):
                call_index = await consume_model_call_if_active()
                async with asyncio.timeout(settings.MODEL_CALL_TIMEOUT_SECONDS):
                    async for chunk in llm.astream(messages):
                        content = str(getattr(chunk, "content", "") or "")
                        if content:
                            output_parts.append(content)
                            row = {"type": "text", "content": content}
                            chunks.append(row)
                            yield content
                        provider_usage = getattr(chunk, "usage_metadata", None) or provider_usage
            success = True
        except BudgetExceeded as exc:
            yield f"请求已停止：{exc}"
        except asyncio.CancelledError:
            raise
        except Exception:
            yield "当前模型暂时不可用，请稍后重试。"
        finally:
            reset_request_budget(budget_token)
            if call_index is not None:
                try:
                    input_tokens = int(provider_usage.get("input_tokens") or len(body.query) // 4)
                    output_tokens = int(provider_usage.get("output_tokens") or len("".join(output_parts)) // 4)
                    model_id = get_canonical_model_id(body.model_choice)
                    input_price, output_price = get_model_pricing(model_id)
                    cost = (input_tokens * input_price + output_tokens * output_price) // 1_000_000
                    await record_model_usage(
                        key,
                        call_index=call_index,
                        model_id=model_id,
                        provider=get_model_provider(model_id),
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        usage_source="provider" if provider_usage else "estimated",
                        cost_microunits=cost,
                        price_input_microunits=input_price,
                        price_output_microunits=output_price,
                    )
                except Exception as exc:
                    print(f"⚠️ [usage] 直连流 usage 记录失败：{type(exc).__name__}")
            await finish_request(key, response=chunks, success=success)

    # StreamingResponse 是 FastAPI/Starlette 提供的“流式 HTTP 响应包装器”：
    # - 它接收一个（异步）生成器
    # - 生成器每 yield 一段，HTTP 响应体就继续往前端写一段
    # - 不需要等完整答案准备好才返回
    return StreamingResponse(generate_chat(), media_type="text/plain")

# 动态智能体 Agent 接口
@router.post("/chat/agent", summary="通用智能体 Agent 接口（ReAct 主循环 + Tools + PAE）")
async def chat_agent_endpoint(body: ChatRequest, request: Request):
    """
    统一智能体入口：默认走 ReAct 主循环，必要时由模型主动调用 PAE 工具。
    - 传入 thread_id 可保持多轮对话记忆（相同 ID 自动拼接历史）
    - 不传 thread_id 则每次独立会话
    - RAG 检索已收敛至 search_company_rules 工具，无需单独调用 /chat/rag
    """
    # 未指定 thread_id 时自动分配 UUID，保证无状态调用的隔离性
    thread_id = body.thread_id or str(uuid.uuid4())
    # user_id 不传则为空串，inject_long_term_memory 中间件会跳过记忆读写
    user_id = body.user_id or ""
    if not is_model_available(body.model_choice):
        raise HTTPException(status_code=400, detail={"code": "MODEL_UNAVAILABLE", "message": "所选模型当前不可用，请切换其他模型。"})
    key, reservation, client_ip = await _begin(request, body.model_dump(), thread_id)
    if reservation.status == "completed":
        return _stream_cached(reservation.response or [], "application/x-ndjson")
    agent_slot_acquired = False
    try:
        await asyncio.wait_for(_agent_concurrency.acquire(), timeout=settings.REQUEST_TIMEOUT_SECONDS)
        agent_slot_acquired = True
        if not await acquire_thread_lock(thread_id, key):
            await finish_request(key, response=None, success=False)
            _agent_concurrency.release()
            agent_slot_acquired = False
            raise HTTPException(status_code=409, detail={"code": "THREAD_BUSY", "message": "同一会话正在处理中，请稍后重试。"})
    except asyncio.TimeoutError as exc:
        await finish_request(key, response=None, success=False)
        raise HTTPException(status_code=429, detail={"code": "AGENT_BUSY", "message": "当前服务繁忙，请稍后重试。"}) from exc
    except UsageServiceError as exc:
        await finish_request(key, response=None, success=False)
        if agent_slot_acquired:
            _agent_concurrency.release()
        raise HTTPException(status_code=503, detail={"code": exc.code, "message": exc.message}) from exc

    turn_id = reservation.turn_id
    session_turn_started = False
    if user_id.strip() and turn_id:
        try:
            await ensure_session_started(thread_id, user_id, body.query)
            turn_id = await start_session_turn(
                thread_id=thread_id,
                user_id=user_id,
                turn_id=turn_id,
                idempotency_key=key,
            )
            session_turn_started = True
        except SessionOwnershipError as exc:
            await finish_request(key, response=None, success=False)
            await release_thread_lock(thread_id, key)
            if agent_slot_acquired:
                _agent_concurrency.release()
            raise HTTPException(status_code=403, detail={"code": exc.code, "message": "当前会话不可访问。"}) from exc
        except Exception as exc:
            await finish_request(key, response=None, success=False)
            await release_thread_lock(thread_id, key)
            if agent_slot_acquired:
                _agent_concurrency.release()
            raise HTTPException(status_code=503, detail={"code": "SESSION_STORE_UNAVAILABLE", "message": "会话服务暂时不可用，请稍后重试。"}) from exc

    async def generate_agent_output():
        # 这里返回的是“异步生成器”，不是一次性算完整答案后再 return。
        # FastAPI 的 StreamingResponse 会边迭代、边把 chunk 刷给前端，
        # 因此主循环 token、工具 trace、PAE 阶段信息都能实时显示。
        chunks: list[dict] = []
        budget_token = set_request_budget(RequestBudget(key))
        success = False
        turn_status = "failed"
        try:
            async with asyncio.timeout(settings.REQUEST_TIMEOUT_SECONDS):
                plan_mode = body.plan_mode or body.task_mode
                async for chunk in get_agent_stream(
                    body.query,
                    thread_id=thread_id,
                    user_id=user_id,
                    turn_id=turn_id if session_turn_started else None,
                    plan_mode=plan_mode,
                    model_choice=body.model_choice,
                    metadata_filters=body.metadata_filters,
                    request_key=key,
                    client_ip=client_ip,
                ):
                    chunks.append(chunk)
                    yield json.dumps(chunk, ensure_ascii=False) + "\n"
            success = True
            turn_status = "completed"
        except BudgetExceeded as exc:
            trace_row = {
                "type": "trace",
                "content": f"❌ [请求终止] {exc}",
            }
            chunks.append(trace_row)
            yield json.dumps(trace_row, ensure_ascii=False) + "\n"
            row = {"type": "error", "code": exc.code, "content": str(exc)}
            chunks.append(row)
            yield json.dumps(row, ensure_ascii=False) + "\n"
        except asyncio.CancelledError:
            turn_status = "cancelled"
            raise
        except asyncio.TimeoutError:
            trace_row = {
                "type": "trace",
                "content": "❌ [请求终止] 请求处理超时，请缩小问题范围后重试。",
            }
            chunks.append(trace_row)
            yield json.dumps(trace_row, ensure_ascii=False) + "\n"
            row = {
                "type": "error",
                "code": "REQUEST_TIMEOUT",
                "content": "请求处理超时，请缩小问题范围后重试。",
            }
            chunks.append(row)
            yield json.dumps(row, ensure_ascii=False) + "\n"
        except Exception:
            trace_row = {
                "type": "trace",
                "content": "❌ [请求终止] 当前请求暂时失败，请稍后重试。",
            }
            chunks.append(trace_row)
            yield json.dumps(trace_row, ensure_ascii=False) + "\n"
            row = {"type": "error", "code": "REQUEST_FAILED", "content": "当前请求暂时失败，请稍后重试。"}
            chunks.append(row)
            yield json.dumps(row, ensure_ascii=False) + "\n"
        finally:
            reset_request_budget(budget_token)
            if session_turn_started and turn_id:
                try:
                    await emit_session_event(
                        turn_id=turn_id,
                        event_type="turn_end",
                        event_key="turn_end",
                        content=turn_status,
                        payload={"status": turn_status},
                    )
                except SessionEventLimitError:
                    pass
                finally:
                    try:
                        await finish_session_turn(turn_id, turn_status)
                    except Exception as exc:
                        print(f"⚠️ [session] turn 收尾失败：{type(exc).__name__}")
            try:
                await finish_request(key, response=chunks if success else [], success=success)
            finally:
                await release_thread_lock(thread_id, key)
                if agent_slot_acquired:
                    _agent_concurrency.release()

    # 这里返回的不是普通 JSONResponse，而是 StreamingResponse。
    # 因此 Agent 主循环里的 token、工具 trace、PAE 阶段信息都可以边产生边发送给前端。
    return StreamingResponse(generate_agent_output(), media_type="application/x-ndjson")


@router.get("/runtime/models", response_model=RuntimeModelsResponse, summary="读取可用模型注册表")
async def get_runtime_model_list():
    return {"models": get_runtime_models()}

# 上传文件接口
@router.post("/knowledge/upload", summary="上传文件并录入本地知识库")
async def upload_knowledge(request: Request, file: UploadFile = File(...)):
    """
    接收用户上传的 TXT / MD / PDF / HTML / CSV 文件，
    进行结构化切块、Embedding，并原子写入 PostgreSQL/pgvector 知识库。
    """
    original_name = Path(file.filename or "upload.bin").name
    suffix = Path(original_name).suffix.lower()
    if suffix not in {".txt", ".md", ".pdf", ".html", ".htm", ".csv"}:
        raise HTTPException(status_code=415, detail={"code": "UNSUPPORTED_FILE_TYPE", "message": "仅支持 TXT、MD、PDF、HTML 和 CSV 文件。"})
    temp_dir = Path(settings.BACKEND_ROOT) / "data" / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file_path = temp_dir / f"{uuid.uuid4().hex}{suffix}"

    try:
        size = 0
        with temp_file_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > settings.MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail={"code": "UPLOAD_TOO_LARGE", "message": "上传文件不能超过 10 MB。"})
                buffer.write(chunk)
        retrieval_token = set_retrieval_request_context(
            request.headers.get("Idempotency-Key") or uuid.uuid4().hex,
            _client_ip(request),
        )
        try:
            chunks_count = await asyncio.to_thread(
                process_and_store_document,
                str(temp_file_path),
                {
                    "source": original_name,
                    "upload_name": original_name,
                },
            )
        finally:
            reset_retrieval_request_context(retrieval_token)
        return {
            "code": 200,
            "message": "录入成功！",
            "filename": original_name,
            "source": original_name,
            "chunks_inserted": chunks_count
        }
    except HTTPException:
        raise
    except RetrievalUsageError as exc:
        raise HTTPException(status_code=429, detail={"code": exc.code, "message": exc.message}) from exc
    except RetrievalProviderError as exc:
        raise HTTPException(status_code=503, detail={"code": exc.code, "message": exc.message}) from exc
    except KnowledgeStoreError as exc:
        status_code = 409 if exc.code == "KNOWLEDGE_IMPORT_IN_PROGRESS" else 503
        raise HTTPException(status_code=status_code, detail={"code": exc.code, "message": exc.message}) from exc
    except Exception:
        raise HTTPException(status_code=500, detail={"code": "UPLOAD_PROCESSING_FAILED", "message": "文件处理失败，请检查文件后重试。"})
    finally:
        # 3. 擦屁股：存进向量库后删掉服务器上的临时原文件
        temp_file_path.unlink(missing_ok=True)


@router.get("/runtime/assets", response_model=RuntimeAssetsResponse, summary="读取运行时资产")
async def get_runtime_assets(user_id: str = Query(default="", description="用户ID，加载该用户的 insight.md")):
    """读取 insight.md / skills，供前端编辑。"""
    return load_runtime_assets(user_id)


@router.put("/runtime/assets", response_model=RuntimeAssetsResponse, summary="更新运行时资产")
async def update_runtime_assets(request: RuntimeAssetsUpdateRequest, user_id: str = Query(default="", description="用户ID")):
    """更新 insight.md / skills。"""
    return save_runtime_assets(
        user_id=user_id,
        insight_md=request.insight_md,
        skills=[skill.model_dump() for skill in request.skills],
    )


@router.post("/sessions/bootstrap", response_model=SessionBootstrapResponse, summary="加载用户历史 session 并创建新会话")
async def bootstrap_user_sessions(request: SessionRequest):
    return await bootstrap_sessions(request.user_id)


@router.post("/sessions", response_model=SessionSummary, summary="为用户创建新会话")
async def create_user_session(request: SessionRequest):
    return await create_empty_session(request.user_id)


@router.get("/sessions", response_model=SessionListResponse, summary="按 USERID 列出历史 session")
async def list_user_sessions(user_id: str = Query(..., description="用户ID")):
    return {"sessions": await list_sessions(user_id)}


@router.get("/sessions/{thread_id}/messages", response_model=SessionMessagesResponse, summary="加载指定历史 session 消息")
async def get_session_messages(thread_id: str, user_id: str = Query(..., description="用户ID")):
    session = await get_session(thread_id, user_id)
    if session is None:
        raise HTTPException(status_code=404, detail="未找到该用户下的会话。")
    return {
        "thread_id": thread_id,
        "messages": await load_session_replay(thread_id, user_id),
    }


@router.delete("/sessions/{thread_id}", summary="删除指定历史 session")
async def delete_user_session(thread_id: str, user_id: str = Query(..., description="用户ID")):
    session = await get_session(thread_id, user_id)
    if session is None:
        raise HTTPException(status_code=404, detail="未找到该用户下的会话。")
    deleted = await delete_session(thread_id, user_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="删除会话失败。")
    return {"deleted": True, "thread_id": thread_id}
