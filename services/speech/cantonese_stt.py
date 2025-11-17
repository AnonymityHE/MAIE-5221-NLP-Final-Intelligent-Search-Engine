"""
粤语专用语音识别API客户端
支持专门针对粤语优化的Speech API
"""
import os
import tempfile
import requests
from typing import Optional, Dict
from services.core.logger import logger
from services.core.config import settings

class CantoneseSTT:
    """粤语专用语音转文本服务"""
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        初始化粤语STT
        
        Args:
            api_key: API密钥（如果不提供，从配置中读取）
            api_url: API URL（如果不提供，从配置中读取）
        """
        self.api_key = api_key or settings.CANTONESE_SPEECH_API_KEY
        self.api_url = api_url or settings.CANTONESE_SPEECH_API_URL
        
        if not self.api_key:
            logger.warning("粤语Speech API密钥未配置")
        else:
            logger.info(f"粤语Speech API已初始化")
    
    def transcribe(
        self, 
        audio_file_path: str,
        language: str = "yue"
    ) -> Dict:
        """
        将音频文件转换为文本
        
        Args:
            audio_file_path: 音频文件路径（支持wav, mp3, m4a等格式）
            language: 语言代码（默认为yue-粤语）
            
        Returns:
            包含text、language等信息的字典
        """
        if not self.api_key:
            return {
                "error": "粤语Speech API密钥未配置",
                "text": "",
                "language": None
            }
        
        if not os.path.exists(audio_file_path):
            return {
                "error": f"音频文件不存在: {audio_file_path}",
                "text": "",
                "language": None
            }
        
        try:
            logger.info(f"开始使用粤语API转录音频: {audio_file_path}")
            
            # 准备请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
            }
            
            # 读取音频文件
            with open(audio_file_path, "rb") as audio_file:
                files = {
                    "audio": audio_file
                }
                
                data = {
                    "language": language,
                    "model": "cantonese-v1"  # 可根据实际API调整
                }
                
                # 发送请求
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=30
                )
            
            # 处理响应
            if response.status_code == 200:
                result = response.json()
                text = result.get("text", "").strip()
                
                logger.info(f"粤语API转录完成: 文本='{text[:50]}...', 文本长度={len(text)}")
                
                return {
                    "text": text,
                    "language": "yue",
                    "confidence": result.get("confidence", 0.95),
                    "provider": "cantonese_api"
                }
            else:
                error_msg = f"粤语API请求失败: HTTP {response.status_code}"
                logger.error(error_msg)
                return {
                    "error": error_msg,
                    "text": "",
                    "language": None
                }
                
        except requests.exceptions.Timeout:
            logger.error("粤语API请求超时")
            return {
                "error": "API请求超时",
                "text": "",
                "language": None
            }
        except Exception as e:
            logger.error(f"粤语API转录失败: {e}")
            return {
                "error": str(e),
                "text": "",
                "language": None
            }
    
    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        audio_format: str = "wav",
        language: str = "yue"
    ) -> Dict:
        """
        将音频字节流转换为文本
        
        Args:
            audio_bytes: 音频文件的字节数据
            audio_format: 音频格式（wav, mp3, m4a, webm等）
            language: 语言代码（默认为yue-粤语）
            
        Returns:
            包含text、language等信息的字典
        """
        if not self.api_key:
            return {
                "error": "粤语Speech API密钥未配置",
                "text": "",
                "language": None
            }
        
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(
                suffix=f".{audio_format}",
                delete=False
            ) as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name
            
            # 转录
            result = self.transcribe(tmp_path, language=language)
            
            # 清理临时文件
            try:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except Exception as e:
                logger.debug(f"清理临时文件失败: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"粤语API音频字节流转录失败: {e}")
            return {
                "error": str(e),
                "text": "",
                "language": None
            }
    
    def is_available(self) -> bool:
        """检查粤语STT是否可用"""
        return bool(self.api_key)


# 全局粤语STT实例
_cantonese_stt: Optional[CantoneseSTT] = None


def get_cantonese_stt() -> Optional[CantoneseSTT]:
    """
    获取粤语STT实例
    
    Returns:
        CantoneseSTT实例或None
    """
    global _cantonese_stt
    
    if _cantonese_stt is None:
        if settings.USE_CANTONESE_API:
            _cantonese_stt = CantoneseSTT()
        else:
            logger.info("粤语API未启用（USE_CANTONESE_API=false）")
            return None
    
    return _cantonese_stt if _cantonese_stt.is_available() else None

