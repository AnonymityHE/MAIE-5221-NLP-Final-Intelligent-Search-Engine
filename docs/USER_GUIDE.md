# 用户使用指南

## 📋 目录
1. [快速开始](#快速开始)
2. [语音助手使用](#语音助手使用)
3. [RAG检索功能](#rag检索功能)
4. [Agent智能查询](#agent智能查询)
5. [故障排查](#故障排查)

---

## 🚀 快速开始

### 启动服务
```bash
conda activate ise
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

访问：http://localhost:8000/voice

---

## 🎤 语音助手使用

### 实时语音交互

1. **连接WebSocket**：点击"连接"按钮
2. **开始录音**：点击"开始录音"，授予麦克风权限
3. **说话**：说 "Jarvis, [你的问题]"
4. **自动停止**：说完后等待2秒，系统自动检测静音并停止
5. **查看结果**：转录文本和回答会显示在界面上

### 唤醒词格式
- `Jarvis, 今天天气怎么样？`
- `jarvis, what is RAG?`
- `Jarvis！帮我查一下股价`

### 支持的语言
- ✅ 普通话
- ✅ 粤语
- ✅ 英语
- ✅ 混合语言

### API使用（文件上传）

```bash
curl -X POST "http://localhost:8000/api/voice/query" \
  -F "audio=@voice_query.wav" \
  -F 'request={"use_wake_word": true, "use_agent": true}'
```

### Whisper模型说明

**重要：完全免费，本地运行！**

- 使用 `medium` 模型（默认，高准确度）
- 首次使用会自动下载模型（约769MB）
- 之后完全离线运行
- 无API费用，数据不出本地

如需切换模型：`.env` 中设置 `WHISPER_MODEL_SIZE=tiny/base/small/medium/large`

### VAD语音活动检测

**前端VAD**（自动）：
- 实时检测语音活动
- 静音2秒后自动停止录音
- 无需手动点击停止

**后端Silero VAD**（可选）：
- 自动去除静音部分
- 提高识别准确度
- 需要安装：`pip install torch silero-vad onnxruntime`

---

## 🔍 RAG检索功能

### 多语言支持

系统支持**粤语、普通话、英语**的混合检索：

```bash
# 粤语查询
curl -X POST "http://localhost:8000/api/rag_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "RAG系统係乜嘢？"}'

# 普通话查询
curl -X POST "http://localhost:8000/api/rag_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "什么是RAG系统？"}'

# 英语查询
curl -X POST "http://localhost:8000/api/rag_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG system?"}'
```

### 多语言优化

- **粤语查询优化**：自动增加50%候选数量，提升检索召回率
- **语言匹配权重**：粤语查询匹配粤语文档时，分数提升15%
- **混合语言检测**：自动识别混合语言查询

### 知识库构建

将文档放入 `documents/` 目录，然后索引：

```bash
# 索引单个文件
python scripts/utils/ingest.py documents/your_file.pdf

# 批量索引
python scripts/utils/ingest.py documents/
```

---

## 🤖 Agent智能查询

Agent会自动选择最合适的工具：

### 支持的查询类型

1. **天气查询**
   - "今天天气怎么样？"
   - "明天的天气"
   - "昨天香港的天气"（历史天气→web_search）

2. **金融查询**
   - "苹果公司股价"
   - "比特币价格"
   - "AAPL股票"

3. **交通查询**
   - "从香港到深圳需要多久？"
   - "中环到尖沙咀的地铁"

4. **网页搜索**
   - "最新的AI新闻"
   - "2024年科技趋势"

5. **RAG检索**
   - "什么是RAG？"
   - "向量数据库的原理"

### API使用

```bash
curl -X POST "http://localhost:8000/api/agent_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "今天天气怎么样？"}'
```

### 工具选择逻辑

- **天气查询** → `weather` 工具（实时）/ `web_search`（历史）
- **金融查询** → `finance` 工具
- **交通查询** → `transport` 工具
- **实时查询** → `web_search` 工具
- **其他** → `local_rag` → `web_search`（fallback）

---

## 🐛 故障排查

### 语音识别问题

**问题1：识别失败**
- 检查是否安装：`pip install openai-whisper soundfile`
- 检查模型是否下载完成
- 查看日志：`logs/rag_system.log`

**问题2：识别准确度低**
- 升级Whisper模型：`.env` 设置 `WHISPER_MODEL_SIZE=medium`
- 确保音频清晰，减少背景噪音
- 检查麦克风质量

**问题3：唤醒词检测失败**
- 确保音频中包含"Jarvis"
- 查看 `transcribed_text` 字段确认识别结果
- 可以禁用唤醒词：`use_wake_word=false`

### WebSocket连接问题

**问题1：无法连接**
- 确保API服务正在运行
- 检查端口8000是否被占用
- 查看浏览器控制台错误

**问题2：麦克风权限**
- 检查浏览器权限设置
- 确保使用localhost（开发环境）
- Chrome/Edge/Safari都支持

### RAG检索问题

**问题1：检索不到结果**
- 检查知识库是否已索引：`python scripts/utils/check_knowledge_base.py`
- 确认文档已放入 `documents/` 目录
- 检查Milvus连接：`curl http://localhost:8000/api/health`

**问题2：多语言识别不准确**
- 检查是否启用多语言embedding：`.env` 设置 `USE_MULTILINGUAL_EMBEDDING=true`
- 查看日志了解语言检测结果

### API配置问题

**Google搜索API配置**：
1. 获取API密钥：https://console.cloud.google.com/
2. 设置环境变量：`.env` 中 `GOOGLE_API_KEY=your_key` 和 `GOOGLE_SEARCH_ENGINE_ID=your_id`
3. 或使用DuckDuckGo（无需配置）

**LLM API配置**：
- HKGAI：`.env` 设置 `HKGAI_API_KEY` 和 `HKGAI_API_URL`
- DeepSeek：`.env` 设置 `DEEPSEEK_API_KEY`

---

## 📝 最佳实践

1. **语音识别**：
   - 说话清晰，语速适中
   - 减少背景噪音
   - 使用16kHz采样率音频

2. **查询优化**：
   - 使用纯语言查询效果最好
   - 混合语言查询也能正常工作
   - 粤语查询会自动优化

3. **知识库建设**：
   - 为重要内容创建多语言版本
   - 确保每种语言都有足够文档
   - 定期检查语言分布

4. **性能优化**：
   - 使用`base`或`medium`Whisper模型平衡速度和准确度
   - 启用缓存提升重复查询速度
   - 根据需求调整RAG的`top_k`参数

---

## 📞 获取帮助

- 查看日志：`logs/rag_system.log`
- 检查健康状态：`curl http://localhost:8000/api/health`
- 浏览器控制台：F12查看前端错误
- 查看项目主README：`README.md`

