# Google Custom Search API 故障排查指南

## 当前状态

- ✅ **CSE ID**: `72654d7b67f3b424a`（已确认正确）
- ⚠️ **API Key**: 配置了但可能权限未启用

## 错误信息

```
400 Bad Request
API key not valid. Please pass a valid API key.
```

## 解决方案

### 步骤1：检查API Key是否正确

1. 访问：https://console.cloud.google.com/apis/credentials
2. 查找API Key：`247520e58efa7b02a382...`
3. 确认API Key存在且状态为"已启用"

### 步骤2：启用Custom Search API

**方法A：通过API Key设置启用**

1. 在API Key列表中找到你的API Key
2. 点击API Key名称进入详情页
3. 在"API限制"部分：
   - 如果选择的是"不限制"，需要改为"限制密钥"
   - 在"限制此密钥的API调用"中：
     - 点击"选择要限制的API"
     - 搜索"Custom Search API"
     - **勾选"Custom Search API"**
     - 点击"保存"

**方法B：先在API库中启用Custom Search API**

1. 访问：https://console.cloud.google.com/apis/library/customsearch.googleapis.com
2. 点击**"启用"**按钮
3. 等待启用完成（可能需要几分钟）
4. 然后回到步骤1配置API Key限制

### 步骤3：验证配置

运行检查脚本：

```bash
conda activate ise
python scripts/tests/check_google_api.py
```

如果仍然失败，检查：
- API Key是否正确复制（没有多余空格）
- Custom Search API是否已启用
- 是否等待了足够的时间让更改生效（通常需要1-5分钟）

### 步骤4：检查项目配置

确保你的Google Cloud项目：
1. 已创建或选择了正确的项目
2. 已启用结算功能（即使是免费配额也需要）
3. 有足够的权限访问API

## 常见问题

### Q1: 为什么需要启用API？
A: Google Cloud的API默认是关闭的，需要在项目级别启用后才能使用。

### Q2: 配额限制是多少？
A: 免费版每天100次搜索请求。超出后返回403错误。

### Q3: 可以继续使用DuckDuckGo吗？
A: 可以！如果Google API配置有问题，系统会自动回退到DuckDuckGo，功能不受影响。

### Q4: 如何检查API是否已启用？
A: 访问 https://console.cloud.google.com/apis/dashboard，搜索"Custom Search API"，查看状态是否为"已启用"。

## 测试命令

配置完成后，运行：

```bash
conda activate ise
python scripts/tests/check_google_api.py
```

期望看到：
- ✅ API调用成功！
- 📊 找到 X 个结果

## 备用方案

如果Google API配置有困难，系统会自动使用DuckDuckGo：
- ✅ 无需配置
- ✅ 免费无限制
- ✅ 功能完全正常

只是在搜索结果质量和数量上可能不如Google。

