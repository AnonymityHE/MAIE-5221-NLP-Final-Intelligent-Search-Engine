#!/usr/bin/env python3
"""
生成Jude系统架构图 V3 - 优化布局
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np

# 莫兰迪配色方案
MORANDI_COLORS = {
    'dusty_blue': '#9db4c0',
    'sage_green': '#a8b5a0',
    'warm_beige': '#c4b5a0',
    'soft_coral': '#d4a5a5',
    'muted_purple': '#b5a7c4',
    'light_purple': '#d4c9e0',
    'light_blue': '#c9dce8',
    'light_green': '#d4e0d0',
    'light_coral': '#e8d4d4',
    'light_beige': '#e8e0d4',
    'dark_text': '#5a5a5a',
    'medium_text': '#8a8a8a',
    'background': '#f7f6f3'
}

# 创建图表
fig, ax = plt.subplots(figsize=(20, 14))
fig.patch.set_facecolor(MORANDI_COLORS['background'])
ax.set_xlim(0, 20)
ax.set_ylim(0, 14)
ax.axis('off')

def draw_box(ax, x, y, width, height, text, color, text_size=11, bold=False, alpha=0.9):
    """绘制圆角矩形框"""
    box = FancyBboxPatch((x, y), width, height,
                         boxstyle="round,pad=0.08",
                         facecolor=color,
                         edgecolor='white',
                         linewidth=3,
                         alpha=alpha)
    ax.add_patch(box)
    
    weight = 'bold' if bold else '400'
    ax.text(x + width/2, y + height/2, text,
           ha='center', va='center',
           fontsize=text_size, fontweight=weight,
           color=MORANDI_COLORS['dark_text'],
           linespacing=1.3)

def draw_arrow(ax, x1, y1, x2, y2, color, width=2.5, alpha=0.6):
    """绘制箭头"""
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->,head_width=0.4,head_length=0.5',
                           color=color,
                           linewidth=width,
                           alpha=alpha,
                           mutation_scale=25)
    ax.add_patch(arrow)

# ============ 标题 ============
ax.text(10, 13, 'Jude System Architecture', 
       ha='center', va='center', fontsize=22, fontweight='300',
       color=MORANDI_COLORS['dark_text'])
ax.text(10, 12.4, 'Six-Stage Pipeline: Input → Processing → Tools → LLM → Output',
       ha='center', va='center', fontsize=13, fontweight='400',
       color=MORANDI_COLORS['medium_text'], style='italic')

# ============ Stage 1: Input Ingestion (顶部) ============
# 标题
ax.text(3.5, 11.2, '① Input Ingestion', ha='center', va='center',
       fontsize=12, fontweight='600', color=MORANDI_COLORS['dark_text'],
       bbox=dict(boxstyle='round,pad=0.4', facecolor=MORANDI_COLORS['muted_purple'],
                edgecolor='white', alpha=0.3, linewidth=2))

# 三个输入框
draw_box(ax, 1.0, 10.0, 1.5, 0.8, 'Text\nInput', MORANDI_COLORS['light_purple'], 10)
draw_box(ax, 2.7, 10.0, 1.5, 0.8, 'Voice\n(STT)', MORANDI_COLORS['light_purple'], 10)
draw_box(ax, 4.4, 10.0, 1.5, 0.8, 'Image\nUpload', MORANDI_COLORS['light_purple'], 10)

# ============ Stage 2: Preprocessing ============
ax.text(3.5, 9.0, '② Preprocessing', ha='center', va='center',
       fontsize=12, fontweight='600', color=MORANDI_COLORS['dark_text'],
       bbox=dict(boxstyle='round,pad=0.4', facecolor=MORANDI_COLORS['dusty_blue'],
                edgecolor='white', alpha=0.3, linewidth=2))

draw_box(ax, 1.5, 7.8, 4.0, 0.8, 'STT / OCR / Normalization', 
        MORANDI_COLORS['light_blue'], 11)

# 箭头：输入 -> 预处理
for x in [1.75, 3.45, 5.15]:
    draw_arrow(ax, x, 10.0, 3.5, 8.6, MORANDI_COLORS['muted_purple'])

# ============ Stage 3: Agent Routing ============
ax.text(3.5, 7.0, '③ Agent Routing', ha='center', va='center',
       fontsize=12, fontweight='600', color=MORANDI_COLORS['dark_text'],
       bbox=dict(boxstyle='round,pad=0.4', facecolor=MORANDI_COLORS['muted_purple'],
                edgecolor='white', alpha=0.3, linewidth=2))

draw_box(ax, 1.0, 5.6, 5.0, 1.0, 'Agent Router\n(LLM-Driven Intent Detection)',
        MORANDI_COLORS['light_purple'], 11, bold=True)

# 箭头：预处理 -> Agent
draw_arrow(ax, 3.5, 7.8, 3.5, 6.6, MORANDI_COLORS['dusty_blue'])

# ============ Stage 4: Tool Execution (中间) ============
ax.text(3.5, 4.8, '④ Tool Execution (Parallel)', ha='center', va='center',
       fontsize=12, fontweight='600', color=MORANDI_COLORS['dark_text'],
       bbox=dict(boxstyle='round,pad=0.4', facecolor=MORANDI_COLORS['soft_coral'],
                edgecolor='white', alpha=0.3, linewidth=2))

# 五个工具框
tools = [
    ('Local\nRAG', 0.5),
    ('Web\nSearch', 1.8),
    ('Weather\nAPI', 3.1),
    ('Finance\nAPI', 4.4),
    ('Transport\nAPI', 5.7)
]

for tool, x in tools:
    draw_box(ax, x, 3.4, 1.1, 0.8, tool, MORANDI_COLORS['light_coral'], 10)
    # 箭头：Agent -> Tools
    draw_arrow(ax, 3.5, 5.6, x + 0.55, 4.2, MORANDI_COLORS['soft_coral'], width=2)

# ============ Stage 5: Answer Generation (底部左侧) ============
ax.text(3.5, 2.6, '⑤ Answer Generation (Dual-Brain LLM)', ha='center', va='center',
       fontsize=12, fontweight='600', color=MORANDI_COLORS['dark_text'],
       bbox=dict(boxstyle='round,pad=0.4', facecolor=MORANDI_COLORS['sage_green'],
                edgecolor='white', alpha=0.3, linewidth=2))

# 两个LLM框
draw_box(ax, 1.0, 1.0, 2.3, 0.9, 'HKGAI-V1\n(Chinese Text)',
        MORANDI_COLORS['light_purple'], 10, bold=True)
draw_box(ax, 3.7, 1.0, 2.3, 0.9, 'Doubao Seed-1-6\n(Multimodal)',
        MORANDI_COLORS['light_purple'], 10, bold=True)

# 箭头：Tools -> LLMs
for tool, x in tools:
    draw_arrow(ax, x + 0.55, 3.4, 2.15, 1.9, MORANDI_COLORS['sage_green'], width=1.5, alpha=0.4)
    draw_arrow(ax, x + 0.55, 3.4, 4.85, 1.9, MORANDI_COLORS['sage_green'], width=1.5, alpha=0.4)

# ============ Stage 6: Output Rendering (顶部右侧) ============
ax.text(16.5, 11.2, '⑥ Output Rendering', ha='center', va='center',
       fontsize=12, fontweight='600', color=MORANDI_COLORS['dark_text'],
       bbox=dict(boxstyle='round,pad=0.4', facecolor=MORANDI_COLORS['dusty_blue'],
                edgecolor='white', alpha=0.3, linewidth=2))

# 三个输出框
draw_box(ax, 14.0, 10.0, 1.5, 0.8, 'Text\nDisplay', MORANDI_COLORS['light_blue'], 10)
draw_box(ax, 15.7, 10.0, 1.5, 0.8, 'TTS\nAudio', MORANDI_COLORS['light_blue'], 10)
draw_box(ax, 17.4, 10.0, 1.5, 0.8, 'Image\nAnnotation', MORANDI_COLORS['light_blue'], 10)

# 箭头：LLMs -> 输出 (弧形)
draw_arrow(ax, 2.15, 1.9, 14.75, 10.0, MORANDI_COLORS['dusty_blue'], width=2.5, alpha=0.5)
draw_arrow(ax, 4.85, 1.9, 16.45, 10.0, MORANDI_COLORS['dusty_blue'], width=2.5, alpha=0.5)
draw_arrow(ax, 4.85, 1.9, 18.15, 10.0, MORANDI_COLORS['dusty_blue'], width=2.5, alpha=0.5)

# ============ Technology Stack (右侧面板) ============
# 背景框
tech_box = FancyBboxPatch((13.5, 3.0), 6.0, 6.5,
                         boxstyle="round,pad=0.15",
                         facecolor='white',
                         edgecolor=MORANDI_COLORS['light_purple'],
                         linewidth=3,
                         alpha=0.95)
ax.add_patch(tech_box)

ax.text(16.5, 9.0, 'Technology Stack', ha='center', va='top',
       fontsize=14, fontweight='600', color=MORANDI_COLORS['dark_text'])

tech_stack = [
    ('RAG Infrastructure', [
        ('Vector DB:', 'Milvus 2.3', MORANDI_COLORS['soft_coral']),
        ('Embeddings:', 'MiniLM-L12-v2', MORANDI_COLORS['soft_coral']),
        ('Reranking:', 'Cross-Encoder', MORANDI_COLORS['soft_coral']),
    ]),
    ('AI Models', [
        ('LLM (Text):', 'HKGAI-V1', MORANDI_COLORS['muted_purple']),
        ('LLM (Vision):', 'Doubao Seed-1-6', MORANDI_COLORS['muted_purple']),
        ('STT:', 'Web Speech API', MORANDI_COLORS['muted_purple']),
        ('TTS:', 'Edge TTS', MORANDI_COLORS['muted_purple']),
    ]),
    ('Application Stack', [
        ('Backend:', 'FastAPI + Uvicorn', MORANDI_COLORS['dusty_blue']),
        ('Frontend:', 'React + Vite', MORANDI_COLORS['dusty_blue']),
    ])
]

y_pos = 8.4
for category, items in tech_stack:
    # 分类标题
    ax.text(14.0, y_pos, category, ha='left', va='center',
           fontsize=10, fontweight='600', color=MORANDI_COLORS['dark_text'],
           style='italic')
    y_pos -= 0.4
    
    for label, value, color in items:
        # 彩色圆点
        circle = Circle((14.1, y_pos), 0.08, color=color, alpha=0.8, 
                       edgecolor='white', linewidth=1.5)
        ax.add_patch(circle)
        
        ax.text(14.4, y_pos, label, ha='left', va='center',
               fontsize=9, fontweight='600', color=MORANDI_COLORS['dark_text'])
        ax.text(16.5, y_pos, value, ha='left', va='center',
               fontsize=9, fontweight='400', color=MORANDI_COLORS['medium_text'])
        y_pos -= 0.35
    
    y_pos -= 0.15

# ============ Core Features (底部) ============
features_text = 'Core Features: 91.8% Accuracy • 0.77s Search Latency • Dual-Brain Architecture • Intelligent Tool Routing'
ax.text(10, 0.3, features_text,
       ha='center', va='center', fontsize=12, fontweight='400',
       color=MORANDI_COLORS['dark_text'],
       bbox=dict(boxstyle='round,pad=0.6', facecolor='white', 
                edgecolor=MORANDI_COLORS['sage_green'], alpha=0.95, linewidth=3))

plt.tight_layout()
plt.savefig('visualizations/system_architecture.png', dpi=300, bbox_inches='tight',
            facecolor=MORANDI_COLORS['background'], edgecolor='none', pad_inches=0.3)
print("✅ 已重新生成优化布局的系统架构图: system_architecture.png")
plt.close()

