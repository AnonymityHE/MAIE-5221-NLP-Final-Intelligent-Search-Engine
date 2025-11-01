# Google Custom Search API 配置指南

## 概述

要使用 Google Custom Search API，你需要：
1. **API Key**（已提供）
2. **Custom Search Engine ID (CSE ID)**（需要创建）

## 步骤1：创建 Custom Search Engine

### 方法1：使用 Google Programmable Search Engine（推荐）

1. **访问创建页面**：
   - 打开：https://programmablesearchengine.google.com/controlpanel/create

2. **填写基本信息**：
   - **搜索引擎名称**：例如 "ISE Search Engine"
   - **要搜索的网站**：
     - 选项1：搜索整个网络 → 输入 `*` （星号表示搜索整个互联网）
     - 选项2：搜索特定网站 → 输入特定域名，如 `example.com`
   - **语言**：选择你需要的语言（可选）
   - **区域**：选择搜索区域（可选）

3. **点击"创建"**

4. **获取 CSE ID**：
   - 创建完成后，进入控制面板
   - 在"搜索引擎详细信息"中找到 **Search Engine ID**
   - 格式类似：`012345678901234567890:abcdefghijk`

### 方法2：使用现有搜索引擎（如果有）

如果你已经有Google Custom Search Engine，直接复制其ID即可。

## 步骤2：配置到项目中

### 方法A：通过配置文件（推荐）

编辑 `services/core/config.py`，添加CSE ID：

```python
GOOGLE_CSE_ID: Optional[str] = get_env("GOOGLE_CSE_ID", "你的CSE_ID_这里")
```

### 方法B：通过环境变量（推荐用于生产环境）

创建或编辑 `.env` 文件：

```bash
GOOGLE_SEARCH_API_KEY=247520e58efa7b02a382ea53355b23a843dc182c8be3b6c05b0cfd139caeb807
GOOGLE_CSE_ID=你的CSE_ID_这里
```

### 方法C：直接在代码中设置（不推荐，仅用于测试）

在 `services/core/config.py` 中：

```python
GOOGLE_CSE_ID: Optional[str] = get_env("GOOGLE_CSE_ID", "012345678901234567890:abcdefghijk")
```

## 步骤3：验证配置

运行测试验证配置是否正确：

```bash
conda activate ise
python -c "
from services.agent.tools.web_search_tool import web_search
result = web_search('Python programming', num_results=3)
print(f'搜索成功: {result[\"success\"]}')
print(f'结果数量: {len(result[\"results\"])}个结果')
for i, r in enumerate(result['results'][:3], 1):
    print(f'{i}. {r[\"title\"]}: {r[\"snippet\"][:50]}...')
"
```

## 配额说明

**免费配额**：
- Google Custom Search API 免费版提供：**100次搜索/天**
- 超出后需要付费或等待重置

**注意事项**：
- 如果配额用完，系统会自动回退到DuckDuckGo
- 建议在生产环境中监控API使用量

## 故障排查

### 问题1：返回 "Invalid API Key"
- 检查API Key是否正确
- 确认API Key已启用"Custom Search API"

### 问题2：返回 "Invalid CSE ID"
- 检查CSE ID格式是否正确
- 确认CSE ID已激活

### 问题3：搜索返回空结果
- 检查CSE配置中的搜索范围（是否设置为搜索整个网络）
- 验证搜索查询是否合理

### 问题4：配额已用完
- 检查当日配额使用情况
- 系统会自动回退到DuckDuckGo，这是正常的

## 无需CSE ID的替代方案

如果你不想创建CSE ID，系统会自动使用DuckDuckGo API作为备用方案：
- ✅ 无需配置
- ✅ 免费无限制
- ⚠️ 功能相对简单
- ⚠️ 结果质量可能不如Google

## 快速测试

配置完成后，可以运行测试脚本验证：

```bash
conda activate ise
python scripts/tests/test_agent.py
```

查看网页搜索相关的测试结果，确认是否使用了Google API。

