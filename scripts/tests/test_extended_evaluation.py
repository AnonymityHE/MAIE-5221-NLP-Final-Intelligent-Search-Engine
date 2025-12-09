#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extended Evaluation Test Suite
扩展评估测试套件 - 覆盖更多场景和边界情况
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import requests
import time
import json
from datetime import datetime
from collections import Counter

# 扩展测试集 - 40个测试用例
EXTENDED_TEST_QUESTIONS = [
    # ==================== 基础知识检索 (10题) ====================
    {
        "id": "KB-1",
        "question": "香港科技大学在哪里？",
        "category": "基础知识",
        "expected_tools": ["local_rag"],
        "language": "zh"
    },
    {
        "id": "KB-2", 
        "question": "What is HKUST known for?",
        "category": "基础知识",
        "expected_tools": ["local_rag"],
        "language": "en"
    },
    {
        "id": "KB-3",
        "question": "RAG系统的核心组件有哪些？",
        "category": "技术知识",
        "expected_tools": ["local_rag"],
        "language": "zh"
    },
    {
        "id": "KB-4",
        "question": "How does retrieval-augmented generation work?",
        "category": "技术知识",
        "expected_tools": ["local_rag"],
        "language": "en"
    },
    {
        "id": "KB-5",
        "question": "什么是向量数据库？",
        "category": "技术知识",
        "expected_tools": ["local_rag"],
        "language": "zh"
    },
    {
        "id": "KB-6",
        "question": "Explain the concept of embedding in NLP",
        "category": "技术知识",
        "expected_tools": ["local_rag"],
        "language": "en"
    },
    {
        "id": "KB-7",
        "question": "香港有多少所大学？",
        "category": "基础知识",
        "expected_tools": ["local_rag", "web_search"],
        "language": "zh"
    },
    {
        "id": "KB-8",
        "question": "What is cross-encoder reranking?",
        "category": "技术知识",
        "expected_tools": ["local_rag"],
        "language": "en"
    },
    {
        "id": "KB-9",
        "question": "Milvus向量数据库的特点是什么？",
        "category": "技术知识",
        "expected_tools": ["local_rag"],
        "language": "zh"
    },
    {
        "id": "KB-10",
        "question": "How to improve RAG retrieval quality?",
        "category": "技术知识",
        "expected_tools": ["local_rag"],
        "language": "en"
    },
    
    # ==================== 实时金融查询 (8题) ====================
    {
        "id": "FIN-1",
        "question": "苹果公司的股价是多少？",
        "category": "金融查询",
        "expected_tools": ["finance"],
        "language": "zh"
    },
    {
        "id": "FIN-2",
        "question": "What is Tesla's current stock price?",
        "category": "金融查询",
        "expected_tools": ["finance"],
        "language": "en"
    },
    {
        "id": "FIN-3",
        "question": "比亚迪和特斯拉哪个股价更高？",
        "category": "金融对比",
        "expected_tools": ["finance"],
        "language": "zh"
    },
    {
        "id": "FIN-4",
        "question": "Compare Microsoft and Google stock prices",
        "category": "金融对比",
        "expected_tools": ["finance"],
        "language": "en"
    },
    {
        "id": "FIN-5",
        "question": "英伟达股价多少？",
        "category": "金融查询",
        "expected_tools": ["finance"],
        "language": "zh"
    },
    {
        "id": "FIN-6",
        "question": "Amazon stock price today",
        "category": "金融查询",
        "expected_tools": ["finance"],
        "language": "en"
    },
    {
        "id": "FIN-7",
        "question": "腾讯和阿里巴巴哪个市值更高？",
        "category": "金融对比",
        "expected_tools": ["finance", "web_search"],
        "language": "zh"
    },
    {
        "id": "FIN-8",
        "question": "What is the current price of Bitcoin?",
        "category": "加密货币",
        "expected_tools": ["finance"],
        "language": "en"
    },
    
    # ==================== 天气查询 (8题) ====================
    {
        "id": "WX-1",
        "question": "香港现在天气怎么样？",
        "category": "天气查询",
        "expected_tools": ["weather"],
        "language": "zh"
    },
    {
        "id": "WX-2",
        "question": "What's the weather in Beijing now?",
        "category": "天气查询",
        "expected_tools": ["weather"],
        "language": "en"
    },
    {
        "id": "WX-3",
        "question": "比较香港和北京今天的天气",
        "category": "天气对比",
        "expected_tools": ["weather"],
        "language": "zh"
    },
    {
        "id": "WX-4",
        "question": "Weather forecast for Tokyo",
        "category": "天气查询",
        "expected_tools": ["weather"],
        "language": "en"
    },
    {
        "id": "WX-5",
        "question": "深圳明天会下雨吗？",
        "category": "天气预测",
        "expected_tools": ["weather"],
        "language": "zh"
    },
    {
        "id": "WX-6",
        "question": "Is it raining in London now?",
        "category": "天气查询",
        "expected_tools": ["weather"],
        "language": "en"
    },
    {
        "id": "WX-7",
        "question": "上海和广州哪个更热？",
        "category": "天气对比",
        "expected_tools": ["weather"],
        "language": "zh"
    },
    {
        "id": "WX-8",
        "question": "Compare weather in New York and Los Angeles",
        "category": "天气对比",
        "expected_tools": ["weather"],
        "language": "en"
    },
    
    # ==================== 网络搜索 (8题) ====================
    {
        "id": "WEB-1",
        "question": "最近有什么热门新闻？",
        "category": "实时新闻",
        "expected_tools": ["web_search"],
        "language": "zh"
    },
    {
        "id": "WEB-2",
        "question": "What are the latest AI developments?",
        "category": "实时新闻",
        "expected_tools": ["web_search"],
        "language": "en"
    },
    {
        "id": "WEB-3",
        "question": "铜锣湾有什么好吃的餐厅？",
        "category": "本地信息",
        "expected_tools": ["web_search"],
        "language": "zh"
    },
    {
        "id": "WEB-4",
        "question": "Best hiking trails in Hong Kong",
        "category": "本地信息",
        "expected_tools": ["web_search"],
        "language": "en"
    },
    {
        "id": "WEB-5",
        "question": "GPT-4o有什么新功能？",
        "category": "技术新闻",
        "expected_tools": ["web_search"],
        "language": "zh"
    },
    {
        "id": "WEB-6",
        "question": "When is the next Apple event?",
        "category": "科技事件",
        "expected_tools": ["web_search"],
        "language": "en"
    },
    {
        "id": "WEB-7",
        "question": "香港红馆最近有什么演唱会？",
        "category": "娱乐信息",
        "expected_tools": ["web_search"],
        "language": "zh"
    },
    {
        "id": "WEB-8",
        "question": "Latest iPhone release date",
        "category": "产品信息",
        "expected_tools": ["web_search"],
        "language": "en"
    },
    
    # ==================== 翻译与语言 (6题) ====================
    {
        "id": "LANG-1",
        "question": "香港粤语怎么说？",
        "category": "语言翻译",
        "expected_tools": ["llm_direct"],
        "language": "zh"
    },
    {
        "id": "LANG-2",
        "question": "How do you say 'thank you' in Cantonese?",
        "category": "语言翻译",
        "expected_tools": ["llm_direct"],
        "language": "en"
    },
    {
        "id": "LANG-3",
        "question": "早安用日语怎么说？",
        "category": "语言翻译",
        "expected_tools": ["llm_direct"],
        "language": "zh"
    },
    {
        "id": "LANG-4",
        "question": "Translate 'I love Hong Kong' to Chinese",
        "category": "语言翻译",
        "expected_tools": ["llm_direct"],
        "language": "en"
    },
    {
        "id": "LANG-5",
        "question": "唔该用普通话怎么说？",
        "category": "粤普翻译",
        "expected_tools": ["llm_direct"],
        "language": "zh"
    },
    {
        "id": "LANG-6",
        "question": "What does '多谢' mean in English?",
        "category": "语言翻译",
        "expected_tools": ["llm_direct"],
        "language": "en"
    },
]


