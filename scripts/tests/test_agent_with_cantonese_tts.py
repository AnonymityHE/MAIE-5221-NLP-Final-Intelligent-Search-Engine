#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试集1和2的Agent + 粤语TTS完整流程
完整体验：问题 → Agent智能回答 → 粤语语音播报
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
        print(f"⏳ Agent正在思考...")
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=120)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "answer": data.get("answer", ""),
                "response_time": response_time,
                "tools_used": data.get("tools_used", []),
                "workflow_steps": len(data.get("workflow_steps", []))
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


async def generate_cantonese_tts(text: str, output_file: str) -> bool:
    """
    生成粤语TTS语音
    
    Args:
        text: 要转换的文本
        output_file: 输出文件路径
        
    Returns:
        bool: 是否成功
    """
    try:
        # 使用香港粤语女声
        voice = "zh-HK-HiuMaanNeural"
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        return True
    except Exception as e:
        print(f"❌ TTS失败: {e}")
        return False


def test_question_with_tts(question: str, question_id: str, output_dir: Path):
    """
    测试单个问题：Agent回答 + 粤语TTS
    
    Args:
        question: 问题文本
        question_id: 问题编号（如 "set1_q1"）
        output_dir: 输出目录
    """
    print(f"\n{'─'*80}")
    print(f"❓ 问题: {question}")
    print(f"{'─'*80}")
    
    # 1. Agent处理问题
    result = query_agent(question)
    
    if not result["success"]:
        print(f"❌ Agent失败: {result['error']}")
        return False
    
    answer = result["answer"]
    print(f"✅ Agent回答成功!")
    print(f"⏱️  响应时间: {result['response_time']:.2f}秒")
    print(f"🔧 使用工具: {', '.join(result['tools_used']) if result['tools_used'] else '无'}")
    print(f"\n📝 回答:\n{answer[:300]}{'...' if len(answer) > 300 else ''}")
    
    # 2. 生成粤语TTS
    output_file = output_dir / f"{question_id}.mp3"
    print(f"\n🎤 生成粤语语音...")
    
    success = asyncio.run(generate_cantonese_tts(answer, str(output_file)))
    
    if success:
        file_size = output_file.stat().st_size / 1024
        print(f"✅ TTS成功!")
        print(f"💾 已保存: {output_file.name}")
        print(f"📊 大小: {file_size:.2f} KB")
        
        # 3. 播放语音
        print(f"\n🔊 正在播放粤语回答...")
        os.system(f'afplay "{output_file}"')
        print(f"✅ 播放完成!")
        
        return True
    else:
        print(f"❌ TTS失败")
        return False


def run_test_set(test_set: list, set_name: str, output_dir: Path):
    """
    运行整个测试集
    
    Args:
        test_set: 问题列表
        set_name: 测试集名称（如 "Set1"）
        output_dir: 输出目录
    """
    print(f"\n\n{'='*80}")
    print(f"🎯 {set_name}")
    print(f"{'='*80}")
    print(f"📋 共{len(test_set)}个问题")
    
    results = []
    
    for i, question in enumerate(test_set, 1):
        print(f"\n\n{'#'*80}")
        print(f"进度: {i}/{len(test_set)} | {set_name}")
        print(f"{'#'*80}")
        
        question_id = f"{set_name.lower()}_q{i}"
        success = test_question_with_tts(question, question_id, output_dir)
        
        results.append({
            "question": question,
            "success": success
        })
        
        # 等待一下避免API限流
        if i < len(test_set):
            print(f"\n⏳ 等待5秒...")
            time.sleep(5)
    
    # 统计
    success_count = sum(1 for r in results if r["success"])
    print(f"\n\n{'='*80}")
    print(f"📊 {set_name}测试完成")
    print(f"{'='*80}")
    print(f"成功: {success_count}/{len(test_set)}")
    
    if success_count < len(test_set):
        print(f"\n❌ 失败的问题:")
        for r in results:
            if not r["success"]:
                print(f"  - {r['question']}")


def main():
    print("="*80)
    print("🎤 测试集1和2 - Agent + 粤语TTS完整流程")
    print("="*80)
    print("\n🎯 测试流程:")
    print("  1️⃣  Agent接收问题")
    print("  2️⃣  调用工具获取信息（RAG/搜索/天气/金融等）")
    print("  3️⃣  生成智能回答")
    print("  4️⃣  用粤语TTS朗读回答")
    print("  5️⃣  自动播放语音")
    print("\n🤖 Agent引擎: HKGAI-V1")
    print("🎵 TTS引擎: Edge TTS (zh-HK-HiuMaanNeural)")
    
    # 创建输出目录
    output_dir = Path("cantonese_tts_output")
    output_dir.mkdir(exist_ok=True)
    print(f"\n💾 输出目录: {output_dir.absolute()}")
    
    # 询问用户选择
    print(f"\n{'='*80}")
    print("请选择测试集:")
    print("  1 - 测试集1（4个基础问题）")
    print("  2 - 测试集2（4个进阶问题）")
    print("  3 - 两个测试集都测试（8个问题）")
    print("  4 - 单个问题测试")
    print(f"{'='*80}")
    
    choice = input("\n请输入选择 (1/2/3/4): ").strip()
    
    if choice == "1":
        run_test_set(TEST_SET_1, "Set1", output_dir)
    elif choice == "2":
        run_test_set(TEST_SET_2, "Set2", output_dir)
    elif choice == "3":
        run_test_set(TEST_SET_1, "Set1", output_dir)
        print("\n\n⏳ 等待10秒后开始测试集2...")
        time.sleep(10)
        run_test_set(TEST_SET_2, "Set2", output_dir)
    elif choice == "4":
        question = input("\n请输入问题: ").strip()
        if question:
            test_question_with_tts(question, "custom", output_dir)
        else:
            print("❌ 问题不能为空")
    else:
        print("❌ 无效选择")
        return
    
    print(f"\n\n{'='*80}")
    print("✅ 测试完成！")
    print(f"{'='*80}")
    print(f"\n📂 所有语音文件已保存到: {output_dir.absolute()}")
    print(f"\n💡 播放方法:")
    print(f"  cd {output_dir}")
    print(f"  afplay set1_q1.mp3")
    print(f"\n或者:")
    print(f"  afplay cantonese_tts_output/*.mp3")


if __name__ == "__main__":
    main()

