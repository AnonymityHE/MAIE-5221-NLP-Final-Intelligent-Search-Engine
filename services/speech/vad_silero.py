"""
Silero VAD（语音活动检测）模块
使用深度学习模型进行更精确的语音活动检测
"""
import os
import tempfile
import numpy as np
from typing import List, Tuple, Optional
from services.core.logger import logger

try:
    import torch
    SILERO_VAD_AVAILABLE = True
except ImportError:
    SILERO_VAD_AVAILABLE = False
    logger.warning("torch未安装，Silero VAD功能将被禁用。安装命令: pip install torch")


class SileroVAD:
    """Silero VAD语音活动检测器"""
    
    def __init__(self, device: str = "cpu"):
        """
        初始化Silero VAD
        
        Args:
            device: 设备类型（"cpu"或"cuda"）
        """
        if not SILERO_VAD_AVAILABLE:
            self.model = None
            self.utils = None
            logger.warning("Silero VAD未安装，无法初始化")
            return
        
        try:
            self.device = torch.device(device)
            logger.info(f"正在加载Silero VAD模型（设备: {device}）...")
            
            # 使用torch.hub加载Silero VAD模型
            # 这是官方推荐的方式
            self.model, self.utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False  # 如果安装了onnxruntime，可以设置为True
            )
            
            # 提取工具函数
            # utils是一个元组：(get_speech_timestamps, save_audio, read_audio, ...)
            self.get_speech_timestamps = self.utils[0]
            
            logger.info("✅ Silero VAD模型加载完成")
        except Exception as e:
            logger.error(f"加载Silero VAD模型失败: {e}", exc_info=True)
            self.model = None
            self.utils = None
    
    def detect_speech_segments(self, audio_array: np.ndarray, sample_rate: int = 16000) -> List[Tuple[float, float]]:
        """
        检测音频中的语音片段
        
        Args:
            audio_array: 音频数据（numpy数组，float32，范围-1到1）
            sample_rate: 采样率（默认16000Hz）
            
        Returns:
            语音片段列表，每个元素为(start_time, end_time)元组（单位：秒）
        """
        if self.model is None or self.utils is None:
            logger.warning("Silero VAD模型未加载，无法检测语音片段")
            return []
        
        try:
            # 确保音频数据格式正确
            if isinstance(audio_array, np.ndarray):
                if audio_array.dtype != np.float32:
                    audio_array = audio_array.astype(np.float32)
                
                # 归一化到-1到1范围
                max_val = np.max(np.abs(audio_array))
                if max_val > 1.0:
                    audio_array = audio_array / max_val
            else:
                # 如果是torch tensor，转换为numpy
                if hasattr(audio_array, 'numpy'):
                    audio_array = audio_array.numpy().astype(np.float32)
                else:
                    audio_array = np.array(audio_array, dtype=np.float32)
            
            # 转换为torch tensor（Silero VAD需要torch tensor）
            if isinstance(audio_array, np.ndarray):
                audio_tensor = torch.from_numpy(audio_array).to(self.device)
            elif hasattr(audio_array, 'to'):
                # 已经是torch tensor
                audio_tensor = audio_array.to(self.device)
            else:
                audio_tensor = torch.tensor(audio_array, dtype=torch.float32).to(self.device)
            
            # 检测语音片段
            speech_timestamps = self.get_speech_timestamps(
                audio_tensor,
                self.model,
                sampling_rate=sample_rate,
                threshold=0.5,  # 语音概率阈值（0-1）
                min_speech_duration_ms=250,  # 最小语音片段长度（毫秒）
                min_silence_duration_ms=100,  # 最小静音间隔（毫秒）
                speech_pad_ms=30  # 语音片段前后填充（毫秒）
            )
            
            # 转换为(start_time, end_time)格式
            segments = []
            for segment in speech_timestamps:
                start_time = segment['start'] / sample_rate
                end_time = segment['end'] / sample_rate
                segments.append((start_time, end_time))
            
            logger.info(f"Silero VAD检测到 {len(segments)} 个语音片段")
            return segments
            
        except Exception as e:
            logger.error(f"Silero VAD检测失败: {e}", exc_info=True)
            return []
    
    def extract_speech_audio(self, audio_array: np.ndarray, sample_rate: int = 16000) -> Optional[np.ndarray]:
        """
        提取音频中的语音部分（去除静音）
        
        Args:
            audio_array: 原始音频数据
            sample_rate: 采样率
            
        Returns:
            只包含语音的音频数据，如果检测失败返回None
        """
        segments = self.detect_speech_segments(audio_array, sample_rate)
        
        if not segments:
            logger.warning("未检测到语音片段")
            return None
        
        # 合并所有语音片段
        speech_samples = []
        for start_time, end_time in segments:
            start_sample = int(start_time * sample_rate)
            end_sample = int(end_time * sample_rate)
            if start_sample < len(audio_array) and end_sample <= len(audio_array):
                speech_samples.append(audio_array[start_sample:end_sample])
        
        if speech_samples:
            result = np.concatenate(speech_samples)
            logger.info(f"提取语音片段：原始长度={len(audio_array)/sample_rate:.2f}s，语音长度={len(result)/sample_rate:.2f}s")
            return result
        
        return None
    
    def is_speech_active(self, audio_array: np.ndarray, sample_rate: int = 16000) -> bool:
        """
        检测音频中是否包含语音
        
        Args:
            audio_array: 音频数据
            sample_rate: 采样率
            
        Returns:
            True表示包含语音，False表示静音
        """
        segments = self.detect_speech_segments(audio_array, sample_rate)
        return len(segments) > 0


# 全局VAD实例
_silero_vad: Optional[SileroVAD] = None


def get_silero_vad(device: str = "cpu") -> Optional[SileroVAD]:
    """
    获取Silero VAD实例（单例模式）
    
    Args:
        device: 设备类型
        
    Returns:
        SileroVAD实例，如果未安装则返回None
    """
    global _silero_vad
    
    if not SILERO_VAD_AVAILABLE:
        return None
    
    if _silero_vad is None:
        try:
            _silero_vad = SileroVAD(device=device)
        except Exception as e:
            logger.error(f"初始化Silero VAD失败: {e}")
            return None
    
    return _silero_vad if _silero_vad.model is not None else None


def reload_silero_vad():
    """重新加载Silero VAD模型"""
    global _silero_vad
    _silero_vad = None
    logger.info("Silero VAD缓存已清除")

