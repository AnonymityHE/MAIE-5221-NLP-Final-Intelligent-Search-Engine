# RAG问答系统 - 本地开发指南

## 项目简介

这是一个基于Milvus向量数据库和LLM的**智能搜索和问答系统**，支持多模态文件上传、RAG检索、Agent工具调用等功能。本项目采用"最小可行产品（MVP）优先"的开发策略，优先在本地环境完成核心功能。

### 核心功能

- ✅ **RAG检索增强生成**：基于Milvus向量数据库的语义检索，支持Reranker重排序
- ✅ **多语言RAG支持**：支持粤语、普通话、英语的混合检索和生成 ⭐
- ✅ **Jarvis语音助手**：语音识别、唤醒词检测（"Jarvis"）、文本转语音 🎤
- ✅ **流式STT/TTS**：实时语音转文本和文本转语音，降低延迟 🚀 新增
- ✅ **Mac MLX优化**：Lightning Whisper MLX和MLX LM，充分利用Apple Silicon 🍎 新增
- ✅ **多模态文件支持**：上传并处理PDF、图片、代码、文本等多种格式文件
- ✅ **Agent智能工具**：自动选择RAG、网页搜索、天气、金融、交通等工具
- ✅ **多LLM支持**：HKGAI（默认，支持多语言）、Gemini系列（备选）、MLX LM（Mac优化）
- ✅ **用量监控**：Gemini API的token使用量和配额管理
- ✅ **性能优化**：查询缓存、结果过滤、高级重排序
- ✅ **可切换存储后端**：Milvus或传统数据库（SQLite/PostgreSQL）
- ✅ **日志系统**：统一的日志管理，支持文件输出和日志轮转
- ✅ **环境变量配置**：支持从`.env`文件和环境变量加载配置

## 技术栈

### 后端框架
- **Web框架**: FastAPI + Uvicorn
- **编程语言**: Python 3.10+

### 数据存储
- **向量数据库**: Milvus（用于向量检索和文本存储）
- **元数据存储**: 
  - Milvus后端（默认）：通过Milvus查询元数据
  - 传统数据库后端（可选）：SQLite或PostgreSQL

### AI模型
- **Embedding模型**: 
  - 默认：sentence-transformers/all-MiniLM-L6-v2（384维向量）
  - 多语言：paraphrase-multilingual-MiniLM-L12-v2（支持100+语言，包括粤语、普通话、英语）⭐
- **LLM (默认)**: HKGAI-V1 (HKGAI API) - 支持粤语、普通话、英语多语言生成
- **LLM (备选)**: Gemini系列模型 (支持用量监控和配额管理)
  - Gemini 2.5 Pro (50 请求/天, 125K TPM)
  - Gemini 2.5 Flash (250 请求/天, 250K TPM)
  - Gemini 2.0 Flash (200 请求/天, 1M TPM)

### 文档和文件处理
- **PDF处理**: PyMuPDF, pypdf
- **Word文档**: python-docx
- **图片处理**: Pillow
- **OCR识别**: pytesseract (可选，需要系统安装Tesseract OCR)
- **文本处理**: LangChain

### 语音处理
- **语音识别 (STT)**: 
  - Whisper (支持多语言：粤语、普通话、英语)
  - Faster Whisper (流式处理，内存占用低95%) 🚀
  - Lightning Whisper MLX (Mac优化，Apple Silicon加速) 🍎
- **语音合成 (TTS)**: 
  - Edge TTS (免费，多语言，云端处理)
  - Parler-TTS (流式输出，降低延迟) 🚀
  - MeloTTS (多语言，Mac优化) 🍎
- **流式处理**: 实时STT/TTS，降低延迟，提升用户体验 🚀
- **VAD**: 前端Web Audio API + 后端Silero VAD（自动检测语音活动）

### Agent工具
- **本地RAG**: Milvus向量检索
- **网页搜索**: DuckDuckGo API / Google Search API
- **天气查询**: wttr.in API（实时和历史天气）
- **金融数据**: 股票和加密货币价格查询（Yahoo Finance, CoinGecko）
- **交通查询**: 旅行时间和路线查询（OpenRouteService）
- **可扩展**: 支持添加更多工具

### 前端
- **语音助手页面**: `frontend/voice_assistant.html` - 实时语音交互界面
- **WebSocket**: 实时双向通信，支持流式音频处理

## 快速开始

### 第一步：环境准备

1. **安装Docker Desktop**
   - 访问 https://www.docker.com/products/docker-desktop/ 下载并安装
   - 启动Docker Desktop并确保Docker正在运行
   - 验证安装：在终端运行 `docker --version`

