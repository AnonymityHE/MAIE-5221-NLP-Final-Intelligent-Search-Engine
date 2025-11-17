"""
知识库Q&A演示测试
展示基于新构建的知识库的实际问答效果
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from services.agent.agent import agent
from services.core.logger import logger
import time

# 设计多样化的测试问题
TEST_QUESTIONS = [
    {
        "category": "系统使用",
        "language": "zh",
        "question": "如何使用粤语进行语音输入？",
        "expected_topics": ["Whisper", "粤语API", "STT", "自动检测"]
    },
    {
        "category": "技术架构",
        "language": "zh",
        "question": "系统采用了什么样的工作流架构？LLM在其中起什么作用？",
        "expected_topics": ["LLM驱动", "规则引擎", "动态执行", "工具调用"]
    },
    {
        "category": "功能查询",
        "language": "en",
        "question": "What tools are available in this system and what can they do?",
        "expected_topics": ["local_rag", "web_search", "finance", "weather", "transport"]
    },
    {
        "category": "技术细节",
        "language": "en",
        "question": "What is reranking and why is it important in RAG systems?",
        "expected_topics": ["cross-encoder", "relevance", "semantic", "ranking"]
    },
    {
        "category": "多语言支持",
        "language": "zh",
        "question": "这个系统支持哪些语言？分别在哪些方面支持？",
        "expected_topics": ["粤语", "普通话", "英语", "STT", "TTS", "embedding"]
    },
    {
        "category": "API对比",
        "language": "en",
        "question": "What's the difference between HKGAI and Gemini APIs? When does the system use each one?",
        "expected_topics": ["primary", "fallback", "quota", "failure", "automatic"]
    },
    {
        "category": "知识库管理",
        "language": "zh",
        "question": "我想添加新文档到知识库，有什么方法？",
        "expected_topics": ["上传", "API", "命令行", "索引", "文件格式"]
    },
    {
        "category": "RAG优化",
        "language": "zh",
        "question": "RAG系统中的chunking策略有哪些最佳实践？",
        "expected_topics": ["chunk size", "overlap", "semantic", "metadata", "boundaries"]
    },
    {
        "category": "故障排查",
        "language": "zh",
        "question": "如果Milvus连接失败应该怎么办？",
        "expected_topics": ["Docker", "端口", "配置", "重启"]
    },
]

def format_answer(answer: str, max_length: int = 600) -> str:
    """格式化答案输出，添加适当的换行和截断"""
    lines = answer.split('\n')
    formatted_lines = []
    current_length = 0
    
    for line in lines:
        if current_length + len(line) > max_length:
            formatted_lines.append("   " + line[:max_length - current_length] + "...")
            formatted_lines.append("   [答案已截断，完整内容请查看详细输出]")
            break
        formatted_lines.append("   " + line)
        current_length += len(line)
    
    return '\n'.join(formatted_lines)

def test_qa_demo():
    """运行Q&A演示测试"""
    logger.info("\n" + "="*120)
    logger.info("🎯 知识库Q&A演示测试".center(120))
    logger.info("="*120)
    logger.info(f"\n总测试问题数: {len(TEST_QUESTIONS)}")
    logger.info("测试内容: 系统使用、技术架构、功能查询、技术细节、多语言、API对比、知识库管理、RAG优化、故障排查")
    logger.info("="*120 + "\n")
    
    results = []
    total_time = 0
    
    for i, test_case in enumerate(TEST_QUESTIONS, 1):
        print("\n" + "="*120)
        print(f"📝 问题 {i}/{len(TEST_QUESTIONS)}")
        print("="*120)
        print(f"分类: {test_case['category']}")
        print(f"语言: {test_case['language']}")
        print(f"问题: {test_case['question']}")
        print("-"*120)
        
        # 执行查询
        start_time = time.time()
        try:
            result = agent.execute(test_case['question'])
            elapsed_time = time.time() - start_time
            total_time += elapsed_time
            
            answer = result.get('answer', '未获取到答案')
            tools_used = result.get('tools_used', [])
            contexts_count = result.get('contexts_count', 0)
            has_context = result.get('has_context', False)
            tokens = result.get('tokens', {})
            workflow_type = result.get('workflow_type')
            workflow_engine = result.get('workflow_engine')
            
            # 显示答案
            print(f"\n💡 答案:")
            print(format_answer(answer))
            
            # 显示元信息
            print(f"\n📊 执行信息:")
            print(f"   - 响应时间: {elapsed_time:.2f}秒")
            print(f"   - 使用工具: {', '.join(tools_used)}")
            print(f"   - 检索上下文数: {contexts_count}")
            print(f"   - 使用知识库: {'是' if has_context else '否'}")
            
            if workflow_engine:
                print(f"   - 工作流引擎: {workflow_engine}")
                print(f"   - 工作流类型: {workflow_type}")
            
            if tokens:
                print(f"   - Token使用: 输入={tokens.get('input', 0)}, 输出={tokens.get('output', 0)}, 总计={tokens.get('total', 0)}")
            
            # 检查预期主题是否出现在答案中
            expected_topics = test_case.get('expected_topics', [])
            found_topics = [topic for topic in expected_topics if topic.lower() in answer.lower()]
            
            if found_topics:
                print(f"   - 覆盖主题: {', '.join(found_topics)} ({len(found_topics)}/{len(expected_topics)})")
            
            # 评估答案质量
            quality_score = "优秀" if len(found_topics) >= len(expected_topics) * 0.6 else "良好" if len(found_topics) >= len(expected_topics) * 0.3 else "一般"
            print(f"   - 答案质量: {quality_score}")
            
            results.append({
                'question': test_case['question'],
                'category': test_case['category'],
                'success': True,
                'time': elapsed_time,
                'tools': tools_used,
                'contexts': contexts_count,
                'quality': quality_score,
                'topics_found': len(found_topics),
                'topics_total': len(expected_topics),
                'answer_length': len(answer),
            })
            
            print("="*120)
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            total_time += elapsed_time
            
            logger.error(f"❌ 问题执行失败: {e}")
            import traceback
            traceback.print_exc()
            
            results.append({
                'question': test_case['question'],
                'category': test_case['category'],
                'success': False,
                'time': elapsed_time,
                'error': str(e)
            })
            
            print("="*120)
        
        # 每个问题之间稍作停顿
        time.sleep(0.5)
    
    # 输出总体统计
    print("\n" + "="*120)
    print("📊 测试总结".center(120))
    print("="*120)
    
    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]
    
    print(f"\n✅ 成功: {len(successful)}/{len(TEST_QUESTIONS)}")
    print(f"❌ 失败: {len(failed)}/{len(TEST_QUESTIONS)}")
    print(f"⏱️  总耗时: {total_time:.2f}秒")
    print(f"⏱️  平均响应时间: {total_time/len(TEST_QUESTIONS):.2f}秒")
    
    if successful:
        avg_contexts = sum(r.get('contexts', 0) for r in successful) / len(successful)
        print(f"📚 平均检索上下文数: {avg_contexts:.1f}")
        
        # 按分类统计
        print(f"\n📋 分类统计:")
        categories = {}
        for r in successful:
            cat = r['category']
            if cat not in categories:
                categories[cat] = {'count': 0, 'avg_time': 0, 'total_time': 0}
            categories[cat]['count'] += 1
            categories[cat]['total_time'] += r['time']
        
        for cat, stats in categories.items():
            stats['avg_time'] = stats['total_time'] / stats['count']
            print(f"   - {cat}: {stats['count']}个问题, 平均{stats['avg_time']:.2f}秒")
        
        # 质量统计
        print(f"\n⭐ 质量分布:")
        quality_counts = {}
        for r in successful:
            quality = r.get('quality', '未知')
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        for quality, count in quality_counts.items():
            print(f"   - {quality}: {count}个 ({count/len(successful)*100:.1f}%)")
        
        # 工具使用统计
        print(f"\n🛠️  工具使用统计:")
        tool_counts = {}
        for r in successful:
            for tool in r.get('tools', []):
                tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        for tool, count in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {tool}: {count}次")
    
    if failed:
        print(f"\n❌ 失败问题:")
        for r in failed:
            print(f"   - {r['question'][:60]}... (错误: {r.get('error', '未知')})")
    
    print("\n" + "="*120)
    print("✅ Q&A演示测试完成！".center(120))
    print("="*120 + "\n")
    
    # 保存详细结果到文件
    output_file = 'docs/QA_TEST_RESULTS.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 知识库Q&A测试结果\n\n")
        f.write(f"测试日期: 2025-11-17\n")
        f.write(f"总问题数: {len(TEST_QUESTIONS)}\n")
        f.write(f"成功: {len(successful)}\n")
        f.write(f"失败: {len(failed)}\n\n")
        f.write("---\n\n")
        
        for i, (test_case, result) in enumerate(zip(TEST_QUESTIONS, results), 1):
            f.write(f"## 问题 {i}: {test_case['category']}\n\n")
            f.write(f"**问题**: {test_case['question']}\n\n")
            
            if result.get('success'):
                # 重新获取完整答案（这里简化处理）
                f.write(f"**答案**: [见测试输出]\n\n")
                f.write(f"**响应时间**: {result['time']:.2f}秒\n\n")
                f.write(f"**使用工具**: {', '.join(result['tools'])}\n\n")
                f.write(f"**检索上下文**: {result['contexts']}个\n\n")
                f.write(f"**答案质量**: {result['quality']}\n\n")
            else:
                f.write(f"**状态**: ❌ 失败\n\n")
                f.write(f"**错误**: {result.get('error')}\n\n")
            
            f.write("---\n\n")
    
    logger.info(f"详细结果已保存到: {output_file}")
    
    return results

if __name__ == "__main__":
    results = test_qa_demo()

