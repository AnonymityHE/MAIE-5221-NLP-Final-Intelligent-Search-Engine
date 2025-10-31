"""
FastAPI应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.api import router
from services.milvus_client import milvus_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("正在连接Milvus...")
    if milvus_client.connect():
        print("Milvus连接成功")
    else:
        print("警告: Milvus连接失败，请确保Milvus服务正在运行")
    
    yield
    
    # 关闭时
    print("正在断开Milvus连接...")
    milvus_client.disconnect()


app = FastAPI(
    title="RAG问答系统API",
    description="基于Milvus和LLM的RAG问答系统",
    version="1.0.0",
    lifespan=lifespan
)

# 注册路由
app.include_router(router, prefix="/api", tags=["RAG"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "RAG问答系统API",
        "docs": "/docs",
        "health": "/api/health"
    }

