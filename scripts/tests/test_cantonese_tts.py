#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试粤语TTS（文本转语音）
测试HKGAI的粤语语音合成能力
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import requests
from pathlib import Path


def test_hkgai_cantonese_tts(text: str, output_file: str = "cantonese_output.wav"):
    """
    测试HKGAI粤语TTS
    
    Args:
        text: 要合成的文本
        output_file: 输出音频文件名
    """
    print("=" * 80)
    print("🎤 HKGAI粤语TTS测试")
    print("=" * 80)
    print(f"\n📝 文本: {text}")
    print(f"🌐 语言: 粤语 (Cantonese)")
    print(f"💾 输出: {output_file}")
    
    # HKGAI Speech API配置
    api_key = "TzmW5eWvGWphlubmavEIRtG5U6OwS9wF02AwtEHWx0stLvtqZWpz5LK2q7lRQhDY"
    url = "https://openspeech.hkgai.net/api/v1/text_to_speech"
    
    # 构建请求
    payload = {
        "text": text,
        "language": "yue",  # 粤语
        "speed": 1.0,
        "volume": 1.0
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("\n⏳ 正在调用HKGAI TTS API...")
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            # 保存音频文件
            output_path = Path(output_file)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            file_size = output_path.stat().st_size / 1024  # KB
            print(f"✅ TTS成功！")
            print(f"💾 已保存到: {output_path.absolute()}")
            print(f"📊 文件大小: {file_size:.2f} KB")
            print(f"\n🎵 使用以下命令播放:")
            print(f"   afplay {output_path.absolute()}")
            
            return True
        else:
            print(f"❌ TTS失败: HTTP {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_tts_cantonese(text: str, output_file: str = "edge_cantonese_output.mp3"):
    """
    测试Edge TTS粤语（作为对比）
    
    Args:
        text: 要合成的文本
        output_file: 输出音频文件名
    """
    print("\n" + "=" * 80)
    print("🎤 Edge TTS粤语测试（对比）")
    print("=" * 80)
    print(f"\n📝 文本: {text}")
    print(f"🌐 语言: 粤语 (Cantonese)")
    print(f"💾 输出: {output_file}")
    
    try:
        import edge_tts
        import asyncio
        
        async def synthesize():
            # 使用香港粤语女声
            voice = "zh-HK-HiuMaanNeural"
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_file)
        
        print("\n⏳ 正在调用Edge TTS API...")
        asyncio.run(synthesize())
        
        output_path = Path(output_file)
        file_size = output_path.stat().st_size / 1024  # KB
        print(f"✅ TTS成功！")
        print(f"💾 已保存到: {output_path.absolute()}")
        print(f"📊 文件大小: {file_size:.2f} KB")
        print(f"\n🎵 使用以下命令播放:")
        print(f"   afplay {output_path.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Edge TTS失败: {e}")
        return False


def main():
    print("\n" + "🎵" * 40)
    print("粤语TTS测试")
    print("🎵" * 40)
    
    # 测试文本
    test_texts = [
        {
            "text": "请勿靠近车门",
            "desc": "地铁提示音（短）",
            "hkgai_output": "cantonese_door_warning_hkgai.wav",
            "edge_output": "cantonese_door_warning_edge.mp3"
        },
        {
            "text": "各位乘客请注意，列车即将到站，请提前做好下车准备。",
            "desc": "地铁报站音（长）",
            "hkgai_output": "cantonese_station_announce_hkgai.wav",
            "edge_output": "cantonese_station_announce_edge.mp3"
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_texts, 1):
        print(f"\n\n{'#' * 80}")
        print(f"测试 {i}/{len(test_texts)}: {test['desc']}")
        print(f"{'#' * 80}")
        
        # 测试HKGAI
        hkgai_success = test_hkgai_cantonese_tts(
            test["text"],
            test["hkgai_output"]
        )
        
        # 等待一下
        import time
        time.sleep(2)
        
        # 测试Edge TTS
        edge_success = test_edge_tts_cantonese(
            test["text"],
            test["edge_output"]
        )
        
        results.append({
            "text": test["text"],
            "desc": test["desc"],
            "hkgai": hkgai_success,
            "edge": edge_success
        })
        
        if i < len(test_texts):
            print("\n⏳ 等待3秒...")
            time.sleep(3)
    
    # 总结
    print("\n\n" + "=" * 80)
    print("📊 测试总结")
    print("=" * 80)
    
    hkgai_count = sum(1 for r in results if r["hkgai"])
    edge_count = sum(1 for r in results if r["edge"])
    
    print(f"\nHKGAI TTS: {hkgai_count}/{len(results)} 成功")
    print(f"Edge TTS: {edge_count}/{len(results)} 成功")
    
    print(f"\n🎵 生成的音频文件:")
    for r in results:
        print(f"\n  📝 {r['text']}")
        if r["hkgai"]:
            print(f"    ✅ HKGAI: cantonese_*_hkgai.wav")
        if r["edge"]:
            print(f"    ✅ Edge: cantonese_*_edge.mp3")
    
    print(f"\n💡 播放方法:")
    print(f"  afplay cantonese_door_warning_hkgai.wav")
    print(f"  afplay cantonese_door_warning_edge.mp3")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

