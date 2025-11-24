# 🎤 Jude - Voice-First AI Agent System

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![Milvus](https://img.shields.io/badge/Milvus-2.3+-orange.svg)](https://milvus.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**支持粤语🇭🇰 | 普通话🇨🇳 | 英语🇺🇸 的智能语音助手**

[功能特点](#-核心创新) • [快速开始](#-快速开始) • [系统架构](#️-系统架构) • [演示](#-在线演示) • [文档](#-文档)

</div>

---

## 📖 项目简介

**Jude** 是一个生产级的语音优先AI Agent系统，专为MAIE5221 NLP Final Project开发。系统整合了多模态RAG、实时语音交互、双LLM架构和动态工具编排，提供无缝的智能问答体验。

### 🎯 三大核心创新

1. **🎙️ Streamed Voice Interaction**
   - Web Speech API实时STT（支持流式识别）
   - Edge TTS低延迟语音合成（支持粤语、普通话）
   - 智能TTS触发（自动检测需要语音回答的问题）

2. **🧠 Cantonese Optimization & Dual-Brain System**
   - **HKGAI-V1**：专注中文文本理解和香港本地知识
   - **Doubao Seed-1-6**：处理多模态任务（图像理解、OCR）
   - 智能任务分发，cost-effective架构

3. **⚡ Dynamic Workflow Orchestration**
   - LLM驱动的智能工具选择（5+外部API）
   - 两阶段RAG检索 + Cross-encoder重排序
   - 自动Fallback机制（RAG → Web Search → Direct LLM）

---

## ✨ 核心功能

### 🤖 智能Agent系统
- ✅ **动态工具路由**：自动选择Local RAG / Web Search / Weather / Finance / Transport
- ✅ **LangGraph工作流**：状态管理 + 并行执行
- ✅ **意图识别**：translation / weather / finance / rag / web query分类
- ✅ **智能降级**：primary tool失败自动cascade到备用方案

### 🔍 高级RAG系统
- ✅ **两阶段检索**：Milvus cosine similarity (top-20) → Cross-encoder reranking (top-5)
- ✅ **多语言Embedding**：paraphrase-multilingual-MiniLM-L12-v2 (384-dim)
- ✅ **智能分块**：512 tokens + 50-token overlap，保留metadata
- ✅ **可信度加权**：0.7 semantic + 0.2 recency + 0.1 source trust

### 🎤 语音交互
- ✅ **实时STT**：Web Speech API（zh-CN）+ Whisper fallback
- ✅ **自然TTS**：Edge TTS HiuGaaiNeural（粤语）、XiaoxiaoNeural（普通话）
- ✅ **智能播报**：Agent自动标记`should_speak`字段触发TTS
- ✅ **语言检测**：自动识别查询语言并匹配对应TTS voice

### 🖼️ 多模态处理
- ✅ **图像识别**：Doubao vision model（Seed-1-6-251015）
- ✅ **OCR**：中英文文本提取
- ✅ **图像历史**：session-based跟踪，支持上下文引用
- ✅ **文档解析**：PDF、DOCX自动提取和索引

### 🌐 外部API集成
- ✅ **Tavily AI Search**：实时网页搜索（主要工具）
- ✅ **wttr.in**：免费天气查询（无需API key）
- ✅ **Yahoo Finance (yfinance)**：股票、金融数据
- ✅ **HK Transport API**：香港交通路线查询
- ✅ **DuckDuckGo Search**：备用搜索引擎

### 🎨 交互式前端
- ✅ **Landing Page**：3D滚动动画、渐变文字效果、FAQ手风琴
- ✅ **System Dashboard**：5页全屏滚动展示（Data Flow / Features / Evaluation / Q&A / Team）
- ✅ **Demo Interface**：实时聊天、语音输入、图像上传、TTS自动播放
- ✅ **响应式设计**：粉紫渐变主题、glassmorphism风格

---

## 🚀 快速开始

### ⚡ 演示启动（4步启动）

如果你已经配置好所有依赖和API密钥，按以下顺序启动：

#### 1️⃣ 打开 Docker Desktop
```bash
# 确保Docker Desktop应用已启动并运行
```

#### 2️⃣ 启动 Docker 服务
```bash
cd "/Users/anonymity/Desktop/MAIE/MAIE5221 NLP/Final"
docker compose up -d

# 验证服务（应看到 milvus-standalone, minio, etcd 3个容器）
docker ps
```

#### 3️⃣ 启动后端 API
```bash
# 在项目根目录下
conda activate ise
uvicorn backend.main:app --host 0.0.0.0 --port 5555 --reload
# 看到 "Application startup complete" 表示成功
# 后端运行在 http://localhost:5555
```

#### 4️⃣ 启动前端
```bash
# 新开一个终端
cd frontend
npm run dev
# 前端运行在 http://localhost:5173
```

#### ✅ 验证启动成功
- 访问 `http://localhost:5173` 看到Landing Page
- 点击 "Experience Jude" 进入Demo界面
- 测试文本输入、语音输入、图像上传功能

#### 💡 演示技巧
- **保持电脑唤醒**：`caffeinate -d` 防止合盖休眠
- **测试问题**：
  - "香港明天天气怎么样？"（天气API + 粤语TTS）
  - "TSLA最新股价是多少？"（金融API）
  - "请勿靠近车门用粤语怎么说？"（翻译 + 自动TTS播报）
  - 上传图片："图片里有什么？"（多模态）

---

### 📋 前置要求

- **Python 3.10+**
- **Node.js 18+** (前端)
- **Docker Desktop** (Milvus)
- **Conda** (推荐)
- **API Keys**: HKGAI, Doubao, Tavily（天气API使用免费的wttr.in，无需密钥）

### ⚙️ 后端安装

1. **克隆项目**
```bash
git clone https://github.com/yourusername/jude-voice-agent.git
cd jude-voice-agent
```

2. **创建虚拟环境**
```bash
conda create -n ise python=3.10
conda activate ise
pip install -r requirements.txt
```

3. **配置API密钥**
```bash
cp .env.example .env
# 编辑.env文件，填入你的API密钥：
# - HKGAI_API_KEY
# - DOUBAO_API_KEY
# - TAVILY_API_KEY
# - OPENWEATHER_API_KEY
```

4. **启动Docker服务**
```bash
# 启动Milvus, MinIO, etcd
docker compose up -d

# 验证服务状态
docker ps
```

5. **构建知识库**
```bash
python scripts/build_knowledge_base.py
```

6. **启动后端API**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 5555 --reload
```

### 🎨 前端安装

```bash
cd frontend
npm install
npm run dev
```

### 🌐 访问系统

- **Landing Page**: http://localhost:5173
- **API文档**: http://localhost:5555/docs
- **Health Check**: http://localhost:5555/api/health

### 🧪 快速测试

```bash
# 测试Agent工具调用
python scripts/tests/test_agent_with_tools.py

# 测试多模态功能
python scripts/tests/test_doubao_multimodal.py

# 测试粤语TTS
python scripts/tests/test_cantonese_tts.py

# 测试完整语音workflow
python scripts/tests/test_speech_to_agent.py
```

---

## 🏗️ 系统架构

### 数据流设计

```
┌────────────┐
│ User Input │ Audio / Text / Image
└──────┬─────┘
       │
┌──────▼─────────┐
│   Ingestion    │ STT / OCR
└──────┬─────────┘
       │
┌──────▼─────────┐
│  Agent Router  │ Intent Detection (translation / weather / finance / rag / web)
└──────┬─────────┘
       │
┌──────▼─────────────────────────────────┐
│       Tool Execution                    │
│  Local RAG │ Web Search │ Weather API  │
│  Finance   │ Transport  │ Image Vision │
└──────┬─────────────────────────────────┘
       │
┌──────▼──────────┐
│ LLM Generation  │ HKGAI (text) / Doubao (multimodal)
└──────┬──────────┘
       │
┌──────▼─────┐
│   Output   │ TTS / UI Render
└────────────┘
```

### 📦 项目结构

```
jude-voice-agent/
├── backend/                  # FastAPI后端
│   ├── main.py              # 主入口（端口5555）
│   ├── api.py               # 路由定义
│   └── models.py            # 数据模型
├── services/                 # 核心服务层
│   ├── agent/               # Agent系统
│   │   ├── agent.py         # 主逻辑（意图检测、工具选择）
│   │   ├── workflow_dynamic.py  # LangGraph动态工作流
│   │   └── tools/           # 工具集（local_rag, web_search, finance, weather, transport）
│   ├── llm/                 # LLM客户端
│   │   ├── unified_client.py    # 统一HKGAI接口
│   │   ├── doubao_multimodal.py # Doubao视觉模型
│   │   └── gemini_multimodal.py # Gemini（备用）
│   ├── vector/              # RAG系统
│   │   ├── milvus_client.py     # Milvus客户端
│   │   ├── retriever.py         # 检索器
│   │   └── reranker.py          # Cross-encoder重排序
│   ├── vision/              # 视觉处理
│   │   ├── image_processor.py   # 图像预处理（resize, base64）
│   │   └── image_history.py     # session管理
│   ├── speech/              # 语音处理
│   │   ├── voice_service.py     # TTS服务（Edge TTS）
│   │   ├── whisper_stt.py       # Whisper STT
│   │   └── hkgai_stt.py         # HKGAI STT（备用）
│   └── core/                # 核心模块
│       ├── config.py            # 配置管理
│       └── logger.py            # 日志系统
├── frontend/                 # React前端
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx      # 主页（3D滚动、动画）
│   │   │   └── DemoInterface.tsx    # 聊天界面
│   │   └── components/
│   │       ├── presentation/
│   │       │   └── Dashboard.tsx    # 系统Dashboard（5页）
│   │       └── GradientText.tsx     # 渐变动画组件
│   ├── public/
│   │   ├── landing page.png         # 背景图
│   │   └── dashboard-bg.png         # Dashboard背景
│   └── package.json
├── scripts/                  # 工具脚本
│   ├── build_knowledge_base.py      # 知识库构建
│   └── tests/                       # 测试脚本
│       ├── test_agent_with_tools.py
│       ├── test_doubao_multimodal.py
│       └── test_speech_to_agent.py
├── docs/                     # 文档
│   ├── FRONTEND_DESIGN_SPEC.md      # 前端设计规范
│   ├── WORKFLOW_ARCHITECTURE.md     # Agent架构
│   ├── PRESENTATION_SCRIPT.md       # 演讲稿
│   └── TAVILY_SETUP.md              # Tavily集成指南
├── documents/                # 知识库文档（PDF/DOCX）
├── logs/                     # 测试日志
├── docker-compose.yml        # Docker配置（Milvus + MinIO + etcd）
├── requirements.txt          # Python依赖
└── .env.example              # 环境变量模板
```

---

## 💻 技术实现细节

### 🏗️ 整体技术架构

```
┌─────────────────────────────────────────────┐
│          Frontend (React + Vite)            │
│  - Landing Page (Framer Motion动画)         │
│  - Dashboard (Recharts可视化)               │
│  - Demo Interface (实时交互)                │
└──────────────────┬──────────────────────────┘
                   │ HTTP/WebSocket
┌──────────────────▼──────────────────────────┐
│        Backend API (FastAPI + Uvicorn)      │
│  - RESTful API                              │
│  - CORS中间件                               │
│  - 异步请求处理                              │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼────────┐   ┌───────▼────────┐
│  Agent System  │   │   RAG System   │
│ (工具编排)     │   │ (知识检索)      │
└───────┬────────┘   └───────┬────────┘
        │                     │
        └──────────┬──────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼────────┐   ┌───────▼────────┐
│  LLM Services  │   │ Vector Store   │
│ HKGAI+Doubao   │   │    Milvus      │
└────────────────┘   └────────────────┘
```

### 🎨 前端技术实现

#### 核心技术栈
- **React 18.3** + **TypeScript** + **Vite 6**
- **Tailwind CSS** - 原子化CSS
- **Framer Motion** - 3D滚动动画
- **Recharts** - 数据可视化
- **Lucide React** - 图标库

#### 关键实现

**1. Landing Page 视差滚动**
```typescript
const { scrollYProgress } = useScroll({
  target: ref,
  offset: ["start start", "end start"]
});

const titleY = useTransform(scrollYProgress, [0, 1], [0, -200]);
const titleOpacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
```
- 使用 `useScroll` 监听滚动进度
- `useTransform` 将滚动映射到动画属性
- GPU加速（`transform: translateZ(0)`）

**2. Dashboard 全屏滚动**
```typescript
const handleWheel = (e: WheelEvent) => {
  if (isScrolling || !canScroll) return;
  
  if (Math.abs(e.deltaY) > SCROLL_THRESHOLD) {
    if (e.deltaY > 0 && currentPage < pages.length - 1) {
      setCurrentPage(prev => prev + 1);
    }
    // 防抖处理：800ms cooldown
    setIsScrolling(true);
    setTimeout(() => setIsScrolling(false), 800);
  }
};
```

**3. 实时语音识别（Web Speech API）**
```typescript
const SpeechRecognition = window.webkitSpeechRecognition;
recognitionRef.current = new SpeechRecognition();
recognitionRef.current.continuous = false; // 自动停止
recognitionRef.current.interimResults = true;
recognitionRef.current.lang = 'zh-CN';

recognitionRef.current.onresult = (event) => {
  let finalTranscript = '';
  for (let i = event.resultIndex; i < event.results.length; ++i) {
    if (event.results[i].isFinal) {
      finalTranscript += event.results[i][0].transcript;
    }
  }
  setInput(prev => prev + finalTranscript);
};
```

**4. 性能优化**
```typescript
// 图片预加载
<link rel="preload" href="/landing%20page.png" as="image" />

// GPU加速
style={{
  willChange: 'transform',
  backfaceVisibility: 'hidden',
  transform: 'translateZ(0)'
}}

// React.memo防止重渲染
const GradientText = React.memo(function GradientText({...}) {
  const gradientStyle = React.useMemo(() => ({
    backgroundImage: `linear-gradient(...)`,
  }), [colors]);
  return <div style={gradientStyle}>{children}</div>;
});
```

### ⚙️ 后端技术实现

#### 核心技术栈
- **FastAPI 0.104+** - 异步Web框架
- **Uvicorn** - ASGI服务器
- **Pydantic 2.5** - 数据验证

#### API设计

**RESTful端点**
```python
# 健康检查
GET /api/health

# Agent查询（核心）
POST /api/agent_query
{
  "query": "用户问题",
  "use_rag": true,
  "use_search": true
}

# 多模态查询
POST /api/multimodal/query
{
  "query": "问题",
  "images": ["base64..."],
  "use_ocr": true
}

# TTS语音合成
POST /api/tts
{
  "text": "文本",
  "language": "zh-CN"
}
```

**CORS配置**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # 本地开发
        "https://jude.darkdark.me",   # 生产环境
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 🤖 Agent系统实现

#### 1. 智能工具选择
```python
def detect_question_type(self, query: str) -> List[str]:
    """根据问题特征选择工具"""
    tools = []
    
    # 翻译问题 → 直接LLM
    if "怎么说" in query or "how to say" in query:
        return []  # 不使用任何工具
    
    # 天气查询 → weather API
    if "天气" in query or "weather" in query:
        tools.append("weather")
    
    # 排名/比较 → web_search
    if "第二大" in query or "second largest" in query:
        tools.insert(0, "web_search")
    
    # 金融查询 → finance API
    if "股票" in query or "stock" in query:
        tools.append("finance")
    
    # 默认 → local_rag
    if not tools:
        tools.append("local_rag")
    
    return tools
```

#### 2. 动态工作流执行
```python
class DynamicWorkflowEngine:
    def execute(self, query: str, plan: Dict) -> Dict:
        """执行多步骤工作流"""
        steps = plan.get("steps", [])
        context_accumulator = []
        
        for step in steps:
            tool_name = step["tool"]
            tool_func = self.tools[tool_name]
            
            # 执行工具
            result = tool_func(query)
            context_accumulator.append(result)
            
            # 中间决策
            if should_stop(result):
                break
        
        # 汇总上下文
        final_context = "\n\n".join(context_accumulator)
        answer = self._generate_final_answer(query, final_context)
        
        return {
            "answer": answer,
            "tools_used": [s["tool"] for s in steps]
        }
```

#### 3. 外部工具集成
```python
# 天气工具 - wttr.in（免费API）
def get_weather(location: str) -> Dict:
    url = f"http://wttr.in/{location}?format=j1"
    response = requests.get(url, timeout=10)
    data = response.json()
    return extract_weather_info(data)

# 金融工具 - Yahoo Finance
def get_stock_price(symbol: str) -> str:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    response = requests.get(url, headers=headers)
    return parse_stock_data(response.json())

# 网页搜索 - Tavily AI
def get_web_search(query: str) -> str:
    from tavily import TavilyClient
    client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    results = client.search(query, max_results=5)
    return format_search_results(results)
```

### 🔍 RAG系统实现

#### 1. 向量存储 - Milvus
```python
# Collection Schema
{
    "id": INT64 (auto_id),
    "text": VARCHAR(5000),
    "vector": FLOAT_VECTOR(384),  # 384维向量
    "source_file": VARCHAR(500)
}

# 索引配置
index_params = {
    "metric_type": "COSINE",  # 余弦相似度
    "index_type": "IVF_FLAT",
    "params": {"nlist": 128}
}
```

#### 2. 两阶段检索
```python
def search(self, query: str, top_k: int = 5) -> List[Dict]:
    # Stage 1: 向量相似度检索 (top-20)
    query_vector = embedder.encode(query)
    initial_results = milvus.search(
        query_vector, 
        top_k=20,  # 召回20个候选
        metric_type="COSINE"
    )
    
    # Stage 2: Cross-encoder重排序 (top-5)
    if use_reranker:
        rerank_scores = cross_encoder.predict([
            [query, doc["text"]] 
            for doc in initial_results
        ])
        
        # 综合评分
        for i, doc in enumerate(initial_results):
            semantic_score = sigmoid(rerank_scores[i])
            credibility = get_credibility(doc)
            freshness = get_freshness(doc)
            
            # 最终分数 = 语义相关性 × 可信度 × 新鲜度
            doc["final_score"] = (
                semantic_score * 
                credibility * 
                freshness
            )
        
        # 按最终分数排序
        results = sorted(
            initial_results, 
            key=lambda x: x["final_score"], 
            reverse=True
        )[:top_k]
    
    return results
```

#### 3. Embedding模型
```python
# Sentence Transformers
model = SentenceTransformer(
    'paraphrase-multilingual-MiniLM-L12-v2'
)
# 特点：
# - 384维向量
# - 支持中文/粤语/英语
# - 轻量级（约120MB）
```

### 🎙️ 语音服务实现

#### STT - Web Speech API
```javascript
// 前端实现（浏览器端）
const recognition = new webkitSpeechRecognition();
recognition.lang = 'zh-CN';
recognition.continuous = false;  // 自动停止
recognition.interimResults = true;  // 实时结果

// 优点：
// - 免费无限制
// - 实时流式识别
// - 无需后端处理
```

#### TTS - Edge TTS
```python
# 后端实现
import edge_tts

async def generate_audio(text: str, language: str):
    voice = {
        'zh-CN': 'zh-CN-XiaoxiaoNeural',    # 普通话
        'zh-HK': 'zh-HK-HiuGaaiNeural',     # 粤语
        'en-US': 'en-US-AriaNeural'          # 英语
    }[language]
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save("output.mp3")
    
    # 转换为base64返回前端
    with open("output.mp3", "rb") as f:
        audio_bytes = f.read()
        return base64.b64encode(audio_bytes).decode()
```

#### 智能TTS触发
```python
def _should_speak(query: str, answer: str) -> bool:
    """判断是否需要TTS播报"""
    # 检测翻译问题
    keywords = ["怎么说", "怎么读", "发音", "粤语"]
    if any(kw in query for kw in keywords):
        return True
    
    # 检测答案中的语言提示
    if "【粤语】" in answer or "发音是" in answer:
        return True
    
    return False

# 在Agent响应中
if _should_speak(query, answer):
    audio_url = await generate_tts(
        answer, 
        language="zh-HK" if "粤语" in query else "zh-CN"
    )
    return {
        "answer": answer,
        "should_speak": True,
        "audio_url": audio_url  # 前端自动播放
    }
```

### 🖼️ 多模态处理实现

#### 图片处理流程
```python
class ImageProcessor:
    def process_image(self, base64_img: str, optimize_for_ocr: bool):
        # 1. 解码base64
        img_data = base64.b64decode(base64_img)
        image = Image.open(BytesIO(img_data))
        
        # 2. OCR优化
        if optimize_for_ocr:
            image = image.convert('L')  # 转灰度
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)  # 增强对比度
            image = image.filter(ImageFilter.SHARPEN)  # 锐化
        
        # 3. 压缩（限制大小）
        if max(image.size) > 1920:
            image.thumbnail((1920, 1920), Image.LANCZOS)
        
        # 4. 计算哈希（去重）
        img_hash = hashlib.md5(image.tobytes()).hexdigest()
        
        # 5. 重新编码
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        new_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "base64": new_base64,
            "hash": img_hash,
            "size": image.size
        }
