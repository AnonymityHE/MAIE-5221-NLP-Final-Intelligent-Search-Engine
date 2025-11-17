"""
快速构建RAG知识库
自动索引项目文档、README、配置文件等
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from services.storage.file_indexer import FileIndexer
from services.storage.file_storage import file_storage
from services.vector.milvus_client import milvus_client
from services.core.logger import logger
import json

# 定义要索引的文档路径
KNOWLEDGE_SOURCES = {
    "项目文档": [
        "docs/PROJECT_INFO.md",
        "docs/TROUBLESHOOTING.md",
        "docs/WORKFLOW_ARCHITECTURE.md",
        "docs/RAG_RESEARCH_FINDINGS.md",
        "docs/RAG_IMPROVEMENT_PLAN.md",
    ],
    "根目录文档": [
        "README.md",
    ],
    "配置文档": [
        "services/config.example.py",
        "services/core/config.example.py",
    ],
}

# FAQ数据（内置）
FAQ_DATA = [
    {
        "question": "如何使用粤语语音输入？",
        "answer": """系统支持粤语STT（语音转文字），通过以下方式：
1. Whisper模型：支持多语言识别，包括粤语
2. 专用粤语Speech API：提供更高准确度的粤语识别
3. 自动语言检测：系统会自动识别输入语言并选择最佳识别引擎
4. 降级机制：如果专用API失败，会自动回退到Whisper

使用方法：直接对着麦克风说粤语，系统会自动处理。""",
        "language": "zh",
        "category": "语音输入",
        "tags": ["speech", "cantonese", "stt", "粤语"]
    },
    {
        "question": "系统支持哪些语言？",
        "answer": """系统支持多语言，包括：
- 粤语 (Cantonese)
- 普通话 (Mandarin Chinese)
- 英语 (English)

多语言支持体现在：
1. 语音输入：STT支持三语
2. 文本查询：embedding模型支持多语言
3. 语音输出：TTS支持多语言
4. 知识库：可索引和检索多语言文档""",
        "language": "zh",
        "category": "系统功能",
        "tags": ["multilingual", "languages", "多语言"]
    },
    {
        "question": "How to query stock prices?",
        "answer": """To query stock prices, you can use natural language queries like:
- "What is the current price of Apple stock?"
- "Show me NVIDIA stock price"
- "Compare Tesla and BYD stock prices"

The system uses:
1. Finance tool with real-time data APIs
2. Intelligent entity extraction (company names → ticker symbols)
3. Multi-source data aggregation (Yahoo Finance, CoinGecko for crypto)

The finance tool supports both US stocks (AAPL, MSFT, etc.) and Hong Kong/China stocks (0700.HK for Tencent, BABA for Alibaba).""",
        "language": "en",
        "category": "Tools",
        "tags": ["finance", "stocks", "query"]
    },
    {
        "question": "系统的工作流是什么？",
        "answer": """系统采用智能工作流架构：

**LLM驱动的工作流（主要）**：
1. LLM分析用户查询
2. 生成多步骤执行计划（JSON格式）
3. 动态执行引擎按步骤调用工具
4. 综合结果生成最终答案

**规则驱动的工作流（备选）**：
1. 基于关键词检测查询类型
2. 应用预定义工作流模板
3. 按固定步骤执行

**单工具调用（简单查询）**：
- 直接调用最相关的单个工具

优先级：LLM工作流 > 规则工作流 > 单工具

支持的工具：
- local_rag: 本地知识库检索
- web_search: 网页搜索
- finance: 金融数据查询
- weather: 天气查询
- transport: 交通信息查询""",
        "language": "zh",
        "category": "架构",
        "tags": ["workflow", "architecture", "工作流"]
    },
    {
        "question": "What is the difference between HKGAI and Gemini APIs?",
        "answer": """The system supports multiple LLM providers:

**HKGAI API (Primary)**:
- Default provider for LLM requests
- Stable and reliable
- Used for workflow planning and answer generation

**Gemini API (Fallback)**:
- Backup provider
- Activated when HKGAI fails or exceeds quota
- Supports multiple models (gemini-2.0-flash-exp, gemini-1.5-pro)
- Includes usage monitoring

