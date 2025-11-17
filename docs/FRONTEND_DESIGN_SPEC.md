# MiniMango 前端交互设计规范

> **面向前端开发者的完整API和交互设计文档**  
> 版本：v1.0.0 | 更新日期：2025-11-17

---

## 📋 目录

1. [设计理念](#设计理念)
2. [核心功能概览](#核心功能概览)
3. [交互方式](#交互方式)
4. [API接口规范](#api接口规范)
5. [数据格式定义](#数据格式定义)
6. [UI/UX设计指南](#uiux设计指南)
7. [交互流程图](#交互流程图)
8. [错误处理](#错误处理)
9. [性能优化建议](#性能优化建议)

---

## 🎨 设计理念

### 核心原则

- **极简主义**：类似Siri的简洁交互界面
- **智能响应**：自动识别用户意图，无需手动选择工具
- **多模态**：无缝切换文本、语音交互
- **实时反馈**：流式输出，即时显示处理状态
- **多语言**：原生支持粤语、普通话、英语

### 设计风格

```
┌─────────────────────────────────────┐
│                                     │
│         🤖 MiniMango                │
│                                     │
│    ┌─────────────────────────┐    │
│    │                         │    │
│    │   你好！我能帮你什么？    │    │
│    │                         │    │
│    └─────────────────────────┘    │
│                                     │
│    [文本输入框或语音按钮]           │
│                                     │
└─────────────────────────────────────┘
```

---

## 🌟 核心功能概览

### 1. 智能问答
- **本地知识库检索**：175+知识块，涵盖系统文档、FAQ、技术细节
- **实时网页搜索**：获取最新信息
- **多轮对话**：支持上下文理解（需前端管理对话历史）

### 2. 实时信息查询
- **天气查询**：支持全球主要城市
- **股票查询**：实时股价、涨跌幅
- **交通路线**：旅行时间和路线规划

### 3. 多模态交互
- **文本输入**：支持多语言混合输入
- **语音输入**：Whisper + 粤语专用API
- **语音输出**：自然流畅的TTS（支持粤语、普通话、英语）

### 4. 智能工作流
- **自动工具选择**：系统自动判断需要哪些工具
- **多步骤任务**：复杂查询自动分解执行
- **结果综合**：整合多个数据源的信息

---

## 🔄 交互方式

### 方式一：文本交互（REST API）

**推荐场景**：桌面端、移动端文本输入

```javascript
// 发送文本查询
POST /api/agent_query
Content-Type: application/json

{
  "query": "香港今天天气怎么样？",
  "provider": "hkgai",  // 可选：hkgai（默认）或 gemini
  "model": "HKGAI-V1"   // 可选：指定模型
}

// 响应
{
  "answer": "香港今天的天气是多云，温度为25°C...",
  "tools_used": ["weather"],
  "contexts_count": 3,
  "has_context": true,
  "model": "HKGAI-V1",
  "tokens": {
    "input": 150,
    "output": 200,
    "total": 350
  },
  "workflow_engine": "llm_driven",
  "response_time": 12.5
}
```

### 方式二：语音交互（WebSocket）

**推荐场景**：移动端、智能助手模式

```javascript
// 1. 建立WebSocket连接
const ws = new WebSocket('ws://localhost:8000/ws/voice');

// 2. 发送音频流（实时）
ws.send(audioChunk);  // Int16Array 或 Float32Array

// 3. 接收转录和回答
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'transcription') {
    // 显示转录文本
    console.log('你说：', data.text);
  }
  
  if (data.type === 'answer') {
    // 显示回答
    console.log('助手：', data.answer);
  }
  
  if (data.type === 'audio') {
    // 播放语音回复（Base64编码的音频）
    playAudio(data.audio);
  }
};
```

### 方式三：混合交互（推荐）

支持用户在文本和语音间自由切换：

```javascript
// 文本输入时使用REST API
async function sendTextQuery(text) {
  const response = await fetch('/api/agent_query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: text })
  });
  return await response.json();
}

// 语音输入时切换到WebSocket
function startVoiceMode() {
  ws = new WebSocket('ws://localhost:8000/ws/voice');
  // ... WebSocket逻辑
}
```

---

## 📡 API接口规范

### 基础信息

- **Base URL**: `http://localhost:8000` (开发环境)
- **生产环境**: `https://your-domain.com`
- **API版本**: v1
- **认证方式**: 暂无（可根据需求添加JWT）

---

### 1. 智能问答接口

#### 1.1 Agent查询（推荐使用）

**端点**: `POST /api/agent_query`

**功能**: 智能识别用户意图，自动选择合适工具，返回综合答案

**请求体**:
```json
{
  "query": "string (必需)",           // 用户问题
  "provider": "string (可选)",         // LLM提供商：hkgai/gemini，默认hkgai
  "model": "string (可选)",           // 模型名称，默认HKGAI-V1
  "conversation_id": "string (可选)"  // 对话ID（用于多轮对话）
}
```

**响应**:
```json
{
  "answer": "string",              // 最终答案
  "tools_used": ["string"],        // 使用的工具列表
  "contexts_count": 0,             // 检索到的上下文数量
  "has_context": false,            // 是否使用了知识库
  "model": "string",               // 使用的模型
  "tokens": {                      // Token使用情况
    "input": 0,
    "output": 0,
    "total": 0
  },
  "workflow_engine": "string",     // 工作流引擎：llm_driven/rule_based/single_tool
  "workflow_type": "string",       // 工作流类型
  "workflow_confidence": 0.95,     // 工作流规划置信度
  "response_time": 12.5            // 响应时间（秒）
}
```

**示例**:
```bash
# 天气查询
curl -X POST "http://localhost:8000/api/agent_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "香港今天天气"}'

# 股票查询
curl -X POST "http://localhost:8000/api/agent_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "苹果公司的股价"}'

# 知识库查询
curl -X POST "http://localhost:8000/api/agent_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "如何使用粤语输入？"}'

# 复杂查询（触发工作流）
curl -X POST "http://localhost:8000/api/agent_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "对比NVIDIA和AMD的股价"}'
```

---

#### 1.2 RAG查询（仅知识库）

**端点**: `POST /api/rag_query`

**功能**: 仅从本地知识库检索，不使用外部工具

**请求体**:
```json
{
  "query": "string (必需)",
  "top_k": 5,                     // 可选：检索数量，默认5
  "provider": "hkgai",             // 可选：LLM提供商
  "file_ids": ["string"]           // 可选：指定文件ID
}
```

**响应**:
```json
{
  "answer": "string",
  "context": ["string"],           // 检索到的上下文
  "query": "string",
  "model_used": "string",
  "tokens_used": {},
  "answer_source": "rag"
}
```

---

### 2. 语音交互接口

#### 2.1 WebSocket实时语音

**端点**: `ws://localhost:8000/ws/voice`

**协议**: WebSocket

**连接参数**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/voice');
```

**客户端发送（音频流）**:
```javascript
// 音频格式：16kHz, 16-bit, Mono, PCM
const audioData = new Int16Array(sampleBuffer);
ws.send(audioData.buffer);
```

**服务端消息类型**:

1. **连接确认**:
```json
{
  "type": "connected",
  "message": "WebSocket连接成功",
  "session_id": "uuid"
}
```

2. **转录结果**:
```json
{
  "type": "transcription",
  "text": "你好，今天天气怎么样？",
  "language": "zh",
  "confidence": 0.95
}
```

3. **处理状态**:
```json
{
  "type": "status",
  "status": "processing",        // processing/completed/error
  "message": "正在查询天气信息..."
}
```

4. **文本答案**:
```json
{
  "type": "answer",
  "answer": "香港今天的天气是...",
  "tools_used": ["weather"],
  "response_time": 3.5
}
```

5. **语音回复**:
```json
{
  "type": "audio",
  "audio": "base64_encoded_audio_data",
  "format": "mp3",
  "language": "zh-CN"
}
```

6. **错误信息**:
```json
{
  "type": "error",
  "error": "语音识别失败",
  "code": "STT_ERROR"
}
```

---

#### 2.2 文件上传语音查询

**端点**: `POST /api/voice/query`

**功能**: 上传音频文件进行查询（非实时）

**请求**:
```javascript
const formData = new FormData();
formData.append('audio', audioBlob, 'query.wav');
formData.append('request', JSON.stringify({
  use_wake_word: false,
  use_agent: true,
  language: 'zh'  // 可选：zh/yue/en
}));

fetch('/api/voice/query', {
  method: 'POST',
  body: formData
});
```

**响应**:
```json
{
  "transcription": {
    "text": "转录文本",
    "language": "zh",
    "confidence": 0.95
  },
  "answer": "回答内容",
  "tools_used": ["tool1"],
  "audio_response": "base64_audio_data"
}
```

---

### 3. 文件管理接口

#### 3.1 上传文件

**端点**: `POST /api/upload`

**功能**: 上传PDF、图片、代码等文件到知识库

**请求**:
```javascript
const formData = new FormData();
formData.append('file', fileBlob, 'document.pdf');

fetch('/api/upload', {
  method: 'POST',
  body: formData
});
```

**响应**:
```json
{
  "file_id": "uuid",
  "filename": "document.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "uploaded_at": "2025-11-17T10:00:00",
  "processed": false,
  "message": "文件上传成功，正在后台处理..."
}
```

#### 3.2 列出文件

**端点**: `GET /api/files`

**查询参数**:
- `file_type`: 按类型筛选（pdf/image/code/text）
- `processed`: 是否已处理（true/false）
- `limit`: 返回数量（默认50）

**响应**:
```json
{
  "files": [
    {
      "file_id": "uuid",
      "filename": "document.pdf",
      "file_type": "pdf",
      "file_size": 1024000,
      "uploaded_at": "2025-11-17T10:00:00",
      "processed": true,
      "chunk_count": 25
    }
  ],
  "total": 100,
  "page": 1
}
```

#### 3.3 删除文件

**端点**: `DELETE /api/files/{file_id}`

**响应**:
```json
{
  "message": "文件删除成功",
  "file_id": "uuid"
}
```

---

### 4. 系统信息接口

#### 4.1 健康检查

**端点**: `GET /health`

**响应**:
```json
{
  "status": "healthy",
  "services": {
    "milvus": "connected",
    "llm": "available",
    "speech": "available"
  },
  "version": "1.0.0"
}
```

#### 4.2 支持的模型

**端点**: `GET /api/models`

**响应**:
```json
{
  "default_provider": "hkgai",
  "providers": ["hkgai", "gemini"],
  "hkgai_models": ["HKGAI-V1"],
  "gemini_models": [
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-2.5-pro"
  ]
}
```

#### 4.3 用量统计

**端点**: `GET /api/usage/stats`

**响应**:
```json
{
  "date": "2025-11-17",
  "total_requests": 150,
  "total_tokens": 50000,
  "by_model": {
    "HKGAI-V1": {
      "requests": 100,
      "tokens": 30000
    },
    "gemini-2.0-flash": {
      "requests": 50,
      "tokens": 20000
    }
  }
}
```

---

## 📦 数据格式定义

### 查询对象

```typescript
interface Query {
  query: string;                    // 必需：用户问题
  provider?: 'hkgai' | 'gemini';    // 可选：LLM提供商
  model?: string;                   // 可选：模型名称
  conversation_id?: string;         // 可选：对话ID
  file_ids?: string[];              // 可选：指定文件
  top_k?: number;                   // 可选：检索数量
}
```

### 响应对象

```typescript
interface Response {
  answer: string;                   // 答案文本
  tools_used: string[];             // 使用的工具
  contexts_count: number;           // 上下文数量
  has_context: boolean;             // 是否使用知识库
  model: string;                    // 使用的模型
  tokens?: TokenUsage;              // Token使用情况
  workflow_engine?: string;         // 工作流引擎
  workflow_type?: string;           // 工作流类型
  workflow_confidence?: number;     // 置信度
  response_time: number;            // 响应时间
}

interface TokenUsage {
  input: number;
  output: number;
  total: number;
}
```

### 语音对象

```typescript
interface VoiceTranscription {
  text: string;                     // 转录文本
  language: 'zh' | 'yue' | 'en';    // 识别语言
  confidence: number;               // 置信度 0-1
}

interface VoiceResponse {
  transcription: VoiceTranscription;
  answer: string;                   // 文本答案
  tools_used: string[];
  audio_response?: string;          // Base64音频
}
```

### 文件对象

```typescript
interface FileInfo {
  file_id: string;
  filename: string;
  file_type: 'pdf' | 'image' | 'code' | 'text';
  file_size: number;                // 字节
  uploaded_at: string;              // ISO 8601
  processed: boolean;
  chunk_count?: number;
}
```

---

## 🎨 UI/UX设计指南

### 主界面设计

#### 布局结构

```
┌────────────────────────────────────────┐
│  Header                                │
│  ┌──────────────────────────────────┐ │
│  │  🤖 MiniMango                    │ │
│  │  你的智能助手                     │ │
│  └──────────────────────────────────┘ │
│                                        │
│  Chat Container                        │
│  ┌──────────────────────────────────┐ │
│  │                                  │ │
│  │  [对话气泡区域]                   │ │
│  │                                  │ │
│  │  ┌────────────────────────────┐ │ │
│  │  │ 用户：香港今天天气？        │ │ │
│  │  └────────────────────────────┘ │ │
│  │                                  │ │
│  │  ┌────────────────────────────┐ │ │
│  │  │ 助手：香港今天多云，25°C... │ │ │
│  │  │ 🌤️ 温度：25°C               │ │ │
│  │  │ 💨 风速：19km/h             │ │ │
│  │  └────────────────────────────┘ │ │
│  │                                  │ │
│  └──────────────────────────────────┘ │
│                                        │
│  Input Area                            │
│  ┌──────────────────────────────────┐ │
│  │  [文本输入框]          🎤  ➡️    │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```

---

### 交互状态设计

#### 1. 空闲状态（Idle）

```
┌────────────────────────────────┐
│                                │
│        🤖 MiniMango            │
│                                │
│    你好！我能帮你什么？         │
│                                │
│  💡 试试这些：                 │
│  • "香港今天天气"              │
│  • "苹果股价"                  │
│  • "如何上传文件"              │
│                                │
│  [          输入...      🎤 ] │
└────────────────────────────────┘
```

#### 2. 输入状态（Typing）

```
┌────────────────────────────────┐
│  你：香港今天天气|             │
│                                │
│  [  香港今天天气怎么样  🎤 ➡️]│
└────────────────────────────────┘
```

#### 3. 语音输入状态（Listening）

```
┌────────────────────────────────┐
│                                │
│        🎤 正在听...            │
│                                │
│     ●●●●●●●●○○                │
│                                │
│      [点击停止录音]            │
└────────────────────────────────┘
```

#### 4. 处理状态（Processing）

```
┌────────────────────────────────┐
│  你：香港今天天气怎么样         │
│                                │
│  助手：                        │
│  ⏳ 正在查询天气信息...        │
│  🔍 使用工具：weather          │
│                                │
│  [动画加载指示器]              │
└────────────────────────────────┘
```

#### 5. 回答状态（Answering）

```
┌────────────────────────────────┐
│  你：香港今天天气怎么样         │
│                                │
│  助手：                        │
│  香港今天的天气是多云，         │
│  温度为25°C，体感27°C。        │
│                                │
│  🌤️ 多云                       │
│  🌡️ 25°C (体感 27°C)           │
│  💧 湿度 69%                    │
│  💨 风速 19km/h 东北            │
│                                │
│  📊 使用工具：weather           │
│  ⏱️ 响应时间：3.2秒            │
└────────────────────────────────┘
```

#### 6. 错误状态（Error）

```
┌────────────────────────────────┐
│  你：查询xyz股票               │
│                                │
│  助手：                        │
│  ⚠️ 抱歉，无法识别该股票代码   │
│                                │
│  💡 建议：                     │
│  • 检查股票代码是否正确        │
│  • 尝试使用公司全名            │
│  • 例如："苹果股价"            │
└────────────────────────────────┘
```

---

### 消息气泡设计

#### 用户消息

```css
.user-message {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 18px 18px 4px 18px;
  padding: 12px 16px;
  max-width: 70%;
  margin-left: auto;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}
```

#### 助手消息

```css
.assistant-message {
  background: #f7f9fc;
  color: #2d3748;
  border-radius: 18px 18px 18px 4px;
  padding: 12px 16px;
  max-width: 75%;
  margin-right: auto;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
```

#### 系统消息（工具调用、状态）

```css
.system-message {
  background: #edf2f7;
  color: #718096;
  border-radius: 12px;
  padding: 8px 12px;
  font-size: 14px;
  text-align: center;
  margin: 8px auto;
}
```

---

### 特殊内容卡片设计

#### 天气卡片

```html
<div class="weather-card">
  <div class="weather-icon">🌤️</div>
  <div class="weather-main">
    <h3>香港</h3>
    <div class="temperature">25°C</div>
    <div class="condition">多云</div>
  </div>
  <div class="weather-details">
    <div class="detail-item">
      <span class="icon">🌡️</span>
      <span>体感 27°C</span>
    </div>
    <div class="detail-item">
      <span class="icon">💧</span>
      <span>湿度 69%</span>
    </div>
    <div class="detail-item">
      <span class="icon">💨</span>
      <span>风速 19km/h</span>
    </div>
  </div>
</div>
```

#### 股票卡片

```html
<div class="stock-card">
  <div class="stock-header">
    <h3>苹果公司 (AAPL)</h3>
    <span class="stock-exchange">NASDAQ</span>
  </div>
  <div class="stock-price">
    <span class="price">$272.41</span>
    <span class="change positive">+$3.25 (+1.21%)</span>
  </div>
  <div class="stock-chart">
    [迷你走势图]
  </div>
  <div class="stock-time">
    更新时间：2025-11-17 16:00 EST
  </div>
</div>
```

#### 知识卡片

```html
<div class="knowledge-card">
  <div class="card-header">
    <span class="icon">📚</span>
    <h4>如何使用粤语输入</h4>
  </div>
  <div class="card-content">
    <p>系统支持粤语STT（语音转文字），通过以下方式：</p>
    <ul>
      <li>Whisper模型：支持多语言识别</li>
      <li>专用粤语Speech API：提供更高准确度</li>
      <li>自动语言检测：自动选择最佳引擎</li>
    </ul>
  </div>
  <div class="card-footer">
    <span class="source">来源：系统知识库</span>
  </div>
</div>
```

---

### 动画效果

#### 1. 消息进入动画

```css
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message {
  animation: slideIn 0.3s ease-out;
}
```

#### 2. 打字效果（流式输出）

```javascript
function typeWriter(text, element, speed = 30) {
  let i = 0;
  element.textContent = '';
  
  const timer = setInterval(() => {
    if (i < text.length) {
      element.textContent += text.charAt(i);
      i++;
    } else {
      clearInterval(timer);
    }
  }, speed);
}
```

#### 3. 语音波形动画

```css
@keyframes pulse {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(1.5); }
}

.voice-bar {
  width: 4px;
  height: 20px;
  background: #667eea;
  animation: pulse 0.8s ease-in-out infinite;
}

.voice-bar:nth-child(2) { animation-delay: 0.1s; }
.voice-bar:nth-child(3) { animation-delay: 0.2s; }
```

#### 4. 加载动画

```css
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
}
```

---

## 🔄 交互流程图

### 文本查询流程

```
用户输入文本
    ↓
前端发送POST /api/agent_query
    ↓
显示"处理中"状态
    ↓
后端处理
    ├→ 工具选择（自动）
    ├→ 数据检索
    └→ 生成答案
    ↓
接收响应
    ↓
解析tools_used
    ├→ weather → 显示天气卡片
    ├→ finance → 显示股票卡片
    ├→ local_rag → 显示知识卡片
    └→ 其他 → 显示文本答案
    ↓
显示答案（带动画）
    ↓
显示元信息（工具、时间）
```

### 语音查询流程

```
用户点击语音按钮
    ↓
请求麦克风权限
    ↓
建立WebSocket连接
    ↓
显示"正在听..."状态
    ↓
开始录音
    ├→ 捕获音频流
    ├→ 实时发送到服务器
    └→ 显示音波动画
    ↓
用户停止录音 或 检测到静音
    ↓
显示"处理中"状态
    ↓
接收转录结果
    ↓
显示转录文本
    ↓
接收答案
    ↓
显示文本答案
    ↓
接收音频回复
    ↓
播放TTS音频
    ↓
完成
```

### 文件上传流程

```
用户选择文件
    ↓
前端验证
    ├→ 检查文件大小（<50MB）
    ├→ 检查文件类型
    └→ 预览缩略图
    ↓
显示上传进度条
    ↓
POST /api/upload
    ↓
接收file_id
    ↓
显示"处理中"提示
    ↓
轮询文件状态
GET /api/files/{file_id}
    ↓
processed = true
    ↓
显示"上传成功"
    ↓
更新文件列表
```

---

## ⚠️ 错误处理

### 错误类型和处理策略

#### 1. 网络错误

```javascript
try {
  const response = await fetch('/api/agent_query', options);
} catch (error) {
  if (error instanceof TypeError) {
    showError('网络连接失败，请检查网络设置');
  } else {
    showError('请求失败，请稍后重试');
  }
}
```

**UI显示**:
```
⚠️ 网络连接失败
请检查你的网络设置后重试

[重试] [取消]
```

#### 2. API错误

```javascript
if (!response.ok) {
  const error = await response.json();
  
  switch (response.status) {
    case 400:
      showError('请求格式错误：' + error.detail);
      break;
    case 429:
      showError('请求过于频繁，请稍后再试');
      break;
    case 500:
      showError('服务器错误，我们正在修复中...');
      break;
    default:
      showError('未知错误，请联系管理员');
  }
}
```

#### 3. 超时错误

```javascript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 30000);

try {
  const response = await fetch('/api/agent_query', {
    signal: controller.signal,
    ...options
  });
} catch (error) {
  if (error.name === 'AbortError') {
    showError('请求超时，请稍后重试');
  }
} finally {
  clearTimeout(timeoutId);
}
```

#### 4. 语音相关错误

```javascript
// 麦克风权限被拒绝
navigator.mediaDevices.getUserMedia({ audio: true })
  .catch(error => {
    if (error.name === 'NotAllowedError') {
      showError('需要麦克风权限才能使用语音功能');
    } else if (error.name === 'NotFoundError') {
      showError('未检测到麦克风设备');
    }
  });
```

### 错误消息显示规范

```typescript
interface ErrorMessage {
  type: 'error' | 'warning' | 'info';
  title: string;
  message: string;
  actions?: {
    label: string;
    handler: () => void;
  }[];
}

// 示例
const errorMsg: ErrorMessage = {
  type: 'error',
  title: '网络错误',
  message: '无法连接到服务器，请检查网络设置',
  actions: [
    { label: '重试', handler: () => retryRequest() },
    { label: '取消', handler: () => closeError() }
  ]
};
```

---

## ⚡ 性能优化建议

### 1. 前端优化

#### 防抖和节流

```javascript
// 输入防抖（用于搜索建议）
const debouncedSearch = debounce((query) => {
  fetchSuggestions(query);
}, 300);

// 滚动节流（用于无限滚动）
const throttledScroll = throttle(() => {
  loadMoreMessages();
}, 1000);
```

#### 消息虚拟化

```javascript
// 仅渲染可见消息，提升长对话性能
import { VirtualList } from 'react-virtual';

<VirtualList
  height={600}
  itemCount={messages.length}
  itemSize={100}
  renderItem={({ index }) => <Message data={messages[index]} />}
/>
```

#### 懒加载

```javascript
// 懒加载历史消息
const loadHistoryMessages = async () => {
  if (hasMore && !loading) {
    setLoading(true);
    const oldMessages = await fetchMessages(offset);
    setMessages(prev => [...oldMessages, ...prev]);
    setLoading(false);
  }
};
```

### 2. 请求优化

#### 缓存策略

```javascript
// 缓存常见查询结果
const cache = new Map();

async function queryWithCache(query) {
  const cacheKey = query.toLowerCase();
  
  if (cache.has(cacheKey)) {
    const cached = cache.get(cacheKey);
    if (Date.now() - cached.timestamp < 3600000) { // 1小时
      return cached.data;
    }
  }
  
  const data = await fetchQuery(query);
  cache.set(cacheKey, { data, timestamp: Date.now() });
  return data;
}
```

#### 请求取消

```javascript
let currentRequest = null;

async function searchQuery(query) {
  // 取消上一个未完成的请求
  if (currentRequest) {
    currentRequest.abort();
  }
  
  currentRequest = new AbortController();
  
  try {
    const response = await fetch('/api/agent_query', {
      signal: currentRequest.signal,
      method: 'POST',
      body: JSON.stringify({ query })
    });
    return await response.json();
  } catch (error) {
    if (error.name !== 'AbortError') {
      throw error;
    }
  }
}
```

### 3. WebSocket优化

#### 心跳机制

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/voice');
let heartbeatInterval;

ws.onopen = () => {
  // 每30秒发送心跳
  heartbeatInterval = setInterval(() => {
    ws.send(JSON.stringify({ type: 'ping' }));
  }, 30000);
};

ws.onclose = () => {
  clearInterval(heartbeatInterval);
};
```

#### 自动重连

```javascript
function connectWebSocket(maxRetries = 5) {
  let retries = 0;
  
  function connect() {
    const ws = new WebSocket('ws://localhost:8000/ws/voice');
    
    ws.onclose = () => {
      if (retries < maxRetries) {
        retries++;
        setTimeout(connect, 1000 * retries); // 指数退避
      }
    };
    
    ws.onerror = () => {
      ws.close();
    };
    
    return ws;
  }
  
  return connect();
}
```

---

## 📱 响应式设计

### 断点定义

```css
/* 移动端 */
@media (max-width: 768px) {
  .chat-container {
    padding: 12px;
  }
  
  .message {
    max-width: 85%;
    font-size: 15px;
  }
  
  .input-area {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
  }
}

/* 平板 */
@media (min-width: 769px) and (max-width: 1024px) {
  .chat-container {
    max-width: 768px;
    margin: 0 auto;
  }
}

/* 桌面 */
@media (min-width: 1025px) {
  .chat-container {
    max-width: 1024px;
    margin: 0 auto;
  }
  
  .sidebar {
    display: block; /* 显示侧边栏 */
  }
}
```

### 移动端优化

```javascript
// 检测移动设备
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

if (isMobile) {
  // 启用触摸优化
  enableTouchGestures();
  
  // 优化语音按钮大小
  voiceButton.style.minHeight = '48px';
  voiceButton.style.minWidth = '48px';
  
  // 防止输入框缩放
  inputField.style.fontSize = '16px';
}
```

---

## 🎯 推荐技术栈

### 前端框架

**选项1: React + TypeScript（推荐）**
```bash
npm create vite@latest minimango-frontend -- --template react-ts
```

**选项2: Vue 3 + TypeScript**
```bash
npm create vite@latest minimango-frontend -- --template vue-ts
```

### 关键库

```json
{
  "dependencies": {
    "axios": "^1.6.0",           // HTTP请求
    "socket.io-client": "^4.5.0", // WebSocket
    "react-markdown": "^9.0.0",   // Markdown渲染
    "framer-motion": "^10.0.0",   // 动画
    "recharts": "^2.10.0",        // 图表（股票走势）
    "@heroicons/react": "^2.0.0", // 图标
    "date-fns": "^2.30.0"         // 日期处理
  }
}
```

---

## 📝 完整代码示例

### React组件示例

```typescript
// ChatInterface.tsx
import { useState, useEffect, useRef } from 'react';
import axios from 'axios';

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    tools_used?: string[];
    response_time?: number;
  };
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    // 添加用户消息
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // 调用API
      const response = await axios.post('http://localhost:8000/api/agent_query', {
        query: input
      });

      // 添加助手回复
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.data.answer,
        timestamp: new Date(),
        metadata: {
          tools_used: response.data.tools_used,
          response_time: response.data.response_time
        }
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      // 添加错误消息
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'system',
        content: '抱歉，发生了错误，请稍后重试。',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="chat-interface">
      <div className="messages-container">
        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.type}`}>
            <div className="message-content">{msg.content}</div>
            {msg.metadata && (
              <div className="message-metadata">
                {msg.metadata.tools_used && (
                  <span>🔧 {msg.metadata.tools_used.join(', ')}</span>
                )}
                {msg.metadata.response_time && (
                  <span>⏱️ {msg.metadata.response_time.toFixed(2)}s</span>
                )}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="message assistant loading">
            <div className="loading-spinner" />
            正在思考...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="输入你的问题..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()}>
          发送
        </button>
      </div>
    </div>
  );
}
```

---

## 🎨 样式参考

```css
/* styles.css */
:root {
  --primary-color: #667eea;
  --secondary-color: #764ba2;
  --background: #ffffff;
  --surface: #f7f9fc;
  --text-primary: #2d3748;
  --text-secondary: #718096;
  --border-radius: 18px;
  --shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chat-interface {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
  background: var(--background);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  padding: 12px 16px;
  border-radius: var(--border-radius);
  max-width: 70%;
  word-wrap: break-word;
  box-shadow: var(--shadow);
}

.message.user {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  margin-left: auto;
  border-radius: 18px 18px 4px 18px;
}

.message.assistant {
  background: var(--surface);
  color: var(--text-primary);
  margin-right: auto;
  border-radius: 18px 18px 18px 4px;
}

.message.system {
  background: #edf2f7;
  color: var(--text-secondary);
  font-size: 14px;
  text-align: center;
  margin: 8px auto;
  max-width: 80%;
}

.message-metadata {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-secondary);
  display: flex;
  gap: 12px;
}

.input-area {
  display: flex;
  padding: 16px;
  background: var(--surface);
  border-top: 1px solid #e2e8f0;
  gap: 12px;
}

.input-area input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 24px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.3s;
}

.input-area input:focus {
  border-color: var(--primary-color);
}

.input-area button {
  padding: 12px 24px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  border: none;
  border-radius: 24px;
  font-size: 16px;
  cursor: pointer;
  transition: transform 0.2s;
}

.input-area button:hover {
  transform: translateY(-2px);
}

.input-area button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  display: inline-block;
  margin-right: 8px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

---

## 📞 技术支持

如有前端集成问题，请：
1. 查看 `/docs` 下的技术文档
2. 访问 API Swagger文档：`http://localhost:8000/docs`
3. 创建GitHub Issue
4. 联系项目维护者

---

**文档版本**: v1.0.0  
**最后更新**: 2025-11-17  
**维护者**: Team MiniMango  
**项目地址**: https://github.com/AnonymityHE/MAIE-5221-NLP-Final-Intelligent-Search-Engine


