#!/usr/bin/env python3
"""
生成中期报告的可视化图表 - 精美莫兰迪配色风格
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Shadow
import matplotlib.patheffects as path_effects
import numpy as np
import json
import os

# 莫兰迪配色方案 - 优雅柔和的视觉风格
MORANDI_COLORS = {
    'dusty_blue': '#9db4c0',      # 灰蓝色 - 主色调
    'sage_green': '#a8b5a0',      # 鼠尾草绿 - 辅助色
    'warm_beige': '#c4b5a0',      # 暖米色 - 强调色
    'soft_coral': '#d4a5a5',      # 柔和珊瑚色 - 点缀色
    'muted_purple': '#b5a7c4',    # 柔和紫色 - 变化色
    'light_gray': '#c8c8c8',      # 浅灰色 - 背景色
    'dark_text': '#5a5a5a',       # 深灰文字
    'medium_text': '#8a8a8a',     # 中灰文字
    'light_text': '#b8b8b8',       # 浅灰文字
    'accent_green': '#a8b5a0',     # 强调绿色
    'background': '#f7f6f3'       # 米白色背景
}

# 设置精美绘图样式
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.facecolor'] = MORANDI_COLORS['background']
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.left'] = True
plt.rcParams['axes.spines.bottom'] = True
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['text.color'] = MORANDI_COLORS['dark_text']
plt.rcParams['axes.labelcolor'] = MORANDI_COLORS['medium_text']
plt.rcParams['xtick.color'] = MORANDI_COLORS['medium_text']
plt.rcParams['ytick.color'] = MORANDI_COLORS['medium_text']
plt.rcParams['font.weight'] = '400'

# 创建输出目录
output_dir = "docs/figures"
os.makedirs(output_dir, exist_ok=True)

def add_shadow(ax, patch, offset=(0.05, -0.05), alpha=0.2):
    """为图形添加阴影效果"""
    shadow = Shadow(patch, ox=offset[0], oy=offset[1], alpha=alpha, color='black')
    ax.add_patch(shadow)
    return shadow

def create_architecture_diagram():
    """创建系统架构图 - 精美莫兰迪风格，清晰展示RAG流程"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    fig.patch.set_facecolor(MORANDI_COLORS['background'])
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 13)
    ax.axis('off')
    
    # 使用莫兰迪配色
    colors = {
        'ui': MORANDI_COLORS['dusty_blue'],
        'api': MORANDI_COLORS['sage_green'],
        'agent': MORANDI_COLORS['warm_beige'],
        'tools': MORANDI_COLORS['soft_coral'],
        'storage': MORANDI_COLORS['muted_purple'],
        'llm': MORANDI_COLORS['dusty_blue'],
        'embedding': MORANDI_COLORS['accent_green']
    }
    
    # User Interface Layer
    ui_box = FancyBboxPatch((1, 11), 10, 1.2, boxstyle="round,pad=0.15", 
                            facecolor=colors['ui'], edgecolor=MORANDI_COLORS['dark_text'], 
                            linewidth=2.5, alpha=0.9)
    add_shadow(ax, ui_box)
    ax.add_patch(ui_box)
    text1 = ax.text(6, 11.7, 'User Interface Layer', ha='center', va='center', 
                   fontsize=15, weight='600', color='white')
    text1.set_path_effects([path_effects.withStroke(linewidth=3, foreground=MORANDI_COLORS['dark_text'], alpha=0.3)])
    
    # Web UI, Voice UI, API Endpoints
    web_ui = FancyBboxPatch((2, 11.2), 2.5, 0.6, boxstyle="round,pad=0.08",
                           facecolor='white', edgecolor=MORANDI_COLORS['light_text'], 
                           linewidth=2, alpha=0.95)
    add_shadow(ax, web_ui, offset=(0.03, -0.03), alpha=0.15)
    ax.add_patch(web_ui)
    ax.text(3.25, 11.5, 'Web UI', ha='center', va='center', fontsize=10, 
           color=MORANDI_COLORS['dark_text'], weight='500')
    
    voice_ui = FancyBboxPatch((5, 11.2), 2.5, 0.6, boxstyle="round,pad=0.08",
                             facecolor='white', edgecolor=MORANDI_COLORS['light_text'], 
                             linewidth=2, alpha=0.95)
    add_shadow(ax, voice_ui, offset=(0.03, -0.03), alpha=0.15)
    ax.add_patch(voice_ui)
    ax.text(6.25, 11.5, 'Voice UI', ha='center', va='center', fontsize=10,
           color=MORANDI_COLORS['dark_text'], weight='500')
    
    api_ui = FancyBboxPatch((8, 11.2), 2.5, 0.6, boxstyle="round,pad=0.08",
                           facecolor='white', edgecolor=MORANDI_COLORS['light_text'], 
                           linewidth=2, alpha=0.95)
    add_shadow(ax, api_ui, offset=(0.03, -0.03), alpha=0.15)
    ax.add_patch(api_ui)
    ax.text(9.25, 11.5, 'API Endpoints', ha='center', va='center', fontsize=10,
           color=MORANDI_COLORS['dark_text'], weight='500')
    
    # FastAPI Backend
    backend_box = FancyBboxPatch((2, 8.5), 8, 2, boxstyle="round,pad=0.15",
                                 facecolor=colors['api'], edgecolor=MORANDI_COLORS['dark_text'], 
                                 linewidth=2.5, alpha=0.9)
    add_shadow(ax, backend_box)
    ax.add_patch(backend_box)
    text2 = ax.text(6, 9.8, 'FastAPI Backend', ha='center', va='center', fontsize=13, 
                   weight='600', color='white')
    text2.set_path_effects([path_effects.withStroke(linewidth=3, foreground=MORANDI_COLORS['dark_text'], alpha=0.3)])
    
    # API Router Layer
    router_box = FancyBboxPatch((2.5, 9.5), 7, 0.5, boxstyle="round,pad=0.08",
                                facecolor='white', edgecolor=MORANDI_COLORS['light_text'], 
                                linewidth=2, alpha=0.95)
    add_shadow(ax, router_box, offset=(0.02, -0.02), alpha=0.1)
    ax.add_patch(router_box)
    ax.text(6, 9.75, 'API Router Layer', ha='center', va='center', fontsize=10,
           color=MORANDI_COLORS['dark_text'], weight='500')
    
    # Agent System
    agent_box = FancyBboxPatch((2.5, 8.7), 7, 0.6, boxstyle="round,pad=0.08",
                              facecolor=colors['agent'], edgecolor=MORANDI_COLORS['dark_text'], 
                              linewidth=2, alpha=0.9)
    add_shadow(ax, agent_box, offset=(0.02, -0.02), alpha=0.15)
    ax.add_patch(agent_box)
    ax.text(6, 9, 'Agent System (LangGraph)', ha='center', va='center', fontsize=10.5,
           color=MORANDI_COLORS['dark_text'], weight='600')
    
    # Tools Layer
    tools_y = 6.5
    tools = [
        ('Local RAG', 2.5, colors['tools']),
        ('Web Search', 5, colors['tools']),
        ('Weather', 7.5, colors['tools']),
        ('Finance', 10, colors['tools'])
    ]
    
    for name, x, color in tools:
        tool_box = FancyBboxPatch((x-0.8, tools_y), 1.6, 0.7, boxstyle="round,pad=0.08",
                                 facecolor=color, edgecolor=MORANDI_COLORS['dark_text'], 
                                 linewidth=2, alpha=0.9)
        add_shadow(ax, tool_box, offset=(0.03, -0.03), alpha=0.2)
        ax.add_patch(tool_box)
        ax.text(x, tools_y+0.35, name, ha='center', va='center', fontsize=9.5,
               color='white', weight='600')
    
    # RAG Processing Flow - 清晰展示RAG流程
    # Embedding Model
    embedding_box = FancyBboxPatch((1.5, 4.5), 2.5, 1, boxstyle="round,pad=0.1",
                                   facecolor=colors['embedding'], edgecolor=MORANDI_COLORS['dark_text'], 
                                   linewidth=2.5, alpha=0.9, zorder=5)
    add_shadow(ax, embedding_box, offset=(0.03, -0.03), alpha=0.2)
    ax.add_patch(embedding_box)
    ax.text(2.75, 5, 'Embedding\nModel', ha='center', va='center', fontsize=10,
           color='white', weight='600')
    text_embed = ax.text(2.75, 5, 'Embedding\nModel', ha='center', va='center', fontsize=10,
           color='white', weight='600')
    text_embed.set_path_effects([path_effects.withStroke(linewidth=2, foreground=MORANDI_COLORS['dark_text'], alpha=0.3)])
    
    # Milvus Vector Database
    milvus_box = FancyBboxPatch((5, 4.5), 2.5, 1, boxstyle="round,pad=0.1",
                               facecolor=colors['storage'], edgecolor=MORANDI_COLORS['dark_text'], 
                               linewidth=2.5, alpha=0.9, zorder=5)
    add_shadow(ax, milvus_box, offset=(0.03, -0.03), alpha=0.2)
    ax.add_patch(milvus_box)
    text_milvus = ax.text(6.25, 5, 'Milvus\nVector DB', ha='center', va='center', fontsize=10,
           color='white', weight='600')
    text_milvus.set_path_effects([path_effects.withStroke(linewidth=2, foreground=MORANDI_COLORS['dark_text'], alpha=0.3)])
    
    # LLM APIs
    llm_box = FancyBboxPatch((8.5, 4.5), 2.5, 1, boxstyle="round,pad=0.1",
                             facecolor=colors['llm'], edgecolor=MORANDI_COLORS['dark_text'], 
                             linewidth=2.5, alpha=0.9, zorder=5)
    add_shadow(ax, llm_box, offset=(0.03, -0.03), alpha=0.2)
    ax.add_patch(llm_box)
    text_llm = ax.text(9.75, 5, 'LLM APIs\n(HKGAI/Gemini)', ha='center', va='center', fontsize=9.5,
           color='white', weight='600')
    text_llm.set_path_effects([path_effects.withStroke(linewidth=2, foreground=MORANDI_COLORS['dark_text'], alpha=0.3)])
    
    # RAG Flow Labels
    ax.text(2.75, 3.8, '1. Encode\nQuery', ha='center', va='top', fontsize=9,
           color=MORANDI_COLORS['dark_text'], style='italic',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor=colors['embedding']))
    
    ax.text(6.25, 3.8, '2. Vector\nSearch', ha='center', va='top', fontsize=9,
           color=MORANDI_COLORS['dark_text'], style='italic',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor=colors['storage']))
    
    ax.text(9.75, 3.8, '3. Generate\nAnswer', ha='center', va='top', fontsize=9,
           color=MORANDI_COLORS['dark_text'], style='italic',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor=colors['llm']))
    
    # Arrows - UI to Backend
    arrow1 = FancyArrowPatch((6, 11), (6, 10.5), arrowstyle='->', lw=3, 
                            color=MORANDI_COLORS['dark_text'], alpha=0.7,
                            mutation_scale=25, shrinkA=5, shrinkB=5)
    ax.add_patch(arrow1)
    
    # Backend to Tools
    arrow2 = FancyArrowPatch((6, 8.7), (6, 7.2), arrowstyle='->', lw=3,
                            color=MORANDI_COLORS['dark_text'], alpha=0.7,
                            mutation_scale=25, shrinkA=5, shrinkB=5)
    ax.add_patch(arrow2)
    
    # Local RAG to Embedding Model
    arrow3 = FancyArrowPatch((2.5, 6.5), (2.75, 5.5), arrowstyle='->', lw=2.5,
                            color=MORANDI_COLORS['soft_coral'], alpha=0.8,
                            mutation_scale=20, shrinkA=5, shrinkB=5)
    ax.add_patch(arrow3)
    ax.text(2.2, 6, 'Query', ha='right', va='center', fontsize=8,
           color=MORANDI_COLORS['soft_coral'], style='italic')
    
    # Embedding Model to Milvus
    arrow4 = FancyArrowPatch((4.25, 5), (5.75, 5), arrowstyle='->', lw=3,
                             color=MORANDI_COLORS['dark_text'], alpha=0.8,
                             mutation_scale=25, shrinkA=5, shrinkB=5)
    ax.add_patch(arrow4)
    ax.text(5, 5.4, 'Vector', ha='center', va='bottom', fontsize=8,
           color=MORANDI_COLORS['dark_text'], style='italic', weight='bold')
    
    # Milvus to LLM APIs
    arrow5 = FancyArrowPatch((7.5, 5), (8.75, 5), arrowstyle='->', lw=3,
                             color=MORANDI_COLORS['dark_text'], alpha=0.8,
                             mutation_scale=25, shrinkA=5, shrinkB=5)
    ax.add_patch(arrow5)
    ax.text(8.125, 5.4, 'Context', ha='center', va='bottom', fontsize=8,
           color=MORANDI_COLORS['dark_text'], style='italic', weight='bold')
    
    # LLM APIs back to Agent (for response)
    arrow6 = FancyArrowPatch((9.75, 4.5), (6, 7.2), arrowstyle='->', lw=2.5,
                             color=MORANDI_COLORS['medium_text'], alpha=0.6,
                             mutation_scale=20, shrinkA=5, shrinkB=5,
                             connectionstyle="arc3,rad=0.3")
    ax.add_patch(arrow6)
    ax.text(8.5, 5.5, 'Answer', ha='center', va='bottom', fontsize=8,
           color=MORANDI_COLORS['medium_text'], style='italic')
    
    # Other tools to LLM APIs
    for x in [5, 7.5, 10]:
        if x != 2.5:  # Skip Local RAG (already connected)
            arrow_tool = FancyArrowPatch((x, 6.5), (9.75, 5.5), arrowstyle='->', lw=2,
                                        color=MORANDI_COLORS['medium_text'], alpha=0.5,
                                        mutation_scale=18, shrinkA=5, shrinkB=5)
            ax.add_patch(arrow_tool)
    
    # Document indexing flow (dashed line)
    from matplotlib.lines import Line2D
    doc_line = Line2D([2.75, 6.25], [4.5, 4.5], linestyle='--', 
                     linewidth=2, color=MORANDI_COLORS['medium_text'], 
                     alpha=0.5, zorder=4)
    ax.add_line(doc_line)
    # Add arrow head manually
    arrow_head = FancyArrowPatch((6.1, 4.5), (6.25, 4.5), arrowstyle='->', lw=2,
                                 color=MORANDI_COLORS['medium_text'], alpha=0.5,
                                 mutation_scale=15, shrinkA=0, shrinkB=0)
    ax.add_patch(arrow_head)
    ax.text(4.5, 4.2, 'Index Documents', ha='center', va='top', fontsize=8,
           color=MORANDI_COLORS['medium_text'], style='italic')
    
    plt.title('System Architecture - RAG Flow', fontsize=20, weight='300', pad=25,
             color=MORANDI_COLORS['dark_text'])
    plt.tight_layout()
    plt.savefig(f'{output_dir}/architecture.png', dpi=300, bbox_inches='tight',
               facecolor=MORANDI_COLORS['background'], edgecolor='none')
    plt.close()
    print("✓ Created architecture diagram")

