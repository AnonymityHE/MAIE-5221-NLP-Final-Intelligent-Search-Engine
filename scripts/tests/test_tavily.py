#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tavily AI Search 集成测试
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.tools.tavily_search import get_tavily_client
from services.core import logger


def test_tavily_basic():
    """测试基础搜索"""
    print("=" * 80)
    print("🧪 测试1: 基础搜索")
    print("=" * 80)
    
    try:
        client = get_tavily_client()
        
        query = "What is HKUST?"
        print(f"查询: {query}")
        
        result = client.search(
            query=query,
            max_results=3,
            include_answer=True
        )
        
        if "error" in result:
            print(f"❌ 搜索失败: {result['error']}")
            return False
        
        print(f"\n✅ 搜索成功！")
        print(f"\n🤖 AI答案摘要:")
        print(result.get("answer", "无"))
        
        print(f"\n📝 搜索结果 ({len(result['results'])}个):")
        for i, item in enumerate(result["results"], 1):
            print(f"\n{i}. {item['title']}")
            print(f"   URL: {item['url']}")
            print(f"   相关度: {item['score']:.2f}")
            print(f"   内容: {item['content'][:150]}...")
        
        print(f"\n⏱️  响应时间: {result['response_time']:.2f}秒")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_tavily_chinese():
    """测试中文搜索"""
    print("\n" + "=" * 80)
    print("🧪 测试2: 中文搜索")
    print("=" * 80)
    
    try:
        client = get_tavily_client()
        
        query = "香港科技大学在哪里？"
        print(f"查询: {query}")
        
        result = client.search(
            query=query,
            max_results=3,
            include_answer=True
        )
        
        if "error" in result:
            print(f"❌ 搜索失败: {result['error']}")
            return False
        
        print(f"\n✅ 搜索成功！")
        print(f"\n🤖 AI答案摘要:")
        print(result.get("answer", "无"))
        
        print(f"\n📝 搜索结果 ({len(result['results'])}个):")
        for i, item in enumerate(result["results"], 1):
            print(f"\n{i}. {item['title']}")
            print(f"   内容: {item['content'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_tavily_realtime():
    """测试实时信息搜索"""
    print("\n" + "=" * 80)
    print("🧪 测试3: 实时信息搜索")
    print("=" * 80)
    
    try:
        client = get_tavily_client()
        
        query = "Hong Kong weather today"
        print(f"查询: {query}")
        
        result = client.search(
            query=query,
            max_results=3,
            include_answer=True,
            search_depth="advanced"  # 使用深度搜索
        )
        
        if "error" in result:
            print(f"❌ 搜索失败: {result['error']}")
            return False
        
        print(f"\n✅ 搜索成功！")
        print(f"\n🤖 AI答案摘要:")
        print(result.get("answer", "无"))
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_web_search_tool():
    """测试集成到web_search工具"""
    print("\n" + "=" * 80)
    print("🧪 测试4: Web Search工具集成")
    print("=" * 80)
    
    try:
        from services.agent.tools.web_search_tool import web_search
        
        query = "Best ramen restaurant in Causeway Bay"
        print(f"查询: {query}")
        
        result = web_search(query=query, num_results=3)
        
        if not result.get("success"):
            print(f"❌ 搜索失败")
            return False
        
        print(f"\n✅ 搜索成功！")
        print(f"\n📝 搜索结果 ({len(result['results'])}个):")
        for i, item in enumerate(result["results"], 1):
            print(f"\n{i}. {item['title']}")
            print(f"   {item['snippet'][:100]}...")
        
        # 如果有AI答案摘要
        if result.get("ai_answer"):
            print(f"\n🤖 AI答案摘要:")
            print(result["ai_answer"])
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 100)
    print("🖼️  Tavily AI Search 集成测试")
    print("=" * 100)
    
    # 检查API Key
    from services.core import settings
    tavily_key = getattr(settings, 'TAVILY_API_KEY', None)
    
    if not tavily_key:
        print("\n❌ 错误: 未配置TAVILY_API_KEY")
        print("\n请在.env文件中添加:")
        print("TAVILY_API_KEY=tvly-xxxxxxxxxx")
        print("\n获取API Key: https://tavily.com")
        return
    
    print(f"\n✅ Tavily API Key已配置: {tavily_key[:10]}...")
    
    # 运行测试
    results = []
    
    results.append(("基础搜索", test_tavily_basic()))
    results.append(("中文搜索", test_tavily_chinese()))
    results.append(("实时信息", test_tavily_realtime()))
    results.append(("工具集成", test_web_search_tool()))
    
    # 汇总
    print("\n" + "=" * 100)
    print("📊 测试总结")
    print("=" * 100)
    
    success_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计: {success_count}/{total_count} 通过")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print("\n🎉 所有测试通过！Tavily集成成功！")
    else:
        print("\n⚠️  部分测试失败，请检查配置")
    
    print("=" * 100)


if __name__ == "__main__":
    main()

