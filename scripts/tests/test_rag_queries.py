#!/usr/bin/env python3
"""
测试RAG查询功能
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.vector.milvus_client import milvus_client
from services.vector.retriever import Retriever
from services.llm.unified_client import UnifiedLLMClient
from services.core.config import settings
from sentence_transformers import SentenceTransformer
import time

def test_rag_queries():
    """测试RAG查询"""
    print("=" * 80)
    print("RAG查询测试")
    print("=" * 80)
    
    # 1. 连接Milvus
    print("\n1. 连接Milvus...")
    if not milvus_client.connect():
        print("❌ 无法连接到Milvus")
        return False
    print("✅ Milvus连接成功")
    
    # 2. 检查集合数据
    stats = milvus_client.get_collection_stats()
    if stats and stats.get('num_entities', 0) == 0:
        print("⚠️  集合中没有数据，请先运行索引脚本")
        return False
    print(f"✅ 集合中有 {stats['num_entities']} 条数据")
    
    # 3. 初始化RAG组件
    print("\n2. 初始化RAG组件...")
    try:
        retriever = Retriever()
        llm_client = UnifiedLLMClient()
        print("✅ RAG组件初始化成功")
    except Exception as e:
        print(f"❌ RAG组件初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. 测试查询列表
    test_queries = [
        "Tell me about Sereleia",
        "What is Aetherian Dynamics?",
        "Describe Planet Xylos",
        "Who is Dr. Elara Vance?",
        "What happened during the Great Digital Awakening?",
        "What are the main islands of Sereleia?",
        "How does the Sereleian government work?",
        "What is the Whispering Revolution?",
    ]
    
    print(f"\n3. 开始测试 {len(test_queries)} 个查询...")
    print("=" * 80)
    
    results_summary = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n查询 {i}/{len(test_queries)}: {query}")
        print("-" * 80)
        
        try:
            start_time = time.time()
            
            # 1. 检索相关文档
            retrieved_docs = retriever.search(query, top_k=3)
            
            # 2. 构建上下文
            if retrieved_docs:
                context = "\n\n".join([
                    f"[来源: {doc.get('source_file', 'N/A')}]\n{doc.get('text', '')}"
                    for doc in retrieved_docs
                ])
                
                # 3. 使用LLM生成答案
                system_prompt = "你是一个专业的AI助手，请基于提供的上下文信息回答问题。如果上下文中没有相关信息，请诚实地说不知道。"
                user_prompt = f"""基于以下上下文信息回答用户问题：

上下文信息:
{context}

用户问题: {query}

请用简洁、准确的语言回答问题:"""
                
                llm_result = llm_client.chat(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    max_tokens=2048,
                    temperature=0.7
                )
                answer = llm_result.get('content', '无法生成答案')
            else:
                # 没有检索到文档，直接回答
                system_prompt = "你是一个专业的AI助手，请直接回答问题。"
                user_prompt = f"请回答以下问题: {query}"
                llm_result = llm_client.chat(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    max_tokens=2048,
                    temperature=0.7
                )
                answer = llm_result.get('content', '无法生成答案')
                retrieved_docs = []
            
            elapsed_time = time.time() - start_time
            
            print(f"✅ 查询成功 (耗时: {elapsed_time:.2f}秒)")
            print(f"\n回答:")
            print(answer[:500] + "..." if len(answer) > 500 else answer)
            
            if retrieved_docs:
                print(f"\n来源 ({len(retrieved_docs)} 个):")
                for j, doc in enumerate(retrieved_docs[:3], 1):
                    print(f"  {j}. {doc.get('source_file', 'N/A')}")
                    print(f"     相似度: {doc.get('score', 0):.4f}")
            
            results_summary.append({
                'query': query,
                'success': True,
                'time': elapsed_time,
                'sources_count': len(retrieved_docs)
            })
                
        except Exception as e:
            print(f"❌ 查询失败: {e}")
            import traceback
            traceback.print_exc()
            results_summary.append({
                'query': query,
                'success': False,
                'error': str(e)
            })
        
        # 每两个查询之间稍作等待
        if i < len(test_queries):
            time.sleep(1)
    
    # 5. 汇总结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    success_count = sum(1 for r in results_summary if r.get('success'))
    total_count = len(results_summary)
    
    print(f"\n总查询数: {total_count}")
    print(f"成功: {success_count}")
    print(f"失败: {total_count - success_count}")
    
    if success_count > 0:
        avg_time = sum(r['time'] for r in results_summary if r.get('success')) / success_count
        print(f"平均查询时间: {avg_time:.2f}秒")
    
    print("\n详细结果:")
    for r in results_summary:
        status = "✅" if r.get('success') else "❌"
        print(f"  {status} {r['query']}")
        if r.get('success'):
            print(f"     耗时: {r['time']:.2f}秒, 来源数: {r.get('sources_count', 0)}")
        elif r.get('error'):
            print(f"     错误: {r['error'][:100]}")
    
    print("\n" + "=" * 80)
    print("✅ 测试完成！")
    print("=" * 80)
    
    return success_count == total_count

if __name__ == "__main__":
    success = test_rag_queries()
    sys.exit(0 if success else 1)

