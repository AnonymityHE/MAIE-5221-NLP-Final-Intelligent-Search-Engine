"""
检索器 - 实现RAG的核心检索逻辑（集成Reranker和缓存，支持多语言）
"""
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from services.core.config import settings
from services.vector.milvus_client import milvus_client
from services.vector.reranker import reranker
from services.core.logger import logger
from services.core.cache import get_query_cache, get_embedding_cache, _generate_cache_key
from services.vector.filter import get_result_filter
from services.core.language_detector import get_language_detector


class Retriever:
    """RAG检索器（支持Reranker重排序、多语言支持）"""
    
    def __init__(self):
        # 根据配置选择embedding模型（多语言或单语言）
        if settings.USE_MULTILINGUAL_EMBEDDING:
            model_name = settings.MULTILINGUAL_EMBEDDING_MODEL
            logger.info(f"正在加载多语言embedding模型: {model_name}（支持粤语、普通话、英语）")
        else:
            model_name = settings.EMBEDDING_MODEL
            logger.info(f"正在加载embedding模型: {model_name}")
        
        try:
            self.embedding_model = SentenceTransformer(model_name)
            logger.info(f"Embedding模型加载完成（{'多语言' if settings.USE_MULTILINGUAL_EMBEDDING else '单语言'}）")
        except Exception as e:
            logger.warning(f"加载embedding模型失败: {e}，尝试使用默认模型")
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("使用默认embedding模型")
        
        # 初始化语言检测器
        self.language_detector = get_language_detector()
    
    def search(self, query_text: str, top_k: int = None, use_reranker: bool = None) -> List[Dict]:
        """
        搜索相关文档（可选使用Reranker重排序，支持缓存）
        
        Args:
            query_text: 查询文本
            top_k: 返回最相关的k个文档，默认使用配置值
            use_reranker: 是否使用Reranker，如果为None则使用配置值
            
        Returns:
            相关文档列表，每个文档包含text、source_file和score
        """
        if top_k is None:
            top_k = settings.TOP_K
        
        if use_reranker is None:
            use_reranker = settings.USE_RERANKER
        
        # 检查缓存（如果启用）
        if settings.USE_CACHE:
            cache_key = _generate_cache_key(
                query_text, 
                {"num_results": top_k, "use_reranker": use_reranker}
            )
            query_cache = get_query_cache()
            cached_results = query_cache.get(cache_key)
            if cached_results is not None:
                logger.info(f"检索缓存命中: {query_text[:50]}...")
                return cached_results
        
        # 缓存未命中，执行检索
        # 检查embedding缓存
        embedding_cache = get_embedding_cache()
        embedding_key = _generate_cache_key(query_text)
        query_vector = embedding_cache.get(embedding_key)
        
        # 检测语言（无论是否缓存命中都需要，用于检索优化）
        lang_info = self.language_detector.detect(query_text)
        
        if query_vector is None:
            if lang_info["mixed"] > 0.3 or lang_info["primary"] != "unknown":
                logger.debug(f"检测到多语言查询: {lang_info['primary']} "
                           f"(粤语={lang_info['cantonese']:.2f}, "
                           f"普通话={lang_info['mandarin']:.2f}, "
                           f"英语={lang_info['english']:.2f})")
            
            # 向量化查询文本（多语言模型会自动处理不同语言）
            query_for_embedding = query_text
            if lang_info["cantonese"] > 0.4:
                logger.debug("检测到粤语查询，应用相似度优化")
            
            query_vector = self.embedding_model.encode([query_for_embedding], show_progress_bar=False)[0].tolist()
            # 缓存embedding向量
            embedding_cache.set(embedding_key, query_vector)
        else:
            logger.debug(f"Embedding缓存命中: {query_text[:50]}...")
        
        # 在Milvus中搜索（先检索更多结果，如果使用reranker）
        # 对于粤语查询，检索更多候选以提高召回率
        initial_k = top_k * 2 if use_reranker else top_k
        
        # 粤语查询优化：检索更多候选以提高召回率
        if lang_info.get("cantonese", 0) > 0.4:
            initial_k = int(initial_k * 1.5)  # 增加50%的候选
            logger.debug(f"粤语查询优化：增加检索候选数量至 {initial_k}")
        
        results = milvus_client.search_vectors(query_vector, top_k=initial_k)
        
        # 如果启用Reranker且模型可用，进行高级重排序（credibility + freshness）
        if use_reranker and reranker.is_available() and results:
            logger.debug(f"使用高级Reranker对 {len(results)} 个结果进行重排序（credibility + freshness）")
            results = reranker.rerank(
                query_text, 
                results, 
                top_k=top_k,
                use_credibility=True,  # 启用可信度权重
                use_freshness=True     # 启用新鲜度权重
            )
        elif use_reranker and not reranker.is_available():
            logger.warning("Reranker已启用但模型不可用，使用原始排序结果")
        
        final_results = results[:top_k]
        
        # 应用结果过滤（可选，默认启用）
        # 注意：对于时效性查询，可以传递is_realtime_query=True
        result_filter = get_result_filter()
        if final_results:
            # 检测是否为时效性查询
            is_realtime_query = self._is_realtime_query(query_text)
            final_results = result_filter.filter(
                final_results,
                is_realtime_query=is_realtime_query,
                apply_credibility_filter=True,
                apply_freshness_filter=True,
                apply_quality_filter=True
            )
        
        # 缓存结果
        if settings.USE_CACHE:
            query_cache.set(cache_key, final_results)
        
        return final_results
    
    def _is_realtime_query(self, query_text: str) -> bool:
        """检测是否为时效性查询"""
        realtime_keywords = [
            "latest", "recent", "current", "now", "today", "now",
            "最新", "当前", "现在", "实时", "今天"
        ]
        query_lower = query_text.lower()
        return any(kw in query_lower for kw in realtime_keywords)
    
    def get_context(self, query_text: str, top_k: int = None) -> str:
        """
        获取检索到的上下文文本（拼接后的字符串）
        
        Args:
            query_text: 查询文本
            top_k: 返回最相关的k个文档
            
        Returns:
            拼接后的上下文文本
        """
        results = self.search(query_text, top_k)
        
        # 拼接所有检索到的文本
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[文档{i}]\n{result['text']}\n")
        
        context = "\n".join(context_parts)
        return context


# 全局检索器实例
retriever = Retriever()

