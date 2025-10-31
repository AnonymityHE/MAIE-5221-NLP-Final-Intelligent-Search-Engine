"""
本地知识库RAG工具 - 将RAG封装成Agent工具
"""
from typing import Dict, List
from services.retriever import retriever


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


def get_local_knowledge_context(query: str) -> str:
    """
    从本地知识库获取上下文
    
    Args:
        query: 查询文本
        
    Returns:
        上下文文本，如果没有相关结果返回空字符串
    """
    search_result = local_knowledge_base_search(query)
    
    if not search_result["relevant"]:
        return ""
    
    # 构建上下文
    context_parts = []
    for result in search_result["results"]:
        context_parts.append(result['text'])
    
    return "\n\n".join(context_parts)