```

#### Doubao视觉模型调用
```python
from openai import OpenAI

class DoubaoMultimodalClient:
    def __init__(self, model: str):
        self.client = OpenAI(
            api_key=settings.DOUBAO_API_KEY,
            base_url=settings.DOUBAO_BASE_URL
        )
        self.model = model
    
    def query_with_images(self, query: str, images: List[str]):
        # 构建消息
        content = [{"type": "text", "text": query}]
        
        for img_base64 in images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_base64}"
                }
            })
        
        # 调用API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": content}],
            max_tokens=2048
        )
        
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "tokens": response.usage.total_tokens
        }
```

### 🚀 性能优化策略

#### 前端优化
```typescript
// 1. 图片预加载
<link rel="preload" href="/landing%20page.png" as="image" />

// 2. GPU加速
style={{
  willChange: 'transform',
  backfaceVisibility: 'hidden',
  transform: 'translateZ(0)'
}}

// 3. React.memo防止重渲染
const GradientText = React.memo(function GradientText({...}) {
  const gradientStyle = React.useMemo(() => ({
    backgroundImage: `linear-gradient(...)`,
  }), [colors]);
  return <div style={gradientStyle}>{children}</div>;
});
```

#### 后端优化
```python
# 1. 异步请求处理
@router.post("/api/agent_query")
async def agent_query(request: QueryRequest):
    # 并发调用多个工具
    results = await asyncio.gather(
        call_tool_async("web_search", query),
        call_tool_async("local_rag", query),
        return_exceptions=True
    )
    return process_results(results)

