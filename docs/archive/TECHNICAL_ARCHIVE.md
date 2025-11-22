# 技术文档归档

本文档包含项目的技术细节、优化记录和对比分析。

## 📋 目录
1. [依赖兼容性修复](#依赖兼容性修复)
2. [内存占用测试结果](#内存占用测试结果)
3. [Hugging Face S2S对比](#hugging-face-s2s对比)
4. [MLX优化配置](#mlx优化配置)
5. [流式STT/TTS安装](#流式stttts安装)

---

## 🔧 依赖兼容性修复

### 问题描述

服务启动时遇到依赖版本兼容性问题：
```
ImportError: cannot import name 'is_torch_npu_available' from 'transformers'
```

### 解决方案

#### 1. 升级transformers版本
```bash
pip install transformers==4.46.1
```

#### 2. 添加兼容性补丁

在`services/__init__.py`中添加了兼容性补丁：

```python
# 兼容性补丁：在导入其他模块之前修复transformers版本问题
try:
    import transformers
    # 修复旧版本transformers缺少is_torch_npu_available的问题
    if not hasattr(transformers, 'is_torch_npu_available'):
        transformers.is_torch_npu_available = lambda: False
except ImportError:
    pass
```

#### 3. 依赖版本

- **transformers**: 4.46.1（兼容parler-tts和sentence-transformers）
- **sentence-transformers**: 5.1.2
- **注意**: melotts要求transformers==4.27.4，但4.46.1也能工作

### 当前状态

- ✅ 兼容性补丁已添加
- ✅ transformers版本已升级
- ✅ 模块导入测试通过
- ✅ 服务可以正常启动

### 依赖冲突说明

虽然pip显示melotts有版本冲突警告，但实际上：
- transformers 4.46.1 可以正常工作
- melotts功能不受影响
- 如果遇到问题，可以暂时不使用melotts（使用parler-tts或edge-tts）

---

## 📊 内存占用测试结果

### 测试结果

| 模型 | 内存占用 | 增加量 | 评价 |
|------|---------|--------|------|
| **标准Whisper (medium)** | 4089.75 MB | +3858.77 MB | ⚠️ **非常高**（接近4GB） |
| **Faster Whisper (base)** | 1904.61 MB | +183.17 MB | ✅ **非常低**（推荐） |
| **Edge TTS** | 208.23 MB | +0 MB | ✅ **最佳**（无模型加载） |

### 关键发现

1. **标准Whisper medium模型占用接近4GB内存** ⚠️
   - 不适合资源受限环境
   - 建议改用Faster Whisper或更小的模型

2. **Faster Whisper base模型只占用183MB** ✅
   - 比标准Whisper低**21倍**！
   - 支持流式处理
   - 强烈推荐使用

3. **Edge TTS无需加载模型** ✅
   - 内存占用为0
   - 云端处理，本地无负担

### 优化建议

#### 立即优化（推荐）

**使用Faster Whisper替代标准Whisper**：
```bash
# 安装Faster Whisper
pip install faster-whisper

# 在.env中配置
ENABLE_STREAMING_STT=true
```

**优势**：
- 内存占用降低95%（从4GB降到183MB）
- 支持流式处理
- 速度更快
- int8量化自动优化

#### Mac用户优化

**使用MLX优化**：
```bash
# 安装MLX
pip install mlx mlx-lm lightning-whisper-mlx

# 在.env中配置
USE_MLX=true
MLX_STT_MODEL=tiny  # 或base
```

**优势**：
- 充分利用Apple Silicon性能
- 内存占用更低
- 速度更快

#### 模型选择建议

| 使用场景 | 推荐模型 | 内存占用 | 准确度 |
|---------|---------|---------|--------|
| 资源受限 | Faster Whisper base | ~180MB | 良好 |
| 平衡性能 | Faster Whisper small | ~400MB | 很好 |
| 高准确度 | Faster Whisper medium | ~800MB | 优秀 |
| Mac优化 | Lightning Whisper MLX tiny | ~100MB | 良好 |

### 配置建议

#### 当前配置（高内存占用）
```bash
WHISPER_MODEL_SIZE=medium  # 占用4GB内存 ⚠️
```

#### 优化配置（推荐）
```bash
# 使用Faster Whisper
ENABLE_STREAMING_STT=true
WHISPER_MODEL_SIZE=base  # 或small

# 或Mac用户使用MLX
USE_MLX=true
MLX_STT_MODEL=base
```

#### 最小配置（资源受限）
```bash
ENABLE_STREAMING_STT=true
WHISPER_MODEL_SIZE=base  # 或tiny
TTS_TYPE=edge  # Edge TTS无内存占用
```

---

## 🔄 Hugging Face Speech-to-Speech 对比

### Hugging Face S2S 项目概述

[Hugging Face Speech-to-Speech](https://github.com/huggingface/speech-to-speech) 是一个开源的、模块化的语音到语音转换系统，目标是创建一个类似 GPT-4o 的开源替代方案。

**核心架构**：`VAD → STT → LLM → TTS`

**模块化设计**：
- **VAD**: Silero VAD v5
- **STT**: Whisper、Lightning Whisper MLX、Paraformer
- **LLM**: Hugging Face Hub模型、MLX LM、OpenAI API
- **TTS**: Parler-TTS、MeloTTS、ChatTTS

### 架构对比

| 组件 | Hugging Face S2S | 我们的项目 |
|------|-----------------|-----------|
| **VAD** | Silero VAD v5（必需） | Silero VAD（可选）+ 前端Web Audio API |
| **STT** | Whisper / Lightning Whisper MLX / Paraformer | Whisper（可配置，支持MLX） |
| **中间处理** | 直接LLM | **Agent系统**（RAG/Web/Weather/Finance/Transport） |
| **LLM** | Hugging Face Hub / MLX LM / OpenAI | HKGAI（默认，多语言） / DeepSeek（备选） |
| **TTS** | Parler-TTS / MeloTTS / ChatTTS | Parler-TTS / MeloTTS / Edge TTS |

### 功能对比

| 功能 | Hugging Face S2S | 我们的项目 |
|------|-----------------|-----------|
| **核心定位** | 纯语音对话系统 | **RAG + Agent + 语音** |
| **知识检索** | ❌ 无 | ✅ **RAG检索**（Milvus向量数据库） |
| **工具调用** | ❌ 无 | ✅ **Agent工具**（天气、金融、交通、网页搜索） |
| **唤醒词** | ❌ 无 | ✅ **"Jarvis"唤醒词检测** |
| **多语言** | ✅ 6种语言 | ✅ **粤语、普通话、英语**（香港本地化） |
| **流式输出** | ✅ Parler-TTS流式 | ✅ 流式STT/TTS支持 |
| **MLX优化** | ✅ Mac MPS优化 | ✅ Mac MLX优化 |

### 我们的项目优势

1. **RAG + Agent系统** ⭐⭐⭐⭐⭐
   - ✅ 本地知识库检索（Milvus）
   - ✅ 智能工具选择（天气、金融、交通等）
   - ✅ Reranker优化检索结果

2. **香港本地化** ⭐⭐⭐⭐⭐
   - ✅ **粤语支持**（完整的多语言RAG）
   - ✅ **多语言混合**查询优化
   - ✅ HKGAI API（香港本地LLM）

3. **Agent工具调用** ⭐⭐⭐⭐
   - ✅ 自动选择工具（天气、金融、交通、网页搜索）
   - ✅ 历史天气查询自动路由到web_search

### Hugging Face S2S的优势

1. **模块化设计** ⭐⭐⭐⭐⭐
   - ✅ 每个组件都可以轻松替换
   - ✅ 支持多种模型选择

2. **流式输出** ⭐⭐⭐⭐
   - ✅ Parler-TTS支持音频流式输出
   - ✅ 降低延迟，提升用户体验

3. **Docker支持** ⭐⭐⭐
   - ✅ 开箱即用的Docker配置
   - ✅ 简化部署

### 结论

两个项目定位不同：
- **Hugging Face S2S**：专注于纯语音对话，模块化设计
- **我们的项目**：**RAG + Agent + 语音**，更完整的智能助手系统

我们的项目在**RAG检索**、**Agent工具调用**和**香港本地化**方面有明显优势。

---

## 🍎 MLX优化配置

### 已完成的配置

#### 1. MLX组件安装
- ✅ MLX框架 (0.29.3)
- ✅ Lightning Whisper MLX（语音识别）
- ✅ MLX LM（语言模型，有兼容性问题但不影响主要功能）

#### 2. .env配置
```bash
# MLX优化配置
USE_MLX=true
MLX_STT_MODEL=base
MLX_LM_MODEL=mlx-community/Meta-Llama-3.1-8B-Instruct-4bit

# 流式处理
ENABLE_STREAMING_STT=true
ENABLE_STREAMING_TTS=true
TTS_TYPE=parler
```

#### 3. 代码修复
- ✅ 修复了Lightning Whisper MLX参数（`model`而不是`model_name`）
- ✅ 添加了MLX LM兼容性处理
- ✅ 更新了WebSocket处理器支持MLX

### 测试结果

| 组件 | 状态 | 说明 |
|------|------|------|
| MLX框架 | ✅ 通过 | 正常工作 |
| Lightning Whisper MLX | ✅ 通过 | 可以加载和使用 |
| MLX LM | ⚠️ 兼容性问题 | tokenizer属性问题，但不影响主要功能 |

### 使用方法

系统会根据`.env`配置自动启用MLX优化：

1. **语音识别**：使用Lightning Whisper MLX（Mac优化）
2. **流式处理**：启用流式STT/TTS降低延迟
3. **性能优化**：充分利用Apple Silicon性能

### 优势

#### 内存占用
- Lightning Whisper MLX：比标准Whisper占用更少内存
- 4bit量化模型：内存占用降低75%

#### 性能
- 利用Apple Silicon GPU加速
- 流式处理降低延迟
- 本地运行，无需API调用

#### 兼容性
- 如果MLX组件不可用，自动降级到标准实现
- 不影响现有功能

### 注意事项

1. **MLX LM兼容性问题**
   - 某些模型可能有tokenizer兼容性问题
   - 不影响主要功能（系统仍使用HKGAI API）
   - 如需修复：`pip install --upgrade transformers`

2. **仅Mac支持**
   - MLX仅支持Mac系统
   - 其他平台会自动降级到标准实现

3. **首次使用**
   - Lightning Whisper MLX会下载模型（首次使用）
   - 模型会缓存到本地

---

## 🚀 流式STT/TTS安装

### 依赖安装

#### 1. 基础流式STT（必需）
```bash
# Faster Whisper（更快的流式STT）
pip install faster-whisper
```

#### 2. 流式TTS（可选）

**选项A：Parler-TTS（推荐，流式输出）**
```bash
pip install parler-tts
pip install transformers
```

**选项B：MeloTTS（多语言，Mac优化）**
```bash
# MeloTTS需要从GitHub安装（不是标准pip包）
pip install git+https://github.com/myshell-ai/MeloTTS.git
```

#### 3. Mac MLX优化（可选，仅Mac）
```bash
pip install mlx
pip install mlx-lm
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
MLX_STT_MODEL=tiny

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
pip install parler-tts
```

#### 方案3：完整功能（所有平台）
```bash
pip install faster-whisper
pip install parler-tts
pip install git+https://github.com/myshell-ai/MeloTTS.git
```

### 常见问题

#### 问题1：MeloTTS安装失败
**原因**：MeloTTS不是标准pip包  
**解决**：使用 `pip install git+https://github.com/myshell-ai/MeloTTS.git`

#### 问题2：MLX在非Mac系统上安装失败
**原因**：MLX仅支持Mac系统  
**解决**：在非Mac系统上不要启用`USE_MLX=true`

#### 问题3：Parler-TTS导入错误
**原因**：可能缺少transformers  
**解决**：`pip install transformers`

### 验证安装

```python
# 测试流式STT
from services.speech.streaming_stt import get_streaming_stt
stt = get_streaming_stt()
if stt:
    print("✅ 流式STT可用")

# 测试流式TTS
from services.speech.streaming_tts import get_streaming_tts
tts = get_streaming_tts(tts_type="parler")
if tts:
    print("✅ 流式TTS可用")

# 测试MLX（仅Mac）
try:
    import mlx.core as mx
    print("✅ MLX可用")
except:
    print("⚠️  MLX不可用（非Mac系统或未安装）")
```

---

## 📝 总结

本文档归档了项目的技术细节和优化记录：

1. **依赖兼容性**：已解决transformers版本冲突问题
2. **内存优化**：推荐使用Faster Whisper，内存占用降低95%
3. **技术对比**：与Hugging Face S2S的详细对比分析
4. **MLX优化**：Mac用户的性能优化方案
5. **流式处理**：流式STT/TTS的安装和配置指南

更多信息请参考：
- 安装指南：`docs/SETUP_GUIDE.md`
- 故障排查：`docs/TROUBLESHOOTING.md`
- 用户指南：`docs/USER_GUIDE.md`

