#!/usr/bin/env python3
"""
测试MLX优化功能
验证MLX STT和MLX LM是否正常工作
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.core.config import settings
from services.core.logger import logger


def test_mlx_stt():
    """测试MLX STT"""
    print("=" * 80)
    print("🧪 测试1: Lightning Whisper MLX")
    print("=" * 80)
    
    if not settings.USE_MLX:
        print("⚠️  MLX未启用，请在.env中设置 USE_MLX=true")
        return False
    
    try:
        from services.speech.streaming_stt import get_streaming_stt
        
        print(f"\n配置:")
        print(f"  模型大小: {settings.MLX_STT_MODEL}")
        print(f"  设备: mps (Mac GPU)")
        
        print("\n正在加载Lightning Whisper MLX...")
        stt = get_streaming_stt(
            model_size=settings.MLX_STT_MODEL,
            use_mlx=True,
            device="mps"
        )
        
        if stt and stt.is_available():
            print(f"✅ Lightning Whisper MLX加载成功")
            print(f"  模型类型: {stt.model_type}")
            return True
        else:
            print("❌ Lightning Whisper MLX加载失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mlx_lm():
    """测试MLX LM"""
    print("\n" + "=" * 80)
    print("🧪 测试2: MLX LM")
    print("=" * 80)
    
    if not settings.USE_MLX:
        print("⚠️  MLX未启用")
        return False
    
    try:
        from services.llm.mlx_lm_client import get_mlx_lm
        
        print(f"\n配置:")
        print(f"  模型: {settings.MLX_LM_MODEL}")
        
        print("\n正在加载MLX LM...")
        mlx_lm = get_mlx_lm(model_name=settings.MLX_LM_MODEL)
        
        if mlx_lm and mlx_lm.is_available():
            print("✅ MLX LM加载成功")
            
            # 测试生成
            print("\n测试文本生成...")
            prompt = "你好，请简单介绍一下你自己。"
            response = mlx_lm.generate(prompt, max_tokens=50, temperature=0.7)
            
            if response:
                print(f"✅ 生成成功")
                print(f"  提示: {prompt}")
                print(f"  回答: {response[:100]}...")
                return True
            else:
                print("❌ 生成失败")
                return False
        else:
            print("❌ MLX LM加载失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mlx_integration():
    """测试MLX集成"""
    print("\n" + "=" * 80)
    print("🧪 测试3: MLX集成检查")
    print("=" * 80)
    
    print("\n检查MLX组件:")
    
    # 检查MLX框架
    try:
        import mlx.core as mx
        print("  ✅ MLX框架: 已安装")
    except ImportError:
        print("  ❌ MLX框架: 未安装")
        return False
    
    # 检查MLX LM
    try:
        from mlx_lm import load
        print("  ✅ MLX LM: 已安装")
    except ImportError:
        print("  ❌ MLX LM: 未安装")
        print("    安装: pip install mlx-lm")
    
    # 检查Lightning Whisper MLX
    try:
        from lightning_whisper_mlx import LightningWhisperMLX
        print("  ✅ Lightning Whisper MLX: 已安装")
    except ImportError:
        print("  ❌ Lightning Whisper MLX: 未安装")
        print("    安装: pip install lightning-whisper-mlx")
    
    # 检查配置
    print(f"\n配置状态:")
    print(f"  USE_MLX: {settings.USE_MLX}")
    print(f"  ENABLE_STREAMING_STT: {settings.ENABLE_STREAMING_STT}")
    print(f"  ENABLE_STREAMING_TTS: {settings.ENABLE_STREAMING_TTS}")
    
    if settings.USE_MLX:
        print("\n✅ MLX优化已启用")
        return True
    else:
        print("\n⚠️  MLX优化未启用")
        print("  在.env中设置: USE_MLX=true")
        return False


def main():
    """主函数"""
    print("🚀 开始MLX优化功能测试\n")
    
    results = {}
    
    # 测试集成
    results['integration'] = test_mlx_integration()
    
    # 测试MLX STT
    if settings.USE_MLX:
        results['mlx_stt'] = test_mlx_stt()
    else:
        print("\n⚠️  跳过MLX STT测试（MLX未启用）")
        results['mlx_stt'] = None
    
    # 测试MLX LM
    if settings.USE_MLX:
        results['mlx_lm'] = test_mlx_lm()
    else:
        print("\n⚠️  跳过MLX LM测试（MLX未启用）")
        results['mlx_lm'] = None
    
    # 汇总
    print("\n" + "=" * 80)
    print("📊 测试结果汇总")
    print("=" * 80)
    
    print(f"\n{'测试项':<30} {'状态':<10}")
    print("-" * 80)
    
    for name, result in results.items():
        if result is True:
            status = "✅ 通过"
        elif result is False:
            status = "❌ 失败"
        else:
            status = "⚠️  跳过"
        print(f"{name:<30} {status:<10}")
    
    # 建议
    print("\n" + "=" * 80)
    print("💡 使用建议")
    print("=" * 80)
    
    if settings.USE_MLX:
        print("\n✅ MLX优化已启用，系统将：")
        print("  1. 使用Lightning Whisper MLX进行语音识别（Mac优化）")
        print("  2. 使用MLX LM进行文本生成（4bit量化，内存占用低）")
        print("  3. 充分利用Apple Silicon性能")
        print("\n📝 配置文件: .env")
        print("  USE_MLX=true")
        print(f"  MLX_STT_MODEL={settings.MLX_STT_MODEL}")
        print(f"  MLX_LM_MODEL={settings.MLX_LM_MODEL}")
    else:
        print("\n⚠️  MLX优化未启用")
        print("  要启用MLX优化，请在.env文件中添加：")
        print("  USE_MLX=true")
        print("  MLX_STT_MODEL=base")
        print("  MLX_LM_MODEL=mlx-community/Meta-Llama-3.1-8B-Instruct-4bit")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

