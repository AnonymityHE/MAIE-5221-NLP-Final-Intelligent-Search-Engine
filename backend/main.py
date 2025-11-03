"""
FastAPI应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from backend.api import router
from services.vector import milvus_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    from services.core import logger
    
    # 启动时
    logger.info("正在连接Milvus...")
    if milvus_client.connect():
        logger.info("Milvus连接成功")
    else:
        logger.warning("Milvus连接失败，请确保Milvus服务正在运行")
    
    yield
    
    # 关闭时
    logger.info("正在断开Milvus连接...")
    milvus_client.disconnect()


app = FastAPI(
    title="RAG问答系统API",
    description="基于Milvus和LLM的RAG问答系统",
    version="1.0.0",
    lifespan=lifespan
)

# 注册路由
app.include_router(router, prefix="/api", tags=["RAG"])

# 静态文件服务（用于前端页面）
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/voice")
async def voice_assistant_page():
    """语音助手前端页面"""
    frontend_file = os.path.join(frontend_dir, "voice_assistant.html")
    if os.path.exists(frontend_file):
        return FileResponse(frontend_file)
    return {"message": "前端页面未找到，请确保frontend/voice_assistant.html存在"}


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "RAG问答系统API",
        "docs": "/docs",
        "health": "/api/health",
        "voice_assistant": "/voice"
    }

