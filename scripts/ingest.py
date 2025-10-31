"""
数据注入脚本 - 将文档加载、切分、向量化并存入Milvus
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from services.milvus_client import milvus_client
from services.config import settings


def load_pdf(file_path: str) -> str:
    """加载PDF文件并提取文本"""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"加载PDF失败 {file_path}: {e}")
        return ""


def process_documents(documents_dir: str = "documents"):
    """
    处理文档目录中的所有文档
    
    Args:
        documents_dir: 文档目录路径
    """
    # 1. 连接Milvus并创建集合
    print("正在连接Milvus...")
    if not milvus_client.connect():
        print("错误: 无法连接到Milvus，请确保Milvus服务正在运行")
        return
    
    print("正在创建集合...")
    milvus_client.create_collection_if_not_exists(
        dimension=settings.EMBEDDING_DIMENSION
    )
    
    # 2. 加载embedding模型
    print(f"正在加载embedding模型: {settings.EMBEDDING_MODEL}")
    embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    print("Embedding模型加载完成")
    
    # 3. 初始化文本分割器
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
    )
    
    # 4. 处理文档
    docs_path = Path(documents_dir)
    if not docs_path.exists():
        print(f"警告: 文档目录 {documents_dir} 不存在，正在创建...")
        docs_path.mkdir(parents=True, exist_ok=True)
        print(f"请将PDF文档放入 {docs_path.absolute()} 目录后重新运行脚本")
        return
    
    all_texts = []
    all_vectors = []
    all_source_files = []
    
    # 遍历文档目录
    pdf_files = list(docs_path.glob("*.pdf"))
    if not pdf_files:
        print(f"未找到PDF文件，请将PDF文档放入 {docs_path.absolute()} 目录")
        return
    
    print(f"找到 {len(pdf_files)} 个PDF文件")
    
    for pdf_file in pdf_files:
        print(f"正在处理: {pdf_file.name}")
        text = load_pdf(str(pdf_file))
        
        if not text.strip():
            print(f"  警告: {pdf_file.name} 没有提取到文本，跳过")
            continue
        
        # 切分文本
        chunks = text_splitter.split_text(text)
        print(f"  切分为 {len(chunks)} 个块")
        
        # 向量化
        vectors = embedding_model.encode(chunks).tolist()
        
        # 准备数据
        texts = chunks
        source_files = [pdf_file.name] * len(chunks)
        
        all_texts.extend(texts)
        all_vectors.extend(vectors)
        all_source_files.extend(source_files)
        
        print(f"  {pdf_file.name} 处理完成")
    
    # 5. 批量插入Milvus
    if all_texts:
        print(f"\n正在插入 {len(all_texts)} 条数据到Milvus...")
        if milvus_client.insert(all_texts, all_vectors, all_source_files):
            print("数据注入成功！")
            
            # 显示统计信息
            stats = milvus_client.get_collection_stats()
            if stats:
                print(f"集合统计: {stats['num_entities']} 条数据")
        else:
            print("数据注入失败")
    else:
        print("没有数据需要插入")


if __name__ == "__main__":
    # 可以从命令行参数获取文档目录
    documents_dir = sys.argv[1] if len(sys.argv) > 1 else "documents"
    process_documents(documents_dir)
