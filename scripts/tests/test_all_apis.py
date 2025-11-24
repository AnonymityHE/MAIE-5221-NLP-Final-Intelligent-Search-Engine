#!/usr/bin/env python3
"""
测试所有API连接
检查HKGAI、Doubao、Tavily、Yahoo Finance等API是否可用
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.core.config import settings
from services.core.logger import logger
import asyncio

def print_section(title: str):
    """打印章节标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_result(name: str, status: str, details: str = ""):
    """打印测试结果"""
    status_icon = "✅" if status == "OK" else "❌"
    print(f"{status_icon} {name}: {status}")
    if details:
        print(f"   └─ {details}")

async def test_hkgai():
    """测试HKGAI API"""
    print_section("1. HKGAI API 测试")
    
    try:
        from services.llm.unified_client import UnifiedLLMClient
        
        # 检查API key
        if not settings.HKGAI_API_KEY:
            print_result("HKGAI API Key", "MISSING", "请在.env文件中设置HKGAI_API_KEY")
            return False
        
        print_result("HKGAI API Key", "OK", f"已配置 (前10位: {settings.HKGAI_API_KEY[:10]}...)")
        print(f"   Base URL: {settings.HKGAI_BASE_URL}")
        print(f"   Model: {settings.HKGAI_MODEL_ID}")
        
        # 测试调用
        print("\n测试调用中...")
        client = UnifiedLLMClient()
        response = await client.generate(
            query="Hello, this is a test. Reply with 'OK' only.",
            context=[],
            max_tokens=10
        )
        
        if response:
            print_result("HKGAI API 调用", "OK", f"响应: {response[:50]}...")
            return True
        else:
            print_result("HKGAI API 调用", "FAILED", "未返回响应")
            return False
            
    except Exception as e:
        print_result("HKGAI API", "ERROR", str(e))
        return False

async def test_doubao():
    """测试Doubao API"""
    print_section("2. Doubao API 测试")
    
    try:
        from services.llm.doubao_multimodal import DoubaoMultimodalClient
        
        # 检查API key
        if not settings.DOUBAO_API_KEY:
            print_result("Doubao API Key", "MISSING", "请在.env文件中设置DOUBAO_API_KEY")
            return False
        
        print_result("Doubao API Key", "OK", f"已配置 (前10位: {settings.DOUBAO_API_KEY[:10]}...)")
        print(f"   Model: {settings.DOUBAO_DEFAULT_MODEL}")
        print(f"   Lite Model: {settings.DOUBAO_LITE_MODEL}")
        
        # 测试调用（纯文本）
        print("\n测试调用中...")
        client = DoubaoMultimodalClient(model_name=settings.DOUBAO_LITE_MODEL)
        
        response = await client.query_with_images(
            query="Hello, this is a test. Reply with 'OK' only.",
            images=[]
        )
        
        if response:
            print_result("Doubao API 调用", "OK", f"响应: {response[:50]}...")
            return True
        else:
            print_result("Doubao API 调用", "FAILED", "未返回响应")
            return False
            
    except Exception as e:
        print_result("Doubao API", "ERROR", str(e))
        return False

async def test_tavily():
    """测试Tavily API"""
    print_section("3. Tavily AI Search 测试")
    
    try:
        # 检查API key
        if not settings.TAVILY_API_KEY:
            print_result("Tavily API Key", "MISSING", "请在.env文件中设置TAVILY_API_KEY")
            return False
        
        print_result("Tavily API Key", "OK", f"已配置 (前10位: {settings.TAVILY_API_KEY[:10]}...)")
        
        # 测试调用
        print("\n测试调用中...")
        from services.tools.tavily_search import tavily_search
        
        result = await tavily_search("test query")
        
        if result and "error" not in result.lower():
            print_result("Tavily API 调用", "OK", f"返回 {len(result)} 字符的结果")
            return True
        else:
            print_result("Tavily API 调用", "FAILED", result[:100] if result else "无响应")
            return False
            
    except Exception as e:
        print_result("Tavily API", "ERROR", str(e))
        return False

async def test_yfinance():
    """测试Yahoo Finance"""
    print_section("4. Yahoo Finance (yfinance) 测试")
    
    try:
        import yfinance as yf
        
        print("测试获取股票数据中...")
        
        # 测试获取苹果股票数据
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        
        if info and 'currentPrice' in info:
            print_result("Yahoo Finance", "OK", f"AAPL 当前价格: ${info.get('currentPrice', 'N/A')}")
            return True
        else:
            print_result("Yahoo Finance", "WARNING", "可以连接但数据可能不完整")
            return True
            
    except Exception as e:
        print_result("Yahoo Finance", "ERROR", str(e))
        return False

async def test_weather():
    """测试天气API"""
    print_section("5. OpenWeatherMap API 测试")
    
    try:
        # OpenWeatherMap不需要在settings中配置，可能在agent tools中
        from services.agent.tools.weather_tool import get_weather
        
        print("测试获取天气数据中...")
        result = await get_weather("Hong Kong")
        
        if result and "error" not in result.lower():
            print_result("Weather API", "OK", f"成功获取香港天气: {result[:100]}...")
            return True
        else:
            print_result("Weather API", "FAILED", result[:100] if result else "无响应")
            return False
            
    except Exception as e:
        print_result("Weather API", "ERROR", str(e))
        logger.info("提示: 天气API可能需要在.env中配置OPENWEATHER_API_KEY")
        return False

async def test_edge_tts():
    """测试Edge TTS"""
    print_section("6. Edge TTS 测试")
    
    try:
        import edge_tts
        
        print("测试Edge TTS (不需要API key)...")
        
        # 列出可用的语音
        voices = await edge_tts.list_voices()
        cantonese_voices = [v for v in voices if 'zh-HK' in v['Locale']]
        
        if cantonese_voices:
            print_result("Edge TTS", "OK", f"找到 {len(cantonese_voices)} 个粤语语音")
            print(f"   └─ 粤语语音示例: {cantonese_voices[0]['ShortName']}")
            return True
        else:
            print_result("Edge TTS", "WARNING", "未找到粤语语音")
            return True
            
    except Exception as e:
        print_result("Edge TTS", "ERROR", str(e))
        return False

async def main():
    """主测试流程"""
    print("\n" + "🔍 Jude API 连通性测试".center(60, "="))
    print(f"项目路径: {project_root}")
    
    # 运行所有测试
    results = {
        "HKGAI": await test_hkgai(),
        "Doubao": await test_doubao(),
        "Tavily": await test_tavily(),
        "Yahoo Finance": await test_yfinance(),
        "Weather API": await test_weather(),
        "Edge TTS": await test_edge_tts(),
    }
    
    # 总结
    print_section("测试总结")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {name}")
    
    print(f"\n通过: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有API测试通过！系统已准备好进行Presentation！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个API测试失败，请检查配置")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