2. **配置API密钥**
   ```bash
   # 复制配置文件示例
   cp services/config.example.py services/config.py
   
   # 编辑 config.py，填入你的API密钥
   # 或创建 .env 文件（推荐）：
   cp .env.example .env
   # 然后编辑 .env 文件填入API密钥
   ```
   
   **重要**：API密钥不应提交到Git仓库，`services/config.py` 和 `.env` 已添加到 `.gitignore`

3. **安装Python依赖**
   ```bash
   # 建议使用conda创建虚拟环境
   conda create -n ise python=3.10
   conda activate ise
   
   # 安装所有依赖
   pip install -r requirements.txt
   
   # 如果使用图片OCR功能，还需要安装系统级Tesseract OCR：
   # macOS: brew install tesseract tesseract-lang
   # Ubuntu: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
   ```
   
   **注意**：
   - OCR功能（`pytesseract`）为可选依赖，如果未安装，图片上传功能仍可使用，但OCR识别会被禁用
   - 如果遇到模块导入错误，请确保已激活正确的conda环境

### 第三步：启动Milvus

在项目根目录运行：

```bash
# Docker Compose V2 (推荐，新版本Docker)
docker compose up -d

# 或者使用旧版本的命令（如果上面命令不工作）
docker-compose up -d
```

**注意**：Docker Compose V2使用 `docker compose`（没有连字符），V1使用 `docker-compose`（有连字符）。如果 `docker compose` 不工作，请使用 `docker-compose`。

检查Milvus是否正常运行：

```bash
docker ps
```

你应该看到三个容器正在运行：
- `milvus-standalone` (Milvus向量数据库)
- `milvus-etcd` (元数据存储)
- `milvus-minio` (对象存储)

**验证Milvus连接**：
```bash
# 检查Milvus健康状态
docker exec milvus-standalone curl http://localhost:9091/healthz
```

**停止Milvus**（如果需要）：
```bash
docker compose down
# 或
docker-compose down
```

**重启Milvus**：
```bash
docker compose restart
# 或
docker-compose restart
```

### 第三步：准备文档

1. 创建文档目录（如果不存在）：
   ```bash
   mkdir -p documents
   ```

2. 将你的PDF文档放入 `documents/` 目录

### 第四步：数据注入

运行数据注入脚本：

```bash
python scripts/utils/ingest.py
```

这个脚本会：
- 加载 `documents/` 目录中的所有PDF文件
- 将文本切分成小块
- 使用embedding模型进行向量化
- 将数据和向量插入Milvus

### 第五步：启动API服务

```bash
uvicorn backend.main:app --reload
```

服务将在 `http://localhost:8000` 启动。

### 第六步：测试API

#### 方法1：使用curl

```bash
curl -X POST "http://localhost:8000/api/rag_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "你的问题"}'
```

#### 方法2：使用Postman

1. 打开Postman
2. 创建POST请求：`http://localhost:8000/api/rag_query`
3. 在Body中选择raw -> JSON，输入：
   ```json
   {
     "query": "你的问题"
   }
   ```
4. 发送请求

#### 方法3：访问API文档

打开浏览器访问：`http://localhost:8000/docs`

这是FastAPI自动生成的Swagger UI，你可以直接在页面上测试API。

## 项目结构

