#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图片预处理服务
提供图片格式转换、压缩、OCR等功能
"""
import base64
import io
import hashlib
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ImageEnhance
from services.core import logger


class ImageProcessor:
    """
    图片处理器
    
    功能：
    1. 格式转换和验证
    2. 图片压缩和优化
    3. 图片增强（对比度、锐化等）
    4. 生成图片哈希（去重）
    """
    
    def __init__(self):
        self.supported_formats = ['JPEG', 'PNG', 'GIF', 'WEBP', 'BMP']
        self.max_size = 10 * 1024 * 1024  # 10MB
        self.default_quality = 85
        
    def decode_base64_image(self, image_data: str) -> Image.Image:
        """
        解码Base64图片
        
        Args:
            image_data: Base64编码的图片（可能包含data URL前缀）
            
        Returns:
            PIL Image对象
            
        Raises:
            ValueError: 图片数据无效
        """
        try:
            # 移除data URL前缀
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            
            # 解码Base64
            image_bytes = base64.b64decode(image_data)
            
            # 检查大小
            if len(image_bytes) > self.max_size:
                raise ValueError(f"图片大小超过限制 ({len(image_bytes)} bytes > {self.max_size} bytes)")
            
            # 打开图片
            image = Image.open(io.BytesIO(image_bytes))
            
            # 验证格式
            if image.format not in self.supported_formats:
                logger.warning(f"不支持的图片格式: {image.format}，尝试转换...")
            
            return image
            
        except Exception as e:
            logger.error(f"图片解码失败: {e}")
            raise ValueError(f"无效的图片数据: {e}")
    
    def encode_image_to_base64(
        self, 
        image: Image.Image, 
        format: str = 'JPEG',
        quality: int = None
    ) -> str:
        """
        将PIL Image编码为Base64
        
        Args:
            image: PIL Image对象
            format: 输出格式
            quality: 质量（1-100）
            
        Returns:
            Base64编码的字符串
        """
        try:
            buffer = io.BytesIO()
            
            # 转换为RGB（JPEG不支持透明通道）
            if format.upper() == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # 保存到缓冲区
            save_kwargs = {'format': format}
            if format.upper() in ['JPEG', 'WEBP']:
                save_kwargs['quality'] = quality or self.default_quality
            
            image.save(buffer, **save_kwargs)
            
            # 编码为Base64
            image_bytes = buffer.getvalue()
            base64_str = base64.b64encode(image_bytes).decode('utf-8')
            
            return base64_str
            
        except Exception as e:
            logger.error(f"图片编码失败: {e}")
            raise ValueError(f"图片编码失败: {e}")
    
    def resize_image(
        self, 
        image: Image.Image, 
        max_width: int = 1024, 
        max_height: int = 1024,
        maintain_aspect: bool = True
    ) -> Image.Image:
        """
        调整图片大小
        
        Args:
            image: PIL Image对象
            max_width: 最大宽度
            max_height: 最大高度
            maintain_aspect: 保持宽高比
            
        Returns:
            调整后的图片
        """
        width, height = image.size
        
        # 如果图片已经足够小，直接返回
        if width <= max_width and height <= max_height:
            return image
        
        if maintain_aspect:
            # 计算缩放比例
            ratio = min(max_width / width, max_height / height)
            new_size = (int(width * ratio), int(height * ratio))
        else:
            new_size = (max_width, max_height)
        
        # 使用高质量重采样
        resized = image.resize(new_size, Image.Resampling.LANCZOS)
        
        logger.info(f"图片已调整: {image.size} -> {resized.size}")
        return resized
    
    def enhance_image(
        self,
        image: Image.Image,
        contrast: float = 1.2,
        sharpness: float = 1.1,
        brightness: float = 1.0
    ) -> Image.Image:
        """
        增强图片（提高OCR准确度）
        
        Args:
            image: PIL Image对象
            contrast: 对比度（1.0=不变）
            sharpness: 锐度（1.0=不变）
            brightness: 亮度（1.0=不变）
            
        Returns:
            增强后的图片
        """
        try:
            # 对比度
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(contrast)
            
            # 锐度
            if sharpness != 1.0:
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(sharpness)
            
            # 亮度
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(brightness)
            
            logger.info("图片已增强（对比度/锐度/亮度）")
            return image
            
        except Exception as e:
            logger.error(f"图片增强失败: {e}")
            return image  # 返回原图
    
    def calculate_image_hash(self, image: Image.Image) -> str:
        """
        计算图片哈希（用于去重）
        
        Args:
            image: PIL Image对象
            
        Returns:
            图片哈希值（MD5）
        """
        try:
            # 转换为字节
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            image_bytes = buffer.getvalue()
            
            # 计算MD5
            hash_md5 = hashlib.md5(image_bytes)
            return hash_md5.hexdigest()
            
        except Exception as e:
            logger.error(f"计算图片哈希失败: {e}")
            return ""
    
    def prepare_for_ocr(self, image: Image.Image) -> Image.Image:
        """
        为OCR准备图片（预处理）
        
        Args:
            image: PIL Image对象
            
        Returns:
            预处理后的图片
        """
        # 转换为灰度图
        if image.mode != 'L':
            image = image.convert('L')
        
        # 增强对比度和锐度
        image = self.enhance_image(
            image,
            contrast=1.5,
            sharpness=1.3,
            brightness=1.1
        )
        
        logger.info("图片已预处理（OCR优化）")
        return image
    
    def get_image_info(self, image: Image.Image) -> Dict[str, Any]:
        """
        获取图片信息
        
        Args:
            image: PIL Image对象
            
        Returns:
            图片信息字典
        """
        return {
            "size": image.size,
            "width": image.size[0],
            "height": image.size[1],
            "format": image.format,
            "mode": image.mode,
            "hash": self.calculate_image_hash(image)
        }
    
    def process_image(
        self,
        image_data: str,
        optimize_for_ocr: bool = False,
        max_size: Tuple[int, int] = (1024, 1024)
    ) -> Dict[str, Any]:
        """
        一站式图片处理
        
        Args:
            image_data: Base64编码的图片
            optimize_for_ocr: 是否优化OCR
            max_size: 最大尺寸
            
        Returns:
            {
                "image": PIL Image对象,
                "base64": Base64字符串,
                "info": 图片信息,
                "hash": 图片哈希
            }
        """
        try:
            # 解码
            image = self.decode_base64_image(image_data)
            
            # 调整大小
            image = self.resize_image(image, max_size[0], max_size[1])
            
            # OCR优化
            if optimize_for_ocr:
                image = self.prepare_for_ocr(image)
            
            # 获取信息
            info = self.get_image_info(image)
            
            # 重新编码
            base64_str = self.encode_image_to_base64(image)
            
            return {
                "image": image,
                "base64": base64_str,
                "info": info,
                "hash": info["hash"]
            }
            
        except Exception as e:
            logger.error(f"图片处理失败: {e}")
            raise


# 全局单例
_image_processor = None

def get_image_processor() -> ImageProcessor:
    """获取图片处理器单例"""
    global _image_processor
    if _image_processor is None:
        _image_processor = ImageProcessor()
    return _image_processor

