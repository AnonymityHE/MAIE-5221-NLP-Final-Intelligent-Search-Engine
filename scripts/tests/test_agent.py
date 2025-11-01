#!/usr/bin/env python3
"""
Agent功能测试脚本
测试：普通工具调用、工作流、高级重排序等功能
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.agent import agent
from services.core.logger import logger
import json
from typing import Dict


def print_separator(title: str = ""):
    """打印分隔线"""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80 + "\n")


def test_basic_agent():
    """测试基本Agent功能"""
    print_separator("测试1: 基本Agent功能")
    
    test_queries = [
        "什么是RAG？",
        "今天香港的天气怎么样？",
        "比特币的当前价格是多少？",
    ]
    
    for query in test_queries:
        print(f"\n📝 查询: {query}")
        print("-" * 80)
        try:
            result = agent.execute(query)
            
            print(f"✅ 工具使用: {', '.join(result.get('tools_used', []))}")
            print(f"📊 上下文数量: {result.get('contexts_count', 0)}")
            print(f"🤖 使用模型: {result.get('model', 'N/A')}")
            
            answer = result.get('answer', '')
            if answer:
                print(f"\n💬 回答:\n{answer[:300]}{'...' if len(answer) > 300 else ''}")
            else:
                print("⚠️  未生成回答")
            
            if result.get('tokens'):
                tokens = result['tokens']
                print(f"\n🔢 Token使用: 输入={tokens.get('input', 0)}, 输出={tokens.get('output', 0)}, 总计={tokens.get('total', 0)}")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()


def test_workflow():
    """测试工作流功能（多步骤查询）"""
    print_separator("测试2: 动态工作流功能")
    
    # 测试金融对比查询（应该触发工作流）
    test_query = "What was the impact of the latest NVIDIA earnings report on their stock price and how does it compare to AMD's?"
    
    print(f"\n📝 查询: {test_query}")
    print("-" * 80)
    
    try:
        result = agent.execute(test_query)
        
        print(f"✅ 工作流类型: {result.get('workflow_type', 'N/A')}")
        print(f"✅ 工具使用: {', '.join(result.get('tools_used', []))}")
        print(f"📊 工作流步骤完成数: {result.get('workflow_steps_completed', 0)}")
        print(f"🤖 使用模型: {result.get('model', 'N/A')}")
        
        answer = result.get('answer', '')
        if answer:
            print(f"\n💬 回答:\n{answer[:500]}{'...' if len(answer) > 500 else ''}")
        else:
            print("⚠️  未生成回答")
        
        if result.get('tokens'):
            tokens = result['tokens']
            print(f"\n🔢 Token使用: 输入={tokens.get('input', 0)}, 输出={tokens.get('output', 0)}, 总计={tokens.get('total', 0)}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


def test_reranker():
    """测试高级重排序功能（credibility + freshness）"""
    print_separator("测试3: 高级重排序功能")
    
    # 测试实时查询（应该优先新鲜度）
    test_query = "最新的RAG技术发展"
    
    print(f"\n📝 查询: {test_query}")
    print("-" * 80)
    
    try:
        result = agent.execute(test_query)
        
        print(f"✅ 工具使用: {', '.join(result.get('tools_used', []))}")
        print(f"📊 上下文数量: {result.get('contexts_count', 0)}")
        print(f"🤖 使用模型: {result.get('model', 'N/A')}")
        
        # 如果有上下文，说明使用了RAG（会经过reranker）
        if result.get('has_context'):
            print("✅ 使用了RAG检索（包含高级重排序：credibility + freshness）")
        
        answer = result.get('answer', '')
        if answer:
            print(f"\n💬 回答:\n{answer[:300]}{'...' if len(answer) > 300 else ''}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


def test_all_tools():
    """测试所有工具类型"""
    print_separator("测试4: 所有工具类型")
    
    test_cases = [
        ("金融查询", "AAPL的股价是多少？"),
        ("天气查询", "北京今天的天气怎么样？"),
        ("交通查询", "从香港到深圳需要多长时间？"),
        ("实时查询", "最新的AI技术新闻"),
        ("知识库查询", "Milvus是什么？"),
    ]
    
    for tool_type, query in test_cases:
        print(f"\n🔧 {tool_type}: {query}")
        print("-" * 80)
        try:
            result = agent.execute(query)
            
            tools_used = result.get('tools_used', [])
            print(f"✅ 工具: {', '.join(tools_used)}")
            
            answer = result.get('answer', '')
            if answer:
                print(f"💬 回答: {answer[:150]}{'...' if len(answer) > 150 else ''}")
            
        except Exception as e:
            print(f"❌ 错误: {e}")


def main():
    """主测试函数"""
    print_separator("Agent功能测试套件")
    print("正在测试Agent的各种功能...")
    
    try:
        # 测试1: 基本功能
        test_basic_agent()
        
        # 测试2: 工作流
        test_workflow()
        
        # 测试3: 高级重排序
        test_reranker()
        
        # 测试4: 所有工具
        test_all_tools()
        
        print_separator("测试完成")
        print("✅ 所有测试已完成！")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

