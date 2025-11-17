"""
LLM驱动的工作流效果展示 - 多场景测试

展示HKGAI作为规划器的能力：
1. 简单查询（不需要工作流）
2. 对比分析查询（需要工作流）
3. 多步骤复杂查询
4. 边界情况测试
"""
import sys
import os
from typing import Dict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from services.agent.workflow_llm_planner import get_llm_workflow_planner
from services.core.logger import logger
import json


# 测试问题集
TEST_QUERIES = [
    {
        "id": 1,
        "query": "什么是机器学习？",
        "expected": "简单知识查询，不需要工作流",
        "category": "简单查询"
    },
    {
        "id": 2,
        "query": "香港今天天气怎么样？",
        "expected": "单一工具（weather），不需要工作流",
        "category": "简单查询"
    },
    {
        "id": 3,
        "query": "What was the impact of the latest NVIDIA earnings report on their stock price and how does it compare to AMD's?",
        "expected": "多步骤：搜索财报 + NVIDIA股价 + AMD股价 + 综合分析",
        "category": "复杂对比查询（项目公告示例）"
    },
    {
        "id": 4,
        "query": "比较特斯拉和比亚迪最近的股价表现，并分析原因",
        "expected": "多步骤：Tesla股价 + BYD股价 + 新闻搜索 + 分析",
        "category": "中文对比查询"
    },
    {
        "id": 5,
        "query": "苹果公司的股票现在多少钱？",
        "expected": "单一工具（finance），不需要工作流",
        "category": "简单查询"
    },
    {
        "id": 6,
        "query": "给我分析一下微软、谷歌和亚马逊三家科技公司的股价对比",
        "expected": "多步骤：MSFT + GOOG + AMZN股价 + 对比分析",
        "category": "多目标对比"
    },
    {
        "id": 7,
        "query": "香港到深圳需要多长时间，今天天气适合出行吗？",
        "expected": "多步骤：交通查询 + 天气查询 + 综合建议",
        "category": "跨领域综合查询"
    },
    {
        "id": 8,
        "query": "Tell me about the recent developments in AI technology",
        "expected": "网页搜索，可能不需要多步骤工作流",
        "category": "实时信息查询"
    },
]


def print_plan_analysis(query_info: Dict, plan):
    """打印规划分析结果"""
    print("\n" + "="*100)
    print(f"📝 测试 #{query_info['id']}: {query_info['category']}")
    print("="*100)
    print(f"🔍 查询: {query_info['query']}")
    print(f"💭 预期: {query_info['expected']}")
    print("\n" + "-"*100)
    print("🧠 LLM规划结果:")
    print("-"*100)
    print(f"  ✓ 需要工作流: {'是' if plan.requires_workflow else '否'}")
    print(f"  ✓ 工作流类型: {plan.workflow_type}")
    print(f"  ✓ LLM置信度: {plan.confidence:.2f}")
    print(f"  ✓ LLM推理: {plan.reasoning[:150]}...")
    
    if plan.entities:
        print(f"\n  📦 提取的实体:")
        for key, value in plan.entities.items():
            if value:  # 只显示非空值
                print(f"     - {key}: {value}")
    
    if plan.requires_workflow and plan.steps:
        print(f"\n  📋 执行步骤 (共{len(plan.steps)}步):")
        for i, step in enumerate(plan.steps, 1):
            print(f"\n     步骤 {i}:")
            print(f"       - 工具: {step.tool}")
            print(f"       - 动作: {step.action}")
            print(f"       - 查询: {step.query[:80]}...")
            print(f"       - 原因: {step.reason[:80]}...")
            if step.entities:
                print(f"       - 实体: {step.entities}")
            if step.dependencies:
                print(f"       - 依赖: 步骤 {step.dependencies}")
    
    # 评价
    print("\n" + "-"*100)
    print("📊 评价:")
    
    # 判断LLM规划是否合理
    is_correct = True
    feedback = []
    
    if "简单查询" in query_info['category']:
        if plan.requires_workflow:
            is_correct = False
            feedback.append("❌ 误判：简单查询不应该触发工作流")
        else:
            feedback.append("✅ 正确：识别为简单查询，不需要工作流")
    
    elif "对比查询" in query_info['category'] or "多目标" in query_info['category']:
        if not plan.requires_workflow:
            is_correct = False
            feedback.append("❌ 误判：对比查询应该触发工作流")
        else:
            feedback.append("✅ 正确：识别为对比分析，需要多步骤")
            # 检查步骤数是否合理
            if len(plan.steps) < 2:
                feedback.append("⚠️  步骤较少：对比查询通常需要至少2个数据采集步骤")
            elif len(plan.steps) >= 2:
                feedback.append(f"✅ 步骤合理：{len(plan.steps)}个步骤符合对比分析需求")
    
    elif "跨领域" in query_info['category']:
        if not plan.requires_workflow:
            feedback.append("⚠️  可能欠缺：跨领域查询通常需要多工具协作")
        else:
            feedback.append("✅ 正确：识别为跨领域综合查询")
    
    # 检查置信度
    if plan.confidence >= 0.7:
        feedback.append(f"✅ 高置信度：{plan.confidence:.2f} - LLM对规划很有信心")
    elif plan.confidence >= 0.5:
        feedback.append(f"⚠️  中等置信度：{plan.confidence:.2f} - 规划可能有不确定性")
    else:
        feedback.append(f"❌ 低置信度：{plan.confidence:.2f} - 规划质量可能不高")
    
    for f in feedback:
        print(f"  {f}")
    
    print("="*100)
    
    return is_correct, feedback


