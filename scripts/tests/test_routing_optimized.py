#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试路由优化效果 - 只测试关键case"""
import sys
sys.path.append('/Users/anonymity/Desktop/MAIE/MAIE5221 NLP/Final')

import requests
import time
import json

# 只测试之前失败的关键case
KEY_TESTS = [
    # 基础知识类（之前0/3）
    {"id": "KB-1", "q": "香港科技大学在哪里？", "expected": "local_rag", "cat": "基础知识"},
    {"id": "KB-2", "q": "What is HKUST known for?", "expected": "local_rag", "cat": "基础知识"},
    
    # 技术知识类（之前2/7）
    {"id": "TECH-1", "q": "RAG系统的核心组件有哪些？", "expected": "local_rag", "cat": "技术知识"},
    {"id": "TECH-2", "q": "什么是向量数据库？", "expected": "local_rag", "cat": "技术知识"},
    {"id": "TECH-3", "q": "Milvus向量数据库的特点是什么？", "expected": "local_rag", "cat": "技术知识"},
    {"id": "TECH-4", "q": "What is cross-encoder reranking?", "expected": "local_rag", "cat": "技术知识"},
    {"id": "TECH-5", "q": "Explain the concept of embedding in NLP", "expected": "local_rag", "cat": "技术知识"},
    
    # 金融类（验证不受影响）
    {"id": "FIN-1", "q": "苹果公司的股价是多少？", "expected": "finance", "cat": "金融查询"},
    
    # 天气类（验证不受影响）
    {"id": "WX-1", "q": "香港现在天气怎么样？", "expected": "weather", "cat": "天气查询"},
]

URL = "http://localhost:5555/api/agent_query"

def test_one(test_case):
    """测试单个查询"""
    try:
        start = time.time()
        resp = requests.post(URL, json={"query": test_case["q"]}, timeout=30)
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            data = resp.json()
            tools = data.get("tools_used", [])
            matched = test_case["expected"] in tools or (test_case["expected"] == "local_rag" and "local_rag" in str(tools))
            return {
                "success": True,
                "tools": tools,
                "matched": matched,
                "time": elapsed
            }
        return {"success": False, "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

print("="*80)
print("🎯 路由优化验证测试")
print("="*80)
print(f"测试数: {len(KEY_TESTS)}\n")

results = []
for i, test in enumerate(KEY_TESTS, 1):
    print(f"[{i}/{len(KEY_TESTS)}] {test['id']}: {test['q'][:45]}...")
    print(f"   预期: {test['expected']}")
    
    result = test_one(test)
    time.sleep(1.5)  # 短暂等待
    
    if result["success"]:
        status = "✅" if result["matched"] else "❌"
        print(f"   实际: {result['tools']} ({result['time']:.1f}s) {status}")
        results.append({
            "id": test["id"],
            "category": test["cat"],
            "expected": test["expected"],
            "actual": result["tools"],
            "matched": result["matched"]
        })
    else:
        print(f"   错误: {result['error']} ❌")
        results.append({
            "id": test["id"],
            "category": test["cat"],
            "expected": test["expected"],
            "actual": None,
            "matched": False
        })
    print()

# 统计
print("="*80)
print("📊 结果汇总")
print("="*80)
total = len(results)
correct = sum(1 for r in results if r["matched"])
print(f"总测试数: {total}")
print(f"路由正确: {correct}/{total}")
print(f"准确率: {correct/total*100:.1f}%")

# 按类别
print("\n按类别统计:")
cats = {}
for r in results:
    cat = r["category"]
    if cat not in cats:
        cats[cat] = {"total": 0, "correct": 0}
    cats[cat]["total"] += 1
    if r["matched"]:
        cats[cat]["correct"] += 1

for cat, stats in cats.items():
    pct = stats["correct"]/stats["total"]*100
    print(f"  {cat}: {stats['correct']}/{stats['total']} ({pct:.0f}%)")

# 失败case
failed = [r for r in results if not r["matched"]]
if failed:
    print(f"\n❌ 失败case ({len(failed)}个):")
    for r in failed:
        print(f"  {r['id']}: 预期 {r['expected']}, 实际 {r['actual']}")
else:
    print("\n✅ 全部通过！")

# 保存
with open("logs/routing_optimization_test.json", "w") as f:
    json.dump({"total": total, "correct": correct, "accuracy": correct/total*100, "results": results}, f, indent=2, ensure_ascii=False)

print(f"\n💾 结果已保存: logs/routing_optimization_test.json")
print("="*80)

