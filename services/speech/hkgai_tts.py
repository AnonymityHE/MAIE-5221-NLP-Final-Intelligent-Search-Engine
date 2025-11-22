"""
HKGAI语音合成客户端 - 粤语TTS服务
支持粤语、普通话的高质量语音合成
"""
import requests
import tempfile
import os
from typing import Optional
from services.core.logger import logger
from services.core.config import settings


class HKGAITTSClient:
    """HKGAI文字转语音客户端（支持粤语）"""
    
    # JWT Token（从文档示例中获取）
    # 注意：这个token有过期时间，实际生产环境需要实现token刷新机制
    JWT_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRfaWQiOiJ0MSIsInJvbGUiOiJ1c2VyIiwicGF0aHMiOlsiL3NlcnZlcl9wcm94eS9hcGkvZ2VuIiwiL3NlcnZlcl9wcm94eS9hcGkvdHRzIl0sImF0dHJzIjp7InR0c19hbGwiOmZhbHNlLCJ0dHNfdm9pY2VzIjpbInpoX2ZlbWFsZV8xIiwiZW5fbWFsZV8yIl19LCJzdWIiOiJ1c2VyLTEiLCJleHAiOjEwNDAzMjY1NDYxLCJpYXQiOjE3NjMzNTE4NjF9.gQ9aBrApIUZljjqp-vRJnpCkFAoykgNaz-f_QHhcDOEotCilkQn1aahvSCixCn3ISvj6D2q7sbx0lj4JppApHCm7d8iEPAEkd4_wZENLTvYSjTr-wCmdu5RcH_KuxyPG_vWzkN6OT8gkbQLNbdV8Oa2tQqE5gWfVTzgv5rOW6bCqm2mjYVIkcm2-eKdlMz5-EcZPRflL_FqghseiC9S7jn_gn6k_tvQpVJxSq6A5OftZ-BVszdR1Rf8bIyZd082AxaCu1LyQG9TOcwcjbwQHqe7A--OASa54DmUZiG-AsxaGCIO4Jgcf5Ek5Qvh6EuS2XFW1B5LXS9gcTKJ7CW5fdg"
    
    def __init__(self, jwt_token: Optional[str] = None):
        """
        初始化HKGAI TTS客户端
        
        Args:
            jwt_token: JWT认证token，如果不提供则使用默认token
        """
        self.jwt_token = jwt_token or self.JWT_TOKEN
        self.base_url = "https://openspeech.hkgai.net/server_proxy/api/tts"
        
        if not self.jwt_token:
            logger.warning("⚠️  HKGAI TTS JWT Token未配置")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("✅ HKGAI语音合成已启用（支持粤语、普通话）")
    
    def synthesize(
        self, 
        text: str, 
        language: str = "cantonese",
        voice: str = "female",
        output_file: Optional[str] = None
    ) -> Optional[str]:
        """
        文字转语音
        
        Args:
            text: 要合成的文本
            language: 语言
                - "cantonese": 粤语（推荐）
                - "mandarin": 普通话
            voice: 音色
                - "female": 女声（默认）
                - "male": 男声
            output_file: 输出文件路径（如果不提供则自动生成临时文件）
            
        Returns:
            生成的音频文件路径，失败返回None
        """
        if not self.enabled:
            logger.error("❌ HKGAI TTS未配置")
            return None
        
        if not text or not text.strip():
            logger.warning("⚠️  TTS输入文本为空")
            return None
        
        # 准备请求参数
        params = {
            "text": text,
            "language": language,
            "voice": voice,
            "type": "file"  # 输出文件（不是流）
        }
        
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.jwt_token}"
        }
        
        logger.info(f"🎤 调用HKGAI TTS API: text='{text[:30]}...', language={language}, voice={voice}")
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=30
            )
            
            # 检查HTTP状态
            if response.status_code != 200:
                logger.error(f"❌ HKGAI TTS请求失败: HTTP {response.status_code}")
                logger.error(f"   响应内容: {response.text[:200]}")
                return None
            
            # 检查是否返回音频数据
            content_type = response.headers.get('Content-Type', '')
            if 'audio' not in content_type and 'octet-stream' not in content_type:
                # 可能是错误信息
                logger.error(f"❌ HKGAI TTS返回非音频数据: {content_type}")
                logger.error(f"   响应内容: {response.text[:200]}")
                return None
            
            # 保存音频文件
            if output_file is None:
                # 创建临时文件
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    output_file = tmp.name
            
            # 写入音频数据
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            logger.info(f"✅ HKGAI TTS合成成功: {output_file} ({file_size} bytes)")
            
            return output_file
            
        except requests.exceptions.Timeout:
            logger.error("❌ HKGAI TTS请求超时")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ HKGAI TTS请求异常: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ HKGAI TTS合成异常: {e}")
            return None
    
    def synthesize_cantonese(self, text: str, voice: str = "female", output_file: Optional[str] = None) -> Optional[str]:
        """
        粤语语音合成（快捷方法）
        
        Args:
            text: 粤语文本
            voice: 音色（female/male）
            output_file: 输出文件路径
            
        Returns:
            音频文件路径
        """
        return self.synthesize(text, language="cantonese", voice=voice, output_file=output_file)
    
    def synthesize_mandarin(self, text: str, voice: str = "female", output_file: Optional[str] = None) -> Optional[str]:
        """
        普通话语音合成（快捷方法）
        
        Args:
            text: 普通话文本
            voice: 音色（female/male）
            output_file: 输出文件路径
            
        Returns:
            音频文件路径
        """
        return self.synthesize(text, language="mandarin", voice=voice, output_file=output_file)
    
    def is_available(self) -> bool:
        """检查HKGAI TTS服务是否可用"""
        return self.enabled


# 全局HKGAI TTS客户端实例（单例）
_hkgai_tts_client = None

def get_hkgai_tts_client() -> HKGAITTSClient:
    """获取HKGAI TTS客户端实例（单例模式）"""
    global _hkgai_tts_client
    if _hkgai_tts_client is None:
        _hkgai_tts_client = HKGAITTSClient()
    return _hkgai_tts_client

