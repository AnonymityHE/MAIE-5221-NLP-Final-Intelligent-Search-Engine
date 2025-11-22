#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Set 3对比测试：HKGAI vs 豆包
对比两个模型在文本推理任务上的表现
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import requests
import time
from typing import Dict, List
import json


# Test Set 3 - 文本问题（排除图片问题）
TEXT_QUESTIONS = [
    {
        "id": "CN-1",
        "question": "香港科技大学在哪里？",
        "language": "中文",
        "category": "基础知识"
    },
    {
        "id": "CN-2",
        "question": "RAG系统的核心组件有哪些？",
        "language": "中文",
        "category": "技术知识"
    },
    {
        "id": "CN-3",
        "question": "现在香港的天气怎么样？",
        "language": "中文",
        "category": "实时信息"
    },
    {
        "id": "CN-4",
        "question": "苹果公司的股价是多少？",
        "language": "中文",
        "category": "实时信息"
    },
    {
        "id": "CN-5",
        "question": "比亚迪和特斯拉哪个股价更高？",
        "language": "中文",
        "category": "对比分析"
    },
    {
        "id": "EN-1",
        "question": "Where is the Hong Kong University of Science and Technology located?",
        "language": "英文",
        "category": "基础知识"
    },
    {
        "id": "EN-2",
        "question": "What are the core components of a RAG system?",
        "language": "英文",
        "category": "技术知识"
    },
    {
        "id": "EN-3",
        "question": "What's the weather like in Hong Kong now?",
        "language": "英文",
        "category": "实时信息"
    },
    {
        "id": "EN-4",
        "question": "What is Apple's stock price?",
        "language": "英文",
        "category": "实时信息"
    },
    {
        "id": "EN-5",
        "question": "Which has a higher stock price, BYD or Tesla?",
        "language": "英文",
        "category": "对比分析"
    },
]


def query_agent(question: str, provider: str) -> Dict:
    """
    调用Agent API查询
    
    Args:
        question: 问题
        provider: hkgai 或 doubao_text
        
    Returns:
        {
            "success": bool,
            "answer": str,
            "response_time": float,
            "tools_used": list,
            "error": str (if failed)
        }
    """
    url = "http://localhost:5555/api/agent_query"
    
    # 根据provider选择合适的参数
    if provider == "hkgai":
        payload = {
            "query": question,
            "provider": "hkgai",
            "model": "HKGAI-V1"
        }
    elif provider == "doubao_text":
        # 豆包文本模型（如果有的话，暂时用多模态API但不传图片）
        # 这里我们还是用agent_query，但指定provider
        payload = {
            "query": question,
            "provider": "hkgai",  # 暂时还是用HKGAI的agent
            "model": "HKGAI-V1"
        }
    else:
        return {"success": False, "error": f"不支持的provider: {provider}"}
    
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
                "workflow_steps": len(data.get("workflow_steps", [])),
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


def query_llm_direct(question: str, provider: str) -> Dict:
    """
    直接调用LLM API（绕过Agent）
    
    Args:
        question: 问题
        provider: hkgai 或 doubao
        
    Returns:
        结果字典
    """
    try:
        start_time = time.time()
        
        if provider == "hkgai":
            response = requests.post(
                'https://oneapi.hkgai.net/v1/chat/completions',
                headers={
                    'Authorization': 'Bearer sk-iqA1pjC48rpFXdkU7cCaE3BfBc9145B4BfCbEe0912126646',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'HKGAI-V1',
                    'messages': [{'role': 'user', 'content': question}],
                    'max_tokens': 1000,
                    'temperature': 0.7
                },
                timeout=60
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "answer": data['choices'][0]['message']['content'],
                    "response_time": response_time,
                    "tokens": data.get('usage', {}).get('total_tokens', 0)
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response_time": response_time
                }
                
        elif provider == "doubao":
            response = requests.post(
                'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
                headers={
                    'Authorization': 'Bearer 54579d1e-6f10-4006-9c9c-9bab09425c1d',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'doubao-seed-1-6-251015',
                    'messages': [{'role': 'user', 'content': question}],
                    'max_completion_tokens': 1000,
                    'temperature': 0.7
                },
                timeout=60
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "answer": data['choices'][0]['message']['content'],
                    "response_time": response_time,
                    "tokens": data.get('usage', {}).get('total_tokens', 0)
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response_time": response_time
                }
        else:
            return {"success": False, "error": f"不支持的provider: {provider}"}
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response_time": time.time() - start_time
        }


