"""
语音服务整合模块 - 封装语音查询的完整流程
支持双引擎STT：HKGAI（粤语优化） + Whisper（多语言）
"""
from typing import Dict, Optional, Tuple
from services.core.logger import logger
from services.core.config import settings


class VoiceService:
    """语音服务整合类 - 统一处理语音查询流程"""
    
    def __init__(self):
        self._stt = None
        self._hkgai_stt = None  # 新增：HKGAI STT客户端
        self._hkgai_tts = None  # 新增：HKGAI TTS客户端（粤语优化）
        self._wake_word_detector = None
        self._tts = None
    
    def _get_stt(self):
        """获取STT实例（延迟加载）"""
        if self._stt is None:
            from services.speech import get_whisper_stt, reload_whisper_model
            
            # 强制清除所有模型缓存，确保使用最新配置
            logger.info(f"准备加载Whisper模型: {settings.WHISPER_MODEL_SIZE}")
            for old_model in ['base', 'small', 'medium', 'large']:
                if old_model != settings.WHISPER_MODEL_SIZE:
                    reload_whisper_model(old_model)
            
            self._stt = get_whisper_stt(model_size=settings.WHISPER_MODEL_SIZE)
            
            # 验证模型是否正确加载
            if self._stt and self._stt.is_available():
                actual_model = getattr(self._stt, 'model_name', 'unknown')
                expected_model = settings.WHISPER_MODEL_SIZE
                if actual_model != expected_model:
                    logger.error(f"❌ 模型不匹配！期望: {expected_model}, 实际: {actual_model}")
                    logger.error(f"❌ 这可能导致识别准确度低！请检查配置。")
                else:
                    logger.info(f"✅ Whisper模型加载成功: {actual_model}")
        return self._stt
    
    def _get_wake_word_detector(self):
        """获取唤醒词检测器（延迟加载）"""
        if self._wake_word_detector is None:
            from services.speech import get_jarvis_detector
            self._wake_word_detector = get_jarvis_detector()
        return self._wake_word_detector
    
    def _get_tts(self):
        """获取TTS实例（延迟加载）"""
        if self._tts is None:
            from services.speech import get_tts
            self._tts = get_tts(use_edge_tts=settings.USE_EDGE_TTS)
        return self._tts
    
    def _get_hkgai_stt(self):
        """获取HKGAI STT实例（延迟加载）"""
        if self._hkgai_stt is None:
            try:
                from services.speech.hkgai_stt import get_hkgai_client
                self._hkgai_stt = get_hkgai_client()
                if self._hkgai_stt.is_available():
                    logger.info("✅ HKGAI语音识别已加载（粤语优化）")
                else:
                    logger.warning("⚠️  HKGAI语音识别未配置")
            except Exception as e:
                logger.warning(f"⚠️  HKGAI STT加载失败: {e}")
                self._hkgai_stt = None
        return self._hkgai_stt
    
    def _get_hkgai_tts(self):
        """获取HKGAI TTS实例（延迟加载）"""
        if self._hkgai_tts is None:
            try:
                from services.speech.hkgai_tts import get_hkgai_tts_client
                self._hkgai_tts = get_hkgai_tts_client()
                if self._hkgai_tts.is_available():
                    logger.info("✅ HKGAI语音合成已加载（粤语/普通话）")
                else:
                    logger.warning("⚠️  HKGAI TTS未配置")
            except Exception as e:
                logger.warning(f"⚠️  HKGAI TTS加载失败: {e}")
                self._hkgai_tts = None
        return self._hkgai_tts
    
    def transcribe_audio(
        self,
        audio_bytes: bytes,
        audio_format: str,
        language: Optional[str] = None,
        prefer_hkgai: bool = True  # 新增：是否优先使用HKGAI（粤语场景）
    ) -> Dict:
        """
        将音频转换为文本（支持双引擎STT：HKGAI + Whisper）
        
        Args:
            audio_bytes: 音频字节数据
            audio_format: 音频格式（wav, mp3等）
            language: 指定语言（可选）
                - None: 自动检测（推荐，支持中文、粤语、英语混合）
                - "zh": 强制中文（普通话）
                - "yue": 强制粤语（优先使用HKGAI）
                - "en": 强制英语
                - "auto": 自动检测
            prefer_hkgai: 是否优先使用HKGAI（粤语优化）
            
        Returns:
            转录结果字典
        """
        # 判断是否使用HKGAI（粤语场景）
        use_hkgai_first = (
            prefer_hkgai and 
            settings.USE_CANTONESE_API and 
            (language == "yue" or language == "zh" or language is None)
        )
        
        # 尝试使用HKGAI（粤语优化）
        if use_hkgai_first:
            hkgai_stt = self._get_hkgai_stt()
            if hkgai_stt and hkgai_stt.is_available():
                logger.info("🎤 使用HKGAI进行语音识别（粤语优化）...")
                
                hkgai_result = hkgai_stt.recognize(audio_bytes)
                
                if hkgai_result.get("success"):
                    logger.info(f"✅ HKGAI识别成功: '{hkgai_result['text'][:50]}...'")
                    # 添加置信度信息
                    hkgai_result['confidence'] = hkgai_result.get('confidence', 0.95)
                    return hkgai_result
                else:
                    logger.warning(f"⚠️  HKGAI识别失败，fallback到Whisper: {hkgai_result.get('error')}")
        
        # 使用Whisper（作为主要引擎或fallback）
        logger.info("🎤 使用Whisper进行语音识别...")
        stt = self._get_stt()
        if not stt or not stt.is_available():
            return {
                "error": "语音识别服务不可用",
                "text": "",
                "language": None
            }
        
        # 如果未指定语言，使用自动检测（支持多语言）
        if language is None:
            logger.debug("使用自动语言检测（支持中文、粤语、英语）")
        
        result = stt.transcribe_bytes(
            audio_bytes=audio_bytes,
            audio_format=audio_format,
            language=language
        )
        
        if "error" not in result:
            transcribed_text = result.get('text', '')
            detected_language = result.get('language', 'unknown')
            confidence = result.get('confidence', 0)
            
            # 详细记录语言信息
            lang_info = ""
            if detected_language == "yue":
                lang_info = "（粤语）"
            elif detected_language == "zh":
                lang_info = "（中文/普通话）"
            elif detected_language == "en":
                lang_info = "（英语）"
            elif detected_language == "mixed":
                lang_info = "（混合语言）"
            
            logger.info(
                f"✅ Whisper识别完成: '{transcribed_text[:50]}...' "
                f"(语言: {detected_language}{lang_info}, 置信度: {confidence:.2f})"
            )
        
        return result
    
    def detect_and_extract_query(
        self,
        transcribed_text: str,
        use_wake_word: bool = True
    ) -> Tuple[bool, str]:
        """
        检测唤醒词并提取查询文本
        
        Args:
            transcribed_text: 转录的文本
            use_wake_word: 是否使用唤醒词检测
            
        Returns:
            (是否检测到唤醒词, 查询文本)
        """
        if not use_wake_word:
            return False, transcribed_text.strip()
        
        detector = self._get_wake_word_detector()
        wake_word_detected = detector.detect_in_text(transcribed_text)
        
        if wake_word_detected:
            query_text = detector.extract_query_after_wake_word(transcribed_text)
            logger.info(f"检测到唤醒词'Jarvis'，提取查询: '{query_text[:50]}...'")
            return True, query_text
        else:
            logger.info("未检测到唤醒词，使用完整转录文本作为查询")
            return False, transcribed_text.strip()
    
    def generate_audio_response(
        self,
        text: str,
        language: str = "zh",
        prefer_hkgai: bool = True  # 新增：是否优先使用HKGAI（粤语/普通话场景）
    ) -> Optional[str]:
        """
        生成语音回复（支持双引擎TTS：HKGAI + Edge TTS）
        
        Args:
            text: 要转换的文本
            language: 语言代码
                - "zh": 普通话
                - "yue": 粤语
                - "en": 英语
            prefer_hkgai: 是否优先使用HKGAI（粤语/普通话场景）
            
        Returns:
            音频文件路径（如果成功）或None
        """
        if not settings.ENABLE_SPEECH:
            return None
        
        # 判断是否使用HKGAI TTS（粤语或普通话场景）
        use_hkgai_first = (
            prefer_hkgai and 
            (language in ["zh", "yue", "zh-CN", "zh-HK"])
        )
        
        # 尝试使用HKGAI TTS（粤语/普通话优化）
        if use_hkgai_first:
            hkgai_tts = self._get_hkgai_tts()
            if hkgai_tts and hkgai_tts.is_available():
                logger.info("🎤 使用HKGAI TTS合成语音（粤语/普通话优化）...")
                
                # 确定HKGAI语言
                hkgai_lang = "cantonese" if language in ["yue", "zh-HK"] else "mandarin"
                
                audio_file = hkgai_tts.synthesize(
                    text=text,
                    language=hkgai_lang,
                    voice="female"  # 默认女声
                )
                
                if audio_file:
                    logger.info(f"✅ HKGAI TTS合成成功: {audio_file}")
                    return audio_file
                else:
                    logger.warning("⚠️  HKGAI TTS合成失败，fallback到Edge TTS")
        
        # 使用Edge TTS（作为主要引擎或fallback）
        try:
            logger.info("🎤 使用Edge TTS合成语音...")
            tts = self._get_tts()
            if not tts or not tts.is_available():
                logger.warning("⚠️  Edge TTS服务不可用")
                return None
            
            # 确定语言映射
            tts_language_map = {
                "en": "en",
                "zh": "zh-CN",  # 普通话
                "yue": "zh-HK",  # 粤语
                "zh-CN": "zh-CN",
                "zh-HK": "zh-HK",
            }
            tts_lang = tts_language_map.get(language, "zh-CN")
            
            # 创建临时文件
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_audio:
                audio_path = tmp_audio.name
            
            audio_file = tts.speak(
                text=text,
                language=tts_lang,
                output_file=audio_path
            )
            
            if audio_file and os.path.exists(audio_file):
                logger.info(f"✅ Edge TTS合成成功: {audio_file} ({len(text)}字符)")
                return audio_file
            else:
                return None
                
        except Exception as e:
            logger.warning(f"❌ 语音合成失败: {e}")
            return None


# 全局语音服务实例
_voice_service = None


def get_voice_service() -> VoiceService:
    """获取语音服务实例（单例）"""
    global _voice_service
    
    if _voice_service is None:
        _voice_service = VoiceService()
    
    return _voice_service