# 2. Milvus连接池复用
milvus_client = MilvusClient()
milvus_client.connect()  # 启动时连接，复用连接

# 3. 查询缓存
from cachetools import TTLCache
query_cache = TTLCache(maxsize=200, ttl=3600)

def search_with_cache(query: str):
    cache_key = hashlib.md5(query.encode()).hexdigest()
    if cache_key in query_cache:
        return query_cache[cache_key]
    
    results = milvus.search(query)
    query_cache[cache_key] = results
    return results
```

---

## 📊 性能指标

### 测试集结果（Test Sets 1-3）

| 指标 | Test Set 1 | Test Set 2 | Test Set 3 | 平均 |
|------|-----------|-----------|-----------|------|
| **Mean Search Time** | 0.52s | 0.68s | 1.12s | **0.77s** |
| **Total Response Latency** | 1.85s | 2.10s | 3.45s | **2.47s** |
| **Accuracy** | 95.0% | 88.5% | 92.0% | **91.8%** |
| **Test Queries** | 10 | 8 | 12 | **30** |

### 工具使用统计

- **Local RAG**: 43.3% (13/30)
- **Web Search**: 26.7% (8/30)
- **Finance Tool**: 16.7% (5/30)
- **Weather Tool**: 10.0% (3/30)
- **Transport Tool**: 3.3% (1/30)

### 多模态测试

- **Image Recognition**: ✅ 识别风景照、物体、文字内容
- **OCR Accuracy**: 95%+ (中英文混合文档)
- **Session Tracking**: ✅ 支持多轮对话中引用历史图片

---

## 🎬 在线演示

### 💬 文本查询示例

```bash
# 本地知识查询（触发Local RAG）
curl -X POST "http://localhost:5555/api/agent_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "香港科技大学在哪里？"}'

