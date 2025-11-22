# 📂 项目目录结构说明

## 根目录文件

```
Final/
├── 📄 README.md                    # 项目主文档
├── 📄 LICENSE                      # 开源许可证
├── 📄 CONTRIBUTING.md              # 贡献指南
├── 📄 PROJECT_STRUCTURE.md         # 项目结构概览
├── 📄 requirements.txt             # Python依赖
├── 📄 docker-compose.yml           # Docker编排配置
└── 📄 .env                         # 环境变量（不在git中）
```

---

## 核心代码目录

### 📁 `backend/` - 后端API服务
```
backend/
├── main.py          # FastAPI应用入口
├── api.py           # API路由定义
└── models.py        # Pydantic数据模型
```

### 📁 `services/` - 业务逻辑服务
```
services/
├── core/            # 核心配置和工具
│   ├── config.py    # 配置管理
│   ├── logger.py    # 日志系统
│   └── cache.py     # 缓存系统
├── llm/             # LLM客户端
│   ├── hkgai_client.py          # HKGAI接口
│   ├── gemini_client.py         # Gemini接口
│   ├── doubao_multimodal.py     # 豆包多模态接口
│   └── unified_client.py        # 统一LLM客户端
├── agent/           # Agent智能体
│   ├── agent.py              # Agent主逻辑
│   ├── workflow_dynamic.py   # 动态工作流
│   ├── planner.py            # LLM规划器
│   └── tools/                # Agent工具集
├── vector/          # 向量数据库
│   ├── milvus_client.py      # Milvus客户端
│   ├── retriever.py          # 检索器
│   └── embedder.py           # Embedding模型
├── speech/          # 语音服务
│   ├── voice_service.py      # 语音服务主入口
│   ├── whisper_stt.py        # Whisper STT
│   ├── hkgai_stt.py          # HKGAI STT（粤语）
│   └── edge_tts_service.py   # Edge TTS
├── vision/          # 视觉服务
│   ├── image_processor.py    # 图像处理
│   └── image_history.py      # 图像历史
├── storage/         # 文件存储
│   ├── file_storage.py       # 文件存储管理
│   ├── file_processor.py     # 文件处理
│   └── file_indexer.py       # 文件索引
└── tools/           # 工具服务
    └── tavily_search.py      # Tavily搜索API
```

### 📁 `frontend/` - 前端页面
```
frontend/
├── voice_assistant.html      # 语音助手界面
└── README.md                 # 前端说明
```

### 📁 `scripts/` - 工具脚本
```
scripts/
├── build_knowledge_base.py   # 构建知识库
├── tests/                    # 测试脚本
│   ├── test_speech_to_agent.py      # 语音交互测试
│   ├── test_agent_with_cantonese_tts.py  # Agent+TTS测试
│   ├── test_doubao_multimodal.py    # 豆包多模态测试
│   └── ...
└── utils/                    # 工具脚本
    └── ...
```

---

## 数据和资源目录

### 📁 `data/` - 数据存储
```
data/
├── file_index.json           # 文件索引
└── image_history/            # 多模态会话图片历史
```

### 📁 `documents/` - 知识库文档
```
documents/
├── multilingual_rag_guide_zh.md    # 中文文档
├── multilingual_rag_guide_yue.md   # 粤语文档
├── multilingual_rag_guide_en.md    # 英文文档
└── test_document.pdf               # 测试文档
```

### 📁 `uploaded_files/` - 用户上传文件
- 用户通过API上传的文档存储位置

### 📁 `figures/` - 图片资源
```
figures/
├── hkust.png        # 香港科技大学图片
├── snack.png        # 测试图片
└── error_info.png   # 错误信息截图
```

---

## 输出和日志目录

### 📁 `logs/` - 系统日志
```
logs/
├── rag_system.log                # 系统运行日志
├── backend.log                   # 后端日志
├── test_set3_hkgai.log          # 测试集3日志
├── test_hkgai_vs_doubao.log     # LLM对比测试日志
├── test_agent_with_tools.log    # Agent工具测试日志
└── ...
```

### 📁 `test_results/` - 测试结果
```
test_results/
├── test_agent_with_tools_results.json     # Agent测试结果
├── test_hkgai_vs_doubao_results.json     # LLM对比结果
└── usage_data.json                        # API使用统计
```

### 📁 `speech_questions_audio/` - 语音问题库
```
speech_questions_audio/
├── set1_q1_question.mp3   # 问题音频
├── set1_q1_answer.mp3     # 回答音频（完整Agent流程）
├── set1_q2_question.mp3
├── set1_q2_answer.mp3
└── ...                     # 测试集1和2的所有语音文件
```

