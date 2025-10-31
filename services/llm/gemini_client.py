"""
Gemini API客户端 - 支持多模型选择和用量监控
"""
import requests
from typing import Dict, Optional
import json
from services.llm.usage_monitor import usage_monitor


class GeminiClient:
    """Gemini API客户端"""
    
    # 支持的模型列表
    # Gemini API模型名称格式（根据Google AI Studio的实际模型）
    # 注意：如果模型不存在，API会返回错误，需要根据实际可用的模型调整
    SUPPORTED_MODELS = {
        "gemini-2.5-pro": "gemini-2.5-pro",
        "gemini-2.5-flash": "gemini-2.5-flash", 
        "gemini-2.0-flash": "gemini-2.0-flash-exp"  # 2.0 Flash可能使用exp版本
    }
    
    DEFAULT_MODEL = "gemini-2.0-flash-exp"  # 默认使用2.0 Flash实验版
    
    def __init__(self, api_key: str):
        self.api_key = api_key.strip()  # 去除可能的空白字符
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        # 验证API key格式（Google API key必须以AIza开头）
        if not self.api_key.startswith("AIza"):
            from services.core.logger import logger
            logger.warning(f"API Key格式可能不正确。Google API Key必须以'AIza'开头，当前: {self.api_key[:10]}...")
    
    def _count_tokens(self, text: str) -> int:
        """
        估算token数量（简化版本）
        注意：实际应该使用Gemini的countTokens API，这里用简单估算
        """
        # 简单估算：大约4个字符=1个token（中文更少，英文更多）
        # 这是一个粗略估计，实际应该调用API
        return len(text) // 4 + len(text) // 10  # 混合估算
    
    def chat(self, system_prompt: str, user_prompt: str,
             model: Optional[str] = None,
             max_tokens: int = 2048,
             temperature: float = 0.7) -> Dict:
        """
        发送聊天请求到Gemini API
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            model: 模型名称，如果为None则使用默认模型
            max_tokens: 最大生成token数
            temperature: 温度参数
            
        Returns:
            包含content、token使用量等信息的字典
        """
        # 选择模型（用户指定的模型名称，用于配额跟踪）
        user_model_name = model or "gemini-2.0-flash"  # 标准化名称
        if user_model_name not in self.SUPPORTED_MODELS:
            user_model_name = "gemini-2.0-flash"
        
        # 映射到实际API模型名称
        api_model_name = self.SUPPORTED_MODELS[user_model_name]
        model_name_for_quota = user_model_name  # 用于配额跟踪
        
        # 检查配额
        quota_check = usage_monitor.check_quota(model_name_for_quota)
        if not quota_check["available"]:
            return {
                "error": f"模型 {model_name_for_quota} 今日配额已用完",
                "quota_info": quota_check
            }
        
        # 构建请求
        full_prompt = f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt
        
        # 估算输入token
        estimated_input_tokens = self._count_tokens(full_prompt)
        
        # Gemini API可以使用query参数或header传递API key
        # 优先使用query参数方式
        url = f"{self.base_url}/models/{api_model_name}:generateContent"
        
        # 同时设置headers（某些情况下可能需要）
        headers = {
            "Content-Type": "application/json"
        }
        
        # API key通过query参数传递
        params = {
            "key": self.api_key
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": full_prompt
                }]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, params=params, timeout=30)
            
            # 如果响应不成功，尝试提取错误信息
            if not response.ok:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", f"HTTP {response.status_code}")
                    return {
                        "error": f"Gemini API错误: {error_msg}",
                        "status_code": response.status_code,
                        "model": model_name_for_quota,
                        "api_model_tried": api_model_name,
                        "raw_error": error_data
                    }
                except:
                    return {
                        "error": f"Gemini API错误: HTTP {response.status_code} - {response.text[:200]}",
                        "status_code": response.status_code,
                        "model": model_name_for_quota,
                        "api_model_tried": api_model_name
                    }
            
            response.raise_for_status()
            data = response.json()
            
            # 提取响应内容
            content = ""
            if "candidates" in data and len(data["candidates"]) > 0:
                if "content" in data["candidates"][0]:
                    if "parts" in data["candidates"][0]["content"]:
                        for part in data["candidates"][0]["content"]["parts"]:
                            if "text" in part:
                                content += part["text"]
            
            # 提取token使用量
            input_tokens = data.get("usageMetadata", {}).get("promptTokenCount", estimated_input_tokens)
            output_tokens = data.get("usageMetadata", {}).get("candidatesTokenCount", self._count_tokens(content))
            
            # 记录使用量（使用标准化的模型名称）
            usage_monitor.record_usage(model_name_for_quota, input_tokens, output_tokens)
            
            if not content:
                return {
                    "content": "",
                    "warning": "Empty content returned from Gemini API",
                    "raw": data
                }
            
            return {
                "content": content.strip(),
                "model": model_name_for_quota,  # 返回用户指定的模型名称
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "raw": data
            }
            
        except requests.exceptions.HTTPError as e:
            # HTTP错误，尝试解析响应
            try:
                error_data = e.response.json() if hasattr(e, 'response') else {}
                error_msg = error_data.get("error", {}).get("message", str(e))
            except:
                error_msg = str(e)
            return {
                "error": f"Gemini API HTTP错误: {error_msg}",
                "status_code": e.response.status_code if hasattr(e, 'response') else None,
                "model": model_name_for_quota,
                "raw_error": str(e)
            }
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Gemini API请求失败: {str(e)}",
                "model": model_name_for_quota,
                "raw_error": str(e)
            }
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return {
                "error": f"Gemini API处理错误: {str(e)}",
                "model": model_name_for_quota,
                "traceback": error_trace
            }
    
    def get_supported_models(self) -> Dict:
        """获取支持的模型列表"""
        return {
            "supported_models": list(self.SUPPORTED_MODELS.keys()),
            "default_model": self.DEFAULT_MODEL
        }


# 注意：这个实例需要在config中初始化，暂时不创建全局实例

