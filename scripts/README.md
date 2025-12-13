# Scripts 目录说明

本目录包含项目的所有脚本文件，按用途分类组织。

## 📁 目录结构

```
scripts/
├── utils/          # 常用工具脚本
│   ├── ingest.py              # 数据注入脚本（将文档向量化存入Milvus）
│   ├── start_api.sh           # 启动API服务脚本（智能端口检测）
│   ├── create_test_doc.py     # 创建测试PDF文档
│   └── read_project_announcement.py  # 读取项目公告文档
│
└── tests/          # 测试脚本
    ├── test_improvements.py         # 改进功能测试（完整测试）
    ├── test_refactoring.sh          # 重构测试（导入路径验证）
    ├── quick_test.sh                # 快速功能测试
    ├── test_agent_with_tools.py     # Agent工具完整测试
    ├── test_set1_complete.py        # Test Set 1完整测试（48问题）
    ├── test_set2_complete.py        # Test Set 2完整测试（45问题）
    ├── test_set3_complete.py        # Test Set 3完整测试（18问题）
    ├── test_image_questions.py      # 图像问题测试（6问题）
    ├── performance_benchmark.py     # 性能基准测试
    ├── analyze_all_results.py       # 测试结果分析
    ├── run_complete_tests.sh        # 并发运行所有测试集
    ├── run_sequential_tests.sh      # 顺序运行所有测试集（推荐）
    ├── check_test_status.sh         # 检查测试进度
    ├── monitor_tests.sh             # 监控测试运行状态
    └── README_COMPLETE_TESTS.md     # 完整测试套件文档
```

## 🛠️ 常用工具脚本（utils/）

### `ingest.py` - 数据注入脚本
将文档加载、切分、向量化并存入Milvus。

**使用方法**：
```bash
python scripts/utils/ingest.py
```

**功能**：
- 加载 `documents/` 目录中的所有PDF文件
- 文本切分和向量化
- 批量插入Milvus

---

### `start_api.sh` - 启动API服务脚本
智能启动API服务，包含端口检测和进程管理。

**使用方法**：
```bash
bash scripts/utils/start_api.sh
```

**功能**：
- 自动检测和激活conda环境（ise）
- 检查并启动Milvus服务
- 智能端口占用检测
- 自动检查API服务状态
- 安全进程终止和重启

**特性**：
- 如果端口被占用，会检测是否为API服务
- 如果服务正常运行，询问是否重启
- 安全终止旧进程并启动新服务

---

### `create_test_doc.py` - 创建测试文档
创建简单的测试PDF文档用于快速测试。

**使用方法**：
```bash
python scripts/utils/create_test_doc.py
```

---

### `read_project_announcement.py` - 读取项目公告
读取并解析项目公告Word文档。

**使用方法**：
```bash
python scripts/utils/read_project_announcement.py
```

## 🧪 测试脚本（tests/）

### `test_improvements.py` - 改进功能完整测试
测试所有新实现的功能（Reranker、Agent工具、日志系统等）。

**使用方法**：
```bash
# 确保API服务正在运行
conda activate ise
uvicorn backend.main:app --reload

# 在另一个终端运行测试
python scripts/tests/test_improvements.py
```

**测试内容**：
- Reranker功能
- Agent金融工具
- Agent交通工具
- Agent工具选择
- 日志系统
- 环境变量配置
- API健康检查

---

### `test_refactoring.sh` - 重构验证测试
测试重构后的导入路径和代码结构。

**使用方法**：
```bash
bash scripts/tests/test_refactoring.sh
```

**测试内容**：
- 新导入路径测试
- 向后兼容导入测试
- API服务检查

---

### `quick_test.sh` - 快速功能测试
快速测试核心功能是否正常。

**使用方法**：
```bash
bash scripts/tests/quick_test.sh
```

**测试内容**：
- 日志系统检查
- 环境变量配置
- Reranker功能（需要API运行）
- Agent金融工具（需要API运行）
- Agent交通工具（需要API运行）

---

### 完整测试套件（推荐用于最终评估）

#### `run_sequential_tests.sh` - 顺序运行所有测试集 ⭐
按顺序运行Test Set 1、2、3，避免资源竞争，**推荐使用**。

