#!/usr/bin/env python3
"""
测试多语言RAG功能
测试粤语、普通话、英语的检索能力
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.vector.retriever import retriever
from services.core.language_detector import get_language_detector
from services.core.config import settings


def test_language_detection():
    """测试语言检测功能"""
    print("=" * 80)
    print("🧪 测试语言检测功能")
    print("=" * 80)
    
    detector = get_language_detector()
    
    test_cases = [
        ("你好，我是测试", "mandarin"),  # 普通话
        ("你好，我係測試", "cantonese"),  # 粤语
        ("Hello, this is a test", "english"),  # 英语
        ("你好Hello，我係test", "mixed"),  # 混合
        ("This is a mixed text with 中文 and English", "mixed"),  # 混合
    ]
    
    print("\n测试用例:")
    for text, expected in test_cases:
        result = detector.detect(text)
        primary = result["primary"]
        print(f"  文本: '{text[:30]}...'")
        print(f"  检测: {primary} (预期: {expected})")
        print(f"  详情: 粤语={result['cantonese']:.2f}, "
              f"普通话={result['mandarin']:.2f}, "
              f"英语={result['english']:.2f}")
        print()
    
    return True


def test_multilingual_embedding():
    """测试多语言embedding"""
    print("=" * 80)
    print("🧪 测试多语言Embedding功能")
    print("=" * 80)
    
    print(f"\n当前配置:")
    print(f"  使用多语言模型: {settings.USE_MULTILINGUAL_EMBEDDING}")
    if settings.USE_MULTILINGUAL_EMBEDDING:
        print(f"  多语言模型: {settings.MULTILINGUAL_EMBEDDING_MODEL}")
    else:
        print(f"  单语言模型: {settings.EMBEDDING_MODEL}")
    
    # 测试不同语言的embedding
    test_queries = [
        "什么是RAG系统？",  # 普通话
        "RAG系统係乜嘢？",  # 粤语
        "What is RAG system?",  # 英语
        "RAG系统是检索增强生成",  # 普通话
        "RAG系统係檢索增強生成",  # 粤语
    ]
    
    print("\n生成embedding向量:")
    for query in test_queries:
        lang_info = retriever.language_detector.detect(query)
        vector = retriever.embedding_model.encode([query], show_progress_bar=False)[0]
        print(f"  查询: '{query[:40]}...'")
        print(f"  语言: {lang_info['primary']}")
        print(f"  向量维度: {len(vector)}")
        print(f"  向量前5个值: {vector[:5]}")
        print()
    
    return True


def test_multilingual_retrieval():
    """测试多语言检索（需要先有索引的数据）"""
    print("=" * 80)
    print("🧪 测试多语言检索功能")
    print("=" * 80)
    
    print("\n注意: 此测试需要先有数据索引到Milvus")
    print("可以使用以下命令索引文档:")
    print("  python scripts/utils/ingest.py")
    print()
    
    # 测试查询（不同语言）
    test_queries = [
        "什么是RAG？",  # 普通话
        "RAG係乜嘢？",  # 粤语（如果知识库有粤语内容）
        "What is RAG?",  # 英语
    ]
    
    for query in test_queries:
        print(f"查询: '{query}'")
        try:
            results = retriever.search(query, top_k=3)
            if results:
                print(f"  找到 {len(results)} 个结果")
                for i, result in enumerate(results[:2], 1):
                    print(f"  结果{i}: {result.get('text', '')[:60]}...")
                    print(f"    来源: {result.get('source_file', 'N/A')}")
                    print(f"    分数: {result.get('score', 0):.4f}")
            else:
                print("  未找到结果（可能知识库为空）")
        except Exception as e:
            print(f"  检索失败: {e}")
        print()
    
    return True


def main():
    """主函数"""
    try:
        print("🚀 开始测试多语言RAG功能\n")
        
        # 测试语言检测
        test_language_detection()
        
        # 测试多语言embedding
        test_multilingual_embedding()
        
        # 测试多语言检索（可选，需要数据）
        print("\n" + "=" * 80)
        response = input("是否测试多语言检索？（需要先索引数据）[y/N]: ")
        if response.lower() == 'y':
            test_multilingual_retrieval()
        else:
            print("跳过多语言检索测试")
        
        print("\n" + "=" * 80)
        print("✅ 多语言RAG功能测试完成！")
        print("=" * 80)
        print("\n💡 提示:")
        print("  1. 确保启用多语言模型: USE_MULTILINGUAL_EMBEDDING=true")
        print("  2. 多语言模型支持粤语、普通话、英语混合检索")
        print("  3. 可以在知识库中混合使用不同语言的文档")
        print("  4. 系统会自动检测查询语言并优化检索")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    main()

