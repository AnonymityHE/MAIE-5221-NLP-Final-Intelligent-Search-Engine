"""
Services模块 - 提供统一的服务接口

向后兼容：支持旧版导入路径
新版导入：使用模块化的导入方式
"""

# 核心基础设施
from services.core import settings, logger
from services.core.config import Settings

# LLM相关
from services.llm import (
    HKGAIClient,
    llm_client,
    GeminiClient,
    UnifiedLLMClient,
    unified_llm_client,
    UsageMonitor,
    usage_monitor,
)

# 向量数据库
from services.vector import (
    MilvusClient,
    milvus_client,
    Retriever,
    retriever,
    Reranker,
    reranker,
)

# 存储管理
from services.storage import (
    FileStorageManager,
    file_storage,
    FileProcessor,
    file_processor,
    FileIndexer,
    file_indexer,
    StorageBackend,
    MilvusStorageBackend,
    DatabaseStorageBackend,
    get_storage_backend,
)

# Agent
from services.agent import (
    RAGAgent,
    agent,
)

# 向后兼容：提供旧版导入路径
# 这些导入允许旧代码继续工作
from services.core.config import settings as _settings
from services.core.logger import logger as _logger
from services.llm.unified_client import unified_llm_client as _unified_llm_client
from services.vector.retriever import retriever as _retriever
from services.agent.agent import agent as _agent
from services.storage.file_storage import file_storage as _file_storage
from services.storage.file_processor import file_processor as _file_processor
from services.storage.file_indexer import file_indexer as _file_indexer
from services.llm.usage_monitor import usage_monitor as _usage_monitor

# 为了向后兼容，提供全局变量
import sys
_current_module = sys.modules[__name__]
_current_module.settings = _settings
_current_module.logger = _logger
_current_module.unified_llm_client = _unified_llm_client
_current_module.retriever = _retriever
_current_module.agent = _agent
_current_module.file_storage = _file_storage
_current_module.file_processor = _file_processor
_current_module.file_indexer = _file_indexer
_current_module.usage_monitor = _usage_monitor
# 为了向后兼容 llm_client
from services.llm.hkgai_client import llm_client as _llm_client
_current_module.llm_client = _llm_client
# 为了向后兼容 milvus_client
from services.vector.milvus_client import milvus_client as _milvus_client
_current_module.milvus_client = _milvus_client

__all__ = [
    # 核心
    "settings",
    "logger",
    "Settings",
    # LLM
    "HKGAIClient",
    "llm_client",
    "GeminiClient",
    "UnifiedLLMClient",
    "unified_llm_client",
    "UsageMonitor",
    "usage_monitor",
    # 向量数据库
    "MilvusClient",
    "milvus_client",
    "Retriever",
    "retriever",
    "Reranker",
    "reranker",
    # 存储
    "FileStorageManager",
    "file_storage",
    "FileProcessor",
    "file_processor",
    "FileIndexer",
    "file_indexer",
    "StorageBackend",
    "MilvusStorageBackend",
    "DatabaseStorageBackend",
    "get_storage_backend",
    # Agent
    "RAGAgent",
    "agent",
]