**使用方法**：
```bash
# 确保后端服务运行
bash scripts/tests/run_sequential_tests.sh
```

**测试规模**：111个问题（48+45+18）
**预计耗时**：~10分钟（优化后）
**输出**：`test_results/test_set*_complete_*.json`

---

#### `test_set1_complete.py` - Test Set 1测试
测试48个基础问题（知识库、天气、金融等）。

**使用方法**：
```bash
python scripts/tests/test_set1_complete.py
```

**测试内容**：
- 基础知识查询
- 实时天气数据
- 股票金融数据
- Web搜索
- 翻译和语言任务

---

#### `test_set2_complete.py` - Test Set 2测试
测试45个进阶问题（多步骤、比较、分析）。

**使用方法**：
```bash
python scripts/tests/test_set2_complete.py
```

**测试内容**：
- 多步骤工作流
- 比较性查询
- 复杂RAG检索
- 跨工具协作

---

#### `test_set3_complete.py` - Test Set 3测试
测试18个文本问题（Test Set 3不包含图像问题）。

**使用方法**：
```bash
python scripts/tests/test_set3_complete.py
```

---

#### `test_image_questions.py` - 图像问题测试
测试6个图像理解问题（使用Doubao multimodal API）。

**使用方法**：
```bash
python scripts/tests/test_image_questions.py
```

**测试内容**：
- 图像识别
- OCR文字提取
- 图像理解和描述

---

#### `performance_benchmark.py` - 性能基准测试
快速验证系统性能（8个代表性问题）。

**使用方法**：
```bash
python scripts/tests/performance_benchmark.py
```

**输出**：平均响应时间、工具准确率、性能提升百分比

---

#### `analyze_all_results.py` - 测试结果分析
分析test_results/中的所有JSON文件，生成综合报告。

**使用方法**：
```bash
python scripts/tests/analyze_all_results.py
```

---

#### `check_test_status.sh` / `monitor_tests.sh` - 测试监控
检查后台测试进度和状态。

**使用方法**：
```bash
bash scripts/tests/check_test_status.sh
# 或
bash scripts/tests/monitor_tests.sh
```

## 📝 使用建议

### 开发流程

1. **数据准备**：
   ```bash
   # 创建测试文档（可选）
   python scripts/utils/create_test_doc.py
   
   # 注入文档到Milvus
   python scripts/utils/ingest.py
   ```

2. **启动服务**：
   ```bash
   # 启动Docker服务（Milvus）
   docker compose up -d
   
   # 启动API服务
   bash scripts/utils/start_api.sh
   # 或手动启动
   conda activate ise
   uvicorn backend.main:app --host 0.0.0.0 --port 5555
   ```

3. **运行测试**：
   ```bash
   # 快速测试（验证基本功能）
   bash scripts/tests/quick_test.sh
   
   # 性能基准测试（8个问题，2分钟）
   python scripts/tests/performance_benchmark.py
   
   # 完整评估测试（111个问题，10分钟）⭐ 推荐
   bash scripts/tests/run_sequential_tests.sh
   
   # 图像问题测试（6个问题）
   python scripts/tests/test_image_questions.py
   ```

4. **分析结果**：
   ```bash
   # 生成综合分析报告
   python scripts/tests/analyze_all_results.py
   
   # 查看结果文件
   ls -lh test_results/
   ```

### 最终评估流程 ⭐

用于项目最终提交前的完整测试：

```bash
# 1. 确保所有服务运行
docker compose up -d
uvicorn backend.main:app --host 0.0.0.0 --port 5555 &

# 2. 等待服务启动（约30秒）
sleep 30

# 3. 运行完整测试套件（111问题）
bash scripts/tests/run_sequential_tests.sh

# 4. 运行图像测试（6问题）
python scripts/tests/test_image_questions.py

# 5. 分析所有结果
python scripts/tests/analyze_all_results.py

# 6. 检查结果文件
ls -lh test_results/test_set*_complete_*.json
```

**预期结果**：
- ✅ 总问题数：111 + 6 = 117
- ✅ 成功率：100%
- ✅ 平均响应时间：~7秒（优化后）
- ✅ 工具路由准确率：100%

## 🔗 相关文档

- 主 README.md - 项目完整说明
- START_API.md - API启动详细指南
- TESTING.md - 测试指南

