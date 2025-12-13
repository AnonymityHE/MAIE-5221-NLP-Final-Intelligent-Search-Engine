#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Set 2 完整测试 - 进阶问题（45个）
包含虚构知识库测试
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

# Test Set 2 - 完整问题列表
TEST_SET_2_COMPLETE = [
    # English Questions (30个)
    {"id": "EN-1", "question": "Provide the route from Kennedy Town to Hong Kong International Airport.", "language": "English", "category": "Transport"},
    {"id": "EN-2", "question": "Assess the chance of Typhoon Signal No. 8 being issued tonight.", "language": "English", "category": "Weather"},
    {"id": "EN-3", "question": "State whether heavy rain would affect Shenzhen Bay Port opening hours.", "language": "English", "category": "Policy"},
    {"id": "EN-4", "question": "Provide today's Hang Seng Index percentage change at close.", "language": "English", "category": "Finance"},
    {"id": "EN-5", "question": "State whether an evening run in Mong Kok today is advisable.", "language": "English", "category": "Advice"},
    {"id": "EN-6", "question": "State whether the Star Ferry Central–Tsim Sha Tsui service operates after 23:00.", "language": "English", "category": "Schedule"},
    {"id": "EN-7", "question": "State whether schools are currently suspended in Hong Kong.", "language": "English", "category": "Real-time"},
    {"id": "EN-8", "question": "Provide tomorrow's opening time for Lo Wu Control Point.", "language": "English", "category": "Schedule"},
    {"id": "EN-9", "question": "List recommended restaurants in Kowloon City.", "language": "English", "category": "Recommendation"},
    {"id": "EN-10", "question": "State whether road closures will occur at Kai Tak Cruise Terminal during the National Games period.", "language": "English", "category": "Event"},
    {"id": "EN-11", "question": "Provide the current CLP residential basic tariff per kWh.", "language": "English", "category": "Utility"},
    {"id": "EN-12", "question": "Provide the nearest 24/7 pharmacy in Sha Tin.", "language": "English", "category": "Location"},
    {"id": "EN-13", "question": "State the date of the Hong Kong Marathon.", "language": "English", "category": "Event"},
    {"id": "EN-14", "question": "Provide the current gold price in HKD.", "language": "English", "category": "Finance"},
    {"id": "EN-15", "question": "State whether Ocean Park tickets can be extended on a typhoon day.", "language": "English", "category": "Policy"},
    {"id": "EN-16", "question": "Provide the latest HKO forecast track for the nearest tropical cyclone.", "language": "English", "category": "Weather"},
    {"id": "EN-17", "question": "List currently popular TV series in Hong Kong.", "language": "English", "category": "Entertainment"},
    {"id": "EN-18", "question": "Provide a brief evaluation of former Taiwan President Tsai Ingwen.", "language": "English", "category": "Politics"},
    {"id": "EN-19", "question": "Compare the QS rankings of CUHK and HKUST over the past ten years.", "language": "English", "category": "Education"},
    {"id": "EN-20", "question": "Provide the current top five teams in the English Premier League table.", "language": "English", "category": "Sports"},
    {"id": "EN-21", "question": "List the leaders the Japanese Prime Minister met at this year's APEC.", "language": "English", "category": "Politics"},
    {"id": "EN-22", "question": "What is the country closest to Fujian.", "language": "English", "category": "Geography"},
    # Fictional Knowledge Base Questions (虚构知识库)
    {"id": "EN-23", "question": "Describe the key principles of the 'Sereleian Model' of economics and the nation's primary industries.", "language": "English", "category": "Fictional-KB"},
    {"id": "EN-24", "question": "Detail the three core technologies of Aetherian Dynamics and the ethical considerations for the Synapse Neural Interface.", "language": "English", "category": "Fictional-KB"},
    {"id": "EN-25", "question": "Explain the 'Dynamic Covenant' that guides Aetherian Dynamics' corporate philosophy.", "language": "English", "category": "Fictional-KB"},
    {"id": "EN-26", "question": "Describe the unique atmospheric and geological features of Planet Xylos.", "language": "English", "category": "Fictional-KB"},
    {"id": "EN-27", "question": "Describe the biological nature and communication method of the silicon-based 'Luminoids' on Planet Xylos.", "language": "English", "category": "Fictional-KB"},
    {"id": "EN-28", "question": "Explain Dr. Elara Vance's novel scientific approach that led to the discovery of Xylos.", "language": "English", "category": "Fictional-KB"},
    {"id": "EN-29", "question": "Detail the 'Vance Protocol' and its four key principles for ethical space exploration.", "language": "English", "category": "Fictional-KB"},
    {"id": "EN-30", "question": "Explain how 'The Great Digital Awakening' led to a decentralized internet.", "language": "English", "category": "Fictional-KB"},
    
    # Chinese Questions (15个)
    {"id": "CN-1", "question": "由堅尼地城前往香港國際機場的路線是什麼？", "language": "Chinese", "category": "Transport"},
    {"id": "CN-2", "question": "今晚是否有機會發出八號風球？", "language": "Chinese", "category": "Weather"},
    {"id": "CN-3", "question": "如果有大雨是否會影響深圳灣口岸開放時間？", "language": "Chinese", "category": "Policy"},
    {"id": "CN-4", "question": "今日恆生指數收市升跌百分比是多少？", "language": "Chinese", "category": "Finance"},
    {"id": "CN-5", "question": "今日傍晚在旺角跑步是否建議進行？", "language": "Chinese", "category": "Advice"},
    {"id": "CN-6", "question": "天星小輪中環—尖沙咀航線23:00後是否營運？", "language": "Chinese", "category": "Schedule"},
    {"id": "CN-7", "question": "現時學校是否停課？", "language": "Chinese", "category": "Real-time"},
    {"id": "CN-8", "question": "羅湖管制站明天幾點開門？", "language": "Chinese", "category": "Schedule"},
    {"id": "CN-9", "question": "九龍城有什麼好吃的餐廳？", "language": "Chinese", "category": "Recommendation"},
    {"id": "CN-10", "question": "啟德郵輪碼頭全運會期間是否有道路封閉？", "language": "Chinese", "category": "Event"},
    {"id": "CN-11", "question": "中電住宅每度電基本電價是多少？", "language": "Chinese", "category": "Utility"},
    {"id": "CN-12", "question": "沙田最近的24小時藥房在哪裡？", "language": "Chinese", "category": "Location"},
    {"id": "CN-13", "question": "香港馬拉松是在哪一天？", "language": "Chinese", "category": "Event"},
    {"id": "CN-14", "question": "現時金價是多少？", "language": "Chinese", "category": "Finance"},
    {"id": "CN-15", "question": "颱風日海洋公園門票是否可延長有效期？", "language": "Chinese", "category": "Policy"},
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
    print("🧪 Test Set 2 完整测试 - 进阶问题（含虚构知识库）")
    print("="*100)
    print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 总问题数: {len(TEST_SET_2_COMPLETE)}")
    print("="*100)
    
    results = []
    start_time = time.time()
    
    for i, test_case in enumerate(TEST_SET_2_COMPLETE, 1):
        try:
            result = test_question(test_case, i, len(TEST_SET_2_COMPLETE))
            results.append(result)
            
            # 每5个问题等待3秒
            if i < len(TEST_SET_2_COMPLETE) and i % 5 == 0:
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
    fictional_kb = [r for r in successful if r['category'] == 'Fictional-KB']
    
    print(f"\n\n{'='*100}")
    print("📊 Test Set 2 测试总结")
    print(f"{'='*100}")
    print(f"✅ 成功: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"❌ 失败: {len(failed)}/{len(results)}")
    print(f"⏱️  平均响应时间: {avg_time:.2f}秒")
    print(f"⏱️  总耗时: {total_time/60:.1f}分钟")
    print(f"📚 虚构知识库问题: {len(fictional_kb)}/8 成功")
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_results/test_set2_complete_{timestamp}.json"
    
    os.makedirs("test_results", exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "total_questions": len(TEST_SET_2_COMPLETE),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful)/len(results)*100 if results else 0,
            "avg_response_time": avg_time,
            "total_time_minutes": total_time/60,
            "fictional_kb_success": len(fictional_kb),
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 详细结果已保存到: {output_file}")
    print("\n✅ Test Set 2 测试完成！")


if __name__ == "__main__":
    main()