def run_comparison_test():
    """运行对比测试"""
    print("=" * 100)
    print("🔥 HKGAI vs 豆包：Test Set 3 文本问题对比测试")
    print("=" * 100)
    print(f"\n📋 测试问题数: {len(TEXT_QUESTIONS)}")
    print("🤖 测试模型:")
    print("  - HKGAI-V1 (香港生成式AI)")
    print("  - 豆包 Seed-1-6 (字节跳动)")
    print("\n测试方式: 直接调用LLM API（无Agent工具）")
    print("=" * 100)
    
    results = []
    
    for i, test_case in enumerate(TEXT_QUESTIONS, 1):
        print(f"\n\n{'#'*100}")
        print(f"进度: {i}/{len(TEXT_QUESTIONS)} | ID: {test_case['id']} | 类别: {test_case['category']}")
        print(f"{'#'*100}")
        print(f"\n❓ 问题: {test_case['question']}")
        print(f"🌐 语言: {test_case['language']}")
        
        result = {
            "id": test_case["id"],
            "question": test_case["question"],
            "language": test_case["language"],
            "category": test_case["category"],
            "hkgai": {},
            "doubao": {}
        }
        
        # 测试HKGAI
        print(f"\n{'─'*80}")
        print("🤖 HKGAI-V1")
        print(f"{'─'*80}")
        hkgai_result = query_llm_direct(test_case["question"], "hkgai")
        result["hkgai"] = hkgai_result
        
        if hkgai_result["success"]:
            print(f"✅ 成功 | ⏱️  {hkgai_result['response_time']:.2f}秒 | 📊 {hkgai_result.get('tokens', 0)} tokens")
            print(f"\n📝 回答:")
            answer = hkgai_result['answer']
            if len(answer) > 400:
                print(answer[:400] + "...")
            else:
                print(answer)
        else:
            print(f"❌ 失败: {hkgai_result['error']}")
        
        time.sleep(2)
        
        # 测试豆包
        print(f"\n{'─'*80}")
        print("🤖 豆包 Seed-1-6")
        print(f"{'─'*80}")
        doubao_result = query_llm_direct(test_case["question"], "doubao")
        result["doubao"] = doubao_result
        
        if doubao_result["success"]:
            print(f"✅ 成功 | ⏱️  {doubao_result['response_time']:.2f}秒 | 📊 {doubao_result.get('tokens', 0)} tokens")
            print(f"\n📝 回答:")
            answer = doubao_result['answer']
            if len(answer) > 400:
                print(answer[:400] + "...")
            else:
                print(answer)
        else:
            print(f"❌ 失败: {doubao_result['error']}")
        
        results.append(result)
        
        # 等待避免频率限制
        if i < len(TEXT_QUESTIONS):
            print(f"\n⏳ 等待3秒...")
            time.sleep(3)
    
    # 汇总统计
    print(f"\n\n{'='*100}")
    print("📊 测试总结")
    print(f"{'='*100}")
    
    hkgai_success = sum(1 for r in results if r["hkgai"].get("success", False))
    doubao_success = sum(1 for r in results if r["doubao"].get("success", False))
    
    hkgai_avg_time = sum(r["hkgai"].get("response_time", 0) for r in results if r["hkgai"].get("success", False)) / max(hkgai_success, 1)
    doubao_avg_time = sum(r["doubao"].get("response_time", 0) for r in results if r["doubao"].get("success", False)) / max(doubao_success, 1)
    
    hkgai_avg_tokens = sum(r["hkgai"].get("tokens", 0) for r in results if r["hkgai"].get("success", False)) / max(hkgai_success, 1)
    doubao_avg_tokens = sum(r["doubao"].get("tokens", 0) for r in results if r["doubao"].get("success", False)) / max(doubao_success, 1)
    
    print(f"\n🤖 HKGAI-V1:")
    print(f"  成功率: {hkgai_success}/{len(TEXT_QUESTIONS)} ({hkgai_success/len(TEXT_QUESTIONS)*100:.1f}%)")
    print(f"  平均响应时间: {hkgai_avg_time:.2f}秒")
    print(f"  平均Token数: {hkgai_avg_tokens:.0f}")
    
    print(f"\n🤖 豆包 Seed-1-6:")
    print(f"  成功率: {doubao_success}/{len(TEXT_QUESTIONS)} ({doubao_success/len(TEXT_QUESTIONS)*100:.1f}%)")
    print(f"  平均响应时间: {doubao_avg_time:.2f}秒")
    print(f"  平均Token数: {doubao_avg_tokens:.0f}")
    
    # 按类别统计
    print(f"\n📊 按类别统计:")
    categories = set(r["category"] for r in results)
    for category in categories:
        cat_results = [r for r in results if r["category"] == category]
        cat_hkgai_success = sum(1 for r in cat_results if r["hkgai"].get("success", False))
        cat_doubao_success = sum(1 for r in cat_results if r["doubao"].get("success", False))
        print(f"  {category}:")
        print(f"    HKGAI: {cat_hkgai_success}/{len(cat_results)}")
        print(f"    豆包: {cat_doubao_success}/{len(cat_results)}")
    
    # 按语言统计
    print(f"\n🌐 按语言统计:")
    for lang in ["中文", "英文"]:
        lang_results = [r for r in results if r["language"] == lang]
        lang_hkgai_success = sum(1 for r in lang_results if r["hkgai"].get("success", False))
        lang_doubao_success = sum(1 for r in lang_results if r["doubao"].get("success", False))
        print(f"  {lang}:")
        print(f"    HKGAI: {lang_hkgai_success}/{len(lang_results)}")
        print(f"    豆包: {lang_doubao_success}/{len(lang_results)}")
    
    # 失败案例
    hkgai_failures = [r for r in results if not r["hkgai"].get("success", False)]
    doubao_failures = [r for r in results if not r["doubao"].get("success", False)]
    
    if hkgai_failures:
        print(f"\n❌ HKGAI失败案例:")
        for r in hkgai_failures:
            print(f"  - {r['id']}: {r['question'][:50]}... | {r['hkgai'].get('error', '')}")
    
    if doubao_failures:
        print(f"\n❌ 豆包失败案例:")
        for r in doubao_failures:
            print(f"  - {r['id']}: {r['question'][:50]}... | {r['doubao'].get('error', '')}")
    
    # 保存详细结果
    output_file = "test_hkgai_vs_doubao_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 详细结果已保存到: {output_file}")
    
    print(f"\n{'='*100}")
    print("✅ 对比测试完成！")
    print(f"{'='*100}")


if __name__ == "__main__":
    run_comparison_test()

