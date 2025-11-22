#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整语音交互测试：语音问题 → STT → Agent → TTS回答
步骤：
1. 将测试集1和2的问题用粤语TTS生成音频
2. 用STT识别音频得到文本
3. 将识别的文本发送给Agent
4. (可选)用TTS播报Agent的回答
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import requests
import time
import edge_tts
import asyncio
from pathlib import Path


# 测试集1 - 基础问题
TEST_SET_1 = [
    "香港科技大学在哪里？",
    "现在香港的天气怎么样？",
    "苹果公司的股价是多少？",
    "RAG系统是什么？"
]

# 测试集2 - 进阶问题
TEST_SET_2 = [
    "比亚迪和特斯拉哪个股价更高？",
    "比较香港和北京的天气",
    "RAG系统的核心组件有哪些？",
    "如何优化RAG系统的检索质量？"
]


async def generate_question_audio(question: str, output_file: str) -> bool:
    """
    将问题文本转换为粤语音频
    
    Args:
        question: 问题文本
        output_file: 输出音频文件路径
        
    Returns:
        bool: 是否成功
    """
    try:
        # 使用香港粤语女声
        voice = "zh-HK-HiuMaanNeural"
        communicate = edge_tts.Communicate(question, voice)
        await communicate.save(output_file)
        return True
    except Exception as e:
        print(f"❌ TTS生成失败: {e}")
        return False


def stt_recognize(audio_file: str) -> dict:
    """
    调用STT识别音频
    
    Args:
        audio_file: 音频文件路径
        
    Returns:
        {
            "success": bool,
            "text": str,
            "language": str,
            "confidence": float,
            "error": str (if failed)
        }
    """
    url = "http://localhost:5555/api/stt"
    
    try:
        with open(audio_file, 'rb') as f:
            files = {'audio': f}
            response = requests.post(url, files=files, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "text": data.get("text", ""),
                "language": data.get("language", ""),
                "confidence": data.get("confidence", 0.0)
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text[:200]}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def query_agent(question: str) -> dict:
    """
    调用Agent处理问题
    
    Args:
        question: 用户问题
        
    Returns:
        {
            "success": bool,
            "answer": str,
            "response_time": float,
            "tools_used": list,
            "error": str (if failed)
        }
    """
    url = "http://localhost:5555/api/agent_query"
    
    payload = {
        "query": question,
        "provider": "hkgai",
        "model": "HKGAI-V1"
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=120)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "answer": data.get("answer", ""),
                "response_time": response_time,
                "tools_used": data.get("tools_used", [])
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text[:200]}",
                "response_time": response_time
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response_time": 0
        }