```
.
├── backend/                # FastAPI后端应用
│   ├── main.py           # 应用入口
│   ├── api.py            # API路由
│   └── models.py         # Pydantic数据模型
├── services/              # 服务层（按功能模块化组织）
│   ├── __init__.py       # 统一导出接口（支持向后兼容）
│   ├── core/             # 核心基础设施
│   │   ├── config.py     # 配置管理（支持环境变量）
│   │   └── logger.py     # 日志系统
│   ├── llm/              # LLM相关模块
│   │   ├── hkgai_client.py      # HKGAI客户端
│   │   ├── gemini_client.py     # Gemini客户端
│   │   ├── unified_client.py    # 统一LLM客户端接口
│   │   └── usage_monitor.py     # API用量监控（Gemini配额管理）
│   ├── vector/           # 向量数据库相关
│   │   ├── milvus_client.py     # Milvus向量数据库客户端
│   │   ├── retriever.py         # RAG检索器
│   │   └── reranker.py          # 重排序器（交叉编码器）
│   ├── storage/            # 存储相关
│   │   ├── file_storage.py      # 文件存储管理系统
│   │   ├── file_processor.py    # 多模态文件处理器（PDF/图片/代码）
│   │   ├── file_indexer.py      # 文件索引服务（向量化和Milvus索引）
│   │   ├── backend.py            # 存储后端抽象接口（Milvus/数据库）
│   │   └── milvus_metadata.py   # Milvus元数据查询
│   └── agent/           # Agent相关
│       ├── agent.py      # Agent智能工具选择器
│       └── tools/        # Agent工具
│           ├── local_rag_tool.py     # 本地RAG工具
│           ├── web_search_tool.py    # 网页搜索工具
│           ├── weather_tool.py       # 天气查询工具
│           ├── finance_tool.py       # 金融数据工具
│           └── transport_tool.py    # 交通路线工具
├── frontend/             # 前端项目（Next.js，规划中）
│   └── README.md
├── scripts/               # 工具脚本（按用途分类）
│   ├── utils/            # 常用工具脚本
│   │   ├── ingest.py     # 数据注入脚本
│   │   ├── start_api.sh  # 启动API服务脚本
│   │   ├── create_test_doc.py  # 创建测试文档
│   │   └── read_project_announcement.py  # 读取项目公告
│   └── tests/            # 测试脚本
│       ├── test_improvements.py  # 完整功能测试
│       ├── test_refactoring.sh   # 重构验证测试
│       └── quick_test.sh         # 快速功能测试
├── docs/                  # 项目文档
│   └── README.md         # 文档索引
├── documents/            # 原始文档目录（用于批量导入）
├── uploaded_files/       # 用户上传文件存储目录（存储实际的PDF、图片、代码等文件）
├── file_index.json       # 文件索引（仅存储file_id -> file_path映射）
├── usage_data.json       # Gemini API用量数据（已加入.gitignore）
├── logs/                 # 日志文件目录
├── docker-compose.yml    # Milvus Docker配置
├── requirements.txt      # Python依赖
└── README.md            # 本文件
```

### 代码组织说明

项目采用模块化设计，`services/` 目录按功能分类：

- **`core/`**：核心基础设施（配置、日志）
- **`llm/`**：LLM客户端和用量监控
- **`vector/`**：向量数据库和检索相关
- **`storage/`**：文件存储和处理
- **`agent/`**：Agent逻辑和工具

#### 导入方式

**推荐的新导入方式**：
```python
from services.core import settings, logger
from services.llm import unified_llm_client
from services.vector import retriever, reranker
from services.agent import agent
from services.storage import file_storage
```

**向后兼容的旧导入方式**（仍支持）：
```python
from services import settings, logger, unified_llm_client, retriever, agent
```

## LLM提供商配置

### 默认提供商：HKGAI
系统默认使用 **HKGAI-V1** API，稳定可靠，无需额外配置。

### 备选提供商：Gemini系列
系统支持使用 **Google Gemini** 系列模型作为备选，支持多个模型和用量监控：

#### Gemini模型列表

- **Gemini 2.5 Pro**: 50 请求/天, 125,000 TPM，适合高质量回答
- **Gemini 2.5 Flash**: 250 请求/天, 250,000 TPM，速度快
- **Gemini 2.0 Flash**: 200 请求/天, 1,000,000 TPM（默认Gemini模型），平衡性能和速度

#### 使用Gemini API

在API请求中指定 `provider: "gemini"`：

```bash
# 使用默认Gemini模型 (2.0 Flash)
curl -X POST "http://localhost:8000/api/rag_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "什么是RAG？", "provider": "gemini"}'

# 指定使用Gemini 2.5 Pro（高质量回答）
curl -X POST "http://localhost:8000/api/rag_query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "详细解释RAG的工作原理",
    "provider": "gemini",
    "model": "gemini-2.5-pro"
  }'

# 指定使用Gemini 2.5 Flash（快速响应）
curl -X POST "http://localhost:8000/api/rag_query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是RAG？",
    "provider": "gemini",
    "model": "gemini-2.5-flash"
  }'
```

#### Agent模式（支持Gemini）

Agent模式也支持指定Gemini模型：

```bash
curl -X POST "http://localhost:8000/api/agent_query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "香港今天天气怎么样？",
    "provider": "gemini",
    "model": "gemini-2.0-flash"
  }'
```

#### 用量监控API

Gemini API提供了完整的用量监控功能：

**查看今日用量统计**：
```bash
# 查看所有模型的统计
curl "http://localhost:8000/api/usage/stats"

# 查看特定模型的统计
curl "http://localhost:8000/api/usage/stats?model=gemini-2.0-flash"
```

**检查配额状态**：
```bash
curl "http://localhost:8000/api/usage/quota?model=gemini-2.0-flash"
```

**获取支持的模型列表**：
```bash
curl "http://localhost:8000/api/models"
```

#### API响应格式

使用Gemini API时，响应包含详细的token使用量和配额信息：

