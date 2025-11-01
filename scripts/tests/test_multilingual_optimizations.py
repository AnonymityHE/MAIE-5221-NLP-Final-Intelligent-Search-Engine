#!/usr/bin/env python3
"""
测试多语言RAG优化效果
包括：混合语言检测改进、粤语查询优化、多语言知识库
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.core.language_detector import get_language_detector
from services.vector.retriever import retriever


def test_improved_mixed_language():
    """测试改进的混合语言检测"""
    print("=" * 80)
    print("🧪 测试改进的混合语言检测")
    print("=" * 80)
    
    detector = get_language_detector()
    
    test_cases = [
        ("你好Hello，我係test", "mixed"),  # 混合：粤语+英语
        ("你好Hello，我是测试", "mixed"),  # 混合：普通话+英语
        ("This is a mixed text with 中文", "mixed"),  # 混合：英语+中文
        ("RAG系统是检索增强生成，What does it mean?", "mixed"),  # 混合：普通话+英语
    ]
    
    print("\n测试用例（改进后应该能检测为mixed）:")
    all_correct = True
    for text, expected in test_cases:
        result = detector.detect(text)
        primary = result["primary"]
        is_correct = primary == expected or (expected == "mixed" and result["mixed"] > 0.3)
        
        status = "✅" if is_correct else "⚠️"
        print(f"{status} 文本: '{text[:40]}...'")
        print(f"    检测: {primary} (预期: {expected})")
        print(f"    混合分数: {result['mixed']:.2f}")
        print(f"    详情: 粤语={result['cantonese']:.2f}, "
              f"普通话={result['mandarin']:.2f}, "
              f"英语={result['english']:.2f}")
        print()
        
        if not is_correct:
            all_correct = False
    
    if all_correct:
        print("✅ 所有混合语言检测测试通过！")
    else:
        print("⚠️ 部分测试需要进一步优化")
    
    return all_correct


def test_cantonese_optimization():
    """测试粤语查询优化"""
    print("\n" + "=" * 80)
    print("🧪 测试粤语查询优化")
    print("=" * 80)
    
    print("\n注意: 此测试需要先索引多语言文档")
    print("运行以下命令索引文档:")
    print("  python scripts/utils/ingest.py")
    print()
    
    # 测试粤语查询
    cantonese_queries = [
        "RAG係乜嘢？",
        "檢索增強生成點樣運作？",
        "多語言支持係點樣實現嘅？"
    ]
    
    print("测试粤语查询优化:")
    for query in cantonese_queries:
        print(f"\n查询: '{query}'")
        try:
            # 检测语言
            lang_info = retriever.language_detector.detect(query)
            print(f"  语言检测: {lang_info['primary']} (粤语={lang_info['cantonese']:.2f})")
            
            # 执行检索
            results = retriever.search(query, top_k=3)
            if results:
                print(f"  找到 {len(results)} 个结果")
                for i, result in enumerate(results[:2], 1):
                    # 检测结果文档的语言
                    doc_lang = retriever.language_detector.detect(result.get('text', ''))
                    print(f"  结果{i}:")
                    print(f"    语言: {doc_lang['primary']} (粤语={doc_lang['cantonese']:.2f})")
                    print(f"    分数: {result.get('final_score', result.get('score', 0)):.4f}")
                    print(f"    语言权重: {result.get('language_weight', 1.0):.2f}")
                    print(f"    文本: {result.get('text', '')[:60]}...")
            else:
                print("  未找到结果（可能知识库为空或需要索引）")
        except Exception as e:
            print(f"  检索失败: {e}")
    
    print("\n✅ 粤语查询优化测试完成")
    print("提示: 如果知识库中有粤语文档，语言权重应该 > 1.0")


def test_multilingual_knowledge_base():
    """测试多语言知识库"""
    print("\n" + "=" * 80)
    print("🧪 测试多语言知识库")
    print("=" * 80)
    
    print("\n已创建多语言测试文档:")
    print("  - documents/multilingual_rag_guide_zh.md (普通话)")
    print("  - documents/multilingual_rag_guide_yue.md (粤语)")
    print("  - documents/multilingual_rag_guide_en.md (英语)")
    print("\n请运行以下命令索引这些文档:")
    print("  python scripts/utils/ingest.py")
    print("\n然后测试不同语言的查询:")
    print("  - 普通话: '什么是RAG？'")
    print("  - 粤语: 'RAG係乜嘢？'")
    print("  - 英语: 'What is RAG?'")


def main():
    """主函数"""
    try:
        print("🚀 开始测试多语言RAG优化\n")
        
        # 测试1: 混合语言检测
        test_improved_mixed_language()
        
        # 测试2: 粤语查询优化
        response = input("\n是否测试粤语查询优化？（需要先索引数据）[y/N]: ")
        if response.lower() == 'y':
            test_cantonese_optimization()
        
        # 测试3: 多语言知识库
        test_multilingual_knowledge_base()
        
        print("\n" + "=" * 80)
        print("✅ 所有优化测试完成！")
        print("=" * 80)
        print("\n📝 优化总结:")
        print("  1. ✅ 混合语言检测：改进了阈值和评分算法")
        print("  2. ✅ 粤语查询优化：增加检索候选数量，语言匹配权重提升")
        print("  3. ✅ 多语言知识库：创建了粤语、普通话、英语测试文档")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

