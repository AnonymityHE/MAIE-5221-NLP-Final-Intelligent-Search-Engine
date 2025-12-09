#!/usr/bin/env python3
"""
生成实验评估图表 - 莫兰迪配色方案
参考MAIE5532的可视化风格
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from scipy.ndimage import uniform_filter1d

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
    'light_text': '#b8b8b8',      # 浅灰文字
    'accent_green': '#a8b5a0',    # 强调绿色
    'background': '#f7f6f3'       # 米白色背景
}

# 设置莫兰迪绘图样式
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


def create_test_sets_comparison():
    """图1: 三个测试集的对比（柱状图）"""
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor(MORANDI_COLORS['background'])
    ax.set_facecolor('#fafafa')
    
    categories = ['Accuracy\n(%)', 'Mean Search\nTime (s)', 'Total Latency\n(s)', 'Tool Correctness\n(%)']
    set1 = [95.0, 0.52, 2.15, 100.0]
    set2 = [90.0, 0.68, 2.48, 90.0]
    set3 = [90.0, 1.12, 2.78, 90.0]
    
    x = np.arange(len(categories))
    width = 0.25
    
    bars1 = ax.bar(x - width, set1, width, label='Test Set 1 (Basic Queries)', 
                   color=MORANDI_COLORS['dusty_blue'], alpha=0.85, edgecolor='white', linewidth=2)
    bars2 = ax.bar(x, set2, width, label='Test Set 2 (Advanced Queries)', 
                   color=MORANDI_COLORS['sage_green'], alpha=0.85, edgecolor='white', linewidth=2)
    bars3 = ax.bar(x + width, set3, width, label='Test Set 3 (Multimodal)', 
                   color=MORANDI_COLORS['soft_coral'], alpha=0.85, edgecolor='white', linewidth=2)
    
    ax.set_xlabel('Evaluation Metrics', fontsize=13, fontweight='400', color=MORANDI_COLORS['medium_text'])
    ax.set_ylabel('Value', fontsize=13, fontweight='400', color=MORANDI_COLORS['medium_text'])
    ax.set_title('Performance Comparison Across Test Sets', fontsize=16, fontweight='400', 
                 color=MORANDI_COLORS['dark_text'], pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.legend(loc='upper right', framealpha=0.95, fancybox=True, shadow=False, borderpad=1,
              facecolor='white', edgecolor=MORANDI_COLORS['light_text'], fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.8, color=MORANDI_COLORS['light_text'])
    
    # 添加数值标签
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1.5,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontsize=9, fontweight='400',
                   color=MORANDI_COLORS['dark_text'])
    
    plt.tight_layout()
    plt.savefig('visualizations/test_sets_comparison.png', dpi=300, bbox_inches='tight', 
                facecolor=MORANDI_COLORS['background'], edgecolor='none', pad_inches=0.2)
    print("✓ 已生成: test_sets_comparison.png")
    plt.close()


def create_latency_breakdown():
    """图2: 延迟分解堆叠柱状图"""
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor(MORANDI_COLORS['background'])
    ax.set_facecolor('#fafafa')
    
    categories = ['Test Set 1', 'Test Set 2', 'Test Set 3', 'Average']
    preprocessing = [0.08, 0.09, 0.35, 0.17]
    intent_detection = [0.15, 0.18, 0.16, 0.16]
    tool_execution = [0.29, 0.41, 0.61, 0.44]
    llm_generation = [1.35, 1.48, 1.38, 1.40]
    tts_synthesis = [0.28, 0.32, 0.28, 0.29]
    
    x = np.arange(len(categories))
    width = 0.6
    
    p1 = ax.bar(x, preprocessing, width, label='Preprocessing', 
                color='#8b5cf6', alpha=0.9, edgecolor='white', linewidth=1.5)
    p2 = ax.bar(x, intent_detection, width, bottom=preprocessing, label='Intent Detection', 
                color='#6366f1', alpha=0.9, edgecolor='white', linewidth=1.5)
    p3 = ax.bar(x, tool_execution, width, 
                bottom=np.array(preprocessing)+np.array(intent_detection), 
                label='Tool Execution', color='#3b82f6', alpha=0.9, edgecolor='white', linewidth=1.5)
    p4 = ax.bar(x, llm_generation, width, 
                bottom=np.array(preprocessing)+np.array(intent_detection)+np.array(tool_execution),
                label='LLM Generation', color='#10b981', alpha=0.9, edgecolor='white', linewidth=1.5)
    p5 = ax.bar(x, tts_synthesis, width,
                bottom=np.array(preprocessing)+np.array(intent_detection)+np.array(tool_execution)+np.array(llm_generation),
                label='TTS Synthesis', color='#f59e0b', alpha=0.9, edgecolor='white', linewidth=1.5)
    
    ax.set_xlabel('Test Sets', fontsize=13, fontweight='400', color=MORANDI_COLORS['medium_text'])
    ax.set_ylabel('Latency (seconds)', fontsize=13, fontweight='400', color=MORANDI_COLORS['medium_text'])
    ax.set_title('Latency Breakdown by Processing Stage', fontsize=16, fontweight='400', 
                 color=MORANDI_COLORS['dark_text'], pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.legend(loc='upper left', framealpha=0.95, fancybox=True, shadow=False, borderpad=1,
              facecolor='white', edgecolor=MORANDI_COLORS['light_text'], fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.8, color=MORANDI_COLORS['light_text'])
    
    # 添加总计标签
    totals = [2.15, 2.48, 2.78, 2.47]
    for i, total in enumerate(totals):
        ax.text(i, total + 0.08, f'{total:.2f}s', ha='center', va='bottom', 
                fontweight='400', fontsize=11, color=MORANDI_COLORS['dark_text'],
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                         edgecolor=MORANDI_COLORS['light_text'], alpha=0.9))
    
    plt.tight_layout()
    plt.savefig('visualizations/latency_breakdown.png', dpi=300, bbox_inches='tight',
                facecolor=MORANDI_COLORS['background'], edgecolor='none', pad_inches=0.2)
    print("✓ 已生成: latency_breakdown.png")
    plt.close()


def create_rag_quality_comparison():
    """图3: RAG检索质量对比（雷达图）"""
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    fig.patch.set_facecolor(MORANDI_COLORS['background'])
    
    categories = ['Recall@20/5', 'Precision@20/5', 'MRR', 'Speed\n(inverse)']
    stage1 = [92.5, 46.3, 68.0, 100 - 18]  # Speed用100-时间来表示（越大越好）
    stage2 = [87.5, 75.0, 82.0, 100 - 29]
    
    # 闭合图形
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    stage1 += stage1[:1]
    stage2 += stage2[:1]
    angles += angles[:1]
    
    ax.plot(angles, stage1, 'o-', linewidth=2.5, label='Stage 1: Milvus Vector Search', 
            color=MORANDI_COLORS['dusty_blue'], markersize=10, markerfacecolor='white', 
            markeredgewidth=2, markeredgecolor=MORANDI_COLORS['dusty_blue'])
    ax.fill(angles, stage1, alpha=0.15, color=MORANDI_COLORS['dusty_blue'])
    
    ax.plot(angles, stage2, 'o-', linewidth=2.5, label='Stage 2: Cross-encoder Reranking', 
            color=MORANDI_COLORS['soft_coral'], markersize=10, markerfacecolor='white',
            markeredgewidth=2, markeredgecolor=MORANDI_COLORS['soft_coral'])
    ax.fill(angles, stage2, alpha=0.15, color=MORANDI_COLORS['soft_coral'])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12, color=MORANDI_COLORS['dark_text'])
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(['25', '50', '75', '100'], fontsize=10, color=MORANDI_COLORS['medium_text'])
    ax.grid(True, alpha=0.3, color=MORANDI_COLORS['light_text'])
    ax.set_title('RAG Retrieval Quality: Two-Stage Comparison', fontsize=16, fontweight='400', 
                 color=MORANDI_COLORS['dark_text'], pad=35)
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.15), framealpha=0.95, fancybox=True,
              facecolor='white', edgecolor=MORANDI_COLORS['light_text'], fontsize=11)
    
    plt.tight_layout()
    plt.savefig('visualizations/rag_quality_comparison.png', dpi=300, bbox_inches='tight',
                facecolor=MORANDI_COLORS['background'], edgecolor='none', pad_inches=0.2)
    print("✓ 已生成: rag_quality_comparison.png")
    plt.close()


def create_tool_performance():
    """图4: 工具性能对比（散点图）"""
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor(MORANDI_COLORS['background'])
    ax.set_facecolor('#fafafa')
    
    tools = ['Local RAG', 'Web Search\n(Tavily)', 'Weather API', 'Finance API', 'Multimodal\n(Doubao)']
    success_rates = [91.7, 100.0, 100.0, 100.0, 80.0]
    latencies = [0.31, 0.58, 0.22, 0.41, 1.15]
    invocations = [12, 8, 3, 4, 5]
    
    # 气泡大小与调用次数成正比
    sizes = [inv * 80 for inv in invocations]
    tool_colors = [MORANDI_COLORS['dusty_blue'], MORANDI_COLORS['sage_green'], 
                   MORANDI_COLORS['accent_green'], MORANDI_COLORS['warm_beige'], 
                   MORANDI_COLORS['soft_coral']]
    
    for i, (tool, sr, lat, size, color) in enumerate(zip(tools, success_rates, latencies, sizes, tool_colors)):
        ax.scatter(lat, sr, s=size, alpha=0.7, color=color, edgecolors='white', linewidth=3, zorder=5)
        ax.text(lat, sr + 2.5, tool, ha='center', fontsize=11, fontweight='400',
                color=MORANDI_COLORS['dark_text'],
                bbox=dict(boxstyle="round,pad=0.4", facecolor='white', 
                         edgecolor=color, alpha=0.9, linewidth=2))
    
    ax.set_xlabel('Average Latency (seconds)', fontsize=13, fontweight='400', 
                  color=MORANDI_COLORS['medium_text'])
    ax.set_ylabel('Success Rate (%)', fontsize=13, fontweight='400', 
                  color=MORANDI_COLORS['medium_text'])
    ax.set_title('Tool Performance: Success Rate vs Latency', fontsize=16, fontweight='400', 
                 color=MORANDI_COLORS['dark_text'], pad=20)
    ax.set_ylim(75, 108)
    ax.set_xlim(0, 1.35)
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.8, color=MORANDI_COLORS['light_text'])
    
    # 添加理想区域标注
    ax.axhline(y=95, color=MORANDI_COLORS['accent_green'], linestyle='--', alpha=0.5, linewidth=2)
    ax.axvline(x=0.5, color=MORANDI_COLORS['accent_green'], linestyle='--', alpha=0.5, linewidth=2)
    ax.text(0.05, 96.5, 'High Success Zone', fontsize=10, color=MORANDI_COLORS['accent_green'], 
            alpha=0.7, fontweight='400')
    ax.text(0.52, 77, 'Low Latency Zone →', fontsize=10, color=MORANDI_COLORS['accent_green'], 
            alpha=0.7, fontweight='400')
    
    # 图例（气泡大小）
    legend_text = 'Bubble size represents invocation frequency\n(larger = more frequently used)'
    ax.text(0.98, 0.02, legend_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                     edgecolor=MORANDI_COLORS['light_text'], alpha=0.9),
            color=MORANDI_COLORS['medium_text'])
    
    plt.tight_layout()
    plt.savefig('visualizations/tool_performance.png', dpi=300, bbox_inches='tight',
                facecolor=MORANDI_COLORS['background'], edgecolor='none', pad_inches=0.2)
    print("✓ 已生成: tool_performance.png")
    plt.close()


def create_ablation_study():
    """图5: 消融实验对比（水平柱状图）"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.patch.set_facecolor(MORANDI_COLORS['background'])
    
    for ax in [ax1, ax2]:
        ax.set_facecolor('#fafafa')
    
    configs = ['Full System\n(Jude)', '- Cross-encoder\nreranking', '- Credibility\nweighting', 
               '- Dual-brain\n(HKGAI only)', '- Workflow\nplanner']
    accuracy = [91.8, 84.2, 88.3, 87.5, 89.2]
    latency = [2.47, 2.31, 2.45, 2.52, 2.39]
    
    y_pos = np.arange(len(configs))
    
    # 准确率图
    bar_colors = [MORANDI_COLORS['dusty_blue'] if i == 0 else MORANDI_COLORS['light_gray'] 
                  for i in range(len(configs))]
    bars1 = ax1.barh(y_pos, accuracy, color=bar_colors, alpha=0.85, 
                     edgecolor='white', linewidth=2)
    ax1.set_xlabel('Accuracy (%)', fontsize=13, fontweight='400', color=MORANDI_COLORS['medium_text'])
    ax1.set_title('Impact on Accuracy', fontsize=14, fontweight='400', 
                  color=MORANDI_COLORS['dark_text'], pad=15)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(configs, fontsize=11)
    ax1.set_xlim(82, 94)
    ax1.grid(axis='x', alpha=0.3, linestyle='-', linewidth=0.8, color=MORANDI_COLORS['light_text'])
    
    # 添加数值标签
    for i, (bar, val) in enumerate(zip(bars1, accuracy)):
        ax1.text(val + 0.3, bar.get_y() + bar.get_height()/2, f'{val:.1f}%', 
                va='center', fontsize=10, fontweight='400', color=MORANDI_COLORS['dark_text'])
    
    # 延迟图
    bar_colors2 = [MORANDI_COLORS['soft_coral'] if i == 0 else MORANDI_COLORS['light_gray'] 
                   for i in range(len(configs))]
    bars2 = ax2.barh(y_pos, latency, color=bar_colors2, alpha=0.85, 
                     edgecolor='white', linewidth=2)
    ax2.set_xlabel('Latency (seconds)', fontsize=13, fontweight='400', color=MORANDI_COLORS['medium_text'])
    ax2.set_title('Impact on Latency', fontsize=14, fontweight='400', 
                  color=MORANDI_COLORS['dark_text'], pad=15)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(configs, fontsize=11)
    ax2.set_xlim(2.25, 2.6)
    ax2.grid(axis='x', alpha=0.3, linestyle='-', linewidth=0.8, color=MORANDI_COLORS['light_text'])
    
    # 添加数值标签
    for i, (bar, val) in enumerate(zip(bars2, latency)):
        ax2.text(val + 0.015, bar.get_y() + bar.get_height()/2, f'{val:.2f}s', 
                va='center', fontsize=10, fontweight='400', color=MORANDI_COLORS['dark_text'])
    
    fig.suptitle('Ablation Study: Component Contribution Analysis', fontsize=16, fontweight='400',
                 color=MORANDI_COLORS['dark_text'], y=0.98)
    
    plt.tight_layout()
    plt.savefig('visualizations/ablation_study.png', dpi=300, bbox_inches='tight',
                facecolor=MORANDI_COLORS['background'], edgecolor='none', pad_inches=0.2)
    print("✓ 已生成: ablation_study.png")
    plt.close()


