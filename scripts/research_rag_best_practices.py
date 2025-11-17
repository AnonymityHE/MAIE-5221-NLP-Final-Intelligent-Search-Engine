"""
使用Agent搜索RAG最佳实践并分析当前知识库
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from services.agent.agent import agent
from services.core.logger import logger
import json

# RAG相关研究问题
RESEARCH_QUERIES = [
    "What are the best practices for building a production RAG retrieval augmented generation system in 2024?",
    "How to optimize RAG chunking strategies and document processing for better retrieval?",
    "What are advanced RAG techniques like reranking, hybrid search, and query expansion?",
    "How to build multilingual RAG systems that support Chinese, Cantonese and English?",
]

def research_rag_best_practices():
    """研究RAG最佳实践"""
    logger.info("\n" + "="*120)
    logger.info("🔬 RAG最佳实践研究".center(120))
    logger.info("="*120 + "\n")
    
    findings = []
    
    for i, query in enumerate(RESEARCH_QUERIES, 1):
        logger.info(f"\n{'='*120}")
        logger.info(f"📝 研究问题 {i}/{len(RESEARCH_QUERIES)}")
        logger.info(f"{'='*120}")
        logger.info(f"🔍 查询: {query}\n")
        
        try:
            # 使用agent执行查询
            result = agent.execute(query)
            
            answer = result.get('answer', '')
            tools_used = result.get('tools_used', [])
            
            print(f"\n{'='*120}")
            print(f"📊 问题 {i}: {query[:80]}...")
            print(f"{'='*120}")
            print(f"\n🛠️  使用工具: {', '.join(tools_used)}")
            print(f"\n💡 答案:\n")
            
            # 分段打印答案以便阅读
            lines = answer.split('\n')
            for line in lines:
                if line.strip():
                    print(f"   {line}")
            
            print(f"\n{'='*120}\n")
            
            findings.append({
                'query': query,
                'answer': answer,
                'tools': tools_used,
                'length': len(answer)
            })
            
        except Exception as e:
            logger.error(f"查询失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 保存研究结果
    output_file = 'docs/RAG_RESEARCH_FINDINGS.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# RAG系统最佳实践研究报告\n\n")
        f.write(f"研究日期: 2025-11-17\n\n")
        f.write("---\n\n")
        
        for i, finding in enumerate(findings, 1):
            f.write(f"## 研究问题 {i}\n\n")
            f.write(f"**查询**: {finding['query']}\n\n")
            f.write(f"**使用工具**: {', '.join(finding['tools'])}\n\n")
            f.write(f"**研究发现**:\n\n")
            f.write(finding['answer'])
            f.write("\n\n---\n\n")
    
    logger.info(f"\n✅ 研究报告已保存到: {output_file}")
    
    # 分析总结
    print("\n" + "="*120)
    print("📊 研究总结")
    print("="*120)
    print(f"总研究问题: {len(RESEARCH_QUERIES)}")
    print(f"成功获取答案: {len([f for f in findings if f['length'] > 0])}")
    print(f"平均答案长度: {sum(f['length'] for f in findings) / len(findings):.0f} 字符")
    print(f"\n报告位置: {output_file}")
    print("="*120 + "\n")
    
    return findings

if __name__ == "__main__":
    findings = research_rag_best_practices()