def test_speech_question(original_question: str, question_id: str, audio_dir: Path, enable_answer_tts: bool = False):
    """
    测试单个语音问题的完整流程
    
    Args:
        original_question: 原始问题文本
        question_id: 问题编号（如 "set1_q1"）
        audio_dir: 音频目录
        enable_answer_tts: 是否对回答也进行TTS
    """
    print(f"\n{'='*80}")
    print(f"🎤 原始问题: {original_question}")
    print(f"{'='*80}")
    
    # 步骤1: 生成问题音频
    question_audio = audio_dir / f"{question_id}_question.mp3"
    print(f"\n📝 步骤1: 生成问题音频...")
    
    success = asyncio.run(generate_question_audio(original_question, str(question_audio)))
    
    if not success:
        print(f"❌ 问题音频生成失败")
        return {
            "success": False,
            "stage": "TTS",
            "error": "Failed to generate question audio"
        }
    
    file_size = question_audio.stat().st_size / 1024
    print(f"✅ 问题音频已生成: {question_audio.name} ({file_size:.2f} KB)")
    
    # 步骤2: STT识别
    print(f"\n🎧 步骤2: STT识别语音...")
    stt_result = stt_recognize(str(question_audio))
    
    if not stt_result["success"]:
        print(f"❌ STT识别失败: {stt_result['error']}")
        return {
            "success": False,
            "stage": "STT",
            "error": stt_result["error"]
        }
    
    recognized_text = stt_result["text"]
    language = stt_result.get("language", "unknown")
    confidence = stt_result.get("confidence", 0.0)
    
    print(f"✅ STT识别成功!")
    print(f"📝 识别文本: {recognized_text}")
    print(f"🌍 语言: {language}")
    print(f"📊 置信度: {confidence:.2%}")
    
    # 计算识别准确率
    accuracy = calculate_text_similarity(original_question, recognized_text)
    print(f"🎯 识别准确率: {accuracy:.1%}")
    
    # 步骤3: Agent处理
    print(f"\n🤖 步骤3: Agent处理问题...")
    agent_result = query_agent(recognized_text)
    
    if not agent_result["success"]:
        print(f"❌ Agent处理失败: {agent_result['error']}")
        return {
            "success": False,
            "stage": "Agent",
            "original_question": original_question,
            "recognized_text": recognized_text,
            "stt_accuracy": accuracy,
            "error": agent_result["error"]
        }
    
    answer = agent_result["answer"]
    print(f"✅ Agent回答成功!")
    print(f"⏱️  响应时间: {agent_result['response_time']:.2f}秒")
    print(f"🔧 使用工具: {', '.join(agent_result['tools_used']) if agent_result['tools_used'] else '无'}")
    print(f"\n📝 回答:\n{answer[:300]}{'...' if len(answer) > 300 else ''}")
    
    # 步骤4: (可选)回答TTS
    if enable_answer_tts:
        print(f"\n🎤 步骤4: 生成回答语音...")
        answer_audio = audio_dir / f"{question_id}_answer.mp3"
        success = asyncio.run(generate_question_audio(answer, str(answer_audio)))
        
        if success:
            print(f"✅ 回答音频已生成: {answer_audio.name}")
            print(f"🔊 正在播放回答...")
            os.system(f'afplay "{answer_audio}"')
    
    return {
        "success": True,
        "original_question": original_question,
        "recognized_text": recognized_text,
        "stt_accuracy": accuracy,
        "answer": answer,
        "response_time": agent_result["response_time"],
        "tools_used": agent_result["tools_used"]
    }


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    计算两个文本的相似度（简单字符匹配）
    
    Args:
        text1: 原始文本
        text2: 识别文本
        
    Returns:
        float: 相似度 (0.0-1.0)
    """
    # 简单的字符级相似度
    text1 = text1.strip().replace(" ", "").replace("？", "").replace("?", "")
    text2 = text2.strip().replace(" ", "").replace("？", "").replace("?", "")
    
    if not text1 or not text2:
        return 0.0
    
    # 计算公共字符数
    common = sum(1 for c in text1 if c in text2)
    return common / max(len(text1), len(text2))


def run_test_set(test_set: list, set_name: str, audio_dir: Path, enable_answer_tts: bool = False):
    """
    运行整个测试集
    
    Args:
        test_set: 问题列表
        set_name: 测试集名称（如 "Set1"）
        audio_dir: 音频目录
        enable_answer_tts: 是否对回答也进行TTS
    """
    print(f"\n\n{'#'*80}")
    print(f"🎯 {set_name}")
    print(f"{'#'*80}")
    print(f"📋 共{len(test_set)}个问题")
    print(f"🔊 完整流程: 问题TTS → STT识别 → Agent处理 → {'回答TTS' if enable_answer_tts else '文本回答'}")
    
    results = []
    
    for i, question in enumerate(test_set, 1):
        print(f"\n\n{'─'*80}")
        print(f"进度: {i}/{len(test_set)} | {set_name}")
        print(f"{'─'*80}")
        
        question_id = f"{set_name.lower()}_q{i}"
        result = test_speech_question(question, question_id, audio_dir, enable_answer_tts)
        
        results.append(result)
        
        # 等待一下避免API限流
        if i < len(test_set):
            print(f"\n⏳ 等待3秒...")
            time.sleep(3)
    
    # 统计
    success_count = sum(1 for r in results if r["success"])
    total_accuracy = sum(r.get("stt_accuracy", 0) for r in results if r["success"])
    avg_accuracy = total_accuracy / success_count if success_count > 0 else 0
    
    print(f"\n\n{'='*80}")
    print(f"📊 {set_name}测试完成")
    print(f"{'='*80}")
    print(f"✅ 成功: {success_count}/{len(test_set)}")
    print(f"🎯 平均STT识别准确率: {avg_accuracy:.1%}")
    
    if success_count < len(test_set):
        print(f"\n❌ 失败的问题:")
        for r in results:
            if not r["success"]:
                print(f"  - {r.get('original_question', 'Unknown')} (失败阶段: {r.get('stage', 'Unknown')})")
    
    # 详细结果
    print(f"\n📝 详细结果:")
    for i, r in enumerate(results, 1):
        if r["success"]:
            print(f"\n{i}. 原始: {r['original_question']}")
            print(f"   识别: {r['recognized_text']}")
            print(f"   准确率: {r['stt_accuracy']:.1%}")
            print(f"   工具: {', '.join(r['tools_used']) if r['tools_used'] else '无'}")
    
    return results


def main():
    print("="*80)
    print("🎤 完整语音交互测试")
    print("="*80)
    print("\n🎯 测试流程:")
    print("  1️⃣  将问题转换为粤语音频 (TTS)")
    print("  2️⃣  识别音频得到文本 (STT)")
    print("  3️⃣  Agent处理识别的文本")
    print("  4️⃣  (可选)将回答转换为语音")
    print("\n🎵 TTS引擎: Edge TTS (zh-HK-HiuMaanNeural)")
    print("🎧 STT引擎: Whisper + HKGAI (双引擎)")
    print("🤖 Agent引擎: HKGAI-V1")
    
    # 创建音频目录
    audio_dir = Path("speech_questions_audio")
    audio_dir.mkdir(exist_ok=True)
    print(f"\n💾 音频目录: {audio_dir.absolute()}")
    
    # 询问用户选择
    print(f"\n{'='*80}")
    print("请选择测试集:")
    print("  1 - 测试集1（4个基础问题）")
    print("  2 - 测试集2（4个进阶问题）")
    print("  3 - 两个测试集都测试（8个问题）")
    print(f"{'='*80}")
    
    choice = input("\n请输入选择 (1/2/3): ").strip()
    
    # 询问是否启用回答TTS（默认为y）
    answer_input = input("\n是否对回答也进行TTS播报？(y/n，默认y): ").strip().lower()
    answer_tts = answer_input != 'n'  # 除非输入n，否则默认为y
    
    print("\n" + "="*80)
    print("🚀 开始测试...")
    print("="*80)
    
    if choice == "1":
        run_test_set(TEST_SET_1, "Set1", audio_dir, answer_tts)
    elif choice == "2":
        run_test_set(TEST_SET_2, "Set2", audio_dir, answer_tts)
    elif choice == "3":
        results1 = run_test_set(TEST_SET_1, "Set1", audio_dir, answer_tts)
        print("\n\n⏳ 等待5秒后开始测试集2...")
        time.sleep(5)
        results2 = run_test_set(TEST_SET_2, "Set2", audio_dir, answer_tts)
        
        # 总体统计
        all_results = results1 + results2
        total_success = sum(1 for r in all_results if r["success"])
        total_accuracy = sum(r.get("stt_accuracy", 0) for r in all_results if r["success"])
        avg_accuracy = total_accuracy / total_success if total_success > 0 else 0
        
        print(f"\n\n{'='*80}")
        print(f"📊 总体统计")
        print(f"{'='*80}")
        print(f"✅ 总成功率: {total_success}/{len(all_results)} ({total_success/len(all_results)*100:.1f}%)")
        print(f"🎯 平均STT识别准确率: {avg_accuracy:.1%}")
    else:
        print("❌ 无效选择")
        return
    
    print(f"\n\n{'='*80}")
    print("✅ 测试完成！")
    print(f"{'='*80}")
    print(f"\n📂 所有音频文件已保存到: {audio_dir.absolute()}")
    print(f"\n💡 文件说明:")
    print(f"  *_question.mp3 - 问题的粤语音频")
    if answer_tts:
        print(f"  *_answer.mp3 - 回答的粤语音频")


if __name__ == "__main__":
    main()

