"""
端到端工作流测试 - 展示完整的问答过程
从规划到执行到最终答案
"""
import sys
import os
from typing import Dict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from services.agent.agent import agent
from services.core.logger import logger


# 精选测试问题
DEMO_QUERIES = [
    {
        "id": 1,
        "query": "什么是RAG技术？",
        "category": "简单知识查询"
    },
    {
        "id": 2,
        "query": "比较一下特斯拉和比亚迪最近的股价表现",
        "category": "金融对比查询"
    },
    {
        "id": 3,
        "query": "What's the current stock price of Apple and Microsoft?",
        "category": "多目标金融查询"
    },
    {
        "id": 4,
        "query": "香港到深圳高铁要多久，今天香港天气怎么样？",
        "category": "跨领域综合查询"
    },
]


def print_full_result(query_info: Dict, result: Dict):
    """打印完整的执行结果"""
    print("\n" + "="*120)
    print(f"📝 测试 #{query_info['id']}: {query_info['category']}")
    print("="*120)
    print(f"🔍 查询: {query_info['query']}")
    print("\n" + "-"*120)
    
    # 工作流信息
    if 'workflow_type' in result:
        print("🔄 工作流信息:")
        print(f"   - 类型: {result.get('workflow_type')}")
        print(f"   - 引擎: {result.get('workflow_engine')}")
        print(f"   - 完成步骤: {result.get('workflow_steps_completed')}/{result.get('contexts_count', 0)}")
        if 'workflow_confidence' in result:
            print(f"   - 置信度: {result.get('workflow_confidence'):.2f}")
    
    # 使用的工具
    print(f"\n🛠️  使用的工具:")
    for i, tool in enumerate(result.get('tools_used', []), 1):
        print(f"   {i}. {tool}")
    
    # LLM信息
    if result.get('model'):
        print(f"\n🤖 LLM模型: {result.get('model')}")
    if result.get('tokens'):
        tokens = result['tokens']
        print(f"   Token使用: 输入={tokens['input']}, 输出={tokens['output']}, 总计={tokens['total']}")
    
    # 最终答案
    print("\n" + "-"*120)
    print("💬 最终答案:")
    print("-"*120)
    answer = result.get('answer', '无答案')
    # 格式化长答案
    if len(answer) > 500:
        lines = answer.split('\n')
        for line in lines:
            if line.strip():
                print(f"   {line}")
    else:
        print(f"   {answer}")
    
    print("="*120 + "\n")


def run_demo():
    """运行端到端演示"""
    logger.info("\n\n" + "🚀 端到端工作流测试".center(120, "="))
    logger.info("展示从规划到执行到最终答案的完整流程\n")
    
    logger.info(f"📍 测试配置:")
    logger.info(f"   - Agent工作流引擎: LLM驱动（优先）+ 规则fallback")
    logger.info(f"   - LLM提供商: HKGAI (主) + Gemini (fallback)")
    logger.info(f"   - 测试问题数: {len(DEMO_QUERIES)}\n")
    
    results = []
    
    for query_info in DEMO_QUERIES:
        try:
            logger.info(f"\n{'='*50} 测试 #{query_info['id']} {'='*50}")
            logger.info(f"开始执行查询: {query_info['query'][:50]}...")
            
            # 执行完整的agent查询
            result = agent.execute(query_info['query'])
            
            # 打印完整结果
            print_full_result(query_info, result)
            
            results.append({
                "query": query_info["query"],
                "category": query_info["category"],
                "success": "error" not in result.get('answer', ''),
                "has_workflow": 'workflow_type' in result,
                "tools_count": len(result.get('tools_used', [])),
                "answer_length": len(result.get('answer', ''))
            })
            
        except Exception as e:
            logger.error(f"❌ 测试 #{query_info['id']} 失败: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "query": query_info["query"],
                "category": query_info["category"],
                "success": False,
                "error": str(e)
            })
    
    # 总结
    print("\n" + "="*120)
    print("📊 测试总结")
    print("="*120)
    successful = sum(1 for r in results if r.get('success'))
    print(f"成功执行: {successful}/{len(DEMO_QUERIES)}")
    print(f"使用工作流: {sum(1 for r in results if r.get('has_workflow'))}/{len(DEMO_QUERIES)}")
    print(f"平均工具数: {sum(r.get('tools_count', 0) for r in results) / len(results):.1f}")
    print(f"平均答案长度: {sum(r.get('answer_length', 0) for r in results) / len(results):.0f} 字符")
    print("="*120 + "\n")
    
    return results


if __name__ == "__main__":
    results = run_demo()

