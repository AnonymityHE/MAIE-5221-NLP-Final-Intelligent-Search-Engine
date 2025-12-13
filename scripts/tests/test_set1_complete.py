#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Set 1 完整测试 - 基础问题（48个）
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import requests
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Test Set 1 - 完整问题列表（从docs/Test Questions Set 1.docx提取）
TEST_SET_1_COMPLETE = [
    # English Questions (30个)
    {"id": "EN-1", "question": "What are some common symptoms of hay fever?", "language": "English", "category": "Knowledge"},
    {"id": "EN-2", "question": "What's the weather forecast for this afternoon in Hong Kong?", "language": "English", "category": "Real-time"},
    {"id": "EN-3", "question": "What is the standard voltage for household electronics in Hong Kong?", "language": "English", "category": "Knowledge"},
    {"id": "EN-4", "question": "What is 15 multiplied by 24?", "language": "English", "category": "Math"},
    {"id": "EN-5", "question": "What are the five official colors of the Olympic rings?", "language": "English", "category": "Knowledge"},
    {"id": "EN-6", "question": "How do you say 'thank you' in Cantonese?", "language": "English", "category": "Language"},
    {"id": "EN-7", "question": "What are the upcoming public holidays in Hong Kong this year?", "language": "English", "category": "Real-time"},
    {"id": "EN-8", "question": "How can I report a lost Octopus card?", "language": "English", "category": "Procedure"},
    {"id": "EN-9", "question": "Will it rain in Shenzhen tomorrow?", "language": "English", "category": "Weather"},
    {"id": "EN-10", "question": "What year was the Hong Kong-Zhuhai-Macau Bridge opened?", "language": "English", "category": "Knowledge"},
    {"id": "EN-11", "question": "Who wrote 'Romeo and Juliet'?", "language": "English", "category": "Knowledge"},
    {"id": "EN-12", "question": "How do I apply for a Hong Kong public library card?", "language": "English", "category": "Procedure"},
    {"id": "EN-13", "question": "What is the tallest building in Hong Kong?", "language": "English", "category": "Knowledge"},
    {"id": "EN-14", "question": "Give me a simple recipe for fried rice.", "language": "English", "category": "Recipe"},
    {"id": "EN-15", "question": "What is the temperature in Beijing right now?", "language": "English", "category": "Weather"},
    {"id": "EN-16", "question": "What are the operating hours for the Star Ferry between Central and Tsim Sha Tsui?", "language": "English", "category": "Schedule"},
    {"id": "EN-17", "question": "What time is sunset in Hong Kong today?", "language": "English", "category": "Real-time"},
    {"id": "EN-18", "question": "What are the general visiting hours for public hospitals in Hong Kong?", "language": "English", "category": "Information"},
    {"id": "EN-19", "question": "What is the chemical formula for water?", "language": "English", "category": "Knowledge"},
    {"id": "EN-20", "question": "What is the emergency phone number for the police in Hong Kong?", "language": "English", "category": "Emergency"},
    {"id": "EN-21", "question": "In Hong Kong, what is the Voluntary Health Insurance Scheme (VHIS)?", "language": "English", "category": "Policy"},
    {"id": "EN-22", "question": "What is the main food eaten during the Dragon Boat Festival in Hong Kong?", "language": "English", "category": "Culture"},
    {"id": "EN-23", "question": "What is the wind speed in Shanghai?", "language": "English", "category": "Weather"},
    {"id": "EN-24", "question": "What is the difference between a typhoon warning signal No. 8 and No. 10?", "language": "English", "category": "Knowledge"},
    {"id": "EN-25", "question": "What planet is known as the Red Planet?", "language": "English", "category": "Knowledge"},
    {"id": "EN-26", "question": "How many days are in a leap year?", "language": "English", "category": "Knowledge"},
    {"id": "EN-27", "question": "How many SARs (Special Administrative Regions) are in China?", "language": "English", "category": "Knowledge"},
    {"id": "EN-28", "question": "What does the 'MPF' abbreviation stand for in Hong Kong?", "language": "English", "category": "Knowledge"},
    {"id": "EN-29", "question": "What is the capital of Japan?", "language": "English", "category": "Knowledge"},
    {"id": "EN-30", "question": "What is the maximum claim amount for the Small Claims Tribunal in Hong Kong?", "language": "English", "category": "Legal"},
    
    # Chinese Questions (18个)
    {"id": "CN-1", "question": "如果我發燒和喉嚨痛，應該去看普通科還是專科醫生？", "language": "Chinese", "category": "Medical"},
    {"id": "CN-2", "question": "香港天文臺現在懸掛的是什麼熱帶氣旋警告信號？", "language": "Chinese", "category": "Real-time"},
    {"id": "CN-3", "question": "香港的公共圖書館在哪個熱帶氣旋警告信號下會關閉？", "language": "Chinese", "category": "Policy"},
    {"id": "CN-4", "question": "1024減去768等於多少？", "language": "Chinese", "category": "Math"},
    {"id": "CN-5", "question": "構成漢字的'永字八法'指的是哪八個筆劃？", "language": "Chinese", "category": "Knowledge"},
    {"id": "CN-6", "question": "'早晨'在廣東話裡是什麼意思？", "language": "Chinese", "category": "Language"},
    {"id": "CN-7", "question": "香港法定最低時薪是多少？", "language": "Chinese", "category": "Policy"},
    {"id": "CN-8", "question": "在香港如何申請一本特區護照？", "language": "Chinese", "category": "Procedure"},
    {"id": "CN-9", "question": "明天廣州的空氣質量指數是多少？", "language": "Chinese", "category": "Real-time"},
    {"id": "CN-10", "question": "香港會議展覽中心是什麼時候建成的？", "language": "Chinese", "category": "Knowledge"},
    {"id": "CN-11", "question": "中國四大古典名著是哪幾部？", "language": "Chinese", "category": "Knowledge"},
    {"id": "CN-12", "question": "在香港續領駕駛執照需要什麼文件？", "language": "Chinese", "category": "Procedure"},
    {"id": "CN-13", "question": "香港最大的離島是哪個島？", "language": "Chinese", "category": "Knowledge"},
    {"id": "CN-14", "question": "如何製作一杯港式檸檬茶？", "language": "Chinese", "category": "Recipe"},
    {"id": "CN-15", "question": "澳門現在的濕度是多少？", "language": "Chinese", "category": "Weather"},
    {"id": "CN-16", "question": "香港電車的首班車和末班車是幾點？", "language": "Chinese", "category": "Schedule"},
    {"id": "CN-17", "question": "今天香港的日出時間是幾點？", "language": "Chinese", "category": "Real-time"},
    {"id": "CN-18", "question": "香港的公立醫院急症室收費是多少？", "language": "Chinese", "category": "Medical"},
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
        print(f"✅ 成功", flush=True)
        print(f"⏱️  响应时间: {result['response_time']:.2f}秒", flush=True)
        print(f"🔧 使用工具: {', '.join(result['tools_used']) if result['tools_used'] else '无'}", flush=True)
        print(f"📝 回答: {result['answer'][:200]}{'...' if len(result['answer']) > 200 else ''}", flush=True)
    
    return {
        **test_case,
        "result": result
    }


def main():
    print("="*100)
    print("🧪 Test Set 1 完整测试 - 基础问题")
    print("="*100)
    print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 总问题数: {len(TEST_SET_1_COMPLETE)}")
    print("="*100)
    
    results = []
    start_time = time.time()
    
    for i, test_case in enumerate(TEST_SET_1_COMPLETE, 1):
        try:
            result = test_question(test_case, i, len(TEST_SET_1_COMPLETE))
            results.append(result)
            
            # 每5个问题等待3秒
            if i < len(TEST_SET_1_COMPLETE) and i % 5 == 0:
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
    
    print(f"\n\n{'='*100}")
    print("📊 Test Set 1 测试总结")
    print(f"{'='*100}")
    print(f"✅ 成功: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"❌ 失败: {len(failed)}/{len(results)}")
    print(f"⏱️  平均响应时间: {avg_time:.2f}秒")
    print(f"⏱️  总耗时: {total_time/60:.1f}分钟")
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_results/test_set1_complete_{timestamp}.json"
    
    os.makedirs("test_results", exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "total_questions": len(TEST_SET_1_COMPLETE),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful)/len(results)*100 if results else 0,
            "avg_response_time": avg_time,
            "total_time_minutes": total_time/60,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 详细结果已保存到: {output_file}")
    print("\n✅ Test Set 1 测试完成！")


if __name__ == "__main__":
    main()

