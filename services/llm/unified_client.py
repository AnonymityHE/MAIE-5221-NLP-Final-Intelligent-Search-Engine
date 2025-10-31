"""
统一LLM客户端 - 支持HKGAI和Gemini，根据配置选择
"""
from typing import Dict, Optional
from services.core.config import settings
from services.llm.hkgai_client import HKGAIClient
from services.llm.gemini_client import GeminiClient


class UnifiedLLMClient:
    """统一的LLM客户端，支持多个API提供商"""
    
    def __init__(self):
        # 初始化HKGAI客户端（向后兼容）
        self.hkgai_client = HKGAIClient()
        
        # 初始化Gemini客户端（如果启用）
        if settings.GEMINI_ENABLED and settings.GEMINI_API_KEY:
            self.gemini_client = GeminiClient(settings.GEMINI_API_KEY)
        else:
            self.gemini_client = None
    
    def chat(self, system_prompt: str, user_prompt: str,
             max_tokens: int = 2048,
             temperature: float = 0.7,
             model: Optional[str] = None,
             provider: str = "hkgai") -> Dict:
        """
        发送聊天请求
        
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
        if provider.lower() == "gemini" and self.gemini_client:
            # 使用Gemini API
            return self.gemini_client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=model or settings.GEMINI_DEFAULT_MODEL,
                max_tokens=max_tokens,
                temperature=temperature
            )
        else:
            # 使用HKGAI API（向后兼容）
            return self.hkgai_client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
    
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