```json
{
  "answer": "回答内容...",
  "context": [...],
  "query": "用户问题",
  "model_used": "gemini-2.0-flash",
  "tokens_used": {
    "input": 150,
    "output": 200,
    "total": 350
  },
  "quota_remaining": 195,
  "answer_source": "rag"
}
```

#### Gemini功能特性

✅ **用量监控与控制**
- 每日请求量监控（RPD - Requests Per Day）
- Token使用量跟踪（输入、输出、总计）
- 自动配额检查，防止超量使用
- 用量数据持久化存储（`usage_data.json`）

✅ **配额管理**
- 系统会自动检查每日配额
- 如果某个模型的配额用完，会返回429错误
- 用量数据每天自动重置（按日期）

✅ **Token计数**
- Gemini API返回准确的token使用量
- 系统会记录并累计每日token使用
- 可在响应中查看每次请求的token消耗

## 多模态文件上传功能

系统支持用户上传多种格式的文件，文件会自动解析、向量化并索引到RAG知识库中。

### 支持的文件类型

- **PDF文件** (`.pdf`) - 自动提取文本内容
- **图片文件** (`.png`, `.jpg`, `.jpeg`, `.gif`) - 使用OCR识别文字
- **代码文件** (`.py`, `.js`, `.java`, `.cpp`, `.c`, `.go`, `.rs`等) - 直接读取代码内容
- **文本文件** (`.txt`, `.md`, `.json`, `.csv`等) - 直接读取文本

### 文件上传API

#### 上传文件

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@/path/to/your/file.pdf"
```

**响应示例**：
```json
{
  "file_id": "abc123...",
  "filename": "document.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "uploaded_at": "2025-10-30T21:00:00",
  "processed": false,
  "already_exists": false,
  "message": "文件上传成功，正在后台处理和索引..."
}
```

#### 列出所有上传的文件

```bash
# 列出所有文件
curl "http://localhost:8000/api/files"

# 按类型筛选
curl "http://localhost:8000/api/files?file_type=pdf"

# 列出未处理的文件
curl "http://localhost:8000/api/files?processed=false"
```

#### 获取文件信息

```bash
curl "http://localhost:8000/api/files/{file_id}"
```

#### 删除文件

```bash
curl -X DELETE "http://localhost:8000/api/files/{file_id}"
```

#### 重新索引文件

```bash
curl -X POST "http://localhost:8000/api/files/{file_id}/reindex"
```

### 在查询中使用上传的文件

上传的文件会自动索引到Milvus，与本地知识库文档一起参与RAG检索。

**指定特定文件进行查询**：

```bash
curl -X POST "http://localhost:8000/api/rag_query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "总结这个文档的主要内容",
    "file_ids": ["file_id_1", "file_id_2"]
  }'
```

这样系统会优先在这些指定的文件中搜索，然后再搜索其他知识库内容。

### 文件处理流程

1. **上传** - 文件保存到 `uploaded_files/` 目录
2. **解析** - 根据文件类型提取文本内容：
   - PDF: 使用PyMuPDF提取文本
   - 图片: 使用Tesseract OCR识别文字（需系统安装Tesseract）
   - 代码: 直接读取源代码
   - 文本: 直接读取内容
3. **切分** - 使用LangChain的RecursiveCharacterTextSplitter切分文本
4. **向量化** - 使用Embedding模型生成向量
5. **索引** - 插入到Milvus向量数据库
6. **标记** - 标记文件为"已处理"状态

### 数据存储架构

系统采用分层存储架构，充分利用各存储介质的优势：

#### 1. 二进制文件存储（文件系统）

**存储位置**：`uploaded_files/` 目录

**存储内容**：
- PDF文件（`.pdf`）
- 图片文件（`.png`, `.jpg`, `.jpeg`, `.gif`）
- 代码文件（`.py`, `.js`, `.java`等）
- 文本文件（`.txt`, `.md`, `.json`等）

**设计原理**：
- 文件系统适合存储二进制数据
- 不占用向量数据库资源
- 访问简单，支持直接文件读取
- **为什么不在Milvus？** Milvus是向量数据库，设计用于存储向量和元数据，不适合存储大量二进制文件

#### 2. 向量和文本存储（Milvus）

**存储位置**：Milvus向量数据库

**存储内容**：
- **向量字段**（`vector`）：文本内容向量化后的embedding（384维）
- **文本字段**（`text`）：从文件提取的文本内容chunks
- **元数据字段**（`source_file`）：文件信息（格式：`"filename||file_id:xxx||file_type:xxx"`）

**存储格式**：
```
Collection: knowledge_base
Fields:
  - id: INT64 (自动生成)
  - text: VARCHAR (文本chunk)
  - vector: FLOAT_VECTOR[384] (embedding向量)
  - source_file: VARCHAR (文件元数据)
  - file_id: VARCHAR (文件ID)
  - file_type: VARCHAR (文件类型)
