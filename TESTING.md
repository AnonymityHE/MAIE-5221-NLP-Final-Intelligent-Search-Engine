# 测试指南

本文档说明如何测试新实现的功能。

## 准备工作

### 1. 激活Conda环境

```bash
conda activate ise
# 或根据你的环境名称调整
```

### 2. 启动Milvus

```bash
docker compose up -d
# 检查状态
docker ps
```

### 3. 启动API服务

```bash
uvicorn backend.main:app --reload
```

服务将在 `http://localhost:8000` 启动。

## 快速测试

### 使用测试脚本

```bash
# 快速测试（bash脚本，无需Python依赖）
bash scripts/tests/quick_test.sh

# 详细测试（Python脚本，需要API运行）
python scripts/tests/test_improvements.py
```

### 手动测试

#### 1. 测试日志系统

启动API后，检查日志文件：

```bash
# 查看日志文件
ls -lh logs/rag_system.log

# 实时查看日志
tail -f logs/rag_system.log

# 测试日志级别（设置环境变量）
export LOG_LEVEL=DEBUG
uvicorn backend.main:app --reload
```

#### 2. 测试Reranker功能

```bash
curl -X POST "http://localhost:8000/api/rag_query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是RAG？",
    "top_k": 5
  }'
```

检查响应中的文档顺序（Reranker会重新排序）。

#### 3. 测试Agent金融工具

```bash
# 测试股票查询
curl -X POST "http://localhost:8000/api/agent_query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "AAPL的股价是多少？"
  }'

# 测试加密货币
curl -X POST "http://localhost:8000/api/agent_query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "比特币价格"
  }'
```

预期：`tools_used` 中包含 `"finance"`

#### 4. 测试Agent交通工具

```bash
curl -X POST "http://localhost:8000/api/agent_query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "从香港到深圳需要多久？"
  }'
```

预期：`tools_used` 中包含 `"transport"`

#### 5. 测试环境变量支持

创建 `.env` 文件：

```bash
cp .env.example .env
# 编辑.env文件，修改配置
```

然后重启API服务，配置会自动加载。

```bash
# 测试特定配置
export USE_RERANKER=false
export LOG_LEVEL=DEBUG
uvicorn backend.main:app --reload
```

## 使用Swagger UI测试

访问 `http://localhost:8000/docs` 可以直接在浏览器中测试所有API：

1. **测试RAG查询**：使用 `/api/rag_query` 端点
2. **测试Agent查询**：使用 `/api/agent_query` 端点
3. **查看工具使用情况**：检查响应中的 `tools_used` 字段

## 验证功能

### 验证Reranker是否启用

1. 进行RAG查询
2. 检查日志中是否有 "Reranker重排序完成" 消息
3. 或者设置 `USE_RERANKER=false`，对比结果

### 验证Agent工具选择

查看响应中的 `tools_used` 字段：

```json
{
  "answer": "...",
  "tools_used": ["finance", "local_rag"],
  "answer_source": "agent"
}
```

### 验证日志系统

1. 进行API调用
2. 检查 `logs/rag_system.log` 文件
3. 应该看到不同级别的日志记录

## 常见问题

### API服务无法启动

**问题**：`ModuleNotFoundError` 或导入错误

**解决**：
```bash
# 确保conda环境已激活
conda activate ise

# 安装依赖
pip install -r requirements.txt
```

### Milvus连接失败

**问题**：`连接Milvus失败`

**解决**：
```bash
# 检查Docker状态
docker ps

# 重启Milvus
docker compose restart
```

### 金融/交通工具无响应

**问题**：工具被调用但无结果

**说明**：这是正常的，因为：
- 金融工具依赖外部API（Yahoo Finance, CoinGecko）
- 交通工具使用简化的实现（可扩展为完整API）

可以查看日志了解详情。

### Reranker未生效

**检查**：
1. 查看日志是否有 "Reranker模型加载完成"
2. 检查配置 `USE_RERANKER=true`
3. 确保 `sentence-transformers` 已正确安装

## 性能测试

### 对比Reranker开启/关闭

```bash
# 关闭Reranker
export USE_RERANKER=false
# 测试查询速度

# 开启Reranker
export USE_RERANKER=true
# 测试查询速度和准确性
```

### 查看日志性能

日志会记录：
- 模型加载时间
- 查询处理时间
- 工具调用时间

## 下一步

完成测试后，可以：
1. 查看 `docs/CHANGELOG_IMPROVEMENTS.md` 了解详细改进
2. 查看 `docs/IMPROVEMENTS.md` 了解后续改进建议
3. 根据需要调整配置（`.env` 文件）

