# 存储架构说明

## Milvus能存储什么？

**Milvus是一个向量数据库**，它的设计目标是：
- ✅ 存储向量（embedding vectors）
- ✅ 存储元数据（metadata：字符串、数字、布尔值等）
- ✅ 快速向量相似度搜索
- ❌ **不适合存储二进制文件**（如PDF、图片、视频等）

## 正确的存储架构

### 1. 二进制文件 → 文件系统

**存储位置**：`uploaded_files/` 目录

**存储内容**：
- PDF文件（`.pdf`）
- 图片文件（`.png`, `.jpg`, `.jpeg`, `.gif`）
- 代码文件（`.py`, `.js`, `.java`等）
- 文本文件（`.txt`, `.md`, `.json`等）

**为什么**：
- 文件系统适合存储二进制数据
- 不占用向量数据库资源
- 访问简单，支持直接文件读取

### 2. 向量和文本 → Milvus

**存储位置**：Milvus向量数据库

**存储内容**：
- **向量字段**（`vector`）：从文件提取的文本内容向量化后的embedding
- **文本字段**（`text`）：提取的文本内容（用于RAG检索）
- **元数据字段**（`source_file`）：文件ID、文件名、文件类型等信息

**存储格式示例**：
```
Collection: knowledge_base
Fields:
  - id: INT64 (自动生成)
  - text: VARCHAR (文本chunk，例如："RAG是检索增强生成...")
  - vector: FLOAT_VECTOR[384] (文本的embedding向量)
  - source_file: VARCHAR (例如："document.pdf||file_id:abc123||file_type:pdf")
```

### 3. 文件元数据 → Milvus（通过查询获取）

**存储方式**：通过查询Milvus中`source_file`字段获取文件元数据

**包含信息**：
- 文件ID（基于文件内容hash生成）
- 原始文件名
- 文件类型（pdf、image、code、text）
- 分块数量（通过统计Milvus中该文件的chunks数量）
- 处理状态（如果能在Milvus中找到，说明已处理）

### 4. 轻量级索引 → JSON文件

**存储位置**：`file_index.json`

**存储内容**：仅存储`file_id -> file_path`的映射

**用途**：
- 快速查找文件的物理路径
- 补充Milvus查询（获取文件大小、上传时间等静态信息）
- 用于未处理文件的快速查找

## 文件处理流程

```
1. 用户上传文件
   └─> 保存到 uploaded_files/目录（文件系统）
   
2. 解析文件
   ├─> PDF → PyMuPDF提取文本
   ├─> 图片 → Tesseract OCR识别文字
   ├─> 代码/文本 → 直接读取
   └─> 提取的文本 → 保存到变量
   
3. 文本处理
   ├─> 文本切分 → RecursiveCharacterTextSplitter
   └─> 生成向量 → sentence-transformers
   
4. 存储到Milvus
   ├─> vector: 向量数组
   ├─> text: 文本chunk
   └─> source_file: "filename||file_id:xxx||file_type:xxx"
   
5. 文件查询
   ├─> 通过file_id查询Milvus → 获取文件元数据
   └─> 通过file_id查找file_index.json → 获取文件路径
```

## 总结

- **二进制文件**：存储在文件系统（`uploaded_files/`）
- **向量和文本**：存储在Milvus
- **元数据**：通过查询Milvus获取，无需额外数据库
- **索引**：轻量级JSON文件，仅用于快速路径查找

这样的架构充分利用了Milvus的优势（向量检索），同时避免了在Milvus中存储大量二进制数据的低效做法。

