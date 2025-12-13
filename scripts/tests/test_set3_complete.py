#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Set 3 完整测试 - 复杂场景（18个文本问题，跳过6个图片问题）
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import requests
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict

# Test Set 3 - 完整文本问题列表（跳过图片问题）
TEST_SET_3_COMPLETE = [
    # English Questions (不含图片，9个)
    {"id": "EN-4", "question": "Compare the stock performance of NVIDIA (NVDA) and AMD over the last 5 days and summarize the top 3 reasons that might have influenced these movements.", "language": "English", "category": "Finance-Analysis"},
    {"id": "EN-5", "question": "I want to go hiking this Sunday in Sai Kung. Check the weather forecast for Sunday and suggest a trail that is safe for those conditions (avoid slippery routes if raining).", "language": "English", "category": "Weather-Recommendation"},
    {"id": "EN-6", "question": "Find a restaurant in Causeway Bay that serves Japanese Ramen and is currently open.", "language": "English", "category": "Search"},
    {"id": "EN-7", "question": "Who won the Best Actor award at the most recent Hong Kong Film Awards, and what is the Douban score of the movie they won for?", "language": "English", "category": "Entertainment"},
    {"id": "EN-8", "question": "Identify the winner of the most recent UEFA Champions League final, and list the goal scorers for that match along with the minute they scored.", "language": "English", "category": "Sports"},
    {"id": "EN-9", "question": "What are the departure times for the Bus 91M from Diamond Hill station?", "language": "English", "category": "Transport"},
    {"id": "EN-10", "question": "What is the current exchange rate between HKD and JPY, and how much is 50,000 Yen in HKD right now?", "language": "English", "category": "Finance"},
    {"id": "EN-11", "question": "What is the current Air Quality Health Index (AQHI) at the Central/Western monitoring station, and is the health risk considered 'High'?", "language": "English", "category": "Environment"},
    {"id": "EN-12", "question": "Find the next scheduled concert or public event at the Hong Kong Coliseum", "language": "English", "category": "Event"},
    
    # Chinese Questions (不含图片，9个)
    {"id": "CN-4", "question": "比較 NVIDIA (NVDA) 和 AMD 過去 5 天的股價表現，並總結可能影響這些波動的前 3 條原因。", "language": "Chinese", "category": "Finance-Analysis"},
    {"id": "CN-5", "question": "我這週日想去西貢遠足。請查詢週日的天氣預報，並根據天氣狀況推薦一條安全的路線（如果下雨，請避免濕滑路段）。", "language": "Chinese", "category": "Weather-Recommendation"},
    {"id": "CN-6", "question": "在銅鑼灣找一家目前正在營業的日式拉麵餐廳。", "language": "Chinese", "category": "Search"},
    {"id": "CN-7", "question": "誰在最近一屆香港電影金像獎中獲得了最佳男主角？他獲獎電影的豆瓣評分是多少？", "language": "Chinese", "category": "Entertainment"},
    {"id": "CN-8", "question": "找出最近一屆歐洲冠軍聯賽 (UEFA Champions League) 決賽的獲勝隊伍，並列出該場比賽的進球球員及其進球時間（分鐘）。", "language": "Chinese", "category": "Sports"},
    {"id": "CN-9", "question": "從鑽石山站開出的91M巴士的發車時間是什麼時候？", "language": "Chinese", "category": "Transport"},
    {"id": "CN-10", "question": "目前港幣 (HKD) 與日元 (JPY) 的匯率是多少？50,000 日元現在等於多少港幣？", "language": "Chinese", "category": "Finance"},
    {"id": "CN-11", "question": "查詢中西區監測站目前的空氣質素健康指數 (AQHI)，並判斷該健康風險級別是否屬於'高'？", "language": "Chinese", "category": "Environment"},
    {"id": "CN-12", "question": "找出香港體育館 (紅館) 下一個預定舉行的演唱會或公開活動", "language": "Chinese", "category": "Event"},
]


