"""
文本转语音模块 - Jarvis的语音输出
支持多种TTS引擎（edge-tts优先，fallback到pyttsx3）
"""
from typing import Optional, Dict
import io
from services.core.logger import logger

# 尝试导入edge-tts（优先，支持多语言）
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.warning("edge-tts未安装，将尝试使用其他TTS引擎")

# 尝试导入pyttsx3（备用，离线）
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3未安装")


class TextToSpeech:
    """文本转语音合成器"""
    
    def __init__(self):
        self.edge_tts_available = EDGE_TTS_AVAILABLE
        self.pyttsx3_available = PYTTSX3_AVAILABLE
        self.pyttsx3_engine = None
        
        # 初始化pyttsx3引擎（如果可用）
        if self.pyttsx3_available:
            try:
                self.pyttsx3_engine = pyttsx3.init()
                logger.info("pyttsx3引擎初始化成功（离线TTS）")
            except Exception as e:
                logger.warning(f"pyttsx3初始化失败: {e}")
                self.pyttsx3_available = False
        
        if self.edge_tts_available:
            logger.info("edge-tts可用（在线TTS，支持多语言）")
    
    def synthesize(
        self, 
        text: str, 
        language: str = "zh-CN",
        voice: Optional[str] = None,
        output_format: str = "mp3"
    ) -> bytes:
        """
        将文本转换为语音音频
        
        Args:
            text: 要合成的文本
            language: 语言代码
                - zh-CN: 普通话
                - yue-HK: 粤语（香港）
                - en-US: 英语（美国）
            voice: 语音名称（可选，edge-tts会自动选择）
            output_format: 输出格式（mp3, wav等）
            
        Returns:
            音频文件的字节数据
        """
        # 优先使用edge-tts（支持多语言，质量好）
        if self.edge_tts_available:
            return self._synthesize_edge_tts(text, language, voice)
        
        # Fallback到pyttsx3（离线，但功能有限）
        if self.pyttsx3_available:
            return self._synthesize_pyttsx3(text)
        
        logger.error("没有可用的TTS引擎")
        return b""
    
    def _synthesize_edge_tts(self, text: str, language: str, voice: Optional[str]) -> bytes:
        """使用edge-tts合成语音"""
        try:
            import asyncio
            
            async def _generate():
                # 如果没有指定voice，根据language自动选择
                if voice is None:
                    # 根据language选择voice
                    voice_map = {
                        "zh-CN": "zh-CN-XiaoxiaoNeural",  # 普通话女声
                        "yue-HK": "yue-HK-HiuGaaiNeural",  # 粤语女声
                        "en-US": "en-US-AriaNeural"  # 英语女声
                    }
                    selected_voice = voice_map.get(language, "zh-CN-XiaoxiaoNeural")
                else:
                    selected_voice = voice
                
                # 生成语音
                communicate = edge_tts.Communicate(text, selected_voice)
                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                
                return audio_data
            
            # 运行异步函数
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环已经在运行，创建新任务
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, _generate())
                    audio_data = future.result()
            else:
                audio_data = loop.run_until_complete(_generate())
            
            logger.info(f"TTS合成完成: {len(text)}字符 -> {len(audio_data)}字节")
            return audio_data
            
        except Exception as e:
            logger.error(f"edge-tts合成失败: {e}")
            # Fallback到pyttsx3
            if self.pyttsx3_available:
                return self._synthesize_pyttsx3(text)
            return b""
    
    def _synthesize_pyttsx3(self, text: str) -> bytes:
        """使用pyttsx3合成语音（离线，功能有限）"""
        try:
            # pyttsx3只能保存到文件，不能直接返回bytes
            # 这里使用临时文件
            import tempfile
            from pathlib import Path
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_path = tmp_file.name
            
            try:
                self.pyttsx3_engine.save_to_file(text, tmp_path)
                self.pyttsx3_engine.runAndWait()
                
                with open(tmp_path, "rb") as f:
                    audio_data = f.read()
                
                return audio_data
            finally:
                Path(tmp_path).unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"pyttsx3合成失败: {e}")
            return b""
    
    def speak(self, text: str, language: str = "zh-CN"):
        """
        直接播放语音（同步）
        
        Args:
            text: 要说的文本
            language: 语言代码
        """
        if self.pyttsx3_available and self.pyttsx3_engine:
            try:
                self.pyttsx3_engine.say(text)
                self.pyttsx3_engine.runAndWait()
                logger.info(f"播放语音: {text[:50]}...")
            except Exception as e:
                logger.error(f"播放语音失败: {e}")
        else:
            logger.warning("pyttsx3不可用，无法直接播放语音")
    
    def is_available(self) -> bool:
        """检查TTS是否可用"""
        return self.edge_tts_available or self.pyttsx3_available


# 全局TTS实例
_tts = None


def get_tts() -> TextToSpeech:
    """获取全局TTS实例"""
    global _tts
    if _tts is None:
        _tts = TextToSpeech()
    return _tts

