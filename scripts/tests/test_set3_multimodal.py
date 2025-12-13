#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Set 3 多模态测试 - 图片问题（6个）
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

# Test Set 3 - 图片问题
TEST_SET_3_MULTIMODAL = [
    # English Questions with Images (3个)
    {
        "id": "EN-1",
        "question": "Identify this sculpture, explain its symbolic meaning, and tell me where exactly on campus it is located.",
        "language": "English",
        "category": "Vision-Analysis",
        "image": "figures/hkust.png"
    },
    {
        "id": "EN-2",
        "question": "Is this snack suitable for someone on a low-sodium diet? Extract the sodium content to justify your answer.",
        "language": "English",
        "category": "OCR-Analysis",
        "image": "figures/snack.png"
    },
    {
        "id": "EN-3",
        "question": "Analyze this error screenshot and suggest a fix for the Python code.",
        "language": "English",
        "category": "Code-Analysis",
        "image": "figures/error_info.png"
    },
    
    # Chinese Questions with Images (3个)
    {
        "id": "CN-1",
        "question": "識別這座雕塑，解釋它的象徵意義，並告訴我它具體位於校園的哪個位置。",
        "language": "Chinese",
        "category": "Vision-Analysis",
        "image": "figures/hkust.png"
    },
    {
        "id": "CN-2",
        "question": "這個零食適合低鈉飲食的人嗎？提取鈉含量來支持你的回答。",
        "language": "Chinese",
        "category": "OCR-Analysis",
        "image": "figures/snack.png"
    },
    {
        "id": "CN-3",
        "question": "分析這個錯誤截圖並建議修復此 Python 代碼的方法。",
        "language": "Chinese",
        "category": "Code-Analysis",
        "image": "figures/error_info.png"
    },
]


def image_to_base64(image_path: str) -> str:
    """将图片转换为base64编码"""
    with open(image_path, 'rb') as f:
        image_data = f.read()
        return base64.b64encode(image_data).decode('utf-8')


def query_multimodal(question: str, image_path: str) -> Dict:
    """调用Multimodal接口处理图片问题"""
    url = "http://localhost:5555/api/multimodal/query"
    
    try:
        # 读取并编码图片
        image_base64 = image_to_base64(image_path)
        
        payload = {
            "query": question,
            "images": [image_base64],
            "use_ocr": True,
            "provider": "doubao",
            "model": "doubao-seed-1-6-251015"
        }
        
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=120)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "answer": data.get("answer", ""),
                "response_time": response_time,
                "ocr_results": data.get("ocr_results", []),
                "model_used": data.get("model_used", "")
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


def test_question(test_case: dict, index: int, total: int) -> dict:
    """测试单个图片问题"""
    print(f"\n{'#'*100}")
    print(f"进度: {index}/{total}")
    print(f"{'#'*100}")
    print(f"❓ [{test_case['id']}] {test_case['question']}")
    print(f"   语言: {test_case['language']} | 类别: {test_case['category']}")
    print(f"   图片: {test_case['image']}")
    print(f"{'─'*100}")
    
    # 检查图片文件是否存在
    if not os.path.exists(test_case['image']):
        print(f"❌ 图片文件不存在: {test_case['image']}")
        return {
            **test_case,
            "result": {
                "success": False,
                "error": "Image file not found",
                "response_time": 0
            }
        }
    
    result = query_multimodal(test_case['question'], test_case['image'])
    
    if not result["success"]:
        print(f"❌ 失败: {result.get('error', 'Unknown error')}")
    else:
        print(f"✅ 成功")
        print(f"⏱️  响应时间: {result['response_time']:.2f}秒")
        print(f"🤖 模型: {result.get('model_used', 'N/A')}")
        if result.get('ocr_results'):
            print(f"📝 OCR识别: {len(result['ocr_results'])}个结果")
            for i, ocr in enumerate(result['ocr_results'], 1):
                text_preview = ocr.get('text', '')[:100]
                print(f"   图片{i}: {text_preview}..." if len(ocr.get('text', '')) > 100 else f"   图片{i}: {text_preview}")
        print(f"💬 回答: {result['answer'][:250]}{'...' if len(result['answer']) > 250 else ''}")
    
    return {
        **test_case,
        "result": result
    }


def main():
    print("="*100)
    print("🧪 Test Set 3 多模态测试 - 图片问题")
    print("="*100)
    print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 总问题数: {len(TEST_SET_3_MULTIMODAL)}")
    print(f"🖼️  使用模型: Doubao Seed-1-6-251015 (多模态)")
    print("="*100)
    
    results = []
    start_time = time.time()
    
    for i, test_case in enumerate(TEST_SET_3_MULTIMODAL, 1):
        try:
            result = test_question(test_case, i, len(TEST_SET_3_MULTIMODAL))
            results.append(result)
            
            # 每个问题等待3秒
            if i < len(TEST_SET_3_MULTIMODAL):
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
            categories[cat] = []
        categories[cat].append(r['result']['response_time'])
    
    print(f"\n\n{'='*100}")
    print("📊 Test Set 3 多模态测试总结")
    print(f"{'='*100}")
    print(f"✅ 成功: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"❌ 失败: {len(failed)}/{len(results)}")
    print(f"⏱️  平均响应时间: {avg_time:.2f}秒")
    print(f"⏱️  总耗时: {total_time/60:.1f}分钟")
    
    if categories:
        print(f"\n按类别统计:")
        for cat, times in sorted(categories.items()):
            avg = sum(times) / len(times)
            print(f"  {cat}: {len(times)}个, 平均 {avg:.2f}秒")
    
    if failed:
        print(f"\n❌ 失败的问题:")
        for r in failed:
            print(f"  [{r['id']}] {r['question'][:50]}... - {r['result'].get('error', 'Unknown')}")
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_results/test_set3_multimodal_{timestamp}.json"
    
    os.makedirs("test_results", exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "total_questions": len(TEST_SET_3_MULTIMODAL),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful)/len(results)*100 if results else 0,
            "avg_response_time": avg_time,
            "total_time_minutes": total_time/60,
            "model": "Doubao Seed-1-6-251015",
            "note": "多模态图片问题测试（OCR + Vision Analysis）",
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 详细结果已保存到: {output_file}")
    print("\n✅ Test Set 3 多模态测试完成！")


if __name__ == "__main__":
    main()

