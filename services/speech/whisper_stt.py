"""
语音转文本模块 - 使用Whisper实现多语言语音识别
支持粤语、普通话、英语
集成粤语专用API以提供更好的粤语识别效果
"""
import os
import tempfile
from typing import Optional, Dict
from services.core.logger import logger
from services.core.config import settings

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("openai-whisper未安装，语音识别功能将被禁用")

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False


class WhisperSTT:
    """Whisper语音转文本服务（支持多语言）"""
    
    def __init__(self, model_size: str = "base"):
        """
        初始化Whisper STT
        
        Args:
            model_size: 模型大小
                - tiny: 最快，准确度较低
                - base: 平衡速度和准确度（推荐）
                - small: 更准确但更慢
                - medium: 高准确度
                - large: 最高准确度（最慢）
        """
        self.model = None
        self.model_size = model_size
        self.model_name = f"base"  # 默认使用base模型
        
        if not WHISPER_AVAILABLE:
            logger.warning("Whisper未安装，语音识别功能不可用")
            logger.info("安装命令: pip install openai-whisper")
            return
        
        try:
            logger.info(f"正在加载Whisper模型: {model_size}")
            self.model = whisper.load_model(model_size)
            self.model_name = model_size
            logger.info(f"Whisper模型加载完成: {model_size}")
        except Exception as e:
            logger.error(f"加载Whisper模型失败: {e}")
            self.model = None
    
    def transcribe(
        self, 
        audio_file_path: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict:
        """
        将音频文件转换为文本
        
        Args:
            audio_file_path: 音频文件路径（支持wav, mp3, m4a等格式）
            language: 指定语言（可选）
                - "zh": 中文（自动检测普通话或粤语）
                - "en": 英语
                - "yue": 粤语（如果Whisper支持）
                - None: 自动检测
            task: "transcribe"（转写）或"translate"（翻译为英语）
            
        Returns:
            包含text、language等信息的字典
        """
        if not self.model:
            return {
                "error": "Whisper模型未加载",
                "text": "",
                "language": None
            }
        
        if not os.path.exists(audio_file_path):
            return {
                "error": f"音频文件不存在: {audio_file_path}",
                "text": "",
                "language": None
            }
        
        try:
            logger.info(f"开始转录音频: {audio_file_path}")
            
            # 准备参数
            decode_options = {}
            
            # 如果未指定语言，使用自动检测（支持中文、粤语、英语混合）
            # Whisper可以自动检测语言，包括中文（普通话和粤语）和英语
            if language is None:
                logger.debug("使用自动语言检测（支持中文、粤语、英语）")
                # 不指定language参数，让Whisper自动检测
            else:
                # 如果指定了语言，进行映射
                lang_map = {
                    "zh": "zh",  # 中文（普通话）
                    "zh-CN": "zh",  # 普通话
                    "zh-HK": "zh",  # 粤语（Whisper用zh表示，但会识别粤语特征）
                    "yue": "zh",  # 粤语
                    "en": "en",  # 英语
                    "auto": None,  # 自动检测
                }
                mapped_lang = lang_map.get(language, language)
                if mapped_lang:
                    decode_options["language"] = mapped_lang
                    logger.debug(f"使用指定语言: {decode_options['language']}")
                else:
                    logger.debug("使用自动语言检测")
            
            # 转录（使用更好的参数提高准确度）
            # 添加更多参数以提高准确度
            transcribe_kwargs = {
                "task": task,
                "verbose": False,
                "fp16": False,  # CPU模式不使用半精度
            }
            
            # 如果指定了语言，添加到参数中
            if decode_options.get("language"):
                transcribe_kwargs["language"] = decode_options["language"]
            
            # 使用更好的beam size和temperature参数
            transcribe_kwargs.update({
                "beam_size": 5,  # 增加beam size提高准确度
                "temperature": 0.0,  # 使用确定性采样（temperature=0）
                "best_of": 5,  # 生成多个候选，选择最好的
                "condition_on_previous_text": True,  # 使用上下文信息
            })
            
            result = self.model.transcribe(
                audio_file_path,
                **transcribe_kwargs
            )
            
            text = result.get("text", "").strip()
            detected_language = result.get("language", "unknown")
            
            logger.info(f"转录完成: 语言={detected_language}, 文本='{text[:50]}...', 文本长度={len(text)}")
            
            # 使用语言检测器进一步分析（区分普通话和粤语）
            if detected_language == "zh" and text:
                try:
                    from services.core.language_detector import get_language_detector
                    lang_detector = get_language_detector()
                    lang_info = lang_detector.detect(text)
                    
                    # 如果检测到粤语特征，标记为粤语
                    if lang_info.get("cantonese", 0) > 0.3:
                        detected_language = "yue"
                        logger.info(f"✅ 检测到粤语特征: 粤语占比={lang_info['cantonese']:.2f}, 文本='{text[:30]}...'")
                    elif lang_info.get("english", 0) > 0.3 and lang_info.get("mixed", 0) > 0.3:
                        detected_language = "mixed"
                        logger.info(f"✅ 检测到混合语言: 英语占比={lang_info['english']:.2f}, 中文占比={lang_info['mandarin']:.2f}")
                except Exception as e:
                    logger.debug(f"语言检测器分析失败: {e}，使用Whisper检测结果")
            
            return {
                "text": text,
                "language": detected_language,
                "segments": result.get("segments", []),
                "confidence": self._calculate_confidence(result)
            }
            
        except Exception as e:
            logger.error(f"音频转录失败: {e}")
            return {
                "error": str(e),
                "text": "",
                "language": None
            }
    
    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        audio_format: str = "wav",
        language: Optional[str] = None
    ) -> Dict:
        """
        将音频字节流转换为文本
        
        Args:
            audio_bytes: 音频文件的字节数据
            audio_format: 音频格式（wav, mp3, m4a, webm等）
            language: 指定语言（可选）
                - "zh": 中文（推荐，提高中文识别准确度）
                - "en": 英语
                - "yue": 粤语（将使用粤语专用API）
                - None: 自动检测（可能不准确）
            
        Returns:
            包含text、language等信息的字典
        """
        # 如果指定了粤语，且粤语API可用，优先使用粤语专用API
        if language in ["yue", "zh-HK"] and settings.USE_CANTONESE_API:
            try:
                from services.speech.cantonese_stt import get_cantonese_stt
                cantonese_stt = get_cantonese_stt()
                
                if cantonese_stt and cantonese_stt.is_available():
                    logger.info("🎤 使用粤语专用API进行识别")
                    result = cantonese_stt.transcribe_bytes(
                        audio_bytes, 
                        audio_format=audio_format,
                        language="yue"
                    )
                    
                    # 如果粤语API成功，直接返回结果
                    if result.get("text") and not result.get("error"):
                        logger.info(f"✅ 粤语API识别成功: '{result['text'][:50]}...'")
                        return result
                    else:
                        logger.warning(f"粤语API识别失败，降级到Whisper: {result.get('error', 'Unknown error')}")
            except Exception as e:
                logger.warning(f"粤语API调用失败，降级到Whisper: {e}")
        
        if not self.model:
            return {
                "error": "Whisper模型未加载",
                "text": "",
                "language": None
            }
        
        try:
            # WebM格式需要转换为WAV（Whisper对WAV支持最好）
            if audio_format.lower() == "webm":
                logger.info("检测到WebM格式，转换为WAV以提高识别准确度")
                try:
                    import pydub
                    from pydub import AudioSegment
                    from io import BytesIO
                    
                    # 使用pydub转换WebM到WAV
                    audio_segment = AudioSegment.from_file(
                        BytesIO(audio_bytes),
                        format="webm"
                    )
                    
                    # 音频预处理以提高识别准确度
                    # 1. 标准化音量（避免音量过小或过大）
                    if audio_segment.max_possible_amplitude > 0:
                        target_dBFS = -20.0  # 目标音量（-20dBFS比较合适）
                        change_in_dBFS = target_dBFS - audio_segment.dBFS
                        audio_segment = audio_segment.apply_gain(change_in_dBFS)
                    
                    # 2. 转换为16kHz单声道（Whisper推荐格式）
                    audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
                    
                    # 3. 标准化采样宽度（16位）
                    audio_segment = audio_segment.set_sample_width(2)
                    
                    # 4. 简单的降噪（高通滤波，去除低频噪音）
                    # 注意：pydub的简单滤波可能不够，但可以略微改善
                    # audio_segment = audio_segment.high_pass_filter(80)  # 可选
                    
                    wav_buffer = BytesIO()
                    audio_segment.export(wav_buffer, format="wav", parameters=["-ac", "1", "-ar", "16000"])
                    audio_bytes = wav_buffer.getvalue()
                    audio_format = "wav"
                    logger.info("WebM已转换为WAV格式（16kHz单声道，已优化音量）")
                except ImportError:
                    logger.warning("pydub未安装，无法转换WebM格式，可能影响识别准确度")
                    logger.info("安装命令: pip install pydub")
                except Exception as e:
                    logger.warning(f"WebM转换失败: {e}，使用原始格式")
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(
                suffix=f".{audio_format}",
                delete=False
            ) as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name
            
            # 可选：使用Silero VAD提取语音片段（去除静音，提高识别准确度）
            use_vad = os.getenv("USE_SILERO_VAD", "true").lower() == "true"
            vad_tmp_path = None
            if use_vad:
                try:
                    from services.speech.vad_silero import get_silero_vad
                    import soundfile as sf
                    
                    vad = get_silero_vad()
                    if vad and vad.model is not None:
                        logger.info("使用Silero VAD提取语音片段（去除静音）...")
                        
                        try:
                            # 读取音频数据
                            audio_array, sample_rate = sf.read(tmp_path)
                            
                            # 提取语音片段
                            speech_audio = vad.extract_speech_audio(audio_array, sample_rate)
                            
                            if speech_audio is not None and len(speech_audio) > 0:
                                # 保存提取的语音片段
                                vad_tmp_path = tmp_path.replace(f".{audio_format}", "_vad.wav")
                                sf.write(vad_tmp_path, speech_audio, sample_rate)
                                tmp_path = vad_tmp_path
                                logger.info(f"✅ Silero VAD已提取语音片段：原始={len(audio_array)/sample_rate:.2f}s，语音={len(speech_audio)/sample_rate:.2f}s")
                            else:
                                logger.warning("Silero VAD未检测到语音，使用原始音频")
                        except Exception as e:
                            logger.warning(f"Silero VAD处理失败: {e}，使用原始音频")
                except ImportError:
                    logger.debug("Silero VAD未安装，跳过VAD处理（这是正常的）")
                except Exception as e:
                    logger.debug(f"Silero VAD不可用: {e}，使用原始音频")
            
            # 转录（如果未指定语言，使用自动检测以支持多语言）
            if language is None:
                # 使用自动检测，支持中文、粤语、英语混合识别
                logger.debug("使用自动语言检测（支持中文、粤语、英语）")
                language = None  # 保持None，让Whisper自动检测
            elif language == "auto":
                language = None  # "auto"也使用自动检测
            else:
                # 映射语言代码
                lang_map = {
                    "zh": "zh",  # 中文（普通话）
                    "zh-CN": "zh",
                    "zh-HK": "zh",  # 粤语（Whisper用zh表示）
                    "yue": "zh",
                    "en": "en",  # 英语
                }
                language = lang_map.get(language, language)
                logger.debug(f"使用指定语言: {language}")
            
            result = self.transcribe(tmp_path, language=language)
            
            # 如果Whisper检测到粤语，且粤语API可用，尝试使用粤语API重新识别
            if (result.get("language") == "yue" or 
                (result.get("language") == "zh" and language is None)) and \
                settings.USE_CANTONESE_API:
                try:
                    # 检查是否可能是粤语
                    text = result.get("text", "")
                    if text:  # 有文本才尝试
                        from services.core.language_detector import get_language_detector
                        lang_detector = get_language_detector()
                        lang_info = lang_detector.detect(text)
                        
                        # 如果检测到粤语特征，使用粤语API重新识别
                        if lang_info.get("cantonese", 0) > 0.3:
                            logger.info(f"🔍 检测到粤语特征({lang_info['cantonese']:.2f})，尝试使用粤语专用API重新识别")
                            
                            from services.speech.cantonese_stt import get_cantonese_stt
                            cantonese_stt = get_cantonese_stt()
                            
                            if cantonese_stt and cantonese_stt.is_available():
                                # 使用临时文件路径重新识别
                                cantonese_result = cantonese_stt.transcribe(tmp_path, language="yue")
                                
                                # 如果粤语API成功且返回了文本，使用粤语API的结果
                                if cantonese_result.get("text") and not cantonese_result.get("error"):
                                    logger.info(f"✅ 粤语API重新识别成功: '{cantonese_result['text'][:50]}...'")
                                    result = cantonese_result
                                else:
                                    logger.debug("粤语API未返回结果，保持Whisper结果")
                except Exception as e:
                    logger.debug(f"粤语API重新识别失败，保持Whisper结果: {e}")
            
            # 清理临时文件
            try:
                if vad_tmp_path and os.path.exists(vad_tmp_path):
                    os.unlink(vad_tmp_path)  # 删除VAD处理后的文件
                if tmp_path and os.path.exists(tmp_path) and tmp_path != vad_tmp_path:
                    os.unlink(tmp_path)  # 删除原始临时文件
            except Exception as e:
                logger.debug(f"清理临时文件失败: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"音频字节流转录失败: {e}")
            return {
                "error": str(e),
                "text": "",
                "language": None
            }
    
    def _calculate_confidence(self, result: Dict) -> float:
        """计算转录置信度"""
        segments = result.get("segments", [])
        if not segments:
            return 0.0
        
        # 简单的置信度计算（基于段落的平均概率）
        total_confidence = 0.0
        count = 0
        
        for segment in segments:
            # Whisper可能不直接提供置信度，这里使用简单估计
            if "no_speech_prob" in segment:
                confidence = 1.0 - segment["no_speech_prob"]
                total_confidence += confidence
                count += 1
        
        return total_confidence / count if count > 0 else 0.8
    
    def is_available(self) -> bool:
        """检查STT是否可用"""
        return self.model is not None


# 全局STT实例（按模型大小缓存）
_whisper_stt_cache = {}


def get_whisper_stt(model_size: str = "base") -> Optional[WhisperSTT]:
    """
    获取Whisper STT实例（支持多模型缓存）
    
    Args:
        model_size: 模型大小 (tiny/base/small/medium/large)
        
    Returns:
        WhisperSTT实例或None
    """
    global _whisper_stt_cache
    
    # 如果已缓存该模型，直接返回
    if model_size in _whisper_stt_cache:
        stt = _whisper_stt_cache[model_size]
        if stt and stt.is_available():
            return stt
    
    # 创建新实例
    if WHISPER_AVAILABLE:
        logger.info(f"创建新的Whisper STT实例: {model_size}")
        stt = WhisperSTT(model_size=model_size)
        _whisper_stt_cache[model_size] = stt
        return stt
    else:
        logger.warning("Whisper未安装，无法创建STT实例")
        return None


def reload_whisper_model(model_size: str = "base"):
    """
    重新加载Whisper模型（切换模型时使用）
    
    Args:
        model_size: 新的模型大小
    """
    global _whisper_stt_cache
    if model_size in _whisper_stt_cache:
        del _whisper_stt_cache[model_size]
    logger.info(f"已清除模型缓存: {model_size}，下次使用时将重新加载")

