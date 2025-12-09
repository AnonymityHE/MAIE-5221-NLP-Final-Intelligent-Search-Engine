"""
Part 3: 知识蒸馏可视化脚本
生成知识蒸馏实验的综合分析图表
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

def load_data(file_path="results/part3/part3_unified_results.json"):
    """加载Part 3数据"""
    if not os.path.exists(file_path):
        print_with_timestamp(f"❌ 数据文件未找到: {file_path}")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_comprehensive_visualization():
    """创建Part 3综合可视化"""
    print_with_timestamp("🎨 生成Part 3知识蒸馏可视化...")
    
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
    
    fig.suptitle('Part 3: Knowledge Distillation - Comprehensive Analysis\nTeacher: WRN-40-2 → Students on CIFAR-100', 
                 fontsize=16, fontweight='bold', y=0.96)
    
    teacher_acc = data['teacher_model']['test_accuracy'] * 100
    teacher_size = data['teacher_model']['model_size_mb']
    
    # ========== 1. Teacher vs Students Accuracy ==========
    ax1 = fig.add_subplot(gs[0, 0])
    
    models = ['Teacher\nWRN-40-2', 'Student\nWRN-22-6', 'Student\nWRN-16-2']
    accuracies = [
        teacher_acc,
        data['experiments']['exp5_improved_student']['test_accuracy'] * 100,
        data['experiments']['exp2_standard_kd']['test_accuracy'] * 100
    ]
    model_colors = [colors['danger'], colors['primary'], colors['secondary']]
    
    bars = ax1.bar(models, accuracies, color=model_colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.set_title('Teacher vs Students Accuracy', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Accuracy (%)', fontsize=11)
    ax1.set_ylim(60, 82)
    ax1.grid(True, alpha=0.3)
    
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                f'{acc:.2f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # ========== 2. Model Size Comparison (Log Scale) ==========
    ax2 = fig.add_subplot(gs[0, 1])
    
    sizes_mb = [
        teacher_size,
        data['experiments']['exp5_improved_student']['model_size_mb'],
        data['experiments']['exp2_standard_kd']['model_size_mb']
    ]
    
    bars = ax2.bar(models, sizes_mb, color=model_colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax2.set_title('Model Size Comparison', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Model Size (MB, Log Scale)', fontsize=11)
    ax2.set_yscale('log')
    ax2.set_ylim(5, 200)
    ax2.grid(True, alpha=0.3)
    
    for bar, size in zip(bars, sizes_mb):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, height * 1.15,
                f'{size:.1f}MB', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # ========== 3. Compression Ratio ==========
    ax3 = fig.add_subplot(gs[0, 2])
    
    student_names = ['WRN-22-6', 'WRN-16-2']
    compression_ratios = [
        data['experiments']['exp5_improved_student']['compression_ratio'],
        data['experiments']['exp2_standard_kd']['compression_ratio']
    ]
    
    bars = ax3.bar(student_names, compression_ratios, color=[colors['primary'], colors['secondary']], 
                   alpha=0.8, edgecolor='black', linewidth=1.5)
    ax3.set_title('Compression Ratio', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Compression Ratio (×)', fontsize=11)
    ax3.set_ylim(0, 15)
    ax3.grid(True, alpha=0.3)
    
    for bar, ratio in zip(bars, compression_ratios):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2, height + 0.3,
                f'{ratio:.2f}×', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # ========== 4. Temperature Optimization Results ==========
    ax4 = fig.add_subplot(gs[1, 0])
    
    temp_results = data['experiments']['exp1_temperature_optimization']['temperature_results']
    temperatures = [r['temperature'] for r in temp_results]
    val_accs = [r['val_accuracy'] * 100 for r in temp_results]
    
    ax4.plot(temperatures, val_accs, marker='o', markersize=8, linewidth=2.5, 
             color=colors['tertiary'], label='Validation Accuracy')
    ax4.fill_between(temperatures, val_accs, alpha=0.2, color=colors['tertiary'])
    
    optimal_temp = data['experiments']['exp1_temperature_optimization']['optimal_temperature']
    optimal_acc = data['experiments']['exp1_temperature_optimization']['optimal_val_accuracy'] * 100
    ax4.scatter([optimal_temp], [optimal_acc], s=200, color=colors['danger'], 
                marker='*', edgecolors='black', linewidths=2, label=f'Optimal (T={optimal_temp})', zorder=5)
    
    ax4.set_title('Temperature Optimization', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Temperature', fontsize=11)
    ax4.set_ylabel('Validation Accuracy (%)', fontsize=11)
    ax4.set_ylim(59, 63)
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    # ========== 5. Distillation Methods Comparison ==========
    ax5 = fig.add_subplot(gs[1, 1])
    
    methods = [
        'Improved\nWRN-22-6',
        'Standard KD\nWRN-16-2',
        'Attention\nTransfer',
        'Progressive\nDistillation'
    ]
    method_accs = [
        data['experiments']['exp5_improved_student']['test_accuracy'] * 100,
        data['experiments']['exp2_standard_kd']['test_accuracy'] * 100,
        data['experiments']['exp3_attention_transfer']['test_accuracy'] * 100,
        data['experiments']['exp4_progressive_distillation']['test_accuracy'] * 100
    ]
    method_colors_list = [colors['primary'], colors['secondary'], colors['accent'], colors['tertiary']]
    
    bars = ax5.barh(methods, method_accs, color=method_colors_list, alpha=0.8, 
                    edgecolor='black', linewidth=1.5)
    ax5.axvline(x=teacher_acc, color=colors['danger'], linestyle='--', linewidth=2, label='Teacher')
    ax5.set_title('Distillation Methods Comparison', fontsize=12, fontweight='bold')
    ax5.set_xlabel('Test Accuracy (%)', fontsize=11)
    ax5.set_xlim(60, 81)
    ax5.legend()
    ax5.grid(True, alpha=0.3, axis='x')
    ax5.invert_yaxis()
    
    for bar, acc in zip(bars, method_accs):
        width = bar.get_width()
        ax5.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                f'{acc:.1f}%', ha='left', va='center', fontweight='bold', fontsize=9)
    
    # ========== 6. Accuracy vs Compression Trade-off ==========
    ax6 = fig.add_subplot(gs[1, 2])
    
    all_comp_ratios = [
        1.0,  # Teacher
        data['experiments']['exp5_improved_student']['compression_ratio'],
        data['experiments']['exp2_standard_kd']['compression_ratio'],
        data['experiments']['exp3_attention_transfer']['compression_ratio'],
        data['experiments']['exp4_progressive_distillation']['compression_ratio']
    ]
    all_accuracies = [
        teacher_acc,
        data['experiments']['exp5_improved_student']['test_accuracy'] * 100,
        data['experiments']['exp2_standard_kd']['test_accuracy'] * 100,
        data['experiments']['exp3_attention_transfer']['test_accuracy'] * 100,
        data['experiments']['exp4_progressive_distillation']['test_accuracy'] * 100
    ]
    all_methods_scatter = ['Teacher', 'Improved\nWRN-22-6', 'Standard KD', 'Attention', 'Progressive']
    scatter_colors = [colors['danger'], colors['primary'], colors['secondary'], colors['accent'], colors['tertiary']]
    
    for i, (comp, acc, method, color) in enumerate(zip(all_comp_ratios, all_accuracies, all_methods_scatter, scatter_colors)):
        ax6.scatter(comp, acc, s=250, alpha=0.7, c=color, edgecolors='black', linewidths=2)
        ax6.annotate(method, (comp, acc), xytext=(5, -5 if i % 2 == 0 else 5), 
                    textcoords='offset points', fontweight='bold', fontsize=8,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    
    ax6.set_title('Accuracy vs Compression Trade-off', fontsize=12, fontweight='bold')
    ax6.set_xlabel('Compression Ratio (×)', fontsize=11)
    ax6.set_ylabel('Accuracy (%)', fontsize=11)
    ax6.set_xlim(0, 15)
    ax6.set_ylim(60, 82)
    ax6.grid(True, alpha=0.3)
    
    # 保存图表
    output_path = 'results/visualizations/part3_distillation_comprehensive.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print_with_timestamp(f"✅ Part 3可视化已保存: {output_path}")
    plt.close()
    
    return output_path

def main():
    """主函数"""
    print_with_timestamp("🎨 生成Part 3知识蒸馏可视化...")
    print_with_timestamp("=" * 60)
    
    try:
        chart = create_comprehensive_visualization()
        
        if chart:
            print_with_timestamp("\n🎉 Part 3可视化生成完成!")
            print_with_timestamp(f"📊 图表路径: {chart}")
            print_with_timestamp("\n💡 关键发现:")
            print_with_timestamp("  • 最优温度T=5.22：提供最佳知识传递效果")
            print_with_timestamp("  • WRN-22-6表现最佳：75.46%准确率，3.75×压缩")
            print_with_timestamp("  • 标准KD效果优异：70.15%准确率，13.17×压缩")
            print_with_timestamp("  • 注意力转移未提升：66.21%准确率，不如标准KD")
            print_with_timestamp("  • 学生容量关键：容量比决定性能上限")
        
    except Exception as e:
        print_with_timestamp(f"❌ 生成图表时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

