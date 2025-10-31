"""
网页搜索工具 - 使用DuckDuckGo或其他免费API进行网页搜索
"""
import requests
from typing import Dict, List, Optional
from urllib.parse import quote


def web_search(query: str, num_results: int = 5) -> Dict:
    """
    网页搜索工具（使用DuckDuckGo Instant Answer API）
    
    Args:
        query: 搜索查询
        num_results: 返回结果数量
        
    Returns:
        搜索结果字典
    """
    try:
        # 使用DuckDuckGo API (免费，无需API key)
        # 注意：这是一个简化版本，实际可以使用更强大的搜索API
        url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1&skip_disambig=1"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 提取结果
        results = []
        
        # Abstract (直接答案)
        if data.get("Abstract"):
            results.append({
                "title": data.get("Heading", ""),
                "snippet": data.get("Abstract", ""),
                "url": data.get("AbstractURL", ""),
                "type": "abstract"
            })
        
        # Related Topics
        for topic in data.get("RelatedTopics", [])[:num_results]:
            if isinstance(topic, dict):
                results.append({
                    "title": topic.get("Text", ""),
                    "snippet": topic.get("Text", ""),
                    "url": topic.get("FirstURL", ""),
                    "type": "related"
                })
        
        # Definition
        if data.get("Definition"):
            results.append({
                "title": "定义",
                "snippet": data.get("Definition", ""),
                "url": data.get("DefinitionURL", ""),
                "type": "definition"
            })
        
        return {
            "success": True,
            "query": query,
            "results": results[:num_results]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "results": []
        }


def get_web_search_context(query: str, num_results: int = 3) -> str:
    """
    获取网页搜索结果的文本上下文
    
    Args:
        query: 搜索查询
        num_results: 返回结果数量
        
    Returns:
        格式化的搜索上下文文本
    """
    search_result = web_search(query, num_results)
    
    if not search_result["success"] or not search_result["results"]:
        return ""
    
    context_parts = []
    for i, result in enumerate(search_result["results"], 1):
        snippet = result.get("snippet", "")
        if snippet:
            context_parts.append(f"[搜索结果{i}]: {snippet}")
    
    return "\n\n".join(context_parts)

