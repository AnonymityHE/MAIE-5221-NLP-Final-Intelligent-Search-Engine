#!/usr/bin/env python3
"""
内存占用测试 - 流式STT/TTS和MLX优化（简化版）
直接测试模型加载，避免导入整个服务
"""
import sys
import os
import gc
import psutil

def get_memory_usage():
    """获取当前进程内存使用（MB）"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # 转换为MB


def test_whisper_memory():
    """测试标准Whisper内存占用"""
    print("=" * 80)
    print("🧪 内存占用测试 - 流式STT/TTS和MLX优化")
    print("=" * 80)
    
    initial_memory = get_memory_usage()
    print(f"\n📊 初始内存占用: {initial_memory:.2f} MB\n")
    
    results = {}
    
    # 测试1: 标准Whisper
    print("-" * 80)
    print("测试1: 标准Whisper (medium模型)")
    print("-" * 80)
    try:
        import whisper
        
        before_memory = get_memory_usage()
        print(f"  加载前: {before_memory:.2f} MB")
        
        model = whisper.load_model("medium")
        
        after_memory = get_memory_usage()
        memory_increase = after_memory - before_memory
        
        results['whisper_medium'] = {
            'memory': after_memory,
            'increase': memory_increase
        }
        
        print(f"  加载后: {after_memory:.2f} MB")
        print(f"  增加: +{memory_increase:.2f} MB")
        print(f"  ✅ 成功")
        
        del model
        gc.collect()
        
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        results['whisper_medium'] = {'error': str(e)}
    
    # 测试2: Faster Whisper
    print("\n" + "-" * 80)
    print("测试2: Faster Whisper (medium模型)")
    print("-" * 80)
    try:
        from faster_whisper import WhisperModel
        
        before_memory = get_memory_usage()
        print(f"  加载前: {before_memory:.2f} MB")
        
        model = WhisperModel("medium", device="cpu", compute_type="int8")
        
        after_memory = get_memory_usage()
        memory_increase = after_memory - before_memory
        
        results['faster_whisper_medium'] = {
            'memory': after_memory,
            'increase': memory_increase
        }
        
        print(f"  加载后: {after_memory:.2f} MB")
        print(f"  增加: +{memory_increase:.2f} MB")
        print(f"  ✅ 成功")
        
        del model
        gc.collect()
        
    except ImportError:
        print(f"  ⚠️  Faster Whisper未安装")
        print(f"  安装: pip install faster-whisper")
        results['faster_whisper_medium'] = {'error': 'not_installed'}
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        results['faster_whisper_medium'] = {'error': str(e)}
    
    # 测试3: Lightning Whisper MLX (Mac)
    print("\n" + "-" * 80)
    print("测试3: Lightning Whisper MLX (tiny模型, Mac优化)")
    print("-" * 80)
    try:
        from lightning_whisper_mlx import LightningWhisperMLX
        
        before_memory = get_memory_usage()
        print(f"  加载前: {before_memory:.2f} MB")
        
        model = LightningWhisperMLX(model_name="tiny", batch_size=1, quant=None)
        
        after_memory = get_memory_usage()
        memory_increase = after_memory - before_memory
        
        results['lightning_whisper_mlx'] = {
            'memory': after_memory,
            'increase': memory_increase
        }
        
        print(f"  加载后: {after_memory:.2f} MB")
        print(f"  增加: +{memory_increase:.2f} MB")
        print(f"  ✅ 成功 (Mac优化，内存占用更低)")
        
        del model
        gc.collect()
        
    except ImportError:
        print(f"  ⚠️  Lightning Whisper MLX未安装")
        print(f"  安装: pip install lightning-whisper-mlx")
        results['lightning_whisper_mlx'] = {'error': 'not_installed'}
    except Exception as e:
        print(f"  ⚠️  失败: {e}")
        results['lightning_whisper_mlx'] = {'error': str(e)}
    
    # 测试4: Parler-TTS
    print("\n" + "-" * 80)
    print("测试4: Parler-TTS (流式TTS)")
    print("-" * 80)
    try:
        from parler_tts import ParlerTTSForConditionalGeneration
        from transformers import AutoProcessor
        
        before_memory = get_memory_usage()
        print(f"  加载前: {before_memory:.2f} MB")
        
        model_id = "parler-tts/parler-tts-mini-v2"
        processor = AutoProcessor.from_pretrained(model_id)
        model = ParlerTTSForConditionalGeneration.from_pretrained(model_id)
        model.eval()
        
        after_memory = get_memory_usage()
        memory_increase = after_memory - before_memory
        
        results['parler_tts'] = {
            'memory': after_memory,
            'increase': memory_increase
        }
        
        print(f"  加载后: {after_memory:.2f} MB")
        print(f"  增加: +{memory_increase:.2f} MB")
        print(f"  ✅ 成功")
        
        del model, processor
        gc.collect()
        
    except ImportError:
        print(f"  ⚠️  Parler-TTS未安装")
        print(f"  安装: pip install parler-tts")
        results['parler_tts'] = {'error': 'not_installed'}
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        results['parler_tts'] = {'error': str(e)}
    
    # 测试5: MLX LM (Mac)
    print("\n" + "-" * 80)
    print("测试5: MLX LM (4bit量化模型, Mac优化)")
    print("-" * 80)
    try:
        from mlx_lm import load
        
        before_memory = get_memory_usage()
        print(f"  加载前: {before_memory:.2f} MB")
        
        model, tokenizer = load("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit")
        
        after_memory = get_memory_usage()
        memory_increase = after_memory - before_memory
        
        results['mlx_lm'] = {
            'memory': after_memory,
            'increase': memory_increase
        }
        
        print(f"  加载后: {after_memory:.2f} MB")
        print(f"  增加: +{memory_increase:.2f} MB")
        print(f"  ✅ 成功 (4bit量化，内存占用低)")
        
        del model, tokenizer
        gc.collect()
        
    except ImportError:
        print(f"  ⚠️  MLX LM未安装")
        print(f"  安装: pip install mlx mlx-lm")
        results['mlx_lm'] = {'error': 'not_installed'}
    except Exception as e:
        print(f"  ⚠️  失败: {e}")
        results['mlx_lm'] = {'error': str(e)}
    
    # 汇总
    final_memory = get_memory_usage()
    
    print("\n" + "=" * 80)
    print("📊 内存占用汇总")
    print("=" * 80)
    
    print(f"\n{'模型':<30} {'内存占用(MB)':<18} {'增加(MB)':<15} {'状态':<10}")
    print("-" * 80)
    
    for name, data in results.items():
        if 'error' in data:
            error = data['error']
            if error == 'not_installed':
                status = "⚠️  未安装"
            else:
                status = "❌ 错误"
            print(f"{name:<30} {'N/A':<18} {'N/A':<15} {status:<10}")
        else:
            memory = data.get('memory', 0)
            increase = data.get('increase', 0)
            print(f"{name:<30} {memory:<18.2f} {increase:<15.2f} {'✅':<10}")
    
    print(f"\n初始内存: {initial_memory:.2f} MB")
    print(f"最终内存: {final_memory:.2f} MB")
    print(f"总增加: {final_memory - initial_memory:.2f} MB")
    
    # 建议
    print("\n" + "=" * 80)
    print("💡 内存优化建议")
    print("=" * 80)
    
    max_increase = max([r.get('increase', 0) for r in results.values() if 'error' not in r], default=0)
    
    if max_increase < 500:
        print("✅ 内存占用较低，可以正常使用")
    elif max_increase < 1000:
        print("⚠️  内存占用中等，建议：")
        print("   - 使用较小的模型（tiny/base）")
        print("   - 启用MLX优化（Mac用户）")
    else:
        print("⚠️  内存占用较高，建议：")
        print("   - 使用MLX优化（Mac用户，内存占用更低）")
        print("   - 使用量化模型（4bit/8bit）")
        print("   - 使用更小的模型（tiny/base而不是medium/large）")
    
    # Mac优化提示
    mlx_available = 'lightning_whisper_mlx' in results and 'error' not in results.get('lightning_whisper_mlx', {})
    if mlx_available:
        print("\n💡 Mac用户建议：")
        print("   - 使用Lightning Whisper MLX（内存占用更低）")
        print("   - 使用MLX LM（4bit量化模型）")
        print("   - 在.env中设置 USE_MLX=true")
    
    return results


if __name__ == "__main__":
    try:
        import psutil
    except ImportError:
        print("❌ 需要安装psutil: pip install psutil")
        sys.exit(1)
    
    try:
        test_whisper_memory()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

