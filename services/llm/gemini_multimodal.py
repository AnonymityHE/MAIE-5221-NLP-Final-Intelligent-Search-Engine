#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gemini 多模态客户端
支持文本+图片的混合输入，适用于视觉问答、图片分析等场景
"""
import base64
import io
from typing import List, Dict, Optional, Union, Any
from PIL import Image
import google.generativeai as genai
from services.core import settings, logger


class GeminiMultimodalClient:
    """
    Gemini 多模态客户端
    
    功能：
    1. 支持多张图片+文本输入
    2. 图片格式转换和优化
    3. OCR文字识别
    4. 图片内容分析
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.0-flash-exp"):
        """
        初始化Gemini多模态客户端
        
        Args:
            api_key: Gemini API密钥
            model_name: 模型名称，默认使用gemini-2.0-flash-exp（支持最新多模态功能）
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("Gemini API密钥未配置")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
        # 支持的图片格式
        self.supported_formats = ['jpeg', 'jpg', 'png', 'gif', 'webp']
        
        logger.info(f"✅ Gemini多模态客户端已初始化，模型: {model_name}")
    
    def _decode_image(self, image_data: str) -> Image.Image:
        """
        解码Base64图片
        
        Args:
            image_data: Base64编码的图片数据
            
        Returns:
            PIL Image对象
        """
        try:
            # 移除data URL前缀（如果有）
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # 解码Base64
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            return image
        except Exception as e:
            logger.error(f"图片解码失败: {e}")
            raise ValueError(f"无效的图片数据: {e}")
    
    def _optimize_image(self, image: Image.Image, max_size: int = 1024) -> Image.Image:
        """
        优化图片大小（降低API成本）
        
        Args:
            image: PIL Image对象
            max_size: 最大边长
            
        Returns:
            优化后的图片
        """
        # 如果图片已经足够小，直接返回
        if max(image.size) <= max_size:
            return image
        
        # 计算缩放比例
        ratio = max_size / max(image.size)
        new_size = tuple(int(dim * ratio) for dim in image.size)
        
        # 缩放图片
        optimized = image.resize(new_size, Image.Resampling.LANCZOS)
        logger.info(f"图片已优化: {image.size} -> {optimized.size}")
        
        return optimized
    
    def _prepare_image_for_gemini(self, image_data: str, optimize: bool = True) -> Image.Image:
        """
        准备图片供Gemini使用
        
        Args:
            image_data: Base64编码的图片
            optimize: 是否优化图片大小
            
        Returns:
            准备好的PIL Image对象
        """
        image = self._decode_image(image_data)
        
        # 转换为RGB模式（Gemini要求）
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 优化图片大小
        if optimize:
            image = self._optimize_image(image)
        
        return image
    
    def query_with_images(
        self,
        query: str,
        images: List[str],
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        使用图片+文本进行查询
        
        Args:
            query: 文本查询
            images: Base64编码的图片列表
            system_prompt: 系统提示（可选）
            max_tokens: 最大生成token数
            temperature: 温度参数
            
        Returns:
            {
                "content": "生成的答案",
                "model": "模型名称",
                "input_tokens": 输入token数,
                "output_tokens": 输出token数,
                "total_tokens": 总token数,
                "images_processed": 处理的图片数量
            }
        """
        try:
            # 准备图片
            pil_images = []
            for i, img_data in enumerate(images):
                try:
                    pil_img = self._prepare_image_for_gemini(img_data)
                    pil_images.append(pil_img)
                    logger.info(f"✅ 图片 {i+1}/{len(images)} 已准备就绪")
                except Exception as e:
                    logger.error(f"❌ 图片 {i+1} 处理失败: {e}")
                    # 继续处理其他图片
                    continue
            
            if not pil_images:
                return {"error": "所有图片处理失败"}
            
            # 构建完整提示
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{query}"
            else:
                full_prompt = query
            
            # 构建内容列表：[图片1, 图片2, ..., 文本]
            content = pil_images + [full_prompt]
            
            # 生成配置
            generation_config = genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )
            
            logger.info(f"🖼️ 开始多模态查询: {len(pil_images)}张图片 + 文本")
            
            # 调用Gemini
            response = self.model.generate_content(
                content,
                generation_config=generation_config
            )
            
            # 提取结果
            answer = response.text
            
            # 提取token使用信息
            usage = response.usage_metadata
            result = {
                "content": answer,
                "model": self.model_name,
                "input_tokens": usage.prompt_token_count,
                "output_tokens": usage.candidates_token_count,
                "total_tokens": usage.total_token_count,
                "images_processed": len(pil_images)
            }
            
            logger.info(f"✅ 多模态查询成功，处理{len(pil_images)}张图片，token使用: {result['total_tokens']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Gemini多模态查询失败: {e}")
            return {"error": f"多模态查询失败: {str(e)}"}
    
    def extract_text_from_image(self, image_data: str) -> Dict[str, Any]:
        """
        从图片中提取文字（OCR）
        
        Args:
            image_data: Base64编码的图片
            
        Returns:
            {
                "text": "识别出的文本",
                "confidence": 置信度（0-1）,
                "model": "模型名称"
            }
        """
        try:
            # 准备图片
            pil_image = self._prepare_image_for_gemini(image_data)
            
            # 使用Gemini进行OCR
            prompt = """请提取图片中的所有文字。
要求：
1. 保持原有的排版结构和换行
2. 如果有表格，请用Markdown格式表示
3. 如果有多种语言，请全部提取
4. 只输出文字内容，不要添加任何解释或描述

提取的文字："""
            
            content = [pil_image, prompt]
            response = self.model.generate_content(content)
            
            extracted_text = response.text.strip()
            
            # Gemini不提供置信度，使用固定值
            confidence = 0.95 if len(extracted_text) > 0 else 0.0
            
            result = {
                "text": extracted_text,
                "confidence": confidence,
                "model": self.model_name,
                "language": "auto"  # Gemini自动检测语言
            }
            
            logger.info(f"✅ OCR成功，提取{len(extracted_text)}字符")
            return result
            
        except Exception as e:
            logger.error(f"❌ OCR失败: {e}")
            return {
                "error": f"OCR失败: {str(e)}",
                "text": "",
                "confidence": 0.0
            }
    
    def analyze_image(self, image_data: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        分析图片内容
        
        Args:
            image_data: Base64编码的图片
            analysis_type: 分析类型
                - general: 通用描述
                - detailed: 详细分析
                - objects: 物体识别
                - scene: 场景识别
                - sentiment: 情感分析
                
        Returns:
            {
                "description": "图片描述",
                "tags": ["标签1", "标签2"],
                "model": "模型名称"
            }
        """
        try:
            pil_image = self._prepare_image_for_gemini(image_data)
            
            # 根据分析类型构建提示
            prompts = {
                "general": "请简要描述这张图片的内容。",
                "detailed": "请详细描述这张图片，包括：1)主要对象 2)场景环境 3)颜色和光线 4)整体氛围",
                "objects": "请列出这张图片中的所有物体，用逗号分隔。",
                "scene": "请识别这张图片的场景类型（如：室内/室外、自然/城市、白天/夜晚等）",
                "sentiment": "请分析这张图片传达的情感或氛围。"
            }
            
            prompt = prompts.get(analysis_type, prompts["general"])
            
            content = [pil_image, prompt]
            response = self.model.generate_content(content)
            
            description = response.text.strip()
            
            # 简单提取标签（从描述中）
            tags = []
            if analysis_type == "objects":
                tags = [tag.strip() for tag in description.split(',')]
            
            result = {
                "description": description,
                "tags": tags,
                "analysis_type": analysis_type,
                "model": self.model_name
            }
            
            logger.info(f"✅ 图片分析成功，类型: {analysis_type}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 图片分析失败: {e}")
            return {
                "error": f"图片分析失败: {str(e)}",
                "description": "",
                "tags": []
            }


# 全局单例
_multimodal_client = None

def get_multimodal_client() -> GeminiMultimodalClient:
    """获取多模态客户端单例"""
    global _multimodal_client
    if _multimodal_client is None:
        _multimodal_client = GeminiMultimodalClient()
    return _multimodal_client

