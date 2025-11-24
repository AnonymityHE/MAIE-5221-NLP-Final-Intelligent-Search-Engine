"""
生成Jude系统架构图
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

# 创建图形
fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis('off')

# 定义颜色
color_input = '#A855F7'  # Purple
color_process = '#3B82F6'  # Blue
color_tool = '#EC4899'  # Pink
color_llm = '#8B5CF6'  # Violet
color_output = '#06B6D4'  # Cyan

def draw_box(ax, x, y, width, height, text, color, fontsize=10, fontweight='normal'):
    """绘制圆角矩形框"""
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.1",
        edgecolor=color,
        facecolor=color,
        alpha=0.3,
        linewidth=2
    )
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, text,
            ha='center', va='center',
            fontsize=fontsize, fontweight=fontweight,
            color='#1F2937')

def draw_arrow(ax, x1, y1, x2, y2, color='#6B7280'):
    """绘制箭头"""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle='->,head_width=0.4,head_length=0.4',
        color=color,
        linewidth=2,
        alpha=0.7
    )
    ax.add_patch(arrow)

# 标题
ax.text(5, 11.5, 'Jude System Architecture', 
        ha='center', fontsize=20, fontweight='bold', color='#581C87')
ax.text(5, 11, 'Six-Stage Pipeline: Input → Processing → Tools → LLM → Output',
        ha='center', fontsize=12, color='#6B7280', style='italic')

# Stage 1: Input Ingestion (顶部)
y_input = 9.5
draw_box(ax, 0.5, y_input, 1.5, 0.8, 'Text\nInput', color_input, fontsize=9, fontweight='bold')
draw_box(ax, 2.5, y_input, 1.5, 0.8, 'Voice\n(STT)', color_input, fontsize=9, fontweight='bold')
draw_box(ax, 4.5, y_input, 1.5, 0.8, 'Image\nUpload', color_input, fontsize=9, fontweight='bold')
ax.text(5, y_input + 1.2, '❶ Input Ingestion', ha='center', fontsize=11, fontweight='bold', color=color_input)

# Stage 2: Preprocessing
y_preprocess = 8
draw_box(ax, 1.5, y_preprocess, 2, 0.8, 'STT / OCR / Normalization', color_process, fontsize=9)
ax.text(5, y_preprocess + 1.2, '❷ Preprocessing', ha='center', fontsize=11, fontweight='bold', color=color_process)

# Arrows: Input -> Preprocessing
draw_arrow(ax, 1.25, y_input, 2.5, y_preprocess + 0.8, color_input)
draw_arrow(ax, 3.25, y_input, 2.5, y_preprocess + 0.8, color_input)
draw_arrow(ax, 5.25, y_input, 2.5, y_preprocess + 0.8, color_input)

# Stage 3: Agent Router (Intent Detection)
y_agent = 6.5
draw_box(ax, 1, y_agent, 3, 1, 'Agent Router\n(LLM-Driven Intent Detection)', color_llm, fontsize=10, fontweight='bold')
ax.text(5, y_agent + 1.5, '❸ Agent Routing', ha='center', fontsize=11, fontweight='bold', color=color_llm)

# Arrow: Preprocessing -> Agent
draw_arrow(ax, 2.5, y_preprocess, 2.5, y_agent + 1, color_process)

# Stage 4: Tool Execution
y_tools = 4
draw_box(ax, 0.2, y_tools, 1.4, 0.7, 'Local\nRAG', color_tool, fontsize=8)
draw_box(ax, 1.8, y_tools, 1.4, 0.7, 'Web\nSearch', color_tool, fontsize=8)
draw_box(ax, 3.4, y_tools, 1.4, 0.7, 'Weather\nAPI', color_tool, fontsize=8)
draw_box(ax, 5.0, y_tools, 1.4, 0.7, 'Finance\nAPI', color_tool, fontsize=8)
draw_box(ax, 6.6, y_tools, 1.4, 0.7, 'Transport\nAPI', color_tool, fontsize=8)
ax.text(5, y_tools + 1.3, '❹ Tool Execution (Parallel)', ha='center', fontsize=11, fontweight='bold', color=color_tool)

# Arrows: Agent -> Tools
for x in [0.9, 2.5, 4.1, 5.7, 7.3]:
    draw_arrow(ax, 2.5, y_agent, x, y_tools + 0.7, color_llm)

# Stage 5: Answer Generation
y_llm = 2.2
draw_box(ax, 0.5, y_llm, 2, 0.8, 'HKGAI-V1\n(Chinese Text)', color_llm, fontsize=9)
draw_box(ax, 3, y_llm, 2, 0.8, 'Doubao Seed-1-6\n(Multimodal)', color_llm, fontsize=9)
ax.text(5, y_llm + 1.3, '❺ Answer Generation (Dual-Brain LLM)', ha='center', fontsize=11, fontweight='bold', color=color_llm)

# Arrows: Tools -> LLM
for x_tool in [0.9, 2.5, 4.1, 5.7, 7.3]:
    draw_arrow(ax, x_tool, y_tools, 1.5, y_llm + 0.8, color_tool)
    draw_arrow(ax, x_tool, y_tools, 4, y_llm + 0.8, color_tool)

# Stage 6: Output Rendering
y_output = 0.3
draw_box(ax, 0.5, y_output, 1.5, 0.7, 'Text\nDisplay', color_output, fontsize=9)
draw_box(ax, 2.5, y_output, 1.5, 0.7, 'TTS\nAudio', color_output, fontsize=9)
draw_box(ax, 4.5, y_output, 1.5, 0.7, 'Image\nAnnotation', color_output, fontsize=9)
ax.text(5, y_output - 0.5, '❻ Output Rendering', ha='center', fontsize=11, fontweight='bold', color=color_output)

# Arrows: LLM -> Output
draw_arrow(ax, 1.5, y_llm, 1.25, y_output + 0.7, color_llm)
draw_arrow(ax, 4, y_llm, 3.25, y_output + 0.7, color_llm)
draw_arrow(ax, 4, y_llm, 5.25, y_output + 0.7, color_llm)

# 右侧：技术栈说明
tech_x = 6.5
tech_y_start = 8.5

ax.text(tech_x + 1.5, tech_y_start + 0.5, 'Technology Stack', 
        ha='center', fontsize=12, fontweight='bold', color='#374151')

tech_stack = [
    ('Vector DB:', 'Milvus 2.3', color_tool),
    ('Embeddings:', 'MiniLM-L12-v2', color_tool),
    ('Reranking:', 'Cross-Encoder', color_tool),
    ('LLM (Text):', 'HKGAI-V1', color_llm),
    ('LLM (Vision):', 'Doubao', color_llm),
    ('STT:', 'Web Speech API', color_input),
    ('TTS:', 'Edge TTS', color_output),
    ('Backend:', 'FastAPI + Uvicorn', color_process),
    ('Frontend:', 'React + Vite', color_output),
]

y_pos = tech_y_start
for i, (label, value, color) in enumerate(tech_stack):
    # 小色块标识
    rect = mpatches.Rectangle((tech_x, y_pos - 0.15), 0.15, 0.15, 
                              facecolor=color, edgecolor=color, alpha=0.6)
    ax.add_patch(rect)
    # 文本
    ax.text(tech_x + 0.25, y_pos, f'{label}',
            ha='left', fontsize=8, fontweight='bold', color='#374151')
    ax.text(tech_x + 1.2, y_pos, value,
            ha='left', fontsize=8, color='#6B7280')
    y_pos -= 0.35

# 底部：核心特性
feature_y = -1.2
ax.text(5, feature_y, 'Core Features: 91.8% Accuracy • 0.77s Search Latency • Dual-Brain Architecture • Intelligent Tool Routing',
        ha='center', fontsize=10, color='#6B7280', style='italic',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#F3F4F6', edgecolor='#D1D5DB', linewidth=1))

plt.tight_layout()
plt.savefig('system_architecture.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✅ 系统架构图已生成: system_architecture.png")
plt.close()

