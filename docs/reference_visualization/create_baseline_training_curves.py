"""
Baseline模型（WideResNet-28-10）训练曲线可视化
使用莫兰迪配色方案
CIFAR-100 数据集
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
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


def smooth_curve(data, window_size=5):
    """使用移动平均平滑曲线"""
    if len(data) < window_size:
        return data
    # 使用uniform_filter1d进行移动平均
    smoothed = uniform_filter1d(data, size=window_size, mode='nearest')
    return smoothed


def load_training_data():
    """加载训练数据（优先使用JSON，备选CSV）"""
    base_dir = Path(__file__).parent.parent
    
    # 尝试加载JSON
    json_path = base_dir / 'results/baseline/training_history.json'
    csv_path = base_dir / 'logs/baseline/training_20251112_124947.csv'
    
    history = None
    source = None
    
    if json_path.exists():
        with open(json_path, 'r') as f:
            history = json.load(f)
        source = 'JSON'
        print(f"✓ 从JSON加载了 {len(history['accuracy'])} 个epochs数据")
    elif csv_path.exists():
        df = pd.read_csv(csv_path)
        history = {
            'accuracy': df['accuracy'].tolist(),
            'loss': df['loss'].tolist(),
            'val_accuracy': df['val_accuracy'].tolist(),
            'val_loss': df['val_loss'].tolist()
        }
        source = 'CSV'
        print(f"✓ 从CSV加载了 {len(history['accuracy'])} 个epochs数据")
    else:
        raise FileNotFoundError("未找到训练数据文件（JSON或CSV）")
    
    return history, source


def create_baseline_training_curves(history, data_source):
    """创建baseline训练曲线图"""
    print(f"🎨 正在生成 Baseline (WideResNet-28-10) 训练曲线图...")
    
    # 创建莫兰迪风格图表布局
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor(MORANDI_COLORS['background'])
    
    # 设置子图背景色
    for ax in [ax1, ax2]:
        ax.set_facecolor('#fafafa')
    
    # 莫兰迪风格标题设计
    fig.suptitle('Baseline Model Training Progress - WideResNet-28-10', 
                 fontsize=22, fontweight='300', y=0.85, color=MORANDI_COLORS['dark_text'])
    fig.text(0.5, 0.78, f'CIFAR-100 Classification Task (100 epochs)', 
             ha='center', fontsize=14, color=MORANDI_COLORS['medium_text'], style='italic')
    
    epochs = range(1, len(history['accuracy']) + 1)
    
    # 1. 准确率曲线 - 现代渐变设计
    train_acc = [acc * 100 for acc in history['accuracy']]
    val_acc = [acc * 100 for acc in history['val_accuracy']]
    
    # 应用平滑处理（减少抖动）
    train_acc_smooth = smooth_curve(train_acc, window_size=5)
    val_acc_smooth = smooth_curve(val_acc, window_size=5)
    
    # 绘制莫兰迪风格填充区域（使用平滑后的数据）
    ax1.fill_between(epochs, 0, train_acc_smooth, alpha=0.15, color=MORANDI_COLORS['dusty_blue'], label='Training Range')
    ax1.fill_between(epochs, 0, val_acc_smooth, alpha=0.1, color=MORANDI_COLORS['sage_green'], label='Validation Range')
    
    # 绘制主线条 - 减少数据点密度
    marker_step = max(1, len(epochs) // 10)  # 显示约10个标记点
    marker_epochs = list(epochs[::marker_step])
    marker_train_acc = [train_acc_smooth[i] for i in range(0, len(train_acc_smooth), marker_step)]
    marker_val_acc = [val_acc_smooth[i] for i in range(0, len(val_acc_smooth), marker_step)]
    
    # 先绘制无标记的完整线条（减小线宽，使用平滑数据）
    line1 = ax1.plot(epochs, train_acc_smooth, color=MORANDI_COLORS['dusty_blue'], linewidth=2.0, 
                     label='Training Accuracy', alpha=0.95)
    line2 = ax1.plot(epochs, val_acc_smooth, color=MORANDI_COLORS['sage_green'], linewidth=2.0, 
                     label='Validation Accuracy', alpha=0.95)
    
    # 再绘制稀疏的标记点
    ax1.scatter(marker_epochs, marker_train_acc, color=MORANDI_COLORS['dusty_blue'], s=25, 
                facecolor='white', edgecolor=MORANDI_COLORS['dusty_blue'], linewidth=1.5, zorder=5)
    ax1.scatter(marker_epochs, marker_val_acc, color=MORANDI_COLORS['sage_green'], s=25, 
                facecolor='white', edgecolor=MORANDI_COLORS['sage_green'], linewidth=1.5, zorder=5)
    
    # 设置子图样式
    ax1.set_title('Accuracy Evolution', fontsize=16, fontweight='400', 
                  color=MORANDI_COLORS['dark_text'], pad=15)
    ax1.set_xlabel('Training Epoch', fontsize=13, color=MORANDI_COLORS['medium_text'], fontweight='400')
    ax1.set_ylabel('Model Accuracy (%)', fontsize=13, color=MORANDI_COLORS['medium_text'], fontweight='400')
    
    # 设置Y轴范围
    ax1.set_ylim(0, 90)
    
    ax1.grid(True, alpha=0.3, color=MORANDI_COLORS['light_text'], linestyle='-', linewidth=0.8)
    
    # 美化图例
    legend1 = ax1.legend(loc='lower right', fontsize=11, framealpha=0.95, 
                        fancybox=True, shadow=False, borderpad=1,
                        facecolor='white', edgecolor=MORANDI_COLORS['light_text'])
    
    # 添加成就标注
    final_acc = history['accuracy'][-1] * 100
    final_val_acc = history['val_accuracy'][-1] * 100
    best_val_acc = max(history['val_accuracy']) * 100
    best_val_epoch = history['val_accuracy'].index(max(history['val_accuracy'])) + 1
    
    # 最佳表现线
    ax1.axhline(y=best_val_acc, color=MORANDI_COLORS['soft_coral'], linestyle=':', alpha=0.8, linewidth=2)
    ax1.text(min(10, len(epochs)//4), best_val_acc + 1.5, f'Peak: {best_val_acc:.1f}% (Epoch {best_val_epoch})', 
             fontweight='400', color=MORANDI_COLORS['soft_coral'], fontsize=10,
             bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor=MORANDI_COLORS['soft_coral'], alpha=0.8))
    
    # 最终表现标注
    ax1.scatter([len(epochs)], [final_val_acc], color=MORANDI_COLORS['warm_beige'], s=100, 
                zorder=5, edgecolor='white', linewidth=2)
    ax1.text(len(epochs)-min(8, len(epochs)//5), final_val_acc + 2, f'Final: {final_val_acc:.1f}%', 
             ha='right', va='bottom', fontweight='400', color=MORANDI_COLORS['warm_beige'], fontsize=11,
             bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor=MORANDI_COLORS['warm_beige'], alpha=0.9))
    
    # 2. 损失曲线 - 现代渐变设计
    train_loss = history['loss']
    val_loss = history['val_loss']
    
    # 应用平滑处理（减少抖动）
    train_loss_smooth = smooth_curve(train_loss, window_size=5)
    val_loss_smooth = smooth_curve(val_loss, window_size=5)
    
    # 绘制莫兰迪风格填充区域（使用平滑后的数据）
    ax2.fill_between(epochs, 0, train_loss_smooth, alpha=0.15, color=MORANDI_COLORS['soft_coral'], label='Training Loss Range')
    ax2.fill_between(epochs, 0, val_loss_smooth, alpha=0.1, color=MORANDI_COLORS['muted_purple'], label='Validation Loss Range')
    
    # 绘制主线条 - 减少数据点密度
    marker_train_loss = [train_loss_smooth[i] for i in range(0, len(train_loss_smooth), marker_step)]
    marker_val_loss = [val_loss_smooth[i] for i in range(0, len(val_loss_smooth), marker_step)]
    
    # 先绘制无标记的完整线条（减小线宽，使用平滑数据）
    line3 = ax2.plot(epochs, train_loss_smooth, color=MORANDI_COLORS['soft_coral'], linewidth=2.0, 
                     label='Training Loss', alpha=0.95)
    line4 = ax2.plot(epochs, val_loss_smooth, color=MORANDI_COLORS['muted_purple'], linewidth=2.0, 
                     label='Validation Loss', alpha=0.95)
    
    # 再绘制稀疏的标记点
    ax2.scatter(marker_epochs, marker_train_loss, color=MORANDI_COLORS['soft_coral'], s=25, 
                facecolor='white', edgecolor=MORANDI_COLORS['soft_coral'], linewidth=1.5, zorder=5)
    ax2.scatter(marker_epochs, marker_val_loss, color=MORANDI_COLORS['muted_purple'], s=25, 
                facecolor='white', edgecolor=MORANDI_COLORS['muted_purple'], linewidth=1.5, zorder=5)
    
    # 设置子图样式
    ax2.set_title('Loss Convergence', fontsize=16, fontweight='400', 
                  color=MORANDI_COLORS['dark_text'], pad=15)
    ax2.set_xlabel('Training Epoch', fontsize=13, color=MORANDI_COLORS['medium_text'], fontweight='400')
    ax2.set_ylabel('Model Loss', fontsize=13, color=MORANDI_COLORS['medium_text'], fontweight='400')
    ax2.grid(True, alpha=0.3, color=MORANDI_COLORS['light_text'], linestyle='-', linewidth=0.8)
    
    # 美化图例
    legend2 = ax2.legend(loc='upper right', fontsize=11, framealpha=0.95, 
                        fancybox=True, shadow=False, borderpad=1,
                        facecolor='white', edgecolor=MORANDI_COLORS['light_text'])
    
    # 添加损失收敛标注
    final_loss = history['loss'][-1]
    final_val_loss = history['val_loss'][-1]
    min_val_loss = min(history['val_loss'])
    min_val_loss_epoch = history['val_loss'].index(min_val_loss) + 1
    
    # 最佳损失线
    ax2.axhline(y=min_val_loss, color=MORANDI_COLORS['accent_green'], linestyle=':', alpha=0.8, linewidth=2)
    ax2.text(min(10, len(epochs)//4), min_val_loss + 0.15, f'Best: {min_val_loss:.3f} (Epoch {min_val_loss_epoch})', 
             fontweight='400', color=MORANDI_COLORS['accent_green'], fontsize=10,
             bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor=MORANDI_COLORS['accent_green'], alpha=0.8))
    
    # 最终损失标注
    ax2.scatter([len(epochs)], [final_val_loss], color=MORANDI_COLORS['warm_beige'], s=100, 
                zorder=5, edgecolor='white', linewidth=2)
    ax2.text(len(epochs)-min(8, len(epochs)//5), final_val_loss + 0.2, f'Final: {final_val_loss:.3f}', 
             ha='right', va='bottom', fontweight='400', color=MORANDI_COLORS['warm_beige'], fontsize=11,
             bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor=MORANDI_COLORS['warm_beige'], alpha=0.9))
    
    # 添加整体装饰元素
    # 在图表之间添加分隔线
    fig.text(0.5, 0.5, '|', ha='center', va='center', fontsize=30, color=MORANDI_COLORS['light_text'], alpha=0.3)
    
    # 调整布局 - 为标题留出更合适的空间
    plt.tight_layout(rect=[0, 0.03, 1, 0.85])
    
    # 保存高质量图表
    base_dir = Path(__file__).parent.parent
    output_path = base_dir / 'results/visualizations/baseline_training_curves.png'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor=MORANDI_COLORS['background'], 
                edgecolor='none', pad_inches=0.2)
    print(f"✅ Baseline训练曲线图已保存: {output_path.name}")
    plt.close()
    
    return output_path, history


def main():
    """主函数"""
    print("🎨 生成Baseline模型训练曲线图...")
    print("=" * 70)
    
    try:
        # 加载训练数据
        print("\n📊 加载训练数据...")
        print("-" * 70)
        history, data_source = load_training_data()
        
        # 生成训练曲线
        print("\n📈 生成训练曲线...")
        print("-" * 70)
        chart_path, history = create_baseline_training_curves(history, data_source)
        
        # 显示总结
        print("\n" + "=" * 70)
        print("🎉 训练曲线图生成完成!")
        print("=" * 70)
        print("\n📊 训练统计:")
        print(f"\n  ✅ 模型: WideResNet-28-10")
        print(f"     数据集: CIFAR-100")
        print(f"     训练轮数: {len(history['accuracy'])} epochs")
        print(f"     数据来源: {data_source}")
        print(f"\n  📈 准确率:")
        print(f"     最终训练准确率: {history['accuracy'][-1]*100:.2f}%")
        print(f"     最终验证准确率: {history['val_accuracy'][-1]*100:.2f}%")
        print(f"     最佳验证准确率: {max(history['val_accuracy'])*100:.2f}%")
        best_epoch = history['val_accuracy'].index(max(history['val_accuracy'])) + 1
        print(f"     最佳Epoch: {best_epoch}")
        print(f"\n  📉 损失:")
        print(f"     最终训练损失: {history['loss'][-1]:.4f}")
        print(f"     最终验证损失: {history['val_loss'][-1]:.4f}")
        print(f"     最低验证损失: {min(history['val_loss']):.4f}")
        best_loss_epoch = history['val_loss'].index(min(history['val_loss'])) + 1
        print(f"     最低损失Epoch: {best_loss_epoch}")
        
        print(f"\n📂 保存位置: {chart_path}")
        print("\n💡 提示: 使用以下命令查看:")
        print(f"   open {chart_path}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 生成图表时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


