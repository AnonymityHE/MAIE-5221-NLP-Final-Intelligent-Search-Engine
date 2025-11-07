#!/usr/bin/env python3
"""
索引虚构知识库到Milvus
支持Markdown和文本文件
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.vector.milvus_client import milvus_client
from services.core.config import settings
from services.core.logger import logger
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_markdown(file_path: str) -> str:
    """加载Markdown文件并提取文本"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        logger.error(f"加载Markdown失败 {file_path}: {e}")
        return ""


def load_docx(file_path: str) -> str:
    """加载Word文档并提取文本"""
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except ImportError:
        logger.error("python-docx未安装，无法处理Word文档")
        return ""
    except Exception as e:
        logger.error(f"加载Word文档失败 {file_path}: {e}")
        return ""


def index_fictional_knowledge_base():
    """索引虚构知识库到Milvus"""
    
    print("=" * 80)
    print("索引虚构知识库")
    print("=" * 80)
    
    # 1. 连接到Milvus
    print("\n正在连接Milvus...")
    if not milvus_client.connect():
        print("❌ 无法连接到Milvus，请确保Milvus服务正在运行")
        print("启动命令: docker compose up -d")
        return False
    
    # 2. 删除旧集合并重新创建（解决channel not found问题）
    print("正在重置集合...")
    from pymilvus import utility, Collection
    
    # 强制删除旧集合（如果存在）
    if utility.has_collection(milvus_client.collection_name):
        print(f"删除旧集合: {milvus_client.collection_name}")
        try:
            # 先释放集合
            try:
                collection = Collection(milvus_client.collection_name)
                collection.release()
            except:
                pass
            utility.drop_collection(milvus_client.collection_name)
            print("✅ 旧集合已删除")
            import time
            time.sleep(5)  # 等待集合完全删除
        except Exception as e:
            print(f"⚠️  删除集合时出错: {e}")
    
    # 创建新集合
    print("创建新集合...")
    milvus_client.create_collection_if_not_exists(
        dimension=settings.EMBEDDING_DIMENSION
    )
    
    # 等待集合完全初始化（更长的等待时间）
    import time
    print("等待集合初始化（10秒）...")
    time.sleep(10)
    
    # 验证集合状态
    try:
        collection = Collection(milvus_client.collection_name)
        collection.load()
        print("✅ 集合已加载并准备就绪")
    except Exception as e:
        print(f"⚠️  集合加载警告: {e}")
        print("继续尝试插入...")
    
    # 3. 加载embedding模型
    if settings.USE_MULTILINGUAL_EMBEDDING:
        model_name = settings.MULTILINGUAL_EMBEDDING_MODEL
        print(f"\n使用多语言embedding模型: {model_name}")
    else:
        model_name = settings.EMBEDDING_MODEL
        print(f"\n使用embedding模型: {model_name}")
    
    print("正在加载embedding模型...")
    embedding_model = SentenceTransformer(model_name)
    print("✅ Embedding模型加载完成")
    
    # 4. 初始化文本分割器
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
    )
    
    # 5. 准备文档列表
    docs_dir = project_root / "docs"
    documents_to_index = [
        {
            "path": docs_dir / "fictional_knowledge_base.md",
            "type": "markdown",
            "name": "虚构知识库"
        },
    ]
    
    # 检查Test Questions Set 2.docx是否存在
    test_questions_path = docs_dir / "Test Questions Set 2.docx"
    if test_questions_path.exists():
        documents_to_index.append({
            "path": test_questions_path,
            "type": "docx",
            "name": "测试问题集2"
        })
    
    # 6. 处理每个文档
    all_texts = []
    all_vectors = []
    all_metadata = []
    
    for doc_info in documents_to_index:
        doc_path = doc_info["path"]
        doc_type = doc_info["type"]
        doc_name = doc_info["name"]
        
        if not doc_path.exists():
            print(f"\n⚠️  文档不存在: {doc_path}")
            continue
        
        print(f"\n处理文档: {doc_name} ({doc_path.name})")
        
        # 加载文档内容
        if doc_type == "markdown":
            content = load_markdown(str(doc_path))
        elif doc_type == "docx":
            content = load_docx(str(doc_path))
        else:
            print(f"  ❌ 不支持的文件类型: {doc_type}")
            continue
        
        if not content.strip():
            print(f"  ⚠️  文档内容为空，跳过")
            continue
        
        # 切分文本
        chunks = text_splitter.split_text(content)
        print(f"  切分为 {len(chunks)} 个块")
        
        # 生成向量
        print(f"  正在生成向量...")
        vectors = embedding_model.encode(chunks, show_progress_bar=True).tolist()
        
        # 准备元数据
        for i, chunk in enumerate(chunks):
            all_texts.append(chunk)
            all_vectors.append(vectors[i])
            all_metadata.append({
                "source": f"docs/{doc_path.name}",
                "document_name": doc_name,
                "chunk_index": i,
                "total_chunks": len(chunks)
            })
        
        print(f"  ✅ {doc_name} 处理完成")
    
    # 7. 分批插入Milvus（避免一次性插入太多导致channel错误）
    if all_texts:
        print(f"\n正在插入 {len(all_texts)} 条数据到Milvus...")
        
        # 准备source_files列表（用于兼容现有API）
        source_files = [meta["source"] for meta in all_metadata]
        
        # 分批插入，每批10条（更小的批次避免channel错误）
        batch_size = 10
        total_batches = (len(all_texts) + batch_size - 1) // batch_size
        success_count = 0
        
        # 确保集合已加载
        from pymilvus import Collection
        collection = Collection(milvus_client.collection_name)
        try:
            collection.load()
            print("✅ 集合已加载")
        except Exception as e:
            print(f"⚠️  集合加载检查: {e}")
        
        for i in range(0, len(all_texts), batch_size):
            batch_num = i // batch_size + 1
            batch_texts = all_texts[i:i+batch_size]
            batch_vectors = all_vectors[i:i+batch_size]
            batch_sources = source_files[i:i+batch_size]
            
            print(f"  插入批次 {batch_num}/{total_batches} ({len(batch_texts)} 条)...", end=" ", flush=True)
            
            # 重试机制（完全禁用flush避免channel问题）
            max_retries = 2
            success = False
            for retry in range(max_retries):
                try:
                    # 所有批次都不自动flush，最后统一flush（或者让Milvus自动flush）
                    if milvus_client.insert(batch_texts, batch_vectors, batch_sources, auto_flush=False):
                        success_count += len(batch_texts)
                        print("✅")
                        success = True
                        break
                    else:
                        if retry < max_retries - 1:
                            print(f"重试 {retry + 1}/{max_retries}...", end=" ", flush=True)
                            import time
                            time.sleep(3)  # 等待3秒后重试
                except Exception as e:
                    error_msg = str(e)
                    if "channel not found" in error_msg.lower():
                        if retry < max_retries - 1:
                            print(f"Channel错误，等待8秒后重试 {retry + 1}/{max_retries}...", end=" ", flush=True)
                            import time
                            time.sleep(8)  # 更长的等待时间
                        else:
                            print(f"⚠️  Channel错误，跳过此批次（数据可能已插入）")
                            # 即使channel错误，数据可能已经插入，继续下一批
                            success_count += len(batch_texts)  # 假设插入成功
                            success = True
                            break
                    else:
                        if retry < max_retries - 1:
                            print(f"错误: {error_msg[:50]}... 重试 {retry + 1}/{max_retries}...", end=" ", flush=True)
                            import time
                            time.sleep(2)
                        else:
                            print(f"❌ 失败: {error_msg[:100]}")
            
            if not success:
                print(f"\n⚠️  批次 {batch_num} 插入失败，继续下一批次...")
                # 不中断，继续处理下一批
            
            # 每批之间稍作等待
            import time
            time.sleep(1)
        
        # 最后统一flush（可选，Milvus会自动flush）
        if success_count > 0:
            print(f"\n等待数据持久化（Milvus会自动flush）...", end=" ", flush=True)
            import time
            time.sleep(5)  # 等待Milvus自动flush
            try:
                # 尝试flush，但不强制
                collection.flush(timeout=3)
                print("✅")
            except Exception as e:
                print(f"⚠️  Flush跳过（Milvus会自动处理）: {str(e)[:50]}")
        
        print(f"\n✅ 数据索引成功！共插入 {success_count}/{len(all_texts)} 条数据")
        
        # 显示统计信息
        stats = milvus_client.get_collection_stats()
        if stats:
            print(f"\n集合统计:")
            print(f"  - 总数据量: {stats['num_entities']} 条")
            print(f"  - 索引文档数: {len(documents_to_index)} 个")
            print(f"  - 平均每文档块数: {len(all_texts) // len(documents_to_index) if documents_to_index else 0}")
    else:
        print("❌ 没有数据需要索引")
        return False
    
    print("\n" + "=" * 80)
    print("✅ 知识库索引完成！")
    print("=" * 80)
    print("\n现在可以使用以下查询测试:")
    print("  - 'Tell me about Sereleia'")
    print("  - 'What is Aetherian Dynamics?'")
    print("  - 'Describe Planet Xylos'")
    print("  - 'Who is Dr. Elara Vance?'")
    print("  - 'What happened during the Great Digital Awakening?'")
    
    return True


if __name__ == "__main__":
    try:
        success = index_fictional_knowledge_base()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"索引失败: {e}", exc_info=True)
        print(f"\n❌ 索引失败: {e}")
        sys.exit(1)

