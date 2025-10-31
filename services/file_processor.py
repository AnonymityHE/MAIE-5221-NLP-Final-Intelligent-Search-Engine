"""
多模态文件处理器 - 解析PDF、图片、代码等文件
"""
import io
import base64
from pathlib import Path
from typing import Dict, Optional, List

# PyMuPDF依赖（PDF处理）
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("警告: PyMuPDF 未安装，PDF处理功能将被禁用。请运行: pip install PyMuPDF")

# Pillow依赖（图片处理）
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("警告: Pillow 未安装，图片处理功能将被禁用。请运行: pip install Pillow")

# OCR依赖可选，如果没有安装pytesseract，图片OCR功能将被禁用
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("警告: pytesseract 未安装，图片OCR功能将被禁用。如需使用OCR，请运行: pip install pytesseract")

from services.file_storage import file_storage


class FileProcessor:
    """多模态文件处理器"""
    
    def __init__(self):
        self.supported_types = {
            'pdf': self._process_pdf,
            'image': self._process_image,
            'code': self._process_code,
            'text': self._process_text
        }
    
    def process_file(self, file_id: str) -> Dict:
        """
        处理上传的文件，提取文本内容
        
        Args:
            file_id: 文件ID
            
        Returns:
            包含提取文本和元数据的字典
        """
        file_info = file_storage.get_file(file_id)
        if not file_info:
            raise ValueError(f"文件不存在: {file_id}")
        
        file_path = file_info['file_path']
        file_type = file_info['file_type']
        
        if file_type not in self.supported_types:
            raise ValueError(f"不支持的文件类型: {file_type}")
        
        processor = self.supported_types[file_type]
        result = processor(file_path)
        
        return result
    
    def _process_pdf(self, file_path: str) -> Dict:
        """处理PDF文件"""
        if not PDF_AVAILABLE:
            return {
                "text": "",
                "metadata": {
                    "error": "PDF处理功能未启用",
                    "note": "PyMuPDF未安装，无法处理PDF文件。请运行: pip install PyMuPDF"
                }
            }
        
        try:
            doc = fitz.open(file_path)
            text_parts = []
            page_count = len(doc)
            
            for page_num in range(page_count):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    text_parts.append(f"[页面 {page_num + 1}]\n{text}")
            
            doc.close()
            
            full_text = "\n\n".join(text_parts)
            
            return {
                "text": full_text,
                "metadata": {
                    "page_count": page_count,
                    "char_count": len(full_text)
                }
            }
        except Exception as e:
            return {
                "text": "",
                "metadata": {
                    "error": str(e),
                    "note": "PDF处理失败"
                }
            }
    
    def _process_image(self, file_path: str) -> Dict:
        """处理图片文件（OCR）"""
        if not PIL_AVAILABLE:
            return {
                "text": "",
                "metadata": {
                    "error": "图片处理功能未启用",
                    "note": "Pillow未安装，无法处理图片文件。请运行: pip install Pillow"
                }
            }
        
        if not OCR_AVAILABLE:
            return {
                "text": "",
                "metadata": {
                    "error": "OCR功能未启用",
                    "note": "pytesseract未安装，无法进行OCR识别。请运行: pip install pytesseract，并确保系统已安装Tesseract OCR"
                }
            }
        
        try:
            image = Image.open(file_path)
            # 使用Tesseract OCR提取文本
            text = pytesseract.image_to_string(image, lang='chi_sim+eng')
            
            return {
                "text": text.strip(),
                "metadata": {
                    "image_size": image.size,
                    "image_mode": image.mode,
                    "char_count": len(text.strip())
                }
            }
        except Exception as e:
            # 如果OCR失败，返回空文本
            return {
                "text": "",
                "metadata": {
                    "error": str(e),
                    "note": "OCR失败，可能是不包含文字的图片或Tesseract未正确安装"
                }
            }
    
    def _process_code(self, file_path: str) -> Dict:
        """处理代码文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        return {
            "text": code,
            "metadata": {
                "language": self._detect_language(file_path),
                "line_count": len(code.splitlines()),
                "char_count": len(code)
            }
        }
    
    def _process_text(self, file_path: str) -> Dict:
        """处理文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(file_path, 'r', encoding='gbk') as f:
                text = f.read()
        
        return {
            "text": text,
            "metadata": {
                "char_count": len(text),
                "line_count": len(text.splitlines())
            }
        }
    
    def _detect_language(self, file_path: str) -> str:
        """根据文件扩展名检测编程语言"""
        ext_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.ts': 'TypeScript'
        }
        ext = Path(file_path).suffix.lower()
        return ext_map.get(ext, 'Unknown')


# 全局文件处理器实例
file_processor = FileProcessor()

