# 配置和安装指南

## 📋 目录
1. [环境配置](#环境配置)
2. [API密钥配置](#api密钥配置)
3. [模型配置](#模型配置)
4. [知识库配置](#知识库配置)
5. [依赖安装](#依赖安装)
6. [流式STT/TTS和MLX优化](#流式stttts和mlx优化)

---

## 🔧 环境配置

### 基础环境

```bash
# 激活conda环境
conda activate ise

# 安装基础依赖
pip install -r requirements.txt
```

### 创建.env文件

复制 `.env.example` 创建 `.env`：

```bash
cp .env.example .env
```

### 必需配置项

```bash
# LLM配置（至少配置一个）
HKGAI_API_KEY=your_hkgai_key
HKGAI_API_URL=https://api.hkg.ai/v1/chat/completions

# 或使用DeepSeek
DEEPSEEK_API_KEY=your_deepseek_key

# 向量数据库
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=rag_documents

# 语音功能（可选）
ENABLE_SPEECH=true
WHISPER_MODEL_SIZE=medium
WAKE_WORD=jarvis
USE_EDGE_TTS=true
```

---

## 🔑 API密钥配置

### Google搜索API（可选）

1. **创建项目**：https://console.cloud.google.com/
2. **启用Custom Search API**
3. **创建API密钥**：凭据 → 创建凭据 → API密钥
4. **创建搜索引擎**：https://programmablesearchengine.google.com/
5. **配置.env**：
   ```bash
   GOOGLE_API_KEY=your_api_key
   GOOGLE_SEARCH_ENGINE_ID=your_engine_id
   ```

**注意**：如果未配置，系统会自动使用DuckDuckGo（无需配置）

### HKGAI API

1. **获取API密钥**：联系HKGAI获取
2. **配置.env**：
   ```bash
   HKGAI_API_KEY=your_key
   HKGAI_API_URL=https://api.hkg.ai/v1/chat/completions
   ```

### DeepSeek API（备选）

1. **注册账户**：https://www.deepseek.com/
2. **获取API密钥**
3. **配置.env**：
   ```bash
   DEEPSEEK_API_KEY=your_key
   ```

---

## 🎤 模型配置

### Whisper语音识别模型

**默认**：`medium`（高准确度，约769MB）

```bash
# .env配置
WHISPER_MODEL_SIZE=medium  # tiny/base/small/medium/large
```

**模型对比**：
| 模型 | 大小 | 速度 | 准确度 | 推荐场景 |
|------|------|------|--------|---------|
| tiny | 39MB | 最快 | 较低 | 快速测试 |
| base | 74MB | 快 | 良好 | 一般用途 |
| small | 244MB | 中等 | 很好 | 高质量需求 |
| **medium** | **769MB** | **慢** | **优秀** | **生产环境（推荐）** |
| large | 1550MB | 最慢 | 最佳 | 最高质量 |

**安装依赖**：
```bash
pip install openai-whisper soundfile
```

### 多语言Embedding模型

**默认多语言模型**：`paraphrase-multilingual-MiniLM-L12-v2`

```bash
# .env配置
USE_MULTILINGUAL_EMBEDDING=true
MULTILINGUAL_EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
```

**单语言模型**（仅英语）：
```bash
USE_MULTILINGUAL_EMBEDDING=false
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Silero VAD（可选）

**后端语音活动检测**，自动去除静音：

```bash
# 安装依赖
pip install torch silero-vad onnxruntime

# 启用（默认）
USE_SILERO_VAD=true

# 禁用
USE_SILERO_VAD=false
```

---

## 📚 知识库配置

### Milvus向量数据库

**使用Docker启动**：
```bash
docker compose up -d
```

**配置.env**：
```bash
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=knowledge_base
```

### 索引文档

1. **准备文档**：放入 `docs/` 目录（支持PDF、TXT、MD、DOCX）
2. **索引文档**：
   ```bash
   # 索引虚构知识库
   python scripts/utils/index_fictional_kb.py
   
   # 或使用通用索引脚本
   python scripts/utils/ingest.py documents/your_file.pdf
   ```
3. **检查索引**：
   ```bash
   python scripts/utils/check_knowledge_base.py
   ```

---

## 📦 依赖安装

### 必需依赖

```bash
# 基础框架
pip install fastapi uvicorn pydantic python-dotenv

# 向量数据库
pip install pymilvus

# Embedding模型
pip install sentence-transformers

# LLM客户端
pip install requests openai

# 文档处理
pip install PyPDF2 python-docx python-docx2txt

# 语音识别（如果启用）
pip install openai-whisper soundfile edge-tts pydub

# 音频处理（可选）
pip install torch silero-vad onnxruntime
```

### 完整安装

```bash
# 安装所有依赖
pip install -r requirements.txt
```

---

## 🚀 流式STT/TTS和MLX优化

### 1. 基础流式STT（必需）

```bash
# Faster Whisper（更快的流式STT）
pip install faster-whisper
```

### 2. 流式TTS（可选）

#### 选项A：Parler-TTS（推荐，流式输出）
```bash
# 安装Parler-TTS
pip install parler-tts

# 还需要安装transformers（通常已安装）
pip install transformers
```

#### 选项B：MeloTTS（多语言，Mac优化）
```bash
# MeloTTS需要从GitHub安装（不是标准pip包）
pip install git+https://github.com/myshell-ai/MeloTTS.git

# 安装unidic（日语支持，可选）
python -m unidic download
```

**注意**：MeloTTS不是标准PyPI包，必须从GitHub安装。

### 3. Mac MLX优化（可选，仅Mac）

```bash
# MLX框架
pip install mlx

# MLX语言模型
pip install mlx-lm

# Lightning Whisper MLX（Mac优化的Whisper）
pip install lightning-whisper-mlx
```

### 配置

在`.env`文件中配置：

```bash
# 启用流式处理
ENABLE_STREAMING_STT=true
ENABLE_STREAMING_TTS=true

# Mac MLX优化（仅Mac用户）
USE_MLX=true
MLX_STT_MODEL=base
MLX_LM_MODEL=mlx-community/Meta-Llama-3.1-8B-Instruct-4bit

# TTS类型选择
TTS_TYPE=parler  # 或 melo 或 edge
```

### 推荐的安装方案

#### 方案1：基础流式（推荐）
```bash
pip install faster-whisper
pip install parler-tts
```

#### 方案2：Mac优化（Mac用户）
```bash
pip install faster-whisper
pip install mlx mlx-lm lightning-whisper-mlx
pip install parler-tts  # 或使用MeloTTS
```

#### 方案3：完整功能（所有平台）
```bash
pip install faster-whisper
pip install parler-tts
pip install git+https://github.com/myshell-ai/MeloTTS.git
```

### MLX优化优势

- **内存占用**：Lightning Whisper MLX比标准Whisper占用更少内存
- **性能**：利用Apple Silicon GPU加速
- **流式处理**：降低延迟，实时反馈
- **本地运行**：无需API调用

### 依赖兼容性

如果遇到依赖冲突：

```bash
# 升级transformers版本（解决兼容性问题）
pip install transformers==4.46.1

# 如果仍有问题，创建新的conda环境
conda create -n ise python=3.10
conda activate ise
pip install -r requirements.txt
```

---

## 🔍 配置验证

### 检查配置

```bash
# 检查环境变量
python -c "from services.core.config import settings; print(settings)"

# 检查API连接
curl http://localhost:8000/api/health

# 检查Milvus连接
python scripts/utils/check_knowledge_base.py
```

### 测试语音功能

```bash
# 测试Whisper
python -c "from services.speech.whisper_stt import get_whisper_stt; stt = get_whisper_stt(); print('✅ Whisper可用' if stt.is_available() else '❌ Whisper不可用')"

# 测试流式STT
python -c "from services.speech.streaming_stt import get_streaming_stt; stt = get_streaming_stt(); print('✅ 流式STT可用' if stt else '❌ 流式STT不可用')"

# 测试流式TTS
python -c "from services.speech.streaming_tts import get_streaming_tts; tts = get_streaming_tts(); print('✅ 流式TTS可用' if tts else '❌ 流式TTS不可用')"
```

---

## 🚀 启动服务

### 开发模式

```bash
conda activate ise
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 生产模式

```bash
# 使用gunicorn（推荐）
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 📝 配置优先级

1. **环境变量**（最高优先级）
2. **.env文件**
3. **默认值**（config.py中定义）

### 示例：覆盖配置

```bash
# 临时覆盖（不修改.env）
WHISPER_MODEL_SIZE=small uvicorn backend.main:app --reload

# 或修改.env文件
echo "WHISPER_MODEL_SIZE=small" >> .env
```

---

## ✅ 配置检查清单

- [ ] conda环境已创建并激活
- [ ] 所有依赖已安装
- [ ] .env文件已创建并配置
- [ ] LLM API密钥已配置（至少一个）
- [ ] Milvus已启动并连接成功
- [ ] 知识库已索引（至少一个文档）
- [ ] Whisper模型已下载（如果启用语音）
- [ ] 流式STT/TTS已配置（可选）
- [ ] MLX优化已配置（Mac用户，可选）
- [ ] API服务可以正常启动
- [ ] 健康检查通过：`curl http://localhost:8000/api/health`

---

## 📞 获取帮助

- 查看日志：`logs/rag_system.log`
- 检查配置：`python -c "from services.core.config import settings; print(settings)"`
- 查看文档：`README.md` 和 `docs/USER_GUIDE.md`
- 故障排查：`docs/TROUBLESHOOTING.md`
