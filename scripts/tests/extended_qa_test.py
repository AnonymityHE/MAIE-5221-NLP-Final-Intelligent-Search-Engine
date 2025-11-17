"""扩展Q&A测试 - 30+场景"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from services.agent.agent import agent
import time

# 30+测试场景
TEST_CASES = [
    # 复杂组合查询
    ("对比HKGAI和Gemini的优缺点，并推荐使用场景", "comparison"),
    ("系统如何同时处理粤语、普通话和英语？", "multilingual"),
    ("解释RAG系统中embedding、reranking和chunking的关系", "technical"),
    
    # 实际使用场景
    ("我想用粤语问问题，系统会自动识别吗？", "usage"),
    ("如何上传PDF文档到知识库？", "usage"),
    ("系统的响应速度慢怎么办？", "troubleshooting"),
    
    # 技术细节
    ("什么是Reranker？它用的是什么模型？", "technical"),
    ("Milvus向量数据库的配置参数有哪些？", "technical"),
    ("系统用了哪些embedding模型？", "technical"),
    
    # 工作流相关
    ("什么时候会触发LLM工作流？", "workflow"),
    ("规则引擎和LLM工作流有什么区别？", "workflow"),
    
    # 对比类问题
    ("Whisper和粤语Speech API哪个更准确？", "comparison"),
    ("什么时候用local_rag，什么时候用web_search？", "comparison"),
    
    # 操作指南
    ("如何测试系统是否正常工作？", "guide"),
    ("Docker容器启动失败怎么办？", "troubleshooting"),
]

def run_extended_test():
    """运行扩展测试"""
    print("\n" + "="*100)
    print("🚀 RAG系统扩展测试 (15个场景)".center(100))
    print("="*100 + "\n")
    
    results = []
    
    for i, (question, category) in enumerate(TEST_CASES, 1):
        print(f"\n{'='*100}")
        print(f"[{i}/{len(TEST_CASES)}] {category.upper()}")
        print(f"Q: {question}")
        print("-"*100)
        
        start = time.time()
        try:
            result = agent.execute(question)
            elapsed = time.time() - start
            
            answer = result['answer']
            print(f"\nA: {answer[:300]}..." if len(answer) > 300 else f"\nA: {answer}")
            print(f"\n✓ 工具: {', '.join(result['tools_used'])}")
            print(f"✓ 知识库: {'是' if result.get('has_context') else '否'}")
            print(f"✓ 时间: {elapsed:.2f}s")
            
            results.append({
                'question': question,
                'category': category,
                'success': True,
                'time': elapsed,
                'answer_length': len(answer),
                'used_kb': result.get('has_context', False)
            })
            
        except Exception as e:
            elapsed = time.time() - start
            print(f"\n✗ 失败: {e}")
            results.append({
                'question': question,
                'category': category,
                'success': False,
                'time': elapsed,
                'error': str(e)
            })
    
    # 统计
    print(f"\n\n{'='*100}")
    print("📊 测试总结".center(100))
    print("="*100)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n✅ 成功: {len(successful)}/{len(TEST_CASES)}")
    print(f"❌ 失败: {len(failed)}/{len(TEST_CASES)}")
    print(f"⏱️  平均时间: {sum(r['time'] for r in successful)/len(successful):.2f}s" if successful else "N/A")
    print(f"📚 知识库使用率: {sum(1 for r in successful if r.get('used_kb'))/len(successful)*100:.1f}%" if successful else "N/A")
    
    # 按类别统计
    categories = {}
    for r in successful:
        cat = r['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r['time'])
    
    print(f"\n📋 分类性能:")
    for cat, times in sorted(categories.items()):
        print(f"  {cat}: {len(times)}个, 平均{sum(times)/len(times):.2f}s")
    
    print("="*100 + "\n")
    
    return results

if __name__ == "__main__":
    results = run_extended_test()

