#!/usr/bin/env python3
"""
重新设计延迟分解图表 - 更优雅的莫兰迪风格
"""
import matplotlib.pyplot as plt
import numpy as np

# 莫兰迪配色方案
MORANDI_COLORS = {
    'dusty_blue': '#9db4c0',
    'sage_green': '#a8b5a0',
    'warm_beige': '#c4b5a0',
    'soft_coral': '#d4a5a5',
    'muted_purple': '#b5a7c4',
    'light_gray': '#c8c8c8',
    'dark_text': '#5a5a5a',
    'medium_text': '#8a8a8a',
    'light_text': '#b8b8b8',
    'background': '#f7f6f3'
}

# 设置样式
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.facecolor'] = MORANDI_COLORS['background']
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.left'] = True
plt.rcParams['axes.spines.bottom'] = True
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['text.color'] = MORANDI_COLORS['dark_text']
plt.rcParams['axes.labelcolor'] = MORANDI_COLORS['medium_text']
plt.rcParams['xtick.color'] = MORANDI_COLORS['medium_text']
plt.rcParams['ytick.color'] = MORANDI_COLORS['medium_text']

# 创建图表
fig, ax = plt.subplots(figsize=(16, 8))
fig.patch.set_facecolor(MORANDI_COLORS['background'])
ax.set_facecolor('#fafafa')

# 数据
categories = ['Test Set 1\n(Basic)', 'Test Set 2\n(Advanced)', 'Test Set 3\n(Multimodal)', 'Average']
preprocessing = np.array([0.08, 0.09, 0.35, 0.17])
intent_detection = np.array([0.15, 0.18, 0.16, 0.16])
tool_execution = np.array([0.29, 0.41, 0.61, 0.44])
llm_generation = np.array([1.35, 1.48, 1.38, 1.40])
tts_synthesis = np.array([0.28, 0.32, 0.28, 0.29])

x = np.arange(len(categories))
width = 0.65

# 使用更柔和的渐变色
colors = {
    'preprocessing': MORANDI_COLORS['dusty_blue'],
    'intent': MORANDI_COLORS['muted_purple'],
    'tool': MORANDI_COLORS['sage_green'],
    'llm': MORANDI_COLORS['warm_beige'],
    'tts': MORANDI_COLORS['soft_coral']
}

# 绘制堆叠柱状图
p1 = ax.bar(x, preprocessing, width, label='Preprocessing', 
            color=colors['preprocessing'], alpha=0.9, edgecolor='white', linewidth=2)

p2 = ax.bar(x, intent_detection, width, bottom=preprocessing, 
            label='Intent Detection', color=colors['intent'], alpha=0.9, 
            edgecolor='white', linewidth=2)

p3 = ax.bar(x, tool_execution, width, 
            bottom=preprocessing+intent_detection, 
            label='Tool Execution', color=colors['tool'], alpha=0.9, 
            edgecolor='white', linewidth=2)

p4 = ax.bar(x, llm_generation, width, 
            bottom=preprocessing+intent_detection+tool_execution,
            label='LLM Generation', color=colors['llm'], alpha=0.9, 
            edgecolor='white', linewidth=2)

p5 = ax.bar(x, tts_synthesis, width,
            bottom=preprocessing+intent_detection+tool_execution+llm_generation,
            label='TTS Synthesis', color=colors['tts'], alpha=0.9, 
            edgecolor='white', linewidth=2)

# 设置标签和标题
ax.set_xlabel('Test Sets', fontsize=14, fontweight='400', color=MORANDI_COLORS['dark_text'])
ax.set_ylabel('Latency (seconds)', fontsize=14, fontweight='400', color=MORANDI_COLORS['dark_text'])
ax.set_title('End-to-End Latency Breakdown by Processing Stage', 
             fontsize=17, fontweight='300', color=MORANDI_COLORS['dark_text'], pad=60)

ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=12)
ax.set_ylim(0, 3.2)

# 美化图例
legend = ax.legend(framealpha=0.95, fancybox=True, shadow=False, 
                   borderpad=1, facecolor='white', edgecolor=MORANDI_COLORS['light_text'], 
                   fontsize=12, ncol=5, bbox_to_anchor=(0, 1.02), loc='lower left')

# 网格线
ax.grid(axis='y', alpha=0.25, linestyle='-', linewidth=0.8, color=MORANDI_COLORS['light_text'])
ax.set_axisbelow(True)

# 添加总计标签（更优雅的样式）
totals = [2.15, 2.48, 2.78, 2.47]
for i, total in enumerate(totals):
    # 在柱子顶部添加总时间
    ax.text(i, total + 0.06, f'{total:.2f}s', 
            ha='center', va='bottom', fontweight='600', fontsize=12, 
            color=MORANDI_COLORS['dark_text'])
    
    # 添加百分比标注（LLM占比）
    llm_pct = (llm_generation[i] / total) * 100
    ax.text(i, total - 0.15, f'LLM: {llm_pct:.0f}%', 
            ha='center', va='top', fontsize=11, 
            color='white', fontweight='700',
            bbox=dict(boxstyle="round,pad=0.4", facecolor=colors['llm'], 
                     edgecolor='white', alpha=0.95, linewidth=2))

# 添加关键发现标注
ax.text(0.98, 0.97, 
        'Key Finding:\nLLM Generation dominates\n56.7% of total latency',
        transform=ax.transAxes, fontsize=11, verticalalignment='top', 
        horizontalalignment='right',
        bbox=dict(boxstyle='round,pad=0.8', facecolor='white', 
                 edgecolor=MORANDI_COLORS['warm_beige'], alpha=0.95, linewidth=2),
        color=MORANDI_COLORS['dark_text'], linespacing=1.5)

plt.tight_layout()
plt.savefig('visualizations/latency_breakdown.png', dpi=300, bbox_inches='tight',
            facecolor=MORANDI_COLORS['background'], edgecolor='none', pad_inches=0.2)
print("✅ 已重新生成更美观的 latency_breakdown.png")
plt.close()

