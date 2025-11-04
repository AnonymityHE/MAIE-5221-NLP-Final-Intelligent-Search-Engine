#!/usr/bin/env python3
"""
独立MLX优化测试 - 不依赖服务框架
直接测试MLX组件是否正常工作
"""
import sys
import os
import gc

def test_mlx_framework():
    """测试MLX框架"""
    print("=" * 80)
    print("🧪 测试1: MLX框架")
    print("=" * 80)
    
    try:
        import mlx.core as mx
        
        print("✅ MLX框架已安装")
        print(f"  版本: {mx.__version__ if hasattr(mx, '__version__') else '未知'}")
        
        # 简单测试
        arr = mx.array([1, 2, 3, 4, 5])
        result = mx.mean(arr)
        print(f"  测试计算: mean([1,2,3,4,5]) = {float(result)}")
        print("  ✅ MLX框架工作正常")
        
        return True
    except ImportError:
        print("❌ MLX框架未安装")
        print("  安装: pip install mlx")
        return False
    except Exception as e:
        print(f"❌ MLX框架测试失败: {e}")
        return False


def test_lightning_whisper_mlx():
    """测试Lightning Whisper MLX"""
    print("\n" + "=" * 80)
    print("🧪 测试2: Lightning Whisper MLX (STT)")
    print("=" * 80)
    
    try:
        from lightning_whisper_mlx import LightningWhisperMLX
        
        print("✅ Lightning Whisper MLX已安装")
        print("\n正在加载模型（tiny，快速测试）...")
        
        # 注意：参数是model而不是model_name
        model = LightningWhisperMLX(
            model="tiny",
            batch_size=1,
            quant=None
        )
        
        print("✅ Lightning Whisper MLX模型加载成功")
        print("  模型类型: Lightning Whisper MLX")
        print("  设备: MPS (Mac GPU)")
        
        del model
        gc.collect()
        
        return True
    except ImportError:
        print("❌ Lightning Whisper MLX未安装")
        print("  安装: pip install lightning-whisper-mlx")
        return False
    except Exception as e:
        print(f"❌ Lightning Whisper MLX测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mlx_lm():
    """测试MLX LM"""
    print("\n" + "=" * 80)
    print("🧪 测试3: MLX LM (语言模型)")
    print("=" * 80)
    
    try:
        from mlx_lm import load, generate
        
        print("✅ MLX LM已安装")
        print("\n正在加载4bit量化模型...")
        print("  模型: mlx-community/Meta-Llama-3.1-8B-Instruct-4bit")
        print("  注意: 首次加载会下载模型（约5GB）")
        
        model, tokenizer = load("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit")
        
        print("✅ MLX LM模型加载成功")
        
        # 测试生成
        print("\n测试文本生成...")
        prompt = "Hello, how are you?"
        response = generate(model, tokenizer, prompt=prompt, max_tokens=30, temp=0.7, verbose=False)
        
        print(f"✅ 生成成功")
        print(f"  提示: {prompt}")
        print(f"  回答: {response[:100]}...")
        
        del model, tokenizer
        gc.collect()
        
        return True
    except ImportError:
        print("❌ MLX LM未安装")
        print("  安装: pip install mlx-lm")
        return False
    except Exception as e:
        print(f"❌ MLX LM测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mlx_config():
    """测试配置文件"""
    print("\n" + "=" * 80)
    print("🧪 测试4: 配置文件检查")
    print("=" * 80)
    
    env_file = os.path.join(os.path.dirname(__file__), '../..', '.env')
    
    if os.path.exists(env_file):
        print(f"✅ .env文件存在: {env_file}")
        
        with open(env_file, 'r') as f:
            content = f.read()
        
        mlx_enabled = "USE_MLX=true" in content
        streaming_stt = "ENABLE_STREAMING_STT=true" in content
        streaming_tts = "ENABLE_STREAMING_TTS=true" in content
        
        print(f"\n配置检查:")
        print(f"  USE_MLX: {'✅ 已启用' if mlx_enabled else '❌ 未启用'}")
        print(f"  ENABLE_STREAMING_STT: {'✅ 已启用' if streaming_stt else '❌ 未启用'}")
        print(f"  ENABLE_STREAMING_TTS: {'✅ 已启用' if streaming_tts else '❌ 未启用'}")
        
        if mlx_enabled:
            print("\n✅ MLX优化已在配置中启用")
            return True
        else:
            print("\n⚠️  MLX优化未在配置中启用")
            print("  请在.env文件中添加: USE_MLX=true")
            return False
    else:
        print(f"⚠️  .env文件不存在: {env_file}")
        print("  将创建配置文件...")
        return None


def main():
    """主函数"""
    print("🚀 MLX优化功能测试（独立测试）\n")
    
    results = {}
    
    # 测试MLX框架
    results['mlx_framework'] = test_mlx_framework()
    
    # 测试Lightning Whisper MLX
    results['lightning_whisper'] = test_lightning_whisper_mlx()
    
    # 测试MLX LM
    results['mlx_lm'] = test_mlx_lm()
    
    # 测试配置
    results['config'] = test_mlx_config()
    
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
    print("💡 MLX优化使用指南")
    print("=" * 80)
    
    all_passed = all(r for r in results.values() if r is not None)
    
    if all_passed:
        print("\n✅ 所有MLX组件测试通过！")
        print("\n📝 配置说明:")
        print("  1. 确保.env文件中包含:")
        print("     USE_MLX=true")
        print("     MLX_STT_MODEL=base")
        print("     MLX_LM_MODEL=mlx-community/Meta-Llama-3.1-8B-Instruct-4bit")
        print("     ENABLE_STREAMING_STT=true")
        print("     ENABLE_STREAMING_TTS=true")
        print("\n  2. 重启服务使配置生效")
        print("\n  3. 系统将自动使用MLX优化:")
        print("     - Lightning Whisper MLX进行语音识别")
        print("     - MLX LM进行文本生成")
        print("     - 充分利用Apple Silicon性能")
    else:
        print("\n⚠️  部分组件测试失败")
        print("  请检查:")
        print("  1. MLX是否已安装: pip install mlx mlx-lm lightning-whisper-mlx")
        print("  2. .env文件配置是否正确")
        print("  3. 是否为Mac系统（MLX仅支持Mac）")
    
    print("\n💡 优势:")
    print("  - 内存占用更低（比标准模型低50-70%）")
    print("  - 速度更快（充分利用Apple Silicon）")
    print("  - 功耗更低")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

