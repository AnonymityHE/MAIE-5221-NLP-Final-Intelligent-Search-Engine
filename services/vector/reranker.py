"""
高级Reranker模块 - 使用交叉编码器进行二次排序，考虑相关性、可信度和新鲜度
支持多语言优化（特别是粤语查询）
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from services.core.logger import logger
from services.core.language_detector import get_language_detector

try:
    from sentence_transformers import CrossEncoder
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False
    logger.warning("sentence-transformers未安装CrossEncoder，Reranker功能将被禁用")


class Reranker:
    """高级交叉编码器重排序器（支持credibility和freshness权重）"""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        初始化Reranker
        
        Args:
            model_name: 交叉编码器模型名称
                - cross-encoder/ms-marco-MiniLM-L-6-v2 (推荐，速度快)
                - cross-encoder/ms-marco-MiniLM-L-12-v2 (更准确但更慢)
        """
        self.model = None
        self.model_name = model_name
        self.language_detector = get_language_detector()
        
        # 可信度权重配置（本地知识库 > 官方API > 网页搜索）
        self.credibility_weights = {
            "local_kb": 1.0,      # 本地知识库（最高可信度）
            "uploaded_file": 0.95,  # 用户上传的文件
            "official_api": 0.85,   # 官方API（天气、金融等）
            "web_search": 0.70,     # 网页搜索结果（较低可信度）
            "unknown": 0.75         # 未知来源（默认）
        }
        
        # 新鲜度衰减参数
        self.freshness_half_life_days = 365  # 半衰期（天），即365天后权重减半
        
        if CROSS_ENCODER_AVAILABLE:
            try:
                logger.info(f"正在加载Reranker模型: {model_name}")
                self.model = CrossEncoder(model_name)
                logger.info("Reranker模型加载完成（支持credibility和freshness权重）")
            except Exception as e:
                logger.error(f"加载Reranker模型失败: {e}")
                self.model = None
        else:
            logger.warning("Reranker功能未启用，因为sentence-transformers未正确安装")
    
    def _get_source_credibility(self, doc: Dict) -> float:
        """
        计算文档来源的可信度权重
        
        Args:
            doc: 文档字典，包含source_file等信息
            
        Returns:
            可信度权重（0.0-1.0）
        """
        source_file = doc.get('source_file', '')
        file_type = doc.get('file_type', '')
        
        # 检查是否是上传的文件（有file_id标记）
        if '||file_id:' in source_file or doc.get('file_id'):
            # 用户上传的文件，可信度较高
            return self.credibility_weights['uploaded_file']
        
        # 检查source_file类型
        if 'local_kb' in source_file.lower() or 'knowledge_base' in source_file.lower():
            return self.credibility_weights['local_kb']
        
        # 检查是否是API来源（通过工具判断）
        # 这里可以根据实际使用情况扩展
        # 目前如果source_file包含特定标记，可以识别
        
        # 默认返回中等可信度
        return self.credibility_weights.get('unknown', 0.75)
    
    def _get_freshness_weight(self, doc: Dict, query_is_realtime: bool = False) -> float:
        """
        计算文档新鲜度权重
        
        Args:
            doc: 文档字典，包含uploaded_at等信息
            query_is_realtime: 查询是否为实时查询
            
        Returns:
            新鲜度权重（0.0-1.0），1.0表示最新，0.0表示很旧
        """
        uploaded_at = doc.get('uploaded_at', '')
        
        # 如果没有时间信息，返回默认权重
        if not uploaded_at:
            return 0.85  # 默认中等权重
        
        try:
            # 解析时间字符串（格式：ISO 8601或类似）
            if isinstance(uploaded_at, str):
                # 尝试解析ISO格式
                if 'T' in uploaded_at:
                    upload_time = datetime.fromisoformat(uploaded_at.replace('Z', '+00:00'))
                else:
                    # 尝试其他格式
                    upload_time = datetime.strptime(uploaded_at, '%Y-%m-%d %H:%M:%S')
            else:
                # 如果已经是datetime对象
                upload_time = uploaded_at
            
            # 计算时间差（天）
            now = datetime.now()
            if upload_time.tzinfo:
                # 如果有时区信息，需要调整
                from datetime import timezone
                if now.tzinfo is None:
                    now = now.replace(tzinfo=timezone.utc)
            else:
                # 假设upload_time是本地时间
                pass
            
            days_diff = (now - upload_time.replace(tzinfo=None)).days if upload_time.tzinfo else (now - upload_time).days
            
            # 对于实时查询，新鲜度更重要
            if query_is_realtime:
                # 实时查询：1天内权重1.0，7天内0.9，30天内0.7，之后快速衰减
                if days_diff <= 1:
                    return 1.0
                elif days_diff <= 7:
                    return 0.9
                elif days_diff <= 30:
                    return 0.7
                else:
                    # 使用指数衰减
                    return max(0.3, 0.7 * (0.5 ** (days_diff / 30)))
            else:
                # 非实时查询：使用半衰期衰减
                # 权重 = 0.5 ^ (days / half_life)
                weight = 0.5 ** (days_diff / self.freshness_half_life_days)
                # 最低权重设为0.5（即使是旧信息也有一定价值）
                return max(0.5, weight)
                
        except Exception as e:
            logger.warning(f"解析时间失败 {uploaded_at}: {e}，使用默认权重")
            return 0.85
    
    def _detect_realtime_query(self, query: str) -> bool:
        """
        检测查询是否为实时查询（需要新鲜信息）
        
        Args:
            query: 查询文本
            
        Returns:
            是否为实时查询
        """
        query_lower = query.lower()
        realtime_keywords = [
            "latest", "最新", "current", "当前", "now", "现在", 
            "today", "今天", "recent", "最近", "new", "新",
            "recently", "just", "刚刚", "实时"
        ]
        return any(keyword in query_lower for keyword in realtime_keywords)
    
    def rerank(self, query: str, documents: List[Dict], top_k: int = None, 
               use_credibility: bool = True, use_freshness: bool = True) -> List[Dict]:
        """
        高级重排序：考虑相关性、可信度和新鲜度
        
        Args:
            query: 查询文本
            documents: 文档列表，每个文档包含 'text', 'source_file', 'score' 等字段
            top_k: 返回top_k个最相关的结果，如果为None则返回所有
            use_credibility: 是否使用可信度权重（默认True）
            use_freshness: 是否使用新鲜度权重（默认True）
            
        Returns:
            重排序后的文档列表，包含rerank_score、credibility_weight、freshness_weight、final_score
        """
        if not self.model:
            logger.warning("Reranker模型未加载，返回原始排序结果")
            return documents[:top_k] if top_k else documents
        
        if not documents:
            return []
        
        try:
            # 检测是否为实时查询
            is_realtime = self._detect_realtime_query(query)
            
            # 检测查询语言（用于多语言优化）
            query_lang_info = self.language_detector.detect(query)
            is_cantonese_query = query_lang_info.get("cantonese", 0) > 0.4
            logger.debug(f"查询语言检测: {query_lang_info['primary']}, 粤语={query_lang_info['cantonese']:.2f}")
            
            # 准备输入对 (query, document_text)
            pairs = [(query, doc.get('text', '')) for doc in documents]
            
            # 使用交叉编码器计算相关性分数（分数越高越相关）
            rerank_scores = self.model.predict(pairs)
            
            # 计算综合分数
            for i, doc in enumerate(documents):
                # 1. 相关性分数（来自交叉编码器）
                doc['rerank_score'] = float(rerank_scores[i])
                doc['original_score'] = doc.get('score', 0.0)
                
                # 2. 可信度权重
                credibility_weight = self._get_source_credibility(doc) if use_credibility else 1.0
                doc['credibility_weight'] = credibility_weight
                
                # 3. 新鲜度权重
                freshness_weight = self._get_freshness_weight(doc, is_realtime) if use_freshness else 1.0
                doc['freshness_weight'] = freshness_weight
                
                # 4. 语言匹配权重（粤语查询优化）
                language_weight = 1.0
                if is_cantonese_query:
                    # 检测文档语言
                    doc_text = doc.get('text', '')
                    doc_lang_info = self.language_detector.detect(doc_text)
                    doc_cantonese_ratio = doc_lang_info.get("cantonese", 0)
                    
                    # 如果文档也是粤语，给予更高权重
                    if doc_cantonese_ratio > 0.3:
                        language_weight = 1.15  # 增加15%权重
                        logger.debug(f"粤语查询匹配粤语文档: 语言权重={language_weight:.2f}")
                    elif doc_cantonese_ratio > 0.1:
                        language_weight = 1.05  # 轻微增加
                
                doc['language_weight'] = language_weight
                
                # 5. 综合最终分数
                # CrossEncoder的分数通常是负数到正数，需要使用sigmoid或归一化
                # 使用sigmoid归一化：将分数映射到0-1范围
                import numpy as np
                try:
                    # 使用sigmoid函数归一化（更平滑）
                    normalized_rerank = 1 / (1 + np.exp(-doc['rerank_score']))
                except:
                    # 如果numpy不可用，使用简单线性归一化
                    # 假设CrossEncoder分数范围大约是-10到10
                    normalized_rerank = max(0.0, min(1.0, (doc['rerank_score'] + 10) / 20))
                
                # 综合评分公式（添加语言匹配权重）：
                # final_score = normalized_rerank_score * credibility_weight * freshness_weight * language_weight
                doc['final_score'] = normalized_rerank * credibility_weight * freshness_weight * language_weight
                
                logger.debug(
                    f"文档重排序: rerank={doc['rerank_score']:.3f}, "
                    f"cred={credibility_weight:.3f}, fresh={freshness_weight:.3f}, "
                    f"final={doc['final_score']:.3f}"
                )
            
            # 按最终分数降序排序
            reranked = sorted(documents, key=lambda x: x.get('final_score', 0), reverse=True)
            
            # 返回top_k个结果
            if top_k:
                reranked = reranked[:top_k]
            
            logger.info(
                f"高级Reranker重排序完成: {len(documents)} -> {len(reranked)} 个文档 "
                f"(credibility={use_credibility}, freshness={use_freshness}, realtime={is_realtime})"
            )
            return reranked
            
        except Exception as e:
            logger.error(f"Reranker重排序失败: {e}，返回原始排序结果")
            import traceback
            logger.debug(traceback.format_exc())
            return documents[:top_k] if top_k else documents
    
    def is_available(self) -> bool:
        """检查Reranker是否可用"""
        return self.model is not None


# 全局Reranker实例
reranker = Reranker()

