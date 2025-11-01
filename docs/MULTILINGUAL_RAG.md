# 多语言RAG实现说明

## 概述

根据HKGAI-V1论文要求，本系统现已实现**多语言检索增强生成**，特别针对**粤语、普通话、英语**进行了优化。

## 实现内容

### 1. 多语言Embedding模型支持

- **默认多语言模型**：`paraphrase-multilingual-MiniLM-L12-v2`
  - 支持100+语言
  - 包括粤语、普通话、英语
  - 向量维度：384
  
- **配置方式**：
  ```bash
  USE_MULTILINGUAL_EMBEDDING=true
  MULTILINGUAL_EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
  ```

### 2. 语言检测功能

实现了`LanguageDetector`类，可以自动识别：
- **粤语**：检测特有字符（嘅、咗、係、啲、佢等）
- **普通话**：标准中文文本
- **英语**：ASCII字符文本
- **混合语言**：同时包含多种语言

### 3. 多语言检索优化

检索器（`Retriever`）现在会：
1. 自动检测查询语言
2. 使用多语言embedding模型进行向量化
3. 支持混合语言查询
4. 记录语言信息用于日志和调试

## 文件结构

```
services/
├── core/
│   ├── language_detector.py  # 语言检测模块 ⭐ 新增
│   └── config.py             # 配置（已更新多语言选项）
├── vector/
│   └── retriever.py          # 检索器（已集成多语言支持）
scripts/tests/
└── test_multilingual_rag.py  # 多语言测试脚本 ⭐ 新增
```

## 使用示例

### Python代码

```python
from services.vector.retriever import retriever

# 粤语查询
results = retriever.search("RAG系统係乜嘢？")

# 普通话查询
results = retriever.search("什么是RAG系统？")

# 英语查询
results = retriever.search("What is RAG system?")

# 混合语言查询
results = retriever.search("RAG系统是检索增强生成，What does it mean?")
```

### API调用

```bash
# 粤语查询
curl -X POST "http://localhost:8000/api/rag_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "RAG系统係乜嘢？"}'

# 普通话查询
curl -X POST "http://localhost:8000/api/rag_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "什么是RAG系统？"}'
```

## 测试

运行测试脚本：

```bash
conda activate ise
python scripts/tests/test_multilingual_rag.py
```

测试包括：
1. 语言检测功能测试
2. 多语言embedding测试
3. 多语言检索测试（需要先索引数据）

## 性能对比

| 特性 | 单语言模型 | 多语言模型 |
|------|----------|-----------|
| 支持语言 | 英语 | 100+语言 |
| 向量维度 | 384 | 384 |
| 速度 | 快 | 稍慢 |
| 适用场景 | 单一语言 | 多语言混合 |

## 配置建议

- **香港本地化应用**：启用多语言模型（`USE_MULTILINGUAL_EMBEDDING=true`）
- **纯英文应用**：使用单语言模型（`USE_MULTILINGUAL_EMBEDDING=false`）
- **混合内容知识库**：必须使用多语言模型

## 与HKGAI论文的对应

根据HKGAI-V1论文：
- ✅ 支持多语言环境（粤语、普通话、英语）
- ✅ 集成RAG系统确保及时且基于事实的信息访问
- ✅ 适配香港独特的语言和文化环境

## 未来改进

可能的改进方向：
1. 优化粤语检测准确度
2. 支持更多语言（如日语、韩语）
3. 语言特定的检索权重调整
4. 多语言文档的自动分类

