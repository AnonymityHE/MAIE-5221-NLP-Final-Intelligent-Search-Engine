"""测试工具调用准确性"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from services.agent.agent import agent

# 针对不同工具的测试
TOOL_TESTS = {
    "finance": [
        ("苹果公司的股价是多少？", ["finance"]),
        ("NVIDIA和AMD股票对比", ["finance"]),
        ("特斯拉最新股价", ["finance"]),
    ],
    "weather": [
        ("香港今天天气", ["weather"]),
        ("北京明天会下雨吗？", ["weather"]),
    ],
    "local_rag": [
        ("如何使用粤语输入？", ["local_rag"]),
        ("系统支持哪些语言？", ["local_rag"]),
        ("什么是Reranker？", ["local_rag"]),
    ],
    "workflow": [
        ("对比HKGAI和Gemini的区别", ["local_rag", "workflow"]),  # 应该触发工作流
        ("系统如何处理多语言？", ["local_rag", "workflow"]),
    ],
}

def test_tool_selection():
    """测试工具选择准确性"""
    print("\n" + "="*100)
    print("🔧 工具调用准确性测试".center(100))
    print("="*100 + "\n")
    
    total = 0
    correct = 0
    
    for tool_category, tests in TOOL_TESTS.items():
        print(f"\n{'='*100}")
        print(f"测试类别: {tool_category.upper()}")
        print("="*100)
        
        for query, expected_tools in tests:
            total += 1
            print(f"\nQ: {query}")
            print(f"预期工具: {expected_tools}")
            
            result = agent.execute(query)
            actual_tools = result['tools_used']
            
            # 检查是否使用了预期工具（宽松检查：只要包含一个即可）
            tool_match = any(
                any(expected in tool for expected in expected_tools) 
                for tool in actual_tools
            )
            
            if tool_match:
                print(f"✓ 实际工具: {actual_tools} ✓")
                correct += 1
            else:
                print(f"✗ 实际工具: {actual_tools} (不匹配)")
            
            # 显示答案片段
            answer = result['answer']
            print(f"A: {answer[:150]}...")
    
    # 统计
    print(f"\n\n{'='*100}")
    print("📊 工具选择准确性统计".center(100))
    print("="*100)
    print(f"\n准确率: {correct}/{total} = {correct/total*100:.1f}%")
    
    if correct/total >= 0.8:
        print("✅ 工具选择准确性良好！")
    elif correct/total >= 0.6:
        print("⚠️  工具选择准确性一般，建议优化")
    else:
        print("❌ 工具选择准确性较低，需要改进")
    
    print("="*100 + "\n")
    
    return correct/total

if __name__ == "__main__":
    accuracy = test_tool_selection()

