"""
API Key诊断脚本 - 检查HKGAI和Gemini API是否可用
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from services.core.config import settings
from services.core.logger import logger
import requests


def test_hkgai_api():
    """测试HKGAI API是否可用"""
    logger.info("\n" + "="*80)
    logger.info("🔍 测试HKGAI API")
    logger.info("="*80)
    
    logger.info(f"📍 Base URL: {settings.HKGAI_BASE_URL}")
    logger.info(f"🔑 API Key: {settings.HKGAI_API_KEY[:20]}...")
    logger.info(f"🤖 Model ID: {settings.HKGAI_MODEL_ID}")
    
    endpoint = f"{settings.HKGAI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.HKGAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": settings.HKGAI_MODEL_ID,
        "messages": [
            {"role": "user", "content": "Hello, this is a test message. Please reply with 'OK'."}
        ],
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    try:
        logger.info("📤 发送测试请求...")
        response = requests.post(endpoint, headers=headers, json=payload, timeout=15)
        
        logger.info(f"📥 收到响应: 状态码 {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            logger.info(f"✅ HKGAI API 正常工作!")
            logger.info(f"📝 响应内容: {content}")
            return True
        elif response.status_code == 401:
            logger.error("❌ HKGAI API Key 无效或已过期 (401 Unauthorized)")
            logger.error(f"   响应: {response.text[:200]}")
            return False
        else:
            logger.error(f"❌ HKGAI API 返回错误: {response.status_code}")
            logger.error(f"   响应: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("❌ HKGAI API 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("❌ 无法连接到HKGAI API")
        return False
    except Exception as e:
        logger.error(f"❌ HKGAI API 测试失败: {e}")
        return False


def test_gemini_api():
    """测试Gemini API是否可用"""
    logger.info("\n" + "="*80)
    logger.info("🔍 测试Gemini API")
    logger.info("="*80)
    
    logger.info(f"🔑 API Key: {settings.GEMINI_API_KEY[:20]}...")
    logger.info(f"🤖 默认模型: {settings.GEMINI_DEFAULT_MODEL}")
    logger.info(f"🎚️  启用状态: {settings.GEMINI_ENABLED}")
    
    if not settings.GEMINI_ENABLED:
        logger.warning("⚠️  Gemini API 未启用")
        return False
    
    # 使用REST API测试（不需要安装google.generativeai）
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_DEFAULT_MODEL}:generateContent"
    params = {"key": settings.GEMINI_API_KEY}
    payload = {
        "contents": [{
            "parts": [{"text": "Hello, this is a test. Please reply with 'OK'."}]
        }],
        "generationConfig": {
            "maxOutputTokens": 10,
            "temperature": 0.1
        }
    }
    
    try:
        logger.info("📤 发送测试请求...")
        response = requests.post(url, params=params, json=payload, timeout=15)
        
        logger.info(f"📥 收到响应: 状态码 {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            logger.info(f"✅ Gemini API 正常工作!")
            logger.info(f"📝 响应内容: {content}")
            return True
        elif response.status_code == 400:
            logger.error("❌ Gemini API Key 无效或模型名称错误 (400 Bad Request)")
            logger.error(f"   响应: {response.text[:200]}")
            return False
        elif response.status_code == 403:
            logger.error("❌ Gemini API 权限不足或配额用尽 (403 Forbidden)")
            logger.error(f"   响应: {response.text[:200]}")
            return False
        else:
            logger.error(f"❌ Gemini API 返回错误: {response.status_code}")
            logger.error(f"   响应: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("❌ Gemini API 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("❌ 无法连接到Gemini API")
        return False
    except Exception as e:
        logger.error(f"❌ Gemini API 测试失败: {e}")
        return False


def print_fix_guide(hkgai_ok: bool, gemini_ok: bool):
    """打印修复指南"""
    logger.info("\n" + "="*80)
    logger.info("🔧 修复建议")
    logger.info("="*80)
    
    if not hkgai_ok and not gemini_ok:
        logger.error("❌ 两个API都不可用！")
        logger.info("\n请执行以下步骤:")
        logger.info("1. 检查 .env 文件中的 HKGAI_API_KEY 是否正确")
        logger.info("2. 检查 .env 文件中的 GEMINI_API_KEY 是否正确")
        logger.info("3. 确保API keys没有过期")
        logger.info("4. 检查网络连接")
        
    elif not hkgai_ok:
        logger.warning("⚠️  HKGAI API 不可用，但Gemini API 正常")
        logger.info("\n临时解决方案:")
        logger.info("1. 在 .env 文件中更新或删除 HKGAI_API_KEY")
        logger.info("2. 系统将自动使用Gemini API作为fallback")
        logger.info("\n永久解决方案:")
        logger.info("1. 获取新的HKGAI API key")
        logger.info("2. 更新 .env 文件: HKGAI_API_KEY=your-new-key")
        
    elif not gemini_ok:
        logger.info("✅ HKGAI API 正常，系统可以正常工作")
        logger.info("💡 建议也配置Gemini API作为备用")
        
    else:
        logger.info("✅ 两个API都正常工作！")
        logger.info("🎉 系统完全就绪")
    
    logger.info("\n" + "="*80)
    logger.info("📝 .env 文件位置: /Users/anonymity/Desktop/MAIE/MAIE5221 NLP/Final/.env")
    logger.info("="*80 + "\n")


if __name__ == "__main__":
    logger.info("\n🚀 开始API Key诊断\n")
    
    hkgai_ok = test_hkgai_api()
    gemini_ok = test_gemini_api()
    
    print_fix_guide(hkgai_ok, gemini_ok)
    
    # 返回退出码
    if hkgai_ok or gemini_ok:
        logger.info("✅ 至少有一个API可用，系统可以运行")
        sys.exit(0)
    else:
        logger.error("❌ 没有可用的API，请修复后再试")
        sys.exit(1)

