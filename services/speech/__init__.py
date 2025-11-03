"""
语音识别和合成模块 - Jarvis语音助手
"""
from services.speech.whisper_stt import get_whisper_stt, WhisperSTT, reload_whisper_model
from services.speech.wake_word_detector import get_jarvis_detector, JarvisWakeWordDetector
from services.speech.tts import get_tts, TextToSpeech
from services.speech.voice_service import get_voice_service, VoiceService

# 可选：Silero VAD（如果已安装）
try:
    from services.speech.vad_silero import get_silero_vad, SileroVAD
    SILERO_VAD_AVAILABLE = True
except ImportError:
    SILERO_VAD_AVAILABLE = False
    SileroVAD = None

__all__ = [
    "get_whisper_stt",
    "WhisperSTT",
    "reload_whisper_model",
    "get_jarvis_detector",
    "JarvisWakeWordDetector",
    "get_tts",
    "TextToSpeech",
    "get_voice_service",
    "VoiceService",
]

if SILERO_VAD_AVAILABLE:
    __all__.extend(["get_silero_vad", "SileroVAD"])
