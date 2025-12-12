#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整测试Test Set 1, 2, 3 - 收集详细性能数据
不生成TTS音频，专注于Agent性能测试
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


# Test Set 1 - 基础问题（4个）
TEST_SET_1 = [
    {
        "id": "SET1-1",
        "question": "香港科技大学在哪里？",
        "language": "中文",
        "category": "基础知识",
        "expected_tools": ["local_rag"]
    },
    {
        "id": "SET1-2",
        "question": "现在香港的天气怎么样？",
        "language": "中文",
        "category": "实时信息",
        "expected_tools": ["weather"]
    },
    {
        "id": "SET1-3",
        "question": "苹果公司的股价是多少？",
        "language": "中文",
        "category": "实时信息",
        "expected_tools": ["finance"]
    },
    {
        "id": "SET1-4",
        "question": "RAG系统是什么？",
        "language": "中文",
        "category": "技术知识",
        "expected_tools": ["local_rag"]
    }
]

# Test Set 2 - 进阶问题（4个）
TEST_SET_2 = [
    {
        "id": "SET2-1",
        "question": "比亚迪和特斯拉哪个股价更高？",
        "language": "中文",
        "category": "对比分析",
        "expected_tools": ["finance"]
    },
    {
        "id": "SET2-2",
        "question": "比较香港和北京的天气",
        "language": "中文",
        "category": "对比分析",
        "expected_tools": ["weather"]
    },
    {
        "id": "SET2-3",
        "question": "RAG系统的核心组件有哪些？",
        "language": "中文",
        "category": "技术知识",
        "expected_tools": ["local_rag"]
    },
    {
        "id": "SET2-4",
        "question": "如何优化RAG系统的检索质量？",
        "language": "中文",
        "category": "技术知识",
        "expected_tools": ["local_rag"]
    }
]

# Test Set 3 - 混合场景（10个，来自test_agent_with_tools.log）
TEST_SET_3 = [
    {
        "id": "SET3-1",
        "question": "香港科技大学在哪里？",
        "language": "中文",
        "category": "基础知识",
        "expected_tools": ["local_rag"]
    },
    {
        "id": "SET3-2",
        "question": "RAG系统的核心组件有哪些？",
        "language": "中文",
        "category": "技术知识",
        "expected_tools": ["local_rag"]
    },
    {
        "id": "SET3-3",
        "question": "现在香港的天气怎么样？",
        "language": "中文",
        "category": "实时信息",
        "expected_tools": ["weather"]
    },
    {
        "id": "SET3-4",
        "question": "苹果公司的股价是多少？",
        "language": "中文",
        "category": "实时信息",
        "expected_tools": ["finance"]
    },
    {
        "id": "SET3-5",
        "question": "比亚迪和特斯拉哪个股价更高？",
        "language": "中文",
        "category": "对比分析",
        "expected_tools": ["finance"]
    },
    {
        "id": "SET3-6",
        "question": "比较香港和北京今天的天气",
        "language": "中文",
        "category": "对比分析",
        "expected_tools": ["weather"]
    },
    {
        "id": "SET3-7",
        "question": "Where is the Hong Kong University of Science and Technology located?",
        "language": "英文",
        "category": "基础知识",
        "expected_tools": ["local_rag"]
    },
    {
        "id": "SET3-8",
        "question": "What are the core components of a RAG system?",
        "language": "英文",
        "category": "技术知识",
        "expected_tools": ["local_rag"]
    },
    {
        "id": "SET3-9",
        "question": "What's the weather like in Hong Kong now?",
        "language": "英文",
        "category": "实时信息",
        "expected_tools": ["weather"]
    },
    {
        "id": "SET3-10",
        "question": "What is Apple's stock price?",
        "language": "英文",
        "category": "实时信息",
        "expected_tools": ["finance"]
    }
]


