# 🚀 GitHub上传指南

本文档说明如何将项目上传到GitHub。

## 📋 准备工作

在上传前，请确保：
- ✅ 已清理所有临时文件（已完成）
- ✅ README.md已更新（已完成）
- ✅ .gitignore已配置（已完成）
- ✅ LICENSE文件已创建（已完成）

## 🔧 上传步骤

### 1. 初始化Git仓库（如果还没有）

```bash
cd "/Users/anonymity/Desktop/MAIE/MAIE5221 NLP/Final"
git init
```

### 2. 检查要提交的文件

```bash
# 查看将要提交的文件
git status

# 如果有不想提交的文件，确保它们在.gitignore中
```

### 3. 添加文件到Git

```bash
# 添加所有文件
git add .

# 或者选择性添加
git add README.md LICENSE .gitignore .gitattributes
git add services/
git add scripts/
git add docs/
git add main.py
git add requirements.txt
git add docker-compose.yml
```

### 4. 创建首次提交

```bash
git commit -m "feat: 初始提交 - MiniMango多语言RAG系统"
```

### 5. 在GitHub创建仓库

1. 登录 https://github.com
2. 点击右上角 "+" → "New repository"
3. 填写信息：
   - Repository name: `minimango` 或 `multilingual-rag-system`
   - Description: `🤖 智能多语言RAG问答系统 - 支持粤语、普通话、英语`
   - 选择 Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"（我们已经有了）
4. 点击 "Create repository"

### 6. 连接到GitHub仓库

```bash
# 添加远程仓库（替换为你的GitHub用户名和仓库名）
git remote add origin https://github.com/your-username/minimango.git

# 或者使用SSH（如果配置了SSH密钥）
git remote add origin git@github.com:your-username/minimango.git

# 验证远程仓库
git remote -v
```

### 7. 推送到GitHub

```bash
# 推送到main分支
git push -u origin main

# 如果你的默认分支是master
git branch -M main  # 重命名为main
git push -u origin main
```

## 🔑 配置SSH密钥（推荐）

使用SSH可以避免每次push都输入密码：

```bash
# 1. 生成SSH密钥
ssh-keygen -t ed25519 -C "your-email@example.com"

# 2. 添加到ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 3. 复制公钥
cat ~/.ssh/id_ed25519.pub
# 复制输出的内容

# 4. 在GitHub添加SSH密钥
# 访问 https://github.com/settings/keys
# 点击 "New SSH key"
# 粘贴公钥内容
```

## ⚠️ 重要提醒

### 敏感信息检查

在推送前，确保这些文件**不会**被提交：
- ✅ `.env` - API密钥（已在.gitignore）
- ✅ `usage_data.json` - 用量数据（已在.gitignore）
- ✅ `logs/` - 日志文件（已在.gitignore）
- ✅ `uploaded_files/` - 用户文件（已在.gitignore）

### 如果不小心提交了敏感信息

```bash
# 从历史中删除文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch services/core/config.py" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送（谨慎使用）
git push origin --force --all
```

更安全的方法是使用 `git-filter-repo` 工具。

## 📊 后续维护

### 创建新分支进行开发

```bash
# 创建并切换到新分支
git checkout -b feature/new-feature

# 进行开发...

# 提交更改
git add .
git commit -m "feat: 添加新功能"

# 推送分支
git push origin feature/new-feature

# 在GitHub上创建Pull Request
```

### 更新README徽章

在README.md中添加实际的GitHub仓库链接：

```markdown
[![GitHub stars](https://img.shields.io/github/stars/your-username/minimango.svg)](https://github.com/your-username/minimango/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/your-username/minimango.svg)](https://github.com/your-username/minimango/network)
[![GitHub issues](https://img.shields.io/github/issues/your-username/minimango.svg)](https://github.com/your-username/minimango/issues)
```

## 🎉 完成！

你的项目现在已经在GitHub上了！

别忘了：
- 在仓库设置中添加Topics（如：`rag`, `llm`, `multilingual`, `vector-database`）
- 添加项目描述和网站链接
- 设置GitHub Pages（如果需要）
- 启用Issues和Discussions

---

如有问题，请参考：
- [GitHub官方文档](https://docs.github.com/)
- [Git基础教程](https://git-scm.com/book/zh/v2)

