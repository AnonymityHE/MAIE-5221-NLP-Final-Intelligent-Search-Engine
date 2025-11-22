#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Set 3 完整Agent测试（HKGAI + 工具调用）
测试混合策略：HKGAI作为规划器 + 工具提供实时数据
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import requests
import time
from typing import Dict, List
import json


# Test Set 3 - 文本问题（完整版，包括需要工具的问题）
TEST_QUESTIONS = [
    {
        "id": "CN-1",
        "question": "香港科技大学在哪里？",
        "language": "中文",
        "category": "基础知识",
        "expected_tools": ["local_rag"]
    },
    {
        "id": "CN-2",
        "question": "RAG系统的核心组件有哪些？",
        "language": "中文",
        "category": "技术知识",
        "expected_tools": ["local_rag"]
    },
    {
        "id": "CN-3",
        "question": "现在香港的天气怎么样？",
        "language": "中文",
        "category": "实时信息",
        "expected_tools": ["weather"]
    },
    {
        "id": "CN-4",
        "question": "苹果公司的股价是多少？",
        "language": "中文",
        "category": "实时信息",
        "expected_tools": ["finance"]
    },
    {
        "id": "CN-5",
        "question": "比亚迪和特斯拉哪个股价更高？",
        "language": "中文",
        "category": "对比分析",
        "expected_tools": ["finance"]
    },
    {
        "id": "CN-6",
        "question": "比较香港和北京今天的天气",
        "language": "中文",
        "category": "对比分析",
        "expected_tools": ["weather"]
    },
    {
        "id": "EN-1",
        "question": "Where is the Hong Kong University of Science and Technology located?",
        "language": "英文",
        "category": "基础知识",
        "expected_tools": ["local_rag"]
    },
    {
        "id": "EN-2",
        "question": "What are the core components of a RAG system?",
        "language": "英文",
        "category": "技术知识",
        "expected_tools": ["local_rag"]
    },
    {
        "id": "EN-3",
        "question": "What's the weather like in Hong Kong now?",
        "language": "英文",
        "category": "实时信息",
        "expected_tools": ["weather"]
    },
    {
        "id": "EN-4",
        "question": "What is Apple's stock price?",
        "language": "英文",
        "category": "实时信息",
        "expected_tools": ["finance"]
    },
]


def query_agent(question: str) -> Dict:
    """
    调用Agent API查询（带工具调用）
    
    Args:
        question: 问题
        
    Returns:
        结果字典
    """
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
                "workflow_steps": data.get("workflow_steps", []),
                "provider": data.get("provider", ""),
                "model": data.get("model", "")
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text[:200]}",
                "response_time": response_time
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"请求异常: {str(e)}",
            "response_time": 0
        }