### 📁 `agent_tts_output/` - Agent回答音频
```
agent_tts_output/
├── set1_q1.mp3            # Agent回答的粤语音频
├── set1_q2.mp3
└── ...                     # 测试集的Agent回答
```

### 📁 `test_audio/` - 测试音频样本
```
test_audio/
├── cantonese_door_warning_edge.mp3         # 粤语门警告
├── cantonese_station_announce_edge.mp3     # 粤语站点播报
└── test_*.wav                              # 各种TTS测试
```

---

## 文档目录

### 📁 `docs/` - 项目文档
```
docs/
├── README.md                     # 文档目录索引
├── USER_GUIDE.md                 # 用户指南
├── WORKFLOW_ARCHITECTURE.md      # 架构文档
├── RAG_RESEARCH_FINDINGS.md      # RAG研究成果
├── FRONTEND_DESIGN_SPEC.md       # 前端设计规范
├── TAVILY_SETUP.md               # Tavily搜索配置
├── HKGAI Speech Services.md      # HKGAI语音API文档
├── HK Speech API.md              # 香港语音API说明
├── SETUP_API_KEYS.md             # API密钥配置指南
├── START_API.md                  # 启动API指南
├── GIT_SETUP.md                  # Git配置指南
├── TESTING.md                    # 测试指南
├── DIRECTORY_STRUCTURE.md        # 本文档
├── Test Questions Set 1.docx     # 测试问题集1
├── Test Questions Set 2.docx     # 测试问题集2
├── Test Questions Set 3.docx     # 测试问题集3
├── figures/                      # 文档配图
│   ├── architecture.png
│   ├── workflow.png
│   ├── tech_stack.png
│   ├── api_usage.png
│   └── performance.png
└── archive/                      # 归档的旧文档
    └── ...
```

---

## 模型目录

### 📁 `mlx_models/` - MLX模型缓存
```
mlx_models/
└── tiny/                    # Whisper Tiny模型
    ├── config.json
    └── weights.npz
```

---

## 核心文件说明

| 文件 | 说明 |
|------|------|
| `README.md` | 项目主文档，包含安装、使用说明 |
| `requirements.txt` | Python依赖列表 |
| `docker-compose.yml` | Docker服务编排（Milvus、MinIO、etcd） |
| `.env` | 环境变量配置（API密钥等，不提交到git） |
| `PROJECT_STRUCTURE.md` | 项目结构概览 |

---

## 快速导航

### 🚀 开发者
- **配置API密钥**: `docs/SETUP_API_KEYS.md`
- **启动服务**: `docs/START_API.md`
- **测试系统**: `docs/TESTING.md`
- **架构文档**: `docs/WORKFLOW_ARCHITECTURE.md`

### 👤 用户
- **用户指南**: `docs/USER_GUIDE.md`
- **语音助手**: 打开浏览器访问 `http://localhost:5555/voice`

### 🔧 维护者
- **查看日志**: `logs/rag_system.log`
- **测试结果**: `test_results/`
- **贡献代码**: `CONTRIBUTING.md`

---

## 文件命名规范

### Python模块
- 小写+下划线: `hkgai_client.py`
- 功能清晰: `file_processor.py`

### 文档
- 大写+下划线: `USER_GUIDE.md`
- 功能描述: `TAVILY_SETUP.md`

### 音频文件
- 问题音频: `set{N}_q{N}_question.mp3`
- 回答音频: `set{N}_q{N}_answer.mp3`
- 测试音频: `test_*.wav`

### 日志文件
- 系统日志: `{service}.log`
- 测试日志: `test_{name}.log`

### 测试结果
- JSON格式: `test_{name}_results.json`

---

## 清理建议

### 定期清理
```bash
# 清理旧日志（保留最近7天）
find logs/ -name "*.log" -mtime +7 -delete

# 清理测试音频（可选）
rm -f test_audio/test_*.wav

# 清理临时文件
rm -f *.pyc
find . -type d -name "__pycache__" -exec rm -rf {} +
```

### 忽略文件（.gitignore）
- `logs/*.log`
- `test_results/*.json`
- `test_audio/*.wav`
- `uploaded_files/`
- `data/image_history/`
- `__pycache__/`
- `.env`

---

**📌 提示**: 此结构已于2025-11-22整理完成，保持这个结构有助于项目维护！

