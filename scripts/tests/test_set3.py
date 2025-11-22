#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Set 3 - 复杂场景测试
包含多模态输入、跨域查询、实时数据等
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import json
import time
from datetime import datetime

# 测试问题集（暂时跳过需要图片输入的问题）
TEST_QUESTIONS = [
    # 英文问题（非图片）
    {
        "id": "EN-4",
        "question": "Compare the stock performance of NVIDIA (NVDA) and AMD over the last 5 days and summarize the top 3 reasons that might have influenced these movements.",
        "language": "en",
        "expected_tools": ["finance", "web_search"]
    },
    {
        "id": "EN-5",
        "question": "I want to go hiking this Sunday in Sai Kung. Check the weather forecast for Sunday and suggest a trail that is safe for those conditions (avoid slippery routes if raining).",
        "language": "en",
        "expected_tools": ["weather", "web_search"]
    },
    {
        "id": "EN-6",
        "question": "Find a restaurant in Causeway Bay that serves Japanese Ramen and is currently open.",
        "language": "en",
        "expected_tools": ["web_search"]
    },
    {
        "id": "EN-7",
        "question": "Who won the Best Actor award at the most recent Hong Kong Film Awards, and what is the Douban score of the movie they won for?",
        "language": "en",
        "expected_tools": ["web_search"]
    },
    {
        "id": "EN-8",
        "question": "Identify the winner of the most recent UEFA Champions League final, and list the goal scorers for that match along with the minute they scored.",
        "language": "en",
        "expected_tools": ["web_search"]
    },
    {
        "id": "EN-9",
        "question": "What are the departure times for the Bus 91M from Diamond Hill station?",
        "language": "en",
        "expected_tools": ["transport", "web_search"]
    },
    {
        "id": "EN-10",
        "question": "What is the current exchange rate between HKD and JPY, and how much is 50,000 Yen in HKD right now?",
        "language": "en",
        "expected_tools": ["finance"]
    },
    {
        "id": "EN-11",
        "question": "What is the current Air Quality Health Index (AQHI) at the Central/Western monitoring station, and is the health risk considered 'High'?",
        "language": "en",
        "expected_tools": ["web_search"]
    },
    {
        "id": "EN-12",
        "question": "Find the next scheduled concert or public event at the Hong Kong Coliseum",
        "language": "en",
        "expected_tools": ["web_search"]
    },
    
    # 中文问题（非图片）
    {
        "id": "CN-4",
        "question": "比較 NVIDIA (NVDA) 和 AMD 過去 5 天的股價表現，並總結可能影響這些波動的前 3 條原因。",
        "language": "zh",
        "expected_tools": ["finance", "web_search"]
    },
    {
        "id": "CN-5",
        "question": "我這週日想去西貢遠足。請查詢週日的天氣預報，並根據天氣狀況推薦一條安全的路線（如果下雨，請避免濕滑路段）。",
        "language": "zh",
        "expected_tools": ["weather", "web_search"]
    },
    {
        "id": "CN-6",
        "question": "在銅鑼灣找一家目前正在營業的日式拉麵餐廳。",
        "language": "zh",
        "expected_tools": ["web_search"]
    },
    {
        "id": "CN-7",
        "question": "誰在最近一屆香港電影金像獎中獲得了最佳男主角？他獲獎電影的豆瓣評分是多少？",
        "language": "zh",
        "expected_tools": ["web_search"]
    },
    {
        "id": "CN-8",
        "question": "找出最近一屆歐洲冠軍聯賽 (UEFA Champions League) 決賽的獲勝隊伍，並列出該場比賽的進球球員及其進球時間（分鐘）。",
        "language": "zh",
        "expected_tools": ["web_search"]
    },
    {
        "id": "CN-9",
        "question": "從鑽石山站開出的91M巴士的發車時間是什麼時候？",
        "language": "zh",
        "expected_tools": ["transport", "web_search"]
    },
    {
        "id": "CN-10",
        "question": "目前港幣 (HKD) 與日元 (JPY) 的匯率是多少？50,000 日元現在等於多少港幣？",
        "language": "zh",
        "expected_tools": ["finance"]
    },
    {
        "id": "CN-11",
        "question": '查詢中西區監測站目前的空氣質素健康指數 (AQHI)，並判斷該健康風險級別是否屬於"高"？',
        "language": "zh",
        "expected_tools": ["web_search"]
    },
    {
        "id": "CN-12",
        "question": "找出香港體育館 (紅館) 下一個預定舉行的演唱會或公開活動",
        "language": "zh",
        "expected_tools": ["web_search"]
    },
]


