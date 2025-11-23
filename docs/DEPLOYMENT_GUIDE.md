# 🚀 Jude Frontend Deployment Guide

## 部署到 jude.darkdark.me

你有三个主要部署选项，推荐使用 **Cloudflare Pages**（最简单）。

---

## 方案一：Cloudflare Pages（推荐）✨

### 优势
- ✅ 域名已在Cloudflare，DNS配置自动
- ✅ 完全免费，无限带宽
- ✅ 全球CDN加速
- ✅ 自动HTTPS
- ✅ 支持GitHub自动部署

### 部署步骤

#### 1. 准备代码

确保你的前端代码已经推送到GitHub。

#### 2. 登录Cloudflare Dashboard

访问：https://dash.cloudflare.com/

#### 3. 创建Cloudflare Pages项目

1. 点击侧边栏 **"Workers & Pages"**
2. 点击 **"Create application"**
3. 选择 **"Pages"** tab
4. 点击 **"Connect to Git"**
5. 授权GitHub访问，选择你的仓库：
   - `AnonymityHE/MAIE-5221-NLP-Final-Intelligent-Search-Engine`
6. 配置构建设置：

```yaml
Project name: jude-voice-agent
Production branch: main
Framework preset: Vite
Build command: cd frontend && npm install && npm run build
Build output directory: frontend/dist
Root directory: /
```

7. **Environment variables**（环境变量）：

点击 **"Add variable"**，添加以下变量（如果前端需要）：

```bash
# 如果前端需要连接后端API
VITE_API_BASE_URL=https://your-backend-domain.com
```

8. 点击 **"Save and Deploy"**

#### 4. 配置自定义域名

部署完成后：

1. 进入你的Pages项目页面
2. 点击 **"Custom domains"** tab
3. 点击 **"Set up a custom domain"**
4. 输入：`jude.darkdark.me`
5. Cloudflare会自动创建DNS记录（CNAME）
6. 等待几分钟，SSL证书自动配置

#### 5. 验证部署

访问：https://jude.darkdark.me

✅ 你的前端现在已经上线！

---

## 方案二：Vercel（备选）

### 部署步骤

#### 1. 安装Vercel CLI

```bash
npm install -g vercel
```

#### 2. 登录Vercel

```bash
vercel login
```

#### 3. 部署前端

```bash
cd "/Users/anonymity/Desktop/MAIE/MAIE5221 NLP/Final/frontend"
vercel --prod
```

按照提示操作：
- Link to existing project? **No**
- Project name? **jude-voice-agent**
- Which directory? **`./`** (当前目录)
- Build command? **`npm run build`**
- Output directory? **`dist`**

#### 4. 配置自定义域名

1. 访问 Vercel Dashboard：https://vercel.com/dashboard
2. 进入你的项目
3. 点击 **"Settings"** → **"Domains"**
4. 添加域名：`jude.darkdark.me`
5. Vercel会提供DNS配置指令，例如：

```
Type: CNAME
Name: jude
Value: cname.vercel-dns.com
```

6. 回到Cloudflare Dashboard
7. 进入 **"DNS"** → **"Records"**
8. 点击 **"Add record"**：
   - Type: `CNAME`
   - Name: `jude`
   - Target: `cname.vercel-dns.com`（Vercel提供的值）
   - Proxy status: **DNS only**（灰色云朵）
9. 保存，等待DNS传播（5-10分钟）

#### 5. 验证部署

访问：https://jude.darkdark.me

---

## 方案三：Netlify（备选）

### 部署步骤

#### 1. 安装Netlify CLI

```bash
npm install -g netlify-cli
```

#### 2. 登录Netlify

```bash
netlify login
```

#### 3. 部署前端

```bash
cd "/Users/anonymity/Desktop/MAIE/MAIE5221 NLP/Final/frontend"
netlify deploy --prod
```

按照提示操作：
- Create & configure a new site? **Yes**
- Team: 选择你的team
- Site name: **jude-voice-agent**
- Publish directory: **`dist`**

#### 4. 配置自定义域名

1. 访问 Netlify Dashboard
2. 进入你的项目
3. 点击 **"Domain settings"**
4. 点击 **"Add custom domain"**
5. 输入：`jude.darkdark.me`
6. Netlify会提供DNS配置，例如：

```
Type: CNAME
Name: jude
Value: your-site.netlify.app
```

7. 回到Cloudflare，添加CNAME记录（同Vercel步骤）

