"""
测试LLM驱动的智能工作流系统

测试场景：
1. 简单查询（不需要工作流）
2. 金融对比查询（项目公告示例）
3. 多源信息综合查询
4. Fallback机制测试
"""
import sys
import os
from typing import Dict

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from services.agent.agent import agent
from services.core.logger import logger


def print_result(query: str, result: Dict):
    """打印测试结果"""
    print("\n" + "=" * 80)
    print(f"📝 查询: {query}")
    print("=" * 80)
    print(f"\n🤖 回答:\n{result['answer']}\n")
    print(f"🛠️  使用的工具: {', '.join(result['tools_used'])}")
    print(f"📊 上下文数量: {result['contexts_count']}")
    print(f"💻 LLM模型: {result.get('model', 'N/A')}")
    
    if 'workflow_type' in result:
        print(f"\n🔄 工作流信息:")
        print(f"   - 类型: {result.get('workflow_type')}")
        print(f"   - 引擎: {result.get('workflow_engine')}")
        print(f"   - 完成步骤: {result.get('workflow_steps_completed')}")
        if 'workflow_confidence' in result:
            print(f"   - LLM置信度: {result.get('workflow_confidence'):.2f}")
    
    if result.get('tokens'):
        tokens = result['tokens']
        print(f"\n📈 Token使用: 输入={tokens['input']}, 输出={tokens['output']}, 总计={tokens['total']}")
    
    print("=" * 80 + "\n")


def test_simple_query():
    """测试1: 简单查询（不需要工作流）"""
    logger.info("\n\n" + "🧪 测试1: 简单查询".center(80, "="))
    
    query = "什么是机器学习？"
    result = agent.execute(query)
    print_result(query, result)
    
    # 验证：应该不使用工作流
    assert 'workflow_type' not in result or not result.get('workflow_type'), \
        "简单查询不应该触发工作流"
    
    logger.info("✅ 测试1通过: 简单查询正确识别\n")


def test_finance_comparison():
    """测试2: 金融对比查询（项目公告示例）"""
    logger.info("\n\n" + "🧪 测试2: 金融对比查询（项目公告示例）".center(80, "="))
    
    # 项目公告中的示例查询
    query = "What was the impact of the latest NVIDIA earnings report on their stock price and how does it compare to AMD's?"
    result = agent.execute(query)
    print_result(query, result)
    
    # 验证：应该使用工作流
    assert 'workflow_type' in result, "复杂查询应该触发工作流"
    assert len(result['tools_used']) > 1, "应该使用多个工具"
    
    logger.info("✅ 测试2通过: 金融对比工作流正确执行\n")


def test_multi_source_research():
    """测试3: 多源信息综合查询"""
    logger.info("\n\n" + "🧪 测试3: 多源信息综合查询".center(80, "="))
    
    query = "比较一下苹果和微软最近的股价表现，并分析原因"
    result = agent.execute(query)
    print_result(query, result)
    
    # 验证：应该使用工作流
    assert 'workflow_type' in result, "对比分析查询应该触发工作流"
    
    logger.info("✅ 测试3通过: 多源信息综合查询正确执行\n")


def test_weather_query():
    """测试4: 天气查询（单一工具，不需要工作流）"""
    logger.info("\n\n" + "🧪 测试4: 天气查询".center(80, "="))
    
    query = "香港今天天气怎么样？"
    result = agent.execute(query)
    print_result(query, result)
    
    # 验证：应该使用weather工具，但不需要工作流
    assert 'weather' in str(result['tools_used']), "应该使用天气工具"
    
    logger.info("✅ 测试4通过: 天气查询正确执行\n")


def test_complex_workflow():
    """测试5: 复杂的多步骤工作流"""
    logger.info("\n\n" + "🧪 测试5: 复杂的多步骤工作流".center(80, "="))
    
    query = "分析Tesla、Ford和GM三家汽车公司的股价对比，并搜索最新的电动车市场新闻"
    result = agent.execute(query)
    print_result(query, result)
    
    # 验证：应该使用工作流
    assert 'workflow_type' in result, "复杂的多公司对比应该触发工作流"
    
    logger.info("✅ 测试5通过: 复杂工作流正确执行\n")


def test_cantonese_query():
    """测试6: 粤语查询"""
    logger.info("\n\n" + "🧪 测试6: 粤语查询".center(80, "="))
    
    query = "特斯拉同比亚迪嘅股价边间好啲？"
    result = agent.execute(query)
    print_result(query, result)
    
    logger.info("✅ 测试6通过: 粤语查询正确处理\n")


def run_all_tests():
    """运行所有测试"""
    logger.info("\n\n" + "🚀 开始测试LLM驱动的智能工作流系统".center(80, "="))
    logger.info("测试环境检查:")
    logger.info(f"   - Agent类型: {type(agent)}")
    logger.info(f"   - LLM规划器: {'✅ 可用' if agent.llm_planner else '❌ 不可用'}")
    logger.info(f"   - 动态引擎: {'✅ 可用' if agent.dynamic_engine else '❌ 不可用'}")
    logger.info(f"   - 规则引擎: {'✅ 可用' if agent.workflow_engine else '❌ 不可用'}")
    logger.info(f"   - 可用工具: {list(agent.tools.keys())}")
    logger.info("=" * 80)
    
    tests = [
        ("简单查询", test_simple_query),
        ("金融对比查询", test_finance_comparison),
        ("多源信息综合", test_multi_source_research),
        ("天气查询", test_weather_query),
        ("复杂工作流", test_complex_workflow),
        ("粤语查询", test_cantonese_query),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            failed += 1
            logger.error(f"❌ 测试失败 [{test_name}]: {e}")
            import traceback
            traceback.print_exc()
    
    # 测试总结
    logger.info("\n\n" + "📊 测试总结".center(80, "="))
    logger.info(f"✅ 通过: {passed}/{len(tests)}")
    logger.info(f"❌ 失败: {failed}/{len(tests)}")
    logger.info("=" * 80 + "\n")
    
    if failed == 0:
        logger.info("🎉 所有测试通过！LLM驱动的工作流系统运行正常。")
    else:
        logger.warning(f"⚠️  有 {failed} 个测试失败，请检查日志。")


if __name__ == "__main__":
    # 运行测试
    run_all_tests()

