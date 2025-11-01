#!/bin/bash
# 快速设置知识库：将项目文档索引到Milvus

echo "🚀 开始设置RAG知识库..."

# 激活conda环境
if command -v conda &> /dev/null; then
    echo "正在激活conda环境: ise"
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate ise || echo "⚠️  警告：无法激活conda环境，请手动激活"
fi

# 创建documents目录
DOCS_DIR="documents"
mkdir -p "$DOCS_DIR"

echo "📚 准备项目文档..."

# 将项目文档复制到documents目录（转换为Markdown或保持原格式）
# 注意：Word文档需要手动转换或使用工具

# 1. 项目README（已有Markdown）
if [ -f "README.md" ]; then
    cp README.md "$DOCS_DIR/project_readme.md"
    echo "✅ 已添加: README.md"
fi

# 2. 项目公告（已有Markdown）
if [ -f "docs/Project Announcement The Intelligent Search Engine.md" ]; then
    cp "docs/Project Announcement The Intelligent Search Engine.md" "$DOCS_DIR/project_announcement.md"
    echo "✅ 已添加: Project Announcement"
fi

# 3. WarmUp文档
if [ -f "docs/Final WarmUp.md" ]; then
    cp "docs/Final WarmUp.md" "$DOCS_DIR/final_warmup.md"
    echo "✅ 已添加: Final WarmUp"
fi

# 4. 知识库构建指南（可选）
if [ -f "docs/KNOWLEDGE_BASE_GUIDE.md" ]; then
    cp "docs/KNOWLEDGE_BASE_GUIDE.md" "$DOCS_DIR/knowledge_base_guide.md"
    echo "✅ 已添加: Knowledge Base Guide"
fi

echo ""
echo "📋 当前documents目录内容："
ls -lh "$DOCS_DIR" | tail -n +2

echo ""
echo "⚠️  注意："
echo "1. Markdown文件需要先转换为PDF才能使用当前的ingest.py"
echo "2. 或者你可以修改ingest.py支持直接读取Markdown文件"
echo "3. 你可以手动添加更多文档到 $DOCS_DIR/ 目录"
echo ""
echo "下一步："
echo "1. 将其他需要的PDF文档放入 $DOCS_DIR/ 目录"
echo "2. 运行: python scripts/utils/ingest.py"
echo "3. 或者使用API上传文件: curl -X POST http://localhost:8000/api/upload"

