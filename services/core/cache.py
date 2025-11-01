"""
查询缓存模块
用于缓存常见查询结果，提升Search Time性能
"""
import hashlib
import json
import time
from typing import Any, Optional, Dict, List
from functools import wraps
from collections import OrderedDict
from services.core.logger import logger


class LRUCache:
    """LRU缓存实现"""
    
    def __init__(self, max_size: int = 100, ttl: int = 3600):
        """
        初始化LRU缓存
        
        Args:
            max_size: 最大缓存条目数
            ttl: 缓存过期时间（秒），默认1小时
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, float] = {}
        logger.info(f"初始化LRU缓存: max_size={max_size}, ttl={ttl}s")
    
    def _is_expired(self, key: str) -> bool:
        """检查缓存是否过期"""
        if key not in self.timestamps:
            return True
        elapsed = time.time() - self.timestamps[key]
        return elapsed > self.ttl
    
    def _clean_expired(self):
        """清理过期缓存"""
        expired_keys = [
            k for k in self.timestamps.keys()
            if self._is_expired(k)
        ]
        for key in expired_keys:
            self.cache.pop(key, None)
            self.timestamps.pop(key, None)
        if expired_keys:
            logger.debug(f"清理了 {len(expired_keys)} 个过期缓存项")
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或已过期则返回None
        """
        # 先清理过期项
        self._clean_expired()
        
        if key in self.cache:
            if not self._is_expired(key):
                # 移到末尾（最近使用）
                self.cache.move_to_end(key)
                logger.debug(f"缓存命中: {key[:50]}...")
                return self.cache[key]
            else:
                # 已过期，删除
                self.cache.pop(key, None)
                self.timestamps.pop(key, None)
                logger.debug(f"缓存已过期: {key[:50]}...")
        
        return None
    
    def set(self, key: str, value: Any):
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
        """
        # 先清理过期项
        self._clean_expired()
        
        # 如果超过最大大小，删除最旧的项
        if len(self.cache) >= self.max_size and key not in self.cache:
            # 删除最旧的项（第一个）
            oldest_key = next(iter(self.cache))
            self.cache.pop(oldest_key)
            self.timestamps.pop(oldest_key, None)
            logger.debug(f"缓存已满，删除最旧项: {oldest_key[:50]}...")
        
        # 添加新项
        self.cache[key] = value
        self.timestamps[key] = time.time()
        self.cache.move_to_end(key)
        logger.debug(f"缓存已设置: {key[:50]}... (当前大小: {len(self.cache)})")
    
    def clear(self):
        """清空所有缓存"""
        self.cache.clear()
        self.timestamps.clear()
        logger.info("缓存已清空")
    
    def stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        self._clean_expired()
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl": self.ttl
        }


def _generate_cache_key(query: str, extra_params: Optional[Dict] = None) -> str:
    """
    生成缓存键
    
    Args:
        query: 查询文本
        extra_params: 额外参数（如num_results, model等）
        
    Returns:
        MD5哈希后的缓存键
    """
    # 标准化查询（小写，去除多余空格）
    normalized_query = " ".join(query.lower().split())
    
    # 合并参数
    cache_data = {"query": normalized_query}
    if extra_params:
        # 只包含影响结果的参数
        relevant_params = {
            "num_results": extra_params.get("num_results"),
            "model": extra_params.get("model"),
        }
        cache_data.update(relevant_params)
    
    # 生成MD5哈希
    cache_str = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)
    cache_key = hashlib.md5(cache_str.encode('utf-8')).hexdigest()
    
    return cache_key


# 全局缓存实例
_query_cache = LRUCache(max_size=200, ttl=3600)  # 200个条目，1小时TTL
_embedding_cache = LRUCache(max_size=500, ttl=7200)  # 500个条目，2小时TTL


def get_query_cache() -> LRUCache:
    """获取查询结果缓存实例"""
    return _query_cache


def get_embedding_cache() -> LRUCache:
    """获取embedding向量缓存实例"""
    return _embedding_cache


def cached_query(cache_key_func=None, use_cache: bool = True):
    """
    查询结果缓存装饰器
    
    Args:
        cache_key_func: 自定义缓存键生成函数
        use_cache: 是否启用缓存（可通过配置关闭）
        
    Example:
        @cached_query()
        def search(query: str, num_results: int = 5):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 检查是否启用缓存
            if not use_cache:
                return func(*args, **kwargs)
            
            # 生成缓存键
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                # 默认：使用第一个位置参数（通常是query）和kwargs
                query = args[0] if args else kwargs.get("query", "")
                extra_params = kwargs.copy()
                cache_key = _generate_cache_key(query, extra_params)
            
            # 尝试从缓存获取
            cache = get_query_cache()
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"查询缓存命中: {args[0][:50] if args else 'N/A'}...")
                return cached_result
            
            # 缓存未命中，执行函数
            result = func(*args, **kwargs)
            
            # 存储到缓存
            cache.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


def clear_cache(cache_type: str = "all"):
    """
    清空缓存
    
    Args:
        cache_type: 缓存类型 ("query", "embedding", "all")
    """
    if cache_type in ("query", "all"):
        _query_cache.clear()
    if cache_type in ("embedding", "all"):
        _embedding_cache.clear()
    logger.info(f"已清空缓存: {cache_type}")


def get_cache_stats() -> Dict[str, Dict[str, Any]]:
    """获取所有缓存的统计信息"""
    return {
        "query_cache": _query_cache.stats(),
        "embedding_cache": _embedding_cache.stats()
    }

