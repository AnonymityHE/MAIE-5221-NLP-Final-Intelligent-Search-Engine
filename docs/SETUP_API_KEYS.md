# API Keys 配置指南

## 🔑 需要配置的API Keys

要运行Test Set 3测试，需要配置以下API Keys：

### 1. HKGAI API Key（主要LLM）

编辑 `.env` 文件：

```bash
# HKGAI API (主要LLM，用于聊天和推理)
HKGAI_API_KEY=your-real-hkgai-key-here  # ⚠️ 替换为真实key
```

**获取方式**：
- 访问 HKGAI 平台获取API Key
- 或联系项目管理员获取

### 2. Gemini API Key（Fallback LLM）

```bash
# Gemini API (Fallback备用LLM)
GEMINI_API_KEY=your-real-gemini-key-here  # ⚠️ 替换为真实key
GEMINI_ENABLED=true
```

**获取方式**：
- 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
- 创建新的API Key
- 格式：`AIza...`（以AIza开头）

### 3. 语音API Keys（已配置✅）

```bash
# 粤语语音API（已有）
CANTONESE_SPEECH_API_KEY=TzmW5eWvGWphlubmavEIRtG5U6OwS9wF02AwtEHWx0stLvtqZWpz5LK2q7lRQhDY
```

---

## 🚀 配置步骤

### 步骤1：编辑.env文件

```bash
cd "/Users/anonymity/Desktop/MAIE/MAIE5221 NLP/Final"
nano .env
```

### 步骤2：填入真实API Keys

将 `.env` 中的占位符替换为真实的keys：

```bash
# 之前（占位符）
HKGAI_API_KEY=sk-xxxxxxxxxxxxxx
GEMINI_API_KEY=AIzaxxxxxxxxxxxxxx

# 修改后（真实key）
HKGAI_API_KEY=sk-your-real-key-12345678...
GEMINI_API_KEY=AIzaYour-Real-Gemini-Key-12345...
```

### 步骤3：重启后端服务

```bash
# 停止现有服务
pkill -f "uvicorn backend.main:app"

# 重新启动
cd "/Users/anonymity/Desktop/MAIE/MAIE5221 NLP/Final"
eval "$(conda shell.bash hook)"
conda activate ise
nohup uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
```

### 步骤4：验证配置

```bash
# 测试API
curl -X POST "http://localhost:8000/api/agent_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "你好"}' \
  --max-time 30

# 应该返回JSON响应而不是超时
```

---

## 🧪 运行Test Set 3

配置好API Keys后：

```bash
cd "/Users/anonymity/Desktop/MAIE/MAIE5221 NLP/Final"
conda activate ise
python scripts/tests/test_set3_runner.py
```

---

## ⚠️ 当前状态

### 已配置✅
- Docker容器（Milvus）
- 语音API（HKGAI Speech）
- 双引擎STT（HKGAI + Whisper）
- 双引擎TTS（HKGAI + Edge TTS）

### 待配置❌
- HKGAI LLM API Key
- Gemini API Key（可选，作为fallback）

---

## 💡 临时解决方案

如果暂时无法获取API Keys，可以：

### 选项1：仅测试不需要LLM的功能

```python
# 测试STT/TTS
python scripts/tests/test_dual_engine_stt.py
python scripts/tests/test_dual_engine_tts.py
```

### 选项2：使用本地LLM（需要额外配置）

修改配置使用Ollama等本地LLM替代。

### 选项3：跳过LLM相关测试

运行仅依赖规则的查询测试。

---

## 📞 获取帮助

如果遇到问题：
1. 检查 `backend.log` 查看详细错误
2. 确认API Keys格式正确
3. 测试API Keys是否有效（配额、权限）


