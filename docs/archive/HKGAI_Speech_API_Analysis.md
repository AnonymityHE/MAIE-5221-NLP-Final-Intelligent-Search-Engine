# HKGAI Speech Services API 分析（粤语支持）

## 可用接口总结

### 1. 语音识别（STT/ASR）- 两个选项

#### 选项A：会议转录（带说话人识别）
- **端点**: `POST https://openspeech.hkgai.net/api/v1/transcription`
- **功能**: 
  - ✅ 自动语音识别（ASR）
  - ✅ 说话人区分（Speaker Diarization）
  - ✅ 多语言支持（返回language字段）
  - ✅ 时间戳标记
- **适用场景**: 会议、多人对话、长音频
- **粤语支持**: ⚠️ 文档未明确说明，但有language字段

#### 选项B：简单语音识别（推荐用于粤语）⭐
- **端点**: `POST https://openspeech.hkgai.net/api/v1/speech_recognize`
- **功能**:
  - ✅ 快速语音转文字
  - ✅ 单一识别结果
  - ✅ 更快速度
- **适用场景**: 实时语音输入、短音频、单人说话
- **粤语支持**: ✅ 应该支持（HKGAI是香港的服务）

### 2. 语音合成（TTS）

- **端点**: `GET https://openspeech.hkgai.net/server_proxy/api/tts`
- **粤语支持**: ✅ **明确支持粤语**
  - `language=cantonese` - 粤语
  - `language=mandarin` - 普通话
- **音色选择**:
  - `voice=female` - 女声
  - `voice=male` - 男声

## API认证

**统一API Key**: `TzmW5eWvGWphlubmavEIRtG5U6OwS9wF02AwtEHWx0stLvtqZWpz5LK2q7lRQhDY`

使用方式：
```
Authorization: TzmW5eWvGWphlubmavEIRtG5U6OwS9wF02AwtEHWx0stLvtqZWpz5LK2q7lRQhDY
```

## 推荐配置（粤语友好）

### STT（语音转文字）
```python
# 推荐使用：简单语音识别接口
endpoint = "https://openspeech.hkgai.net/api/v1/speech_recognize"
headers = {
    "Authorization": "TzmW5eWvGWphlubmavEIRtG5U6OwS9wF02AwtEHWx0stLvtqZWpz5LK2q7lRQhDY",
    "Content-Type": "application/json"
}

# 请求格式
payload = {
    "request_id": "uuid-here",
    "resource": {
        "type": 2,  # BYTES
        "data": audio_bytes  # 音频字节流
    }
}
```

### TTS（文字转语音）- 粤语
```bash
# 粤语女声
curl 'https://openspeech.hkgai.net/server_proxy/api/tts?text=你好&voice=female&language=cantonese' \
  -H "Authorization: TzmW5eWvGWphlubmavEIRtG5U6OwS9wF02AwtEHWx0stLvtqZWpz5LK2q7lRQhDY" \
  > output.wav

# 粤语男声
curl 'https://openspeech.hkgai.net/server_proxy/api/tts?text=你好&voice=male&language=cantonese' \
  -H "Authorization: TzmW5eWvGWphlubmavEIRtG5U6OwS9wF02AwtEHWx0stLvtqZWpz5LK2q7lRQhDY" \
  > output.wav
```

## 与现有系统集成

### 当前系统使用
- **Whisper**: 作为主要STT（支持多语言，包括粤语）
- **Edge TTS**: 作为主要TTS

### 建议集成策略

#### 方案1：HKGAI作为粤语专用通道（推荐）⭐
```python
if detected_language == "cantonese":
    # 使用HKGAI Speech API（粤语优化）
    use_hkgai_speech()
else:
    # 使用Whisper（通用多语言）
    use_whisper()
```

#### 方案2：HKGAI作为Fallback
```python
try:
    result = whisper_stt()
except:
    result = hkgai_stt()  # 备用
```

#### 方案3：并行识别（提高准确度）
```python
whisper_result = whisper_stt()
hkgai_result = hkgai_stt()
# 对比结果，选择置信度更高的
final_result = choose_best(whisper_result, hkgai_result)
```

## 性能对比预测

| 特性 | Whisper | HKGAI Speech |
|------|---------|--------------|
| 粤语准确度 | 🟡 中等 | 🟢 高（专门优化） |
| 处理速度 | 🟢 快（本地） | 🟡 中等（网络） |
| 成本 | 🟢 免费 | 🟡 按量计费？ |
| 离线支持 | 🟢 支持 | 🔴 不支持 |
| 多语言 | 🟢 100+语言 | 🟡 主要中英文 |

## 测试建议

### 1. 基础测试
```bash
# 测试粤语TTS
curl 'https://openspeech.hkgai.net/server_proxy/api/tts?text=今日天氣點呀&voice=female&language=cantonese' \
  -H "Authorization: TzmW5eWvGWphlubmavEIRtG5U6OwS9wF02AwtEHWx0stLvtqZWpz5LK2q7lRQhDY" \
  > test_cantonese.wav
```

### 2. STT测试
需要准备：
- 粤语音频文件
- 普通话音频文件
- 对比Whisper和HKGAI的识别结果

## 结论

✅ **可以用于STT/ASR**  
✅ **粤语友好**（TTS明确支持，STT应该也支持）  
⭐ **推荐使用场景**：
- 粤语语音输入（优先使用HKGAI）
- 粤语语音合成（使用HKGAI的cantonese模式）
- 多语言识别（继续使用Whisper）

