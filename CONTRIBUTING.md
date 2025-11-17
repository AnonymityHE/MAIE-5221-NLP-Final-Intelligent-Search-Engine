# 贡献指南 / Contributing Guide

感谢你对MiniMango项目的关注！我们欢迎任何形式的贡献。

## 如何贡献

### 报告Bug 🐛

如果你发现了bug，请创建一个Issue并包含以下信息：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（Python版本、操作系统等）
- 错误日志（如有）

### 提出新功能 💡

如果你有新功能的想法，请：
1. 创建一个Issue描述你的想法
2. 说明为什么这个功能有用
3. 如果可能，提供实现思路

### 提交代码 🔧

1. **Fork本项目**
   ```bash
   # 克隆你的fork
   git clone https://github.com/your-username/minimango.git
   cd minimango
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **进行开发**
   - 遵循现有代码风格
   - 添加必要的注释
   - 更新相关文档

4. **测试你的更改**
   ```bash
   # 运行测试
   python scripts/tests/extended_qa_test.py
   python scripts/tests/test_tool_accuracy.py
   ```

5. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

6. **推送并创建PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   然后在GitHub上创建Pull Request

## 代码规范

### Python代码风格
- 遵循PEP 8规范
- 使用4个空格缩进
- 函数和类添加docstring
- 变量名使用snake_case
- 类名使用PascalCase

### 提交信息规范
使用语义化提交信息：
- `feat:` 新功能
- `fix:` Bug修复
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

示例：
```
feat: 添加粤语语音识别支持
fix: 修复Milvus连接超时问题
docs: 更新README安装说明
```

## 开发环境设置

1. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

2. 配置环境变量
   ```bash
   cp .env.example .env
   # 编辑.env填入必要的API密钥
   ```

3. 启动Milvus
   ```bash
   docker compose up -d
   ```

4. 构建知识库
   ```bash
   python scripts/build_knowledge_base.py
   ```

## 测试

在提交PR前，请确保：
- [ ] 所有测试通过
- [ ] 新功能有对应的测试
- [ ] 代码无明显的linting错误
- [ ] 文档已更新

## 问题讨论

如有任何问题，欢迎：
- 创建Issue讨论
- 在PR中留言
- 通过邮件联系项目维护者

## 行为准则

- 尊重所有贡献者
- 使用友好和包容的语言
- 接受建设性的批评
- 关注对社区最有利的事情

---

再次感谢你的贡献！ 🎉

