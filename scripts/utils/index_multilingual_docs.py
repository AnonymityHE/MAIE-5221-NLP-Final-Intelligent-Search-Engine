#!/usr/bin/env python3
"""
快速索引多语言文档到知识库
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pathlib import Path
from services.vector.milvus_client import milvus_client
from services.core.config import settings
from services.core.logger import logger
from sentence_transformers import SentenceTransformer


def index_multilingual_documents():
    """索引多语言文档"""
    # 文档路径
    documents_dir = Path(__file__).parent.parent.parent / "documents"
    multilingual_docs = [
        "multilingual_rag_guide_zh.md",  # 普通话
        "multilingual_rag_guide_yue.md",  # 粤语
        "multilingual_rag_guide_en.md",  # 英语
    ]
    
    print("=" * 80)
    print("索引多语言文档到知识库")
    print("=" * 80)
    
    # 加载embedding模型
    if settings.USE_MULTILINGUAL_EMBEDDING:
        model_name = settings.MULTILINGUAL_EMBEDDING_MODEL
        print(f"\n使用多语言embedding模型: {model_name}")
    else:
        model_name = settings.EMBEDDING_MODEL
        print(f"\n使用embedding模型: {model_name}")
    
    embedding_model = SentenceTransformer(model_name)
    
    # 连接到Milvus
    if not milvus_client.connect():
        print("❌ 无法连接到Milvus，请确保Milvus服务正在运行")
        print("启动命令: docker-compose up -d")
        return False
    
    # 创建集合（如果不存在）
    milvus_client.create_collection_if_not_exists(dimension=settings.EMBEDDING_DIMENSION)
    
    # 索引每个文档
    total_indexed = 0
    for doc_name in multilingual_docs:
        doc_path = documents_dir / doc_name
        if not doc_path.exists():
            print(f"⚠️  文档不存在: {doc_path}")
            continue
        
        print(f"\n处理文档: {doc_name}")
        
        # 读取文档内容
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ 读取文档失败: {e}")
            continue
        
        # 分块处理（简单分块，每500字符一块）
        chunk_size = settings.CHUNK_SIZE
        chunks = []
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        
        print(f"  分成 {len(chunks)} 个块")
        
        # 生成向量
        texts = []
        vectors = []
        source_files = []
        
        for chunk in chunks:
            texts.append(chunk)
            vector = embedding_model.encode([chunk], show_progress_bar=False)[0].tolist()
            vectors.append(vector)
            source_files.append(f"documents/{doc_name}")
        
        # 插入到Milvus
        try:
            success = milvus_client.insert(texts, vectors, source_files)
            if success:
                total_indexed += len(chunks)
                print(f"  ✅ 成功索引 {len(chunks)} 个块")
            else:
                print(f"  ❌ 索引失败")
        except Exception as e:
            print(f"  ❌ 插入失败: {e}")
    
    print("\n" + "=" * 80)
    print(f"✅ 索引完成！共索引 {total_indexed} 个文档块")
    print("=" * 80)
    print("\n现在可以使用以下查询测试:")
    print("  - 普通话: '什么是RAG？'")
    print("  - 粤语: 'RAG係乜嘢？'")
    print("  - 英语: 'What is RAG?'")
    
    return True


if __name__ == "__main__":
    try:
        index_multilingual_documents()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

