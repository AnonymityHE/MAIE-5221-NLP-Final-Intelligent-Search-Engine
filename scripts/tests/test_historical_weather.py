#!/usr/bin/env python3
"""
测试历史天气查询功能
验证Agent能够正确识别历史天气查询并使用web_search工具
"""

import sys
import os
import json
import requests

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

def print_separator(title: str = ""):
    """打印分隔线"""
    if title:
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    else:
        print("=" * 80 + "\n")

def test_current_weather_query():
    """测试当前天气查询（应该使用weather工具）"""
    print_separator("测试1: 当前天气查询")
    
    url = "http://localhost:8000/api/agent_query"
    query = "今天天气怎么样？"
    
    print(f"查询: {query}")
    print("预期: 使用weather工具\n")
    
    try:
        response = requests.post(url, json={"query": query}, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print(f"响应状态: {response.status_code}")
        print(f"使用的工具: {data.get('tools_used', [])}")
        print(f"回答: {data.get('answer', '')[:200]}...")
        
        # 验证
        tools_used = data.get('tools_used', [])
        if 'weather' in tools_used:
            print("✅ 测试通过：正确使用weather工具")
            return True
        else:
            print(f"⚠️  未使用weather工具，实际使用: {tools_used}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_historical_weather_query():
    """测试历史天气查询（应该使用web_search工具）"""
    print_separator("测试2: 历史天气查询（昨天）")
    
    url = "http://localhost:8000/api/agent_query"
    query = "昨天的天气怎么样？"
    
    print(f"查询: {query}")
    print("预期: 使用web_search工具（历史天气需要搜索）\n")
    
    try:
        response = requests.post(url, json={"query": query}, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print(f"响应状态: {response.status_code}")
        print(f"使用的工具: {data.get('tools_used', [])}")
        print(f"回答: {data.get('answer', '')[:300]}...")
        
        # 验证
        tools_used = data.get('tools_used', [])
        if 'web_search' in tools_used:
            print("✅ 测试通过：正确使用web_search工具（有结果）")
            return True
        elif 'web_search_attempted' in tools_used:
            print("✅ 测试通过：正确使用web_search工具（尝试搜索但无结果）")
            return True
        elif 'weather' in tools_used:
            print("❌ 测试失败：历史天气查询不应该使用weather工具")
            return False
        else:
            print(f"⚠️  未使用web_search工具，实际使用: {tools_used}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_historical_weather_query_english():
    """测试历史天气查询（英文）"""
    print_separator("测试3: 历史天气查询（英文）")
    
    url = "http://localhost:8000/api/agent_query"
    query = "What was the weather yesterday?"
    
    print(f"查询: {query}")
    print("预期: 使用web_search工具\n")
    
    try:
        response = requests.post(url, json={"query": query}, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print(f"响应状态: {response.status_code}")
        print(f"使用的工具: {data.get('tools_used', [])}")
        print(f"回答: {data.get('answer', '')[:300]}...")
        
        # 验证
        tools_used = data.get('tools_used', [])
        if 'web_search' in tools_used:
            print("✅ 测试通过：正确使用web_search工具（有结果）")
            return True
        elif 'web_search_attempted' in tools_used:
            print("✅ 测试通过：正确使用web_search工具（尝试搜索但无结果）")
            return True
        elif 'weather' in tools_used:
            print("❌ 测试失败：历史天气查询不应该使用weather工具")
            return False
        else:
            print(f"⚠️  未使用web_search工具，实际使用: {tools_used}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_historical_weather_with_location():
    """测试带地点的历史天气查询"""
    print_separator("测试4: 带地点的历史天气查询")
    
    url = "http://localhost:8000/api/agent_query"
    query = "Turves昨天的天气怎么样？"
    
    print(f"查询: {query}")
    print("预期: 使用web_search工具（历史天气需要搜索）\n")
    
    try:
        response = requests.post(url, json={"query": query}, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print(f"响应状态: {response.status_code}")
        print(f"使用的工具: {data.get('tools_used', [])}")
        print(f"回答: {data.get('answer', '')[:300]}...")
        
        # 验证
        tools_used = data.get('tools_used', [])
        if 'web_search' in tools_used:
            print("✅ 测试通过：正确使用web_search工具（有结果）")
            return True
        elif 'web_search_attempted' in tools_used:
            print("✅ 测试通过：正确使用web_search工具（尝试搜索但无结果）")
            return True
        elif 'weather' in tools_used:
            print("❌ 测试失败：历史天气查询不应该使用weather工具")
            return False
        else:
            print(f"⚠️  未使用web_search工具，实际使用: {tools_used}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_last_week_weather():
    """测试上周天气查询"""
    print_separator("测试5: 上周天气查询")
    
    url = "http://localhost:8000/api/agent_query"
    query = "上周的天气怎么样？"
    
    print(f"查询: {query}")
    print("预期: 使用web_search工具\n")
    
    try:
        response = requests.post(url, json={"query": query}, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print(f"响应状态: {response.status_code}")
        print(f"使用的工具: {data.get('tools_used', [])}")
        print(f"回答: {data.get('answer', '')[:300]}...")
        
        # 验证
        tools_used = data.get('tools_used', [])
        if 'web_search' in tools_used:
            print("✅ 测试通过：正确使用web_search工具（有结果）")
            return True
        elif 'web_search_attempted' in tools_used:
            print("✅ 测试通过：正确使用web_search工具（尝试搜索但无结果）")
            return True
        elif 'weather' in tools_used:
            print("❌ 测试失败：历史天气查询不应该使用weather工具")
            return False
        else:
            print(f"⚠️  未使用web_search工具，实际使用: {tools_used}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("\n" + "=" * 80)
    print("  历史天气查询功能测试")
    print("=" * 80)
    
    # 检查API是否运行
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code != 200:
            print("❌ API服务未运行，请先启动: uvicorn backend.main:app --reload")
            return
    except Exception:
        print("❌ 无法连接到API服务，请先启动: uvicorn backend.main:app --reload")
        return
    
    print("✅ API服务运行正常\n")
    
    # 运行测试
    results = []
    
    results.append(("当前天气查询", test_current_weather_query()))
    results.append(("历史天气查询（昨天）", test_historical_weather_query()))
    results.append(("历史天气查询（英文）", test_historical_weather_query_english()))
    results.append(("带地点的历史天气查询", test_historical_weather_with_location()))
    results.append(("上周天气查询", test_last_week_weather()))
    
    # 打印总结
    print_separator("测试总结")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")

if __name__ == "__main__":
    main()

