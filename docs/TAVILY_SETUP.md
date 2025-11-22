# 🔍 Tavily AI Search 配置指南

## 为什么选择Tavily？

Tavily AI Search是专为AI应用设计的搜索API，相比传统搜索API有以下优势：

✅ **AI优化** - 返回结构化、清洗过的结果，直接可用于RAG
✅ **免费额度** - 1000次/月，足够开发和测试使用
✅ **速度快** - 平均响应时间 < 1秒
✅ **多语言** - 支持中文、粤语、英文等
✅ **AI答案摘要** - 自动生成答案摘要，可直接使用
✅ **无需维护** - 不需要配置Custom Search Engine

---

## 📋 获取API Key（30秒）

### 步骤1：注册账号
访问：https://tavily.com

点击 **"Get API Key"** 或 **"Sign Up"**

### 步骤2：快速登录
选择以下任一方式登录（推荐Google，最快）：
- Google账号
- GitHub账号
- Email注册

### 步骤3：获取API Key
登录后，在Dashboard页面找到你的API Key

格式：`tvly-xxxxxxxxxxxxxxxxxxxxxxxxxx`

**复制并保存这个Key！**

---

## ⚙️ 配置到项目

### 方法1：通过.env文件（推荐）

编辑项目根目录的`.env`文件，添加：

```bash
# Tavily AI Search配置
TAVILY_API_KEY=tvly-your-api-key-here
USE_TAVILY_SEARCH=true
```

### 方法2：通过环境变量

```bash
export TAVILY_API_KEY="tvly-your-api-key-here"
export USE_TAVILY_SEARCH=true
```

---

## 🧪 测试集成

### 1. 快速测试

```bash
cd /path/to/project
conda activate ise
python scripts/tests/test_tavily.py
```

### 2. 在Agent中测试

重启后端服务，然后：

```bash
python -c "
import requests
response = requests.post(
    'http://localhost:8000/api/agent_query',
    json={'query': 'What are the best attractions in Hong Kong?', 'use_agent': True}
)
print(response.json()['answer'])
"
```

### 3. 完整Test Set 3测试

```bash
python scripts/tests/test_set3.py
```

---

## 📊 使用配额

### 免费计划
- **1000次/月** - 足够开发使用
- 每次搜索返回最多10个结果
- 支持所有功能

### 查看用量
登录Tavily Dashboard查看：
- https://app.tavily.com/dashboard

### 升级（可选）
如果需要更多配额：
- **Starter**: $20/月 - 5000次
- **Pro**: $100/月 - 50000次

---

## 🎯 优势对比

| 特性 | Tavily | Google CSE | DuckDuckGo |
|------|--------|------------|------------|
| 免费额度 | 1000次/月 | 100次/天 | 无限（但不稳定） |
| AI优化 | ✅✅✅ | ❌ | ❌ |
| 速度 | ⚡⚡⚡ | ⚡⚡ | ⚡ |
| 结果质量 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 配置难度 | 简单 | 中等 | 简单 |
| 多语言 | ✅ | ✅ | ✅ |
| AI答案摘要 | ✅ | ❌ | ❌ |
| 适合RAG | ✅✅✅ | ✅ | ✅ |

---

## 🔧 故障排查

### 问题1: API Key无效
```
错误: Tavily API Key无效或已过期
```
**解决：**
- 检查`.env`文件中的Key是否正确
- 确保Key没有多余的空格或引号
- 登录Tavily Dashboard确认Key是否有效

### 问题2: 配额用完
```
错误: API配额已用完
```
**解决：**
- 等待下个月自动重置
- 或升级到付费计划

### 问题3: 搜索无结果
```
返回: 0个结果
```
**可能原因：**
- 查询过于具体或罕见
- 网络连接问题
- API暂时不可用

**解决：**
- 尝试更通用的查询
- 检查网络连接
- 系统会自动回退到Google或DuckDuckGo

---

## 📚 API文档

完整API文档：https://docs.tavily.com

Python SDK：https://github.com/tavily-ai/tavily-python

---

## 💡 最佳实践

### 1. 优化查询
```python
# ❌ 不好的查询
query = "restaurant"

# ✅ 好的查询
query = "best Japanese ramen restaurant in Causeway Bay Hong Kong"
```

### 2. 合理设置结果数
```python
# 一般查询
max_results = 3-5  # 够用且省配额

# 深度研究
max_results = 8-10  # 更全面
```

### 3. 使用AI答案摘要
```python
result = client.search(query, include_answer=True)
ai_answer = result.get("answer", "")  # 直接使用这个答案
```

---

## ✅ 配置完成检查清单

- [ ] 已注册Tavily账号
- [ ] 已获取API Key
- [ ] 已添加到`.env`文件
- [ ] 已运行测试脚本
- [ ] 测试通过
- [ ] Test Set 3验证通过

---

**需要帮助？** 查看项目文档或提Issue！