def query_agent(question: str, timeout: int = 120) -> dict:
    """调用Agent API"""
    url = "http://localhost:5555/api/agent_query"
    
    payload = {
        "query": question,
        "provider": "hkgai",
        "model": "HKGAI-V1"
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=timeout)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "answer": data.get("answer", ""),
                "response_time": response_time,
                "tools_used": data.get("tools_used", []),
                "provider": data.get("provider", ""),
                "model": data.get("model", "")
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "response_time": response_time
            }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Timeout",
            "response_time": timeout
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response_time": 0
        }


def run_extended_evaluation():
    """运行扩展评估测试"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print("=" * 100)
    print("🧪 Extended Evaluation Test Suite")
    print("=" * 100)
    print(f"测试时间: {timestamp}")
    print(f"测试用例数: {len(EXTENDED_TEST_QUESTIONS)}")
    print("=" * 100)
    
    results = []
    
    for i, test_case in enumerate(EXTENDED_TEST_QUESTIONS, 1):
        print(f"\n{'─'*80}")
        print(f"[{i}/{len(EXTENDED_TEST_QUESTIONS)}] {test_case['id']} | {test_case['category']}")
        print(f"❓ {test_case['question']}")
        print(f"🔧 预期: {test_case['expected_tools']}")
        
        result = query_agent(test_case["question"])
        
        test_result = {
            "id": test_case["id"],
            "question": test_case["question"],
            "category": test_case["category"],
            "language": test_case["language"],
            "expected_tools": test_case["expected_tools"],
            **result
        }
        
        if result["success"]:
            tools_used = result.get("tools_used", [])
            expected = set(test_case["expected_tools"])
            actual = set(tools_used)
            
            tool_match = bool(expected & actual) or (not tools_used and "llm_direct" in expected)
            
            status = "✅" if tool_match else "⚠️"
            print(f"{status} {result['response_time']:.2f}s | 工具: {tools_used or ['direct']}")
            print(f"📝 {result['answer'][:100]}...")
            
            test_result["tool_match"] = tool_match
        else:
            print(f"❌ 失败: {result['error']}")
            test_result["tool_match"] = False
        
        results.append(test_result)
        
        # 短暂等待避免API限流
        if i < len(EXTENDED_TEST_QUESTIONS):
            time.sleep(2)
    
    # ==================== 统计汇总 ====================
    print(f"\n\n{'='*100}")
    print("📊 EVALUATION RESULTS SUMMARY")
    print(f"{'='*100}")
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    tool_matched = [r for r in successful if r.get("tool_match")]
    
    total = len(results)
    success_rate = len(successful) / total * 100
    tool_accuracy = len(tool_matched) / len(successful) * 100 if successful else 0
    
    print(f"\n📈 Overall Metrics:")
    print(f"  • Total Queries: {total}")
    print(f"  • Success Rate: {len(successful)}/{total} ({success_rate:.1f}%)")
    print(f"  • Tool Routing Accuracy: {len(tool_matched)}/{len(successful)} ({tool_accuracy:.1f}%)")
    
    if successful:
        avg_time = sum(r["response_time"] for r in successful) / len(successful)
        min_time = min(r["response_time"] for r in successful)
        max_time = max(r["response_time"] for r in successful)
        print(f"  • Avg Response Time: {avg_time:.2f}s (min: {min_time:.2f}s, max: {max_time:.2f}s)")
    
    # 按类别统计
    print(f"\n📊 Results by Category:")
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "success": 0, "tool_match": 0, "times": []}
        categories[cat]["total"] += 1
        if r.get("success"):
            categories[cat]["success"] += 1
            categories[cat]["times"].append(r["response_time"])
            if r.get("tool_match"):
                categories[cat]["tool_match"] += 1
    
    for cat, stats in sorted(categories.items()):
        success_pct = stats["success"] / stats["total"] * 100
        tool_pct = stats["tool_match"] / stats["success"] * 100 if stats["success"] else 0
        avg_t = sum(stats["times"]) / len(stats["times"]) if stats["times"] else 0
        print(f"  {cat}: {stats['success']}/{stats['total']} ({success_pct:.0f}%) | Tool: {tool_pct:.0f}% | Avg: {avg_t:.1f}s")
    
    # 按语言统计
    print(f"\n🌐 Results by Language:")
    for lang in ["zh", "en"]:
        lang_results = [r for r in results if r["language"] == lang]
        lang_success = [r for r in lang_results if r.get("success")]
        if lang_results:
            print(f"  {lang.upper()}: {len(lang_success)}/{len(lang_results)} ({len(lang_success)/len(lang_results)*100:.1f}%)")
    
    # 工具使用统计
    print(f"\n🔧 Tool Usage Statistics:")
    all_tools = []
    for r in successful:
        all_tools.extend(r.get("tools_used", ["direct"]))
    if not all_tools:
        all_tools = ["direct"]
    tool_counts = Counter(all_tools)
    for tool, count in tool_counts.most_common():
        print(f"  • {tool}: {count} times ({count/len(successful)*100:.1f}%)")
    
    # 失败案例
    if failed:
        print(f"\n❌ Failed Queries ({len(failed)}):")
        for r in failed[:5]:  # 只显示前5个
            print(f"  • {r['id']}: {r.get('error', 'Unknown')}")
    
    # 保存结果
    output = {
        "timestamp": timestamp,
        "summary": {
            "total_queries": total,
            "success_count": len(successful),
            "success_rate": success_rate,
            "tool_accuracy": tool_accuracy,
            "avg_response_time": avg_time if successful else 0,
            "categories": {cat: {
                "total": stats["total"],
                "success": stats["success"],
                "tool_match": stats["tool_match"],
                "avg_time": sum(stats["times"]) / len(stats["times"]) if stats["times"] else 0
            } for cat, stats in categories.items()}
        },
        "results": results
    }
    
    output_file = f"logs/extended_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("logs", exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"\n{'='*100}")
    print("✅ Extended Evaluation Complete!")
    print(f"{'='*100}")
    
    return output


if __name__ == "__main__":
    run_extended_evaluation()