def run_agent_test():
    """运行完整Agent测试"""
    print("=" * 100)
    print("🤖 Test Set 3 完整Agent测试（混合策略）")
    print("=" * 100)
    print("\n🎯 测试策略:")
    print("  - 规划器: HKGAI-V1 (快速、准确)")
    print("  - 工具链: local_rag, web_search, weather, finance, transport")
    print("  - 目标: 验证Agent能否正确调用工具获取实时/知识库数据")
    print(f"\n📋 测试问题数: {len(TEST_QUESTIONS)}")
    print("=" * 100)
    
    results = []
    
    for i, test_case in enumerate(TEST_QUESTIONS, 1):
        print(f"\n\n{'#'*100}")
        print(f"进度: {i}/{len(TEST_QUESTIONS)} | ID: {test_case['id']} | 类别: {test_case['category']}")
        print(f"{'#'*100}")
        print(f"\n❓ 问题: {test_case['question']}")
        print(f"🌐 语言: {test_case['language']}")
        print(f"🔧 预期工具: {', '.join(test_case['expected_tools'])}")
        
        # 调用Agent
        print(f"\n{'─'*80}")
        print("⏳ 正在通过Agent处理...")
        agent_result = query_agent(test_case["question"])
        
        result = {
            "id": test_case["id"],
            "question": test_case["question"],
            "language": test_case["language"],
            "category": test_case["category"],
            "expected_tools": test_case["expected_tools"],
            "result": agent_result
        }
        
        if agent_result["success"]:
            print(f"✅ 成功")
            print(f"⏱️  响应时间: {agent_result['response_time']:.2f}秒")
            print(f"🤖 使用模型: {agent_result.get('provider', '')} / {agent_result.get('model', '')}")
            print(f"🔧 调用工具: {', '.join(agent_result['tools_used']) if agent_result['tools_used'] else '无'}")
            print(f"📊 工作流步骤: {len(agent_result['workflow_steps'])}步")
            
            # 检查工具使用是否符合预期
            tools_used_set = set(agent_result['tools_used'])
            expected_tools_set = set(test_case['expected_tools'])
            
            if tools_used_set & expected_tools_set:
                print(f"✅ 工具使用正确（符合预期）")
            else:
                print(f"⚠️  工具使用异常：预期 {expected_tools_set}，实际 {tools_used_set}")
            
            print(f"\n📝 回答:")
            answer = agent_result['answer']
            if len(answer) > 500:
                print(answer[:500] + "...")
            else:
                print(answer)
        else:
            print(f"❌ 失败")
            print(f"错误: {agent_result['error']}")
        
        results.append(result)
        
        # 等待避免频率限制
        if i < len(TEST_QUESTIONS):
            print(f"\n⏳ 等待3秒...")
            time.sleep(3)
    
    # 汇总统计
    print(f"\n\n{'='*100}")
    print("📊 测试总结")
    print(f"{'='*100}")
    
    success_count = sum(1 for r in results if r["result"].get("success", False))
    total_count = len(results)
    
    avg_time = sum(r["result"].get("response_time", 0) for r in results if r["result"].get("success", False)) / max(success_count, 1)
    
    print(f"\n✅ 成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    print(f"⏱️  平均响应时间: {avg_time:.2f}秒")
    
    # 工具使用统计
    print(f"\n🔧 工具使用统计:")
    all_tools_used = []
    for r in results:
        if r["result"].get("success", False):
            all_tools_used.extend(r["result"].get("tools_used", []))
    
    if all_tools_used:
        from collections import Counter
        tool_counts = Counter(all_tools_used)
        for tool, count in tool_counts.most_common():
            print(f"  - {tool}: {count}次")
    else:
        print("  无工具被调用")
    
    # 按类别统计
    print(f"\n📊 按类别统计:")
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "success": 0}
        categories[cat]["total"] += 1
        if r["result"].get("success", False):
            categories[cat]["success"] += 1
    
    for cat, stats in categories.items():
        success_rate = stats["success"] / stats["total"] * 100
        print(f"  {cat}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
    
    # 工具使用准确性
    print(f"\n🎯 工具使用准确性:")
    tool_match_count = 0
    tool_total_count = 0
    
    for r in results:
        if r["result"].get("success", False):
            tool_total_count += 1
            tools_used_set = set(r["result"].get("tools_used", []))
            expected_tools_set = set(r["expected_tools"])
            
            if tools_used_set & expected_tools_set:
                tool_match_count += 1
    
    if tool_total_count > 0:
        print(f"  准确率: {tool_match_count}/{tool_total_count} ({tool_match_count/tool_total_count*100:.1f}%)")
    else:
        print("  无数据")
    
    # 失败案例
    failures = [r for r in results if not r["result"].get("success", False)]
    if failures:
        print(f"\n❌ 失败案例:")
        for r in failures:
            print(f"  - {r['id']}: {r['question'][:50]}...")
            print(f"    错误: {r['result'].get('error', '')[:100]}")
    
    # 工具使用异常案例
    print(f"\n⚠️  工具使用异常案例:")
    tool_mismatches = []
    for r in results:
        if r["result"].get("success", False):
            tools_used_set = set(r["result"].get("tools_used", []))
            expected_tools_set = set(r["expected_tools"])
            
            if not (tools_used_set & expected_tools_set):
                tool_mismatches.append(r)
    
    if tool_mismatches:
        for r in tool_mismatches:
            print(f"  - {r['id']}: {r['question'][:50]}...")
            print(f"    预期: {r['expected_tools']}")
            print(f"    实际: {r['result'].get('tools_used', [])}")
    else:
        print("  无异常")
    
    # 保存详细结果
    output_file = "test_agent_with_tools_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 详细结果已保存到: {output_file}")
    
    print(f"\n{'='*100}")
    print("✅ Agent测试完成！")
    print(f"{'='*100}")


if __name__ == "__main__":
    run_agent_test()

