"""
检索器 - 实现RAG的核心检索逻辑（集成Reranker）
"""
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from services.core.config import settings
from services.vector.milvus_client import milvus_client
from services.vector.reranker import reranker
from services.core.logger import logger


class Retriever:
    """RAG检索器（支持Reranker重排序）"""
    
    def __init__(self):
        # 初始化embedding模型
        logger.info(f"正在加载embedding模型: {settings.EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("Embedding模型加载完成")
    
    def search(self, query_text: str, top_k: int = None, use_reranker: bool = None) -> List[Dict]:
        """
        搜索相关文档（可选使用Reranker重排序）
        
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
        
        # 将查询文本向量化
        query_vector = self.embedding_model.encode([query_text])[0].tolist()
        
        # 在Milvus中搜索（先检索更多结果，如果使用reranker）
        initial_k = top_k * 2 if use_reranker else top_k
        results = milvus_client.search_vectors(query_vector, top_k=initial_k)
        
        # 如果启用Reranker且模型可用，进行重排序
        if use_reranker and reranker.is_available() and results:
            logger.debug(f"使用Reranker对 {len(results)} 个结果进行重排序")
            results = reranker.rerank(query_text, results, top_k=top_k)
        elif use_reranker and not reranker.is_available():
            logger.warning("Reranker已启用但模型不可用，使用原始排序结果")
        
        return results[:top_k]
    
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

