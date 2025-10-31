# 启动API服务指南

如果无法访问 `http://localhost:8000/docs`，说明API服务未运行。

## 快速启动（推荐）

使用启动脚本：

```bash
bash scripts/start_api.sh
```

## 手动启动步骤

### 1. 激活Conda环境

```bash
conda activate ise
```

如果环境不存在，先创建：

```bash
conda create -n ise python=3.10
conda activate ise
pip install -r requirements.txt
```

### 2. 启动Milvus（如果未运行）

```bash
# 检查Milvus状态
docker ps | grep milvus

# 如果未运行，启动Milvus
docker compose up -d

# 或使用旧版本命令
docker-compose up -d
```

### 3. 启动API服务

在项目根目录运行：

```bash
uvicorn backend.main:app --reload
```

## 验证服务已启动

启动成功后，你应该看到：

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

然后就可以访问：
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health

## 常见问题

### 问题1: `ModuleNotFoundError: No module named 'fastapi'`

**解决**：
```bash
conda activate ise
pip install -r requirements.txt
```

### 问题2: `连接Milvus失败`

**解决**：
```bash
# 检查Docker是否运行
docker ps

# 启动Milvus
docker compose up -d

# 检查Milvus容器状态
docker compose ps
```

### 问题3: 端口8000被占用

**解决**：
```bash
# 查找占用端口的进程
lsof -ti:8000

# 或使用其他端口
uvicorn backend.main:app --reload --port 8001
```

### 问题4: Conda环境未激活

**解决**：
```bash
# 查看所有conda环境
conda env list

# 激活环境（根据你的环境名调整）
conda activate ise

# 如果环境不存在，创建它
conda create -n rag_system python=3.10
conda activate ise
pip install -r requirements.txt
```

## 停止服务

在运行API的终端按 `Ctrl+C` 停止服务。

## 后台运行（可选）

如果想在后台运行API：

```bash
# 使用nohup
nohup uvicorn backend.main:app --reload > api.log 2>&1 &

# 查看日志
tail -f api.log

# 停止后台服务
pkill -f "uvicorn backend.main:app"
```

