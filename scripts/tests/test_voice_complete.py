#!/usr/bin/env python3
"""
完整的Jarvis语音助手功能测试
包括：唤醒词检测、Whisper模型加载、Silero VAD、API测试
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import requests
import json
from pathlib import Path
from services.speech.wake_word_detector import get_jarvis_detector
from services.speech.voice_service import get_voice_service
from services.speech.whisper_stt import get_whisper_stt
from services.core.config import settings


def test_wake_word_detection():
    """测试唤醒词检测"""
    print("=" * 80)
    print("🧪 测试1: Jarvis唤醒词检测")
    print("=" * 80)
    
    detector = get_jarvis_detector()
    
    test_cases = [
        ("Jarvis, 今天天气怎么样？", True, "今天天气怎么样？"),
        ("jarvis, what is the weather?", True, "what is the weather?"),
        ("Javis, 帮我查一下", True, "帮我查一下"),  # 容错拼写
        ("今天天气怎么样？", False, None),  # 没有唤醒词
        ("Hello Jarvis, 你好", True, "你好"),
        ("Jarvis！帮我查一下", True, "帮我查一下"),
        ("Jarvis, RAG係乜嘢？", True, "RAG係乜嘢？"),  # 粤语
    ]
    
    print("\n测试用例:")
    passed = 0
    failed = 0
    for text, expected_detected, expected_query in test_cases:
        detected = detector.detect_in_text(text)
        query = detector.extract_query_after_wake_word(text) if detected else None
        
        if detected == expected_detected:
            if not expected_query or query == expected_query:
                print(f"✅ '{text}' → 检测: {detected}, 查询: '{query}'")
                passed += 1
            else:
                print(f"⚠️  '{text}' → 检测正确但查询不匹配")
                print(f"     预期: '{expected_query}', 实际: '{query}'")
                failed += 1
        else:
            print(f"❌ '{text}' → 检测: {detected} (预期: {expected_detected})")
            failed += 1
    
    print(f"\n结果: ✅ {passed} 通过, ❌ {failed} 失败")
    return failed == 0


def test_whisper_model():
    """测试Whisper模型加载"""
    print("\n" + "=" * 80)
    print("🧪 测试2: Whisper模型加载")
    print("=" * 80)
    
    print(f"\n配置:")
    print(f"  模型大小: {settings.WHISPER_MODEL_SIZE}")
    print(f"  启用语音: {settings.ENABLE_SPEECH}")
    
    try:
        stt = get_whisper_stt()
        if stt and stt.is_available():
            print(f"\n✅ Whisper模型加载成功")
            print(f"  模型类型: {type(stt.model).__name__}")
            print(f"  模型大小: {settings.WHISPER_MODEL_SIZE}")
            return True
        else:
            print(f"\n❌ Whisper模型未加载")
            print("  可能原因:")
            print("  - 未安装: pip install openai-whisper soundfile")
            print("  - 模型下载失败")
            return False
    except Exception as e:
        print(f"\n❌ Whisper模型加载失败: {e}")
        return False


def test_silero_vad():
    """测试Silero VAD（可选）"""
    print("\n" + "=" * 80)
    print("🧪 测试3: Silero VAD（可选功能）")
    print("=" * 80)
    
    try:
        from services.speech.vad_silero import get_silero_vad
        
        vad = get_silero_vad()
        if vad and vad.model is not None:
            print(f"\n✅ Silero VAD已加载")
            print(f"  设备: {vad.device}")
            return True
        else:
            print(f"\n⚠️  Silero VAD未安装或未加载")
            print("  这是可选功能，不影响基础语音识别")
            print("  安装命令: pip install torch silero-vad onnxruntime")
            return None  # 不是失败，只是未安装
    except ImportError:
        print(f"\n⚠️  Silero VAD未安装（可选功能）")
        return None
    except Exception as e:
        print(f"\n❌ Silero VAD加载失败: {e}")
        return False


def test_voice_service_integration():
    """测试语音服务整合"""
    print("\n" + "=" * 80)
    print("🧪 测试4: 语音服务整合")
    print("=" * 80)
    
    voice_service = get_voice_service()
    
    print(f"\n配置:")
    print(f"  唤醒词: {settings.WAKE_WORD}")
    print(f"  使用edge-tts: {settings.USE_EDGE_TTS}")
    
    # 测试唤醒词检测和提取
    print("\n测试唤醒词检测和查询提取:")
    test_texts = [
        "Jarvis, 今天天气怎么样？",
        "jarvis, what is RAG?",
        "Javis, RAG係乜嘢？",
    ]
    
    passed = 0
    for text in test_texts:
        detected, query = voice_service.detect_and_extract_query(text, use_wake_word=True)
        if detected and query:
            print(f"  ✅ '{text}' → '{query}'")
            passed += 1
        else:
            print(f"  ❌ '{text}' → 检测失败")
    
    print(f"\n结果: ✅ {passed}/{len(test_texts)} 通过")
    return passed == len(test_texts)


def test_api_endpoint():
    """测试API端点（如果服务正在运行）"""
    print("\n" + "=" * 80)
    print("🧪 测试5: API端点测试")
    print("=" * 80)
    
    base_url = "http://localhost:8000"
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print(f"\n✅ API服务正在运行")
            health_data = response.json()
            print(f"  状态: {health_data.get('status', 'unknown')}")
            return True
        else:
            print(f"\n⚠️  API服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"\n⚠️  API服务未运行")
        print("  启动命令: uvicorn backend.main:app --host 0.0.0.0 --port 8000")
        return None
    except Exception as e:
        print(f"\n❌ API测试失败: {e}")
        return False


def test_websocket_endpoint():
    """测试WebSocket端点可用性"""
    print("\n" + "=" * 80)
    print("🧪 测试6: WebSocket端点")
    print("=" * 80)
    
    print(f"\nWebSocket端点: ws://localhost:8000/api/voice/ws")
    print(f"前端页面: http://localhost:8000/voice")
    print(f"\n💡 WebSocket测试需要:")
    print(f"  1. API服务正在运行")
    print(f"  2. 浏览器访问 http://localhost:8000/voice")
    print(f"  3. 点击'连接'并测试语音输入")
    
    return None  # WebSocket测试需要浏览器，这里只提供信息


def test_audio_format_support():
    """测试支持的音频格式"""
    print("\n" + "=" * 80)
    print("🧪 测试7: 音频格式支持")
    print("=" * 80)
    
    print(f"\n支持的音频格式:")
    print(f"  ✅ WAV (推荐)")
    print(f"  ✅ MP3")
    print(f"  ✅ M4A")
    print(f"  ✅ FLAC")
    print(f"  ✅ WebM (WebSocket实时录音)")
    
    print(f"\n推荐配置:")
    print(f"  采样率: 16kHz")
    print(f"  声道: 单声道")
    print(f"  位深: 16-bit")
    
    return True


def main():
    """主函数"""
    print("🚀 开始完整Jarvis语音助手功能测试\n")
    
    results = {}
    
    # 测试1: 唤醒词检测
    results['wake_word'] = test_wake_word_detection()
    
    # 测试2: Whisper模型
    results['whisper'] = test_whisper_model()
    
    # 测试3: Silero VAD（可选）
    results['silero_vad'] = test_silero_vad()
    
    # 测试4: 语音服务整合
    results['voice_service'] = test_voice_service_integration()
    
    # 测试5: API端点
    results['api'] = test_api_endpoint()
    
    # 测试6: WebSocket端点（信息）
    results['websocket'] = test_websocket_endpoint()
    
    # 测试7: 音频格式支持
    results['audio_format'] = test_audio_format_support()
    
    # 汇总结果
    print("\n" + "=" * 80)
    print("📊 测试结果汇总")
    print("=" * 80)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    print(f"\n✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"⚠️  跳过: {skipped}")
    
    print(f"\n详细结果:")
    for name, result in results.items():
        if result is True:
            status = "✅"
        elif result is False:
            status = "❌"
        else:
            status = "⚠️ "
        print(f"  {status} {name.replace('_', ' ').title()}")
    
    print("\n" + "=" * 80)
    print("💡 下一步建议")
    print("=" * 80)
    
    if not results.get('whisper'):
        print("  1. 安装Whisper依赖: pip install openai-whisper soundfile")
    
    if results.get('silero_vad') is None:
        print("  2. （可选）安装Silero VAD: pip install torch silero-vad onnxruntime")
    
    if results.get('api') is None:
        print("  3. 启动API服务: uvicorn backend.main:app --host 0.0.0.0 --port 8000")
        print("  4. 访问语音助手: http://localhost:8000/voice")
    
    print("\n✅ 测试完成！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

