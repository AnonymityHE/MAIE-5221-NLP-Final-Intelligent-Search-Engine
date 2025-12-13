#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Set 3 图片问题测试（6个）
测试Doubao多模态能力
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import requests
import time
import json
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict

# 图片问题列表
IMAGE_TEST_QUESTIONS = [
    {
        "id": "EN-IMG-1",
        "image": "figures/hkust.png",
        "question": "Identify this sculpture, explain its symbolic meaning, and tell me where exactly on campus it is located.",
        "language": "English",
        "category": "Image-Recognition"
    },
    {
        "id": "EN-IMG-2",
        "image": "figures/snack.png",
        "question": "Is this snack suitable for someone on a low-sodium diet? Extract the sodium content to justify your answer.",
        "language": "English",
        "category": "OCR-Analysis"
    },
    {
        "id": "EN-IMG-3",
        "image": "figures/error_info.png",
        "question": "Analyze this error screenshot and suggest a fix for the Python code.",
        "language": "English",
        "category": "Code-Debug"
    },
    {
        "id": "CN-IMG-1",
        "image": "figures/hkust.png",
        "question": "識別這座雕塑，解釋它的象徵意義，並告訴我它具體位於校園的哪個位置。",
        "language": "Chinese",
        "category": "Image-Recognition"
    },
    {
        "id": "CN-IMG-2",
        "image": "figures/snack.png",
        "question": "這個零食適合低鈉飲食的人嗎？提取鈉含量來支持你的回答。",
        "language": "Chinese",
        "category": "OCR-Analysis"
    },
    {
        "id": "CN-IMG-3",
        "image": "figures/error_info.png",
        "question": "分析這個錯誤截圖並建議修復此 Python 代碼的方法。",
        "language": "Chinese",
        "category": "Code-Debug"
    }
]


def load_image_as_base64(image_path: str) -> str:
    """将图片转换为base64"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def query_multimodal(question: str, image_base64: str) -> Dict:
    """
    调用多模态接口
    
    Args:
        question: 用户问题
        image_base64: 图片的base64编码
        
    Returns:
        结果字典
    """
    url = "http://localhost:5555/api/multimodal/query"
    
    payload = {
        "query": question,
        "images": [image_base64],  # 注意是数组格式
        "provider": "doubao",
        "use_ocr": True
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
                "model": data.get("model_used", "Doubao")
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


def test_image_question(test_case: dict, index: int, total: int) -> dict:
    """测试单个图片问题"""
    print(f"\n{'#'*100}")
    print(f"进度: {index}/{total}")
    print(f"{'#'*100}")
    print(f"❓ [{test_case['id']}] {test_case['question']}")
    print(f"   语言: {test_case['language']} | 类别: {test_case['category']}")
    print(f"   图片: {test_case['image']}")
    print(f"{'─'*100}")
    
    # 加载图片
    try:
        image_base64 = load_image_as_base64(test_case['image'])
        print(f"📸 图片已加载 (大小: {len(image_base64)/1024:.1f}KB)")
    except Exception as e:
        print(f"❌ 图片加载失败: {e}")
        return {
            **test_case,
            "result": {
                "success": False,
                "error": f"Image load failed: {e}",
                "response_time": 0
            }
        }
    
    # 调用多模态接口
    result = query_multimodal(test_case['question'], image_base64)
    
    if not result["success"]:
        print(f"❌ 失败: {result.get('error', 'Unknown error')}")
    else:
        print(f"✅ 成功")
        print(f"⏱️  响应时间: {result['response_time']:.2f}秒")
        print(f"🤖 使用模型: {result.get('model', 'Unknown')}")
        print(f"📝 回答: {result['answer'][:300]}{'...' if len(result['answer']) > 300 else ''}")
    
    return {
        **test_case,
        "result": result
    }


def main():
    print("="*100)
    print("🖼️  Test Set 3 图片问题测试 (6个)")
    print("="*100)
    print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 总问题数: {len(IMAGE_TEST_QUESTIONS)}")
    print(f"🤖 使用模型: Doubao (多模态)")
    print("="*100)
    
    results = []
    start_time = time.time()
    
    for i, test_case in enumerate(IMAGE_TEST_QUESTIONS, 1):
        try:
            result = test_image_question(test_case, i, len(IMAGE_TEST_QUESTIONS))
            results.append(result)
            
            # 每个问题后等待3秒
            if i < len(IMAGE_TEST_QUESTIONS):
                print(f"\n⏳ 等待3秒...")
                time.sleep(3)
        except KeyboardInterrupt:
            print("\n\n⚠️  测试被用户中断")
            break
        except Exception as e:
            print(f"\n❌ 测试异常: {e}")
            continue
    
    total_time = time.time() - start_time
    
    # 统计
    successful = [r for r in results if r['result']['success']]
    failed = [r for r in results if not r['result']['success']]
    avg_time = sum(r['result']['response_time'] for r in successful) / len(successful) if successful else 0
    
    # 按类别统计
    categories = {}
    for r in successful:
        cat = r['category']
        if cat not in categories:
            categories[cat] = {"count": 0, "times": []}
        categories[cat]["count"] += 1
        categories[cat]["times"].append(r['result']['response_time'])
    
    print(f"\n\n{'='*100}")
    print("📊 图片问题测试总结")
    print(f"{'='*100}")
    print(f"✅ 成功: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"❌ 失败: {len(failed)}/{len(results)}")
    print(f"⏱️  平均响应时间: {avg_time:.2f}秒")
    print(f"⏱️  总耗时: {total_time/60:.1f}分钟")
    
    if categories:
        print(f"\n按类别统计:")
        for cat, data in sorted(categories.items()):
            avg = sum(data['times']) / len(data['times'])
            print(f"  {cat}: {data['count']}个, 平均 {avg:.2f}秒")
    
    if failed:
        print(f"\n❌ 失败的问题:")
        for r in failed:
            print(f"  [{r['id']}] {r['question'][:60]}... - {r['result'].get('error', 'Unknown')}")
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_results/test_set3_images_{timestamp}.json"
    
    os.makedirs("test_results", exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "total_questions": len(IMAGE_TEST_QUESTIONS),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful)/len(results)*100 if results else 0,
            "avg_response_time": avg_time,
            "total_time_minutes": total_time/60,
            "note": "使用Doubao多模态模型测试图片问题",
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 详细结果已保存到: {output_file}")
    print("\n✅ 图片问题测试完成！")


if __name__ == "__main__":
    main()

