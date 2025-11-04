#!/usr/bin/env python3
"""
快速内存检查 - 只测试已安装的模型
"""
import sys
import os
import gc
import psutil

def get_memory_usage():
    """获取当前进程内存使用（MB）"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def test_installed_models():
    """测试已安装的模型"""
    print("=" * 80)
    print("🧪 内存占用测试 - 只测试已安装的模型")
    print("=" * 80)
    
    initial_memory = get_memory_usage()
    print(f"\n📊 初始内存占用: {initial_memory:.2f} MB\n")
    
    results = {}
    
    # 测试1: 标准Whisper (medium)
    print("-" * 80)
    print("测试1: 标准Whisper (medium模型)")
    print("-" * 80)
    try:
        import whisper
        
        before = get_memory_usage()
        print(f"  加载前: {before:.2f} MB")
        
        print("  正在加载模型（这可能需要几分钟）...")
        model = whisper.load_model("medium")
        
        after = get_memory_usage()
        increase = after - before
        
        results['whisper_medium'] = {'memory': after, 'increase': increase}
        
        print(f"  加载后: {after:.2f} MB")
        print(f"  增加: +{increase:.2f} MB ✅")
        
        del model
        gc.collect()
        
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        results['whisper_medium'] = {'error': str(e)}
    
    # 测试2: 检查Faster Whisper
    print("\n" + "-" * 80)
    print("测试2: Faster Whisper (检查是否安装)")
    print("-" * 80)
    try:
        from faster_whisper import WhisperModel
        
        before = get_memory_usage()
        print(f"  加载前: {before:.2f} MB")
        print("  正在加载模型...")
        
        model = WhisperModel("base", device="cpu", compute_type="int8")
        
        after = get_memory_usage()
        increase = after - before
        
        results['faster_whisper_base'] = {'memory': after, 'increase': increase}
        
        print(f"  加载后: {after:.2f} MB")
        print(f"  增加: +{increase:.2f} MB ✅")
        
        del model
        gc.collect()
        
    except ImportError:
        print("  ⚠️  未安装 Faster Whisper")
        print("  安装: pip install faster-whisper")
        results['faster_whisper'] = {'error': 'not_installed'}
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        results['faster_whisper'] = {'error': str(e)}
    
    # 测试3: 检查MLX相关
    print("\n" + "-" * 80)
    print("测试3: MLX框架检查（Mac优化）")
    print("-" * 80)
    try:
        import mlx.core as mx
        print("  ✅ MLX已安装")
        
        # 测试MLX LM
        try:
            from mlx_lm import load
            print("  ✅ MLX LM已安装")
            
            before = get_memory_usage()
            print(f"  加载前: {before:.2f} MB")
            print("  正在加载4bit量化模型...")
            
            model, tokenizer = load("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit")
            
            after = get_memory_usage()
            increase = after - before
            
            results['mlx_lm_4bit'] = {'memory': after, 'increase': increase}
            
            print(f"  加载后: {after:.2f} MB")
            print(f"  增加: +{increase:.2f} MB ✅ (4bit量化，内存占用低)")
            
            del model, tokenizer
            gc.collect()
            
        except ImportError:
            print("  ⚠️  MLX LM未安装")
            print("  安装: pip install mlx-lm")
        except Exception as e:
            print(f"  ⚠️  MLX LM加载失败: {e}")
            
    except ImportError:
        print("  ⚠️  MLX未安装（Mac用户需要）")
        print("  安装: pip install mlx")
        results['mlx'] = {'error': 'not_installed'}
    
    # 测试4: 检查TTS
    print("\n" + "-" * 80)
    print("测试4: TTS模型检查")
    print("-" * 80)
    
    # Edge TTS（应该已安装）
    try:
        import edge_tts
        print("  ✅ Edge TTS已安装（无需加载模型，内存占用低）")
        results['edge_tts'] = {'memory': get_memory_usage(), 'increase': 0}
    except ImportError:
        print("  ⚠️  Edge TTS未安装")
    
    # Parler-TTS
    try:
        from parler_tts import ParlerTTSForConditionalGeneration
        from transformers import AutoProcessor
        
        before = get_memory_usage()
        print(f"  加载前: {before:.2f} MB")
        print("  正在加载Parler-TTS...")
        
        processor = AutoProcessor.from_pretrained("parler-tts/parler-tts-mini-v2")
        model = ParlerTTSForConditionalGeneration.from_pretrained("parler-tts/parler-tts-mini-v2")
        model.eval()
        
        after = get_memory_usage()
        increase = after - before
        
        results['parler_tts'] = {'memory': after, 'increase': increase}
        
        print(f"  加载后: {after:.2f} MB")
        print(f"  增加: +{increase:.2f} MB ✅")
        
        del model, processor
        gc.collect()
        
    except ImportError:
        print("  ⚠️  Parler-TTS未安装")
        print("  安装: pip install parler-tts")
    except Exception as e:
        print(f"  ⚠️  Parler-TTS加载失败: {e}")
    
    # 汇总
    final_memory = get_memory_usage()
    
    print("\n" + "=" * 80)
    print("📊 内存占用汇总")
    print("=" * 80)
    
    print(f"\n{'模型':<30} {'内存占用(MB)':<18} {'增加(MB)':<15}")
    print("-" * 80)
    
    for name, data in results.items():
        if 'error' in data:
            print(f"{name:<30} {'N/A':<18} {'N/A':<15}")
        else:
            memory = data.get('memory', 0)
            increase = data.get('increase', 0)
            print(f"{name:<30} {memory:<18.2f} {increase:<15.2f}")
    
    print(f"\n初始内存: {initial_memory:.2f} MB")
    print(f"最终内存: {final_memory:.2f} MB")
    print(f"总增加: {final_memory - initial_memory:.2f} MB")
    
    # 分析和建议
    print("\n" + "=" * 80)
    print("💡 内存分析")
    print("=" * 80)
    
    increases = [r.get('increase', 0) for r in results.values() if 'error' not in r]
    if increases:
        max_increase = max(increases)
        total_increase = sum(increases)
        
        print(f"\n单个模型最大增加: {max_increase:.2f} MB")
        print(f"所有模型总增加: {total_increase:.2f} MB")
        
        if max_increase < 500:
            print("\n✅ 内存占用较低，可以正常使用")
            print("   建议: 可以同时加载多个模型")
        elif max_increase < 1000:
            print("\n⚠️  内存占用中等")
            print("   建议: 使用较小的模型或MLX优化")
        else:
            print("\n⚠️  内存占用较高")
            print("   建议:")
            print("   - 使用MLX优化（Mac用户，内存占用更低）")
            print("   - 使用量化模型（4bit/8bit）")
            print("   - 按需加载模型（不使用时卸载）")
    
    print("\n" + "=" * 80)
    print("💡 优化建议")
    print("=" * 80)
    
    print("\n1. Mac用户（推荐）:")
    print("   - 使用MLX优化: USE_MLX=true")
    print("   - MLX LM 4bit模型: 内存占用更低")
    print("   - Lightning Whisper MLX: 比标准Whisper占用更少")
    
    print("\n2. 所有用户:")
    print("   - 使用base模型而不是medium/large")
    print("   - 使用Faster Whisper（int8量化）")
    print("   - Edge TTS（无需加载模型，内存占用最低）")
    
    print("\n3. 流式处理:")
    print("   - 流式STT/TTS不会额外增加内存占用")
    print("   - 只是处理方式不同，模型内存占用相同")
    
    return results


if __name__ == "__main__":
    try:
        import psutil
    except ImportError:
        print("❌ 需要安装psutil: pip install psutil")
        sys.exit(1)
    
    try:
        test_installed_models()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