def run_demo():
    """运行展示"""
    logger.info("\n\n" + "🚀 LLM驱动的工作流效果展示".center(100, "="))
    logger.info("测试HKGAI作为工作流规划器的能力\n")
    
    # 初始化规划器
    tools = ["local_rag", "web_search", "weather", "finance", "transport"]
    planner = get_llm_workflow_planner(tools)
    
    logger.info(f"📍 规划器配置:")
    logger.info(f"   - LLM提供商: HKGAI (via unified_llm_client)")
    logger.info(f"   - 可用工具: {', '.join(tools)}")
    logger.info(f"   - 测试问题数: {len(TEST_QUERIES)}\n")
    
    results = []
    correct_count = 0
    
    for query_info in TEST_QUERIES:
        try:
            # 使用LLM规划器分析查询
            plan = planner.analyze_query(query_info["query"])
            
            # 打印分析结果
            is_correct, feedback = print_plan_analysis(query_info, plan)
            
            if is_correct:
                correct_count += 1
            
            results.append({
                "query": query_info["query"],
                "category": query_info["category"],
                "requires_workflow": plan.requires_workflow,
                "workflow_type": plan.workflow_type,
                "confidence": plan.confidence,
                "steps_count": len(plan.steps),
                "is_correct": is_correct,
                "feedback": feedback
            })
            
        except Exception as e:
            logger.error(f"❌ 测试 #{query_info['id']} 失败: {e}")
            results.append({
                "query": query_info["query"],
                "category": query_info["category"],
                "error": str(e)
            })
    
    # 总结
    print("\n\n" + "="*100)
    print("📊 测试总结")
    print("="*100)
    print(f"总测试数: {len(TEST_QUERIES)}")
    print(f"成功规划: {len([r for r in results if 'error' not in r])}/{len(TEST_QUERIES)}")
    print(f"规划准确: {correct_count}/{len(TEST_QUERIES)}")
    
    # 按类别统计
    print("\n按类别统计:")
    categories = {}
    for r in results:
        cat = r.get("category", "未知")
        if cat not in categories:
            categories[cat] = {"total": 0, "workflow": 0, "correct": 0}
        categories[cat]["total"] += 1
        if r.get("requires_workflow"):
            categories[cat]["workflow"] += 1
        if r.get("is_correct"):
            categories[cat]["correct"] += 1
    
    for cat, stats in categories.items():
        print(f"  - {cat}: {stats['correct']}/{stats['total']} 正确, "
              f"{stats['workflow']}/{stats['total']} 触发工作流")
    
    # 置信度统计
    confidences = [r["confidence"] for r in results if "confidence" in r]
    if confidences:
        avg_confidence = sum(confidences) / len(confidences)
        print(f"\n平均置信度: {avg_confidence:.2f}")
        print(f"最高置信度: {max(confidences):.2f}")
        print(f"最低置信度: {min(confidences):.2f}")
    
    print("\n" + "="*100)
    print("💡 结论:")
    if correct_count / len(TEST_QUERIES) >= 0.8:
        print("  ✅ LLM规划器表现优秀，HKGAI能够很好地理解查询意图")
    elif correct_count / len(TEST_QUERIES) >= 0.6:
        print("  ⚠️  LLM规划器表现尚可，但有改进空间")
    else:
        print("  ❌ LLM规划器表现不佳，建议调整prompt或考虑其他LLM")
    
    print("="*100 + "\n")
    
    return results


if __name__ == "__main__":
    results = run_demo()