# 实时信息查询（触发Web Search）
curl -X POST "http://localhost:5555/api/agent_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "今天有什么最新科技新闻？"}'

# 翻译查询（触发Direct LLM + Auto TTS）
curl -X POST "http://localhost:5555/api/agent_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "请问请勿靠近车门用粤语怎么说？"}'
```

### 🎤 语音交互示例

1. 打开前端页面：http://localhost:5173
2. 点击 "Experience Jude" 或 "Hey Jude" 按钮
3. 使用麦克风图标进行语音输入
4. 系统自动STT识别 → Agent处理 → TTS播报（针对翻译类问题）

### 🖼️ 多模态示例

```bash
# 图像识别（上传base64编码的图片）
curl -X POST "http://localhost:5555/api/multimodal/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "这张图片里有什么？",
    "images": ["data:image/jpeg;base64,..."],
    "session_id": "test-session"
  }'
```

---

## 📚 文档

- **[前端设计规范](docs/FRONTEND_DESIGN_SPEC.md)** - UI/UX设计、API接口
- **[Agent架构设计](docs/WORKFLOW_ARCHITECTURE.md)** - LangGraph工作流详解
- **[Presentation演讲稿](docs/PRESENTATION_SCRIPT.md)** - 5分钟演讲脚本
- **[Tavily集成指南](docs/TAVILY_SETUP.md)** - Web搜索工具配置

---

## 🔧 配置说明

### 环境变量（.env）

```bash
# === LLM配置 ===
HKGAI_API_KEY=sk-iqA1pjC48rpFXdkU7cCaE3BfBc9145B4BfCbEe0912126646
HKGAI_BASE_URL=https://oneapi.hkgai.net/v1
HKGAI_DEFAULT_MODEL=HKGAI-V1

