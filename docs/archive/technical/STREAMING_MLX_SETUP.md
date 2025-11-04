# 流式STT/TTS和MLX优化安装指南

## 📦 依赖安装

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

## ⚙️ 配置

在`.env`文件中配置：

```bash
# 启用流式处理
ENABLE_STREAMING_STT=true
ENABLE_STREAMING_TTS=true

# Mac MLX优化（仅Mac用户）
USE_MLX=true
MLX_STT_MODEL=tiny
MLX_LM_MODEL=mlx-community/Meta-Llama-3.1-8B-Instruct-4bit

# TTS类型选择
TTS_TYPE=parler  # 或 melo 或 edge
```

## 🎯 推荐的安装方案

### 方案1：基础流式（推荐）
```bash
pip install faster-whisper
pip install parler-tts
```

### 方案2：Mac优化（Mac用户）
```bash
pip install faster-whisper
pip install mlx mlx-lm lightning-whisper-mlx
pip install parler-tts  # 或使用MeloTTS
```

### 方案3：完整功能（所有平台）
```bash
pip install faster-whisper
pip install parler-tts
pip install git+https://github.com/myshell-ai/MeloTTS.git
```

## ⚠️ 常见问题

### 问题1：MeloTTS安装失败
**原因**：MeloTTS不是标准pip包  
**解决**：使用 `pip install git+https://github.com/myshell-ai/MeloTTS.git`

### 问题2：MLX在非Mac系统上安装失败
**原因**：MLX仅支持Mac系统  
**解决**：在非Mac系统上不要启用`USE_MLX=true`

### 问题3：Parler-TTS导入错误
**原因**：可能缺少transformers  
**解决**：`pip install transformers`

## 📝 验证安装

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

