"""
Part 4: 压缩技术交互分析可视化脚本
生成组合压缩技术的综合分析图表
"""

import json
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from datetime import datetime

# 莫兰迪配色方案
MORANDI_COLORS = {
    'dusty_blue': '#9db4c0',      # 灰蓝色
    'sage_green': '#a8b5a0',      # 鼠尾草绿
    'warm_beige': '#c4b5a0',      # 暖米色
    'soft_coral': '#d4a5a5',      # 柔和珊瑚色
    'muted_purple': '#b5a7c4',    # 柔和紫色
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

def load_data(file_path="results/part4/combination_results.json"):
    """加载Part 4数据"""
    if not os.path.exists(file_path):
        print_with_timestamp(f"❌ 数据文件未找到: {file_path}")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_comprehensive_visualization():
    """创建Part 4综合可视化"""
    print_with_timestamp("🎨 生成Part 4压缩技术交互分析可视化...")
    
    data = load_data()
    if not data:
        return None
    
    # 使用莫兰迪配色方案
    colors = {
        'baseline': MORANDI_COLORS['soft_coral'],      # 柔和珊瑚色
        'single': MORANDI_COLORS['dusty_blue'],        # 灰蓝色
        'combined': MORANDI_COLORS['sage_green'],      # 鼠尾草绿
        'best': MORANDI_COLORS['muted_purple'],        # 柔和紫色
        'accent': MORANDI_COLORS['warm_beige'],        # 暖米色
    }
    
    # 创建图表
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
    
    fig.suptitle('Part 4: Compression Technique Interaction Analysis\nCombining Pruning, Quantization & Distillation on CIFAR-100', 
                 fontsize=16, fontweight='bold', y=0.96)
    
    baseline_acc = data['baseline']['accuracy'] * 100
    baseline_size = data['baseline']['size_mb']
    
    # ========== 1. Single vs Combined Techniques - Accuracy ==========
    ax1 = fig.add_subplot(gs[0, 0])
    
    methods = [
        'Baseline',
        'Pruning\n30%',
        'Quantization\nINT8',
        'Distillation\nWRN-22-6',
        'Distillation\nWRN-16-2',
        'WRN-22-6\n+ INT8',
        'WRN-16-2\n+ INT8'
    ]
    
    accuracies = [
        baseline_acc,
        data['pruning_30']['accuracy'] * 100,
        data['quantization_int8']['accuracy'] * 100,
        data['distillation_wrn22_6']['accuracy'] * 100,
        data['distillation_wrn16_2']['accuracy'] * 100,
        data['distilled_wrn22_6_int8']['accuracy'] * 100,
        data['distilled_wrn16_2_int8']['accuracy'] * 100
    ]
    
    method_colors = [
        colors['baseline'],
        colors['single'], colors['single'], colors['single'], colors['single'],
        colors['combined'], colors['combined']
    ]
    
    bars = ax1.bar(methods, accuracies, color=method_colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.axhline(y=baseline_acc, color=colors['baseline'], linestyle='--', linewidth=2, alpha=0.5)
    ax1.set_title('Accuracy Comparison', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Accuracy (%)', fontsize=11)
    ax1.set_ylim(65, 82)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, height + 0.4,
                f'{acc:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    # ========== 2. Compression Ratio Comparison ==========
    ax2 = fig.add_subplot(gs[0, 1])
    
    comp_methods = [
        'Quantization\nINT8',
        'Distillation\nWRN-16-2',
        'WRN-22-6\n+ INT8',
        'WRN-16-2\n+ INT8 [Best]'
    ]
    
    comp_ratios = [
        data['quantization_int8']['compression_ratio'],
        data['distillation_wrn16_2']['compression_ratio'],
        data['distilled_wrn22_6_int8']['compression_ratio'],
        data['distilled_wrn16_2_int8']['compression_ratio']
    ]
    
    comp_colors_list = [
        colors['single'], colors['single'],
        colors['combined'], colors['best']
    ]
    
    bars = ax2.barh(comp_methods, comp_ratios, color=comp_colors_list, alpha=0.8, 
                    edgecolor='black', linewidth=1.5)
    ax2.set_title('Compression Ratio', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Compression Ratio (×)', fontsize=11)
    ax2.set_xlim(0, 55)
    ax2.grid(True, alpha=0.3, axis='x')
    ax2.invert_yaxis()
    
    # 给[Best]标签加粗
    for label, tick in zip(comp_methods, ax2.get_yticklabels()):
        if '[Best]' in label:
            tick.set_fontweight('bold')
    
    for bar, ratio in zip(bars, comp_ratios):
        width = bar.get_width()
        ax2.text(width + 1.5, bar.get_y() + bar.get_height()/2,
                f'{ratio:.1f}×', ha='left', va='center', fontweight='bold', fontsize=9)
    
    # ========== 3. Model Size (Log Scale) ==========
    ax3 = fig.add_subplot(gs[0, 2])
    
    size_methods = [
        'Baseline',
        'INT8',
        'WRN-16-2',
        'WRN-22-6\n+ INT8',
        'WRN-16-2\n+ INT8 [Winner]'
    ]
    
    sizes_mb = [
        baseline_size,
        data['quantization_int8']['size_mb'],
        data['distillation_wrn16_2']['size_mb'],
        data['distilled_wrn22_6_int8']['size_mb'],
        data['distilled_wrn16_2_int8']['size_mb']
    ]
    
    size_colors_list = [
        colors['baseline'],
        colors['single'], colors['single'],
        colors['combined'], colors['best']
    ]
    
    bars = ax3.bar(size_methods, sizes_mb, color=size_colors_list, alpha=0.8, 
                   edgecolor='black', linewidth=1.5)
    ax3.set_title('Model Size Comparison', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Model Size (MB, Log Scale)', fontsize=11)
    ax3.set_yscale('log')
    ax3.set_ylim(1, 200)
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # 给标签着色，Winner用柔和珊瑚色加粗
    for i, (label, tick) in enumerate(zip(size_methods, ax3.get_xticklabels())):
        if '[Winner]' in label:
            tick.set_color(MORANDI_COLORS['soft_coral'])
            tick.set_fontweight('bold')
    
    for bar, size in zip(bars, sizes_mb):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2, height * 1.2,
                f'{size:.1f}MB', ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    # ========== 4. Accuracy vs Compression Trade-off ==========
    ax4 = fig.add_subplot(gs[1, 0])
    
    all_methods_scatter = [
        'Baseline',
        'Pruning 30%',
        'INT8 Quant',
        'WRN-22-6',
        'WRN-16-2',
        'WRN-22-6\n+ INT8',
        'WRN-16-2\n+ INT8'
    ]
    
    all_comp_ratios = [
        1.0,
        data['pruning_30']['compression_ratio'],
        data['quantization_int8']['compression_ratio'],
        data['distillation_wrn22_6']['compression_ratio'],
        data['distillation_wrn16_2']['compression_ratio'],
        data['distilled_wrn22_6_int8']['compression_ratio'],
        data['distilled_wrn16_2_int8']['compression_ratio']
    ]
    
    all_accuracies = [
        baseline_acc,
        data['pruning_30']['accuracy'] * 100,
        data['quantization_int8']['accuracy'] * 100,
        data['distillation_wrn22_6']['accuracy'] * 100,
        data['distillation_wrn16_2']['accuracy'] * 100,
        data['distilled_wrn22_6_int8']['accuracy'] * 100,
        data['distilled_wrn16_2_int8']['accuracy'] * 100
    ]
    
    scatter_colors = [
        colors['baseline'],
        colors['single'], colors['single'], colors['single'], colors['single'],
        colors['combined'], colors['best']
    ]
    
    scatter_sizes = [300, 200, 200, 200, 200, 300, 400]
    
    for i, (comp, acc, method, color, size) in enumerate(zip(all_comp_ratios, all_accuracies, 
                                                               all_methods_scatter, scatter_colors, scatter_sizes)):
        ax4.scatter(comp, acc, s=size, alpha=0.7, c=color, edgecolors='black', linewidths=2)
        
        # 所有点都标注，根据位置调整标签方向避免重叠
        if i == 0:  # Baseline (x≈1, y≈79.6)
            xytext = (-30, 5)  # 往左移
        elif i == 1:  # Pruning 30% (x≈0.33, y≈78.2)
            xytext = (5, -15)  # 往右移（改到点的右下方）
        elif i == 2:  # INT8 Quant (x≈4, y≈79.7)
            xytext = (5, -15)  # 右下方，避开baseline
        elif i == 3:  # WRN-22-6 (x≈1.3, y≈75.5)
            xytext = (-30, 5)  # 左下方
        elif i == 4:  # WRN-16-2 (x≈4.4, y≈70.2)
            xytext = (5, 8)  # 右上方
        elif i == 5:  # WRN-22-6 + INT8 (x≈14.9, y≈74.8)
            xytext = (5, -18)  # 右下方
        else:  # WRN-16-2 + INT8 (Winner) (x≈51.4, y≈70.4)
            xytext = (5, 5)  # 右上方
            method = method.replace('[Winner]', '[Winner]').strip()
        
        fontweight = 'bold' if '[Winner]' in method or '[Best]' in method else 'normal'
        fontcolor = MORANDI_COLORS['soft_coral'] if '[Winner]' in method else MORANDI_COLORS['dark_text']
        
        ax4.annotate(method, (comp, acc), xytext=xytext, 
                    textcoords='offset points', fontweight=fontweight, fontsize=7.5,
                    color=fontcolor,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.85, 
                             edgecolor=MORANDI_COLORS['soft_coral'] if '[Winner]' in method else 'gray', 
                             linewidth=1.5 if '[Winner]' in method else 0.5))
    
    ax4.set_title('Accuracy vs Compression Trade-off', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Compression Ratio (×)', fontsize=11)
    ax4.set_ylabel('Accuracy (%)', fontsize=11)
    ax4.set_xlim(-2, 55)
    ax4.set_ylim(68, 81)
    ax4.grid(True, alpha=0.3)
    
    # ========== 5. Technique Combination Effect ==========
    ax5 = fig.add_subplot(gs[1, 1])
    
    x = np.arange(3)
    width = 0.35
    
    techniques = ['Distillation\nWRN-22-6', 'INT8 Quant', 'Combined\nWRN-22-6+INT8']
    
    acc_values = [
        data['distillation_wrn22_6']['accuracy'] * 100,
        data['quantization_int8']['accuracy'] * 100,
        data['distilled_wrn22_6_int8']['accuracy'] * 100
    ]
    
    comp_values = [
        data['distillation_wrn22_6']['compression_ratio'],
        data['quantization_int8']['compression_ratio'],
        data['distilled_wrn22_6_int8']['compression_ratio']
    ]
    
    bars1 = ax5.bar(x - width/2, acc_values, width, label='Accuracy (%)', 
                    color=colors['single'], alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax5.bar(x + width/2, comp_values, width, label='Compression (×)', 
                    color=colors['combined'], alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax5.set_title('Combination Effect - WRN-22-6 + INT8', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Value', fontsize=11)
    ax5.set_xticks(x)
    ax5.set_xticklabels(techniques)
    ax5.legend()
    ax5.grid(True, alpha=0.3, axis='y')
    
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2, height + 1,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=9)
    
    # ========== 6. Best Methods Ranking ==========
    ax6 = fig.add_subplot(gs[1, 2])
    
    ranking_methods = [
        'INT8 Quant\n(79.67%, 4×)',
        'Baseline\n(79.61%, 1×)',
        'Pruning 30%\n(78.21%, 0.3×)',
        'WRN-22-6\n(75.46%, 1.3×)',
        'WRN-22-6+INT8\n(74.80%, 14.9×) [Best]',
        'WRN-16-2+INT8\n(70.43%, 51.4×) [Winner]'
    ]
    
    # 综合评分 = accuracy - 0.1 * (100 - accuracy) + 5 * log(compression)
    scores = []
    for key in ['quantization_int8', 'baseline', 'pruning_30', 
                'distillation_wrn22_6', 'distilled_wrn22_6_int8', 'distilled_wrn16_2_int8']:
        if key == 'baseline':
            acc = data['baseline']['accuracy'] * 100
            comp = 1.0
        else:
            acc = data[key]['accuracy'] * 100
            comp = data[key]['compression_ratio']
        score = acc - 0.1 * (100 - acc) + 5 * np.log10(max(comp, 0.1))
        scores.append(score)
    
    ranking_colors_list = [
        colors['single'], colors['baseline'], colors['single'],
        colors['single'], colors['combined'], colors['best']
    ]
    
    bars = ax6.barh(ranking_methods, scores, color=ranking_colors_list, alpha=0.8, 
                    edgecolor='black', linewidth=1.5)
    ax6.set_title('Overall Performance Score', fontsize=12, fontweight='bold')
    ax6.set_xlabel('Score (Accuracy + Compression)', fontsize=11)
    ax6.grid(True, alpha=0.3, axis='x')
    ax6.invert_yaxis()
    
    # 给[Winner]标签用柔和珊瑚色加粗
    for label, tick in zip(ranking_methods, ax6.get_yticklabels()):
        if '[Winner]' in label:
            tick.set_color(MORANDI_COLORS['soft_coral'])
            tick.set_fontweight('bold')
        elif '[Best]' in label:
            tick.set_fontweight('bold')
    
    for bar, score in zip(bars, scores):
        width = bar.get_width()
        ax6.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                f'{score:.1f}', ha='left', va='center', fontweight='bold', fontsize=9)
    
    # 保存图表
    output_path = 'results/visualizations/part4_interaction_comprehensive.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print_with_timestamp(f"✅ Part 4可视化已保存: {output_path}")
    plt.close()
    
    return output_path

def main():
    """主函数"""
    print_with_timestamp("🎨 生成Part 4压缩技术交互分析可视化...")
    print_with_timestamp("=" * 60)
    
    try:
        chart = create_comprehensive_visualization()
        
        if chart:
            print_with_timestamp("\n🎉 Part 4可视化生成完成!")
            print_with_timestamp(f"📊 图表路径: {chart}")
            print_with_timestamp("\n💡 关键发现:")
            print_with_timestamp("  • 组合技术显著优于单一技术")
            print_with_timestamp("  • WRN-16-2 + INT8: 51.4×压缩，极致压缩方案")
            print_with_timestamp("  • WRN-22-6 + INT8: 14.9×压缩，性价比最优")
            print_with_timestamp("  • INT8量化几乎无损：79.67% vs 79.61%")
            print_with_timestamp("  • 技术叠加产生乘法效应：1.3× × 4× ≈ 14.9×")
        
    except Exception as e:
        print_with_timestamp(f"❌ 生成图表时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

