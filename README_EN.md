# Jude - Voice-First AI Agent System

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![Milvus](https://img.shields.io/badge/Milvus-2.3+-orange.svg)](https://milvus.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Intelligent Voice Assistant supporting Cantonese 🇭🇰 | Mandarin 🇨🇳 | English 🇺🇸**

[Features](#-core-innovations) • [Quick Start](#-quick-start) • [Architecture](#️-system-architecture) • [Demo](#-live-demo) • [Documentation](#-documentation)

[中文README](README.md)

</div>

---

## 📖 Project Overview

**Jude** is a production-grade voice-first AI Agent system developed for MAIE5221 NLP Final Project. The system integrates multimodal RAG, real-time voice interaction, dual-LLM architecture, and dynamic tool orchestration to provide seamless intelligent Q&A experiences.

> 📄 **[View Full Project Report (Final_Report.pdf)](Final_Report.pdf)** - 20-page technical documentation with system architecture, implementation details, evaluation results, and deployment strategies.

### 🎯 Three Core Innovations

1. **🎙️ Streamed Voice Interaction**
   - Real-time STT with Web Speech API (streaming recognition)
   - Low-latency TTS via Edge TTS (Cantonese & Mandarin support)
   - Intelligent TTS triggering (auto-detect questions requiring voice responses)

2. **🧠 Cantonese Optimization & Dual-Brain System**
   - **HKGAI-V1**: Specialized in Chinese text understanding and Hong Kong local knowledge
   - **Doubao Seed-1-6**: Handles multimodal tasks (image understanding, OCR)
   - Intelligent task routing, cost-effective architecture

3. **⚡ Dynamic Workflow Orchestration**
   - LLM-driven intelligent tool selection (5+ external APIs)
   - Two-stage RAG retrieval + Cross-encoder reranking
   - Automatic fallback mechanism (RAG → Web Search → Direct LLM)

---

## ✨ Core Features

### 🤖 Intelligent Agent System
- ✅ **Dynamic Tool Routing**: Auto-select Local RAG / Web Search / Weather / Finance / Transport
- ✅ **LangGraph Workflow**: State management + parallel execution
- ✅ **Intent Recognition**: translation / weather / finance / rag / web query classification
- ✅ **Smart Fallback**: Auto-cascade to backup tools on primary tool failure

### 🔍 Advanced RAG System
- ✅ **Two-Stage Retrieval**: Milvus cosine similarity (top-20) → Cross-encoder reranking (top-5)
- ✅ **Multilingual Embedding**: paraphrase-multilingual-MiniLM-L12-v2 (384-dim)
- ✅ **Smart Chunking**: 512 tokens + 50-token overlap, metadata preservation
- ✅ **Credibility Weighting**: 0.7 semantic + 0.2 recency + 0.1 source trust

### 🎤 Voice Interaction
- ✅ **Real-time STT**: Web Speech API (zh-CN) + Whisper fallback
- ✅ **Natural TTS**: Edge TTS HiuGaaiNeural (Cantonese), XiaoxiaoNeural (Mandarin)
- ✅ **Smart Broadcast**: Agent auto-marks `should_speak` field to trigger TTS
- ✅ **Language Detection**: Auto-detect query language and route to appropriate TTS voice

### 🖼️ Multimodal Processing
- ✅ **Image Recognition**: Doubao vision model (Seed-1-6-251015)
- ✅ **OCR**: Chinese & English text extraction
- ✅ **Image History**: Session-based tracking, contextual reference support
- ✅ **Document Parsing**: Automatic PDF & DOCX extraction and indexing

### 🌐 External API Integration
- ✅ **Tavily AI Search**: Real-time web search (primary tool)
- ✅ **wttr.in**: Free weather queries (no API key required)
- ✅ **Yahoo Finance (yfinance)**: Stock & financial data
- ✅ **HK Transport API**: Hong Kong transit route queries
- ✅ **DuckDuckGo Search**: Backup search engine

### 🎨 Interactive Frontend
- ✅ **Landing Page**: 3D scroll animations, gradient text effects, FAQ accordion
- ✅ **System Dashboard**: 5-page fullscreen scroll (Data Flow / Features / Optimized Performance / Q&A / Team)
- ✅ **Demo Interface**: Real-time chat, voice input, image upload, auto-play TTS
- ✅ **Responsive Design**: Pink-purple gradient theme, glassmorphism style

---

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.10+
- **Node.js**: 18+
- **Docker Desktop**: For Milvus vector database
- **API Keys**: HKGAI, Doubao, Tavily (see [API Setup](#-api-configuration))

### Installation

#### 1️⃣ Clone Repository

```bash
git clone https://github.com/AnonymityHE/MAIE-5221-NLP-Final.git
cd MAIE-5221-NLP-Final
```

#### 2️⃣ Backend Setup

```bash
# Create virtual environment
conda create -n ise python=3.10
conda activate ise

# Install dependencies
pip install -r requirements.txt

# Configure API keys (see .env.example)
cp .env.example .env
# Edit .env with your API keys
```

#### 3️⃣ Start Docker Services

```bash
# Start Milvus, MinIO, etcd
docker compose up -d

# Verify services
docker ps
```

#### 4️⃣ Build Knowledge Base

```bash
# Index documents into Milvus
python scripts/build_knowledge_base.py
```

#### 5️⃣ Start Backend Server

```bash
# Start FastAPI backend
uvicorn backend.main:app --host 0.0.0.0 --port 5555
```

#### 6️⃣ Start Frontend (Optional)

```bash
cd frontend
npm install
npm run dev
```

### Access System

- **Landing Page**: http://localhost:5173
- **API Documentation**: http://localhost:5555/docs
- **Health Check**: http://localhost:5555/api/health

---

## 🏗️ System Architecture

```
┌─────────────┐
│   User      │ (Voice / Text / Image)
└──────┬──────┘
       │
┌──────▼──────────────────────────────────────┐
│           Frontend (React + Vite)            │
│  • Landing Page  • Dashboard  • Demo UI     │
└──────┬──────────────────────────────────────┘
       │ HTTP/WebSocket
┌──────▼──────────────────────────────────────┐
│         Backend (FastAPI + Uvicorn)          │
│  ┌─────────────────────────────────────┐    │
│  │      Agent System (LangGraph)       │    │
│  │  • Intent Detection                 │    │
│  │  • Tool Routing                     │    │
│  │  • Workflow Orchestration           │    │
│  └────┬────────────────────────────────┘    │
│       │                                      │
│  ┌────▼──────┐  ┌──────────┐  ┌─────────┐  │
│  │    RAG    │  │ LLM APIs │  │  Tools  │  │
│  │  (Milvus) │  │ HKGAI    │  │ Tavily  │  │
│  │  Rerank   │  │ Doubao   │  │ Finance │  │
│  └───────────┘  └──────────┘  │ Weather │  │
│                                └─────────┘  │
└───────────────────────────────────────────────┘
```

---

## 📊 Performance Metrics

### Complete Test Suite (December 2025 - Post-Optimization)

**Test Scale**: 111 queries across 3 test sets

| Metric | Value |
|--------|-------|
| **Total Queries** | 111 |
| **Success Rate** | **100%** (111/111) |
| **Tool Routing Accuracy** | **100%** |
| **Avg Response Time** | **6.98s** |
| **Performance Improvement** | **82.7%** ⬆️ (from 40.44s) |

#### By Test Set

| Test Set | Queries | Success Rate | Avg Response Time | Before Optimization | Improvement |
|----------|---------|-------------|------------------|---------------------|-------------|
| **Test Set 1** (Basic) | 48 | **100%** | **4.98s** | 36.88s | **86.5%** |
| **Test Set 2** (Advanced) | 45 | **100%** | **6.45s** | 39.95s | **83.8%** |
| **Test Set 3** (Complex) | 18 | **100%** | **13.66s** | 50.51s | **73.0%** |

#### By Tool Usage

| Tool | Invocations | Usage Rate | Primary Use Case |
|------|-------------|-----------|------------------|
| Direct LLM | 53 | 47.7% | General knowledge, simple Q&A |
| Web Search | 32 | 28.8% | Real-time info, current events |
| Finance API | 13 | 11.7% | Stock prices, market data |
| Local RAG | 8 | 7.2% | Technical docs, KB queries |
| Weather API | 7 | 6.3% | Weather forecasts, conditions |

**Key Optimization Results**:
- 🚀 **Intelligent LLM Workflow Planning**: 90% of simple queries skip unnecessary planning steps, saving ~13s per request
- ✅ **Perfect Accuracy**: 100% success rate + 100% tool routing accuracy
- ⚡ **Fast Response**: Average 6.98s (basic queries only 4.98s)

### Initial Test Sets (Test Sets 1-3)

| Metric | Test Set 1 | Test Set 2 | Test Set 3 | Average |
|--------|-----------|-----------|-----------|---------|
| **Mean Search Time** | 0.52s | 0.68s | 1.12s | **0.77s** |
| **Total Response Latency** | 1.85s | 2.10s | 3.45s | **2.47s** |
| **Accuracy** | 95.0% | 88.5% | 92.0% | **91.8%** |
| **Test Queries** | 10 | 8 | 12 | **30** |

### Multimodal Testing

- **Image Recognition**: ✅ Recognizes landscapes, objects, text content
- **OCR Accuracy**: 95%+ (Chinese & English mixed documents)
- **Session Tracking**: ✅ Supports referencing historical images in multi-turn dialogues

---

## 🎬 Live Demo

### 💬 Text Query Examples

```bash
# Local knowledge query (triggers Local RAG)
curl -X POST "http://localhost:5555/api/agent_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Where is HKUST located?"}'

# Real-time information query (triggers Web Search)
curl -X POST "http://localhost:5555/api/agent_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the latest tech news today?"}'

# Translation query (triggers Direct LLM + Auto TTS)
curl -X POST "http://localhost:5555/api/agent_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "How do you say please stand clear of the doors in Cantonese?"}'
```

### 🎙️ Voice Query Example

Open frontend demo page → Click voice button → Speak your question

### 🖼️ Image Query Example

Open frontend demo page → Upload image → Ask "What's in this image?"

---

## 🔧 API Configuration

Create `.env` file in project root:

```bash
# === LLM Configuration ===
HKGAI_API_KEY=your_hkgai_key
HKGAI_BASE_URL=https://oneapi.hkgai.net/v1
HKGAI_DEFAULT_MODEL=HKGAI-V1

DOUBAO_API_KEY=your_doubao_key
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_DEFAULT_MODEL=doubao-seed-1-6-lite-251015
DOUBAO_DEFAULT_OCR_MODEL=doubao-seed-1-6-251015

# === External APIs ===
TAVILY_API_KEY=your_tavily_key

# === Milvus Configuration ===
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=knowledge_base

# === RAG Configuration ===
USE_MULTILINGUAL_EMBEDDING=true
MULTILINGUAL_EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
USE_RERANKER=true
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
TOP_K=20
RERANK_TOP_K=5
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# === Voice Configuration ===
TTS_PROVIDER=edge
CANTONESE_TTS_VOICE=zh-HK-HiuGaaiNeural
MANDARIN_TTS_VOICE=zh-CN-XiaoxiaoNeural
TTS_RATE=+0%
TTS_VOLUME=+0%
```

---

## 📁 Project Structure

```
.
├── backend/                  # FastAPI backend
│   ├── main.py              # Main application
│   ├── api.py               # API routes
│   └── models.py            # Data models
├── services/                 # Core services
│   ├── agent/               # Agent system (12 files)
│   │   ├── agent.py         # Main agent logic
│   │   ├── intent_detector.py
│   │   ├── workflow.py      # LangGraph workflow
│   │   └── tool_executor.py
│   ├── llm/                 # LLM integration (8 files)
│   │   ├── hkgai_client.py
│   │   ├── doubao_client.py
│   │   └── llm_interface.py
│   ├── speech/              # Speech processing (15 files)
│   │   ├── stt_service.py
│   │   ├── tts_service.py
│   │   └── edge_tts_service.py
│   ├── vector/              # Vector DB (5 files)
│   │   ├── milvus_client.py
│   │   └── embeddings.py
│   ├── vision/              # Vision processing (3 files)
│   │   └── doubao_vision.py
│   ├── storage/             # File storage (6 files)
│   │   └── file_manager.py
│   └── tools/               # External tools (1 file)
│       └── search_tools.py
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── presentation/
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   └── ScrollSection.tsx
│   │   │   └── GradientText.tsx
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx
│   │   │   └── DemoInterface.tsx
│   │   └── App.tsx
│   ├── public/              # Static assets
│   └── package.json
├── scripts/                  # Utility scripts
│   ├── build_knowledge_base.py
│   ├── tests/               # Test scripts (16 files)
│   └── utils/               # Utilities (8 files)
├── docs/                     # Documentation
│   ├── Final_Report.pdf     # Project report (20 pages)
│   ├── Final_Report.tex     # LaTeX source
│   ├── generate_architecture_diagram_v4.py
│   ├── generate_deployment_diagram.py
│   └── visualizations/      # Generated charts (8 PNG files)
├── documents/                # Knowledge base documents (PDF/DOCX)
├── logs/                     # Test logs
├── docker-compose.yml        # Docker configuration (Milvus + MinIO + etcd)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## 📚 Documentation

### 📄 Final Report
- **[Final_Report.pdf](Final_Report.pdf)** - Complete project report (20 pages)
  - System architecture design
  - Core technology implementation (RAG, Agent, Voice, Multimodal)
  - Evaluation results (40 query tests, 77.5% tool routing accuracy)
  - Deployment architecture diagram
  - Complete references
  - 📍 Also available at [docs/Final_Report.pdf](docs/Final_Report.pdf)

### 📖 Technical Documentation
- **[Frontend Design Spec](docs/FRONTEND_DESIGN_SPEC.md)** - UI/UX design, API interfaces
- **[Agent Architecture](docs/WORKFLOW_ARCHITECTURE.md)** - LangGraph workflow details
- **[Presentation Script](docs/PRESENTATION_SCRIPT.md)** - 5-minute presentation script
- **[Tavily Integration Guide](docs/TAVILY_SETUP.md)** - Web search tool configuration

---

## 👥 Team

| Name | Student ID | Key Responsibilities |
|------|------------|----------------------|
| **Yunlin He** | 21270701 | Overall project management, system architecture design, Agent system and LangGraph workflow implementation, and integrating all components |
| **Letian Wang** | 21211913 | Implementing specialized tools (Weather, Finance, Transport, Web Search), API integration, and managing external service connections and error handling |
| **Ziyao Su** | 21272577 | Document processing pipeline, multimodal support (file upload, audio/voice), Milvus vector database management, and knowledge base indexing |
| **Ziyu Jing** | 21280146 | RAG retrieval optimization, reranking and filtering implementation, caching mechanisms, performance optimization, and system testing |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Professor Xue Wei for guidance and support throughout the project
- HKUST MAIE Program for providing the learning platform
- Open-source community for tools like Milvus, FastAPI, and React

---

## 📞 Contact

- **GitHub**: [AnonymityHE/MAIE-5221-NLP-Final](https://github.com/AnonymityHE/MAIE-5221-NLP-Final-Intelligent-Search-Engine)
- **Live Demo**: [https://jude.darkdark.me](https://jude.darkdark.me)
- **Email**: Contact via GitHub Issues

---

<div align="center">

**Built with ❤️ by Team Jude**

*HKUST MAIE5221 Natural Language Processing - Final Project*

</div>

