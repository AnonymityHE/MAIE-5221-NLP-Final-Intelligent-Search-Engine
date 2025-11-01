#!/usr/bin/env python3
"""
Google搜索API测试脚本
用于验证Google Custom Search API配置是否正确
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.agent.tools.web_search_tool import web_search, get_web_search_context
from services.core.config import settings


def test_google_search():
    """测试Google搜索配置"""
    print("=" * 80)
    print("Google Custom Search API 配置测试")
    print("=" * 80)
    
    # 检查配置
    api_key = getattr(settings, 'GOOGLE_SEARCH_API_KEY', None)
    cse_id = getattr(settings, 'GOOGLE_CSE_ID', None)
    
    print(f"\n📋 配置检查:")
    print(f"  API Key: {api_key[:20]}..." if api_key else "  API Key: 未配置")
    print(f"  CSE ID: {cse_id if cse_id else '未配置'}")
    
    if not api_key or api_key == "your-google-search-api-key-here":
        print("\n❌ 错误: Google Search API Key未配置")
        return
    
    if not cse_id:
        print("\n⚠️  警告: Google CSE ID未配置，将使用DuckDuckGo作为备用")
        print("   要使用Google搜索，请按照 docs/GOOGLE_SEARCH_SETUP.md 配置CSE ID")
    
    # 测试搜索
    print(f"\n🔍 测试搜索查询: 'Python programming'")
    print("-" * 80)
    
    try:
        result = web_search("Python programming", num_results=3)
        
        print(f"✅ 搜索成功: {result['success']}")
        print(f"📊 结果数量: {len(result.get('results', []))} 个")
        
        if result['success'] and result.get('results'):
            print(f"\n📄 搜索结果:")
            for i, r in enumerate(result['results'][:3], 1):
                result_type = r.get('type', 'unknown')
                title = r.get('title', '无标题')[:50]
                snippet = r.get('snippet', '')[:100]
                print(f"\n  {i}. [{result_type}] {title}")
                print(f"     摘要: {snippet}...")
                if r.get('url'):
                    print(f"     URL: {r['url'][:70]}...")
        else:
            print(f"⚠️  未获取到搜索结果")
            if result.get('error'):
                print(f"   错误信息: {result['error']}")
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试上下文提取
    print(f"\n\n📝 测试上下文提取:")
    print("-" * 80)
    
    try:
        context = get_web_search_context("Python programming", num_results=2)
        if context:
            print("✅ 上下文提取成功:")
            print(context[:300] + "..." if len(context) > 300 else context)
        else:
            print("⚠️  未获取到上下文")
    except Exception as e:
        print(f"❌ 上下文提取失败: {e}")


if __name__ == "__main__":
    test_google_search()

