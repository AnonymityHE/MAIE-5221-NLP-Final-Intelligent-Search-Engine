"""
创建简单的测试文档（用于快速测试系统）
"""
from pathlib import Path
import fitz  # PyMuPDF

def create_test_pdf(output_path: str = "documents/test_document.pdf"):
    """创建一个简单的测试PDF文档"""
    doc = fitz.open()  # 创建新PDF
    page = doc.new_page()
    
    # 添加测试内容
    test_content = """
RAG系统测试文档

什么是RAG？
RAG是检索增强生成（Retrieval-Augmented Generation）的缩写。它是一种结合了信息检索和文本生成的技术。

RAG的工作原理：
1. 首先，将文档库中的内容转换为向量并存储在向量数据库中
2. 当用户提问时，系统将问题向量化
3. 在向量数据库中搜索最相关的文档片段
4. 将检索到的文档片段作为上下文，结合LLM生成答案

RAG的优势：
- 可以提供基于实际文档的准确回答
- 减少LLM的幻觉问题
- 可以处理大型文档库
- 支持实时更新知识库

Milvus是什么？
Milvus是一个开源的向量数据库，专门用于存储和检索大规模向量数据。它支持高效的相似度搜索，非常适合RAG系统使用。

技术栈：
- 后端框架：FastAPI
- 向量数据库：Milvus
- Embedding模型：sentence-transformers
- LLM API：HKGAI-V1
"""
    
    # 插入文本
    page.insert_text(
        (50, 50),  # 位置
        test_content,
        fontsize=12,
        fontname="helv"
    )
    
    # 保存PDF
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    doc.close()
    print(f"测试文档已创建: {output_path}")
    print(f"文档内容长度: {len(test_content)} 字符")


if __name__ == "__main__":
    create_test_pdf()

