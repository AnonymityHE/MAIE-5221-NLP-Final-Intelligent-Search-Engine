# HKGAI Speech Services 集成总结

## 📊 API可用性分析

### ✅ 可以用于STT/ASR（语音转文字）

HKGAI提供**两个STT接口**，都可以使用你现有的API Key：

#### 1. 简单语音识别（推荐）⭐
```
POST https://openspeech.hkgai.net/api/v1/speech_recognize
```

**特点**：
- ✅ 快速、简单
- ✅ 适合实时语音输入
- ✅ 粤语友好（HKGAI是香港服务，应该对粤语有优化）
- ✅ 使用现有API Key即可

**认证方式**：
```
Authorization: TzmW5eWvGWphlubmavEIRtG5U6OwS9wF02AwtEHWx0stLvtqZWpz5LK2q7lRQhDY
```

#### 2. 会议转录（带说话人识别）
```
POST https://openspeech.hkgai.net/api/v1/transcription
```

**特点**：
- ✅ 区分不同说话人
- ✅ 提供时间戳
- ✅ 适合长音频、多人对话
- ✅ 使用同一个API Key

---

### ⚠️ TTS（文字转语音）需要JWT Token

```
GET https://openspeech.hkgai.net/server_proxy/api/tts
```

**问题**：
- ❌ 需要JWT Bearer Token（不是简单的API Key）
- ⚠️ 你现有的Key无法直接用于TTS
- 📝 文档中的示例使用了一个JWT token（以`eyJhbGciOiJ...`开头）

**TTS功能**（如果有JWT token）：
- ✅ 明确支持粤语：`language=cantonese`
- ✅ 支持普通话：`language=mandarin`
- ✅ 男声/女声选择

---

## 🎯 推荐集成方案

### 方案1：HKGAI STT + Whisper STT（双引擎）⭐

```python
# 粤语输入：优先使用HKGAI（粤语优化）
if detected_language == "yue" or user_prefers_cantonese:
    result = hkgai_speech_recognize(audio)
    if result.success and result.confidence > 0.8:
        return result
    else:
        # Fallback to Whisper
        return whisper_stt(audio)

# 其他语言：使用Whisper
else:
    result = whisper_stt(audio)
    return result
```

**优势**：
- 🟢 粤语识别更准确（HKGAI专门优化）
- 🟢 多语言支持（Whisper作为backup）
- 🟢 互为backup，提高可靠性

### 方案2：仅使用Whisper（当前方案）

```python
# 继续使用Whisper
result = whisper_stt(audio, language="yue")
```

**优势**：
- 🟢 完全离线
- 🟢 免费无限制
- 🟢 支持100+语言
- 🟡 粤语准确度可能略低

### 方案3：HKGAI作为主要引擎

```python
# 所有语音都先尝试HKGAI
try:
    result = hkgai_speech_recognize(audio)
    if result.success:
        return result
except:
    # Network error, fallback to Whisper
    return whisper_stt(audio)
```

**优势**：
- 🟢 云端计算，不占本地资源
- 🟢 可能有更好的持续更新
- 🔴 需要网络连接
- 🟡 可能有API调用限制

---

## 💡 具体实现建议

### 1. 添加HKGAI STT客户端

创建`services/speech/hkgai_stt_client.py`：

```python
import requests
import base64
import uuid
from typing import Dict, Optional

class HKGAISpeechClient:
    """HKGAI语音识别客户端（粤语优化）"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openspeech.hkgai.net"
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
    
    def recognize(self, audio_bytes: bytes) -> Dict:
        """
        语音识别
        
        Args:
            audio_bytes: 音频字节数据
            
        Returns:
            {
                "text": "识别文本",
                "success": True,
                "confidence": 0.95,
                "language": "zh"
            }
        """
        endpoint = f"{self.base_url}/api/v1/speech_recognize"
        
        # 转换为base64
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        payload = {
            "request_id": str(uuid.uuid4()),
            "resource": {
                "type": 2,  # BYTES
                "data": audio_b64
            }
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") == 200:
                result_text = data.get("data", {}).get("result", "")
                return {
                    "text": result_text,
                    "success": True,
                    "confidence": 0.95,  # HKGAI不返回置信度，给个默认值
                    "language": "zh",
                    "provider": "hkgai"
                }
            else:
                return {
                    "text": "",
                    "success": False,
                    "error": data.get("msg", "Unknown error"),
                    "provider": "hkgai"
                }
                
        except Exception as e:
            return {
                "text": "",
                "success": False,
                "error": str(e),
                "provider": "hkgai"
            }
    
    def recognize_with_speakers(self, audio_bytes: bytes) -> Dict:
        """会议转录（带说话人识别）"""
        endpoint = f"{self.base_url}/api/v1/transcription"
        
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        payload = {
            "request_id": str(uuid.uuid4()),
            "resource": {
                "type": 2,
                "data": audio_b64
            }
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=60  # 会议转录可能较慢
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") == 200:
                messages = data.get("data", {}).get("messages", [])
                return {
                    "messages": messages,
                    "success": True,
                    "provider": "hkgai"
                }
            else:
                return {
                    "messages": [],
                    "success": False,
                    "error": data.get("msg"),
                    "provider": "hkgai"
                }
                
        except Exception as e:
            return {
                "messages": [],
                "success": False,
                "error": str(e),
                "provider": "hkgai"
            }
```

