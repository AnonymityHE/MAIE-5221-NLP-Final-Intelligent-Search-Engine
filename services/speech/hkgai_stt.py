"""
HKGAI语音识别客户端 - 粤语优化的STT服务
支持更准确的粤语语音识别
"""
import requests
import base64
import uuid
from typing import Dict, Optional
from services.core.logger import logger
from services.core.config import settings


class HKGAISpeechClient:
    """HKGAI语音识别客户端（专门优化粤语识别）"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化HKGAI语音客户端
        
        Args:
            api_key: API密钥，如果不提供则从配置读取
        """
        self.api_key = api_key or settings.CANTONESE_SPEECH_API_KEY
        self.base_url = "https://openspeech.hkgai.net"
        
        if not self.api_key:
            logger.warning("⚠️  HKGAI Speech API Key未配置，粤语识别将不可用")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("✅ HKGAI语音识别已启用（粤语优化）")
    
    def recognize(self, audio_bytes: bytes, timeout: int = 30) -> Dict:
        """
        语音识别（快速模式，适合实时输入）
        
        Args:
            audio_bytes: 音频字节数据（WAV/MP3等格式）
            timeout: 请求超时时间（秒）
            
        Returns:
            {
                "text": "识别文本",
                "success": True,
                "confidence": 0.95,
                "language": "zh",
                "provider": "hkgai"
            }
        """
        if not self.enabled:
            return {
                "text": "",
                "success": False,
                "error": "HKGAI API未配置",
                "provider": "hkgai"
            }
        
        endpoint = f"{self.base_url}/api/v1/speech_recognize"
        
        # 准备请求头
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        
        # 转换音频为base64
        try:
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"❌ 音频编码失败: {e}")
            return {
                "text": "",
                "success": False,
                "error": f"音频编码失败: {e}",
                "provider": "hkgai"
            }
        
        # 准备请求体
        payload = {
            "request_id": str(uuid.uuid4()),
            "resource": {
                "type": 2,  # BYTES类型
                "data": audio_b64
            }
        }
        
        logger.info("🎤 调用HKGAI语音识别API...")
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            # 检查HTTP状态码
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                logger.error(f"❌ HKGAI API请求失败: {error_msg}")
                return {
                    "text": "",
                    "success": False,
                    "error": error_msg,
                    "provider": "hkgai"
                }
            
            # 解析响应
            data = response.json()
            
            if data.get("code") == 200:
                result_text = data.get("data", {}).get("result", "").strip()
                
                if not result_text:
                    logger.warning("⚠️  HKGAI返回空文本")
                    return {
                        "text": "",
                        "success": False,
                        "error": "识别结果为空",
                        "provider": "hkgai"
                    }
                
                logger.info(f"✅ HKGAI识别成功: '{result_text[:50]}...'")
                
                return {
                    "text": result_text,
                    "success": True,
                    "confidence": 0.95,  # HKGAI不返回置信度，给个默认高值
                    "language": "zh",  # 假设是中文（包括粤语）
                    "provider": "hkgai",
                    "status_desc": data.get("data", {}).get("status_desc", ""),
                    "request_id": data.get("data", {}).get("request_id", "")
                }
            else:
                error_msg = data.get("msg", "Unknown error")
                logger.error(f"❌ HKGAI API返回错误: {error_msg}")
                return {
                    "text": "",
                    "success": False,
                    "error": error_msg,
                    "provider": "hkgai"
                }
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ HKGAI API请求超时（{timeout}秒）")
            return {
                "text": "",
                "success": False,
                "error": f"请求超时（{timeout}秒）",
                "provider": "hkgai"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ HKGAI API请求异常: {e}")
            return {
                "text": "",
                "success": False,
                "error": str(e),
                "provider": "hkgai"
            }
        except Exception as e:
            logger.error(f"❌ HKGAI语音识别异常: {e}")
            return {
                "text": "",
                "success": False,
                "error": str(e),
                "provider": "hkgai"
            }
    
    def recognize_with_speakers(self, audio_bytes: bytes, timeout: int = 60) -> Dict:
        """
        会议转录（带说话人识别）
        适合多人对话、长音频场景
        
        Args:
            audio_bytes: 音频字节数据
            timeout: 请求超时时间（秒，会议转录可能较慢）
            
        Returns:
            {
                "messages": [
                    {
                        "time_range": {"start": 0, "end": 1000},
                        "speaker": {"name": "Speaker-1"},
                        "content": "说话内容",
                        "language": "zh"
                    }
                ],
                "success": True,
                "provider": "hkgai"
            }
        """
        if not self.enabled:
            return {
                "messages": [],
                "success": False,
                "error": "HKGAI API未配置",
                "provider": "hkgai"
            }
        
        endpoint = f"{self.base_url}/api/v1/transcription"
        
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"❌ 音频编码失败: {e}")
            return {
                "messages": [],
                "success": False,
                "error": f"音频编码失败: {e}",
                "provider": "hkgai"
            }
        
        payload = {
            "request_id": str(uuid.uuid4()),
            "resource": {
                "type": 2,
                "data": audio_b64
            }
        }
        
        logger.info("🎤 调用HKGAI会议转录API（带说话人识别）...")
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                logger.error(f"❌ HKGAI会议转录请求失败: {error_msg}")
                return {
                    "messages": [],
                    "success": False,
                    "error": error_msg,
                    "provider": "hkgai"
                }
            
            data = response.json()
            
            if data.get("code") == 200:
                messages = data.get("data", {}).get("messages", [])
                
                logger.info(f"✅ HKGAI会议转录成功，识别到 {len(messages)} 段对话")
                
                return {
                    "messages": messages,
                    "success": True,
                    "provider": "hkgai",
                    "status_desc": data.get("data", {}).get("status_desc", ""),
                    "request_id": data.get("data", {}).get("request_id", "")
                }
            else:
                error_msg = data.get("msg", "Unknown error")
                logger.error(f"❌ HKGAI会议转录返回错误: {error_msg}")
                return {
                    "messages": [],
                    "success": False,
                    "error": error_msg,
                    "provider": "hkgai"
                }
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ HKGAI会议转录超时（{timeout}秒）")
            return {
                "messages": [],
                "success": False,
                "error": f"请求超时（{timeout}秒）",
                "provider": "hkgai"
            }
        except Exception as e:
            logger.error(f"❌ HKGAI会议转录异常: {e}")
            return {
                "messages": [],
                "success": False,
                "error": str(e),
                "provider": "hkgai"
            }
    
    def is_available(self) -> bool:
        """检查HKGAI语音识别服务是否可用"""
        return self.enabled


# 全局HKGAI客户端实例（单例）
_hkgai_client = None

def get_hkgai_client() -> HKGAISpeechClient:
    """获取HKGAI客户端实例（单例模式）"""
    global _hkgai_client
    if _hkgai_client is None:
        _hkgai_client = HKGAISpeechClient()
    return _hkgai_client

