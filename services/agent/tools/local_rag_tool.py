"""
本地知识库RAG工具 - 将RAG封装成Agent工具
"""
from typing import Dict, List
from services.vector.retriever import retriever


def local_knowledge_base_search(query: str) -> Dict:
    """
    本地知识库搜索工具
    
    Args:
        query: 查询文本
        
    Returns:
        包含搜索结果和是否相关的字典
    """
    # 搜索相关文档
    search_results = retriever.search(query, top_k=5)
    
    if not search_results:
        return {
            "has_results": False,
            "relevant": False,
            "results": []
        }
    
    # 检查相似度：L2距离越小越相似
    RELEVANCE_THRESHOLD = 3.0
    best_score = min(result.get('score', float('inf')) for result in search_results)
    is_relevant = best_score <= RELEVANCE_THRESHOLD
    
    return {
        "has_results": True,
        "relevant": is_relevant,
        "results": search_results,
        "best_score": best_score
    }


def get_local_knowledge_context(query: str, top_k: int = 8) -> str:
    """
    从本地知识库获取上下文
    
    Args:
        query: 查询文本
        top_k: 检索数量（默认8，复杂查询可增加）
        
    Returns:
        上下文文本，如果没有相关结果返回空字符串
    """
    # 使用动态top_k
    search_results = retriever.search(query, top_k=top_k)
    
    if not search_results:
        return ""
    
    # 构建上下文（移除调试信息，更简洁）
    context_parts = []
    for result in search_results:
        text = result.get('text', '')
        if text:
            context_parts.append(text)
    
    return "\n\n".join(context_parts)

