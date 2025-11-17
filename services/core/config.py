"""
项目配置文件 - 支持从环境变量和.env文件加载
"""
from pydantic import BaseModel
from typing import Optional
import os
from pathlib import Path

# 加载.env文件（如果存在）
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        # 延迟导入logger避免循环依赖
        try:
            from services.core.logger import logger
            logger.info(f"已加载环境变量文件: {env_path}")
        except:
            print(f"已加载环境变量文件: {env_path}")
    else:
        load_dotenv()  # 尝试加载项目根目录的.env
except ImportError:
    # 延迟导入logger避免循环依赖
    try:
        from services.core.logger import logger
        logger.warning("python-dotenv未安装，无法从.env文件加载配置")
    except:
        print("警告: python-dotenv未安装，无法从.env文件加载配置")


def get_env(key: str, default: str = None) -> str:
    """从环境变量获取值，如果不存在则返回默认值"""
    return os.getenv(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """从环境变量获取布尔值"""
    value = os.getenv(key, str(default)).lower()
    return value in ("true", "1", "yes", "on")


def get_env_int(key: str, default: int = 0) -> int:
    """从环境变量获取整数值"""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


class Settings(BaseModel):
    """应用配置"""
    
    # Milvus 配置
    MILVUS_HOST: str = get_env("MILVUS_HOST", "localhost")
    MILVUS_PORT: int = get_env_int("MILVUS_PORT", 19530)
    MILVUS_COLLECTION_NAME: str = get_env("MILVUS_COLLECTION_NAME", "knowledge_base")
    
    # Embedding 模型配置
    EMBEDDING_MODEL: str = get_env("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION: int = get_env_int("EMBEDDING_DIMENSION", 384)
    
    # 多语言Embedding模型配置（支持粤语、普通话、英语）
    USE_MULTILINGUAL_EMBEDDING: bool = get_env("USE_MULTILINGUAL_EMBEDDING", "true").lower() == "true"
    MULTILINGUAL_EMBEDDING_MODEL: str = get_env(
        "MULTILINGUAL_EMBEDDING_MODEL", 
        "paraphrase-multilingual-MiniLM-L12-v2"  # 支持100+语言，包括粤语、普通话、英语
    )
    MULTILINGUAL_EMBEDDING_DIMENSION: int = get_env_int("MULTILINGUAL_EMBEDDING_DIMENSION", 384)
    
    # LLM API 配置 - HKGAI
    HKGAI_BASE_URL: str = get_env("HKGAI_BASE_URL", "https://oneapi.hkgai.net/v1")
    HKGAI_API_KEY: str = get_env("HKGAI_API_KEY", "")  # 请在.env文件中设置
    HKGAI_MODEL_ID: str = get_env("HKGAI_MODEL_ID", "HKGAI-V1")
    
    # Gemini API 配置
    GEMINI_API_KEY: str = get_env("GEMINI_API_KEY", "")  # 请在.env文件中设置
    GEMINI_DEFAULT_MODEL: str = get_env("GEMINI_DEFAULT_MODEL", "gemini-2.0-flash")
    GEMINI_ENABLED: bool = get_env_bool("GEMINI_ENABLED", True)
    GEMINI_PROJECT_NUMBER: str = get_env("GEMINI_PROJECT_NUMBER", "your-project-number-here")
    
    # RAG 配置
    TOP_K: int = get_env_int("TOP_K", 5)
    CHUNK_SIZE: int = get_env_int("CHUNK_SIZE", 500)
    CHUNK_OVERLAP: int = get_env_int("CHUNK_OVERLAP", 50)
    USE_RERANKER: bool = get_env_bool("USE_RERANKER", True)  # 是否使用Reranker
    
    # 文件上传存储配置
    UPLOAD_STORAGE_DIR: str = get_env("UPLOAD_STORAGE_DIR", "uploaded_files")
    MAX_UPLOAD_SIZE: int = get_env_int("MAX_UPLOAD_SIZE", 50 * 1024 * 1024)
    ALLOWED_EXTENSIONS: list = [
        ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".py", ".txt", ".md", ".json", ".csv"
    ]
    
    # 存储后端配置
    STORAGE_BACKEND: str = get_env("STORAGE_BACKEND", "milvus")
    DATABASE_URL: str = get_env("DATABASE_URL", "sqlite:///./file_storage.db")
    
    # 日志配置
    LOG_LEVEL: str = get_env("LOG_LEVEL", "INFO")
    
    # 金融和交通工具API配置（可选）
    OPENROUTESERVICE_API_KEY: Optional[str] = get_env("OPENROUTESERVICE_API_KEY", None)
    
    # 网页搜索API配置
    GOOGLE_SEARCH_API_KEY: Optional[str] = get_env("GOOGLE_SEARCH_API_KEY", None)  # 请在.env文件中设置
    GOOGLE_CSE_ID: Optional[str] = get_env("GOOGLE_CSE_ID", None)  # Custom Search Engine ID
    
    # 性能优化配置
    USE_CACHE: bool = get_env("USE_CACHE", "true").lower() == "true"  # 是否启用查询缓存
    CACHE_MAX_SIZE: int = int(get_env("CACHE_MAX_SIZE", "200"))  # 缓存最大条目数
    CACHE_TTL: int = int(get_env("CACHE_TTL", "3600"))  # 缓存过期时间（秒），默认1小时
    
    # 语音识别和合成配置（Jarvis语音助手）
    ENABLE_SPEECH: bool = get_env("ENABLE_SPEECH", "true").lower() == "true"  # 是否启用语音功能
    WHISPER_MODEL_SIZE: str = get_env("WHISPER_MODEL_SIZE", "medium")  # Whisper模型大小 (tiny/base/small/medium/large)，默认medium提高准确度
    WAKE_WORD: str = get_env("WAKE_WORD", "jarvis")  # 唤醒词（默认：jarvis）
    USE_EDGE_TTS: bool = get_env("USE_EDGE_TTS", "true").lower() == "true"  # 是否使用edge-tts（多语言支持）
    TTS_LANGUAGE: str = get_env("TTS_LANGUAGE", "zh-CN")  # TTS默认语言（zh-CN/yue-HK/en-US）
    
    # 粤语Speech API配置
    CANTONESE_SPEECH_API_KEY: str = get_env("CANTONESE_SPEECH_API_KEY", "TzmW5eWvGWphlubmavEIRtG5U6OwS9wF02AwtEHWx0stLvtqZWpz5LK2q7lRQhDY")
    CANTONESE_SPEECH_API_URL: str = get_env("CANTONESE_SPEECH_API_URL", "https://api.speech.hkust.edu.hk/v1/recognize")  # 默认URL，可根据实际API调整
    USE_CANTONESE_API: bool = get_env("USE_CANTONESE_API", "true").lower() == "true"  # 是否启用粤语专用API
    
    # 流式处理配置
    ENABLE_STREAMING_STT: bool = get_env("ENABLE_STREAMING_STT", "true").lower() == "true"  # 是否启用流式STT
    ENABLE_STREAMING_TTS: bool = get_env("ENABLE_STREAMING_TTS", "true").lower() == "true"  # 是否启用流式TTS
    STREAMING_STT_CHUNK_SIZE: int = get_env_int("STREAMING_STT_CHUNK_SIZE", 16000)  # 流式STT块大小（采样数）
    
    # Mac MLX优化配置
    USE_MLX: bool = get_env("USE_MLX", "false").lower() == "true"  # 是否使用MLX（Mac优化）
    MLX_STT_MODEL: str = get_env("MLX_STT_MODEL", "tiny")  # MLX STT模型大小
    MLX_LM_MODEL: str = get_env("MLX_LM_MODEL", "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit")  # MLX LM模型
    TTS_TYPE: str = get_env("TTS_TYPE", "parler")  # TTS类型（parler/melo/edge）
    
    class Config:
        case_sensitive = True


settings = Settings()

