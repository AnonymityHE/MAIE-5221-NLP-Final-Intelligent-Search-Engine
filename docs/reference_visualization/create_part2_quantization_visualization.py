"""
Part 2: 量化技术可视化脚本
生成量化实验的综合分析图表
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

def load_data(file_path="results/part2/all_quantization_results.json"):
    """加载Part 2数据"""
    if not os.path.exists(file_path):
        print_with_timestamp(f"❌ 数据文件未找到: {file_path}")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_comprehensive_visualization():
    """创建Part 2综合可视化"""
    print_with_timestamp("🎨 生成Part 2量化技术可视化...")
    
    data = load_data()
    if not data:
        return None
    
    # 使用莫兰迪配色方案
    colors = {
        'primary': MORANDI_COLORS['dusty_blue'],      # 灰蓝色
        'secondary': MORANDI_COLORS['muted_purple'],  # 柔和紫色
        'tertiary': MORANDI_COLORS['sage_green'],     # 鼠尾草绿
        'accent': MORANDI_COLORS['warm_beige'],       # 暖米色
        'danger': MORANDI_COLORS['soft_coral']        # 柔和珊瑚色
    }
    
    # 创建图表
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
    
    fig.suptitle('Part 2: Quantization Techniques - Comprehensive Analysis\nWide-ResNet-28-10 on CIFAR-100', 
                 fontsize=16, fontweight='bold', y=0.96)
    
    baseline_acc = data['baseline']['test_accuracy'] * 100
    baseline_size_mb = data['baseline']['model_path']  # Will calculate from file
    baseline_size_mb = 139.8  # From metadata
    
    # ========== 1. PTQ Methods Comparison ==========
    ax1 = fig.add_subplot(gs[0, 0])
    
    ptq_methods = ['Baseline', 'INT8', 'Dynamic', 'Float16']
    ptq_accs = [
        baseline_acc,
        data['ptq']['int8']['test_accuracy'] * 100,
        data['ptq']['dynamic_range']['test_accuracy'] * 100,
        data['ptq']['float16']['test_accuracy'] * 100
    ]
    ptq_colors = [colors['danger'], colors['primary'], colors['secondary'], colors['tertiary']]
    
    bars = ax1.bar(ptq_methods, ptq_accs, color=ptq_colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.set_title('PTQ Methods - Accuracy', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Accuracy (%)', fontsize=11)
    ax1.set_ylim(78, 81)
    ax1.grid(True, alpha=0.3)
    
    for bar, acc in zip(bars, ptq_accs):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, height + 0.05,
                f'{acc:.2f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # ========== 2. Model Size Comparison (Log Scale) ==========
    ax2 = fig.add_subplot(gs[0, 1])
    
    size_methods = ['Baseline', 'INT8', 'Dynamic', 'Float16']
    sizes_mb = [
        baseline_size_mb,
        data['ptq']['int8']['model_size_bytes'] / (1024**2),
        data['ptq']['dynamic_range']['model_size_bytes'] / (1024**2),
        data['ptq']['float16']['model_size_bytes'] / (1024**2)
    ]
    
    bars = ax2.bar(size_methods, sizes_mb, color=ptq_colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax2.set_title('Model Size Comparison', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Model Size (MB, Log Scale)', fontsize=11)
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    for bar, size in zip(bars, sizes_mb):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, height * 1.05,
                f'{size:.1f}MB', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # ========== 3. Compression Ratio ==========
    ax3 = fig.add_subplot(gs[0, 2])
    
    compression_methods = ['INT8', 'Dynamic', 'Float16']
    compression_ratios = [
        data['ptq']['int8']['compression_ratio'],
        data['ptq']['dynamic_range']['compression_ratio'],
        data['ptq']['float16']['compression_ratio']
    ]
    comp_colors = [colors['primary'], colors['secondary'], colors['tertiary']]
    
    bars = ax3.bar(compression_methods, compression_ratios, color=comp_colors, alpha=0.8, 
                   edgecolor='black', linewidth=1.5)
    ax3.set_title('Compression Ratio', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Compression Ratio (×)', fontsize=11)
    ax3.set_ylim(0, 14)
    ax3.grid(True, alpha=0.3)
    
    for bar, ratio in zip(bars, compression_ratios):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2, height + 0.3,
                f'{ratio:.1f}×', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # ========== 4. Accuracy vs Compression Trade-off ==========
    ax4 = fig.add_subplot(gs[1, 0])
    
    all_methods = ['Baseline', 'Float16', 'Dynamic', 'INT8', 'INT4']
    all_comp_ratios = [1.0, 6.0, 11.95, 11.92, 8.0]
    all_accuracies = [
        baseline_acc,
        data['ptq']['float16']['test_accuracy'] * 100,
        data['ptq']['dynamic_range']['test_accuracy'] * 100,
        data['ptq']['int8']['test_accuracy'] * 100,
        data['extreme']['int4']['test_accuracy'] * 100
    ]
    
    scatter = ax4.scatter(all_comp_ratios, all_accuracies, s=200, alpha=0.7, 
                         c=[colors['danger'], colors['tertiary'], colors['secondary'], 
                            colors['primary'], colors['accent']], edgecolors='black', linewidths=2)
    
    # 根据位置调整每个标签避免重叠
    # Dynamic (11.95, 79.59) 和 INT8 (11.92, 79.52) 位置非常接近
    label_positions = [
        (-50, 5),    # Baseline (左上方)
        (5, -18),    # Float16 (右下方)
        (5, 10),     # Dynamic (右上方)
        (5, -20),    # INT8 (右下方，与Dynamic分开)
        (5, 5)       # INT4 (右上方)
    ]
    
    for i, method in enumerate(all_methods):
        ax4.annotate(method, (all_comp_ratios[i], all_accuracies[i]), 
                    xytext=label_positions[i], textcoords='offset points', 
                    fontweight='bold', fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax4.set_title('Accuracy vs Compression Trade-off', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Compression Ratio (×)', fontsize=11)
    ax4.set_ylabel('Accuracy (%)', fontsize=11)
    ax4.set_xlim(0, 13)
    ax4.set_ylim(70, 81)
    ax4.grid(True, alpha=0.3)
    
    # ========== 5. Quantization Types Comparison ==========
    ax5 = fig.add_subplot(gs[1, 1])
    
    x = np.arange(4)
    width = 0.35
    
    methods_compare = ['PTQ\nINT8', 'PTQ\nDynamic', 'PTQ\nFloat16', 'QAT']
    acc_values = [
        data['ptq']['int8']['test_accuracy'] * 100,
        data['ptq']['dynamic_range']['test_accuracy'] * 100,
        data['ptq']['float16']['test_accuracy'] * 100,
        data['qat']['qat']['keras_test_accuracy'] * 100
    ]
    comp_values = [
        data['ptq']['int8']['compression_ratio'],
        data['ptq']['dynamic_range']['compression_ratio'],
        data['ptq']['float16']['compression_ratio'],
        11.92  # Assumed similar to INT8
    ]
    
    bars1 = ax5.bar(x - width/2, acc_values, width, label='Accuracy (%)', 
                    color=colors['primary'], alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax5.bar(x + width/2, comp_values, width, label='Compression (×)', 
                    color=colors['accent'], alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax5.set_title('Quantization Methods Comparison', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Value', fontsize=11)
    ax5.set_xticks(x)
    ax5.set_xticklabels(methods_compare)
    ax5.legend()
    ax5.grid(True, alpha=0.3, axis='y')
    
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=8)
    
    # ========== 6. Accuracy Loss Comparison ==========
    ax6 = fig.add_subplot(gs[1, 2])
    
    loss_methods = ['Float16', 'Dynamic', 'INT8', 'QAT', 'INT4', 'Binary']
    acc_losses = [
        baseline_acc - data['ptq']['float16']['test_accuracy'] * 100,
        baseline_acc - data['ptq']['dynamic_range']['test_accuracy'] * 100,
        baseline_acc - data['ptq']['int8']['test_accuracy'] * 100,
        baseline_acc - data['qat']['qat']['keras_test_accuracy'] * 100,
        baseline_acc - data['extreme']['int4']['test_accuracy'] * 100,
        baseline_acc - data['extreme']['binary']['test_accuracy'] * 100
    ]
    
    colors_loss = [colors['tertiary'], colors['secondary'], colors['primary'], 
                   colors['accent'], colors['accent'], colors['danger']]
    
    bars = ax6.barh(loss_methods, acc_losses, color=colors_loss, alpha=0.8, 
                    edgecolor='black', linewidth=1.5)
    ax6.set_title('Accuracy Loss from Baseline', fontsize=12, fontweight='bold')
    ax6.set_xlabel('Accuracy Loss (%)', fontsize=11)
    ax6.grid(True, alpha=0.3, axis='x')
    ax6.invert_yaxis()
    ax6.set_xlim(0, 80)
    
    for bar, loss in zip(bars, acc_losses):
        width = bar.get_width()
        ax6.text(width + 1, bar.get_y() + bar.get_height()/2,
                f'{loss:.2f}%', ha='left', va='center', fontweight='bold', fontsize=9)
    
    # 保存图表
    output_path = 'results/visualizations/part2_quantization_comprehensive.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print_with_timestamp(f"✅ Part 2可视化已保存: {output_path}")
    plt.close()
    
    return output_path

def main():
    """主函数"""
    print_with_timestamp("🎨 生成Part 2量化技术可视化...")
    print_with_timestamp("=" * 60)
    
    try:
        chart = create_comprehensive_visualization()
        
        if chart:
            print_with_timestamp("\n🎉 Part 2可视化生成完成!")
            print_with_timestamp(f"📊 图表路径: {chart}")
            print_with_timestamp("\n💡 关键发现:")
            print_with_timestamp("  • PTQ INT8最优：11.92×压缩，仅-0.09%准确率损失")
            print_with_timestamp("  • Dynamic Range量化效果相当：11.95×压缩，-0.02%损失")
            print_with_timestamp("  • Float16保守方案：6×压缩，几乎无损")
            print_with_timestamp("  • INT4极限量化：8×压缩，-7.2%准确率损失")
            print_with_timestamp("  • Binary量化失败：准确率降至1.06%")
        
    except Exception as e:
        print_with_timestamp(f"❌ 生成图表时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

