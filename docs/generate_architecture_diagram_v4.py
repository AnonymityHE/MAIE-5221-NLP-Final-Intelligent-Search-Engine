#!/usr/bin/env python3
"""
生成Jude系统架构图 V4 - 垂直流程布局
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
fig, ax = plt.subplots(figsize=(20, 16))
fig.patch.set_facecolor(MORANDI_COLORS['background'])
ax.set_xlim(0, 20)
ax.set_ylim(0, 16)
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

def draw_stage_label(ax, x, y, text, number, color):
    """绘制阶段标签"""
    ax.text(x, y, f'{number} {text}', ha='left', va='center',
           fontsize=13, fontweight='600', color=MORANDI_COLORS['dark_text'],
           bbox=dict(boxstyle='round,pad=0.4', facecolor=color,
                    edgecolor='white', alpha=0.3, linewidth=2))

# ============ 标题 ============
ax.text(7.5, 15.2, 'Jude System Architecture', 
       ha='center', va='center', fontsize=24, fontweight='300',
       color=MORANDI_COLORS['dark_text'])
ax.text(7.5, 14.5, 'Six-Stage Pipeline: Input → Processing → Tools → LLM → Output',
       ha='center', va='center', fontsize=14, fontweight='400',
       color=MORANDI_COLORS['medium_text'], style='italic')

# ============ Stage 1: Input Ingestion ============
# 架构图居中位置偏移量
offset_x = 1.5

draw_stage_label(ax, 0.5 + offset_x, 13.5, 'Input Ingestion', '①', MORANDI_COLORS['muted_purple'])

draw_box(ax, 0.5 + offset_x, 12.2, 2.8, 1.0, 'Text\nInput', MORANDI_COLORS['light_purple'], 13)
draw_box(ax, 3.6 + offset_x, 12.2, 2.8, 1.0, 'Voice\n(STT)', MORANDI_COLORS['light_purple'], 13)
draw_box(ax, 6.7 + offset_x, 12.2, 2.8, 1.0, 'Image\nUpload', MORANDI_COLORS['light_purple'], 13)

# ============ Stage 2: Preprocessing ============
draw_stage_label(ax, 0.5 + offset_x, 11.2, 'Preprocessing', '②', MORANDI_COLORS['dusty_blue'])

draw_box(ax, 1.5 + offset_x, 10.0, 7.0, 1.0, 'STT / OCR / Normalization', 
        MORANDI_COLORS['light_blue'], 14)

# 箭头：输入 -> 预处理
center_x = 5.0 + offset_x
for x in [1.9 + offset_x, 5.0 + offset_x, 8.1 + offset_x]:
    draw_arrow(ax, x, 12.2, center_x, 11.0, MORANDI_COLORS['muted_purple'])

# ============ Stage 3: Agent Routing ============
draw_stage_label(ax, 0.5 + offset_x, 9.2, 'Agent Routing', '③', MORANDI_COLORS['muted_purple'])

draw_box(ax, 0.5 + offset_x, 7.8, 9.0, 1.2, 'Agent Router\n(LLM-Driven Intent Detection)',
        MORANDI_COLORS['light_purple'], 14, bold=True)

# 箭头：预处理 -> Agent
draw_arrow(ax, center_x, 10.0, center_x, 9.0, MORANDI_COLORS['dusty_blue'])

# ============ Stage 4: Tool Execution ============
draw_stage_label(ax, 0.5 + offset_x, 7.0, 'Tool Execution (Parallel)', '④', MORANDI_COLORS['soft_coral'])

# 更宽的块，间距更大
tools = [
    ('Local\nRAG', 0.3 + offset_x),
    ('Web\nSearch', 2.2 + offset_x),
    ('Weather\nAPI', 4.1 + offset_x),
    ('Finance\nAPI', 6.0 + offset_x),
    ('Transport\nAPI', 7.9 + offset_x)
]

tool_width = 1.7  # 更宽的块

for tool, x in tools:
    draw_box(ax, x, 5.6, tool_width, 1.0, tool, MORANDI_COLORS['light_coral'], 13)
    # 箭头：Agent -> Tools
    draw_arrow(ax, center_x, 7.8, x + tool_width/2, 6.6, MORANDI_COLORS['soft_coral'], width=2)

# ============ Stage 5: Answer Generation ============
draw_stage_label(ax, 0.5 + offset_x, 4.8, 'Answer Generation (Dual-Brain LLM)', '⑤', MORANDI_COLORS['sage_green'])

draw_box(ax, 0.8 + offset_x, 3.2, 4.0, 1.1, 'HKGAI-V1\n(Chinese Text)',
        MORANDI_COLORS['light_purple'], 13, bold=True)
draw_box(ax, 5.2 + offset_x, 3.2, 4.0, 1.1, 'Doubao Seed-1-6\n(Multimodal)',
        MORANDI_COLORS['light_purple'], 13, bold=True)

llm1_center = 2.8 + offset_x
llm2_center = 7.2 + offset_x

# 箭头：Tools -> LLMs
for tool, x in tools:
    draw_arrow(ax, x + tool_width/2, 5.6, llm1_center, 4.3, MORANDI_COLORS['sage_green'], width=1.5, alpha=0.4)
    draw_arrow(ax, x + tool_width/2, 5.6, llm2_center, 4.3, MORANDI_COLORS['sage_green'], width=1.5, alpha=0.4)

# ============ Stage 6: Output Rendering ============
draw_stage_label(ax, 0.5 + offset_x, 2.4, 'Output Rendering', '⑥', MORANDI_COLORS['dusty_blue'])

draw_box(ax, 0.5 + offset_x, 1.0, 2.8, 1.0, 'Text\nDisplay', MORANDI_COLORS['light_blue'], 13)
draw_box(ax, 3.6 + offset_x, 1.0, 2.8, 1.0, 'TTS\nAudio', MORANDI_COLORS['light_blue'], 13)
draw_box(ax, 6.7 + offset_x, 1.0, 2.8, 1.0, 'Image\nAnnotation', MORANDI_COLORS['light_blue'], 13)

# 箭头：LLMs -> 输出
draw_arrow(ax, llm1_center, 3.2, 1.9 + offset_x, 2.0, MORANDI_COLORS['dusty_blue'], width=2.5)
draw_arrow(ax, llm1_center, 3.2, 5.0 + offset_x, 2.0, MORANDI_COLORS['dusty_blue'], width=2.5)
draw_arrow(ax, llm2_center, 3.2, 8.1 + offset_x, 2.0, MORANDI_COLORS['dusty_blue'], width=2.5)

# ============ Technology Stack (右侧面板 - 缩小但字更大) ============
# 背景框 - 缩小
tech_box = FancyBboxPatch((12.0, 2.5), 7.5, 10.5,
                         boxstyle="round,pad=0.2",
                         facecolor='white',
                         edgecolor=MORANDI_COLORS['light_purple'],
                         linewidth=3,
                         alpha=0.95)
ax.add_patch(tech_box)

ax.text(15.75, 12.3, 'Technology Stack', ha='center', va='top',
       fontsize=15, fontweight='600', color=MORANDI_COLORS['dark_text'])

# 分隔线
ax.plot([12.4, 19.1], [11.8, 11.8], color=MORANDI_COLORS['light_purple'], 
       linewidth=2, alpha=0.5)

tech_stack = [
    ('RAG Infrastructure', [
        ('Vector DB:', 'Milvus 2.3', MORANDI_COLORS['soft_coral']),
        ('Embeddings:', 'MiniLM-L12-v2', MORANDI_COLORS['soft_coral']),
        ('Reranking:', 'Cross-Encoder', MORANDI_COLORS['soft_coral']),
        ('Chunking:', 'Recursive Splitter', MORANDI_COLORS['soft_coral']),
    ]),
    ('AI Models', [
        ('LLM (Text):', 'HKGAI-V1', MORANDI_COLORS['muted_purple']),
        ('LLM (Vision):', 'Doubao Seed-1-6', MORANDI_COLORS['muted_purple']),
        ('STT:', 'Web Speech API', MORANDI_COLORS['muted_purple']),
        ('TTS:', 'Edge TTS', MORANDI_COLORS['muted_purple']),
    ]),
    ('External APIs', [
        ('Web Search:', 'Tavily AI', MORANDI_COLORS['sage_green']),
        ('Weather:', 'wttr.in', MORANDI_COLORS['sage_green']),
        ('Finance:', 'Yahoo Finance', MORANDI_COLORS['sage_green']),
    ]),
    ('Application', [
        ('Backend:', 'FastAPI + Uvicorn', MORANDI_COLORS['dusty_blue']),
        ('Frontend:', 'React + Vite + TS', MORANDI_COLORS['dusty_blue']),
        ('Styling:', 'Tailwind + Framer', MORANDI_COLORS['dusty_blue']),
    ])
]

y_pos = 11.3
for category, items in tech_stack:
    # 分类标题
    ax.text(12.4, y_pos, category, ha='left', va='center',
           fontsize=11, fontweight='700', color=MORANDI_COLORS['dark_text'])
    y_pos -= 0.45
    
    for label, value, color in items:
        # 彩色圆点
        circle = Circle((12.6, y_pos), 0.08, color=color, alpha=0.8, 
                       edgecolor='white', linewidth=2)
        ax.add_patch(circle)
        
        # 字体
        ax.text(12.85, y_pos, label, ha='left', va='center',
               fontsize=10, fontweight='600', color=MORANDI_COLORS['dark_text'])
        ax.text(15.5, y_pos, value, ha='left', va='center',
               fontsize=10, fontweight='400', color=MORANDI_COLORS['medium_text'])
        y_pos -= 0.4
    
    y_pos -= 0.25

# ============ Core Features (底部) ============
features_text = 'Core Features: 91.8% Accuracy • 0.77s Search Latency • Dual-Brain Architecture • Intelligent Tool Routing'
ax.text(10, 0.3, features_text,
       ha='center', va='center', fontsize=13, fontweight='400',
       color=MORANDI_COLORS['dark_text'],
       bbox=dict(boxstyle='round,pad=0.6', facecolor='white', 
                edgecolor=MORANDI_COLORS['sage_green'], alpha=0.95, linewidth=3))

plt.tight_layout()
plt.savefig('visualizations/system_architecture.png', dpi=300, bbox_inches='tight',
            facecolor=MORANDI_COLORS['background'], edgecolor='none', pad_inches=0.3)
print("✅ 已重新生成垂直流程布局的系统架构图: system_architecture.png")
plt.close()

