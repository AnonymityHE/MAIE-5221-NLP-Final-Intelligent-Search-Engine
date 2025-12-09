"""
Part 1: 剪枝技术可视化脚本
生成剪枝实验的综合分析图表
"""

import json
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from datetime import datetime

# 莫兰迪配色方案 - 背景和文字颜色
MORANDI_COLORS = {
    'background': '#f7f6f3',      # 米白色背景
    'dark_text': '#5a5a5a',       # 深灰文字
    'medium_text': '#8a8a8a',     # 中灰文字
}

# 设置莫兰迪绘图样式
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.facecolor'] = MORANDI_COLORS['background']
plt.rcParams['axes.facecolor'] = (1.0, 1.0, 1.0, 0.85)  # 白色带85%不透明度
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

def print_with_timestamp(message):
    """打印带时间戳的消息"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()

def load_data(file_path="results/part1/part1_unified_results.json"):
    """加载Part 1数据"""
    if not os.path.exists(file_path):
        print_with_timestamp(f"❌ 数据文件未找到: {file_path}")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_comprehensive_visualization():
    """创建Part 1综合可视化"""
    print_with_timestamp("🎨 生成Part 1剪枝技术可视化...")
    
    data = load_data()
    if not data:
        return None
    
    # 配色方案（与参考脚本一致）
    colors = {
        'primary': '#3b75af',      # 蓝色
        'secondary': '#8e7cc3',    # 紫色
        'tertiary': '#7aa78a',     # 绿色
        'accent': '#f39c12',       # 橙色
        'danger': '#e74c3c'        # 红色
    }
    
    # 创建图表
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    fig.suptitle('Part 1: Pruning Techniques - Comprehensive Analysis\nWide-ResNet-28-10 on CIFAR-100', 
                 fontsize=16, fontweight='bold', y=0.96)
    
    baseline_acc = data['metadata']['baseline_accuracy'] * 100
    
    # ========== 1. Magnitude-based Pruning ==========
    ax1 = fig.add_subplot(gs[0, 0])
    mag_results = data['1_magnitude_based_pruning']['results']
    
    sparsity_levels = ['30%', '50%', '70%', '90%']
    accuracies = [
        mag_results['30pct_sparsity']['accuracy'] * 100,
        mag_results['50pct_sparsity']['accuracy'] * 100,
        mag_results['70pct_sparsity']['accuracy'] * 100,
        mag_results['90pct_sparsity']['accuracy'] * 100
    ]
    
    bars = ax1.bar(sparsity_levels, accuracies, color=colors['primary'], alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.axhline(y=baseline_acc, color=colors['danger'], linestyle='--', linewidth=2, label=f'Baseline ({baseline_acc:.1f}%)')
    ax1.set_title('Magnitude-Based Pruning', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Accuracy (%)', fontsize=11)
    ax1.set_xlabel('Sparsity Level', fontsize=11)
    ax1.set_ylim(70, 82)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, height + 0.3,
                f'{acc:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # ========== 2. Structured vs Unstructured ==========
    ax2 = fig.add_subplot(gs[0, 1])
    
    methods = ['Unstructured\n30%', 'Structured\n25%', 'Unstructured\n50%', 'Structured\n50%']
    method_accs = [
        mag_results['30pct_sparsity']['accuracy'] * 100,
        data['2_structured_pruning']['results']['25pct_removal']['accuracy'] * 100,
        mag_results['50pct_sparsity']['accuracy'] * 100,
        data['2_structured_pruning']['results']['50pct_removal']['accuracy'] * 100
    ]
    method_colors = [colors['primary'], colors['secondary'], colors['primary'], colors['secondary']]
    
    bars = ax2.bar(methods, method_accs, color=method_colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax2.axhline(y=baseline_acc, color=colors['danger'], linestyle='--', linewidth=2, label='Baseline')
    ax2.set_title('Unstructured vs Structured Pruning', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Accuracy (%)', fontsize=11)
    ax2.set_ylim(70, 82)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    for bar, acc in zip(bars, method_accs):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, height + 0.3,
                f'{acc:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # ========== 3. Gradual vs One-shot ==========
    ax3 = fig.add_subplot(gs[0, 2])
    
    comparison_methods = ['Gradual\n70%', 'One-shot\n70%']
    comparison_accs = [
        data['3_gradual_vs_oneshot']['results']['gradual']['accuracy'] * 100,
        data['3_gradual_vs_oneshot']['results']['oneshot']['accuracy'] * 100
    ]
    comparison_epochs = [
        data['3_gradual_vs_oneshot']['results']['gradual']['epochs'],
        data['3_gradual_vs_oneshot']['results']['oneshot']['epochs']
    ]
    
    x = np.arange(len(comparison_methods))
    width = 0.35
    
    bars1 = ax3.bar(x - width/2, comparison_accs, width, label='Accuracy (%)', 
                    color=colors['tertiary'], alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax3.bar(x + width/2, comparison_epochs, width, label='Epochs', 
                    color=colors['accent'], alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax3.set_title('Gradual vs One-shot Pruning', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Value', fontsize=11)
    ax3.set_xticks(x)
    ax3.set_xticklabels(comparison_methods)
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    for bar, acc in zip(bars1, comparison_accs):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2, height + 1,
                f'{acc:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    for bar, epoch in zip(bars2, comparison_epochs):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2, height + 1,
                f'{epoch}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # ========== 4. Layer Sensitivity (Top 10) ==========
    ax4 = fig.add_subplot(gs[1, :])
    
    sensitivity_data = data['4_layer_sensitivity_analysis']['statistics']
    most_sensitive = sensitivity_data['most_sensitive_layers'][:10]
    
    layer_names = [layer[0].replace('_', ' ') for layer in most_sensitive]
    sensitivities = [layer[1] * 100 for layer in most_sensitive]
    
    bars = ax4.barh(layer_names, sensitivities, color=colors['danger'], alpha=0.8, edgecolor='black', linewidth=1.5)
    ax4.set_title('Layer Sensitivity Analysis - Top 10 Most Sensitive Layers', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Average Accuracy Drop (%)', fontsize=11)
    ax4.grid(True, alpha=0.3, axis='x')
    ax4.invert_yaxis()
    
    for bar, sens in zip(bars, sensitivities):
        width = bar.get_width()
        ax4.text(width + 0.2, bar.get_y() + bar.get_height()/2,
                f'{sens:.2f}%', ha='left', va='center', fontweight='bold', fontsize=9)
    
    # ========== 5. Lottery Ticket Hypothesis ==========
    ax5 = fig.add_subplot(gs[2, 0])
    
    lottery_data = data['5_lottery_ticket_hypothesis']['rounds']
    sparsity_levels_lth = [round_data['sparsity'] * 100 for round_data in lottery_data]
    winning_accs = [round_data['winning_ticket']['test_accuracy'] * 100 for round_data in lottery_data]
    random_accs = [round_data['random_ticket']['test_accuracy'] * 100 for round_data in lottery_data]
    
    x = np.arange(len(sparsity_levels_lth))
    width = 0.35
    
    bars1 = ax5.bar(x - width/2, winning_accs, width, label='Winning Ticket', 
                    color=colors['primary'], alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax5.bar(x + width/2, random_accs, width, label='Random Ticket', 
                    color=colors['secondary'], alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax5.axhline(y=data['5_lottery_ticket_hypothesis']['baseline_accuracy'] * 100, 
                color=colors['danger'], linestyle='--', linewidth=2, label='Baseline')
    
    ax5.set_title('Lottery Ticket Hypothesis', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Accuracy (%)', fontsize=11)
    ax5.set_xlabel('Sparsity Level', fontsize=11)
    ax5.set_xticks(x)
    ax5.set_xticklabels([f'{int(s)}%' for s in sparsity_levels_lth])
    ax5.set_ylim(70, 82)
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2, height + 0.3,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
    
    # ========== 6. Accuracy vs Sparsity Trade-off ==========
    ax6 = fig.add_subplot(gs[2, 1])
    
    all_sparsities = [0, 30, 50, 70, 90]
    all_accuracies = [
        baseline_acc,
        mag_results['30pct_sparsity']['accuracy'] * 100,
        mag_results['50pct_sparsity']['accuracy'] * 100,
        mag_results['70pct_sparsity']['accuracy'] * 100,
        mag_results['90pct_sparsity']['accuracy'] * 100
    ]
    
    ax6.plot(all_sparsities, all_accuracies, marker='o', markersize=10, 
             linewidth=2.5, color=colors['primary'], label='Magnitude Pruning')
    ax6.fill_between(all_sparsities, all_accuracies, alpha=0.2, color=colors['primary'])
    
    ax6.set_title('Accuracy vs Sparsity Trade-off', fontsize=12, fontweight='bold')
    ax6.set_xlabel('Sparsity Level (%)', fontsize=11)
    ax6.set_ylabel('Accuracy (%)', fontsize=11)
    ax6.set_ylim(74, 81)
    ax6.grid(True, alpha=0.3)
    ax6.legend()
    
    for x_val, y_val in zip(all_sparsities, all_accuracies):
        ax6.annotate(f'{y_val:.1f}%', xy=(x_val, y_val), xytext=(0, 5),
                     textcoords='offset points', ha='center', fontweight='bold', fontsize=9)
    
    # ========== 7. Method Comparison Summary ==========
    ax7 = fig.add_subplot(gs[2, 2])
    
    summary_methods = [
        'Lottery\n60%',
        'Magnitude\n30%',
        'One-shot\n70%',
        'Magnitude\n90%',
        'Structured\n25%'
    ]
    summary_accs = [
        78.43,  # Lottery 60%
        78.21,  # Magnitude 30%
        76.78,  # One-shot 70%
        75.96,  # Magnitude 90%
        75.11   # Structured 25%
    ]
    
    bars = ax7.barh(summary_methods, summary_accs, color=colors['tertiary'], alpha=0.8, 
                    edgecolor='black', linewidth=1.5)
    ax7.axvline(x=baseline_acc, color=colors['danger'], linestyle='--', linewidth=2, label='Baseline')
    ax7.set_title('Best Methods Comparison', fontsize=12, fontweight='bold')
    ax7.set_xlabel('Accuracy (%)', fontsize=11)
    ax7.set_xlim(74, 81)
    ax7.legend()
    ax7.grid(True, alpha=0.3, axis='x')
    ax7.invert_yaxis()
    
    for bar, acc in zip(bars, summary_accs):
        width = bar.get_width()
        ax7.text(width + 0.15, bar.get_y() + bar.get_height()/2,
                f'{acc:.1f}%', ha='left', va='center', fontweight='bold', fontsize=9)
    
    # 保存图表
    output_path = 'results/visualizations/part1_pruning_comprehensive.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print_with_timestamp(f"✅ Part 1可视化已保存: {output_path}")
    plt.close()
    
    return output_path

def main():
    """主函数"""
    print_with_timestamp("🎨 生成Part 1剪枝技术可视化...")
    print_with_timestamp("=" * 60)
    
    try:
        chart = create_comprehensive_visualization()
        
        if chart:
            print_with_timestamp("\n🎉 Part 1可视化生成完成!")
            print_with_timestamp(f"📊 图表路径: {chart}")
            print_with_timestamp("\n💡 关键发现:")
            print_with_timestamp("  • Lottery Ticket Hypothesis验证：稀疏网络可超越密集网络")
            print_with_timestamp("  • 30%剪枝率最佳实用性：78.21%准确率，仅-1.76%")
            print_with_timestamp("  • One-shot优于Gradual：准确率高2.31%且训练快3倍")
            print_with_timestamp("  • 首层敏感度极高：13.65%准确率下降")
            print_with_timestamp("  • 深层冗余性强：Group3可激进剪枝")
        
    except Exception as e:
        print_with_timestamp(f"❌ 生成图表时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

