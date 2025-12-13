# 完整测试使用指南

## 📊 测试概览

| 测试集 | 问题数 | 预计时间 | 主要内容 |
|:------|:------|:--------|:---------|
| **Test Set 1** | 48个 | 40-50分钟 | 基础知识、天气、数学、常识 |
| **Test Set 2** | 45个 | 50-60分钟 | 实时信息、虚构知识库、复杂查询 |
| **Test Set 3** | 18个 | 20-30分钟 | 复杂场景、多步推理（不含图片） |
| **总计** | **111个** | **2-3小时** | 全面评估 |

---

## 🚀 快速启动（推荐）

### 方法1: 使用启动脚本（三个测试同时后台运行）

```bash
cd "/Users/anonymity/Desktop/MAIE/MAIE5221 NLP/Final"

# 启动所有测试
bash scripts/tests/run_complete_tests.sh
```

**特点**:
- ✅ 三个测试**并行**运行（更快）
- ✅ 使用nohup后台运行（可以关闭终端）
- ✅ 自动记录日志
- ⚠️  占用更多后端资源

---

### 方法2: 单独运行（串行，更稳定）

#### Test Set 1 (48个问题)
```bash
cd "/Users/anonymity/Desktop/MAIE/MAIE5221 NLP/Final"

# 后台运行
nohup /opt/homebrew/Caskroom/miniforge/base/envs/ise/bin/python \
  scripts/tests/test_set1_complete.py \
  > logs/test_set1_$(date +%Y%m%d_%H%M%S).log 2>&1 &

# 记下PID
echo $! > logs/test_set1.pid
```

#### Test Set 2 (45个问题)
```bash
# 等Test Set 1完成后再运行
nohup /opt/homebrew/Caskroom/miniforge/base/envs/ise/bin/python \
  scripts/tests/test_set2_complete.py \
  > logs/test_set2_$(date +%Y%m%d_%H%M%S).log 2>&1 &

echo $! > logs/test_set2.pid
```

#### Test Set 3 (18个问题)
```bash
nohup /opt/homebrew/Caskroom/miniforge/base/envs/ise/bin/python \
  scripts/tests/test_set3_complete.py \
  > logs/test_set3_$(date +%Y%m%d_%H%M%S).log 2>&1 &

echo $! > logs/test_set3.pid
```

---

## 📈 查看进度

### 实时日志
```bash
# Test Set 1
tail -f logs/complete_tests/test_set1_*.log

# Test Set 2
tail -f logs/complete_tests/test_set2_*.log

# Test Set 3
tail -f logs/complete_tests/test_set3_*.log
```

### 使用状态检查脚本
```bash
bash scripts/tests/check_test_status.sh
```

### 手动检查进程
```bash
# 查看运行中的测试
ps aux | grep test_set

# 查看日志大小（判断进度）
ls -lh logs/complete_tests/
```

---

## 🛑 停止测试

### 停止所有测试
```bash
pkill -f 'test_set.*_complete.py'
```

### 停止单个测试
```bash
# 使用PID
kill $(cat logs/test_set1.pid)
kill $(cat logs/test_set2.pid)
kill $(cat logs/test_set3.pid)

# 或者直接kill
ps aux | grep test_set1_complete
kill <PID>
```

---

## 📁 结果文件

测试完成后会生成JSON结果文件：

```
test_results/
├── test_set1_complete_20251212_160000.json  # 48个问题结果
├── test_set2_complete_20251212_170000.json  # 45个问题结果
└── test_set3_complete_20251212_180000.json  # 18个问题结果
```

### 结果结构
```json
{
  "timestamp": "20251212_160000",
  "total_questions": 48,
  "successful": 45,
  "failed": 3,
  "success_rate": 93.75,
  "avg_response_time": 14.23,
  "total_time_minutes": 45.5,
  "results": [
    {
      "id": "EN-1",
      "question": "...",
      "language": "English",
      "category": "Knowledge",
      "result": {
        "success": true,
        "answer": "...",
        "response_time": 12.5,
        "tools_used": ["web_search"]
      }
    }
  ]
}
```

---

## ⚠️  注意事项

### 1. 后端必须运行
```bash
# 检查后端
curl -s http://localhost:5555/api/agent_query \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"query":"test"}' | head -100
```

### 2. Docker容器必须运行
```bash
docker ps | grep milvus
```

### 3. 测试会很慢
- 很多问题需要web_search（10-25秒/问题）
- 总共111个问题，预计**2-3小时**
- 可以关闭终端，测试在后台继续

### 4. 可能的错误
- **Timeout**: Web search超过10秒会超时（正常）
- **404**: Tavily API偶尔会返回404（网络问题）
- **Rate Limit**: API调用太快可能被限流

### 5. 图片问题已跳过
Test Set 3的6个图片问题（EN-1,2,3和CN-1,2,3）需要multimodal接口，本次跳过。

---

## 📊 预期结果

根据优化后的性能：

| 指标 | 预期值 |
|:-----|:------|
| **总成功率** | 90-95% |
| **工具准确率** | 95-100% |
| **平均响应时间** | 12-16秒 |
| **最慢查询** | 20-30秒（复杂web_search） |
| **最快查询** | 5-8秒（简单knowledge/math） |

---

## 💡 使用建议

### 推荐流程：
1. **晚上启动**：`bash scripts/tests/run_complete_tests.sh`
2. **关闭终端**：测试继续后台运行
3. **第二天查看**：`bash scripts/tests/check_test_status.sh`
4. **分析结果**：查看JSON文件

### 不推荐：
- ❌ 白天运行并等待（太慢）
- ❌ 串行运行所有测试（更慢）
- ❌ 在不稳定的网络环境运行

---

## 🔧 故障排查

### 测试卡住不动
```bash
# 查看日志末尾
tail -50 logs/complete_tests/test_set1_*.log

# 检查后端
tail -50 logs/backend_optimized.log

# 重启后端
pkill -f "uvicorn backend.main"
sleep 3
nohup python -m uvicorn backend.main:app --host 0.0.0.0 --port 5555 &
```

### 测试提前结束
```bash
# 查看错误
grep -i "error\|failed\|exception" logs/complete_tests/*.log

# 重新运行失败的测试集
python scripts/tests/test_set1_complete.py
```

---

## 📞 需要帮助？

查看日志文件获取详细错误信息：
```bash
# 查看所有错误
grep -i "error\|❌" logs/complete_tests/*.log

# 查看成功率
grep -i "测试总结" logs/complete_tests/*.log -A 5
```