```

#### 3. 文件元数据存储（可切换后端）

系统支持两种元数据存储方式，可通过配置切换：

**Milvus后端（默认）**：
- 通过查询Milvus的`source_file`字段获取文件元数据
- 所有数据（向量、文本、元数据）统一在Milvus中管理
- 无需额外数据库，适合小到中等规模应用
- 配置：`STORAGE_BACKEND = "milvus"`

**传统数据库后端（可选）**：
- 使用SQLite或PostgreSQL存储文件元数据
- 支持标准SQL查询和复杂过滤
- 更好的并发性能（PostgreSQL）
- 适合大规模数据管理
- 配置：`STORAGE_BACKEND = "database"`，`DATABASE_URL = "sqlite:///./file_storage.db"`

**数据库表结构**（database后端）：
```sql
CREATE TABLE file_metadata (
    file_id VARCHAR PRIMARY KEY,
    filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_type VARCHAR NOT NULL,
    file_size INTEGER NOT NULL,
    uploaded_at DATETIME,
    processed BOOLEAN DEFAULT FALSE,
    chunk_count INTEGER DEFAULT 0,
    metadata_json TEXT
);
```

#### 4. 轻量级索引（JSON文件）

**存储位置**：`file_index.json`

**存储内容**：仅存储`file_id -> file_path`的映射

**用途**：
- 快速查找文件的物理路径
- 补充Milvus查询（获取文件大小、上传时间等静态信息）
- 用于未处理文件的快速查找

#### 存储架构优势

- **分层清晰**：各层职责明确，互不干扰
- **性能优化**：向量检索用Milvus，文件存储用文件系统
- **灵活扩展**：可切换存储后端适应不同规模需求
- **资源高效**：不浪费向量数据库空间存储二进制文件

#### 使用建议

- **开发/测试环境**：使用`milvus`后端（简单，无需额外数据库）
- **生产环境（小规模）**：使用`milvus`后端或SQLite
- **生产环境（大规模）**：使用PostgreSQL后端，获得更好的性能和扩展性

---

## 多语言RAG支持 ⭐

系统现已支持**多语言检索增强生成**，特别针对**粤语、普通话、英语**进行了优化，符合HKGAI-V1论文中提到的多语言环境需求。

### 功能特点

- ✅ **多语言Embedding**：自动检测查询语言并优化检索
- ✅ **混合语言支持**：支持同一查询中包含多种语言
- ✅ **语言检测**：自动识别粤语、普通话、英语及其混合文本
- ✅ **无缝切换**：可在单语言和多语言模式间切换

### 配置多语言RAG

#### 方法1：环境变量（推荐）

在`.env`文件中添加：

```bash
# 启用多语言embedding模型
USE_MULTILINGUAL_EMBEDDING=true

# 多语言embedding模型（默认：paraphrase-multilingual-MiniLM-L12-v2）
MULTILINGUAL_EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
```

#### 方法2：直接修改配置

编辑`services/core/config.py`：

```python
USE_MULTILINGUAL_EMBEDDING = True
MULTILINGUAL_EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
```

### 使用示例

系统会自动检测查询语言并优化检索：

```python
# 普通话查询
query = "什么是RAG系统？"
results = retriever.search(query)

# 粤语查询
query = "RAG系统係乜嘢？"
results = retriever.search(query)

# 英语查询
query = "What is RAG system?"
results = retriever.search(query)

# 混合语言查询
query = "RAG系统是检索增强生成，What does it mean?"
results = retriever.search(query)
```

### 语言检测功能

系统内置语言检测器，可以识别：

- **粤语特征**：嘅、咗、係、啲、佢、咁、咩等特有字符
- **普通话特征**：标准中文
- **英语特征**：ASCII字符
- **混合语言**：同时包含多种语言

### 测试多语言功能

运行测试脚本：

```bash
conda activate ise
python scripts/tests/test_multilingual_rag.py
```

### 性能说明

- **多语言模型**：`paraphrase-multilingual-MiniLM-L12-v2`
  - 支持100+语言
  - 向量维度：384
  - 速度：略慢于单语言模型，但支持多语言混合检索

- **单语言模型**：`all-MiniLM-L6-v2`
  - 向量维度：384
  - 速度：更快
  - 适用：仅处理英语或单一语言

### 建议

- **香港本地化应用**：使用多语言模型（支持粤语、普通话、英语）
- **纯英文应用**：使用单语言模型（速度更快）
- **混合内容知识库**：必须使用多语言模型

## 🎤 Jarvis语音助手

系统现已实现完整的语音交互功能，支持实时语音识别、唤醒词检测和语音合成。

### 功能特点

- ✅ **多语言语音识别**：Whisper支持粤语、普通话、英语
- ✅ **唤醒词检测**：检测"Jarvis"唤醒词并提取查询
- ✅ **文本转语音**：支持多语言语音回复
- ✅ **流式处理**：实时STT/TTS，降低延迟 🚀
- ✅ **Mac MLX优化**：Lightning Whisper MLX和MLX LM，充分利用Apple Silicon 🍎
- ✅ **VAD语音活动检测**：自动检测说话开始和结束
- ✅ **完整集成**：与Agent系统无缝集成

### 快速开始

#### 方式1：实时语音交互（推荐）

访问：`http://localhost:8000/voice`

