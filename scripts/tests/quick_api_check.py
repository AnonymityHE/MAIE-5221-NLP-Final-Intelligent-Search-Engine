#!/usr/bin/env python3
"""
快速检查所有API连接状态
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.core.config import settings
from services.core.logger import logger

def check_api_keys():
    """检查所有API Key配置"""
    print("\n" + "="*60)
    print("  API Keys 配置检查")
    print("="*60)
    
    apis = {
        "HKGAI API Key": settings.HKGAI_API_KEY,
        "Doubao API Key": settings.DOUBAO_API_KEY,
        "Tavily API Key": settings.TAVILY_API_KEY,
        "Gemini API Key": settings.GEMINI_API_KEY if hasattr(settings, 'GEMINI_API_KEY') else None,
    }
    
    results = {}
    for name, key in apis.items():
        if key and len(key) > 0:
            print(f"✅ {name}: 已配置 ({key[:10]}...)")
            results[name] = True
        else:
            print(f"❌ {name}: 未配置")
            results[name] = False
    
    return results

def test_hkgai():
    """测试HKGAI API"""
    print("\n" + "="*60)
    print("  HKGAI API 测试")
    print("="*60)
    
    if not settings.HKGAI_API_KEY:
        print("❌ HKGAI API Key 未配置")
        return False
    
    try:
        from services.llm.hkgai_client import HKGAIClient
        
        client = HKGAIClient()
        result = client.chat(
            system_prompt="You are a helpful assistant.",
            user_prompt="Say 'OK' only.",
            max_tokens=10
        )
        
        if result and "content" in result and not "error" in result:
            print(f"✅ HKGAI API 连接成功")
            print(f"   响应: {result['content'][:50]}...")
            return True
        else:
            print(f"❌ HKGAI API 调用失败")
            if "error" in result:
                print(f"   错误: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ HKGAI API 测试出错: {str(e)}")
        return False

def test_doubao():
    """测试Doubao API"""
    print("\n" + "="*60)
    print("  Doubao API 测试")
    print("="*60)
    
    if not settings.DOUBAO_API_KEY:
        print("❌ Doubao API Key 未配置")
        return False
    
    try:
        import asyncio
        from openai import OpenAI
        
        # 使用OpenAI SDK测试Doubao
        client = OpenAI(
            api_key=settings.DOUBAO_API_KEY,
            base_url="https://ark.cn-beijing.volces.com/api/v3"
        )
        
        response = client.chat.completions.create(
            model=settings.DOUBAO_LITE_MODEL,
            messages=[
                {"role": "user", "content": "Say 'OK' only."}
            ],
            max_tokens=10
        )
        
        if response and response.choices:
            print(f"✅ Doubao API 连接成功")
            print(f"   响应: {response.choices[0].message.content}")
            return True
        else:
            print(f"❌ Doubao API 调用失败")
            return False
            
    except Exception as e:
        print(f"❌ Doubao API 测试出错: {str(e)}")
        return False

def test_tavily():
    """测试Tavily API"""
    print("\n" + "="*60)
    print("  Tavily AI Search 测试")
    print("="*60)
    
    if not settings.TAVILY_API_KEY:
        print("❌ Tavily API Key 未配置")
        return False
    
    try:
        from tavily import TavilyClient
        
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        result = client.search("test", max_results=1)
        
        if result and 'results' in result:
            print(f"✅ Tavily API 连接成功")
            print(f"   返回 {len(result['results'])} 个搜索结果")
            return True
        else:
            print(f"❌ Tavily API 调用失败")
            return False
            
    except Exception as e:
        print(f"❌ Tavily API 测试出错: {str(e)}")
        return False

def test_edge_tts():
    """测试Edge TTS"""
    print("\n" + "="*60)
    print("  Edge TTS 测试")
    print("="*60)
    
    try:
        import edge_tts
        import asyncio
        
        async def check():
            voices = await edge_tts.list_voices()
            cantonese = [v for v in voices if 'zh-HK' in v['Locale']]
            return cantonese
        
        cantonese_voices = asyncio.run(check())
        
        if cantonese_voices:
            print(f"✅ Edge TTS 可用")
            print(f"   找到 {len(cantonese_voices)} 个粤语语音")
            print(f"   示例: {cantonese_voices[0]['ShortName']}")
            return True
        else:
            print(f"⚠️  Edge TTS 可用但未找到粤语语音")
            return True
            
    except Exception as e:
        print(f"❌ Edge TTS 测试出错: {str(e)}")
        return False

def main():
    """主测试流程"""
    print("\n" + "🔍 Jude API 快速检查".center(60, "="))
    print(f"项目路径: {project_root}\n")
    
    # 检查API Keys
    api_keys = check_api_keys()
    
    # 测试各个API
    results = {}
    
    if api_keys.get("HKGAI API Key"):
        results["HKGAI"] = test_hkgai()
    else:
        results["HKGAI"] = False
    
    if api_keys.get("Doubao API Key"):
        results["Doubao"] = test_doubao()
    else:
        results["Doubao"] = False
    
    if api_keys.get("Tavily API Key"):
        results["Tavily"] = test_tavily()
    else:
        results["Tavily"] = False
    
    results["Edge TTS"] = test_edge_tts()
    
    # 总结
    print("\n" + "="*60)
    print("  测试总结")
    print("="*60)
    
    for name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {name}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n通过: {passed}/{total}")
    
    # 关键API检查
    critical_apis = ["HKGAI", "Doubao", "Edge TTS"]
    critical_passed = all(results.get(api, False) for api in critical_apis)
    
    if critical_passed:
        print("\n🎉 关键API全部通过！系统已准备好进行Presentation！")
        print("\n✨ 可用功能:")
        print("  - 文本查询 (HKGAI)")
        print("  - 图片识别 (Doubao)")
        print("  - 语音合成 (Edge TTS)")
        if results.get("Tavily"):
            print("  - Web搜索 (Tavily)")
        return 0
    else:
        print("\n⚠️  关键API测试失败，请检查配置:")
        for api in critical_apis:
            if not results.get(api, False):
                print(f"  ❌ {api}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

