"""展示Q&A完整答案"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from services.agent.agent import agent

questions = [
    ('如何使用粤语进行语音输入？', 'zh'),
    ('系统采用了什么样的工作流架构？LLM在其中起什么作用？', 'zh'),
    ('What tools are available in this system and what can they do?', 'en'),
    ('What is reranking and why is it important in RAG systems?', 'en'),
    ('这个系统支持哪些语言？分别在哪些方面支持？', 'zh'),
]

for i, (q, lang) in enumerate(questions, 1):
    sep = '='*120
    print(f'\n{sep}')
    print(f'问题 {i}: {q}')
    print(sep)
    
    result = agent.execute(q)
    
    print(f'\n【答案】')
    print(result['answer'])
    
    print(f'\n【元信息】')
    print(f'- 使用工具: {", ".join(result["tools_used"])}')
    print(f'- 使用知识库: {"是" if result.get("has_context") else "否"}')
    print(f'- 检索上下文数: {result.get("contexts_count", 0)}')
    
    if result.get('workflow_engine'):
        print(f'- 工作流引擎: {result["workflow_engine"]}')
        print(f'- 工作流类型: {result.get("workflow_type", "N/A")}')
    
    if result.get('tokens'):
        tokens = result['tokens']
        print(f'- Token使用: 输入={tokens.get("input", 0)}, 输出={tokens.get("output", 0)}, 总计={tokens.get("total", 0)}')
    
    print(sep)

print('\n✅ 演示完成！')

