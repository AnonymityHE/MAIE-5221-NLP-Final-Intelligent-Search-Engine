#!/usr/bin/env python3
"""
生成Jude系统架构图 - 莫兰迪配色方案
更优雅的设计风格
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
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
    'light_gray': '#e8e8e8',
    'dark_text': '#5a5a5a',
    'medium_text': '#8a8a8a',
    'background': '#f7f6f3'
}

# 创建图表
fig, ax = plt.subplots(figsize=(18, 12))
fig.patch.set_facecolor(MORANDI_COLORS['background'])
ax.set_xlim(0, 18)
ax.set_ylim(0, 12)
ax.axis('off')

def draw_box(ax, x, y, width, height, text, color, text_size=11, bold=False):
    """绘制圆角矩形框"""
    box = FancyBboxPatch((x, y), width, height,
                         boxstyle="round,pad=0.1",
                         facecolor=color,
                         edgecolor='white',
                         linewidth=2.5,
                         alpha=0.9)
    ax.add_patch(box)
    
    weight = 'bold' if bold else '400'
    ax.text(x + width/2, y + height/2, text,
           ha='center', va='center',
           fontsize=text_size, fontweight=weight,
           color=MORANDI_COLORS['dark_text'])

def draw_arrow(ax, x1, y1, x2, y2, color, style='->'):
    """绘制箭头"""
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle=style,
                           color=color,
                           linewidth=2,
                           alpha=0.7,
                           mutation_scale=20)
    ax.add_patch(arrow)

def draw_stage_label(ax, x, y, text, number):
    """绘制阶段标签"""
    # 圆形编号
    circle = plt.Circle((x, y), 0.25, color=MORANDI_COLORS['muted_purple'], 
                       alpha=0.9, edgecolor='white', linewidth=2)
    ax.add_patch(circle)
    ax.text(x, y, number, ha='center', va='center',
           fontsize=12, fontweight='bold', color='white')
    
    # 阶段名称
    ax.text(x + 0.4, y, text, ha='left', va='center',
           fontsize=11, fontweight='600', color=MORANDI_COLORS['dark_text'])

# ============ 标题 ============
ax.text(9, 11.3, 'Jude System Architecture', 
       ha='center', va='center', fontsize=20, fontweight='300',
       color=MORANDI_COLORS['dark_text'])
ax.text(9, 10.8, 'Six-Stage Pipeline: Input → Processing → Tools → LLM → Output',
       ha='center', va='center', fontsize=12, fontweight='400',
       color=MORANDI_COLORS['medium_text'], style='italic')

# ============ Stage 1: Input Ingestion ============
draw_stage_label(ax, 0.8, 9.5, 'Input Ingestion', '1')

# 三个输入框
draw_box(ax, 0.5, 8.2, 1.8, 0.8, 'Text\nInput', MORANDI_COLORS['light_purple'], 10)
draw_box(ax, 2.5, 8.2, 1.8, 0.8, 'Voice\n(STT)', MORANDI_COLORS['light_purple'], 10)
draw_box(ax, 4.5, 8.2, 1.8, 0.8, 'Image\nUpload', MORANDI_COLORS['light_purple'], 10)

# ============ Stage 2: Preprocessing ============
draw_stage_label(ax, 0.8, 7.2, 'Preprocessing', '2')

# 预处理框
draw_box(ax, 1.5, 6.3, 3.5, 0.7, 'STT / OCR / Normalization', 
        MORANDI_COLORS['light_blue'], 11)

# 箭头：输入 -> 预处理
for x in [1.4, 3.4, 5.4]:
    draw_arrow(ax, x, 8.2, 3.25, 7.0, MORANDI_COLORS['muted_purple'])

# ============ Stage 3: Agent Routing ============
draw_stage_label(ax, 0.8, 5.5, 'Agent Routing', '3')

# Agent Router框
draw_box(ax, 1.0, 4.3, 4.5, 0.9, 'Agent Router\n(LLM-Driven Intent Detection)',
        MORANDI_COLORS['light_purple'], 11, bold=True)

# 箭头：预处理 -> Agent
draw_arrow(ax, 3.25, 6.3, 3.25, 5.2, MORANDI_COLORS['dusty_blue'])

# ============ Stage 4: Tool Execution ============
draw_stage_label(ax, 0.8, 3.5, 'Tool Execution (Parallel)', '4')

# 五个工具框
tools = [
    ('Local\nRAG', 0.5, 2.0),
    ('Web\nSearch', 2.0, 2.0),
    ('Weather\nAPI', 3.5, 2.0),
    ('Finance\nAPI', 5.0, 2.0),
    ('Transport\nAPI', 6.5, 2.0)
]

for tool, x, y in tools:
    draw_box(ax, x, y, 1.3, 0.8, tool, MORANDI_COLORS['light_coral'], 10)
    # 箭头：Agent -> Tools
    draw_arrow(ax, 3.25, 4.3, x + 0.65, 2.8, MORANDI_COLORS['soft_coral'])

# ============ Stage 5: Answer Generation ============
draw_stage_label(ax, 0.8, 1.2, 'Answer Generation (Dual-Brain LLM)', '5')

# 两个LLM框
draw_box(ax, 1.0, 0.2, 2.5, 0.7, 'HKGAI-V1\n(Chinese Text)',
        MORANDI_COLORS['light_purple'], 10)
draw_box(ax, 4.0, 0.2, 2.5, 0.7, 'Doubao Seed-1-6\n(Multimodal)',
        MORANDI_COLORS['light_purple'], 10)

# 箭头：Tools -> LLMs
for tool, x, y in tools:
    draw_arrow(ax, x + 0.65, 2.0, 2.25, 0.9, MORANDI_COLORS['sage_green'])
    draw_arrow(ax, x + 0.65, 2.0, 5.25, 0.9, MORANDI_COLORS['sage_green'])

# ============ Stage 6: Output Rendering ============
draw_stage_label(ax, 9.5, 9.5, 'Output Rendering', '6')

# 三个输出框
draw_box(ax, 9.2, 8.2, 1.8, 0.8, 'Text\nDisplay', MORANDI_COLORS['light_blue'], 10)
draw_box(ax, 11.2, 8.2, 1.8, 0.8, 'TTS\nAudio', MORANDI_COLORS['light_blue'], 10)
draw_box(ax, 13.2, 8.2, 1.8, 0.8, 'Image\nAnnotation', MORANDI_COLORS['light_blue'], 10)

# 箭头：LLMs -> 输出
draw_arrow(ax, 2.25, 0.2, 10.1, 8.2, MORANDI_COLORS['dusty_blue'], style='->')
draw_arrow(ax, 5.25, 0.2, 12.1, 8.2, MORANDI_COLORS['dusty_blue'], style='->')

# ============ Technology Stack (右侧) ============
ax.text(13.5, 7.2, 'Technology Stack', ha='left', va='top',
       fontsize=13, fontweight='600', color=MORANDI_COLORS['dark_text'])

tech_stack = [
    ('Vector DB:', 'Milvus 2.3', MORANDI_COLORS['soft_coral']),
    ('Embeddings:', 'MiniLM-L12-v2', MORANDI_COLORS['soft_coral']),
    ('Reranking:', 'Cross-Encoder', MORANDI_COLORS['soft_coral']),
    ('LLM (Text):', 'HKGAI-V1', MORANDI_COLORS['muted_purple']),
    ('LLM (Vision):', 'Doubao', MORANDI_COLORS['muted_purple']),
    ('STT:', 'Web Speech API', MORANDI_COLORS['muted_purple']),
    ('TTS:', 'Edge TTS', MORANDI_COLORS['muted_purple']),
    ('Backend:', 'FastAPI + Uvicorn', MORANDI_COLORS['dusty_blue']),
    ('Frontend:', 'React + Vite', MORANDI_COLORS['dusty_blue'])
]

y_pos = 6.8
for label, value, color in tech_stack:
    # 彩色标签
    box = FancyBboxPatch((13.3, y_pos - 0.15), 0.3, 0.25,
                         boxstyle="round,pad=0.02",
                         facecolor=color,
                         edgecolor='white',
                         linewidth=1.5,
                         alpha=0.8)
    ax.add_patch(box)
    
    ax.text(13.7, y_pos, label, ha='left', va='center',
           fontsize=9, fontweight='600', color=MORANDI_COLORS['dark_text'])
    ax.text(15.5, y_pos, value, ha='left', va='center',
           fontsize=9, fontweight='400', color=MORANDI_COLORS['medium_text'])
    y_pos -= 0.35

# ============ Core Features (底部) ============
ax.text(9, -0.3, 'Core Features: 91.8% Accuracy • 0.77s Search Latency • Dual-Brain Architecture • Intelligent Tool Routing',
       ha='center', va='center', fontsize=11, fontweight='400',
       color=MORANDI_COLORS['medium_text'],
       bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                edgecolor=MORANDI_COLORS['light_gray'], alpha=0.9, linewidth=2))

# ============ 流程线 (整体流程) ============
# 从输入到输出的主流程线
flow_y = 10.3
ax.plot([1.4, 3.25], [flow_y, flow_y], color=MORANDI_COLORS['muted_purple'], 
       linewidth=3, alpha=0.3, linestyle='-')
ax.plot([3.25, 3.25], [flow_y, 5.2], color=MORANDI_COLORS['muted_purple'], 
       linewidth=3, alpha=0.3, linestyle='-')
ax.plot([3.25, 4.0], [2.4, 2.4], color=MORANDI_COLORS['soft_coral'], 
       linewidth=3, alpha=0.3, linestyle='-')
ax.plot([3.25, 0.9], [0.55, 0.55], color=MORANDI_COLORS['sage_green'], 
       linewidth=3, alpha=0.3, linestyle='-')

plt.tight_layout()
plt.savefig('visualizations/system_architecture.png', dpi=300, bbox_inches='tight',
            facecolor=MORANDI_COLORS['background'], edgecolor='none', pad_inches=0.3)
print("✅ 已重新生成系统架构图: system_architecture.png")
plt.close()

