"""
项目配置文件
"""
from pydantic import BaseModel
from typing import Optional


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
    HKGAI_API_KEY: str = "sk-iqA1pjC48rpFXdkU7cCaE3BfBc9145B4BfCbEe0912126646"
    HKGAI_MODEL_ID: str = "HKGAI-V1"
    
    # Gemini API 配置
    GEMINI_API_KEY: str = "AIzaSyBGHRyctkSmbEnc2-2eHcEePw-mAKCpz04"  # 注意：以AIza开头
    GEMINI_DEFAULT_MODEL: str = "gemini-2.0-flash"  # 默认使用2.0 Flash（标准化名称）
    GEMINI_ENABLED: bool = True  # 是否启用Gemini API
    GEMINI_PROJECT_NUMBER: str = "359632533737"  # 项目编号
    
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
        """从环境变量加载配置（可选）"""
        import os
        return cls(
            MILVUS_HOST=os.getenv("MILVUS_HOST", "localhost"),
            MILVUS_PORT=int(os.getenv("MILVUS_PORT", "19530")),
            MILVUS_COLLECTION_NAME=os.getenv("MILVUS_COLLECTION_NAME", "knowledge_base"),
            HKGAI_API_KEY=os.getenv("HKGAI_API_KEY", "sk-iqA1pjC48rpFXdkU7cCaE3BfBc9145B4BfCbEe0912126646"),
        )


settings = Settings()

