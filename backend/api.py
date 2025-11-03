"""
FastAPI路由定义
"""
from typing import Optional, List, Dict
from fastapi import APIRouter, HTTPException, UploadFile, File as FastAPIFile, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from backend.models import (
    QueryRequest, QueryResponse, DocumentResult, FileUploadResponse,
    SpeechRequest, SpeechResponse, VoiceQueryRequest, VoiceQueryResponse
)
from services.vector import retriever
from services.llm import llm_client, unified_llm_client, usage_monitor
from services.agent import agent
from services.storage import file_storage, file_processor, file_indexer
from services.core import settings, logger
from services.core.cache import get_cache_stats, clear_cache
import asyncio
import os
import tempfile

router = APIRouter()


@router.post("/rag_query", response_model=QueryResponse)
async def rag_query(request: QueryRequest):
    """
    RAG查询接口（传统模式）
    
    接收用户问题，从Milvus检索相关文档，使用LLM生成答案。
    如果没有检索到文档（RAG库为空），则直接调用LLM回答。
    
    注意：如果use_agent=True，会自动切换到Agent模式。
    """
    # 如果请求使用Agent，重定向到Agent接口
    if request.use_agent:
        return await agent_query(request)
    try:
        # 1. 从Milvus检索相关文档（包括上传的文件）
        search_results = retriever.search(request.query, request.top_k)
        
        # 1.1 如果指定了file_ids，优先搜索这些上传的文件
        if request.file_ids:
            uploaded_results = file_indexer.search_uploaded_files(
                request.query, 
                request.top_k or settings.TOP_K,
                file_ids=request.file_ids
            )
            # 合并结果，上传的文件优先级更高
            search_results = uploaded_results + search_results
        
        # 2. 判断是否有RAG结果，以及结果是否相关
        has_rag_context = len(search_results) > 0
        is_relevant = False
        
        if has_rag_context:
            # 检查相似度分数：L2距离越小越相似
            # 设置阈值：如果最好的结果分数 > 3.0，认为不相关
            # (可以根据实际情况调整这个阈值)
            RELEVANCE_THRESHOLD = 3.0
            best_score = min(result.get('score', float('inf')) for result in search_results)
            is_relevant = best_score <= RELEVANCE_THRESHOLD
        
        if not has_rag_context or not is_relevant:
            # 情况1: RAG库为空
            # 情况2: 检索到的文档相似度太低（不相关）
            # 直接使用LLM回答，不依赖上下文
            system_prompt = "你是一个专业的AI助手，请直接回答问题。"
            user_prompt = request.query
            use_rag = False
        else:
            # 有相关的RAG结果，使用检索到的上下文
            # 构建上下文
            context_parts = []
            for result in search_results:
                context_parts.append(result['text'])
            context = "\n\n".join(context_parts)
            
            # 构建Prompt
            system_prompt = "你是一个专业的AI助手，请基于提供的上下文信息回答问题。"
            user_prompt = f"基于以下信息：\n\n{context}\n\n请回答这个问题：{request.query}"
            use_rag = True
        
        # 3. 调用LLM生成答案（使用统一客户端，支持模型选择）
        llm_result = unified_llm_client.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=2048,
            temperature=0.7,
            model=request.model,
            provider=request.provider
        )
        
        if "error" in llm_result:
            # 如果是配额不足错误，返回更友好的错误信息
            error_msg = llm_result.get("error", "")
            if "配额已用完" in error_msg or "配额" in error_msg:
                raise HTTPException(
                    status_code=429,
                    detail=error_msg,
                    headers={"X-Quota-Info": str(llm_result.get("quota_info", {}))}
                )
            # 记录详细错误（用于调试）
            logger.error(f"LLM调用错误: {error_msg}")
            raise HTTPException(status_code=500, detail=f"LLM调用失败: {error_msg}")
        
        answer = llm_result.get("content", "无法生成答案")
        # 根据provider确定使用的模型名称
        if request.provider == "gemini":
            model_used = llm_result.get("model", request.model or settings.GEMINI_DEFAULT_MODEL)
        else:
            model_used = settings.HKGAI_MODEL_ID
        
        # 获取token使用量（仅Gemini返回）
        tokens_info = None
        if "input_tokens" in llm_result:
            tokens_info = {
                "input": llm_result.get("input_tokens", 0),
                "output": llm_result.get("output_tokens", 0),
                "total": llm_result.get("total_tokens", 0)
            }
        
        # 获取剩余配额（仅Gemini有配额限制）
        quota_remaining = None
        if request.provider == "gemini":
            quota_info = usage_monitor.check_quota(model_used)
            quota_remaining = quota_info.get("remaining_requests", 0)
        
        # 4. 格式化文档结果（只有使用RAG时才返回context）
        document_results = []
        if use_rag and has_rag_context:
            document_results = [
                DocumentResult(
                    text=result['text'],
                    source_file=result.get('source_file', 'unknown'),
                    score=float(result.get('score', 0.0))
                )
                for result in search_results
            ]
        
        return QueryResponse(
            answer=answer,
            context=document_results,
            query=request.query,
            answer_source="rag" if use_rag else "direct_llm",
            model_used=model_used,
            tokens_used=tokens_info,
            quota_remaining=quota_remaining
        )
    
    except HTTPException:
        # 重新抛出HTTP异常（如配额错误）
        raise
    except Exception as e:
        # 记录详细错误信息（用于调试）
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"RAG查询错误详情:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")


