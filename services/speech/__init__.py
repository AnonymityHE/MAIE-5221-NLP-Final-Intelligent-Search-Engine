"""
语音识别和合成模块 - Jarvis语音助手
支持流式STT/TTS和Mac MLX优化
包含粤语专用API支持
"""
from services.speech.whisper_stt import get_whisper_stt, WhisperSTT, reload_whisper_model
from services.speech.wake_word_detector import get_jarvis_detector, JarvisWakeWordDetector
from services.speech.tts import get_tts, TextToSpeech
from services.speech.voice_service import get_voice_service, VoiceService

# 粤语专用STT
try:
    from services.speech.cantonese_stt import get_cantonese_stt, CantoneseSTT
    CANTONESE_STT_AVAILABLE = True
except ImportError:
    CANTONESE_STT_AVAILABLE = False
    CantoneseSTT = None

# 可选：Silero VAD（如果已安装）
try:
    from services.speech.vad_silero import get_silero_vad, SileroVAD
    SILERO_VAD_AVAILABLE = True
except ImportError:
    SILERO_VAD_AVAILABLE = False
    SileroVAD = None

# 可选：流式STT（如果已安装）
try:
    from services.speech.streaming_stt import get_streaming_stt, StreamingSTT
    STREAMING_STT_AVAILABLE = True
except ImportError:
    STREAMING_STT_AVAILABLE = False
    StreamingSTT = None

# 可选：流式TTS（如果已安装）
try:
    from services.speech.streaming_tts import get_streaming_tts, StreamingTTS
    STREAMING_TTS_AVAILABLE = True
except (ImportError, RuntimeError, Exception) as e:
    STREAMING_TTS_AVAILABLE = False
    StreamingTTS = None
    # 忽略MeCab等可选依赖的错误

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

if CANTONESE_STT_AVAILABLE:
    __all__.extend(["get_cantonese_stt", "CantoneseSTT"])

if SILERO_VAD_AVAILABLE:
    __all__.extend(["get_silero_vad", "SileroVAD"])

if STREAMING_STT_AVAILABLE:
    __all__.extend(["get_streaming_stt", "StreamingSTT"])

if STREAMING_TTS_AVAILABLE:
    __all__.extend(["get_streaming_tts", "StreamingTTS"])
