"""
网页搜索工具 - 使用Tavily AI / Google Custom Search / DuckDuckGo进行网页搜索
"""
import requests
from typing import Dict, List, Optional
from urllib.parse import quote
from services.core.config import settings
from services.core.logger import logger


def web_search(query: str, num_results: int = 5) -> Dict:
    """
    网页搜索工具（优先级：Tavily > Google > DuckDuckGo）
    
    Args:
        query: 搜索查询
        num_results: 返回结果数量
        
    Returns:
        搜索结果字典
    """
    # 🌟 优先使用Tavily AI Search（专为AI优化）
    tavily_api_key = getattr(settings, 'TAVILY_API_KEY', None)
    use_tavily = getattr(settings, 'USE_TAVILY_SEARCH', True)
    
    if tavily_api_key and use_tavily:
        try:
            from services.tools.tavily_search import get_tavily_client
            
            tavily_client = get_tavily_client()
            tavily_result = tavily_client.search(
                query=query,
                max_results=num_results,
                search_depth="basic",  # 可选: "basic" (平衡) 或 "advanced" (深度)
                include_answer=True
                # 注意: timeout是requests的参数，不是Tavily API的参数
            )
            
            if "error" not in tavily_result and tavily_result.get("results"):
                # 转换为统一格式
                results = []
                for item in tavily_result["results"]:
                    results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("content", "")[:200],  # 限制长度
                        "url": item.get("url", ""),
                        "type": "tavily_search",
                        "score": item.get("score", 0.0)
                    })
                
                logger.info(f"✅ 使用Tavily AI搜索获取 {len(results)} 个结果")
                
                return {
                    "success": True,
                    "query": query,
                    "results": results,
                    "ai_answer": tavily_result.get("answer", "")  # Tavily的AI答案摘要
                }
        except Exception as e:
            logger.warning(f"⚠️  Tavily搜索失败: {e}，回退到Google/DuckDuckGo")
    
    # 回退到Google Custom Search API
    google_api_key = getattr(settings, 'GOOGLE_SEARCH_API_KEY', None)
    google_cse_id = getattr(settings, 'GOOGLE_CSE_ID', None)
    
    # Google Custom Search API需要API Key和CSE ID
    if google_api_key and google_api_key != "your-google-search-api-key-here" and google_cse_id:
        try:
            # 使用Google Custom Search API
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": google_api_key,
                "cx": google_cse_id,
                "q": query,
                "num": min(num_results, 10)  # Google API最多返回10个结果
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("items", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("link", ""),
                    "type": "google_search"
                })
            
            if results:
                logger.info(f"使用Google搜索API获取 {len(results)} 个结果")
                return {
                    "success": True,
                    "query": query,
                    "results": results
                }
        except Exception as e:
            logger.warning(f"Google搜索API失败: {e}，回退到DuckDuckGo")
    
    # 回退到DuckDuckGo API (免费，无需API key)
    try:
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
        
        logger.info(f"使用DuckDuckGo API获取 {len(results)} 个结果")
        return {
            "success": True,
            "query": query,
            "results": results[:num_results]
        }
        
    except Exception as e:
        logger.error(f"DuckDuckGo搜索失败: {e}")
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
        title = result.get("title", "")
        if snippet:
            if title:
                context_parts.append(f"[搜索结果{i} - {title}]: {snippet}")
            else:
                context_parts.append(f"[搜索结果{i}]: {snippet}")
    
    return "\n\n".join(context_parts)
