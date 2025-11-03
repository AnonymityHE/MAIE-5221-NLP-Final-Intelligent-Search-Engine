"""
实时语音交互 - WebSocket支持
用于实现类似"Hey Siri"的实时语音交互
"""
from fastapi import WebSocket, WebSocketDisconnect
from services.core.logger import logger
from services.speech.voice_service import get_voice_service
from services.agent import agent
from services.core.config import settings
import json
import asyncio
from typing import Optional


class VoiceWebSocketHandler:
    """WebSocket语音交互处理器"""
    
    def __init__(self):
        self.voice_service = None
        self.active_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"客户端 {client_id} 已连接（语音WebSocket）")
        
        if self.voice_service is None:
            self.voice_service = get_voice_service()
    
    def disconnect(self, client_id: str):
        """断开WebSocket连接"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"客户端 {client_id} 已断开连接")
    
    async def send_message(self, client_id: str, message: dict):
        """发送消息到客户端"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败 ({client_id}): {e}")
                self.disconnect(client_id)
    
    async def handle_audio_chunk(self, client_id: str, audio_data: bytes, is_final: bool = False, audio_format: str = "wav"):
        """
        处理音频数据块
        
        Args:
            client_id: 客户端ID
            audio_data: 音频数据（base64编码或字节）
            is_final: 是否为最后一个数据块
            audio_format: 音频格式（wav/webm/mp3等）
        """
        try:
            logger.info(f"收到音频数据块 (client_id={client_id}, is_final={is_final}, format={audio_format}, data_size={len(audio_data) if isinstance(audio_data, (bytes, str)) else 'unknown'})")
            
            # 这里可以实现流式音频处理
            # 当前实现：累积音频数据，当is_final=True时处理
            # 实际应用中可以使用流式Whisper或其他实时处理方案
            
            if is_final:
                # 处理完整的音频
                logger.info(f"开始处理完整音频 (client_id={client_id})")
                result = await self._process_audio(audio_data, audio_format)
                logger.info(f"音频处理完成 (client_id={client_id}, result_type={result.get('type')})")
                await self.send_message(client_id, result)
            else:
                logger.debug(f"收到非最终音频块，等待更多数据 (client_id={client_id})")
        except Exception as e:
            logger.error(f"处理音频数据失败 (client_id={client_id}): {e}", exc_info=True)
            await self.send_message(client_id, {
                "type": "error",
                "message": f"处理音频失败: {str(e)}"
            })
    
    async def _process_audio(self, audio_data: bytes, audio_format: str = "wav") -> dict:
        """处理音频并返回结果"""
        try:
            logger.info(f"开始处理音频 (format={audio_format})")
            
            # 将音频数据转换为文本
            if not self.voice_service:
                logger.info("初始化VoiceService")
                self.voice_service = get_voice_service()
            
            # 假设音频数据是base64编码的，需要解码
            import base64
            if isinstance(audio_data, str):
                logger.info(f"解码base64音频数据 (长度: {len(audio_data)})")
                audio_bytes = base64.b64decode(audio_data)
            else:
                audio_bytes = audio_data
            
            logger.info(f"音频数据大小: {len(audio_bytes)} bytes")
            
            # 语音转文本（使用自动语言检测，支持中文、粤语、英语）
            logger.info("开始语音转文本...")
            transcription_result = self.voice_service.transcribe_audio(
                audio_bytes=audio_bytes,
                audio_format=audio_format,
                language=None  # None表示自动检测，支持中文、粤语、英语混合识别
            )
            logger.info(f"语音转文本完成: {transcription_result}")
            
            if "error" in transcription_result:
                return {
                    "type": "transcription_error",
                    "error": transcription_result["error"]
                }
            
            transcribed_text = transcription_result.get("text", "").strip()
            detected_language = transcription_result.get("language", "unknown")
            
            # 检测唤醒词
            wake_word_detected, query_text = self.voice_service.detect_and_extract_query(
                transcribed_text=transcribed_text,
                use_wake_word=True
            )
            
            logger.info(f"语音处理: 唤醒词检测={wake_word_detected}, 查询文本='{query_text}'")
            
            # 如果检测到唤醒词，处理查询
            answer = None
            tools_used = []
            if wake_word_detected:
                # 如果query_text为空，使用完整转录文本
                if not query_text or query_text.strip() == "":
                    query_text = transcribed_text
                    logger.info(f"查询文本为空，使用完整转录文本: '{query_text}'")
                
                if query_text:
                    try:
                        logger.info(f"开始执行Agent查询: '{query_text}'")
                        agent_result = agent.execute(query_text, model=None)
                        answer = agent_result.get("answer", "")
                        tools_used = agent_result.get("tools_used", [])
                        logger.info(f"Agent查询完成，答案长度: {len(answer) if answer else 0}")
                    except Exception as e:
                        logger.error(f"Agent执行失败: {e}")
                        answer = f"处理查询时出错: {str(e)}"
            else:
                # 即使没有检测到唤醒词，也可以尝试直接回答
                if transcribed_text:
                    logger.info(f"未检测到唤醒词，但尝试直接回答: '{transcribed_text}'")
                    try:
                        agent_result = agent.execute(transcribed_text, model=None)
                        answer = agent_result.get("answer", "")
                        tools_used = agent_result.get("tools_used", [])
                    except Exception as e:
                        logger.error(f"直接查询失败: {e}")
            
            return {
                "type": "response",
                "transcribed_text": transcribed_text,
                "detected_language": detected_language,
                "wake_word_detected": wake_word_detected,
                "query_text": query_text or "",
                "answer": answer or "",
                "tools_used": tools_used
            }
            
        except Exception as e:
            logger.error(f"处理音频失败: {e}")
            return {
                "type": "error",
                "message": str(e)
            }


# 全局WebSocket处理器
_voice_ws_handler = VoiceWebSocketHandler()


def get_voice_ws_handler() -> VoiceWebSocketHandler:
    """获取WebSocket处理器实例"""
    return _voice_ws_handler
