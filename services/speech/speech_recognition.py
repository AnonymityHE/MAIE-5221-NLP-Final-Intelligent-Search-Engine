"""
语音识别模块 - 使用Whisper进行多语言语音转文本
支持粤语、普通话、英语
"""
import io
import tempfile
from typing import Optional, Dict
from pathlib import Path
from services.core.logger import logger

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("openai-whisper未安装，语音识别功能将被禁用")


class SpeechRecognizer:
    """语音识别器 - 使用Whisper模型进行语音转文本"""
    
    def __init__(self, model_name: str = "base"):
        """
        初始化语音识别器
        
        Args:
            model_name: Whisper模型名称
                - tiny: 最快，准确性较低
                - base: 平衡速度和准确性（推荐）
                - small: 更好的准确性
                - medium: 高准确性
                - large: 最高准确性但较慢
        """
        self.model = None
        self.model_name = model_name
        
        if not WHISPER_AVAILABLE:
            logger.error("openai-whisper未安装，语音识别功能不可用")
            return
        
        try:
            logger.info(f"正在加载Whisper模型: {model_name}")
            self.model = whisper.load_model(model_name)
            logger.info(f"Whisper模型加载完成: {model_name}")
        except Exception as e:
            logger.error(f"加载Whisper模型失败: {e}")
            self.model = None
    
    def transcribe(
        self, 
        audio_data: bytes, 
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict:
        """
        将音频数据转换为文本
        
        Args:
            audio_data: 音频文件的字节数据（支持WAV、MP3、M4A等格式）
            language: 目标语言代码（可选，自动检测）
                - zh: 中文（普通话）
                - yue: 粤语
                - en: 英语
                - None: 自动检测
            task: 任务类型（transcribe或translate）
            
        Returns:
            包含text、language等信息的字典
        """
        if not self.model:
            return {
                "text": "",
                "error": "Whisper模型未加载，请检查安装"
            }
        
        try:
            # 将字节数据保存到临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            try:
                # 使用Whisper进行识别
                result = self.model.transcribe(
                    tmp_path,
                    language=language,
                    task=task
                )
                
                detected_language = result.get("language", "unknown")
                text = result.get("text", "").strip()
                
                logger.info(f"语音识别完成: 语言={detected_language}, 文本='{text[:50]}...'")
                
                return {
                    "text": text,
                    "language": detected_language,
                    "language_probability": result.get("language_probability", 1.0),
                    "segments": result.get("segments", [])
                }
            finally:
                # 清理临时文件
                Path(tmp_path).unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"语音识别失败: {e}")
            return {
                "text": "",
                "error": str(e)
            }
    
    def transcribe_file(self, file_path: str, language: Optional[str] = None) -> Dict:
        """
        从音频文件转录
        
        Args:
            file_path: 音频文件路径
            language: 目标语言代码（可选）
            
        Returns:
            转录结果字典
        """
        try:
            with open(file_path, "rb") as f:
                audio_data = f.read()
            return self.transcribe(audio_data, language)
        except Exception as e:
            logger.error(f"读取音频文件失败: {e}")
            return {"text": "", "error": str(e)}
    
    def is_available(self) -> bool:
        """检查语音识别器是否可用"""
        return self.model is not None


# 全局语音识别器实例
_speech_recognizer = None


def get_speech_recognizer(model_name: str = "base") -> SpeechRecognizer:
    """获取全局语音识别器实例"""
    global _speech_recognizer
    if _speech_recognizer is None:
        _speech_recognizer = SpeechRecognizer(model_name)
    return _speech_recognizer

