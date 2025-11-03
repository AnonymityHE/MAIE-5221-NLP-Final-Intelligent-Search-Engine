#!/usr/bin/env python3
"""
测试Jarvis语音助手功能
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.speech.wake_word_detector import get_jarvis_detector
from services.speech.voice_service import get_voice_service
from services.core.config import settings


def test_wake_word_detection():
    """测试唤醒词检测"""
    print("=" * 80)
    print("🧪 测试Jarvis唤醒词检测")
    print("=" * 80)
    
    detector = get_jarvis_detector()
    
    test_cases = [
        ("Jarvis, 今天天气怎么样？", True),
        ("jarvis, what is the weather?", True),
        ("Javis, 帮我查一下", True),  # 容错拼写
        ("今天天气怎么样？", False),  # 没有唤醒词
        ("Hello Jarvis, 你好", True),
        ("Jarvis！帮我查一下", True),
    ]
    
    print("\n测试用例:")
    all_correct = True
    for text, expected in test_cases:
        detected = detector.detect_in_text(text)
        status = "✅" if detected == expected else "❌"
        print(f"{status} 文本: '{text}'")
        print(f"    检测: {detected} (预期: {expected})")
        
        if detected:
            query = detector.extract_query_after_wake_word(text)
            print(f"    提取查询: '{query}'")
        print()
        
        if detected != expected:
            all_correct = False
    
    if all_correct:
        print("✅ 所有唤醒词检测测试通过！")
    else:
        print("⚠️ 部分测试需要检查")
    
    return all_correct


def test_voice_service():
    """测试语音服务整合"""
    print("\n" + "=" * 80)
    print("🧪 测试语音服务整合")
    print("=" * 80)
    
    print(f"\n语音功能配置:")
    print(f"  启用语音: {settings.ENABLE_SPEECH}")
    print(f"  Whisper模型: {settings.WHISPER_MODEL_SIZE}")
    print(f"  唤醒词: {settings.WAKE_WORD}")
    print(f"  使用edge-tts: {settings.USE_EDGE_TTS}")
    
    voice_service = get_voice_service()
    
    # 测试唤醒词检测和提取
    print("\n测试唤醒词检测和查询提取:")
    test_texts = [
        "Jarvis, 今天天气怎么样？",
        "jarvis, what is RAG?",
        "Javis, RAG係乜嘢？",
    ]
    
    for text in test_texts:
        detected, query = voice_service.detect_and_extract_query(text, use_wake_word=True)
        print(f"  原文: '{text}'")
        print(f"  唤醒词检测: {detected}")
        print(f"  提取查询: '{query}'")
        print()
    
    print("✅ 语音服务测试完成")
    print("\n注意: 完整的语音识别测试需要:")
    print("  1. 安装依赖: pip install openai-whisper soundfile edge-tts")
    print("  2. 准备音频文件（wav/mp3格式）")
    print("  3. 通过API上传音频进行测试")


def main():
    """主函数"""
    try:
        print("🚀 开始测试Jarvis语音助手功能\n")
        
        # 测试唤醒词检测
        test_wake_word_detection()
        
        # 测试语音服务
        test_voice_service()
        
        print("\n" + "=" * 80)
        print("✅ 所有测试完成！")
        print("=" * 80)
        print("\n💡 下一步:")
        print("  1. 安装语音依赖: pip install openai-whisper soundfile edge-tts")
        print("  2. 准备测试音频文件")
        print("  3. 使用API上传音频测试: POST /api/voice/query")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

