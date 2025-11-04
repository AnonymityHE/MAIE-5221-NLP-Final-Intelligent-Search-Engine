"""
流式文本转语音模块
支持Parler-TTS、MeloTTS和Edge TTS
支持流式输出，降低延迟
"""
import os
import tempfile
import numpy as np
from typing import Optional, Iterator, AsyncGenerator
from services.core.logger import logger

# Parler-TTS（流式支持）
try:
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoProcessor
    import torch
    PARLER_TTS_AVAILABLE = True
except ImportError:
    PARLER_TTS_AVAILABLE = False

# MeloTTS（多语言，Mac优化）
# 注意：MeloTTS需要从GitHub安装：pip install git+https://github.com/myshell-ai/MeloTTS.git
try:
    from melo.api import TTS
    MELO_TTS_AVAILABLE = True
except ImportError:
    MELO_TTS_AVAILABLE = False
    logger.debug("MeloTTS未安装，使用命令: pip install git+https://github.com/myshell-ai/MeloTTS.git")

# Edge TTS（备选，不支持流式）
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False


class StreamingTTS:
    """流式文本转语音服务"""
    
    def __init__(self, tts_type: str = "parler", device: str = "cpu"):
        """
        初始化流式TTS
        
        Args:
            tts_type: TTS类型（parler/melo/edge）
            device: 设备（cpu/cuda/mps）
        """
        self.tts_type = tts_type
        self.device = device
        self.model = None
        self.processor = None
        
        if tts_type == "parler" and PARLER_TTS_AVAILABLE:
            self._init_parler_tts()
        elif tts_type == "melo" and MELO_TTS_AVAILABLE:
            self._init_melo_tts()
        elif tts_type == "edge" and EDGE_TTS_AVAILABLE:
            logger.info("使用Edge TTS（不支持流式）")
        else:
            logger.warning(f"TTS类型 {tts_type} 不可用，将使用Edge TTS")
    
    def _init_parler_tts(self):
        """初始化Parler-TTS（支持流式）"""
        try:
            logger.info("正在加载Parler-TTS（流式支持）...")
            model_id = "parler-tts/parler-tts-mini-v2"
            
            self.processor = AutoProcessor.from_pretrained(model_id)
            self.model = ParlerTTSForConditionalGeneration.from_pretrained(model_id)
            
            # 设置设备
            if self.device == "cuda" and torch.cuda.is_available():
                self.model = self.model.to("cuda")
            elif self.device == "mps" and torch.backends.mps.is_available():
                self.model = self.model.to("mps")
            
            self.model.eval()
            logger.info("✅ Parler-TTS加载成功（支持流式输出）")
        except Exception as e:
            logger.error(f"Parler-TTS初始化失败: {e}")
            PARLER_TTS_AVAILABLE = False
    
    def _init_melo_tts(self):
        """初始化MeloTTS（多语言，Mac优化）"""
        try:
            logger.info("正在加载MeloTTS（多语言，Mac优化）...")
            # MeloTTS需要指定语言，默认使用EN
            self.model = TTS(language='EN', device=self.device)
            logger.info("✅ MeloTTS加载成功（支持多语言）")
        except Exception as e:
            logger.error(f"MeloTTS初始化失败: {e}")
            logger.info("提示: MeloTTS需要从GitHub安装: pip install git+https://github.com/myshell-ai/MeloTTS.git")
            MELO_TTS_AVAILABLE = False
            self.model = None
    
    def generate_stream(
        self,
        text: str,
        language: str = "zh",
        voice: Optional[str] = None,
        speed: float = 1.0
    ) -> Iterator[bytes]:
        """
        流式生成语音
        
        Args:
            text: 要转换的文本
            language: 语言代码（zh/en/fr/es/ja/ko）
            voice: 语音ID（可选）
            speed: 语速（1.0为正常速度）
            
        Yields:
            音频数据块（bytes）
        """
        if self.tts_type == "parler" and self.model:
            yield from self._generate_parler_stream(text, language, voice)
        elif self.tts_type == "melo" and self.model:
            yield from self._generate_melo_stream(text, language, voice, speed)
        else:
            # Fallback到Edge TTS（非流式）
            yield from self._generate_edge_fallback(text, language, voice)
    
    def _generate_parler_stream(self, text: str, language: str, voice: Optional[str]) -> Iterator[bytes]:
        """使用Parler-TTS流式生成"""
        try:
            # Parler-TTS的流式生成
            inputs = self.processor(
                text=text,
                return_tensors="pt",
                sampling_rate=22050
            )
            
            if self.device == "cuda" and torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            elif self.device == "mps" and torch.backends.mps.is_available():
                inputs = {k: v.to("mps") for k, v in inputs.items()}
            
            # 生成音频（流式）
            with torch.no_grad():
                audio_array = self.model.generate(**inputs)
            
            # 转换为numpy并分块输出
            if isinstance(audio_array, torch.Tensor):
                audio_array = audio_array.cpu().numpy()
            
            # 分块输出（模拟流式）
            chunk_size = 4096
            for i in range(0, len(audio_array), chunk_size):
                chunk = audio_array[i:i+chunk_size]
                # 转换为WAV格式的字节
                yield self._audio_to_wav_bytes(chunk, sample_rate=22050)
                
        except Exception as e:
            logger.error(f"Parler-TTS流式生成失败: {e}")
    
    def _generate_melo_stream(self, text: str, language: str, voice: Optional[str], speed: float) -> Iterator[bytes]:
        """使用MeloTTS流式生成"""
        try:
            # MeloTTS的流式生成
            # 根据语言选择语音
            lang_map = {
                "zh": "ZH",
                "en": "EN",
                "fr": "FR",
                "es": "ES",
                "ja": "JP",
                "ko": "KR"
            }
            melo_lang = lang_map.get(language, "EN")
            
            # 生成音频
            audio_array = self.model.tts_to_file(
                text=text,
                language=melo_lang,
                output_path=None,  # 不保存文件，直接返回
                speed=speed
            )
            
            # 分块输出
            chunk_size = 4096
            for i in range(0, len(audio_array), chunk_size):
                chunk = audio_array[i:i+chunk_size]
                yield self._audio_to_wav_bytes(chunk, sample_rate=22050)
                
        except Exception as e:
            logger.error(f"MeloTTS流式生成失败: {e}")
    
    def _generate_edge_fallback(self, text: str, language: str, voice: Optional[str]) -> Iterator[bytes]:
        """使用Edge TTS作为备选（非流式）"""
        try:
            import asyncio
            import edge_tts
            
            # 选择语音
            if not voice:
                voice_map = {
                    "zh": "zh-CN-XiaoxiaoNeural",
                    "zh-CN": "zh-CN-XiaoxiaoNeural",
                    "zh-HK": "zh-HK-HiuGaaiNeural",
                    "yue": "zh-HK-HiuGaaiNeural",
                    "en": "en-US-AriaNeural",
                }
                voice = voice_map.get(language, "zh-CN-XiaoxiaoNeural")
            
            async def _generate():
                communicate = edge_tts.Communicate(text, voice)
                # 生成完整音频
                audio_bytes = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_bytes += chunk["data"]
                return audio_bytes
            
            audio_bytes = asyncio.run(_generate())
            
            # 分块输出（模拟流式）
            chunk_size = 4096
            for i in range(0, len(audio_bytes), chunk_size):
                yield audio_bytes[i:i+chunk_size]
                
        except Exception as e:
            logger.error(f"Edge TTS生成失败: {e}")
    
    def _audio_to_wav_bytes(self, audio_array: np.ndarray, sample_rate: int = 22050) -> bytes:
        """将音频数组转换为WAV格式的字节"""
        try:
            import soundfile as sf
            from io import BytesIO
            
            buffer = BytesIO()
            sf.write(buffer, audio_array, sample_rate, format='WAV')
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"音频转换失败: {e}")
            return b""
    
    def is_available(self) -> bool:
        """检查TTS是否可用"""
        return self.model is not None or EDGE_TTS_AVAILABLE


# 全局实例
_streaming_tts: Optional[StreamingTTS] = None


def get_streaming_tts(tts_type: str = "parler", device: str = "cpu") -> Optional[StreamingTTS]:
    """获取流式TTS实例"""
    global _streaming_tts
    
    if _streaming_tts is None:
        _streaming_tts = StreamingTTS(tts_type=tts_type, device=device)
    
    return _streaming_tts if _streaming_tts.is_available() else None

