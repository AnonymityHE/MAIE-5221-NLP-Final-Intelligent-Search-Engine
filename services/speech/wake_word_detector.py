"""
唤醒词检测模块 - 检测"Jarvis"
支持简单的关键词检测和音频流检测
"""
import re
from typing import Optional, Callable
from services.core.logger import logger

try:
    import pyaudio
    import numpy as np
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.warning("pyaudio未安装，实时唤醒词检测功能将被禁用")


class JarvisWakeWordDetector:
    """Jarvis唤醒词检测器"""
    
    def __init__(self):
        self.wake_words = ["jarvis", "jarvis", "javis"]  # 支持多种发音
        self.is_listening = False
        self._audio_stream = None
        
        logger.info("初始化Jarvis唤醒词检测器")
    
    def detect_in_text(self, text: str) -> bool:
        """
        在文本中检测唤醒词
        
        Args:
            text: 输入文本
            
        Returns:
            是否检测到唤醒词
        """
        if not text:
            return False
        
        text_lower = text.lower().strip()
        
        # 检查是否包含唤醒词（不限于开头）
        for wake_word in self.wake_words:
            # 匹配 "jarvis" 或 "jarvis, ..." 或 "jarvis ..." 或 "... jarvis"
            pattern = rf'(^|\s+){re.escape(wake_word)}\s*[,，。.?！!]?\s*'
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.info(f"检测到唤醒词: {wake_word}")
                return True
        
        return False
    
    def extract_query_after_wake_word(self, text: str) -> str:
        """
        提取唤醒词之后的查询文本
        
        Args:
            text: 包含唤醒词的完整文本
            
        Returns:
            唤醒词之后的查询文本
        """
        if not text:
            return ""
        
        text_lower = text.lower()
        
        for wake_word in self.wake_words:
            # 找到唤醒词的位置（支持在文本中间）
            pattern = rf'(^|\s+){re.escape(wake_word)}\s*[,，。.?！!]?\s*(.+)'
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                # 返回原始文本中唤醒词之后的部分
                wake_word_pos = text_lower.find(wake_word.lower())
                if wake_word_pos >= 0:
                    query_start = wake_word_pos + len(wake_word)
                    query_text = text[query_start:].strip()
                    # 移除开头的标点符号和空格
                    query_text = re.sub(r'^[,，。.?！!]?\s*', '', query_text)
                    logger.debug(f"提取查询文本: {query_text[:50]}...")
                    return query_text
        
        # 如果没有找到唤醒词，返回原文本
        return text.strip()
    
    def start_listening(
        self,
        callback: Callable[[str], None],
        sample_rate: int = 16000,
        chunk_size: int = 1024
    ) -> bool:
        """
        开始实时监听唤醒词（可选功能）
        
        Args:
            callback: 检测到唤醒词时的回调函数
            sample_rate: 采样率
            chunk_size: 音频块大小
            
        Returns:
            是否成功启动监听
        """
        if not PYAUDIO_AVAILABLE:
            logger.warning("pyaudio未安装，无法启动实时监听")
            return False
        
        # 这里可以实现实时音频流监听
        # 由于需要实时STT和唤醒词检测，实现较复杂
        # 目前先提供文本检测功能
        logger.info("实时监听功能待实现")
        return False
    
    def stop_listening(self):
        """停止监听"""
        if self._audio_stream:
            try:
                self._audio_stream.stop_stream()
                self._audio_stream.close()
                self._audio_stream = None
            except:
                pass
        self.is_listening = False
        logger.info("已停止监听")


# 全局唤醒词检测器实例
_jarvis_detector = None


def get_jarvis_detector() -> JarvisWakeWordDetector:
    """获取Jarvis唤醒词检测器实例"""
    global _jarvis_detector
    
    if _jarvis_detector is None:
        _jarvis_detector = JarvisWakeWordDetector()
    
    return _jarvis_detector