1. 点击"连接"建立WebSocket连接
2. 点击"开始录音"，授予麦克风权限
3. 说："Jarvis, [你的问题]"
4. 系统自动检测静音并停止录音
5. 查看转录文本和回答

#### 方式2：文件上传

```bash
curl -X POST "http://localhost:8000/api/voice/query" \
  -F "audio=@voice_query.wav" \
  -F 'request={"use_wake_word": true, "use_agent": true}'
```

### 配置说明

在`.env`文件中配置：

```bash
# 启用语音功能
ENABLE_SPEECH=true

# Whisper模型大小（tiny/base/small/medium/large）
WHISPER_MODEL_SIZE=medium

# 唤醒词
WAKE_WORD=jarvis

# 流式处理（推荐）
ENABLE_STREAMING_STT=true
ENABLE_STREAMING_TTS=true

# Mac MLX优化（Mac用户推荐）
USE_MLX=true
MLX_STT_MODEL=base
TTS_TYPE=parler  # 或 melo 或 edge
```

### 内存优化建议

根据测试结果，推荐使用：
- **Faster Whisper**：内存占用降低95%（从4GB降到183MB）
- **Mac用户**：使用MLX优化，内存占用更低
- **Edge TTS**：无需加载模型，内存占用为0

详细说明请参考：`docs/USER_GUIDE.md` 和 `docs/MEMORY_USAGE_RESULTS.md`

---

### 最新优化 ⭐

系统已实现以下优化以提升多语言RAG性能：

#### 1. 改进的混合语言检测
- ✅ 降低混合语言检测阈值（从0.2到0.15）
- ✅ 改进评分算法，更准确识别混合语言文本
- ✅ 优化主要语言判断逻辑

#### 2. 粤语查询优化
- ✅ **检索阶段**：粤语查询自动增加50%候选数量以提高召回率
- ✅ **Reranker阶段**：粤语查询匹配粤语文档时，语言权重提升15%
- ✅ **日志记录**：详细记录优化过程便于调试

#### 3. 多语言知识库
- ✅ 创建了三个测试文档（粤语、普通话、英语）
- ✅ 提供快速索引脚本：`python scripts/utils/index_multilingual_docs.py`
- ✅ 平衡知识库语言分布

#### 使用优化后的系统

1. **索引多语言文档**：
```bash
conda activate ise
python scripts/utils/index_multilingual_docs.py
```

2. **测试优化效果**：
```bash
python scripts/tests/test_multilingual_optimizations.py
```

3. **查询示例**：
   - 普通话：`"什么是RAG系统？"`
   - 粤语：`"RAG系統係乜嘢？"`（会自动优化）
   - 英语：`"What is RAG system?"`

### OCR依赖

如果使用图片OCR功能，需要系统安装Tesseract OCR：

**macOS**:
```bash
brew install tesseract tesseract-lang
```

