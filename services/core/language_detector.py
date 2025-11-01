"""
语言检测模块 - 检测文本的语言类型（粤语、普通话、英语）
用于多语言RAG优化
"""
import re
from typing import Dict, Optional, List
from services.core.logger import logger


class LanguageDetector:
    """语言检测器 - 识别粤语、普通话、英语"""
    
    def __init__(self):
        # 粤语特有字符和词汇特征
        self.cantonese_keywords = [
            '嘅', '咗', '係', '係', '啲', '佢', '佢哋', '你哋', '我哋',
            '咁', '咩', '乜', '嘢', '嗰', '噉', '咗', '咩', '噉樣',
            '唔', '冇', '啱', '咁樣', '點解', '點樣', '做咩', '乜嘢'
        ]
        
        # 粤语特有的字符范围
        self.cantonese_chars = set([
            '嘅', '咗', '係', '啲', '佢', '咁', '咩', '乜', '嘢', '嗰',
            '噉', '唔', '冇', '啱', '點', '做', '喺', '嚟', '佢哋',
            '你哋', '我哋', '噉樣', '咁樣'
        ])
        
        # 英语特征（简单检测）
        self.english_pattern = re.compile(r'^[a-zA-Z\s.,!?;:\-\'"]+$')
    
    def detect(self, text: str) -> Dict[str, float]:
        """
        检测文本的语言组成（改进版：增强混合语言识别）
        
        Args:
            text: 输入文本
            
        Returns:
            语言概率字典，例如: {
                "cantonese": 0.3,
                "mandarin": 0.5,
                "english": 0.2,
                "mixed": 0.4
            }
        """
        if not text or not text.strip():
            return {"cantonese": 0.0, "mandarin": 0.0, "english": 0.0, "mixed": 0.0}
        
        text_lower = text.lower()
        
        # 检测粤语特征
        cantonese_score = 0.0
        cantonese_char_count = sum(1 for char in text if char in self.cantonese_chars)
        cantonese_keyword_count = sum(1 for keyword in self.cantonese_keywords if keyword in text)
        
        if len(text) > 0:
            cantonese_score = min(1.0, (cantonese_char_count * 2 + cantonese_keyword_count * 3) / len(text) * 10)
        
        # 检测英语特征（改进：考虑单词长度和比例）
        english_score = 0.0
        words = text.split()
        if words:
            english_word_count = sum(1 for word in words if self.english_pattern.match(word))
            english_char_count = sum(len(word) for word in words if self.english_pattern.match(word))
            total_char_count = sum(len(word) for word in words)
            
            if total_char_count > 0:
                # 同时考虑单词数量和字符比例
                english_score = (english_word_count / len(words)) * 0.6 + (english_char_count / total_char_count) * 0.4
            else:
                english_score = english_word_count / len(words) if len(words) > 0 else 0.0
        
        # 检测中文字符（普通话或粤语）
        chinese_char_count = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        total_chars = len([c for c in text if c.strip()])
        
        if total_chars > 0:
            chinese_ratio = chinese_char_count / total_chars
        else:
            chinese_ratio = 0.0
        
        # 普通话分数（中文但不是粤语）
        mandarin_score = max(0.0, chinese_ratio - cantonese_score * 0.5)
        
        # 改进的混合语言检测（更精确的阈值）
        language_scores = {
            "cantonese": cantonese_score,
            "mandarin": mandarin_score,
            "english": english_score
        }
        
        # 计算有多少种语言超过阈值
        threshold = 0.15  # 降低阈值以更好检测混合语言
        active_languages = [lang for lang, score in language_scores.items() if score > threshold]
        active_count = len(active_languages)
        
        # 混合语言评分：如果2种或以上语言同时活跃，或者单一语言未占绝对主导
        max_score = max(language_scores.values())
        is_mixed = False
        
        if active_count >= 2:
            # 多种语言同时存在
            is_mixed = True
            mixed_score = min(0.8, active_count * 0.25 + (1 - max_score) * 0.5)
        elif max_score < 0.7 and active_count >= 1:
            # 单一语言未占主导，可能是混合
            is_mixed = True
            mixed_score = 0.3
        else:
            mixed_score = 0.0
        
        # 归一化（先归一化各语言分数）
        total = cantonese_score + mandarin_score + english_score
        if total > 0:
            cantonese_score = cantonese_score / total
            mandarin_score = mandarin_score / total
            english_score = english_score / total
        
        result = {
            "cantonese": min(1.0, cantonese_score),
            "mandarin": min(1.0, mandarin_score),
            "english": min(1.0, english_score),
            "mixed": min(1.0, mixed_score)
        }
        
        # 确定主要语言（如果mixed分数足够高，优先返回mixed）
        if result["mixed"] > 0.35:
            result["primary"] = "mixed"
        else:
            primary_language = max(
                [(k, v) for k, v in result.items() if k != "mixed"],
                key=lambda x: x[1],
                default=("unknown", 0.0)
            )
            result["primary"] = primary_language[0] if primary_language[1] > 0.3 else "unknown"
        
        logger.debug(f"语言检测结果: {result['primary']} (粤语={result['cantonese']:.2f}, "
                    f"普通话={result['mandarin']:.2f}, 英语={result['english']:.2f}, "
                    f"混合={result['mixed']:.2f})")
        
        return result
    
    def is_multilingual(self, text: str) -> bool:
        """检查是否为多语言文本"""
        detection = self.detect(text)
        return detection["mixed"] > 0.3
    
    def get_primary_language(self, text: str) -> str:
        """获取主要语言"""
        detection = self.detect(text)
        return detection.get("primary", "unknown")


# 全局语言检测器实例
_language_detector = LanguageDetector()


def get_language_detector() -> LanguageDetector:
    """获取全局语言检测器实例"""
    return _language_detector

