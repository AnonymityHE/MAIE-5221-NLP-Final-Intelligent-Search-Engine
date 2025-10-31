"""
项目配置文件示例

使用方法：
1. 复制此文件为 config.py：cp services/config.example.py services/config.py
2. 在 config.py 中填入你的API密钥
3. 或者使用环境变量（推荐）：创建 .env 文件，然后从环境变量读取
"""
from pydantic import BaseModel
from typing import Optional
import os


class Settings(BaseModel):
    """应用配置"""
    
    # Milvus 配置
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION_NAME: str = "knowledge_base"
    
    # Embedding 模型配置
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # LLM API 配置 - HKGAI (原有)
    HKGAI_BASE_URL: str = "https://oneapi.hkgai.net/v1"
    HKGAI_API_KEY: str = os.getenv("HKGAI_API_KEY", "your-hkgai-api-key-here")
    HKGAI_MODEL_ID: str = "HKGAI-V1"
    
    # Gemini API 配置
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")  # 注意：以AIza开头
    GEMINI_DEFAULT_MODEL: str = "gemini-2.0-flash"  # 默认使用2.0 Flash（标准化名称）
    GEMINI_ENABLED: bool = True  # 是否启用Gemini API
    GEMINI_PROJECT_NUMBER: str = os.getenv("GEMINI_PROJECT_NUMBER", "your-project-number-here")  # 项目编号
    
    # RAG 配置
    TOP_K: int = 5  # 检索返回的文档数量
    CHUNK_SIZE: int = 500  # 文本切块大小
    CHUNK_OVERLAP: int = 50  # 文本切块重叠
    
    # 文件上传存储配置
    UPLOAD_STORAGE_DIR: str = "uploaded_files"  # 上传文件存储目录（相对于项目根目录）
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 最大上传文件大小（50MB）
    ALLOWED_EXTENSIONS: list = [".pdf", ".png", ".jpg", ".jpeg", ".gif", ".py", ".txt", ".md", ".json", ".csv"]
    
    # 存储后端配置
    STORAGE_BACKEND: str = "milvus"  # 存储后端类型: "milvus" 或 "database"
    DATABASE_URL: str = "sqlite:///./file_storage.db"  # 数据库URL（仅用于database后端，支持SQLite和PostgreSQL）
    
    class Config:
        case_sensitive = True
    
    @classmethod
    def from_env(cls):
        """从环境变量加载配置（推荐用于生产环境）"""
        return cls(
            MILVUS_HOST=os.getenv("MILVUS_HOST", "localhost"),
            MILVUS_PORT=int(os.getenv("MILVUS_PORT", "19530")),
            MILVUS_COLLECTION_NAME=os.getenv("MILVUS_COLLECTION_NAME", "knowledge_base"),
            EMBEDDING_MODEL=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            EMBEDDING_DIMENSION=int(os.getenv("EMBEDDING_DIMENSION", "384")),
            HKGAI_BASE_URL=os.getenv("HKGAI_BASE_URL", "https://oneapi.hkgai.net/v1"),
            HKGAI_API_KEY=os.getenv("HKGAI_API_KEY", "your-hkgai-api-key-here"),
            HKGAI_MODEL_ID=os.getenv("HKGAI_MODEL_ID", "HKGAI-V1"),
            GEMINI_API_KEY=os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here"),
            GEMINI_DEFAULT_MODEL=os.getenv("GEMINI_DEFAULT_MODEL", "gemini-2.0-flash"),
            GEMINI_ENABLED=os.getenv("GEMINI_ENABLED", "True").lower() == "true",
            GEMINI_PROJECT_NUMBER=os.getenv("GEMINI_PROJECT_NUMBER", "your-project-number-here"),
            TOP_K=int(os.getenv("TOP_K", "5")),
            CHUNK_SIZE=int(os.getenv("CHUNK_SIZE", "500")),
            CHUNK_OVERLAP=int(os.getenv("CHUNK_OVERLAP", "50")),
            UPLOAD_STORAGE_DIR=os.getenv("UPLOAD_STORAGE_DIR", "uploaded_files"),
            MAX_UPLOAD_SIZE=int(os.getenv("MAX_UPLOAD_SIZE", str(50 * 1024 * 1024))),
            STORAGE_BACKEND=os.getenv("STORAGE_BACKEND", "milvus"),
            DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///./file_storage.db"),
        )


# 使用环境变量优先，如果没有则使用默认值
# 生产环境建议使用 Settings.from_env()
settings = Settings.from_env() if os.getenv("USE_ENV_CONFIG", "False").lower() == "true" else Settings()

