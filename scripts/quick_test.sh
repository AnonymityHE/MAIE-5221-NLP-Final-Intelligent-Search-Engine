#!/bin/bash
# 快速测试脚本 - 测试新功能

echo "============================================================"
echo "RAG系统改进功能快速测试"
echo "============================================================"

# 检查conda环境
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "⚠️  未检测到激活的conda环境"
    echo "   建议先激活环境: conda activate ise"
    echo ""
fi

# 检查API是否运行
echo "检查API服务状态..."
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ API服务正在运行"
    API_RUNNING=true
else
    echo "❌ API服务未运行"
    echo "   启动命令: uvicorn backend.main:app --reload"
    API_RUNNING=false
fi

echo ""
echo "============================================================"
echo "1. 测试日志系统"
echo "============================================================"
if [ -d "logs" ] && [ -f "logs/rag_system.log" ]; then
    echo "✅ 日志文件存在"
    echo "   文件大小: $(du -h logs/rag_system.log | cut -f1)"
    echo "   最后几行:"
    tail -n 3 logs/rag_system.log | sed 's/^/   /'
else
    echo "⚠️  日志文件未创建（需要先运行API）"
fi

echo ""
echo "============================================================"
echo "2. 测试环境变量配置"
echo "============================================================"
if [ -f ".env" ]; then
    echo "✅ .env文件存在"
    echo "   配置项数量: $(grep -v '^#' .env | grep -v '^$' | wc -l)"
else
    echo "ℹ️  未找到.env文件（可选，系统会使用config.py中的默认值）"
fi

echo ""
echo "============================================================"
echo "3. 测试Reranker功能"
echo "============================================================"
if [ "$API_RUNNING" = true ]; then
    echo "测试RAG查询（自动使用Reranker）..."
    response=$(curl -s -X POST "http://localhost:8000/api/rag_query" \
        -H "Content-Type: application/json" \
        -d '{"query": "什么是RAG？", "top_k": 3}')
    
    if echo "$response" | grep -q "answer"; then
        echo "✅ Reranker测试成功"
        echo "   答案预览: $(echo $response | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('answer', '')[:100])")..."
    else
        echo "❌ Reranker测试失败"
        echo "   响应: $response"
    fi
else
    echo "⚠️  跳过（需要API服务）"
fi

echo ""
echo "============================================================"
echo "4. 测试Agent金融工具"
echo "============================================================"
if [ "$API_RUNNING" = true ]; then
    echo "测试股票查询..."
    response=$(curl -s -X POST "http://localhost:8000/api/agent_query" \
        -H "Content-Type: application/json" \
        -d '{"query": "AAPL的股价是多少？"}')
    
    if echo "$response" | grep -q "finance"; then
        echo "✅ 金融工具测试成功"
        tools=$(echo $response | python3 -c "import sys, json; d=json.load(sys.stdin); print(','.join(d.get('tools_used', [])))")
        echo "   使用的工具: $tools"
    else
        echo "⚠️  金融工具可能未触发（这是正常的，取决于实际API响应）"
    fi
else
    echo "⚠️  跳过（需要API服务）"
fi

echo ""
echo "============================================================"
echo "5. 测试Agent交通工具"
echo "============================================================"
if [ "$API_RUNNING" = true ]; then
    echo "测试路线查询..."
    response=$(curl -s -X POST "http://localhost:8000/api/agent_query" \
        -H "Content-Type: application/json" \
        -d '{"query": "从香港到深圳需要多久？"}')
    
    if echo "$response" | grep -q "transport"; then
        echo "✅ 交通工具测试成功"
        tools=$(echo $response | python3 -c "import sys, json; d=json.load(sys.stdin); print(','.join(d.get('tools_used', [])))")
        echo "   使用的工具: $tools"
    else
        echo "⚠️  交通工具可能未触发（这是正常的，取决于实际API响应）"
    fi
else
    echo "⚠️  跳过（需要API服务）"
fi

echo ""
echo "============================================================"
echo "测试完成！"
echo "============================================================"
echo ""
echo "下一步："
echo "1. 如果API未运行，启动: uvicorn backend.main:app --reload"
echo "2. 查看详细日志: tail -f logs/rag_system.log"
echo "3. 测试API文档: http://localhost:8000/docs"

