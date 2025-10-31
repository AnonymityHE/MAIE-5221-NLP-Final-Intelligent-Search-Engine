#!/bin/bash
# 启动API服务脚本

echo "============================================================"
echo "启动RAG问答系统API服务"
echo "============================================================"

# 检查conda环境
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "⚠️  未检测到激活的conda环境"
    echo "   正在尝试激活 ise 环境..."
    
    # 尝试激活conda环境
    if command -v conda &> /dev/null; then
        eval "$(conda shell.bash hook)"
        conda activate ise 2>/dev/null || {
            echo "❌ 无法激活 ise 环境"
            echo ""
            echo "请手动激活conda环境："
            echo "  conda activate ise"
            echo ""
            echo "然后运行："
            echo "  uvicorn backend.main:app --reload"
            exit 1
        }
    else
        echo "❌ 未找到conda命令"
        echo "   请手动激活conda环境后运行: uvicorn backend.main:app --reload"
        exit 1
    fi
fi

echo "✅ Conda环境: $CONDA_DEFAULT_ENV"

# 检查Milvus
echo ""
echo "检查Milvus服务..."
if docker ps | grep -q milvus-standalone; then
    echo "✅ Milvus服务正在运行"
else
    echo "⚠️  Milvus服务未运行"
    echo "   正在启动Milvus..."
    docker compose up -d 2>/dev/null || docker-compose up -d
    
    # 等待Milvus启动
    echo "   等待Milvus启动（10秒）..."
    sleep 10
    
    if docker ps | grep -q milvus-standalone; then
        echo "✅ Milvus启动成功"
    else
        echo "❌ Milvus启动失败，请手动检查："
        echo "   docker compose up -d"
        exit 1
    fi
fi

# 检查依赖
echo ""
echo "检查Python依赖..."
if python -c "import fastapi" 2>/dev/null; then
    echo "✅ FastAPI已安装"
else
    echo "⚠️  依赖可能不完整"
    echo "   建议运行: pip install -r requirements.txt"
    read -p "   是否现在安装依赖？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install -r requirements.txt
    fi
fi

# 检查端口占用
echo ""
echo "检查端口8000..."
PORT=8000
if lsof -ti:$PORT > /dev/null 2>&1; then
    PID=$(lsof -ti:$PORT)
    PROCESS_INFO=$(ps -p $PID -o comm= 2>/dev/null || echo "未知进程")
    
    echo "⚠️  端口 $PORT 已被占用"
    echo "   进程ID: $PID"
    echo "   进程名: $PROCESS_INFO"
    echo ""
    
    # 尝试检查是否是我们的API服务
    API_RUNNING=false
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        API_RUNNING=true
        echo "✅ 检测到API服务正在运行"
        echo "   健康检查: http://localhost:8000/api/health"
        
        # 测试健康检查
        HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/health)
        if echo "$HEALTH_RESPONSE" | grep -q "status.*ok" || echo "$HEALTH_RESPONSE" | grep -q '"status"' ; then
            echo "✅ API服务运行正常"
            echo ""
            echo "当前API服务已正常运行，无需重启。"
            echo "访问地址："
            echo "  - API文档: http://localhost:8000/docs"
            echo "  - 健康检查: http://localhost:8000/api/health"
            echo ""
            read -p "是否仍要重启服务？(y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "保持当前服务运行"
                exit 0
            fi
        else
            echo "⚠️  API服务可能异常"
            echo "   响应: $HEALTH_RESPONSE"
        fi
    else
        echo "⚠️  端口被占用但API服务可能异常"
    fi
    
    echo ""
    echo "选项："
    echo "  1. 终止占用端口的进程并重启服务"
    echo "  2. 取消操作"
    echo ""
    read -p "请选择 (1/2): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^1$ ]]; then
        echo "正在终止进程 $PID..."
        kill $PID 2>/dev/null || {
            echo "❌ 无法终止进程，可能需要sudo权限"
            echo "   手动终止命令: kill $PID"
            echo "   或使用: sudo kill $PID"
            exit 1
        }
        
        # 等待进程退出
        sleep 2
        
        # 检查是否成功终止
        if lsof -ti:$PORT > /dev/null 2>&1; then
            echo "⚠️  进程仍在运行，尝试强制终止..."
            kill -9 $PID 2>/dev/null
            sleep 1
        fi
        
        if lsof -ti:$PORT > /dev/null 2>&1; then
            echo "❌ 无法终止进程，请手动处理"
            exit 1
        else
            echo "✅ 进程已终止"
        fi
    else
        echo "取消操作"
        exit 0
    fi
fi

# 启动API
echo ""
echo "============================================================"
echo "启动API服务..."
echo "============================================================"
echo "API将在 http://localhost:8000 启动"
echo "Swagger文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

cd "$(dirname "$0")/.."
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