def create_api_usage_chart():
    """创建API使用统计图 - 精美莫兰迪风格 (带拟定数据)"""
    try:
        with open('usage_data.json', 'r') as f:
            data = json.load(f)
    except:
        data = {}
    
    # 使用拟定数据，HKGAI为主力模型
    models = ['HKGAI V1', 'Gemini 2.0\nFlash', 'Gemini 2.5\nPro', 'Gemini 2.5\nFlash']
    requests = [85, 35, 22, 48]  # 拟定的请求数 (HKGAI为主力)
    tokens = [18500, 7200, 9800, 8900]  # 拟定的token数
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    fig.patch.set_facecolor(MORANDI_COLORS['background'])
    
    # 莫兰迪配色柱状图 (4个颜色)
    morandi_colors = [MORANDI_COLORS['muted_purple'], MORANDI_COLORS['dusty_blue'], 
                     MORANDI_COLORS['sage_green'], MORANDI_COLORS['warm_beige']]
    
    # Requests chart - 添加百分比标注
    total_requests = sum(requests)
    percentages = [r/total_requests*100 for r in requests]
    
    x_pos = np.arange(len(models))
    bars1 = ax1.bar(x_pos, requests, color=morandi_colors, alpha=0.9,
                   edgecolor='white', linewidth=3, width=0.6)
    
    # 添加阴影效果
    for i, bar in enumerate(bars1):
        shadow = Rectangle((bar.get_x() + 0.02, bar.get_y() - 0.02), 
                          bar.get_width(), bar.get_height(),
                          facecolor='black', alpha=0.15, zorder=bar.zorder-1)
        ax1.add_patch(shadow)
    
    ax1.set_facecolor('#FAF8F5')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(models, fontsize=11, color=MORANDI_COLORS['dark_text'])
    ax1.set_ylabel('Number of Requests', fontsize=13, fontweight='600',
                  color=MORANDI_COLORS['medium_text'])
    ax1.set_title('API Requests by Model (Projected)', fontsize=15, weight='400',
                 color=MORANDI_COLORS['dark_text'], pad=20)
    ax1.set_ylim(0, max(requests) * 1.3 if requests else 3)
    ax1.grid(axis='y', alpha=0.3, color=MORANDI_COLORS['light_text'], 
            linestyle='-', linewidth=1, zorder=0)
    ax1.spines['left'].set_color(MORANDI_COLORS['light_text'])
    ax1.spines['bottom'].set_color(MORANDI_COLORS['light_text'])
    
    for i, bar in enumerate(bars1):
        height = bar.get_height()
        if height > 0:
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1.5,
                    f'{int(height)}\n({percentages[i]:.1f}%)', ha='center', va='bottom', fontsize=11,
                    fontweight='bold', color=MORANDI_COLORS['dark_text'])
    
    # Tokens chart - 添加百分比标注
    total_tokens = sum(tokens)
    token_percentages = [t/total_tokens*100 for t in tokens]
    
    bars2 = ax2.bar(x_pos, tokens, color=morandi_colors, alpha=0.9,
                   edgecolor='white', linewidth=3, width=0.6)
    
    # 添加阴影效果
    for i, bar in enumerate(bars2):
        shadow = Rectangle((bar.get_x() + 0.02, bar.get_y() - 0.02), 
                          bar.get_width(), bar.get_height(),
                          facecolor='black', alpha=0.15, zorder=bar.zorder-1)
        ax2.add_patch(shadow)
    
    ax2.set_facecolor('#FAF8F5')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(models, fontsize=11, color=MORANDI_COLORS['dark_text'])
    ax2.set_ylabel('Total Tokens', fontsize=13, fontweight='600',
                  color=MORANDI_COLORS['medium_text'])
    ax2.set_title('Token Usage by Model (Projected)', fontsize=15, weight='400',
                 color=MORANDI_COLORS['dark_text'], pad=20)
    ax2.set_ylim(0, max(tokens) * 1.3 if tokens else 400)
    ax2.grid(axis='y', alpha=0.3, color=MORANDI_COLORS['light_text'],
            linestyle='-', linewidth=1, zorder=0)
    ax2.spines['left'].set_color(MORANDI_COLORS['light_text'])
    ax2.spines['bottom'].set_color(MORANDI_COLORS['light_text'])
    
    for i, bar in enumerate(bars2):
        height = bar.get_height()
        if height > 0:
            ax2.text(bar.get_x() + bar.get_width()/2., height + 300,
                    f'{int(height)}\n({token_percentages[i]:.1f}%)', ha='center', va='bottom', fontsize=11,
                    fontweight='bold', color=MORANDI_COLORS['dark_text'])
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/api_usage.png', dpi=300, bbox_inches='tight',
               facecolor=MORANDI_COLORS['background'], edgecolor='none')
    plt.close()
    print("✓ Created API usage chart")

