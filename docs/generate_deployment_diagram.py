#!/usr/bin/env python3
"""Generate Docker Compose deployment architecture diagram."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Morandi color palette
COLORS = {
    'frontend': '#7B8FA1',      # Morandi blue-gray
    'backend': '#9CAFAA',       # Morandi sage green
    'milvus': '#C5A880',        # Morandi camel
    'minio': '#B4869F',         # Morandi dusty rose
    'etcd': '#A7C4BC',          # Morandi mint
    'docker': '#8EACCD',        # Morandi sky blue
    'external': '#D4A5A5',      # Morandi coral
    'text': '#2D3436',          # Dark text
    'arrow': '#636E72',         # Arrow color
    'bg': '#FAFAFA',            # Background
}

def draw_rounded_box(ax, x, y, width, height, text, color, fontsize=10, subtext=None):
    """Draw a rounded rectangle with text."""
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.03,rounding_size=0.1",
        facecolor=color,
        edgecolor='white',
        linewidth=2,
        alpha=0.9
    )
    ax.add_patch(box)
    
    if subtext:
        ax.text(x + width/2, y + height*0.6, text,
               ha='center', va='center', fontsize=fontsize,
               fontweight='bold', color=COLORS['text'])
        ax.text(x + width/2, y + height*0.3, subtext,
               ha='center', va='center', fontsize=fontsize-2,
               color=COLORS['text'], style='italic')
    else:
        ax.text(x + width/2, y + height/2, text,
               ha='center', va='center', fontsize=fontsize,
               fontweight='bold', color=COLORS['text'])

def draw_arrow(ax, start, end, color=None, style='->', bidirectional=False):
    """Draw an arrow between two points."""
    if color is None:
        color = COLORS['arrow']
    
    arrow = FancyArrowPatch(
        start, end,
        arrowstyle=style,
        color=color,
        linewidth=1.5,
        mutation_scale=15,
        connectionstyle="arc3,rad=0"
    )
    ax.add_patch(arrow)

def main():
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor(COLORS['bg'])
    fig.patch.set_facecolor(COLORS['bg'])
    
    # Title
    ax.text(7, 9.5, 'Jude Deployment Architecture', 
           ha='center', va='center', fontsize=16, fontweight='bold',
           color=COLORS['text'])
    
    # === User Layer ===
    ax.text(7, 8.8, 'User Layer', ha='center', fontsize=11, 
           color=COLORS['text'], style='italic')
    
    # Browser
    draw_rounded_box(ax, 5.5, 7.8, 3, 0.8, 'Web Browser', COLORS['frontend'],
                    subtext='Chrome/Safari')
    
    # === Frontend Layer ===
    ax.add_patch(FancyBboxPatch((0.5, 6.2), 6, 1.4, boxstyle="round,pad=0.02",
                                facecolor=COLORS['docker'], alpha=0.15,
                                edgecolor=COLORS['docker'], linewidth=2, linestyle='--'))
    ax.text(3.5, 7.4, 'Cloudflare Pages', ha='center', fontsize=10, 
           color=COLORS['docker'], fontweight='bold')
    
    draw_rounded_box(ax, 1, 6.4, 2.5, 0.9, 'React App', COLORS['frontend'],
                    subtext='Vite + TailwindCSS')
    draw_rounded_box(ax, 4, 6.4, 2, 0.9, 'Static Assets', COLORS['frontend'])
    
    # === Backend Layer ===
    ax.add_patch(FancyBboxPatch((7.5, 5.0), 6, 3.4, boxstyle="round,pad=0.02",
                                facecolor=COLORS['backend'], alpha=0.15,
                                edgecolor=COLORS['backend'], linewidth=2, linestyle='--'))
    ax.text(10.5, 8.2, 'Local Server', ha='center', fontsize=10, 
           color=COLORS['backend'], fontweight='bold')
    
    draw_rounded_box(ax, 8, 7.0, 2.5, 0.9, 'FastAPI', COLORS['backend'],
                    subtext='Uvicorn ASGI')
    draw_rounded_box(ax, 11, 7.0, 2, 0.9, 'Agent System', COLORS['backend'])
    draw_rounded_box(ax, 8, 5.8, 2.5, 0.9, 'RAG Pipeline', COLORS['backend'])
    draw_rounded_box(ax, 11, 5.8, 2, 0.9, 'LLM Clients', COLORS['backend'])
    draw_rounded_box(ax, 9.5, 5.2, 2, 0.5, 'Speech (TTS/STT)', COLORS['backend'], fontsize=9)
    
    # === Docker Compose Layer ===
    ax.add_patch(FancyBboxPatch((0.5, 1.5), 9, 3.2, boxstyle="round,pad=0.02",
                                facecolor=COLORS['docker'], alpha=0.15,
                                edgecolor=COLORS['docker'], linewidth=2, linestyle='--'))
    ax.text(5, 4.5, 'Docker Compose Network', ha='center', fontsize=10, 
           color=COLORS['docker'], fontweight='bold')
    
    # Milvus
    draw_rounded_box(ax, 1, 3.2, 2.5, 0.9, 'Milvus', COLORS['milvus'],
                    subtext='Vector Database')
    # MinIO
    draw_rounded_box(ax, 4, 3.2, 2.5, 0.9, 'MinIO', COLORS['minio'],
                    subtext='Object Storage')
    # etcd
    draw_rounded_box(ax, 7, 3.2, 2, 0.9, 'etcd', COLORS['etcd'],
                    subtext='Metadata')
    
    # Volumes
    draw_rounded_box(ax, 1, 1.8, 2, 0.7, 'milvus_data', COLORS['milvus'], fontsize=9)
    draw_rounded_box(ax, 3.5, 1.8, 2, 0.7, 'minio_data', COLORS['minio'], fontsize=9)
    draw_rounded_box(ax, 6, 1.8, 2, 0.7, 'etcd_data', COLORS['etcd'], fontsize=9)
    
    # === External APIs ===
    ax.add_patch(FancyBboxPatch((10, 1.5), 3.5, 3.2, boxstyle="round,pad=0.02",
                                facecolor=COLORS['external'], alpha=0.15,
                                edgecolor=COLORS['external'], linewidth=2, linestyle='--'))
    ax.text(11.75, 4.5, 'External APIs', ha='center', fontsize=10, 
           color=COLORS['external'], fontweight='bold')
    
    draw_rounded_box(ax, 10.25, 3.5, 1.5, 0.6, 'HKGAI', COLORS['external'], fontsize=9)
    draw_rounded_box(ax, 12, 3.5, 1.25, 0.6, 'Doubao', COLORS['external'], fontsize=9)
    draw_rounded_box(ax, 10.25, 2.7, 1.5, 0.6, 'Tavily', COLORS['external'], fontsize=9)
    draw_rounded_box(ax, 12, 2.7, 1.25, 0.6, 'wttr.in', COLORS['external'], fontsize=9)
    draw_rounded_box(ax, 10.25, 1.9, 1.5, 0.6, 'Yahoo Fin', COLORS['external'], fontsize=9)
    draw_rounded_box(ax, 12, 1.9, 1.25, 0.6, 'Edge TTS', COLORS['external'], fontsize=9)
    
    # === Arrows ===
    # Browser to Frontend
    draw_arrow(ax, (7, 7.8), (3.5, 7.3))
    
    # Browser to Backend (API)
    draw_arrow(ax, (7, 7.8), (9.25, 7.9))
    
    # Frontend to Backend (dotted - CORS)
    ax.annotate('', xy=(9.25, 6.85), xytext=(6.5, 6.85),
               arrowprops=dict(arrowstyle='->', color=COLORS['arrow'], 
                              linestyle='--', linewidth=1.5))
    ax.text(7.9, 7.05, 'CORS', fontsize=8, color=COLORS['arrow'], style='italic')
    
    # Backend to Docker services
    draw_arrow(ax, (9.25, 5.8), (2.25, 4.1))
    draw_arrow(ax, (9.25, 5.8), (5.25, 4.1))
    
    # Backend to External APIs
    draw_arrow(ax, (12, 5.8), (11.75, 4.1))
    
    # Docker services to volumes
    draw_arrow(ax, (2, 3.2), (2, 2.5), style='-')
    draw_arrow(ax, (5, 3.2), (4.5, 2.5), style='-')
    draw_arrow(ax, (8, 3.2), (7, 2.5), style='-')
    
    # Port labels
    ax.text(7.8, 8.3, ':5173', fontsize=8, color=COLORS['frontend'], fontweight='bold')
    ax.text(9.7, 8.3, ':5555', fontsize=8, color=COLORS['backend'], fontweight='bold')
    ax.text(2.8, 3.0, ':19530', fontsize=7, color=COLORS['milvus'])
    ax.text(5.8, 3.0, ':9000', fontsize=7, color=COLORS['minio'])
    ax.text(8.2, 3.0, ':2379', fontsize=7, color=COLORS['etcd'])
    
    # Legend
    legend_items = [
        ('Frontend (Cloudflare)', COLORS['frontend']),
        ('Backend (Local)', COLORS['backend']),
        ('Docker Services', COLORS['docker']),
        ('External APIs', COLORS['external']),
    ]
    
    for i, (label, color) in enumerate(legend_items):
        ax.add_patch(FancyBboxPatch((0.5 + i*3.3, 0.3), 0.4, 0.4,
                                   boxstyle="round,pad=0.02",
                                   facecolor=color, alpha=0.7))
        ax.text(1.0 + i*3.3, 0.5, label, fontsize=8, va='center', color=COLORS['text'])
    
    plt.tight_layout()
    plt.savefig('visualizations/deployment_architecture.png', 
               dpi=150, bbox_inches='tight', 
               facecolor=COLORS['bg'], edgecolor='none')
    plt.close()
    print("✅ Deployment architecture diagram saved!")

if __name__ == '__main__':
    main()

