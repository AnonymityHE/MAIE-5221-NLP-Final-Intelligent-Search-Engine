"""
FastAPI数据模型定义
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """查询请求模型（支持多模态）"""
    query: str = Field(..., description="用户查询问题")
    top_k: Optional[int] = Field(None, description="返回最相关的k个文档")
    use_agent: bool = Field(False, description="是否使用Agent模式")
    provider: str = Field("hkgai", description="LLM提供商 (hkgai/gemini)")
    model: Optional[str] = Field(None, description="指定模型名称")
    file_ids: Optional[List[str]] = None  # 关联的上传文件ID列表，用于多模态查询
    
    # 🖼️ 多模态支持
    images: Optional[List[str]] = Field(None, description="Base64编码的图片列表")
    image_urls: Optional[List[str]] = Field(None, description="图片URL列表")
    session_id: Optional[str] = Field(None, description="会话ID，用于维护多轮对话和图片历史")


class DocumentResult(BaseModel):
    """文档检索结果模型"""
    text: str
    source_file: str
    score: Optional[float] = None


class QueryResponse(BaseModel):
    """查询响应模型"""
    answer: str
    context: List[str] = []
    documents: Optional[List[DocumentResult]] = None
    query: str
    tools_used: Optional[List[str]] = None
    answer_source: str = "rag"  # rag/agent/direct_llm
    model_used: Optional[str] = None
    tokens_used: Optional[Dict[str, Any]] = None
    quota_remaining: Optional[int] = None
    should_speak: bool = False  # 是否需要语音播报
    audio_url: Optional[str] = None  # TTS音频URL（如果生成了）


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


class VoiceQueryRequest(BaseModel):
    """语音查询请求模型"""
    language: Optional[str] = None  # 指定语言（zh/en/yue），None则自动检测
    use_wake_word: bool = True  # 是否使用唤醒词检测
    use_agent: bool = True  # 是否使用Agent模式
    model: Optional[str] = None  # LLM模型选择


class VoiceQueryResponse(BaseModel):
    """语音查询响应模型"""
    transcribed_text: str  # 转录的文本
    detected_language: Optional[str] = None  # 检测到的语言
    wake_word_detected: bool = False  # 是否检测到唤醒词
    query_text: str  # 提取的查询文本（去除唤醒词后）
    answer: str  # 生成的答案
    answer_audio_url: Optional[str] = None  # 答案的音频URL（如果生成了）
    tools_used: List[str] = []
    model_used: Optional[str] = None
    tokens_used: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None  # 转录置信度


class SpeechRequest(BaseModel):
    """语音请求模型"""
    audio_data: Optional[str] = None  # Base64编码的音频数据
    language: Optional[str] = Field(None, description="目标语言代码（zh/yue/en，可选自动检测）")
    use_wake_word: bool = Field(False, description="是否启用唤醒词检测")


class SpeechResponse(BaseModel):
    """语音响应模型"""
    text: str  # 识别出的文本
    language: Optional[str] = None  # 检测到的语言
    wake_word_detected: bool = False  # 是否检测到唤醒词
    audio_response: Optional[str] = None  # Base64编码的语音响应（可选）


class VoiceQueryRequest(BaseModel):
    """语音查询请求模型（结合语音识别和RAG查询）"""
    audio_data: str  # Base64编码的音频数据
    language: Optional[str] = None  # 目标语言（可选）
    use_agent: bool = Field(False, description="是否使用Agent模式")
    return_audio: bool = Field(True, description="是否返回语音响应")
    provider: str = Field("hkgai", description="LLM提供商")
    model: Optional[str] = None


class VoiceQueryResponse(BaseModel):
    """语音查询响应模型"""
    query_text: str  # 识别出的查询文本
    answer: str  # RAG/Agent生成的答案
    audio_response: Optional[str] = None  # Base64编码的语音答案
    language: Optional[str] = None  # 检测到的语言
    wake_word_detected: bool = False
    tools_used: Optional[List[str]] = None
    model_used: Optional[str] = None


# ========== 🖼️ 多模态相关模型 ==========

class ImageInput(BaseModel):
    """图片输入模型"""
    image_data: str = Field(..., description="Base64编码的图片数据")
    image_url: Optional[str] = Field(None, description="图片URL（与image_data二选一）")
    mime_type: str = Field("image/jpeg", description="图片MIME类型")
    description: Optional[str] = Field(None, description="图片描述（可选）")


class OCRResult(BaseModel):
    """OCR识别结果"""
    text: str = Field(..., description="识别出的文本")
    confidence: float = Field(..., description="识别置信度")
    language: Optional[str] = Field(None, description="识别出的语言")
    bounding_boxes: Optional[List[Dict[str, Any]]] = Field(None, description="文本边界框")


class MultimodalQueryRequest(BaseModel):
    """多模态查询请求"""
    query: str = Field(..., description="用户查询问题")
    images: List[ImageInput] = Field(..., description="图片列表")
    session_id: Optional[str] = Field(None, description="会话ID")
    use_ocr: bool = Field(True, description="是否对图片进行OCR")
    model: str = Field("gemini-2.0-flash-exp", description="使用的模型")
    top_k: Optional[int] = Field(5, description="返回最相关的k个文档")


class MultimodalQueryResponse(BaseModel):
    """多模态查询响应"""
    answer: str = Field(..., description="生成的答案")
    query: str = Field(..., description="原始查询")
    session_id: Optional[str] = Field(None, description="会话ID")
    model_used: str = Field(..., description="使用的模型")
    images_processed: int = Field(..., description="处理的图片数量")
    ocr_results: Optional[List[OCRResult]] = Field(None, description="OCR识别结果")
    tokens_used: Optional[Dict[str, Any]] = None
    context: Optional[List[str]] = Field(None, description="检索到的上下文")


class ImageHistoryItem(BaseModel):
    """图片历史记录项"""
    image_id: str = Field(..., description="图片唯一ID")
    session_id: str = Field(..., description="会话ID")
    image_data: Optional[str] = Field(None, description="Base64编码的图片数据")
    image_url: Optional[str] = Field(None, description="图片URL")
    mime_type: str = Field(..., description="图片MIME类型")
    description: Optional[str] = Field(None, description="图片描述")
    ocr_text: Optional[str] = Field(None, description="OCR识别的文本")
    created_at: str = Field(..., description="创建时间")
    query_count: int = Field(0, description="使用该图片的查询次数")