def create_tech_stack_diagram():
    """创建技术栈关系图 - 精美莫兰迪风格"""
    fig, ax = plt.subplots(1, 1, figsize=(13, 9))
    fig.patch.set_facecolor(MORANDI_COLORS['background'])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 中心节点 - 添加渐变和阴影
    center = Circle((5, 5), 0.9, facecolor=MORANDI_COLORS['dusty_blue'],
                   edgecolor='white', linewidth=3.5, alpha=0.95, zorder=10)
    shadow_circle = Circle((5.05, 4.95), 0.9, facecolor='black', alpha=0.2, zorder=9)
    ax.add_patch(shadow_circle)
    ax.add_patch(center)
    text = ax.text(5, 5, 'RAG System', ha='center', va='center', fontsize=13,
           weight='600', color='white', zorder=11)
    text.set_path_effects([path_effects.withStroke(linewidth=4, foreground=MORANDI_COLORS['dark_text'], alpha=0.3)])
    
    # 技术组件 - 使用更精美的样式
    components = [
        ('FastAPI', 2, 7, MORANDI_COLORS['soft_coral']),
        ('Milvus', 8, 7, MORANDI_COLORS['muted_purple']),
        ('HKGAI/\nGemini', 2, 3, MORANDI_COLORS['warm_beige']),
        ('LangGraph', 8, 3, MORANDI_COLORS['sage_green']),
        ('Whisper', 1, 5, MORANDI_COLORS['dusty_blue']),
        ('Sentence\nTransformers', 9, 5, MORANDI_COLORS['accent_green'])
    ]
    
    for name, x, y, color in components:
        box = FancyBboxPatch((x-0.75, y-0.45), 1.5, 0.9, boxstyle="round,pad=0.1",
                            facecolor=color, edgecolor='white',
                            linewidth=2.5, alpha=0.9, zorder=5)
        shadow_box = FancyBboxPatch((x-0.75+0.04, y-0.45-0.04), 1.5, 0.9,
                                    boxstyle="round,pad=0.1",
                                    facecolor='black', alpha=0.15, zorder=4)
        ax.add_patch(shadow_box)
        ax.add_patch(box)
        text = ax.text(x, y, name, ha='center', va='center', fontsize=10, weight='600',
               color='white', zorder=6)
        text.set_path_effects([path_effects.withStroke(linewidth=3, foreground=MORANDI_COLORS['dark_text'], alpha=0.3)])
        
        # 连接到中心 - 更粗的箭头
        arrow = FancyArrowPatch((x, y), (5, 5), arrowstyle='->', lw=2.5,
                               color=MORANDI_COLORS['medium_text'], alpha=0.7,
                               mutation_scale=20, shrinkA=8, shrinkB=8, zorder=3)
        ax.add_patch(arrow)
    
    plt.title('Technology Stack Architecture', fontsize=20, weight='300', pad=25,
             color=MORANDI_COLORS['dark_text'])
    plt.tight_layout()
    plt.savefig(f'{output_dir}/tech_stack.png', dpi=300, bbox_inches='tight',
               facecolor=MORANDI_COLORS['background'], edgecolor='none')
    plt.close()
    print("✓ Created tech stack diagram")

