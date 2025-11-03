"""
文本转语音模块 - 支持多语言语音合成
"""
from typing import Optional
from services.core.logger import logger

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.debug("pyttsx3未安装，离线TTS功能不可用")

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.debug("edge-tts未安装，在线TTS功能不可用")


class TextToSpeech:
    """文本转语音服务（支持多语言）"""
    
    def __init__(self, use_edge_tts: bool = True):
        """
        初始化TTS服务
        
        Args:
            use_edge_tts: 是否使用edge-tts（在线，支持多语言）
                          False则使用pyttsx3（离线，语言支持有限）
        """
        self.use_edge_tts = use_edge_tts and EDGE_TTS_AVAILABLE
        self.engine = None
        
        if self.use_edge_tts:
            logger.info("使用edge-tts（支持多语言）")
        elif PYTTSX3_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                logger.info("使用pyttsx3（离线TTS）")
            except Exception as e:
                logger.warning(f"pyttsx3初始化失败: {e}")
        else:
            logger.warning("TTS服务不可用（需要安装pyttsx3或edge-tts）")
    
    def speak(
        self,
        text: str,
        language: str = "zh",
        output_file: Optional[str] = None,
        voice: Optional[str] = None
    ) -> Optional[str]:
        """
        将文本转换为语音
        
        Args:
            text: 要转换的文本
            language: 语言代码
                - "zh": 中文（普通话）
                - "zh-HK": 粤语
                - "en": 英语
            output_file: 输出音频文件路径（可选，None则播放）
            voice: 指定语音（可选）
            
        Returns:
            音频文件路径（如果指定output_file）或None
        """
        if self.use_edge_tts and EDGE_TTS_AVAILABLE:
            return self._speak_edge_tts(text, language, output_file, voice)
        elif self.engine:
            return self._speak_pyttsx3(text, output_file)
        else:
            logger.warning("TTS服务不可用")
            return None
    
    def _speak_edge_tts(
        self,
        text: str,
        language: str,
        output_file: Optional[str],
        voice: Optional[str]
    ) -> Optional[str]:
        """使用edge-tts转换（支持多语言）"""
        try:
            import asyncio
            import edge_tts
            
            # 选择语音
            if not voice:
                # 根据语言选择默认语音
                voice_map = {
                    "zh": "zh-CN-XiaoxiaoNeural",  # 中文普通话
                    "zh-CN": "zh-CN-XiaoxiaoNeural",
                    "zh-HK": "zh-HK-HiuGaaiNeural",  # 粤语
                    "yue": "zh-HK-HiuGaaiNeural",
                    "en": "en-US-AriaNeural",  # 英语
                    "en-US": "en-US-AriaNeural",
                }
                voice = voice_map.get(language, "zh-CN-XiaoxiaoNeural")
            
            async def _generate():
                communicate = edge_tts.Communicate(text, voice)
                if output_file:
                    await communicate.save(output_file)
                    return output_file
                else:
                    # 直接播放
                    await communicate.save("temp_audio.mp3")
                    # 这里可以添加播放逻辑
                    return "temp_audio.mp3"
            
            result = asyncio.run(_generate())
            logger.info(f"TTS完成: {len(text)}字符 -> {output_file or '播放中'}")
            return result
            
        except Exception as e:
            logger.error(f"edge-tts转换失败: {e}")
            return None
    
    def _speak_pyttsx3(
        self,
        text: str,
        output_file: Optional[str]
    ) -> Optional[str]:
        """使用pyttsx3转换（离线）"""
        try:
            if output_file:
                self.engine.save_to_file(text, output_file)
                self.engine.runAndWait()
                return output_file
            else:
                self.engine.say(text)
                self.engine.runAndWait()
                return None
        except Exception as e:
            logger.error(f"pyttsx3转换失败: {e}")
            return None
    
    def is_available(self) -> bool:
        """检查TTS是否可用"""
        return self.use_edge_tts or self.engine is not None


# 全局TTS实例
_tts = None


def get_tts(use_edge_tts: bool = True) -> Optional[TextToSpeech]:
    """获取TTS实例"""
    global _tts
    
    if _tts is None:
        _tts = TextToSpeech(use_edge_tts=use_edge_tts)
    
    return _tts

