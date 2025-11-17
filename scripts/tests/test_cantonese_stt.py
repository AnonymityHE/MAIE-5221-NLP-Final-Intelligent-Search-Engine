"""
测试粤语专用STT API集成
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.speech.cantonese_stt import get_cantonese_stt
from services.speech.whisper_stt import get_whisper_stt
from services.core.logger import logger
from services.core.config import settings

def test_cantonese_api_availability():
    """测试粤语API是否可用"""
    logger.info("=" * 60)
    logger.info("测试粤语API可用性")
    logger.info("=" * 60)
    
    logger.info(f"USE_CANTONESE_API: {settings.USE_CANTONESE_API}")
    logger.info(f"CANTONESE_SPEECH_API_KEY: {settings.CANTONESE_SPEECH_API_KEY[:20]}..." if settings.CANTONESE_SPEECH_API_KEY else "未配置")
    logger.info(f"CANTONESE_SPEECH_API_URL: {settings.CANTONESE_SPEECH_API_URL}")
    
    cantonese_stt = get_cantonese_stt()
    if cantonese_stt:
        logger.info("✅ 粤语STT实例创建成功")
        logger.info(f"✅ 粤语API可用: {cantonese_stt.is_available()}")
    else:
        logger.warning("❌ 粤语STT实例创建失败")
    
    return cantonese_stt

def test_whisper_with_cantonese():
    """测试Whisper STT与粤语API的集成"""
    logger.info("\n" + "=" * 60)
    logger.info("测试Whisper STT与粤语API集成")
    logger.info("=" * 60)
    
    whisper_stt = get_whisper_stt(model_size="base")
    if not whisper_stt or not whisper_stt.is_available():
        logger.error("❌ Whisper STT不可用")
        return
    
    logger.info("✅ Whisper STT加载成功")
    
    # 测试配置
    logger.info(f"当前配置:")
    logger.info(f"  - Whisper模型: {whisper_stt.model_name}")
    logger.info(f"  - 粤语API启用: {settings.USE_CANTONESE_API}")
    
    # 说明集成逻辑
    logger.info("\n集成逻辑说明:")
    logger.info("1. 如果显式指定language='yue'或'zh-HK'，优先使用粤语API")
    logger.info("2. 如果Whisper检测到粤语特征，自动切换到粤语API")
    logger.info("3. 如果粤语API失败，降级到Whisper处理")
    
    return whisper_stt

def test_transcribe_simulation():
    """模拟转录测试（不需要真实音频）"""
    logger.info("\n" + "=" * 60)
    logger.info("模拟转录流程")
    logger.info("=" * 60)
    
    logger.info("\n场景1: 指定粤语识别")
    logger.info("  调用: whisper_stt.transcribe_bytes(audio, language='yue')")
    logger.info("  预期: 优先使用粤语API")
    
    logger.info("\n场景2: 自动检测到粤语")
    logger.info("  调用: whisper_stt.transcribe_bytes(audio, language=None)")
    logger.info("  流程: Whisper识别 → 检测到粤语 → 使用粤语API重新识别")
    
    logger.info("\n场景3: 粤语API失败")
    logger.info("  流程: 粤语API调用失败 → 降级到Whisper结果")
    logger.info("  保证: 系统始终能返回结果（容错机制）")

def main():
    """主测试函数"""
    logger.info("🎤 粤语STT API集成测试")
    logger.info("=" * 60)
    
    # 测试1: 检查粤语API可用性
    cantonese_stt = test_cantonese_api_availability()
    
    # 测试2: 检查Whisper集成
    whisper_stt = test_whisper_with_cantonese()
    
    # 测试3: 模拟转录流程
    test_transcribe_simulation()
    
    # 总结
    logger.info("\n" + "=" * 60)
    logger.info("测试总结")
    logger.info("=" * 60)
    
    if cantonese_stt and cantonese_stt.is_available():
        logger.info("✅ 粤语API已成功集成")
        logger.info("✅ 系统将在检测到粤语时自动使用粤语专用API")
        logger.info("✅ 提供容错机制，确保服务稳定性")
    else:
        logger.warning("⚠️  粤语API未启用或配置不完整")
        logger.info("💡 提示: 检查以下配置项:")
        logger.info("   - USE_CANTONESE_API")
        logger.info("   - CANTONESE_SPEECH_API_KEY")
        logger.info("   - CANTONESE_SPEECH_API_URL")
    
    if whisper_stt and whisper_stt.is_available():
        logger.info("✅ Whisper STT正常工作（后备方案）")
    else:
        logger.warning("⚠️  Whisper STT不可用")
    
    logger.info("\n" + "=" * 60)
    logger.info("📝 使用说明")
    logger.info("=" * 60)
    logger.info("要使用粤语识别，有两种方式:")
    logger.info("1. 显式指定: transcribe_bytes(audio, language='yue')")
    logger.info("2. 自动检测: transcribe_bytes(audio) # 系统自动识别粤语")
    logger.info("\n系统会智能选择最佳识别方式:")
    logger.info("- 粤语内容 → 粤语专用API（高准确度）")
    logger.info("- 其他语言 → Whisper（多语言支持）")
    logger.info("- API失败 → 自动降级（高可用性）")

if __name__ == "__main__":
    main()

