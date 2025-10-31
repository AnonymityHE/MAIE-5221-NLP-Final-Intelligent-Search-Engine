"""
API请求和响应模型
"""
from pydantic import BaseModel
from typing import List, Optional, Dict


class QueryRequest(BaseModel):
    """查询请求模型"""
    query: str
    top_k: Optional[int] = None
    use_agent: Optional[bool] = False  # 是否使用Agent模式
    model: Optional[str] = None  # LLM模型选择（仅Gemini使用: gemini-2.5-pro, gemini-2.5-flash, gemini-2.0-flash）
    provider: Optional[str] = "hkgai"  # API提供商，默认使用hkgai，可选: gemini（Gemini系列为备选）
    file_ids: Optional[List[str]] = None  # 关联的上传文件ID列表，用于多模态查询


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    file_id: str
    filename: str
    file_type: str
    file_size: int
    uploaded_at: str
    processed: bool
    already_exists: bool
    message: Optional[str] = None


class DocumentResult(BaseModel):
    """单个文档结果模型"""
    text: str
    source_file: str
    score: float


class QueryResponse(BaseModel):
    """查询响应模型"""
    answer: str
    context: List[DocumentResult]
    query: str
    tools_used: Optional[List[str]] = None  # Agent使用的工具列表
    answer_source: Optional[str] = None  # 答案来源："rag", "agent", "direct_llm"
    model_used: Optional[str] = None  # 使用的模型名称
    tokens_used: Optional[Dict[str, int]] = None  # Token使用量 {"input": int, "output": int, "total": int}
    quota_remaining: Optional[int] = None  # 剩余请求配额

