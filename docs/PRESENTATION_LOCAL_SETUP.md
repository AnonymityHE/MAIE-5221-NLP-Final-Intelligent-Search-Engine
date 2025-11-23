# 🎤 Jude Presentation - 本地环境启动指南

## 📋 Presentation前准备清单

### ✅ 1. 启动Docker服务

```bash
# 确保Docker Desktop已打开
docker compose up -d

# 验证服务状态
docker ps
# 应该看到: milvus-standalone, milvus-minio, milvus-etcd
```

### ✅ 2. 启动后端API

```bash
# 激活虚拟环境
conda activate ise

# 进入项目目录
cd "/Users/anonymity/Desktop/MAIE/MAIE5221 NLP/Final"

# 启动FastAPI后端（端口5555）
uvicorn backend.main:app --host 0.0.0.0 --port 5555 --reload

# 验证后端运行
# 浏览器访问: http://localhost:5555/docs
```

**后端日志应该显示：**
- ✅ Milvus连接成功
- ✅ Application startup complete
- ✅ Uvicorn running on http://0.0.0.0:5555

### ✅ 3. 启动前端

```bash
# 新开一个终端，进入前端目录
cd "/Users/anonymity/Desktop/MAIE/MAIE5221 NLP/Final/frontend"

# 启动Vite开发服务器（端口5173）
npm run dev

# 前端启动成功后会显示:
#   ➜  Local:   http://localhost:5173/
```

---

## 🎬 Presentation流程

### Part 1: Landing Page展示 (2分钟)

**访问本地前端：** http://localhost:5173

**展示内容：**
1. **Hero Section** - JUDE渐变标题动画
2. **Pain Points & Solutions** - 滚动到Current Limitations和Our Solution
3. **Key Features** - 6个可点击的功能展示，点击展开详情
4. **Core Innovations** - 3大核心创新（01, 02, 03）
5. **FAQ** - 技术问答手风琴效果

### Part 2: System Dashboard展示 (2分钟)

**点击：** "View System Dashboard" 按钮

**展示5个页面：**
1. **Page 1: Data Flow** - 6步数据流程图
2. **Page 2: Core Features** - 技术实现细节（APIs、RAG、Filtering、Multimodal）
3. **Page 3: Evaluation** - 
   - Mean Search Time图表（0.77s平均）
   - Total Latency图表（2.47s平均）
   - Accuracy图表（91.8%平均）
4. **Page 4: Real Q&A Examples** - 真实测试问答案例
5. **Page 5: Team Contributions** - 4位成员的详细贡献

**滚动方式：**
- 鼠标滚轮
- 键盘上下键
- 底部页面指示器点击

### Part 3: Live Demo (1分钟)

**点击：** Landing Page上的 "Experience Jude" 或 "Hey Jude" 按钮

**演示功能：**

#### 选项A：文本查询
```
示例1（RAG）: "香港科技大学在哪里？"
示例2（Web Search）: "今天有什么最新科技新闻？"
示例3（Translation + Auto TTS）: "请勿靠近车门用粤语怎么说？"
```

#### 选项B：图片上传
```
1. 点击图片图标
2. 上传测试图片（例如：figures/error_info.png）
3. 输入："这张图片里有什么内容？"
4. 展示Doubao多模态识别能力
```

#### 选项C：语音输入
```
1. 点击麦克风图标（确保Chrome浏览器）
2. 说："你好，你能听见我说话吗？"
3. 展示Web Speech API实时STT
4. 系统自动回复
```

---

## 🔧 常见问题处理

### 问题1：后端连接失败

**症状：** 前端显示"Network Error"

**解决方案：**
```bash
# 检查后端是否运行
curl http://localhost:5555/api/health

# 如果失败，重启后端
# Ctrl+C 停止后端，然后重新运行：
uvicorn backend.main:app --host 0.0.0.0 --port 5555 --reload
```

### 问题2：Milvus连接失败

**症状：** 后端日志显示"Milvus连接失败"

**解决方案：**
```bash
# 重启Docker服务
docker compose down
docker compose up -d

# 等待30秒让Milvus完全启动
sleep 30

# 重启后端
```

