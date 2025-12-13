#!/bin/bash
# 依次运行测试（避免资源竞争）

cd "/Users/anonymity/Desktop/MAIE/MAIE5221 NLP/Final"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PYTHON=/opt/homebrew/Caskroom/miniforge/base/envs/ise/bin/python

echo "🚀 开始顺序测试 - $TIMESTAMP"
echo "================================================================================"

# Test Set 1
echo "1️⃣  运行 Test Set 1 (48问题)..."
$PYTHON scripts/tests/test_set1_complete.py > logs/test_set1_seq_$TIMESTAMP.log 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Test Set 1 完成"
else
    echo "❌ Test Set 1 失败"
fi

sleep 5

# Test Set 2  
echo "2️⃣  运行 Test Set 2 (45问题)..."
$PYTHON scripts/tests/test_set2_complete.py > logs/test_set2_seq_$TIMESTAMP.log 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Test Set 2 完成"
else
    echo "❌ Test Set 2 失败"
fi

sleep 5

# Test Set 3
echo "3️⃣  运行 Test Set 3 (18问题)..."
$PYTHON scripts/tests/test_set3_complete.py > logs/test_set3_seq_$TIMESTAMP.log 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Test Set 3 完成"
else
    echo "❌ Test Set 3 失败"
fi

echo "================================================================================"
echo "✅ 所有测试完成！"
echo "📊 结果文件: test_results/test_set*_complete_*.json"

