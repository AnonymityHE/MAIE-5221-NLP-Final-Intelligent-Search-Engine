"""
测试新实现的功能：
1. Reranker功能
2. Agent金融工具
3. Agent交通工具
4. 日志系统
5. 环境变量支持
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
import json
from typing import Dict, List

# API基础URL
BASE_URL = "http://localhost:8000/api"


def test_reranker():
    """测试Reranker功能"""
    print("\n" + "="*60)
    print("测试 1: Reranker功能")
    print("="*60)
    
    # 测试RAG查询（应该自动使用Reranker）
    query = "什么是RAG？"
    print(f"\n查询: {query}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/rag_query",
            json={"query": query, "top_k": 5},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 查询成功")
            print(f"答案: {data.get('answer', '')[:200]}...")
            print(f"使用的工具: {data.get('answer_source', 'unknown')}")
            
            if data.get('context'):
                print(f"检索到的文档数量: {len(data['context'])}")
                if data['context']:
                    first_doc = data['context'][0]
                    print(f"第一个文档分数: {first_doc.get('score', 'N/A')}")
        else:
            print(f"❌ 查询失败: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ 测试失败: {e}")


def test_finance_tool():
    """测试金融工具"""
    print("\n" + "="*60)
    print("测试 2: Agent金融工具")
    print("="*60)
    
    test_queries = [
        "AAPL的股价是多少？",
        "比特币价格",
        "TSLA stock price"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        try:
            response = requests.post(
                f"{BASE_URL}/agent_query",
                json={"query": query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 查询成功")
                print(f"使用的工具: {data.get('tools_used', [])}")
                print(f"答案: {data.get('answer', '')[:300]}...")
            else:
                print(f"❌ 查询失败: {response.status_code}")
                print(response.text[:200])
        except Exception as e:
            print(f"❌ 测试失败: {e}")


def test_transport_tool():
    """测试交通工具"""
    print("\n" + "="*60)
    print("测试 3: Agent交通工具")
    print("="*60)
    
    test_queries = [
        "从香港到深圳需要多久？",
        "travel time from Hong Kong to Shenzhen"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        try:
            response = requests.post(
                f"{BASE_URL}/agent_query",
                json={"query": query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 查询成功")
                print(f"使用的工具: {data.get('tools_used', [])}")
                print(f"答案: {data.get('answer', '')[:300]}...")
            else:
                print(f"❌ 查询失败: {response.status_code}")
                print(response.text[:200])
        except Exception as e:
            print(f"❌ 测试失败: {e}")


def test_agent_tool_selection():
    """测试Agent工具选择逻辑"""
    print("\n" + "="*60)
    print("测试 4: Agent工具自动选择")
    print("="*60)
    
    test_cases = [
        ("今天香港的天气怎么样？", ["weather"]),
        ("什么是RAG？", ["local_rag"]),
        ("最新的人工智能新闻", ["web_search"]),
        ("AAPL股价", ["finance"]),
        ("从北京到上海的距离", ["transport"]),
    ]
    
    for query, expected_tools in test_cases:
        print(f"\n查询: {query}")
        print(f"预期工具: {expected_tools}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/agent_query",
                json={"query": query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                actual_tools = data.get('tools_used', [])
                print(f"实际工具: {actual_tools}")
                
                # 检查是否使用了预期工具
                has_expected = any(tool in actual_tools for tool in expected_tools)
                if has_expected:
                    print(f"✅ 工具选择正确")
                else:
                    print(f"⚠️  工具选择与预期不同（可能是多工具组合）")
                print(f"答案预览: {data.get('answer', '')[:150]}...")
            else:
                print(f"❌ 查询失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 测试失败: {e}")


def test_logging():
    """测试日志系统"""
    print("\n" + "="*60)
    print("测试 5: 日志系统")
    print("="*60)
    
    from services.core import logger
    
    print("测试日志输出...")
    logger.debug("这是一条DEBUG日志")
    logger.info("这是一条INFO日志")
    logger.warning("这是一条WARNING日志")
    logger.error("这是一条ERROR日志")
    
    log_file = project_root / "logs" / "rag_system.log"
    if log_file.exists():
        print(f"✅ 日志文件已创建: {log_file}")
        print(f"   文件大小: {log_file.stat().st_size} bytes")
    else:
        print(f"⚠️  日志文件未找到（可能需要先运行一次API）")


def test_config_env():
    """测试环境变量支持"""
    print("\n" + "="*60)
    print("测试 6: 环境变量支持")
    print("="*60)
    
    from services.core import settings
    
    print("当前配置:")
    print(f"  LOG_LEVEL: {settings.LOG_LEVEL}")
    print(f"  USE_RERANKER: {settings.USE_RERANKER}")
    print(f"  TOP_K: {settings.TOP_K}")
    print(f"  MILVUS_HOST: {settings.MILVUS_HOST}")
    print(f"  GEMINI_ENABLED: {settings.GEMINI_ENABLED}")
    
    print("\n✅ 配置加载成功")


def test_health_check():
    """测试健康检查"""
    print("\n" + "="*60)
    print("测试 7: API健康检查")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API服务正常运行")
            print(f"   Milvus: {data.get('milvus_host')}:{data.get('milvus_port')}")
            print(f"   默认模型: {data.get('default_model')}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务，请确保API正在运行")
        print("   启动命令: uvicorn backend.main:app --reload")
    except Exception as e:
        print(f"❌ 测试失败: {e}")


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("RAG系统改进功能测试")
    print("="*60)
    print("\n请确保:")
    print("1. Milvus服务正在运行 (docker compose up -d)")
    print("2. API服务正在运行 (uvicorn backend.main:app --reload)")
    print("3. 已经运行过数据注入脚本 (python scripts/ingest.py)")
    print("\n开始测试...\n")
    
    # 先检查健康状态
    health_ok = False
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            health_ok = True
    except:
        pass
    
    if not health_ok:
        print("⚠️  警告: API服务可能未运行，部分测试可能失败")
        print("   请先启动API: uvicorn backend.main:app --reload\n")
    
    # 运行测试
    test_health_check()
    test_config_env()
    test_logging()
    
    if health_ok:
        test_reranker()
        test_finance_tool()
        test_transport_tool()
        test_agent_tool_selection()
    else:
        print("\n⚠️  跳过需要API服务的测试")
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n提示:")
    print("- 查看日志文件: tail -f logs/rag_system.log")
    print("- 检查API文档: http://localhost:8000/docs")
    print("- 如需测试API功能，请先启动服务")


if __name__ == "__main__":
    main()