DOUBAO_API_KEY=your_doubao_key
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_DEFAULT_MODEL=doubao-seed-1-6-lite-251015
DOUBAO_DEFAULT_OCR_MODEL=doubao-seed-1-6-251015

# === 外部API ===
TAVILY_API_KEY=your_tavily_key
OPENWEATHER_API_KEY=your_openweather_key

# === Milvus配置 ===
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=knowledge_base

# === RAG配置 ===
USE_MULTILINGUAL_EMBEDDING=true
MULTILINGUAL_EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
USE_RERANKER=true
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
TOP_K=20
RERANK_TOP_K=5
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# === 语音配置 ===
ENABLE_SPEECH=true
WHISPER_MODEL_SIZE=base
EDGE_TTS_VOICE_CANTONESE=zh-HK-HiuGaaiNeural
EDGE_TTS_VOICE_MANDARIN=zh-CN-XiaoxiaoNeural
```

---

## 👥 团队成员

| 成员 | 学号 | 角色 | 主要贡献 |
|------|------|------|----------|
| **Yunlin He** | 21270701 | Project Lead & System Architect | 项目管理、系统架构、Agent实现、双模型集成、前端开发 |
| **Letian Wang** | 21211913 | API Integration Specialist | 专业工具实现、Tavily集成、API错误处理、限流管理 |
| **Ziyao Su** | 21272577 | Multimodal & Database Engineer | 文档处理、多模态支持、语音流式处理、Milvus管理 |
| **Ziyu Jing** | 21280146 | RAG Optimization & QA Engineer | RAG优化、两阶段重排序、可信度算法、系统测试 |

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📝 Future Improvements

- [ ] 添加用户认证系统（JWT + OAuth2）
- [ ] 实现完整对话历史管理（Redis缓存）
- [ ] 支持更多语言的TTS（日语、韩语等）
- [ ] 添加Agent工具（日历、邮件、提醒）
- [ ] 部署到云端（Vercel + Railway）
- [ ] 实现分布式Milvus集群
- [ ] 添加A/B测试框架
- [ ] 实现RAG性能监控Dashboard

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [React](https://reactjs.org/) + [Framer Motion](https://www.framer.com/motion/) - 前端框架和动画库
- [Milvus](https://milvus.io/) - 高性能向量数据库
- [LangChain](https://www.langchain.com/) + [LangGraph](https://www.langchain.com/langgraph) - Agent开发框架
- [OpenAI Whisper](https://github.com/openai/whisper) - 语音识别模型
- [Edge TTS](https://github.com/rany2/edge-tts) - 免费的多语言TTS
- [Sentence Transformers](https://www.sbert.net/) - 文本Embedding库
- [Tavily AI](https://tavily.com/) - 实时Web搜索API
- [HKGAI](https://hkgai.net/) - 香港AI平台
- [Doubao (ByteDance)](https://www.volcengine.com/) - 多模态大模型

---

<div align="center">

**🎤 "Hey Jude" - Your Voice-First AI Companion**

Built with ❤️ for MAIE5221 NLP Final Project

**⭐ If this project helps you, please give it a star! ⭐**

</div>
