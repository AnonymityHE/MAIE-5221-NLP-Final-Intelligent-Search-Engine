"""
LLM客户端 - 封装HKGAIClient
"""
import requests
from typing import Dict, Optional
from services.core.config import settings
from services.core.logger import logger


class HKGAIClient:
    """HKGAIClient包装类，用于调用LLM API"""
    
    def __init__(self):
        self.base_url = settings.HKGAI_BASE_URL
        self.api_key = settings.HKGAI_API_KEY
        self.model_id = settings.HKGAI_MODEL_ID
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def chat(self, system_prompt: str, user_prompt: str, 
             max_tokens: int = 500, temperature: float = 0.7) -> Dict:
        """
        发送聊天请求到LLM API
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            max_tokens: 最大生成token数
            temperature: 温度参数
            
        Returns:
            包含content和raw数据的字典
        """
        endpoint = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        logger.info(f"🔵 调用HKGAI API: {endpoint}")
        logger.debug(f"请求Payload: model={self.model_id}, max_tokens={max_tokens}, temperature={temperature}")
        logger.debug(f"用户提示: {user_prompt[:100]}...")
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            logger.info(f"✅ HKGAI API调用成功，状态码: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ HKGAI API调用失败: {e}")
            return {"error": str(e)}

        data = response.json()
        content = ""
        try:
            choices = data.get("choices", [])
            if choices:
                first = choices[0] if isinstance(choices[0], dict) else {}
                # Chat schema
                message = first.get("message") or {}
                content = (message.get("content") or "").strip()
                # Fallback to text-based schema
                if not content:
                    content = (first.get("text") or "").strip()
        except Exception:
            pass

        if not content:
            finish_reason = None
            try:
                finish_reason = data.get("choices", [{}])[0].get("finish_reason")
            except Exception:
                pass
            logger.warning(f"⚠️ HKGAI返回空内容，finish_reason: {finish_reason}")
            return {
                "content": "",
                "warning": "Empty content returned. Possible causes: wrong endpoint for model, content filter, or max_tokens too small.",
                "finish_reason": finish_reason,
                "raw": data
            }

        logger.info(f"✅ HKGAI返回内容长度: {len(content)} 字符")
        logger.debug(f"内容预览: {content[:100]}...")
        return {"content": content, "raw": data}


# 全局LLM客户端实例
llm_client = HKGAIClient()

