#!/usr/bin/env python3
"""
内存占用测试 - 流式STT/TTS和MLX优化
测试不同模型加载时的内存占用情况
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import psutil
import gc
from services.core.logger import logger
from services.core.config import settings


def get_memory_usage():
    """获取当前进程内存使用（MB）"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # 转换为MB


def test_memory_usage():
    """测试内存占用"""
    print("=" * 80)
    print("🧪 流式STT/TTS内存占用测试")
    print("=" * 80)
    
    # 初始内存
    initial_memory = get_memory_usage()
    print(f"\n📊 初始内存占用: {initial_memory:.2f} MB")
    
    results = {}
    
    # 测试1: 标准Whisper
    print("\n" + "-" * 80)
    print("测试1: 标准Whisper模型")
    print("-" * 80)
    try:
        from services.speech.whisper_stt import get_whisper_stt
        
        before_memory = get_memory_usage()
        stt = get_whisper_stt(model_size=settings.WHISPER_MODEL_SIZE)
        after_memory = get_memory_usage()
        
        memory_increase = after_memory - before_memory
        results['whisper'] = {
            'memory': after_memory,
            'increase': memory_increase,
            'available': stt.is_available() if stt else False
        }
        
        print(f"  内存占用: {after_memory:.2f} MB (+{memory_increase:.2f} MB)")
        print(f"  状态: {'✅ 可用' if stt and stt.is_available() else '❌ 不可用'}")
        
        # 清理
        del stt
        gc.collect()
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        results['whisper'] = {'error': str(e)}
    
    # 测试2: 流式STT (Faster Whisper)
    print("\n" + "-" * 80)
    print("测试2: 流式STT (Faster Whisper)")
    print("-" * 80)
    try:
        from services.speech.streaming_stt import get_streaming_stt
        
        before_memory = get_memory_usage()
        streaming_stt = get_streaming_stt(
            model_size=settings.WHISPER_MODEL_SIZE,
            use_mlx=False,
            device="cpu"
        )
        after_memory = get_memory_usage()
        
        memory_increase = after_memory - before_memory
        results['streaming_stt'] = {
            'memory': after_memory,
            'increase': memory_increase,
            'available': streaming_stt.is_available() if streaming_stt else False
        }
        
        print(f"  内存占用: {after_memory:.2f} MB (+{memory_increase:.2f} MB)")
        print(f"  状态: {'✅ 可用' if streaming_stt and streaming_stt.is_available() else '❌ 不可用'}")
        
        # 清理
        del streaming_stt
        gc.collect()
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        results['streaming_stt'] = {'error': str(e)}
    
    # 测试3: 流式STT (Lightning Whisper MLX) - 仅Mac
    if settings.USE_MLX:
        print("\n" + "-" * 80)
        print("测试3: 流式STT (Lightning Whisper MLX) - Mac优化")
        print("-" * 80)
        try:
            from services.speech.streaming_stt import get_streaming_stt
            
            before_memory = get_memory_usage()
            mlx_stt = get_streaming_stt(
                model_size=settings.MLX_STT_MODEL,
                use_mlx=True,
                device="mps"
            )
            after_memory = get_memory_usage()
            
            memory_increase = after_memory - before_memory
            results['mlx_stt'] = {
                'memory': after_memory,
                'increase': memory_increase,
                'available': mlx_stt.is_available() if mlx_stt else False
            }
            
            print(f"  内存占用: {after_memory:.2f} MB (+{memory_increase:.2f} MB)")
            print(f"  状态: {'✅ 可用' if mlx_stt and mlx_stt.is_available() else '❌ 不可用'}")
            
            # 清理
            del mlx_stt
            gc.collect()
            
        except Exception as e:
            print(f"  ⚠️  测试跳过: {e} (可能不是Mac或MLX未安装)")
            results['mlx_stt'] = {'error': str(e)}
    
    # 测试4: 流式TTS (Parler-TTS)
    print("\n" + "-" * 80)
    print("测试4: 流式TTS (Parler-TTS)")
    print("-" * 80)
    try:
        from services.speech.streaming_tts import get_streaming_tts
        
        before_memory = get_memory_usage()
        parler_tts = get_streaming_tts(tts_type="parler", device="cpu")
        after_memory = get_memory_usage()
        
        memory_increase = after_memory - before_memory
        results['parler_tts'] = {
            'memory': after_memory,
            'increase': memory_increase,
            'available': parler_tts.is_available() if parler_tts else False
        }
        
        print(f"  内存占用: {after_memory:.2f} MB (+{memory_increase:.2f} MB)")
        print(f"  状态: {'✅ 可用' if parler_tts and parler_tts.is_available() else '❌ 不可用'}")
        
        # 清理
        del parler_tts
        gc.collect()
        
    except Exception as e:
        print(f"  ⚠️  测试跳过: {e} (Parler-TTS可能未安装)")
        results['parler_tts'] = {'error': str(e)}
    
    # 测试5: 流式TTS (MeloTTS)
    print("\n" + "-" * 80)
    print("测试5: 流式TTS (MeloTTS)")
    print("-" * 80)
    try:
        from services.speech.streaming_tts import get_streaming_tts
        
        before_memory = get_memory_usage()
        melo_tts = get_streaming_tts(tts_type="melo", device="cpu")
        after_memory = get_memory_usage()
        
        memory_increase = after_memory - before_memory
        results['melo_tts'] = {
            'memory': after_memory,
            'increase': memory_increase,
            'available': melo_tts.is_available() if melo_tts else False
        }
        
        print(f"  内存占用: {after_memory:.2f} MB (+{memory_increase:.2f} MB)")
        print(f"  状态: {'✅ 可用' if melo_tts and melo_tts.is_available() else '❌ 不可用'}")
        
        # 清理
        del melo_tts
        gc.collect()
        
    except Exception as e:
        print(f"  ⚠️  测试跳过: {e} (MeloTTS可能未安装)")
        results['melo_tts'] = {'error': str(e)}
    
    # 测试6: MLX LM (仅Mac)
    if settings.USE_MLX:
        print("\n" + "-" * 80)
        print("测试6: MLX LM (Mac优化)")
        print("-" * 80)
        try:
            from services.llm.mlx_lm_client import get_mlx_lm
            
            before_memory = get_memory_usage()
            mlx_lm = get_mlx_lm(model_name=settings.MLX_LM_MODEL)
            after_memory = get_memory_usage()
            
            memory_increase = after_memory - before_memory
            results['mlx_lm'] = {
                'memory': after_memory,
                'increase': memory_increase,
                'available': mlx_lm.is_available() if mlx_lm else False
            }
            
            print(f"  内存占用: {after_memory:.2f} MB (+{memory_increase:.2f} MB)")
            print(f"  状态: {'✅ 可用' if mlx_lm and mlx_lm.is_available() else '❌ 不可用'}")
            
            # 清理
            del mlx_lm
            gc.collect()
            
        except Exception as e:
            print(f"  ⚠️  测试跳过: {e} (MLX LM可能未安装)")
            results['mlx_lm'] = {'error': str(e)}
    
    # 测试7: 同时加载所有组件（模拟实际使用）
    print("\n" + "-" * 80)
    print("测试7: 同时加载所有组件（实际使用场景）")
    print("-" * 80)
    
    before_memory = get_memory_usage()
    
    # 加载所有可用组件
    components = {}
    
    try:
        from services.speech.whisper_stt import get_whisper_stt
        components['stt'] = get_whisper_stt()
    except:
        pass
    
    try:
        from services.speech.streaming_stt import get_streaming_stt
        components['streaming_stt'] = get_streaming_stt(use_mlx=False, device="cpu")
    except:
        pass
    
    try:
        from services.speech.streaming_tts import get_streaming_tts
        components['streaming_tts'] = get_streaming_tts(tts_type="parler", device="cpu")
    except:
        pass
    
    after_memory = get_memory_usage()
    total_increase = after_memory - before_memory
    
    results['all_components'] = {
        'memory': after_memory,
        'increase': total_increase,
        'components_loaded': len(components)
    }
    
    print(f"  加载组件数: {len(components)}")
    print(f"  总内存占用: {after_memory:.2f} MB (+{total_increase:.2f} MB)")
    
    # 清理
    for component in components.values():
        del component
    gc.collect()
    
    # 最终内存
    final_memory = get_memory_usage()
    print(f"\n📊 最终内存占用: {final_memory:.2f} MB")
    print(f"   总增加: {final_memory - initial_memory:.2f} MB")
    
    # 汇总结果
    print("\n" + "=" * 80)
    print("📊 内存占用汇总")
    print("=" * 80)
    
    print(f"\n{'模型':<25} {'内存占用(MB)':<15} {'增加(MB)':<15} {'状态':<10}")
    print("-" * 80)
    
    for name, data in results.items():
        if 'error' in data:
            print(f"{name:<25} {'N/A':<15} {'N/A':<15} {'❌ 错误':<10}")
        else:
            memory = data.get('memory', 0)
            increase = data.get('increase', 0)
            available = data.get('available', False)
            status = "✅ 可用" if available else "❌ 不可用"
            print(f"{name:<25} {memory:<15.2f} {increase:<15.2f} {status:<10}")
    
    # 建议
    print("\n" + "=" * 80)
    print("💡 内存优化建议")
    print("=" * 80)
    
    max_memory = max([r.get('memory', 0) for r in results.values() if 'error' not in r], default=0)
    
    if max_memory < 1000:
        print("✅ 内存占用较低，可以正常使用")
    elif max_memory < 2000:
        print("⚠️  内存占用中等，建议：")
        print("   - 使用较小的模型（tiny/base）")
        print("   - 启用MLX优化（Mac用户）")
        print("   - 避免同时加载多个模型")
    else:
        print("⚠️  内存占用较高，建议：")
        print("   - 使用MLX优化（Mac用户，内存占用更低）")
        print("   - 使用量化模型（4bit/8bit）")
        print("   - 按需加载模型（不使用时卸载）")
        print("   - 考虑使用更小的模型")
    
    if settings.USE_MLX:
        print("\n💡 Mac用户建议使用MLX优化，内存占用更低")
    
    return results


if __name__ == "__main__":
    try:
        import psutil
    except ImportError:
        print("❌ 需要安装psutil: pip install psutil")
        sys.exit(1)
    
    try:
        test_memory_usage()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