---

## 🔧 前端配置调整

### 更新API Base URL

如果你的后端部署在不同的域名，需要更新前端的API调用地址。

#### 方法1：使用环境变量

创建 `frontend/.env.production`：

```bash
VITE_API_BASE_URL=https://api.darkdark.me
```

更新 `frontend/vite.config.ts`：

```typescript
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:5555',
          changeOrigin: true,
          secure: false,
        },
      },
    },
  }
})
```

更新 `frontend/src/pages/DemoInterface.tsx`（如果需要）：

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5555';

// 在fetch调用中使用
const response = await fetch(`${API_BASE_URL}/api/agent_query`, {
  // ...
});
```

---

## 📱 后端部署（可选）

如果你也想部署后端，可以使用：

### Railway（推荐）

1. 访问：https://railway.app/
2. 连接GitHub仓库
3. 添加环境变量（API Keys）
4. 自动部署FastAPI后端
5. Railway会提供域名，例如：`jude-api.railway.app`

### Render

1. 访问：https://render.com/
2. 创建 **"New Web Service"**
3. 连接GitHub
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### Docker部署（Railway/Render）

创建 `Dockerfile`：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 5555

# 启动命令
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "5555"]
```

---

## 🔒 CORS配置

如果前端和后端在不同域名，确保后端允许跨域请求。

更新 `backend/main.py`：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jude.darkdark.me",
        "http://localhost:5173",  # 本地开发
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 部署后验证清单

- [ ] 前端可以正常访问 `https://jude.darkdark.me`
- [ ] Landing Page动画正常显示
- [ ] Dashboard可以打开并滚动
- [ ] Demo Interface可以输入文本
- [ ] API连接正常（如果后端也部署了）
- [ ] 语音按钮可以点击（如果连接后端）
- [ ] HTTPS证书有效
- [ ] 所有静态资源正常加载（图片、字体）

---

## 🐛 常见问题

### 1. 构建失败：找不到模块

**解决方案**：确保 `package.json` 中所有依赖都正确列出

```bash
cd frontend
npm install
npm run build  # 本地测试构建
```

### 2. 404错误：页面刷新后找不到

**解决方案**：配置SPA路由重定向

Cloudflare Pages会自动处理，如果使用Vercel/Netlify，创建：

**Vercel**: `frontend/vercel.json`
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

**Netlify**: `frontend/_redirects`
```
/*    /index.html   200
```

### 3. API调用失败：CORS错误

**解决方案**：
1. 检查后端CORS配置
2. 确保前端使用正确的API URL
3. 检查浏览器控制台的错误信息

### 4. 环境变量不生效

**解决方案**：
- Cloudflare Pages：在Dashboard中设置环境变量
- Vercel/Netlify：在项目设置中添加环境变量
- 重新部署项目

---

## 📈 部署后优化

### 1. 启用Cloudflare缓存

在Cloudflare Dashboard中：
- **Speed** → **Optimization**
- 启用 **Auto Minify**（HTML, CSS, JS）
- 启用 **Brotli** 压缩

### 2. 配置Analytics

Cloudflare Pages提供免费的Web Analytics：
- 在Pages项目中启用 **Web Analytics**
- 监控访问量、性能指标

### 3. 设置Page Rules

优化静态资源缓存：
- URL: `jude.darkdark.me/assets/*`
- Cache Level: **Cache Everything**
- Edge Cache TTL: **1 month**

---

## 🎯 推荐方案总结

| 平台 | 推荐度 | 理由 |
|------|--------|------|
| **Cloudflare Pages** | ⭐⭐⭐⭐⭐ | 域名同平台，配置最简单，免费无限带宽 |
| **Vercel** | ⭐⭐⭐⭐ | 性能优秀，CI/CD强大，需要手动配置DNS |
| **Netlify** | ⭐⭐⭐⭐ | 功能全面，易用，需要手动配置DNS |

**最终推荐**：使用 **Cloudflare Pages** + 自动GitHub部署。

---

## 📝 下一步

1. 选择部署平台（推荐Cloudflare Pages）
2. 按照上述步骤部署前端
3. 配置自定义域名 `jude.darkdark.me`
4. 验证访问和功能
5. （可选）部署后端到Railway/Render
6. 更新README.md添加在线演示链接

**部署完成后，你就可以在Presentation时直接访问 `https://jude.darkdark.me` 进行演示了！** 🎉

