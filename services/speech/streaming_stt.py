"""
流式语音转文本模块
支持实时Whisper处理和MLX优化（Mac）
"""
import os
import numpy as np
from typing import Optional, Dict, AsyncGenerator, Iterator
from services.core.logger import logger

# 尝试导入不同的Whisper实现
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

# Lightning Whisper MLX（Mac优化）
try:
    from lightning_whisper_mlx import LightningWhisperMLX
    LIGHTNING_WHISPER_MLX_AVAILABLE = True
except ImportError:
    LIGHTNING_WHISPER_MLX_AVAILABLE = False

# Faster Whisper（更快的流式处理）
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False

# MLX检测（Mac）
try:
    import mlx.core as mx
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False


class StreamingSTT:
    """流式语音转文本服务"""
    
    def __init__(self, model_size: str = "medium", use_mlx: bool = False, device: str = "cpu"):
        """
        初始化流式STT
        
        Args:
            model_size: 模型大小（tiny/base/small/medium/large）
            use_mlx: 是否使用MLX（Mac优化）
            device: 设备（cpu/cuda/mps）
        """
        self.model_size = model_size
        self.use_mlx = use_mlx and MLX_AVAILABLE
        self.device = device
        self.model = None
        self.model_type = None
        
        # 根据平台选择最优实现
        if self.use_mlx and LIGHTNING_WHISPER_MLX_AVAILABLE:
            self._init_lightning_whisper_mlx()
        elif FASTER_WHISPER_AVAILABLE:
            self._init_faster_whisper()
        elif WHISPER_AVAILABLE:
            self._init_whisper()
        else:
            logger.warning("未找到可用的Whisper实现")
    
    def _init_lightning_whisper_mlx(self):
        """初始化Lightning Whisper MLX（Mac优化）"""
        try:
            logger.info(f"使用Lightning Whisper MLX（Mac优化）: {self.model_size}")
            # 注意：参数是model而不是model_name
            self.model = LightningWhisperMLX(
                model=self.model_size,
                batch_size=1,
                quant=None  # 可以设置为"q4_0"或"q8_0"进行量化
            )
            self.model_type = "lightning_mlx"
            logger.info("✅ Lightning Whisper MLX加载成功")
        except Exception as e:
            logger.error(f"Lightning Whisper MLX初始化失败: {e}")
            logger.info("降级到Faster Whisper...")
            self._init_faster_whisper()
    
    def _init_faster_whisper(self):
        """初始化Faster Whisper（支持流式）"""
        try:
            logger.info(f"使用Faster Whisper（流式优化）: {self.model_size}")
            device = "cuda" if self.device == "cuda" else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            self.model = WhisperModel(
                self.model_size,
                device=device,
                compute_type=compute_type
            )
            self.model_type = "faster_whisper"
            logger.info("✅ Faster Whisper加载成功")
        except Exception as e:
            logger.error(f"Faster Whisper初始化失败: {e}")
            self._init_whisper()
    
    def _init_whisper(self):
        """初始化标准Whisper"""
        try:
            logger.info(f"使用标准Whisper: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            self.model_type = "whisper"
            logger.info("✅ Whisper加载成功")
        except Exception as e:
            logger.error(f"Whisper初始化失败: {e}")
    
    def transcribe_stream(
        self,
        audio_chunks: Iterator[np.ndarray],
        sample_rate: int = 16000,
        language: Optional[str] = None
    ) -> Iterator[Dict]:
        """
        流式转录音频块
        
        Args:
            audio_chunks: 音频块迭代器（numpy数组）
            sample_rate: 采样率
            language: 语言代码（可选）
            
        Yields:
            转录结果字典，包含text、language等
        """
        if not self.model:
            yield {
                "error": "模型未加载",
                "text": "",
                "language": None
            }
            return
        
        try:
            # 累积音频块
            accumulated_audio = []
            
            for chunk in audio_chunks:
                accumulated_audio.append(chunk)
                
                # 当累积足够音频时进行转录（例如1秒）
                if len(accumulated_audio) >= sample_rate:  # 1秒音频
                    audio_array = np.concatenate(accumulated_audio)
                    
                    # 根据模型类型转录
                    if self.model_type == "lightning_mlx":
                        result = self._transcribe_lightning_mlx(audio_array, sample_rate, language)
                    elif self.model_type == "faster_whisper":
                        result = self._transcribe_faster_whisper(audio_array, sample_rate, language)
                    else:
                        result = self._transcribe_whisper(audio_array, sample_rate, language)
                    
                    if result:
                        yield result
                    
                    # 保留部分音频用于上下文（例如0.5秒）
                    keep_samples = int(sample_rate * 0.5)
                    accumulated_audio = accumulated_audio[-keep_samples:]
            
            # 处理剩余的音频
            if accumulated_audio:
                audio_array = np.concatenate(accumulated_audio)
                if self.model_type == "lightning_mlx":
                    result = self._transcribe_lightning_mlx(audio_array, sample_rate, language)
                elif self.model_type == "faster_whisper":
                    result = self._transcribe_faster_whisper(audio_array, sample_rate, language)
                else:
                    result = self._transcribe_whisper(audio_array, sample_rate, language)
                
                if result:
                    yield result
                    
        except Exception as e:
            logger.error(f"流式转录失败: {e}")
            yield {
                "error": str(e),
                "text": "",
                "language": None
            }
    
    def _transcribe_lightning_mlx(self, audio_array: np.ndarray, sample_rate: int, language: Optional[str]) -> Optional[Dict]:
        """使用Lightning Whisper MLX转录"""
        try:
            # Lightning Whisper MLX的API
            result = self.model.transcribe(audio_array, language=language)
            return {
                "text": result.get("text", ""),
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", [])
            }
        except Exception as e:
            logger.error(f"Lightning Whisper MLX转录失败: {e}")
            return None
    
    def _transcribe_faster_whisper(self, audio_array: np.ndarray, sample_rate: int, language: Optional[str]) -> Optional[Dict]:
        """使用Faster Whisper转录"""
        try:
            segments, info = self.model.transcribe(
                audio_array,
                language=language,
                beam_size=5,
                vad_filter=True  # 启用VAD过滤
            )
            
            text = " ".join([segment.text for segment in segments])
            return {
                "text": text,
                "language": info.language,
                "segments": [{"text": s.text, "start": s.start, "end": s.end} for s in segments]
            }
        except Exception as e:
            logger.error(f"Faster Whisper转录失败: {e}")
            return None
    
    def _transcribe_whisper(self, audio_array: np.ndarray, sample_rate: int, language: Optional[str]) -> Optional[Dict]:
        """使用标准Whisper转录"""
        try:
            result = self.model.transcribe(
                audio_array,
                language=language,
                fp16=False,
                beam_size=5
            )
            return {
                "text": result.get("text", ""),
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", [])
            }
        except Exception as e:
            logger.error(f"Whisper转录失败: {e}")
            return None
    
    def is_available(self) -> bool:
        """检查STT是否可用"""
        return self.model is not None


# 全局实例
_streaming_stt: Optional[StreamingSTT] = None


def get_streaming_stt(model_size: str = "medium", use_mlx: bool = False, device: str = "cpu") -> Optional[StreamingSTT]:
    """获取流式STT实例"""
    global _streaming_stt
    
    if _streaming_stt is None:
        _streaming_stt = StreamingSTT(model_size=model_size, use_mlx=use_mlx, device=device)
    
    return _streaming_stt if _streaming_stt.is_available() else None

