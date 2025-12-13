#!/bin/bash
# 运行Test Set 1, 2, 3的完整测试
# 使用nohup后台运行，分别记录日志

cd "$(dirname "$0")/../.."

PYTHON="/opt/homebrew/Caskroom/miniforge/base/envs/ise/bin/python"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🚀 开始完整测试 - $(date)"
echo "============================================"
echo "📋 测试计划:"
echo "  • Test Set 1: 48个基础问题"
echo "  • Test Set 2: 45个进阶问题（含虚构KB）"
echo "  • Test Set 3: 18个复杂场景（不含图片）"
echo "  • 总计: 111个问题"
echo "  • 预计耗时: 2-3小时"
echo "============================================"
echo ""

# 创建日志目录
mkdir -p logs/complete_tests

# Test Set 1
echo "1️⃣  启动 Test Set 1 (48个问题)..."
nohup $PYTHON scripts/tests/test_set1_complete.py > logs/complete_tests/test_set1_${TIMESTAMP}.log 2>&1 &
PID1=$!
echo "   PID: $PID1"
echo "   日志: logs/complete_tests/test_set1_${TIMESTAMP}.log"

# 等待10秒避免同时启动造成冲突
echo "   等待10秒..."
sleep 10

# Test Set 2
echo "2️⃣  启动 Test Set 2 (45个问题)..."
nohup $PYTHON scripts/tests/test_set2_complete.py > logs/complete_tests/test_set2_${TIMESTAMP}.log 2>&1 &
PID2=$!
echo "   PID: $PID2"
echo "   日志: logs/complete_tests/test_set2_${TIMESTAMP}.log"

# 等待10秒
echo "   等待10秒..."
sleep 10

# Test Set 3
echo "3️⃣  启动 Test Set 3 (18个问题)..."
nohup $PYTHON scripts/tests/test_set3_complete.py > logs/complete_tests/test_set3_${TIMESTAMP}.log 2>&1 &
PID3=$!
echo "   PID: $PID3"
echo "   日志: logs/complete_tests/test_set3_${TIMESTAMP}.log"

echo ""
echo "✅ 所有测试已启动！"
echo "============================================"
echo "📊 进度查看:"
echo "  tail -f logs/complete_tests/test_set1_${TIMESTAMP}.log"
echo "  tail -f logs/complete_tests/test_set2_${TIMESTAMP}.log"
echo "  tail -f logs/complete_tests/test_set3_${TIMESTAMP}.log"
echo ""
echo "🔍 检查进程:"
echo "  ps aux | grep test_set"
echo ""
echo "🛑 停止测试:"
echo "  kill $PID1 $PID2 $PID3"
echo ""
echo "📁 结果文件:"
echo "  test_results/test_set1_complete_*.json"
echo "  test_results/test_set2_complete_*.json"
echo "  test_results/test_set3_complete_*.json"
echo "============================================"

# 保存PIDs到文件
echo "$PID1" > logs/complete_tests/test_set1.pid
echo "$PID2" > logs/complete_tests/test_set2.pid
echo "$PID3" > logs/complete_tests/test_set3.pid

echo ""
echo "💡 测试将在后台运行，预计2-3小时完成"
echo "   你可以关闭终端，测试会继续运行"