**Intelligent Fallback**:
- System tracks HKGAI failure count
- Automatically switches to Gemini after 3 consecutive failures
- Resets counter when HKGAI recovers
- Ensures high availability

You can explicitly choose a provider:
```python
result = unified_llm_client.chat(
    system_prompt="...",
    user_prompt="...",
    provider="gemini"  # or "hkgai"
)
```""",
        "language": "en",
        "category": "LLM",
        "tags": ["llm", "api", "hkgai", "gemini", "fallback"]
    },
    {
        "question": "如何添加新文档到知识库？",
        "answer": """有多种方式添加文档到知识库：

**方法1：使用文件上传API**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/document.pdf"
```

**方法2：使用命令行脚本**
```bash
python scripts/index_documents.py --file document.pdf
python scripts/index_documents.py --dir documents/ --recursive
```

**方法3：通过存储目录**
将文件放入 `storage/uploads/` 目录，系统会自动索引

**支持的文件格式**：
- PDF (.pdf)
- Word文档 (.docx)
- Markdown (.md)
- 文本文件 (.txt)
- 代码文件 (.py, .js, .java等)
- JSON (.json)
- CSV (.csv)

**处理流程**：
1. 文件解析和文本提取
2. 智能分块（chunking）
3. 生成embedding向量
4. 存储到Milvus向量数据库
5. 创建元数据索引""",
        "language": "zh",
        "category": "知识库管理",
        "tags": ["knowledge_base", "indexing", "documents", "上传"]
    },
    {
        "question": "What is reranking and why is it important?",
        "answer": """Reranking is a crucial component in RAG systems:

**What is Reranking?**
After initial retrieval (e.g., vector similarity search), reranking re-orders the results using a more sophisticated model to improve relevance.

**Why Important?**
1. **Better Relevance**: Initial retrieval may miss nuances; reranker captures deeper semantic relationships
2. **Reduced Noise**: Filters out less relevant results even if they have high vector similarity
3. **Context Aware**: Considers query-document interaction, not just isolated embeddings

**Our Implementation**:
- Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- Features:
  * Semantic similarity scoring
  * Credibility weighting
  * Freshness factor (newer docs ranked higher)
  * Configurable weights for each factor

**Two-Stage Process**:
1. Stage 1: Fast vector retrieval (get top 50)
2. Stage 2: Reranking with cross-encoder (refine to top 10)

This balances speed and accuracy.""",
        "language": "en",
        "category": "RAG Techniques",
        "tags": ["reranking", "retrieval", "rag", "accuracy"]
    },
]

def create_faq_documents():
    """将FAQ数据转换为可索引的文档"""
    faq_docs = []
    for i, faq in enumerate(FAQ_DATA):
        doc_content = f"""# FAQ: {faq['question']}

**问题**: {faq['question']}

**答案**: 
{faq['answer']}

**分类**: {faq['category']}
**语言**: {faq['language']}
**标签**: {', '.join(faq['tags'])}
"""
        faq_docs.append({
            "content": doc_content,
            "metadata": {
                "doc_id": f"faq_{i+1}",
                "doc_title": faq['question'],
                "doc_type": "faq",
                "language": faq['language'],
                "category": faq['category'],
                "tags": faq['tags'],
                "source": "builtin_faq",
            }
        })
    return faq_docs

def build_knowledge_base():
    """构建完整的知识库"""
    logger.info("\n" + "="*100)
    logger.info("🏗️  开始构建RAG知识库".center(100))
    logger.info("="*100 + "\n")
    
    total_indexed = 0
    total_failed = 0
    
    # 初始化索引器
    file_indexer = FileIndexer()
    
    # 1. 索引项目文档
    logger.info("📚 第1步：索引项目文档")
    logger.info("-" * 100)
    
    for category, file_list in KNOWLEDGE_SOURCES.items():
        logger.info(f"\n🔖 分类: {category}")
        for file_path in file_list:
            full_path = Path(file_path)
            if not full_path.exists():
                logger.warning(f"⚠️  文件不存在，跳过: {file_path}")
                total_failed += 1
                continue
            
            try:
                logger.info(f"   📄 正在索引: {file_path}")
                
                # 上传文件到file_storage
                with open(full_path, 'rb') as f:
                    file_content = f.read()
                
                # 保存文件
                result_info = file_storage.save_file(
                    file_content=file_content,
                    filename=full_path.name,
                    mime_type='text/plain'  # 简化，实际可根据扩展名判断
                )
                file_id = result_info['file_id']
                
                # 调用文件索引器
                result = file_indexer.index_file(file_id)
                if result.get('success'):
                    chunks_indexed = result.get('chunks_indexed', 0)
                    total_indexed += chunks_indexed
                    logger.info(f"   ✅ 成功索引 {chunks_indexed} 个块")
                else:
                    logger.error(f"   ❌ 索引失败: {result.get('message')}")
                    total_failed += 1
            except Exception as e:
                logger.error(f"   ❌ 索引异常: {e}")
                import traceback
                traceback.print_exc()
                total_failed += 1
    
    # 2. 索引FAQ数据
    logger.info("\n" + "-" * 100)
    logger.info("💬 第2步：索引FAQ数据")
    logger.info("-" * 100)
    
    faq_docs = create_faq_documents()
    logger.info(f"   准备索引 {len(faq_docs)} 个FAQ条目")
    
    for i, faq_doc in enumerate(faq_docs):
        try:
            # 将FAQ内容写入临时文件再索引
            temp_faq_path = Path(f"data/temp_faq_{i}.md")
            temp_faq_path.parent.mkdir(exist_ok=True)
            
            with open(temp_faq_path, 'w', encoding='utf-8') as f:
                f.write(faq_doc['content'])
            
            # 保存文件
            result_info = file_storage.save_file(
                file_content=faq_doc['content'].encode('utf-8'),
                filename=f"faq_{i+1}_{faq_doc['metadata']['language']}.md",
                mime_type='text/markdown'
            )
            file_id = result_info['file_id']
            
            # 索引
            result = file_indexer.index_file(file_id)
            if result.get('success'):
                chunks_indexed = result.get('chunks_indexed', 0)
                total_indexed += chunks_indexed
                logger.info(f"   ✅ FAQ索引成功: {faq_doc['metadata']['doc_title'][:50]}...")
            else:
                logger.error(f"   ❌ FAQ索引失败: {result.get('message')}")
                total_failed += 1
            
            # 清理临时文件
            if temp_faq_path.exists():
                temp_faq_path.unlink()
                
        except Exception as e:
            logger.error(f"   ❌ FAQ索引异常: {e}")
            import traceback
            traceback.print_exc()
            total_failed += 1
    
    # 3. 获取最终统计
    logger.info("\n" + "="*100)
    logger.info("📊 知识库构建完成".center(100))
    logger.info("="*100)
    
    try:
        stats = milvus_client.get_collection_stats()
        logger.info(f"\n知识库统计:")
        logger.info(f"  - 总文档数: {stats.get('total_docs', 0)}")
        logger.info(f"  - 总块数: {stats.get('total_chunks', 0)}")
        logger.info(f"  - 本次索引成功: {total_indexed} 个块")
        logger.info(f"  - 索引失败: {total_failed} 项")
        
        doc_types = stats.get('doc_types', {})
        if doc_types:
            logger.info(f"\n文档类型分布:")
            for doc_type, count in doc_types.items():
                logger.info(f"  - {doc_type}: {count}")
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
    
    logger.info("\n" + "="*100)
    logger.info("✅ 知识库构建流程完成！")
    logger.info("="*100 + "\n")
    
    # 测试检索
    logger.info("🧪 执行测试检索...")
    logger.info("-" * 100)
    
    test_queries = [
        "如何使用粤语输入？",
        "What tools are available?",
        "系统架构是什么？"
    ]
    
    for query in test_queries:
        logger.info(f"\n🔍 测试查询: {query}")
        try:
            from services.vector.retriever import retriever
            results = retriever.search(query, top_k=3)
            logger.info(f"   ✅ 找到 {len(results)} 个结果")
            for i, result in enumerate(results[:2], 1):
                logger.info(f"   {i}. [{result.get('score', 0):.3f}] {result.get('content', '')[:80]}...")
        except Exception as e:
            logger.error(f"   ❌ 检索失败: {e}")
    
    logger.info("\n" + "="*100)
    logger.info("🎉 全部完成！知识库已就绪，可以开始使用了。")
    logger.info("="*100 + "\n")

if __name__ == "__main__":
    build_knowledge_base()

