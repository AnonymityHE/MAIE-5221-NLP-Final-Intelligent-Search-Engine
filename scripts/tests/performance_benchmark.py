#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
性能基准测试 - 验证优化效果
选择之前最慢的查询进行对比测试
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import requests
import time
from datetime import datetime
from typing import List, Dict

# 选择之前测试中最慢的查询进行性能验证
BENCHMARK_QUERIES = [
    {
        "id": "WEB-1",
        "query": "Will it rain in Shenzhen tomorrow?",
        "expected_tool": "web_search",
        "baseline_time": 52.0,  # 之前的平均web_search时间
        "category": "web_search优化验证"
    },
    {
        "id": "WEB-2",
        "query": "香港天文臺現在懸掛的是什麼熱帶氣旋警告信號？",
        "expected_tool": "web_search",
        "baseline_time": 52.0,
        "category": "web_search优化验证"
    },
    {
        "id": "WEB-3",
        "query": "What is the latest news about APEC?",
        "expected_tool": "web_search",
        "baseline_time": 52.0,
        "category": "web_search优化验证"
    },
    {
        "id": "LLM-1",
        "query": "What are some common symptoms of hay fever?",
        "expected_tool": "direct_llm",
        "baseline_time": 37.0,  # 之前的平均direct_llm时间
        "category": "LLM基准测试"
    },
    {
        "id": "LLM-2",
        "query": "What is the capital of Japan?",
        "expected_tool": "direct_llm",
        "baseline_time": 37.0,
        "category": "LLM基准测试"
    },
    {
        "id": "RAG-1",
        "query": "Where is HKUST located?",
        "expected_tool": "local_rag",
        "baseline_time": 43.0,  # 之前的平均local_rag时间
        "category": "RAG性能测试"
    },
    {
        "id": "WEATHER-1",
        "query": "What is the temperature in Hong Kong right now?",
        "expected_tool": "weather",
        "baseline_time": 46.0,  # 之前的平均weather时间
        "category": "Weather API测试"
    },
    {
        "id": "FINANCE-1",
        "query": "What is Apple's stock price?",
        "expected_tool": "finance",
        "baseline_time": 60.0,  # 之前的平均finance时间
        "category": "Finance API测试"
    }
]


def test_query(query: str, query_id: str) -> Dict:
    """测试单个查询"""
    url = "http://localhost:5555/api/agent_query"
    
    try:
        start_time = time.time()
        response = requests.post(
            url,
            json={"query": query},
            timeout=120
        )
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "response_time": response_time,
                "tools_used": data.get("tools_used", []),
                "answer": data.get("answer", "")[:100]
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


def run_benchmark():
    """运行性能基准测试"""
    print("="*100)
    print("⚡ 性能基准测试 - 验证优化效果")
    print("="*100)
    print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 测试查询数: {len(BENCHMARK_QUERIES)}")
    print("="*100)
    
    results = []
    total_baseline = 0
    total_actual = 0
    
    for i, test_case in enumerate(BENCHMARK_QUERIES, 1):
        print(f"\n[{i}/{len(BENCHMARK_QUERIES)}] {test_case['id']}: {test_case['category']}")
        print(f"   问题: {test_case['query']}")
        print(f"   基准时间: {test_case['baseline_time']:.1f}秒")
        print(f"   {'─'*90}")
        
        result = test_query(test_case['query'], test_case['id'])
        
        if result['success']:
            improvement = test_case['baseline_time'] - result['response_time']
            improvement_pct = (improvement / test_case['baseline_time']) * 100
            
            # 判断工具是否正确
            tool_correct = test_case['expected_tool'] in result['tools_used'] if test_case['expected_tool'] != 'direct_llm' else 'direct_llm' in result['tools_used'] or len(result['tools_used']) == 0
            
            if improvement > 0:
                status = f"✅ 提升 {improvement:.1f}秒 ({improvement_pct:.1f}%)"
            elif improvement > -5:
                status = f"🟡 持平 ({improvement:.1f}秒)"
            else:
                status = f"🔴 变慢 {abs(improvement):.1f}秒"
            
            print(f"   {status}")
            print(f"   实际时间: {result['response_time']:.2f}秒")
            print(f"   工具: {result['tools_used']} {'✅' if tool_correct else '⚠️'}")
            
            total_baseline += test_case['baseline_time']
            total_actual += result['response_time']
            
            results.append({
                **test_case,
                "actual_time": result['response_time'],
                "improvement": improvement,
                "improvement_pct": improvement_pct,
                "tools_used": result['tools_used'],
                "tool_correct": tool_correct
            })
        else:
            print(f"   ❌ 失败: {result.get('error', 'Unknown')}")
            results.append({
                **test_case,
                "actual_time": 0,
                "improvement": 0,
                "improvement_pct": 0,
                "error": result.get('error')
            })
        
        # 等待2秒
        if i < len(BENCHMARK_QUERIES):
            time.sleep(2)
    
    # 汇总统计
    print("\n" + "="*100)
    print("📊 性能对比总结")
    print("="*100)
    
    successful = [r for r in results if 'error' not in r]
    
    if successful:
        avg_baseline = total_baseline / len(successful)
        avg_actual = total_actual / len(successful)
        total_improvement = total_baseline - total_actual
        total_improvement_pct = (total_improvement / total_baseline) * 100
        
        print(f"\n整体性能:")
        print(f"  基准平均时间: {avg_baseline:.2f}秒")
        print(f"  实际平均时间: {avg_actual:.2f}秒")
        print(f"  总体提升: {total_improvement:.2f}秒 ({total_improvement_pct:.1f}%)")
        
        # 按类别统计
        print(f"\n按类别统计:")
        categories = {}
        for r in successful:
            cat = r['category']
            if cat not in categories:
                categories[cat] = {"baseline": [], "actual": []}
            categories[cat]["baseline"].append(r['baseline_time'])
            categories[cat]["actual"].append(r['actual_time'])
        
        for cat, times in categories.items():
            avg_base = sum(times['baseline']) / len(times['baseline'])
            avg_act = sum(times['actual']) / len(times['actual'])
            impr = avg_base - avg_act
            impr_pct = (impr / avg_base) * 100
            
            if impr > 0:
                status = f"✅ 提升{impr:.1f}秒 ({impr_pct:.1f}%)"
            else:
                status = f"🔴 变慢{abs(impr):.1f}秒"
            
            print(f"  {cat}: {avg_base:.1f}s → {avg_act:.1f}s {status}")
        
        # 工具路由准确性
        tool_correct_count = sum(1 for r in successful if r.get('tool_correct', False))
        tool_accuracy = (tool_correct_count / len(successful)) * 100
        print(f"\n工具路由准确性: {tool_correct_count}/{len(successful)} ({tool_accuracy:.1f}%)")
        
        # 评级
        print(f"\n{'='*100}")
        print("🎯 优化效果评级:")
        
        if total_improvement_pct >= 30:
            print("  🌟🌟🌟 优秀 - 性能提升超过30%")
        elif total_improvement_pct >= 15:
            print("  🌟🌟 良好 - 性能提升15-30%")
        elif total_improvement_pct >= 5:
            print("  🌟 一般 - 性能提升5-15%")
        else:
            print("  ⚠️  待改进 - 性能提升不明显")
    
    print("="*100)
    print("✅ 性能基准测试完成！")


if __name__ == "__main__":
    run_benchmark()