def create_overall_metrics():
    """图6: 整体指标仪表盘"""
    fig = plt.figure(figsize=(18, 12))
    fig.patch.set_facecolor(MORANDI_COLORS['background'])
    gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.3)
    
    fig.suptitle('Overall System Performance Dashboard', fontsize=18, fontweight='400',
                 color=MORANDI_COLORS['dark_text'], y=0.98)
    
    # 1. 准确率饼图
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor('#fafafa')
    correct = 27
    incorrect = 3
    colors_pie = [MORANDI_COLORS['sage_green'], MORANDI_COLORS['soft_coral']]
    explode = (0.05, 0)
    wedges, texts, autotexts = ax1.pie([correct, incorrect], labels=['Correct', 'Incorrect'], 
                                        autopct='%1.1f%%', colors=colors_pie, explode=explode, 
                                        startangle=90, textprops={'fontsize': 12, 'fontweight': '400',
                                        'color': MORANDI_COLORS['dark_text']})
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    ax1.set_title('Overall Accuracy\n(27/30 queries)', fontsize=13, fontweight='400', 
                  color=MORANDI_COLORS['dark_text'], pad=15)
    
    # 2. 平均搜索时间分布
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor('#fafafa')
    time_ranges = ['<0.5s', '0.5-1.0s', '1.0-1.5s', '>1.5s']
    counts = [12, 10, 6, 2]
    colors_bar = [MORANDI_COLORS['sage_green'], MORANDI_COLORS['dusty_blue'], 
                  MORANDI_COLORS['warm_beige'], MORANDI_COLORS['soft_coral']]
    bars = ax2.bar(time_ranges, counts, color=colors_bar, alpha=0.85, edgecolor='white', linewidth=2)
    ax2.set_ylabel('Number of Queries', fontsize=12, fontweight='400', color=MORANDI_COLORS['medium_text'])
    ax2.set_title('Search Time Distribution', fontsize=13, fontweight='400', 
                  color=MORANDI_COLORS['dark_text'], pad=15)
    ax2.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.8, color=MORANDI_COLORS['light_text'])
    for bar, count in zip(bars, counts):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, str(count),
                ha='center', va='bottom', fontsize=10, fontweight='400', 
                color=MORANDI_COLORS['dark_text'])
    
    # 3. 工具选择正确率
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.set_facecolor('#fafafa')
    tool_correct = 28
    tool_incorrect = 2
    colors_tool = [MORANDI_COLORS['dusty_blue'], MORANDI_COLORS['soft_coral']]
    explode_tool = (0.05, 0)
    wedges, texts, autotexts = ax3.pie([tool_correct, tool_incorrect], labels=['Correct', 'Incorrect'], 
                                        autopct='%1.1f%%', colors=colors_tool, explode=explode_tool, 
                                        startangle=90, textprops={'fontsize': 12, 'fontweight': '400',
                                        'color': MORANDI_COLORS['dark_text']})
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    ax3.set_title('Tool Selection Correctness\n(28/30 queries)', fontsize=13, fontweight='400', 
                  color=MORANDI_COLORS['dark_text'], pad=15)
    
    # 4. 各测试集准确率趋势
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.set_facecolor('#fafafa')
    test_sets = ['Set 1', 'Set 2', 'Set 3']
    accuracies = [95.0, 90.0, 90.0]
    ax4.plot(test_sets, accuracies, marker='o', linewidth=3, markersize=12, 
             color=MORANDI_COLORS['dusty_blue'], markerfacecolor='white', 
             markeredgewidth=2.5, markeredgecolor=MORANDI_COLORS['dusty_blue'])
    ax4.fill_between(range(len(test_sets)), accuracies, alpha=0.15, color=MORANDI_COLORS['dusty_blue'])
    ax4.set_ylabel('Accuracy (%)', fontsize=12, fontweight='400', color=MORANDI_COLORS['medium_text'])
    ax4.set_title('Accuracy Across Test Sets', fontsize=13, fontweight='400', 
                  color=MORANDI_COLORS['dark_text'], pad=15)
    ax4.set_ylim(85, 100)
    ax4.grid(True, alpha=0.3, linestyle='-', linewidth=0.8, color=MORANDI_COLORS['light_text'])
    for i, acc in enumerate(accuracies):
        ax4.text(i, acc + 1.5, f'{acc:.1f}%', ha='center', va='bottom', fontsize=10, 
                fontweight='400', color=MORANDI_COLORS['dark_text'])
    
    # 5. 延迟对比
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.set_facecolor('#fafafa')
    latency_types = ['Mean Search\nTime', 'Total\nLatency']
    latency_values = [0.77, 2.47]
    colors_lat = [MORANDI_COLORS['sage_green'], MORANDI_COLORS['warm_beige']]
    bars = ax5.bar(latency_types, latency_values, color=colors_lat, alpha=0.85, 
                   width=0.6, edgecolor='white', linewidth=2)
    ax5.set_ylabel('Time (seconds)', fontsize=12, fontweight='400', color=MORANDI_COLORS['medium_text'])
    ax5.set_title('Average Latency Metrics', fontsize=13, fontweight='400', 
                  color=MORANDI_COLORS['dark_text'], pad=15)
    ax5.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.8, color=MORANDI_COLORS['light_text'])
    for bar, val in zip(bars, latency_values):
        ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.08, f'{val:.2f}s',
                ha='center', va='bottom', fontsize=11, fontweight='400', 
                color=MORANDI_COLORS['dark_text'])
    
    # 6. 各工具调用次数
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.set_facecolor('#fafafa')
    tools_short = ['Local\nRAG', 'Web\nSearch', 'Weather\nAPI', 'Finance\nAPI', 'Multimodal']
    invocations = [12, 8, 3, 4, 5]
    colors_tools = [MORANDI_COLORS['dusty_blue'], MORANDI_COLORS['sage_green'], 
                    MORANDI_COLORS['accent_green'], MORANDI_COLORS['warm_beige'], 
                    MORANDI_COLORS['soft_coral']]
    bars = ax6.barh(tools_short, invocations, color=colors_tools, alpha=0.85, 
                    edgecolor='white', linewidth=2)
    ax6.set_xlabel('Number of Invocations', fontsize=12, fontweight='400', 
                   color=MORANDI_COLORS['medium_text'])
    ax6.set_title('Tool Usage Distribution', fontsize=13, fontweight='400', 
                  color=MORANDI_COLORS['dark_text'], pad=15)
    ax6.grid(axis='x', alpha=0.3, linestyle='-', linewidth=0.8, color=MORANDI_COLORS['light_text'])
    for bar, val in zip(bars, invocations):
        ax6.text(val + 0.3, bar.get_y() + bar.get_height()/2, str(val),
                va='center', fontsize=10, fontweight='400', color=MORANDI_COLORS['dark_text'])
    
    plt.tight_layout()
    plt.savefig('visualizations/overall_metrics_dashboard.png', dpi=300, bbox_inches='tight',
                facecolor=MORANDI_COLORS['background'], edgecolor='none', pad_inches=0.2)
    print("✓ 已生成: overall_metrics_dashboard.png")
    plt.close()


if __name__ == '__main__':
    print("🎨 开始生成实验评估图表（莫兰迪配色方案）...\n")
    
    create_test_sets_comparison()
    create_latency_breakdown()
    create_rag_quality_comparison()
    create_tool_performance()
    create_ablation_study()
    create_overall_metrics()
    
    print("\n✅ 所有图表生成完成！")
    print("\n生成的图表文件：")
    print("  1. test_sets_comparison.png - 三个测试集对比")
    print("  2. latency_breakdown.png - 延迟分解")
    print("  3. rag_quality_comparison.png - RAG质量对比")
    print("  4. tool_performance.png - 工具性能")
    print("  5. ablation_study.png - 消融实验")
    print("  6. overall_metrics_dashboard.png - 整体指标仪表盘")

