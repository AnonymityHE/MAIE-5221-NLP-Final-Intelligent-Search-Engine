"""
统一LLM客户端 - 支持HKGAI和Gemini，自动fallback机制
"""
from typing import Dict, Optional
from services.core.config import settings
from services.llm.hkgai_client import HKGAIClient
from services.llm.gemini_client import GeminiClient
from services.core.logger import logger


class UnifiedLLMClient:
    """统一的LLM客户端，支持多个API提供商，带自动fallback"""
    
    def __init__(self):
        # 初始化HKGAI客户端（向后兼容）
        self.hkgai_client = HKGAIClient()
        
        # 初始化Gemini客户端（如果启用）
        if settings.GEMINI_ENABLED and settings.GEMINI_API_KEY:
            self.gemini_client = GeminiClient(settings.GEMINI_API_KEY)
            logger.info("✅ Gemini客户端已初始化，可作为fallback")
        else:
            self.gemini_client = None
            logger.warning("⚠️  Gemini客户端未配置，无fallback选项")
        
        # 记录HKGAI失败次数（用于智能fallback）
        self.hkgai_failure_count = 0
    
    def chat(self, system_prompt: str, user_prompt: str,
             max_tokens: int = 2048,
             temperature: float = 0.7,
             model: Optional[str] = None,
             provider: str = "hkgai") -> Dict:
        """
        发送聊天请求（带自动fallback）
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            max_tokens: 最大生成token数
            temperature: 温度参数
            model: 模型名称（仅Gemini使用）
            provider: API提供商 ("gemini" 或 "hkgai")
            
        Returns:
            包含content、token使用量等信息的字典
        """
        # 如果明确指定使用Gemini
        if provider.lower() == "gemini" and self.gemini_client:
            return self._call_gemini(system_prompt, user_prompt, model, max_tokens, temperature)
        
        # 如果HKGAI连续失败多次，直接使用Gemini
        if self.hkgai_failure_count >= 3 and self.gemini_client:
            logger.warning(f"⚠️  HKGAI已连续失败{self.hkgai_failure_count}次，直接使用Gemini")
            return self._call_gemini(system_prompt, user_prompt, model, max_tokens, temperature)
        
        # 尝试使用HKGAI
        try:
            result = self.hkgai_client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # 检查是否有错误
            if "error" in result:
                self.hkgai_failure_count += 1
                logger.warning(f"⚠️  HKGAI调用失败 (失败计数: {self.hkgai_failure_count})")
                
                # 自动fallback到Gemini
                if self.gemini_client:
                    logger.info("🔄 自动切换到Gemini API")
                    return self._call_gemini(system_prompt, user_prompt, model, max_tokens, temperature)
                else:
                    logger.error("❌ 没有可用的fallback API")
                    return result
            else:
                # 成功，重置失败计数
                if self.hkgai_failure_count > 0:
                    logger.info(f"✅ HKGAI恢复正常，重置失败计数（之前: {self.hkgai_failure_count}）")
                    self.hkgai_failure_count = 0
                result["provider"] = "hkgai"
                return result
                
        except Exception as e:
            self.hkgai_failure_count += 1
            logger.error(f"❌ HKGAI异常: {e} (失败计数: {self.hkgai_failure_count})")
            
            # 自动fallback到Gemini
            if self.gemini_client:
                logger.info("🔄 自动切换到Gemini API")
                return self._call_gemini(system_prompt, user_prompt, model, max_tokens, temperature)
            else:
                return {"error": str(e), "provider": "hkgai"}
    
    def _call_gemini(self, system_prompt: str, user_prompt: str, 
                     model: Optional[str], max_tokens: int, temperature: float) -> Dict:
        """调用Gemini API"""
        try:
            result = self.gemini_client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=model or settings.GEMINI_DEFAULT_MODEL,
                max_tokens=max_tokens,
                temperature=temperature
            )
            result["provider"] = "gemini"
            return result
        except Exception as e:
            logger.error(f"❌ Gemini API调用也失败: {e}")
            return {"error": str(e), "provider": "gemini"}
    
    def get_supported_models(self) -> Dict:
        """获取支持的模型列表"""
        result = {
            "default_provider": "hkgai",
            "providers": ["hkgai"],
            "hkgai_models": [settings.HKGAI_MODEL_ID],
            "hkgai_info": {
                "model": settings.HKGAI_MODEL_ID,
                "description": "默认LLM提供商，稳定可靠"
            }
        }
        
        if self.gemini_client:
            gemini_info = self.gemini_client.get_supported_models()
            result["providers"].append("gemini")
            result["gemini_models"] = gemini_info.get("supported_models", [])
            result["gemini_info"] = {
                "default_model": gemini_info.get("default_model"),
                "models": gemini_info.get("supported_models", []),
                "description": "备选LLM提供商，支持多个Gemini模型，带用量监控"
            }
        
        return result


# 全局统一客户端实例
unified_llm_client = UnifiedLLMClient()

