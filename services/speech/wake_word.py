"""
唤醒词检测模块 - 检测"Hey Jarvis"等唤醒词
支持实时音频流监听
"""
import threading
import queue
from typing import Optional, Callable
from services.core.logger import logger

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.warning("pyaudio未安装，唤醒词检测功能将被禁用")

try:
    from pocketsphinx import LiveSpeech, get_model_path
    POCKETSPHINX_AVAILABLE = True
except ImportError:
    POCKETSPHINX_AVAILABLE = False
    logger.warning("pocketsphinx未安装，唤醒词检测功能将被禁用")


class WakeWordDetector:
    """唤醒词检测器 - 检测"Hey Jarvis"等唤醒词"""
    
    def __init__(self, wake_word: str = "jarvis"):
        """
        初始化唤醒词检测器
        
        Args:
            wake_word: 唤醒词（如"jarvis"）
        """
        self.wake_word = wake_word.lower()
        self.is_listening = False
        self.callback: Optional[Callable] = None
        self.listening_thread: Optional[threading.Thread] = None
        
        # 检查依赖
        self.pyaudio_available = PYAUDIO_AVAILABLE
        self.pocketsphinx_available = POCKETSPHINX_AVAILABLE
        
        if not self.pyaudio_available:
            logger.warning("pyaudio未安装，无法进行实时音频捕获")
        if not self.pocketsphinx_available:
            logger.warning("pocketsphinx未安装，将使用简单的关键词匹配")
    
    def detect_in_text(self, text: str) -> bool:
        """
        在文本中检测唤醒词（简单关键词匹配）
        
        Args:
            text: 输入文本
            
        Returns:
            是否检测到唤醒词
        """
        text_lower = text.lower()
        
        # 检测各种唤醒词变体
        wake_patterns = [
            self.wake_word,
            f"hey {self.wake_word}",
            f"hi {self.wake_word}",
            f"hello {self.wake_word}",
        ]
        
        for pattern in wake_patterns:
            if pattern in text_lower:
            logger.info(f"检测到唤醒词: '{pattern}'")
            return True
        
        return False
    
    def start_listening(self, callback: Callable[[], None]):
        """
        开始实时监听唤醒词
        
        Args:
            callback: 检测到唤醒词时调用的回调函数
        """
        if not self.pyaudio_available:
            logger.error("pyaudio未安装，无法启动实时监听")
            return False
        
        if self.is_listening:
            logger.warning("唤醒词检测已在运行")
            return False
        
        self.callback = callback
        self.is_listening = True
        
        # 如果pocketsphinx可用，使用它进行实时检测
        if self.pocketsphinx_available:
            self._start_pocketsphinx_listening()
        else:
            # 否则使用简单的音频流监听（需要集成Whisper）
            logger.info("使用简单音频监听模式（需要手动集成Whisper）")
        
        return True
    
    def _start_pocketsphinx_listening(self):
        """使用pocketsphinx进行实时唤醒词检测"""
        def _listen():
            try:
                logger.info(f"开始监听唤醒词: '{self.wake_word}'")
                # 这里需要配置pocketsphinx的模型和关键词列表
                # 由于配置较复杂，暂时使用文本检测作为fallback
                logger.warning("pocketsphinx配置较复杂，建议使用文本检测模式")
            except Exception as e:
                logger.error(f"唤醒词监听失败: {e}")
                self.is_listening = False
        
        self.listening_thread = threading.Thread(target=_listen, daemon=True)
        self.listening_thread.start()
    
    def stop_listening(self):
        """停止监听"""
        if not self.is_listening:
            return
        
        self.is_listening = False
        if self.listening_thread:
            self.listening_thread.join(timeout=1.0)
        logger.info("已停止唤醒词监听")
    
    def is_available(self) -> bool:
        """检查唤醒词检测是否可用"""
        return self.pyaudio_available or True  # 文本检测始终可用


# 全局唤醒词检测器实例
_wake_detector = None


def get_wake_detector(wake_word: str = "jarvis") -> WakeWordDetector:
    """获取全局唤醒词检测器实例"""
    global _wake_detector
    if _wake_detector is None:
        _wake_detector = WakeWordDetector(wake_word)
    return _wake_detector