**Ubuntu/Debian**:
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
```

**Windows**: 从 [Tesseract官网](https://github.com/UB-Mannheim/tesseract/wiki) 下载安装程序

## 配置说明

主要配置在 `services/config.py` 中，你可以根据需要修改：

### Milvus配置
- `MILVUS_HOST`: Milvus主机地址（本地开发使用localhost）
- `MILVUS_PORT`: Milvus端口（默认19530）
- `MILVUS_COLLECTION_NAME`: Milvus集合名称（默认knowledge_base）

### RAG配置
- `EMBEDDING_MODEL`: Embedding模型名称（默认sentence-transformers/all-MiniLM-L6-v2）
- `TOP_K`: 检索返回的文档数量（默认5）
- `CHUNK_SIZE`: 文本切块大小（默认500）
- `CHUNK_OVERLAP`: 文本切块重叠（默认50）

### LLM配置

**HKGAI配置（默认）**：
- `HKGAI_API_KEY`: HKGAI API密钥
- `HKGAI_BASE_URL`: HKGAI API基础URL
- `HKGAI_MODEL_ID`: HKGAI模型ID（默认HKGAI-V1）

**Gemini配置（备选）**：
- `GEMINI_API_KEY`: Gemini API密钥（需要在Google Cloud Console获取）
- `GEMINI_DEFAULT_MODEL`: 默认Gemini模型（默认gemini-2.0-flash）
- `GEMINI_ENABLED`: 是否启用Gemini API（默认True）
- `GEMINI_PROJECT_NUMBER`: Google Cloud项目编号

**文件上传配置**：
- `UPLOAD_STORAGE_DIR`: 上传文件存储目录（默认`uploaded_files`，相对于项目根目录）
- `MAX_UPLOAD_SIZE`: 最大上传文件大小（默认50MB）
- `ALLOWED_EXTENSIONS`: 允许的文件扩展名列表

**存储后端配置**（可切换）：
- `STORAGE_BACKEND`: 存储后端类型，可选：
  - `"milvus"`（默认）：通过查询Milvus获取文件元数据，无需额外数据库
  - `"database"`：使用传统数据库（SQLite或PostgreSQL）存储元数据
- `DATABASE_URL`: 数据库URL（仅用于`database`后端）
  - SQLite示例：`"sqlite:///./file_storage.db"`
  - PostgreSQL示例：`"postgresql://user:password@localhost/dbname"`

## 常见问题

### 1. Milvus连接失败

**检查Docker状态**：
```bash
# 检查Docker是否运行
docker ps

# 检查Milvus容器状态
docker compose ps
# 或
docker-compose ps
```

**常见问题排查**：
- **Docker未启动**：启动Docker Desktop
- **容器未运行**：运行 `docker compose up -d` 启动容器
- **容器启动失败**：查看日志 `docker compose logs standalone`
- **端口被占用**：检查19530端口是否被其他程序占用
- **重启Milvus**：
  ```bash
  docker compose restart standalone
  # 或完全重启
  docker compose down
  docker compose up -d
  ```

**查看Milvus日志**：
```bash
# 查看所有服务日志
docker compose logs

