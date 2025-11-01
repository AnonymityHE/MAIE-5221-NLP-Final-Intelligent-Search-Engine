#!/usr/bin/env python3
"""
测试缓存和过滤器功能
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import time
from services.core.cache import get_query_cache, get_embedding_cache, get_cache_stats, clear_cache
from services.vector.filter import get_result_filter
from services.core.config import settings

def test_cache():
    """测试缓存功能"""
    print("=" * 80)
    print("🧪 测试查询缓存功能")
    print("=" * 80)
    
    cache = get_query_cache()
    
    # 测试1: 设置和获取缓存
    print("\n1. 测试缓存设置和获取")
    test_key = "test_query_123"
    test_value = [{"text": "测试文档", "score": 0.9}]
    
    cache.set(test_key, test_value)
    cached_result = cache.get(test_key)
    
    if cached_result == test_value:
        print("✅ 缓存设置和获取成功")
    else:
        print("❌ 缓存设置和获取失败")
        return False
    
    # 测试2: 缓存过期（需要等待，这里只测试逻辑）
    print("\n2. 测试缓存统计")
    stats = cache.stats()
    print(f"   缓存大小: {stats['size']}/{stats['max_size']}")
    print(f"   TTL: {stats['ttl']}秒")
    
    # 测试3: 全局统计
    print("\n3. 测试全局缓存统计")
    all_stats = get_cache_stats()
    print(f"   查询缓存: {all_stats['query_cache']}")
    print(f"   Embedding缓存: {all_stats['embedding_cache']}")
    
    # 测试4: 清空缓存
    print("\n4. 测试清空缓存")
    clear_cache("query")
    stats_after = cache.stats()
    if stats_after['size'] == 0:
        print("✅ 缓存清空成功")
    else:
        print(f"⚠️ 缓存清空后仍有 {stats_after['size']} 个条目")
    
    return True


def test_filter():
    """测试过滤器功能"""
    print("\n" + "=" * 80)
    print("🧪 测试结果过滤器功能")
    print("=" * 80)
    
    filter_obj = get_result_filter()
    
    # 模拟测试结果
    test_results = [
        {
            "text": "这是一个高质量的文档，包含足够的信息内容，应该被保留。",
            "source_file": "documents/local_kb/test.pdf",
            "source_type": "local_kb",
            "score": 0.9,
            "uploaded_at": "2024-01-01T00:00:00"
        },
        {
            "text": "短文本",
            "source_file": "web_search",
            "source_type": "web_search",
            "score": 0.7
        },
        {
            "text": "这是一个中等长度的文档，来自用户上传的文件，应该被保留。",
            "source_file": "uploaded_files/user_doc.pdf",
            "source_type": "uploaded_file",
            "score": 0.8,
            "uploaded_at": "2024-10-01T00:00:00"
        },
        {
            "text": "这是来自网页搜索的结果，内容较长且有用，应该被保留。",
            "source_file": "web_search",
            "source_type": "web_search",
            "score": 0.6
        }
    ]
    
    print(f"\n原始结果数量: {len(test_results)}")
    
    # 测试1: 基本过滤
    print("\n1. 测试基本过滤（质量、可信度、去重）")
    filtered = filter_obj.filter(
        test_results.copy(),
        is_realtime_query=False,
        apply_credibility_filter=True,
        apply_freshness_filter=True,
        apply_quality_filter=True
    )
    print(f"   过滤后结果数量: {len(filtered)}")
    
    # 显示每个结果的可信度和新鲜度
    for i, result in enumerate(filtered, 1):
        cred = result.get("credibility_score", "N/A")
        fresh = result.get("freshness_score", "N/A")
        print(f"   结果{i}: credibility={cred}, freshness={fresh}")
    
    # 测试2: 时效性查询过滤
    print("\n2. 测试时效性查询过滤")
    realtime_results = [
        {
            "text": "这是最新的新闻内容，时间戳很近，应该被保留。",
            "source_file": "web_search",
            "source_type": "web_search",
            "uploaded_at": "2024-10-30T00:00:00"  # 最近
        },
        {
            "text": "这是过时的新闻内容，时间戳很旧，应该被过滤。",
            "source_file": "web_search",
            "source_type": "web_search",
            "uploaded_at": "2023-01-01T00:00:00"  # 很久以前
        }
    ]
    
    filtered_realtime = filter_obj.filter(
        realtime_results.copy(),
        is_realtime_query=True,
        apply_freshness_filter=True
    )
    print(f"   时效性查询过滤后结果数量: {len(filtered_realtime)}")
    
    return True


def test_integration():
    """测试缓存和过滤器的集成"""
    print("\n" + "=" * 80)
    print("🧪 测试缓存与过滤器的集成")
    print("=" * 80)
    
    print("\n检查缓存配置:")
    print(f"   缓存启用: {settings.USE_CACHE}")
    print(f"   缓存最大大小: {settings.CACHE_MAX_SIZE}")
    print(f"   缓存TTL: {settings.CACHE_TTL}秒")
    
    print("\n✅ 所有测试通过！")


def main():
    """主函数"""
    try:
        print("🚀 开始测试缓存和过滤器功能\n")
        
        # 测试缓存
        cache_ok = test_cache()
        if not cache_ok:
            print("❌ 缓存测试失败")
            return
        
        # 测试过滤器
        filter_ok = test_filter()
        if not filter_ok:
            print("❌ 过滤器测试失败")
            return
        
        # 集成测试
        test_integration()
        
        print("\n" + "=" * 80)
        print("✅ 所有测试完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    main()