### 问题3：端口被占用

**症状：** "Address already in use"

**解决方案：**
```bash
# 查找占用端口的进程
lsof -ti:5555  # 后端端口
lsof -ti:5173  # 前端端口

# 杀死进程
kill -9 $(lsof -ti:5555)
```

### 问题4：语音输入不工作

**原因：** 
- Web Speech API只支持HTTPS或localhost
- 某些浏览器不支持

**解决方案：**
- ✅ 使用Chrome浏览器
- ✅ 确保使用localhost（不是127.0.0.1）
- ✅ 第一次使用时授予麦克风权限

### 问题5：TTS不自动播放

**原因：** 浏览器阻止自动播放音频

**解决方案：**
- 用户先点击一次页面任意位置（激活音频上下文）
- 或手动点击播放按钮

---

## 📊 Presentation时的最佳实践

### ✅ DO（推荐做法）

1. **提前测试所有功能** - Presentation前1小时完整走一遍流程
2. **准备备用问题** - 如果TA/instructor问问题失败，有备用demo问题
3. **保持窗口全屏** - 按F11进入全屏，更专业
4. **关闭通知** - 开启勿扰模式，避免弹窗干扰
5. **准备截图/录屏** - 如果现场演示失败，可以展示预先录制的视频

### ❌ DON'T（避免做法）

1. ❌ 不要等Presentation时才第一次运行系统
2. ❌ 不要依赖网络（使用本地环境）
3. ❌ 不要在Presentation时调试代码
4. ❌ 不要展示报错日志（提前测试排除错误）
5. ❌ 不要超时（严格控制7分钟）

---

## ⏱️ 时间控制建议

| 环节 | 时间 | 内容 |
|------|------|------|
| Landing Page | 1min | Hero + Features + Innovations |
| Dashboard | 2min | 5页快速浏览，重点Evaluation |
| Live Demo | 1min | 选1-2个功能演示 |
| Q&A | 1min | 回答问题 |
| 缓冲时间 | 2min | 灵活调整 |

---

## 🎯 演讲要点提示

### 开场（30秒）
- "Today we're presenting Jude - a voice-first AI agent."
- "Instead of slides, we built an interactive web application."
- "Let me walk you through it."

### Landing Page（1分钟）
- "Three major pain points we're solving..."
- "Six key features, each clickable for details..."
- "Three core innovations..."

### Dashboard（2分钟）
- "This dashboard shows our technical implementation..."
- "Mean Search Time: 0.77 seconds on average..."
- "91.8% accuracy across 30 test queries..."

### Demo（1分钟）
- "Now let's see it in action..."
- "I can ask about local knowledge, or real-time information..."
- "For translation queries, it automatically triggers TTS..."

### 结束（10秒）
- "That's Jude - combining RAG, multimodal AI, and intelligent routing."
- "Thank you, happy to answer questions."

---

## 📱 应急预案

如果**现场网络/硬件出问题**：

### Plan B: 使用在线Landing Page
- 访问：https://jude.darkdark.me
- 展示静态页面（Dashboard有模拟数据）
- 用录屏展示Demo功能

### Plan C: 使用演讲稿 + 截图
- 打开：`docs/PRESENTATION_SCRIPT.md`
- 配合截图讲解
- 强调"系统已完成，因网络问题无法现场演示"

---

## ✅ Pre-Presentation检查清单

**Presentation前30分钟：**

- [ ] Docker Desktop已打开
- [ ] `docker ps` 显示3个容器运行中
- [ ] 后端运行在 localhost:5555
- [ ] 前端运行在 localhost:5173
- [ ] 浏览器访问前端正常显示
- [ ] 测试一次文本查询功能
- [ ] 测试一次图片上传功能
- [ ] 测试一次语音输入功能（如果演示）
- [ ] 关闭其他不必要的应用和窗口
- [ ] 开启勿扰模式
- [ ] 充满电或连接电源
- [ ] 备份：录屏/截图已准备

**Presentation前5分钟：**

- [ ] 刷新浏览器页面
- [ ] 确认所有服务正常
- [ ] 深呼吸，准备开始！

---

**Good luck with your presentation! 🚀**

