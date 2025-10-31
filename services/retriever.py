"""
检索器 - 实现RAG的核心检索逻辑
"""
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from services.config import settings
from services.milvus_client import milvus_client


class Retriever:
    """RAG检索器"""
    
    def __init__(self):
        # 初始化embedding模型
        print(f"正在加载embedding模型: {settings.EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        print("Embedding模型加载完成")
    
    def search(self, query_text: str, top_k: int = None) -> List[Dict]:
        """
        搜索相关文档
        
        Args:
            query_text: 查询文本
            top_k: 返回最相关的k个文档，默认使用配置值
            
        Returns:
            相关文档列表，每个文档包含text、source_file和score
        """
        if top_k is None:
            top_k = settings.TOP_K
        
        # 将查询文本向量化
        query_vector = self.embedding_model.encode([query_text])[0].tolist()
        
        # 在Milvus中搜索
        results = milvus_client.search_vectors(query_vector, top_k=top_k)
        
        return results
    
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

