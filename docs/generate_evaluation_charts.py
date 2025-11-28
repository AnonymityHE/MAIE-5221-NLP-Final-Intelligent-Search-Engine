#!/usr/bin/env python3
"""
生成实验评估图表
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# 设置中文字体和样式
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.unicode_minus'] = False

# 定义颜色方案（参考前端Dashboard的紫色系）
colors = {
    'primary': '#a855f7',      # 紫色
    'secondary': '#3b82f6',    # 蓝色
    'success': '#10b981',      # 绿色
    'warning': '#f59e0b',      # 橙色
    'danger': '#ef4444',       # 红色
    'gray': '#6b7280',         # 灰色
}

def create_test_sets_comparison():
    """图1: 三个测试集的对比（柱状图）"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    categories = ['Accuracy (%)', 'Mean Search\nTime (s)', 'Total Latency (s)', 'Tool Correctness (%)']
    set1 = [95.0, 0.52, 2.15, 100.0]
    set2 = [90.0, 0.68, 2.48, 90.0]
    set3 = [90.0, 1.12, 2.78, 90.0]
    
    x = np.arange(len(categories))
    width = 0.25
    
    bars1 = ax.bar(x - width, set1, width, label='Test Set 1', color=colors['primary'], alpha=0.8)
    bars2 = ax.bar(x, set2, width, label='Test Set 2', color=colors['secondary'], alpha=0.8)
    bars3 = ax.bar(x + width, set3, width, label='Test Set 3', color=colors['success'], alpha=0.8)
    
    ax.set_xlabel('Metrics', fontsize=12, fontweight='bold')
    ax.set_ylabel('Value', fontsize=12, fontweight='bold')
    ax.set_title('Performance Comparison Across Test Sets', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 添加数值标签
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('test_sets_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ 已生成: test_sets_comparison.png")
    plt.close()

def create_latency_breakdown():
    """图2: 延迟分解堆叠柱状图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    categories = ['Test Set 1', 'Test Set 2', 'Test Set 3', 'Average']
    preprocessing = [0.08, 0.09, 0.35, 0.17]
    intent_detection = [0.15, 0.18, 0.16, 0.16]
    tool_execution = [0.29, 0.41, 0.61, 0.44]
    llm_generation = [1.35, 1.48, 1.38, 1.40]
    tts_synthesis = [0.28, 0.32, 0.28, 0.29]
    
    x = np.arange(len(categories))
    width = 0.5
    
    p1 = ax.bar(x, preprocessing, width, label='Preprocessing', color='#8b5cf6', alpha=0.9)
    p2 = ax.bar(x, intent_detection, width, bottom=preprocessing, label='Intent Detection', color='#6366f1', alpha=0.9)
    p3 = ax.bar(x, tool_execution, width, bottom=np.array(preprocessing)+np.array(intent_detection), 
                label='Tool Execution', color='#3b82f6', alpha=0.9)
    p4 = ax.bar(x, llm_generation, width, 
                bottom=np.array(preprocessing)+np.array(intent_detection)+np.array(tool_execution),
                label='LLM Generation', color='#10b981', alpha=0.9)
    p5 = ax.bar(x, tts_synthesis, width,
                bottom=np.array(preprocessing)+np.array(intent_detection)+np.array(tool_execution)+np.array(llm_generation),
                label='TTS Synthesis', color='#f59e0b', alpha=0.9)
    
    ax.set_xlabel('Test Sets', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latency (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Latency Breakdown by Stage', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend(loc='upper left', framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 添加总计标签
    totals = [2.15, 2.48, 2.78, 2.47]
    for i, total in enumerate(totals):
        ax.text(i, total + 0.05, f'{total:.2f}s', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('latency_breakdown.png', dpi=300, bbox_inches='tight')
    print("✓ 已生成: latency_breakdown.png")
    plt.close()

def create_rag_quality_comparison():
    """图3: RAG检索质量对比（雷达图）"""
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    
    categories = ['Recall', 'Precision', 'MRR', 'Speed\n(inverse)']
    stage1 = [92.5, 46.3, 68.0, 100 - 18]  # Speed用100-时间来表示（越大越好）
    stage2 = [87.5, 75.0, 82.0, 100 - 29]
    
    # 闭合图形
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    stage1 += stage1[:1]
    stage2 += stage2[:1]
    angles += angles[:1]
    
    ax.plot(angles, stage1, 'o-', linewidth=2, label='Stage 1 (Milvus)', color=colors['secondary'], markersize=8)
    ax.fill(angles, stage1, alpha=0.15, color=colors['secondary'])
    
    ax.plot(angles, stage2, 'o-', linewidth=2, label='Stage 2 (Reranked)', color=colors['primary'], markersize=8)
    ax.fill(angles, stage2, alpha=0.15, color=colors['primary'])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(['25', '50', '75', '100'], fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_title('RAG Retrieval Quality: Stage 1 vs Stage 2', fontsize=14, fontweight='bold', pad=30)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig('rag_quality_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ 已生成: rag_quality_comparison.png")
    plt.close()

def create_tool_performance():
    """图4: 工具性能对比（散点图）"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    tools = ['Local RAG', 'Web Search', 'Weather API', 'Finance API', 'Multimodal']
    success_rates = [91.7, 100.0, 100.0, 100.0, 80.0]
    latencies = [0.31, 0.58, 0.22, 0.41, 1.15]
    invocations = [12, 8, 3, 4, 5]
    
    # 气泡大小与调用次数成正比
    sizes = [inv * 50 for inv in invocations]
    tool_colors = [colors['primary'], colors['secondary'], colors['success'], colors['warning'], colors['danger']]
    
    for i, (tool, sr, lat, size, color) in enumerate(zip(tools, success_rates, latencies, sizes, tool_colors)):
        ax.scatter(lat, sr, s=size, alpha=0.6, color=color, edgecolors='black', linewidth=1.5, label=tool)
        ax.text(lat, sr + 1.5, tool, ha='center', fontsize=9, fontweight='bold')
    
    ax.set_xlabel('Average Latency (seconds)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Tool Performance: Success Rate vs Latency', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(75, 105)
    ax.set_xlim(0, 1.3)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 添加理想区域标注
    ax.axhline(y=95, color='green', linestyle='--', alpha=0.3, linewidth=1)
    ax.axvline(x=0.5, color='green', linestyle='--', alpha=0.3, linewidth=1)
    ax.text(0.05, 97, 'High Success', fontsize=9, color='green', alpha=0.6)
    ax.text(0.05, 0.45, 'Low Latency', fontsize=9, color='green', alpha=0.6, rotation=90)
    
    # 图例（气泡大小）
    legend_elements = [mpatches.Patch(facecolor='gray', alpha=0.3, label=f'Bubble size = invocations')]
    ax.legend(handles=legend_elements, loc='lower right', framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig('tool_performance.png', dpi=300, bbox_inches='tight')
    print("✓ 已生成: tool_performance.png")
    plt.close()

def create_ablation_study():
    """图5: 消融实验对比（水平柱状图）"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    configs = ['Full System\n(Jude)', '- Cross-encoder\nreranking', '- Credibility\nweighting', 
               '- Dual-brain\n(HKGAI only)', '- Workflow\nplanner']
    accuracy = [91.8, 84.2, 88.3, 87.5, 89.2]
    latency = [2.47, 2.31, 2.45, 2.52, 2.39]
    
    y_pos = np.arange(len(configs))
    
    # 准确率图
    bars1 = ax1.barh(y_pos, accuracy, color=[colors['primary'] if i == 0 else colors['gray'] for i in range(len(configs))], alpha=0.8)
    ax1.set_xlabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax1.set_title('Ablation Study: Accuracy', fontsize=13, fontweight='bold', pad=15)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(configs)
    ax1.set_xlim(80, 95)
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    
    # 添加数值标签
    for i, (bar, val) in enumerate(zip(bars1, accuracy)):
        ax1.text(val + 0.3, bar.get_y() + bar.get_height()/2, f'{val:.1f}%', 
                va='center', fontsize=9, fontweight='bold')
    
    # 延迟图
    bars2 = ax2.barh(y_pos, latency, color=[colors['secondary'] if i == 0 else colors['gray'] for i in range(len(configs))], alpha=0.8)
    ax2.set_xlabel('Latency (seconds)', fontsize=12, fontweight='bold')
    ax2.set_title('Ablation Study: Latency', fontsize=13, fontweight='bold', pad=15)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(configs)
    ax2.set_xlim(2.2, 2.6)
    ax2.grid(axis='x', alpha=0.3, linestyle='--')
    
    # 添加数值标签
    for i, (bar, val) in enumerate(zip(bars2, latency)):
        ax2.text(val + 0.01, bar.get_y() + bar.get_height()/2, f'{val:.2f}s', 
                va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('ablation_study.png', dpi=300, bbox_inches='tight')
    print("✓ 已生成: ablation_study.png")
    plt.close()

def create_overall_metrics():
    """图6: 整体指标仪表盘"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Overall System Performance Dashboard', fontsize=16, fontweight='bold', y=0.98)
    
    # 1. 准确率饼图
    ax = axes[0, 0]
    correct = 27
    incorrect = 3
    colors_pie = [colors['success'], colors['danger']]
    explode = (0.05, 0)
    ax.pie([correct, incorrect], labels=['Correct', 'Incorrect'], autopct='%1.1f%%',
           colors=colors_pie, explode=explode, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax.set_title('Overall Accuracy\n(27/30 queries)', fontsize=12, fontweight='bold', pad=10)
    
    # 2. 平均搜索时间分布
    ax = axes[0, 1]
    time_ranges = ['<0.5s', '0.5-1.0s', '1.0-1.5s', '>1.5s']
    counts = [12, 10, 6, 2]
    bars = ax.bar(time_ranges, counts, color=[colors['success'], colors['primary'], colors['warning'], colors['danger']], alpha=0.8)
    ax.set_ylabel('Number of Queries', fontsize=11, fontweight='bold')
    ax.set_title('Search Time Distribution', fontsize=12, fontweight='bold', pad=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, str(count),
               ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # 3. 工具选择正确率
    ax = axes[0, 2]
    tool_correct = 28
    tool_incorrect = 2
    colors_tool = [colors['primary'], colors['danger']]
    explode_tool = (0.05, 0)
    ax.pie([tool_correct, tool_incorrect], labels=['Correct', 'Incorrect'], autopct='%1.1f%%',
           colors=colors_tool, explode=explode_tool, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax.set_title('Tool Selection Correctness\n(28/30 queries)', fontsize=12, fontweight='bold', pad=10)
    
    # 4. 各测试集准确率趋势
    ax = axes[1, 0]
    test_sets = ['Set 1', 'Set 2', 'Set 3']
    accuracies = [95.0, 90.0, 90.0]
    ax.plot(test_sets, accuracies, marker='o', linewidth=2.5, markersize=10, color=colors['primary'])
    ax.fill_between(range(len(test_sets)), accuracies, alpha=0.2, color=colors['primary'])
    ax.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
    ax.set_title('Accuracy Across Test Sets', fontsize=12, fontweight='bold', pad=10)
    ax.set_ylim(85, 100)
    ax.grid(True, alpha=0.3, linestyle='--')
    for i, acc in enumerate(accuracies):
        ax.text(i, acc + 1, f'{acc:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # 5. 延迟对比
    ax = axes[1, 1]
    latency_types = ['Search', 'Total']
    latency_values = [0.77, 2.47]
    bars = ax.bar(latency_types, latency_values, color=[colors['secondary'], colors['warning']], alpha=0.8, width=0.5)
    ax.set_ylabel('Time (seconds)', fontsize=11, fontweight='bold')
    ax.set_title('Average Latency Metrics', fontsize=12, fontweight='bold', pad=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    for bar, val in zip(bars, latency_values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, f'{val:.2f}s',
               ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # 6. 各工具调用次数
    ax = axes[1, 2]
    tools_short = ['RAG', 'Web', 'Weather', 'Finance', 'Multi']
    invocations = [12, 8, 3, 4, 5]
    colors_tools = [colors['primary'], colors['secondary'], colors['success'], colors['warning'], colors['danger']]
    bars = ax.barh(tools_short, invocations, color=colors_tools, alpha=0.8)
    ax.set_xlabel('Invocations', fontsize=11, fontweight='bold')
    ax.set_title('Tool Usage Distribution', fontsize=12, fontweight='bold', pad=10)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    for bar, val in zip(bars, invocations):
        ax.text(val + 0.2, bar.get_y() + bar.get_height()/2, str(val),
               va='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('overall_metrics_dashboard.png', dpi=300, bbox_inches='tight')
    print("✓ 已生成: overall_metrics_dashboard.png")
    plt.close()

if __name__ == '__main__':
    print("🎨 开始生成实验评估图表...\n")
    
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

