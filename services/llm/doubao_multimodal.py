#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
豆包（Doubao）多模态客户端
支持文本+图片的混合输入
"""
import base64
import requests
from typing import List, Dict, Optional, Any
from services.core import settings, logger


class DoubaoMultimodalClient:
    """
    豆包多模态客户端
    
    功能：
    1. 支持多张图片+文本输入
    2. 推理模型（seed系列）
    3. 中国大陆友好
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "doubao-seed-1-6-251015"  # 使用完整版，视觉理解更强
    ):
        """
        初始化豆包客户端
        
        Args:
            api_key: ARK API密钥
            model: 模型名称
        """
        self.api_key = api_key or getattr(settings, 'DOUBAO_API_KEY', None)
        if not self.api_key:
            raise ValueError("Doubao API Key未配置")
        
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3"
        self.model = model
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        logger.info(f"✅ 豆包多模态客户端已初始化，模型: {model}")
    
    def _prepare_image_content(self, image_data: str) -> Dict[str, Any]:
        """
        准备图片内容
        
        Args:
            image_data: Base64编码的图片或URL
            
        Returns:
            图片内容字典
        """
        # 判断是URL还是Base64
        if image_data.startswith('http://') or image_data.startswith('https://'):
            return {
                "type": "image_url",
                "image_url": {
                    "url": image_data
                }
            }
        else:
            # Base64图片，需要转换为data URL
            if not image_data.startswith('data:'):
                # 添加data URL前缀
                image_data = f"data:image/jpeg;base64,{image_data}"
            
            return {
                "type": "image_url",
                "image_url": {
                    "url": image_data
                }
            }
    
    def query_with_images(
        self,
        query: str,
        images: List[str],
        max_tokens: int = 2048,
        reasoning_effort: str = "medium",
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        使用图片+文本进行查询
        
        Args:
            query: 文本查询
            images: Base64编码的图片列表或URL列表
            max_tokens: 最大生成token数
            reasoning_effort: 推理强度 (low/medium/high)
            temperature: 温度参数
            
        Returns:
            {
                "content": "生成的答案",
                "model": "模型名称",
                "usage": {
                    "prompt_tokens": 输入token数,
                    "completion_tokens": 输出token数,
                    "total_tokens": 总token数
                },
                "images_processed": 处理的图片数量
            }
        """
        try:
            # 构建消息内容
            content = []
            
            # 添加图片
            for i, img_data in enumerate(images):
                try:
                    image_content = self._prepare_image_content(img_data)
                    content.append(image_content)
                    logger.info(f"✅ 图片 {i+1}/{len(images)} 已准备就绪")
                except Exception as e:
                    logger.error(f"❌ 图片 {i+1} 处理失败: {e}")
                    continue
            
            # 添加文本
            content.append({
                "type": "text",
                "text": query
            })
            
            if len(content) == 1:  # 只有文本，没有成功的图片
                return {"error": "所有图片处理失败"}
            
            # 构建请求
            payload = {
                "model": self.model,
                "max_completion_tokens": max_tokens,
                "reasoning_effort": reasoning_effort,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            }
            
            logger.info(f"🖼️ 开始豆包多模态查询: {len(images)}张图片 + 文本")
            logger.info(f"📌 使用模型: {self.model}")
            logger.info(f"📌 请求payload中的模型: {payload['model']}")
            
            # 调用API（带重试机制）
            max_retries = 3
            retry_delay = 2
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"🔄 尝试 {attempt + 1}/{max_retries}")
                    response = requests.post(
                        f"{self.base_url}/chat/completions",
                        headers=self.headers,
                        json=payload,
                        timeout=60
                    )
                    break  # 成功则跳出重试循环
                except (requests.exceptions.SSLError, 
                        requests.exceptions.ConnectionError,
                        requests.exceptions.ProxyError) as e:
                    last_error = e
                    logger.warning(f"⚠️  网络错误（尝试 {attempt + 1}/{max_retries}）: {type(e).__name__}")
                    if attempt < max_retries - 1:
                        import time
                        logger.info(f"等待 {retry_delay} 秒后重试...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                    else:
                        logger.error(f"❌ 重试{max_retries}次后仍失败")
                        return {"error": f"网络错误（已重试{max_retries}次）: {str(last_error)}"}
            
            response.raise_for_status()
            data = response.json()
            
            # 提取结果
            if "choices" not in data or not data["choices"]:
                return {"error": "API返回格式错误"}
            
            answer = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            
            result = {
                "content": answer,
                "model": self.model,
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                },
                "images_processed": len(images)
            }
            
            logger.info(f"✅ 豆包多模态查询成功，处理{len(images)}张图片，token使用: {result['usage']['total_tokens']}")
            return result
            
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            try:
                error_data = e.response.json()
                error_msg = error_data.get("error", {}).get("message", str(e))
            except:
                pass
            
            logger.error(f"❌ 豆包API错误: {error_msg}")
            return {"error": f"豆包API错误: {error_msg}"}
        except Exception as e:
            logger.error(f"❌ 豆包多模态查询失败: {e}")
            return {"error": f"查询失败: {str(e)}"}
    
    def extract_text_from_image(self, image_data: str) -> Dict[str, Any]:
        """
        从图片中提取文字（OCR）
        
        Args:
            image_data: Base64编码的图片或URL
            
        Returns:
            {
                "text": "识别出的文本",
                "confidence": 置信度,
                "model": "模型名称"
            }
        """
        ocr_prompt = """请提取图片中的所有文字。
要求：
1. 保持原有的排版结构和换行
2. 如果有表格，请用Markdown格式表示
3. 如果有多种语言，请全部提取
4. 只输出文字内容，不要添加任何解释或描述

提取的文字："""
        
        result = self.query_with_images(
            query=ocr_prompt,
            images=[image_data],
            reasoning_effort="low"  # OCR不需要高推理
        )
        
        if "error" in result:
            return {
                "error": result["error"],
                "text": "",
                "confidence": 0.0
            }
        
        return {
            "text": result["content"],
            "confidence": 0.95,  # 豆包不提供置信度，使用固定值
            "model": self.model,
            "language": "auto"
        }
    
    def analyze_image(self, image_data: str, analysis_prompt: str = None) -> Dict[str, Any]:
        """
        分析图片内容
        
        Args:
            image_data: Base64编码的图片或URL
            analysis_prompt: 自定义分析提示
            
        Returns:
            {
                "description": "图片描述",
                "model": "模型名称"
            }
        """
        if not analysis_prompt:
            analysis_prompt = "请详细描述这张图片的内容，包括主要对象、场景、颜色和整体氛围。"
        
        result = self.query_with_images(
            query=analysis_prompt,
            images=[image_data],
            reasoning_effort="medium"
        )
        
        if "error" in result:
            return {
                "error": result["error"],
                "description": ""
            }
        
        return {
            "description": result["content"],
            "model": self.model
        }


# 全局单例字典（按模型缓存）
_doubao_clients = {}

def get_doubao_client(model: str = None) -> DoubaoMultimodalClient:
    """
    获取豆包客户端（支持多模型）
    
    Args:
        model: 模型名称，如果为None则使用默认模型
    """
    global _doubao_clients
    
    # 确定使用的模型
    if model is None:
        model = getattr(settings, 'DOUBAO_DEFAULT_MODEL', 'doubao-seed-1-6-251015')
    
    # 如果该模型的客户端不存在，创建新的
    if model not in _doubao_clients:
        _doubao_clients[model] = DoubaoMultimodalClient(model=model)
    
    return _doubao_clients[model]