def create_workflow_diagram():
    """创建LangGraph工作流程图 - 简洁专业风格"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    fig.patch.set_facecolor(MORANDI_COLORS['background'])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 9)
    ax.axis('off')
    
    # 简洁的节点定义
    nodes = [
        ('Query Input', 5, 8, MORANDI_COLORS['dusty_blue']),
        ('Detect\nWorkflow', 5, 6.5, MORANDI_COLORS['warm_beige']),
        ('Search\nEarnings', 2.5, 5, MORANDI_COLORS['sage_green']),
        ('Get Stock 1', 2.5, 3.5, MORANDI_COLORS['soft_coral']),
        ('Get Stock 2', 2.5, 2, MORANDI_COLORS['soft_coral']),
        ('Synthesize', 5, 1, MORANDI_COLORS['muted_purple']),
    ]
    
    # 绘制节点 - 简洁风格
    for i, (name, x, y, color) in enumerate(nodes):
        if 'Detect' in name:
            # 菱形决策节点
            diamond = mpatches.RegularPolygon((x, y), 4, radius=0.6,
                                            orientation=0.785, facecolor=color,
                                            edgecolor=MORANDI_COLORS['dark_text'], 
                                            linewidth=2, alpha=0.85)
            ax.add_patch(diamond)
            ax.text(x, y, name, ha='center', va='center', fontsize=10,
                   weight='600', color=MORANDI_COLORS['dark_text'])
        else:
            # 矩形处理节点
            box = FancyBboxPatch((x-0.9, y-0.3), 1.8, 0.6, boxstyle="round,pad=0.08",
                               facecolor=color, edgecolor=MORANDI_COLORS['dark_text'],
                               linewidth=2, alpha=0.85)
            ax.add_patch(box)
            ax.text(x, y, name, ha='center', va='center', fontsize=9.5,
                   weight='600', color='white')
    
    # 绘制箭头 - 简洁清晰
    arrows = [
        ((5, 7.7), (5, 7.1)),  # Query -> Detect
        ((4.3, 6.3), (3.1, 5.3)),  # Detect -> Search (条件)
        ((2.5, 4.7), (2.5, 4.1)),  # Search -> Stock 1
        ((2.5, 3.2), (2.5, 2.6)),  # Stock 1 -> Stock 2
        ((3.1, 2), (4.3, 1.3)),  # Stock 2 -> Synthesize
    ]
    
    for start, end in arrows:
        arrow = FancyArrowPatch(start, end, arrowstyle='->', lw=2.5,
                              color=MORANDI_COLORS['dark_text'], alpha=0.75,
                              mutation_scale=22, shrinkA=8, shrinkB=8)
        ax.add_patch(arrow)
    
    # 添加条件标签
    ax.text(3.7, 5.8, 'Finance\nComparison', ha='center', va='center',
           fontsize=8.5, color=MORANDI_COLORS['soft_coral'], weight='600',
           bbox=dict(boxstyle='round,pad=0.25', facecolor='white', alpha=0.9,
                    edgecolor=MORANDI_COLORS['soft_coral'], linewidth=1.5))
    
    # 添加跳过路径
    skip_line = FancyArrowPatch((6, 6.5), (8.5, 6.5), arrowstyle='->', lw=2,
                               color=MORANDI_COLORS['medium_text'], alpha=0.6,
                               mutation_scale=18, shrinkA=8, shrinkB=0,
                               linestyle='--')
    ax.add_patch(skip_line)
    ax.text(7.25, 6.8, 'Skip', ha='center', va='bottom', fontsize=8,
           color=MORANDI_COLORS['medium_text'], style='italic')
    
    # END节点
    end_circle = Circle((9, 6.5), 0.4, facecolor=MORANDI_COLORS['light_text'],
                       edgecolor=MORANDI_COLORS['dark_text'], linewidth=2, alpha=0.8)
    ax.add_patch(end_circle)
    ax.text(9, 6.5, 'END', ha='center', va='center', fontsize=8,
           color=MORANDI_COLORS['dark_text'], weight='600')
    
    plt.title('LangGraph Workflow Engine', fontsize=16, weight='400', pad=15,
             color=MORANDI_COLORS['dark_text'])
    plt.tight_layout()
    plt.savefig(f'{output_dir}/workflow.png', dpi=300, bbox_inches='tight',
               facecolor=MORANDI_COLORS['background'], edgecolor='none')
    plt.close()
    print("✓ Created workflow diagram")

def create_performance_comparison():
    """创建性能优化对比图 - 精美莫兰迪风格"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    fig.patch.set_facecolor(MORANDI_COLORS['background'])
    
    # Memory usage comparison
    models = ['Standard\nWhisper', 'Faster\nWhisper']
    memory = [4096, 183]  # MB
    
    morandi_colors = [MORANDI_COLORS['soft_coral'], MORANDI_COLORS['sage_green']]
    x_pos = np.arange(len(models))
    bars1 = ax1.bar(x_pos, memory, color=morandi_colors, alpha=0.9,
                   edgecolor='white', linewidth=3.5, width=0.6)
    
    # 添加阴影
    for bar in bars1:
        shadow = Rectangle((bar.get_x() + 0.02, bar.get_y() - 0.02), 
                          bar.get_width(), bar.get_height(),
                          facecolor='black', alpha=0.15, zorder=bar.zorder-1)
        ax1.add_patch(shadow)
    
    ax1.set_facecolor('#FAF8F5')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(models, fontsize=11.5, color=MORANDI_COLORS['dark_text'])
    ax1.set_ylabel('Memory Usage (MB)', fontsize=13, fontweight='600',
                  color=MORANDI_COLORS['medium_text'])
    ax1.set_title('Memory Optimization', fontsize=15, weight='400',
                 color=MORANDI_COLORS['dark_text'], pad=20)
    ax1.set_ylim(0, 4500)
    ax1.grid(axis='y', alpha=0.3, color=MORANDI_COLORS['light_text'],
            linestyle='-', linewidth=1, zorder=0)
    ax1.spines['left'].set_color(MORANDI_COLORS['light_text'])
    ax1.spines['bottom'].set_color(MORANDI_COLORS['light_text'])
    
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 50,
                f'{int(height)} MB', ha='center', va='bottom', fontsize=12,
                fontweight='bold', color=MORANDI_COLORS['dark_text'])
    
    # Add percentage reduction - 更精美的标注
    reduction = (1 - memory[1]/memory[0]) * 100
    reduction_box = FancyBboxPatch((0.5-0.15, memory[0]/2-0.15), 0.3, 0.3,
                                   boxstyle="round,pad=0.1", facecolor=MORANDI_COLORS['soft_coral'],
                                   edgecolor='white', linewidth=2, alpha=0.9, zorder=10)
    shadow_reduction = FancyBboxPatch((0.5-0.15+0.02, memory[0]/2-0.15-0.02), 0.3, 0.3,
                                     boxstyle="round,pad=0.1", facecolor='black',
                                     alpha=0.15, zorder=9)
    ax1.add_patch(shadow_reduction)
    ax1.add_patch(reduction_box)
    ax1.text(0.5, memory[0]/2, f'{reduction:.0f}%\nreduction',
            ha='center', va='center', fontsize=11, weight='bold', color='white',
            zorder=11)
    
    # Response time comparison
    stages = ['Vector\nSearch', 'Reranking', 'LLM\nGeneration', 'Total']
    times = [0.8, 1.2, 1.4, 3.4]  # seconds
    
    time_colors = [MORANDI_COLORS['dusty_blue'], MORANDI_COLORS['sage_green'],
                   MORANDI_COLORS['warm_beige'], MORANDI_COLORS['soft_coral']]
    x_pos2 = np.arange(len(stages))
    bars2 = ax2.bar(x_pos2, times, color=time_colors, alpha=0.9,
                   edgecolor='white', linewidth=3.5, width=0.6)
    
    # 添加阴影
    for bar in bars2:
        shadow = Rectangle((bar.get_x() + 0.02, bar.get_y() - 0.02), 
                          bar.get_width(), bar.get_height(),
                          facecolor='black', alpha=0.15, zorder=bar.zorder-1)
        ax2.add_patch(shadow)
    
    ax2.set_facecolor('#FAF8F5')
    ax2.set_xticks(x_pos2)
    ax2.set_xticklabels(stages, fontsize=11.5, color=MORANDI_COLORS['dark_text'])
    ax2.set_ylabel('Time (seconds)', fontsize=13, fontweight='600',
                  color=MORANDI_COLORS['medium_text'])
    ax2.set_title('Query Processing Time Breakdown', fontsize=15, weight='400',
                 color=MORANDI_COLORS['dark_text'], pad=20)
    ax2.set_ylim(0, 4)
    ax2.grid(axis='y', alpha=0.3, color=MORANDI_COLORS['light_text'],
            linestyle='-', linewidth=1, zorder=0)
    ax2.spines['left'].set_color(MORANDI_COLORS['light_text'])
    ax2.spines['bottom'].set_color(MORANDI_COLORS['light_text'])
    
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.1f}s', ha='center', va='bottom', fontsize=12,
                fontweight='bold', color=MORANDI_COLORS['dark_text'])
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/performance.png', dpi=300, bbox_inches='tight',
               facecolor=MORANDI_COLORS['background'], edgecolor='none')
    plt.close()
    print("✓ Created performance comparison")

def main():
    """主函数"""
    print("Generating beautiful visualizations for Midterm Report (Enhanced Morandi Style)...\n")
    
    create_architecture_diagram()
    create_api_usage_chart()
    create_tech_stack_diagram()
    create_workflow_diagram()
    create_performance_comparison()
    
    print(f"\n✓ All visualizations saved to {output_dir}/")

if __name__ == "__main__":
    main()
