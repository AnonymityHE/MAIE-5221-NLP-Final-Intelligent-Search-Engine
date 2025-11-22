#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
豆包多模态功能测试
测试图片+文本的查询能力
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import base64
import requests
from pathlib import Path


def encode_image_to_base64(image_path: str) -> str:
    """将图片编码为Base64"""
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    return base64.b64encode(image_bytes).decode('utf-8')


def test_doubao_multimodal_query(query: str, image_paths: list, test_name: str):
    """测试豆包多模态查询"""
    print(f"\n{'='*80}")
    print(f"测试: {test_name}")
    print(f"{'='*80}")
    print(f"问题: {query}")
    print(f"图片数量: {len(image_paths)}")
    
    # 编码图片
    images_base64 = []
    for img_path in image_paths:
        if not os.path.exists(img_path):
            print(f"❌ 图片不存在: {img_path}")
            return False
        images_base64.append(encode_image_to_base64(img_path))
        print(f"  ✅ 已加载: {os.path.basename(img_path)}")
    
    # 发送请求
    try:
        print(f"\n⏳ 正在发送请求（使用豆包）...")
        response = requests.post(
            'http://localhost:5555/api/multimodal/query',
            json={
                "query": query,
                "images": images_base64,
                "use_ocr": False,  # 先不做OCR，直接视觉理解
                "provider": "doubao",
                "model": "doubao-seed-1-6-251015"  # 使用标准版，不是lite
            },
            timeout=90
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ 查询成功！")
            print(f"\n📝 回答:")
            print(data.get('answer', ''))
            
            print(f"\n📊 统计:")
            print(f"  - 会话ID: {data.get('session_id', '')}")
            print(f"  - 处理图片: {data.get('images_processed', 0)}张")
            print(f"  - 使用模型: {data.get('model_used', '')}")
            print(f"  - Token使用: {data.get('tokens_used', {}).get('total', 0)}")
            
            # OCR结果
            ocr_results = data.get('ocr_results', [])
            if ocr_results:
                print(f"\n🔍 OCR识别:")
                for i, ocr in enumerate(ocr_results, 1):
                    print(f"  图片{i}: {len(ocr['text'])}字符 (置信度: {ocr['confidence']:.2f})")
                    if ocr['text']:
                        print(f"    预览: {ocr['text'][:100]}...")
            
            return True
            
        else:
            print(f"\n❌ 请求失败: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_doubao_ocr(image_path: str, test_name: str):
    """测试豆包OCR功能"""
    print(f"\n{'='*80}")
    print(f"OCR测试: {test_name}")
    print(f"{'='*80}")
    
    if not os.path.exists(image_path):
        print(f"❌ 图片不存在: {image_path}")
        return False
    
    # 编码图片
    image_base64 = encode_image_to_base64(image_path)
    print(f"✅ 已加载: {os.path.basename(image_path)}")
    
    # 发送请求
    try:
        print(f"\n⏳ 正在识别文字（使用豆包）...")
        response = requests.post(
            'http://localhost:5555/api/multimodal/ocr',
            json={
                "image": image_base64,
                "enhance": True,
                "provider": "doubao"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ OCR成功！")
            print(f"\n📝 识别文字:")
            print(data.get('text', ''))
            
            print(f"\n📊 统计:")
            print(f"  - 字符数: {data.get('char_count', 0)}")
            print(f"  - 置信度: {data.get('confidence', 0):.2f}")
            print(f"  - 语言: {data.get('language', 'auto')}")
            print(f"  - 模型: {data.get('model', '')}")
            
            return True
            
        else:
            print(f"\n❌ 请求失败: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        return False


def main():
    print("=" * 100)
    print("🖼️  豆包多模态功能测试")
    print("=" * 100)
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent.parent
    figures_dir = project_root / "figures"
    
    # Test Set 3 的测试用例
    test_cases = [
        {
            "name": "HKUST雕塑识别（中文）",
            "query": "识别这座雕塑，解释它的象征意义，并告诉我它具体位于校园的哪个位置。",
            "images": [str(figures_dir / "hkust.png")]
        },
        {
            "name": "HKUST雕塑识别（英文）",
            "query": "Identify this sculpture, explain its symbolic meaning, and tell me where exactly on campus it is located.",
            "images": [str(figures_dir / "hkust.png")]
        },
        {
            "name": "零食营养分析（中文）",
            "query": "这个零食适合低钠饮食的人吗？提取钠含量来支持你的回答。",
            "images": [str(figures_dir / "snack.png")]
        },
        {
            "name": "零食营养分析（英文）",
            "query": "Is this snack suitable for someone on a low-sodium diet? Extract the sodium content to justify your answer.",
            "images": [str(figures_dir / "snack.png")]
        },
        {
            "name": "代码错误分析（中文）",
            "query": "分析这个错误截图并建议修复此 Python 代码的方法。",
            "images": [str(figures_dir / "error_info.png")]
        },
        {
            "name": "代码错误分析（英文）",
            "query": "Analyze this error screenshot and suggest a fix for the Python code.",
            "images": [str(figures_dir / "error_info.png")]
        },
    ]
    
    # OCR测试
    ocr_tests = [
        {"name": "零食包装OCR", "image": str(figures_dir / "snack.png")},
        {"name": "错误日志OCR", "image": str(figures_dir / "error_info.png")}
    ]
    
    print(f"\n📋 将执行 {len(test_cases)} 个多模态测试 + {len(ocr_tests)} 个OCR测试")
    print(f"图片目录: {figures_dir}")
    
    # 检查图片是否存在
    if not figures_dir.exists():
        print(f"\n❌ 图片目录不存在: {figures_dir}")
        return
    
    required_images = ["hkust.png", "snack.png", "error_info.png"]
    for img in required_images:
        img_path = figures_dir / img
        if not img_path.exists():
            print(f"❌ 缺少图片: {img}")
            return
    
    print("\n✅ 所有图片就绪\n")
    
    # 执行测试
    results = []
    
    print("\n" + "="*100)
    print("🧪 第一部分：豆包多模态查询测试")
    print("="*100)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n\n{'#'*100}")
        print(f"进度: {i}/{len(test_cases)}")
        print(f"{'#'*100}")
        
        success = test_doubao_multimodal_query(
            query=test["query"],
            image_paths=test["images"],
            test_name=test["name"]
        )
        
        results.append({
            "name": test["name"],
            "type": "multimodal",
            "success": success
        })
        
        if i < len(test_cases):
            print("\n⏳ 等待3秒...")
            import time
            time.sleep(3)
    
    print("\n" + "="*100)
    print("🔍 第二部分：豆包OCR测试")
    print("="*100)
    
    for i, test in enumerate(ocr_tests, 1):
        print(f"\n\n{'#'*100}")
        print(f"进度: {i}/{len(ocr_tests)}")
        print(f"{'#'*100}")
        
        success = test_doubao_ocr(
            image_path=test["image"],
            test_name=test["name"]
        )
        
        results.append({
            "name": test["name"],
            "type": "ocr",
            "success": success
        })
        
        if i < len(ocr_tests):
            print("\n⏳ 等待2秒...")
            import time
            time.sleep(2)
    
    # 汇总
    print(f"\n\n{'='*100}")
    print("📊 测试总结")
    print(f"{'='*100}")
    
    multimodal_results = [r for r in results if r["type"] == "multimodal"]
    ocr_results = [r for r in results if r["type"] == "ocr"]
    
    multimodal_success = sum(1 for r in multimodal_results if r["success"])
    ocr_success = sum(1 for r in ocr_results if r["success"])
    
    print(f"\n多模态查询:")
    print(f"  总数: {len(multimodal_results)}")
    print(f"  成功: {multimodal_success}")
    print(f"  失败: {len(multimodal_results) - multimodal_success}")
    if multimodal_results:
        print(f"  成功率: {multimodal_success/len(multimodal_results)*100:.1f}%")
    
    print(f"\nOCR测试:")
    print(f"  总数: {len(ocr_results)}")
    print(f"  成功: {ocr_success}")
    print(f"  失败: {len(ocr_results) - ocr_success}")
    if ocr_results:
        print(f"  成功率: {ocr_success/len(ocr_results)*100:.1f}%")
    
    print(f"\n总体:")
    total_success = multimodal_success + ocr_success
    total_tests = len(results)
    print(f"  总测试数: {total_tests}")
    print(f"  总成功数: {total_success}")
    print(f"  总成功率: {total_success/total_tests*100:.1f}%")
    
    # 失败列表
    failed = [r for r in results if not r["success"]]
    if failed:
        print(f"\n❌ 失败的测试:")
        for r in failed:
            print(f"  - {r['name']} ({r['type']})")
    else:
        print(f"\n🎉 所有测试通过！豆包多模态集成成功！")
    
    print(f"\n{'='*100}")


if __name__ == "__main__":
    main()