def query_agent(question: str) -> Dict:
    """
    调用Agent处理问题
    
    Args:
        question: 用户问题
        
    Returns:
        {
            "success": bool,
            "answer": str,
            "response_time": float,
            "tools_used": list,
            "workflow_steps": int,
            "error": str (if failed)
        }
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
                "workflow_steps": len(data.get("workflow_steps", []))
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
            "error": str(e),
            "response_time": 0
        }


def test_question(test_case: dict) -> dict:
    """测试单个问题"""
    print(f"\n{'─'*80}")
    print(f"❓ [{test_case['id']}] {test_case['question']}")
    print(f"   语言: {test_case['language']} | 类别: {test_case['category']}")
    print(f"   预期工具: {', '.join(test_case['expected_tools'])}")
    print(f"{'─'*80}")
    
    # 调用Agent
    result = query_agent(test_case['question'])
    
    if not result["success"]:
        print(f"❌ 失败: {result.get('error', 'Unknown error')}")
        return {
            **test_case,
            "result": result
        }
    
    # 检查工具使用正确性
    expected_tools = set(test_case['expected_tools'])
    actual_tools = set(result['tools_used'])
    tool_correct = bool(expected_tools & actual_tools)
    
    print(f"✅ 成功")
    print(f"⏱️  响应时间: {result['response_time']:.2f}秒")
    print(f"🔧 使用工具: {', '.join(result['tools_used']) if result['tools_used'] else '无'}")
    print(f"📊 工作流步骤: {result['workflow_steps']}步")
    print(f"{'✅' if tool_correct else '⚠️ '} 工具使用{'正确' if tool_correct else '异常'}")
    print(f"📝 回答: {result['answer'][:150]}{'...' if len(result['answer']) > 150 else ''}")
    
    return {
        **test_case,
        "result": {
            **result,
            "tool_correct": tool_correct
        }
    }


def run_test_set(test_set: List[dict], set_name: str) -> List[dict]:
    """运行整个测试集"""
    print(f"\n\n{'='*100}")
    print(f"🎯 {set_name}")
    print(f"{'='*100}")
    print(f"📋 共{len(test_set)}个问题")
    print(f"🕐 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    for i, test_case in enumerate(test_set, 1):
        print(f"\n\n{'#'*100}")
        print(f"进度: {i}/{len(test_set)}")
        print(f"{'#'*100}")
        
        result = test_question(test_case)
        results.append(result)
        
        # 等待避免API限流
        if i < len(test_set):
            print(f"\n⏳ 等待3秒...")
            time.sleep(3)
    
    # 统计
    successful = [r for r in results if r['result']['success']]
    failed = [r for r in results if not r['result']['success']]
    tool_correct = [r for r in results if r['result'].get('tool_correct', False)]
    
    avg_time = sum(r['result']['response_time'] for r in successful) / len(successful) if successful else 0
    
    print(f"\n\n{'='*100}")
    print(f"📊 {set_name} 测试总结")
    print(f"{'='*100}")
    print(f"✅ 成功: {len(successful)}/{len(test_set)} ({len(successful)/len(test_set)*100:.1f}%)")
    print(f"⏱️  平均响应时间: {avg_time:.2f}秒")
    print(f"🎯 工具使用准确率: {len(tool_correct)}/{len(results)} ({len(tool_correct)/len(results)*100:.1f}%)")
    
    if failed:
        print(f"\n❌ 失败的问题:")
        for r in failed:
            print(f"  - [{r['id']}] {r['question'][:50]}...")
    
    return results


def main():
    print("="*100)
    print("🧪 完整测试：Test Set 1, 2, 3")
    print("="*100)
    print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 总问题数: {len(TEST_SET_1)} + {len(TEST_SET_2)} + {len(TEST_SET_3)} = {len(TEST_SET_1) + len(TEST_SET_2) + len(TEST_SET_3)}")
    print("="*100)
    
    # 运行三个测试集
    all_results = {}
    
    print("\n\n🚀 开始测试...")
    
    # Test Set 1
    all_results["test_set_1"] = run_test_set(TEST_SET_1, "Test Set 1 - 基础问题")
    
    print("\n\n⏳ 等待10秒后开始Test Set 2...")
    time.sleep(10)
    
    # Test Set 2
    all_results["test_set_2"] = run_test_set(TEST_SET_2, "Test Set 2 - 进阶问题")
    
    print("\n\n⏳ 等待10秒后开始Test Set 3...")
    time.sleep(10)
    
    # Test Set 3
    all_results["test_set_3"] = run_test_set(TEST_SET_3, "Test Set 3 - 混合场景")
    
    # 总体统计
    print(f"\n\n{'='*100}")
    print("📊 总体测试报告")
    print(f"{'='*100}")
    
    summary = {}
    for set_name, results in all_results.items():
        successful = [r for r in results if r['result']['success']]
        tool_correct = [r for r in results if r['result'].get('tool_correct', False)]
        avg_time = sum(r['result']['response_time'] for r in successful) / len(successful) if successful else 0
        
        summary[set_name] = {
            "total": len(results),
            "success": len(successful),
            "success_rate": len(successful)/len(results)*100,
            "avg_response_time": round(avg_time, 2),
            "tool_accuracy": len(tool_correct)/len(results)*100
        }
        
        print(f"\n{set_name.upper().replace('_', ' ')}:")
        print(f"  成功率: {summary[set_name]['success']}/{summary[set_name]['total']} ({summary[set_name]['success_rate']:.1f}%)")
        print(f"  平均响应时间: {summary[set_name]['avg_response_time']}秒")
        print(f"  工具准确率: {summary[set_name]['tool_accuracy']:.1f}%")
    
    # 保存详细结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_results/complete_test_sets_{timestamp}.json"
    
    os.makedirs("test_results", exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "summary": summary,
            "detailed_results": all_results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n{'='*100}")
    print(f"💾 详细结果已保存到: {output_file}")
    print(f"{'='*100}")
    print("\n✅ 所有测试完成！")


if __name__ == "__main__":
    main()