def test_question(question_data: dict, base_url: str = "http://localhost:8000") -> dict:
    """测试单个问题"""
    import requests
    
    print(f"\n{'='*80}")
    print(f"测试ID: {question_data['id']}")
    print(f"问题: {question_data['question']}")
    print(f"语言: {question_data['language']}")
    print(f"预期工具: {', '.join(question_data['expected_tools'])}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{base_url}/api/agent_query",
            json={"query": question_data["question"], "use_agent": True},
            timeout=120  # 增加超时时间以应对复杂查询
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ 查询成功 (耗时: {elapsed:.2f}秒)")
            print(f"\n📝 回答:")
            print(result.get("answer", "无答案"))
            
            # 分析元数据
            metadata = result.get("metadata", {})
            tools_used = metadata.get("tools_used", [])
            
            print(f"\n🔧 使用工具: {', '.join(tools_used) if tools_used else '无'}")
            print(f"📊 置信度: {metadata.get('confidence', 'N/A')}")
            print(f"🤖 使用LLM: {metadata.get('llm_provider', 'N/A')}")
            
            # 检查工具使用是否符合预期
            expected_tools = set(question_data['expected_tools'])
            actual_tools = set(tools_used)
            
            if expected_tools & actual_tools:  # 有交集
                print(f"✅ 工具调用合理（命中: {expected_tools & actual_tools}）")
            else:
                print(f"⚠️  工具调用可能不准确（预期: {expected_tools}, 实际: {actual_tools}）")
            
            return {
                "id": question_data["id"],
                "success": True,
                "elapsed": elapsed,
                "tools_used": tools_used,
                "answer_length": len(result.get("answer", "")),
                "llm_provider": metadata.get("llm_provider", "unknown")
            }
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return {
                "id": question_data["id"],
                "success": False,
                "error": response.text
            }
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ 测试出错 (耗时: {elapsed:.2f}秒): {str(e)}")
        return {
            "id": question_data["id"],
            "success": False,
            "error": str(e)
        }


def main():
    print("=" * 100)
    print("🧪 Test Set 3 - 复杂场景测试")
    print("=" * 100)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试问题数: {len(TEST_QUESTIONS)}")
    print(f"注意: 暂时跳过需要图片输入的问题")
    print("=" * 100)
    
    results = []
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n\n{'#'*100}")
        print(f"进度: {i}/{len(TEST_QUESTIONS)}")
        print(f"{'#'*100}")
        
        result = test_question(question)
        results.append(result)
        
        # 每个问题之间等待2秒，避免过载
        if i < len(TEST_QUESTIONS):
            print("\n⏳ 等待2秒...")
            time.sleep(2)
    
    # 汇总统计
    print(f"\n\n{'='*100}")
    print("📊 测试总结")
    print(f"{'='*100}")
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    print(f"总测试数: {len(results)}")
    print(f"成功: {len(successful)} ✅")
    print(f"失败: {len(failed)} ❌")
    print(f"成功率: {len(successful)/len(results)*100:.1f}%")
    
    if successful:
        avg_time = sum(r["elapsed"] for r in successful) / len(successful)
        print(f"平均响应时间: {avg_time:.2f}秒")
        
        # 统计LLM使用
        llm_stats = {}
        for r in successful:
            provider = r.get("llm_provider", "unknown")
            llm_stats[provider] = llm_stats.get(provider, 0) + 1
        
        print(f"\nLLM使用统计:")
        for provider, count in llm_stats.items():
            print(f"  - {provider}: {count}次")
        
        # 统计工具使用
        tool_stats = {}
        for r in successful:
            for tool in r.get("tools_used", []):
                tool_stats[tool] = tool_stats.get(tool, 0) + 1
        
        if tool_stats:
            print(f"\n工具使用统计:")
            for tool, count in sorted(tool_stats.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {tool}: {count}次")
    
    if failed:
        print(f"\n❌ 失败的测试:")
        for r in failed:
            print(f"  - {r['id']}: {r.get('error', 'Unknown error')}")
    
    print(f"\n{'='*100}")


if __name__ == "__main__":
    main()

