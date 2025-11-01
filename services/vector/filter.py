"""
结果过滤模块
基于credibility、freshness和质量对检索结果进行过滤
"""
from typing import List, Dict
from datetime import datetime
from services.core.logger import logger


class ResultFilter:
    """结果过滤器 - 过滤低质量、低可信度或过时的结果"""
    
    def __init__(
        self, 
        min_credibility: float = 0.3,
        max_age_days: int = 365,
        min_text_length: int = 50,
        remove_duplicates: bool = True
    ):
        """
        初始化过滤器
        
        Args:
            min_credibility: 最低可信度阈值（0-1）
            max_age_days: 对于时效性查询，超过此天数的结果会被降权（默认365天）
            min_text_length: 最小文本长度（字符数）
            remove_duplicates: 是否移除重复结果
        """
        self.min_credibility = min_credibility
        self.max_age_days = max_age_days
        self.min_text_length = min_text_length
        self.remove_duplicates = remove_duplicates
        logger.info(f"初始化结果过滤器: min_credibility={min_credibility}, max_age_days={max_age_days}")
    
    def _get_credibility_score(self, result: Dict) -> float:
        """
        计算结果的可信度分数
        
        Args:
            result: 检索结果字典
            
        Returns:
            可信度分数（0-1）
        """
        source = result.get("source_file", "")
        source_type = result.get("source_type", "unknown")
        
        # 可信度权重表
        credibility_map = {
            "local_kb": 1.0,      # 本地知识库：最高可信度
            "uploaded_file": 0.9,  # 用户上传文件：高可信度
            "official_api": 0.8,   # 官方API（如天气、金融）：较高可信度
            "web_search": 0.6,     # 网页搜索结果：中等可信度
            "unknown": 0.5         # 未知来源：低可信度
        }
        
        # 根据source_type确定可信度
        if source_type in credibility_map:
            return credibility_map[source_type]
        
        # 根据文件名判断
        if "local_kb" in source.lower() or "documents" in source.lower():
            return 0.9
        elif source.endswith((".pdf", ".docx", ".txt")):
            return 0.8
        else:
            return 0.6
    
    def _get_freshness_score(self, result: Dict, is_realtime_query: bool = False) -> float:
        """
        计算结果的新鲜度分数
        
        Args:
            result: 检索结果字典
            is_realtime_query: 是否为时效性查询（如新闻、股票价格）
            
        Returns:
            新鲜度分数（0-1）
        """
        uploaded_at = result.get("uploaded_at", "")
        if not uploaded_at:
            # 如果没有时间戳，对于时效性查询返回较低分数
            return 0.7 if not is_realtime_query else 0.3
        
        try:
            # 解析时间戳（支持ISO格式或字符串）
            if isinstance(uploaded_at, str):
                # 尝试解析ISO格式
                try:
                    upload_time = datetime.fromisoformat(uploaded_at.replace('Z', '+00:00'))
                except:
                    # 尝试其他常见格式（如果安装了python-dateutil）
                    try:
                        from dateutil.parser import parse
                        upload_time = parse(uploaded_at)
                    except ImportError:
                        # 如果没有dateutil，返回默认值
                        logger.warning(f"无法解析时间戳（需要python-dateutil）: {uploaded_at}")
                        return 0.7 if not is_realtime_query else 0.3
            else:
                upload_time = uploaded_at
            
            # 计算时间差
            now = datetime.now()
            if isinstance(upload_time, datetime):
                age_days = (now - upload_time).days
            else:
                # 如果无法解析，返回默认值
                return 0.7 if not is_realtime_query else 0.3
            
            # 对于时效性查询，时间衰减更快
            if is_realtime_query:
                if age_days > 30:  # 超过30天的新闻/股价等视为过时
                    return 0.2
                elif age_days > 7:  # 7-30天：中等新鲜度
                    return 0.5
                else:  # 7天内：新鲜
                    return 1.0
            else:
                # 非时效性查询，衰减较慢
                if age_days > self.max_age_days:  # 超过阈值：过时
                    return 0.3
                elif age_days > self.max_age_days // 2:  # 一半阈值到阈值：中等
                    return 0.6
                else:  # 较新
                    return 1.0
        except Exception as e:
            logger.warning(f"解析时间戳失败: {uploaded_at}, 错误: {e}")
            return 0.7 if not is_realtime_query else 0.3
    
    def _is_duplicate(self, result1: Dict, result2: Dict) -> bool:
        """检查两个结果是否重复"""
        text1 = result1.get("text", "").lower().strip()
        text2 = result2.get("text", "").lower().strip()
        
        # 简单的文本相似度检查
        if text1 == text2:
            return True
        
        # 如果文本长度相似且相似度超过80%，视为重复
        if len(text1) > 0 and len(text2) > 0:
            similarity = self._simple_similarity(text1, text2)
            if similarity > 0.8:
                return True
        
        return False
    
    def _simple_similarity(self, text1: str, text2: str) -> float:
        """简单的文本相似度计算（基于共同词汇）"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def filter(
        self, 
        results: List[Dict], 
        is_realtime_query: bool = False,
        apply_credibility_filter: bool = True,
        apply_freshness_filter: bool = True,
        apply_quality_filter: bool = True
    ) -> List[Dict]:
        """
        过滤结果列表
        
        Args:
            results: 检索结果列表
            is_realtime_query: 是否为时效性查询
            apply_credibility_filter: 是否应用可信度过滤
            apply_freshness_filter: 是否应用新鲜度过滤
            apply_quality_filter: 是否应用质量过滤
            
        Returns:
            过滤后的结果列表
        """
        if not results:
            return results
        
        filtered_results = []
        seen_texts = set()  # 用于去重
        
        for result in results:
            # 1. 质量过滤：检查文本长度
            if apply_quality_filter:
                text = result.get("text", "")
                if len(text) < self.min_text_length:
                    logger.debug(f"过滤短文本结果: {len(text)}字符")
                    continue
            
            # 2. 可信度过滤
            if apply_credibility_filter:
                credibility = self._get_credibility_score(result)
                if credibility < self.min_credibility:
                    logger.debug(f"过滤低可信度结果: credibility={credibility:.2f}")
                    continue
                # 将可信度分数添加到结果中（用于后续排序）
                result["credibility_score"] = credibility
            
            # 3. 新鲜度评分（不直接过滤，但记录分数用于排序）
            if apply_freshness_filter:
                freshness = self._get_freshness_score(result, is_realtime_query)
                result["freshness_score"] = freshness
                
                # 对于时效性查询，如果新鲜度太低则过滤
                if is_realtime_query and freshness < 0.3:
                    logger.debug(f"过滤过时结果（时效性查询）: freshness={freshness:.2f}")
                    continue
            
            # 4. 去重
            if self.remove_duplicates:
                text_normalized = result.get("text", "").lower().strip()[:100]  # 取前100字符用于去重
                if text_normalized in seen_texts:
                    logger.debug("过滤重复结果")
                    continue
                seen_texts.add(text_normalized)
            
            filtered_results.append(result)
        
        logger.info(f"过滤完成: {len(results)} -> {len(filtered_results)} 个结果")
        return filtered_results


# 全局过滤器实例
_result_filter = ResultFilter()


def get_result_filter() -> ResultFilter:
    """获取全局结果过滤器实例"""
    return _result_filter