### 2. 集成到现有语音服务

修改`services/speech/speech_service.py`：

```python
from services.speech.hkgai_stt_client import HKGAISpeechClient
from services.core.config import settings

class SpeechService:
    def __init__(self):
        self.whisper_model = load_whisper()
        
        # 初始化HKGAI STT（如果配置了）
        if settings.CANTONESE_SPEECH_API_KEY:
            self.hkgai_client = HKGAISpeechClient(
                settings.CANTONESE_SPEECH_API_KEY
            )
            logger.info("✅ HKGAI语音识别已启用（粤语优化）")
        else:
            self.hkgai_client = None
    
    def transcribe(self, audio_data: bytes, 
                   language: str = None,
                   prefer_cantonese: bool = False) -> Dict:
        """
        语音转文字
        
        Args:
            audio_data: 音频数据
            language: 指定语言（yue/zh/en）
            prefer_cantonese: 是否优先使用粤语引擎
        """
        
        # 粤语优先使用HKGAI
        if (prefer_cantonese or language == "yue") and self.hkgai_client:
            logger.info("🎤 使用HKGAI进行粤语识别...")
            result = self.hkgai_client.recognize(audio_data)
            
            if result["success"]:
                logger.info(f"✅ HKGAI识别成功: {result['text'][:50]}...")
                return result
            else:
                logger.warning(f"⚠️  HKGAI识别失败，fallback到Whisper: {result.get('error')}")
        
        # 使用Whisper
        logger.info("🎤 使用Whisper进行语音识别...")
        return self.whisper_transcribe(audio_data, language)
```

### 3. 配置文件更新

`.env`已配置：
```bash
# 粤语语音API配置 (HKGAI Speech Services)
CANTONESE_SPEECH_API_KEY=TzmW5eWvGWphlubmavEIRtG5U6OwS9wF02AwtEHWx0stLvtqZWpz5LK2q7lRQhDY
USE_CANTONESE_API=true
USE_HKGAI_STT_FOR_CANTONESE=true  # 新增：粤语优先使用HKGAI
```

---

## 📈 预期效果

### 粤语识别准确度提升

| 场景 | Whisper | HKGAI | 提升 |
|------|---------|-------|------|
| 标准粤语 | 85% | 95% | +10% |
| 粤语口音 | 75% | 90% | +15% |
| 粤语专有词汇 | 70% | 92% | +22% |
| 粤英混合 | 80% | 88% | +8% |

*(以上数据为预估，需实际测试验证)*

---

## ✅ 总结

### 可以用的功能：
1. ✅ **STT/ASR（语音转文字）** - 完全可用
2. ✅ **粤语友好** - HKGAI是香港服务，应该对粤语有特别优化
3. ✅ **说话人识别** - 支持会议转录场景
4. ✅ **使用现有API Key** - 无需额外申请

### 需要注意的：
1. ⚠️ TTS需要JWT token（暂时无法使用）
2. ⚠️ 需要网络连接（云端API）
3. ⚠️ 可能有调用次数/费用限制（需确认）

### 推荐行动：
1. 🔨 实现双引擎STT（HKGAI + Whisper）
2. 🧪 测试粤语识别准确度
3. 📊 对比性能和成本
4. 💡 可选：申请TTS的JWT token以支持粤语语音合成

---

**文档版本**: v1.0  
**最后更新**: 2025-11-20  
**下一步**: 实现HKGAI STT客户端并进行粤语测试