@router.post("/agent_query", response_model=QueryResponse)
async def agent_query(request: QueryRequest):
    """
    Agent智能查询接口
    
    接收用户问题，Agent会根据问题类型自动选择合适的工具（本地知识库、网页搜索、天气查询等）
    支持模型选择和用量监控
    """
    try:
        # 使用Agent处理问题（Agent默认使用HKGAI，如果指定了Gemini模型则使用Gemini）
        agent_result = agent.execute(request.query, model=request.model)
        
        # 获取token使用量和模型信息
        tokens_info = None
        model_used = settings.HKGAI_MODEL_ID  # Agent默认使用HKGAI
        quota_remaining = None
        
        # 如果返回了Gemini的token信息，说明使用了Gemini
        if "tokens" in agent_result and agent_result["tokens"]:
            tokens_info = agent_result["tokens"]
            if "model" in agent_result and agent_result["model"]:
                model_used = agent_result["model"]
                quota_info = usage_monitor.check_quota(model_used)
                quota_remaining = quota_info.get("remaining_requests", 0)
        
        # 格式化响应
        return QueryResponse(
            answer=agent_result["answer"],
            context=[],  # Agent模式下不返回具体文档片段
            query=request.query,
            tools_used=agent_result.get("tools_used", []),
            answer_source="agent",
            model_used=model_used,
            tokens_used=tokens_info,
            quota_remaining=quota_remaining
        )
    
    except HTTPException:
        # 重新抛出HTTP异常（如配额错误）
        raise
    except Exception as e:
        # 记录详细错误信息（用于调试）
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Agent查询错误详情:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")


@router.get("/usage/stats")
async def get_usage_stats(model: Optional[str] = None):
    """
    获取API用量统计
    
    Args:
        model: 模型名称，如果为None则返回所有模型的统计
    """
    stats = usage_monitor.get_daily_stats(model)
    return stats


@router.get("/usage/quota")
async def check_quota(model: str = "gemini-2.0-flash"):
    """
    检查指定模型的配额状态
    
    Args:
        model: 模型名称
    """
    quota = usage_monitor.check_quota(model)
    return quota


