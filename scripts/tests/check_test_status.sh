#!/bin/bash
# 检查测试状态

cd "$(dirname "$0")/../.."

echo "🔍 检查测试状态 - $(date)"
echo "============================================"

# 检查进程
echo "📊 运行中的测试进程:"
ps aux | grep "test_set.*_complete.py" | grep -v grep | awk '{print "   PID: " $2 " | " $11 $12 $13}'

if [ $? -ne 0 ]; then
    echo "   ❌ 没有运行中的测试"
else
    echo ""
fi

echo ""
echo "📁 日志文件:"
if [ -d "logs/complete_tests" ]; then
    ls -lh logs/complete_tests/*.log 2>/dev/null | tail -5 | awk '{print "   " $9 " (" $5 ")"}'
fi

echo ""
echo "📈 最新进度 (Test Set 1):"
if [ -f "logs/complete_tests/$(ls -t logs/complete_tests/test_set1_*.log 2>/dev/null | head -1)" ]; then
    tail -3 logs/complete_tests/$(ls -t logs/complete_tests/test_set1_*.log | head -1)
fi

echo ""
echo "📈 最新进度 (Test Set 2):"
if [ -f "logs/complete_tests/$(ls -t logs/complete_tests/test_set2_*.log 2>/dev/null | head -1)" ]; then
    tail -3 logs/complete_tests/$(ls -t logs/complete_tests/test_set2_*.log | head -1)
fi

echo ""
echo "📈 最新进度 (Test Set 3):"
if [ -f "logs/complete_tests/$(ls -t logs/complete_tests/test_set3_*.log 2>/dev/null | head -1)" ]; then
    tail -3 logs/complete_tests/$(ls -t logs/complete_tests/test_set3_*.log | head -1)
fi

echo ""
echo "============================================"
echo "💡 查看实时日志:"
echo "   tail -f logs/complete_tests/test_set1_*.log"
echo "   tail -f logs/complete_tests/test_set2_*.log"
echo "   tail -f logs/complete_tests/test_set3_*.log"
echo ""
echo "🛑 停止所有测试:"
echo "   pkill -f 'test_set.*_complete.py'"

