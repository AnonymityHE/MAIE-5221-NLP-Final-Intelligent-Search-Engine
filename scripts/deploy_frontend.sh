#!/bin/bash
# Jude Frontend Deployment Script

echo "🚀 Jude Frontend Deployment Script"
echo "=================================="
echo ""

# 检查当前目录
if [ ! -d "frontend" ]; then
    echo "❌ Error: frontend directory not found!"
    echo "Please run this script from the project root directory."
    exit 1
fi

cd frontend

echo "📦 Installing dependencies..."
npm install

echo ""
echo "🔨 Building production bundle..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo ""
echo "✅ Build successful!"
echo ""
echo "📊 Build output:"
ls -lh dist/

echo ""
echo "=================================="
echo "✨ Next steps:"
echo ""
echo "Option 1: Deploy to Cloudflare Pages (Recommended)"
echo "  1. Visit https://dash.cloudflare.com/"
echo "  2. Go to Workers & Pages → Create application"
echo "  3. Connect GitHub and select your repository"
echo "  4. Build command: cd frontend && npm run build"
echo "  5. Build output: frontend/dist"
echo "  6. Add custom domain: jude.darkdark.me"
echo ""
echo "Option 2: Deploy to Vercel"
echo "  Run: npm install -g vercel && vercel --prod"
echo ""
echo "Option 3: Deploy to Netlify"
echo "  Run: npm install -g netlify-cli && netlify deploy --prod"
echo ""
echo "Option 4: Manual deployment"
echo "  Upload the 'frontend/dist' folder to your web server"
echo ""
echo "📚 See docs/DEPLOYMENT_GUIDE.md for detailed instructions"
echo "=================================="

