#!/bin/bash
# 监控测试进度

echo "🔍 测试进度监控"
echo "================================================================================"

# Test Set 1
if ps aux | grep -v grep | grep test_set1_complete > /dev/null; then
    echo "✅ Test Set 1 正在运行..."
    LATEST_LOG1=$(ls -t logs/complete_tests/test_set1_final_*.log 2>/dev/null | head -1)
    if [ -f "$LATEST_LOG1" ]; then
        PROGRESS1=$(grep "进度:" "$LATEST_LOG1" | tail -1 | grep -o "[0-9]*/[0-9]*" || echo "启动中")
        echo "   进度: $PROGRESS1"
    fi
else
    echo "⏹️  Test Set 1 已完成或未运行"
fi

# Test Set 2
if ps aux | grep -v grep | grep test_set2_complete > /dev/null; then
    echo "✅ Test Set 2 正在运行..."
    LATEST_LOG2=$(ls -t logs/complete_tests/test_set2_final_*.log 2>/dev/null | head -1)
    if [ -f "$LATEST_LOG2" ]; then
        PROGRESS2=$(grep "进度:" "$LATEST_LOG2" | tail -1 | grep -o "[0-9]*/[0-9]*" || echo "启动中")
        echo "   进度: $PROGRESS2"
    fi
else
    echo "⏹️  Test Set 2 已完成或未运行"
fi

# Test Set 3
if ps aux | grep -v grep | grep test_set3_complete > /dev/null; then
    echo "✅ Test Set 3 正在运行..."
    LATEST_LOG3=$(ls -t logs/complete_tests/test_set3_final_*.log 2>/dev/null | head -1)
    if [ -f "$LATEST_LOG3" ]; then
        PROGRESS3=$(grep "进度:" "$LATEST_LOG3" | tail -1 | grep -o "[0-9]*/[0-9]*" || echo "启动中")
        echo "   进度: $PROGRESS3"
    fi
else
    echo "⏹️  Test Set 3 已完成或未运行"
fi

echo "================================================================================"

# 检查是否有结果文件
echo ""
echo "📊 最新结果文件:"
ls -t test_results/test_set*_complete_*.json 2>/dev/null | head -3 || echo "  暂无结果文件"