# 查看特定容器日志
docker compose logs standalone
docker compose logs etcd
docker compose logs minio
```

### 2. 导入错误

确保：
- 已激活正确的conda环境
- 已安装所有依赖：`pip install -r requirements.txt`
- 在项目根目录运行命令
- 使用正确的启动命令：`uvicorn backend.main:app --reload`

### 3. 文档处理失败

- 确保PDF文件没有加密
- 检查PDF文件是否损坏
- 查看脚本输出的错误信息

### 4. API返回空结果

- 确保已运行数据注入脚本
- 检查Milvus中是否有数据：查看脚本输出的统计信息
- 尝试使用更简单的查询问题

### 5. Gemini API相关问题

**配额已用完错误**：
```json
{
  "detail": "模型 gemini-2.0-flash 今日配额已用完",
  "headers": {
    "X-Quota-Info": "{...}"
  }
}
```
- 解决方案：使用其他Gemini模型或切换回HKGAI（默认provider）

**API Key无效**：
- 检查 `services/config.py` 中的 `GEMINI_API_KEY` 是否正确
- 确保API Key在Google Cloud Console中已启用"Generative Language API"
- Google API Key通常以 `AIza` 开头

**请求超时**：
- Gemini API可能需要更长时间响应，已设置30秒超时
- 如果经常超时，考虑使用更快的模型（如gemini-2.5-flash）

### 6. 文件上传和处理问题

**文件上传失败**：
- 检查文件大小是否超过限制（默认50MB）
- 检查文件类型是否在允许列表中
- 查看终端错误日志

**文件处理失败**：
- PDF处理失败：确保PyMuPDF已安装（`pip install PyMuPDF`）
- 图片OCR失败：检查是否安装了系统级Tesseract OCR
- 代码文件处理失败：检查文件编码是否为UTF-8

**存储后端问题**：
- 如果使用database后端，检查数据库文件是否可写
- 如果使用Milvus后端，确保Milvus服务正常运行

## 依赖说明

### 必需依赖

所有核心功能需要的依赖已包含在`requirements.txt`中：
- **FastAPI、Uvicorn**：Web框架和ASGI服务器
- **PyMuPDF、python-docx**：文档处理
- **sentence-transformers、langchain**：向量化和文本处理
- **pymilvus**：向量数据库客户端
- **sqlalchemy**：数据库支持（传统数据库后端）
- **Pillow**：图片处理基础库

### 可选依赖

以下依赖为可选，未安装时相关功能会被禁用，但不影响系统运行：

- **pytesseract**：图片OCR识别
  - Python包：`pip install pytesseract`
  - 系统依赖：需要安装Tesseract OCR
    - macOS: `brew install tesseract tesseract-lang`
    - Ubuntu: `sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim`
  - 如果未安装：图片上传功能仍可用，但无法进行OCR识别

### 自动安装的依赖

以下依赖会通过其他包自动安装，无需手动指定：
- numpy, scipy, scikit-learn（sentence-transformers）
- transformers（sentence-transformers）
- pandas, pyarrow（pymilvus）
- torch（sentence-transformers，可能需要较大空间）

## 已完成的改进功能

### ✅ 高优先级功能（全部完成）

1. **✅ 日志系统改进**
   - 统一的日志管理（`services/core/logger.py`）
   - 支持控制台和文件输出（`logs/rag_system.log`）
   - 日志轮转（最大10MB，保留5个备份）
   - 可通过`LOG_LEVEL`环境变量配置日志级别

2. **✅ 环境变量支持完善**
   - 所有配置项支持环境变量覆盖
   - 自动加载`.env`文件
   - 配置加载辅助函数（`get_env()`, `get_env_bool()`, `get_env_int()`）

3. **✅ Reranker功能实现**
   - 交叉编码器重排序（`cross-encoder/ms-marco-MiniLM-L-6-v2`）
   - 集成到检索流程，提升结果相关性
   - 可通过`USE_RERANKER`环境变量启用/禁用（默认启用）

4. **✅ Agent工具扩展**
   - 金融数据工具：股票价格查询（Yahoo Finance）、加密货币价格查询（CoinGecko）
   - 交通查询工具：旅行时间和路线查询（OpenRouteService）
   - Agent现在支持5种工具：本地RAG、网页搜索、天气、金融、交通

5. **✅ 代码重构**
   - Services目录模块化重构
   - 按功能分类：`core/`, `llm/`, `vector/`, `storage/`, `agent/`
   - 保持向后兼容，旧导入方式仍可用

6. **✅ Jarvis语音助手** 🎤
   - 语音识别（Whisper，支持多语言）
   - 唤醒词检测（"Jarvis"）
   - 文本转语音（Edge TTS）
   - WebSocket实时交互

7. **✅ 流式STT/TTS** 🚀
   - Faster Whisper（流式语音识别，内存占用低95%）
   - Parler-TTS / MeloTTS（流式语音合成）
   - 实时处理，降低延迟

8. **✅ Mac MLX优化** 🍎
   - Lightning Whisper MLX（Mac优化的语音识别）
   - MLX LM（Mac优化的语言模型，4bit量化）
   - 充分利用Apple Silicon性能

9. **✅ 依赖兼容性修复**
   - 修复transformers版本兼容性问题
   - 添加兼容性补丁
   - 确保所有模块正常导入

### 🟡 中优先级功能（待实现）

- 测试覆盖（pytest）
- API速率限制
- 统一错误处理
- 配置文件验证

### 🟢 低优先级功能（待实现）

- 缓存机制
- 批量处理优化
- 健康检查增强
- API文档增强

详细改进建议请参考代码注释或开发文档。

## 注意事项

- **内存要求**: 本地开发建议至少16GB RAM（主要用于Embedding模型和向量检索）
- **磁盘空间**: 
  - Embedding模型和依赖：约2-3GB
  - Milvus数据目录：根据文档数量增长
  - 上传文件目录：根据用户上传文件大小
- **API密钥安全**: 
  - `services/config.py` 中的API密钥需要妥善保管
  - 生产环境应使用环境变量而不是硬编码
  - 建议将包含API密钥的配置文件加入`.gitignore`
  - 使用密钥管理服务（如AWS Secrets Manager、Azure Key Vault）管理密钥
- **数据安全**: 
  - 本地开发时注意不要将敏感数据提交到Git
  - 上传文件目录和数据库文件已加入`.gitignore`
- **存储后端选择**:
  - 开发/小规模：使用Milvus后端（默认），无需额外数据库
  - 生产/大规模：使用PostgreSQL后端，获得更好的性能和扩展性
- **Gemini用量数据**: 用量数据存储在`usage_data.json`（已加入`.gitignore`），每天按日期自动重置
- **向后兼容**: 系统完全支持HKGAI API（默认），Gemini为可选备选方案

## 获取帮助

如有问题，请：
1. 查看FastAPI文档：`http://localhost:8000/docs`
2. 检查Milvus日志：`docker-compose logs milvus-standalone`
3. 查看应用日志：终端输出的错误信息
4. 参考项目文档：`docs/Final WarmUp.md`