def query_agent(question: str) -> Dict:
    """调用Agent处理问题"""
    url = "http://localhost:5555/api/agent_query"
    
    payload = {
        "query": question,
        "provider": "hkgai",
        "model": "HKGAI-V1"
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=120)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "answer": data.get("answer", ""),
                "response_time": response_time,
                "tools_used": data.get("tools_used", []),
                "workflow_steps": len(data.get("workflow_steps", []))
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "response_time": response_time
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response_time": 0
        }


def test_question(test_case: dict, index: int, total: int) -> dict:
    """测试单个问题"""
    print(f"\n{'#'*100}")
    print(f"进度: {index}/{total}", flush=True)
    print(f"{'#'*100}", flush=True)
    print(f"❓ [{test_case['id']}] {test_case['question']}", flush=True)
    print(f"   语言: {test_case['language']} | 类别: {test_case['category']}", flush=True)
    print(f"{'─'*100}")
    
    result = query_agent(test_case['question'])
    
    if not result["success"]:
        print(f"❌ 失败: {result.get('error', 'Unknown error')}")
    else:
        print(f"✅ 成功")
        print(f"⏱️  响应时间: {result['response_time']:.2f}秒")
        print(f"🔧 使用工具: {', '.join(result['tools_used']) if result['tools_used'] else '无'}")
        print(f"📝 回答: {result['answer'][:200]}{'...' if len(result['answer']) > 200 else ''}")
    
    return {
        **test_case,
        "result": result
    }


def main():
    print("="*100)
    print("🧪 Test Set 3 完整测试 - 复杂场景（文本问题）")
    print("="*100)
    print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 总问题数: {len(TEST_SET_3_COMPLETE)} (不含6个图片问题)")
    print("⚠️  图片问题已跳过（需要multimodal接口）")
    print("="*100)
    
    results = []
    start_time = time.time()
    
    for i, test_case in enumerate(TEST_SET_3_COMPLETE, 1):
        try:
            result = test_question(test_case, i, len(TEST_SET_3_COMPLETE))
            results.append(result)
            
            # 每5个问题等待3秒
            if i < len(TEST_SET_3_COMPLETE) and i % 5 == 0:
                print(f"\n⏳ 已完成{i}个问题，等待3秒...")
                time.sleep(3)
        except KeyboardInterrupt:
            print("\n\n⚠️  测试被用户中断")
            break
        except Exception as e:
            print(f"\n❌ 测试异常: {e}")
            continue
    
    total_time = time.time() - start_time
    
    # 统计
    successful = [r for r in results if r['result']['success']]
    failed = [r for r in results if not r['result']['success']]
    avg_time = sum(r['result']['response_time'] for r in successful) / len(successful) if successful else 0
    
    # 按类别统计
    categories = {}
    for r in successful:
        cat = r['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r['result']['response_time'])
    
    print(f"\n\n{'='*100}")
    print("📊 Test Set 3 测试总结")
    print(f"{'='*100}")
    print(f"✅ 成功: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"❌ 失败: {len(failed)}/{len(results)}")
    print(f"⏱️  平均响应时间: {avg_time:.2f}秒")
    print(f"⏱️  总耗时: {total_time/60:.1f}分钟")
    
    print(f"\n按类别统计:")
    for cat, times in sorted(categories.items()):
        avg = sum(times) / len(times)
        print(f"  {cat}: {len(times)}个, 平均 {avg:.2f}秒")
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_results/test_set3_complete_{timestamp}.json"
    
    os.makedirs("test_results", exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "total_questions": len(TEST_SET_3_COMPLETE),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful)/len(results)*100 if results else 0,
            "avg_response_time": avg_time,
            "total_time_minutes": total_time/60,
            "note": "图片问题已跳过（EN-1,2,3和CN-1,2,3）",
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 详细结果已保存到: {output_file}")
    print("\n✅ Test Set 3 测试完成！")


if __name__ == "__main__":
    main()