@router.get("/models")
async def get_supported_models():
    """获取支持的模型列表"""
    return unified_llm_client.get_supported_models()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = FastAPIFile(...)):
    """
    文件上传接口
    
    支持上传多种格式的文件：
    - PDF文件 (.pdf)
    - 图片文件 (.png, .jpg, .jpeg, .gif) - 支持OCR
    - 代码文件 (.py, .js, .java等)
    - 文本文件 (.txt, .md, .json, .csv等)
    
    上传的文件会自动解析、向量化并索引到Milvus
    """
    try:
        # 读取文件内容
        file_content = await file.read()
        
        # 保存文件
        result = file_storage.save_file(
            file_content=file_content,
            filename=file.filename,
            mime_type=file.content_type
        )
        
        # 异步处理和索引文件（不阻塞响应）
        if not result.get("already_exists") or not result.get("processed"):
            asyncio.create_task(_process_and_index_file(result["file_id"]))
            message = "文件上传成功，正在后台处理和索引..."
        else:
            message = "文件已存在且已处理"
        
        file_info = file_storage.get_file(result["file_id"])
        
        return FileUploadResponse(
            file_id=result["file_id"],
            filename=result["filename"],
            file_type=result["file_type"],
            file_size=result["file_size"],
            uploaded_at=file_info["uploaded_at"] if file_info else "",
            processed=result.get("processed", False),
            already_exists=result.get("already_exists", False),
            message=message
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


async def _process_and_index_file(file_id: str):
    """异步处理和索引文件"""
    try:
        index_result = file_indexer.index_file(file_id)
        logger.info(f"文件 {file_id} 处理完成: {index_result}")
    except Exception as e:
        logger.error(f"文件 {file_id} 处理失败: {e}")


@router.get("/files")
async def list_files(file_type: Optional[str] = None, processed: Optional[bool] = None):
    """
    列出所有上传的文件
    
    Args:
        file_type: 文件类型过滤 (pdf, image, code, text)
        processed: 是否已处理过滤 (true/false)
    """
    try:
        files = file_storage.list_files(file_type=file_type, processed=processed)
        return {"files": files, "total": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")


@router.get("/files/{file_id}")
async def get_file_info(file_id: str):
    """获取文件详细信息"""
    file_info = file_storage.get_file(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="文件不存在")
    return file_info


@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """删除上传的文件"""
    success = file_storage.delete_file(file_id)
    if not success:
        raise HTTPException(status_code=404, detail="文件不存在")
    return {"message": "文件删除成功", "file_id": file_id}


@router.post("/files/{file_id}/reindex")
async def reindex_file(file_id: str):
    """重新处理和索引文件"""
    try:
        result = file_indexer.index_file(file_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新索引失败: {str(e)}")


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "service": "RAG API with Gemini",
        "milvus_host": settings.MILVUS_HOST,
        "milvus_port": settings.MILVUS_PORT,
        "default_model": settings.GEMINI_DEFAULT_MODEL if settings.GEMINI_ENABLED else settings.HKGAI_MODEL_ID
    }


@router.get("/cache/stats")
async def get_cache_statistics():
    """获取缓存统计信息"""
    try:
        stats = get_cache_stats()
        return {
            "cache_enabled": settings.USE_CACHE,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"获取缓存统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取缓存统计失败: {str(e)}")


@router.post("/cache/clear")
async def clear_cache_endpoint(cache_type: str = "all"):
    """
    清空缓存
    
    Args:
        cache_type: 缓存类型 ("query", "embedding", "all")
    """
    try:
        if cache_type not in ("query", "embedding", "all"):
            raise HTTPException(status_code=400, detail="cache_type必须是'query'、'embedding'或'all'")
        
        clear_cache(cache_type)
        return {
            "message": f"缓存已清空: {cache_type}",
            "cache_type": cache_type
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        raise HTTPException(status_code=500, detail=f"清空缓存失败: {str(e)}")


# ========== 语音查询辅助函数 ==========

def _parse_voice_request_params(request: Optional[str]) -> Dict:
    """解析语音查询请求参数"""
    default_params = {
        "language": None,
        "use_wake_word": True,
        "use_agent": True
    }
    
    if not request:
        return default_params
    
    try:
        import json
        params = json.loads(request)
        return {
            "language": params.get("language"),
            "use_wake_word": params.get("use_wake_word", True),
            "use_agent": params.get("use_agent", True)
        }
    except:
        return default_params


async def _process_voice_query_with_agent(query_text: str, model: Optional[str] = None) -> Dict:
    """使用Agent处理查询"""
    agent_result = agent.execute(query_text, model=model)
    return {
        "answer": agent_result.get("answer", "无法生成答案"),
        "tools_used": agent_result.get("tools_used", []),
        "tokens_info": agent_result.get("tokens", None),
        "model_used": settings.HKGAI_MODEL_ID
    }


async def _process_voice_query_with_rag(query_text: str) -> Dict:
    """使用RAG处理查询"""
    search_results = retriever.search(query_text, top_k=settings.TOP_K)
    
    if search_results:
        context = "\n\n".join([r['text'] for r in search_results[:3]])
        llm_result = unified_llm_client.chat(
            system_prompt="基于以下上下文回答问题。",
            user_prompt=f"上下文：\n{context}\n\n问题：{query_text}",
            max_tokens=2048
        )
        answer = llm_result.get("content", "无法生成答案")
        tools_used = ["rag"]
    else:
        llm_result = unified_llm_client.chat(
            system_prompt="你是一个智能助手。",
            user_prompt=query_text,
            max_tokens=2048
        )
        answer = llm_result.get("content", "无法生成答案")
        tools_used = ["direct_llm"]
    
    return {
        "answer": answer,
        "tools_used": tools_used,
        "tokens_info": None,
        "model_used": settings.HKGAI_MODEL_ID
    }


@router.post("/voice/query", response_model=VoiceQueryResponse)
async def voice_query(audio: UploadFile = FastAPIFile(...), request: Optional[str] = None):
    """
    🎤 Jarvis语音查询接口
    
    接收音频文件，转换为文本，检测唤醒词"Jarvis"，然后使用Agent回答
    
    支持的音频格式: wav, mp3, m4a, flac等
    
    使用示例:
    1. 用户说: "Jarvis, 今天天气怎么样？"
    2. 系统检测到"Jarvis"，提取查询"今天天气怎么样？"
    3. Agent处理查询并生成答案
    4. 返回文本答案（可选：生成语音回复）
    """
    if not settings.ENABLE_SPEECH:
        raise HTTPException(status_code=503, detail="语音功能未启用")
    
    try:
        # 检查语音模块是否可用
        try:
            from services.speech.voice_service import get_voice_service
        except ImportError:
            raise HTTPException(
                status_code=503,
                detail="语音模块未安装，请运行: pip install openai-whisper soundfile edge-tts"
            )
        
        voice_service = get_voice_service()
        
        # 1. 读取并解析音频文件
        audio_bytes = await audio.read()
        audio_format = audio.filename.split('.')[-1] if '.' in audio.filename else "wav"
        logger.info(f"收到语音查询: {audio.filename}, 格式: {audio_format}, 大小: {len(audio_bytes)} bytes")
        
        # 2. 解析请求参数
        params = _parse_voice_request_params(request)
        
        # 3. 语音转文本
        transcription_result = voice_service.transcribe_audio(
            audio_bytes=audio_bytes,
            audio_format=audio_format,
            language=params["language"]
        )
        
        if "error" in transcription_result:
            raise HTTPException(
                status_code=500,
                detail=f"语音识别失败: {transcription_result['error']}"
            )
        
        transcribed_text = transcription_result.get("text", "").strip()
        detected_language = transcription_result.get("language", "unknown")
        confidence = transcription_result.get("confidence", 0.0)
        
        if not transcribed_text:
            raise HTTPException(status_code=400, detail="未能识别语音内容，请检查音频质量")
        
        # 4. 检测唤醒词并提取查询
        wake_word_detected, query_text = voice_service.detect_and_extract_query(
            transcribed_text=transcribed_text,
            use_wake_word=params["use_wake_word"]
        )
        
        if not query_text:
            raise HTTPException(status_code=400, detail="查询文本为空")
        
        # 5. 处理查询（Agent或RAG）
        if params["use_agent"]:
            query_result = await _process_voice_query_with_agent(query_text)
        else:
            query_result = await _process_voice_query_with_rag(query_text)
        
        # 6. 生成语音回复（可选）
        answer_audio_url = None
        if settings.ENABLE_SPEECH and settings.USE_EDGE_TTS:
            audio_file = voice_service.generate_audio_response(
                text=query_result["answer"],
                language=detected_language
            )
            if audio_file:
                answer_audio_url = f"/audio/{os.path.basename(audio_file)}"
        
        # 7. 返回结果
        return VoiceQueryResponse(
            transcribed_text=transcribed_text,
            detected_language=detected_language,
            wake_word_detected=wake_word_detected,
            query_text=query_text,
            answer=query_result["answer"],
            answer_audio_url=answer_audio_url,
            tools_used=query_result["tools_used"],
            model_used=query_result["model_used"],
            tokens_used=query_result["tokens_info"],
            confidence=confidence
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"语音查询处理失败: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"处理语音查询时出错: {str(e)}")


@router.websocket("/voice/ws")
async def voice_websocket(websocket: WebSocket):
    """
    🎤 Jarvis实时语音交互WebSocket接口
    
    支持实时语音输入和响应，类似"Hey Siri"的交互体验
    
    使用方式：
    1. 连接WebSocket: ws://localhost:8000/api/voice/ws
    2. 发送音频数据（base64编码）
    3. 接收转录文本和回答
    
    前端页面访问: http://localhost:8000/voice
    """
    import uuid
    
    client_id = str(uuid.uuid4())
    
    try:
        from services.speech.websocket_handler import get_voice_ws_handler
        
        if not settings.ENABLE_SPEECH:
            await websocket.close(code=1008, reason="语音功能未启用")
            return
        
        handler = get_voice_ws_handler()
        await handler.connect(websocket, client_id)
        
        # 发送连接成功消息
        await handler.send_message(client_id, {
            "type": "connected",
            "message": "Jarvis语音助手已连接",
            "client_id": client_id,
            "wake_word": settings.WAKE_WORD
        })
        
        # 接收消息循环
        while True:
            try:
                # 接收JSON消息
                data = await websocket.receive_json()
                
                message_type = data.get("type", "")
                
                if message_type == "audio":
                    # 处理音频数据
                    audio_data = data.get("data", "")
                    is_final = data.get("is_final", False)
                    audio_format = data.get("format", "webm")
                    await handler.handle_audio_chunk(client_id, audio_data, is_final, audio_format)
                
                elif message_type == "ping":
                    # 心跳检测
                    await handler.send_message(client_id, {
                        "type": "pong",
                        "timestamp": data.get("timestamp")
                    })
                
                elif message_type == "disconnect":
                    # 客户端主动断开
                    break
                    
            except WebSocketDisconnect:
                logger.info(f"客户端 {client_id} 断开连接")
                break
            except Exception as e:
                logger.error(f"WebSocket消息处理错误: {e}")
                await handler.send_message(client_id, {
                    "type": "error",
                    "message": str(e)
                })
    
    except Exception as e:
        logger.error(f"WebSocket连接错误: {e}")
    finally:
        handler.disconnect(client_id)

