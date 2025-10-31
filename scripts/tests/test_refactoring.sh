#!/bin/bash
# 测试重构后的代码 - 验证所有导入和功能正常

echo "============================================================"
echo "测试重构后的Services目录"
echo "============================================================"

# 检查conda环境
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "⚠️  未检测到激活的conda环境"
    echo "   正在尝试激活 ise 环境..."
    
    if command -v conda &> /dev/null; then
        eval "$(conda shell.bash hook)"
        conda activate ise 2>/dev/null || {
            echo "❌ 无法激活 ise 环境"
            echo ""
            echo "请手动激活conda环境："
            echo "  conda activate ise"
            echo ""
            exit 1
        }
    else
        echo "❌ 未找到conda命令"
        exit 1
    fi
fi

echo "✅ Conda环境: $CONDA_DEFAULT_ENV"
echo ""

# 测试1: 导入测试
echo "测试 1: 导入路径测试"
echo "----------------------------------------"
python3 -c "
import sys
sys.path.insert(0, '.')

try:
    # 测试新导入方式
    from services.core import settings, logger
    from services.llm import unified_llm_client
    from services.vector import retriever
    from services.agent import agent
    from services.storage import file_storage
    print('✅ 新导入路径测试成功')
except Exception as e:
    print(f'❌ 新导入路径测试失败: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    # 测试向后兼容导入
    from services import settings, logger, unified_llm_client, retriever, agent
    print('✅ 向后兼容导入测试成功')
except Exception as e:
    print(f'❌ 向后兼容导入测试失败: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "❌ 导入测试失败"
    exit 1
fi

echo ""
echo "测试 2: API服务检查"
echo "----------------------------------------"

# 检查API是否运行
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ API服务正在运行"
    echo ""
    
    # 测试健康检查
    echo "测试健康检查端点..."
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/health)
    echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
    
    echo ""
    echo "============================================================"
    echo "运行完整功能测试..."
    echo "============================================================"
    
    # 运行Python测试脚本
    python3 scripts/tests/test_improvements.py
    
else
    echo "⚠️  API服务未运行"
    echo ""
    echo "请先启动API服务："
    echo "  bash scripts/utils/start_api.sh"
    echo ""
    echo "或手动启动："
    echo "  conda activate ise"
    echo "  uvicorn backend.main:app --reload"
    echo ""
    exit 1
fi

echo ""
echo "============================================================"
echo "✅ 所有测试完成！"
echo "============================================================"

