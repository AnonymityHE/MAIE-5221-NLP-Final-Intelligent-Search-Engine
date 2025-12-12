#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tavily AI Search 客户端
专为AI/RAG优化的搜索API
"""
import requests
import time
from typing import List, Dict, Optional, Any
from services.core import logger, settings

# 🔥 简单的内存缓存（避免重复搜索）
_search_cache = {}
_cache_ttl = 300  # 缓存5分钟


class TavilySearchClient:
    """
    Tavily AI Search 客户端
    
    特点：
    1. 返回AI友好的结构化结果
    2. 自动过滤低质量内容
    3. 支持深度搜索模式
    4. 多语言支持（包括中文）
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化Tavily客户端
        
        Args:
            api_key: Tavily API Key（格式：tvly-xxx）
        """
        self.api_key = api_key or getattr(settings, 'TAVILY_API_KEY', None)
        if not self.api_key:
            raise ValueError("Tavily API Key未配置")
        
        self.base_url = "https://api.tavily.com"
        self.search_endpoint = f"{self.base_url}/search"
        
        logger.info("✅ Tavily Search客户端已初始化")
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        include_answer: bool = True,
        include_raw_content: bool = False,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数（1-10）
            search_depth: 搜索深度
                - "basic": 快速搜索（推荐，适合大多数情况）
                - "advanced": 深度搜索（更全面，但慢一些）
            include_answer: 是否包含AI生成的答案摘要
            include_raw_content: 是否包含原始HTML内容
            include_domains: 限制搜索的域名列表
            exclude_domains: 排除的域名列表
            
        Returns:
            {
                "query": "原始查询",
                "answer": "AI生成的答案摘要（如果启用）",
                "results": [
                    {
                        "title": "标题",
                        "url": "URL",
                        "content": "清洗后的内容",
                        "score": 相关度分数（0-1）
                    }
                ],
                "response_time": 响应时间（秒）
            }
        """
        try:
            # 🔥 检查缓存
            cache_key = f"{query}_{max_results}_{search_depth}"
            if cache_key in _search_cache:
                cached_data, cached_time = _search_cache[cache_key]
                if time.time() - cached_time < _cache_ttl:
                    logger.info(f"⚡ 使用缓存结果（避免重复搜索）")
                    return cached_data
            
            # 构建请求
            payload = {
                "api_key": self.api_key,
                "query": query,
                "max_results": min(max_results, 10),  # Tavily限制最多10个
                "search_depth": search_depth,
                "include_answer": include_answer,
                "include_raw_content": include_raw_content
            }
            
            # 可选参数
            if include_domains:
                payload["include_domains"] = include_domains
            if exclude_domains:
                payload["exclude_domains"] = exclude_domains
            
            logger.info(f"🔍 Tavily搜索: '{query}' (max_results={max_results}, depth={search_depth})")
            
            # 发送请求
            response = requests.post(
                self.search_endpoint,
                json=payload,
                timeout=10  # 🔥 减少到10秒超时（原30秒）
            )
            
            response.raise_for_status()
            data = response.json()
            
            # 提取结果
            results = []
            for item in data.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "score": item.get("score", 0.0)
                })
            
            result = {
                "query": query,
                "answer": data.get("answer", ""),  # AI生成的答案摘要
                "results": results,
                "response_time": data.get("response_time", 0)
            }
            
            # 🔥 缓存结果
            _search_cache[cache_key] = (result, time.time())
            
            logger.info(f"✅ Tavily搜索成功: 找到{len(results)}个结果，响应时间{result['response_time']:.2f}秒")
            
            return result
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error("❌ Tavily API Key无效或已过期")
                return {"error": "Tavily API Key无效", "results": []}
            elif e.response.status_code == 429:
                logger.error("❌ Tavily API配额已用完")
                return {"error": "API配额已用完", "results": []}
            else:
                logger.error(f"❌ Tavily API错误: {e}")
                return {"error": str(e), "results": []}
        except Exception as e:
            logger.error(f"❌ Tavily搜索失败: {e}")
            return {"error": str(e), "results": []}
    
    def quick_search(self, query: str, max_results: int = 3) -> List[str]:
        """
        快速搜索，只返回内容列表（用于RAG）
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            
        Returns:
            内容列表
        """
        result = self.search(
            query=query,
            max_results=max_results,
            search_depth="basic",
            include_answer=False
        )
        
        if "error" in result:
            return []
        
        # 提取内容
        contents = []
        for item in result.get("results", []):
            content = item.get("content", "").strip()
            if content:
                contents.append(content)
        
        return contents
    
    def search_with_answer(self, query: str) -> str:
        """
        搜索并返回AI生成的答案摘要
        
        Args:
            query: 搜索查询
            
        Returns:
            AI答案摘要
        """
        result = self.search(
            query=query,
            max_results=5,
            search_depth="basic",
            include_answer=True
        )
        
        if "error" in result:
            return ""
        
        return result.get("answer", "")


# 全局单例
_tavily_client = None

def get_tavily_client() -> TavilySearchClient:
    """获取Tavily客户端单例"""
    global _tavily_client
    if _tavily_client is None:
        _tavily_client = TavilySearchClient()
    return _tavily_client

