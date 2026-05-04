#!/usr/bin/env python3
"""
Create a summary infographic of collaboration findings.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / 'figures_elegant'

# ARGOS Theme Colors
COLORS = {
    'primary': '#374151',
    'secondary': '#6B7280',
    'light': '#9CA3AF',
    'lighter': '#D1D5DB',
    'background': '#FAFAFA',
    'text': '#374151',
    'accent': '#374151',
    'lmic': '#7C9CBF',
    'highlight': '#EF4444',
}

plt.rcParams.update({
    'figure.facecolor': COLORS['background'],
    'axes.facecolor': COLORS['background'],
    'savefig.facecolor': COLORS['background'],
    'font.family': 'sans-serif',
})


def create_collaboration_summary():
    """Create a summary infographic of collaboration patterns."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # =====================
    # Panel A: Collaboration Types (Pie)
    # =====================
    ax1 = axes[0, 0]
    sizes = [81, 19]
    labels = ['HIC-HIC\n(81%)', 'HIC-LMIC\n(19%)']
    colors = [COLORS['primary'], COLORS['light']]
    
    wedges, texts = ax1.pie(sizes, labels=labels, colors=colors, startangle=90,
                            wedgeprops=dict(edgecolor='white', linewidth=2),
                            textprops={'fontsize': 11, 'fontweight': 'bold'})
    
    ax1.set_title('A. Collaboration Types', fontweight='bold', fontsize=12, pad=10)
    
    # Add note about LMIC-LMIC
    ax1.text(0.5, -0.15, 'LMIC-LMIC: 0%', transform=ax1.transAxes, 
             ha='center', fontsize=10, style='italic', color=COLORS['highlight'])
    
    # =====================
    # Panel B: Top Collaborating Countries
    # =====================
    ax2 = axes[0, 1]
    countries = ['UK', 'USA', 'Italy', 'Germany', 'Japan', 'S. Korea', 'China', 'France']
    counts = [92, 79, 35, 29, 26, 21, 21, 19]
    colors_bar = [COLORS['primary']]*6 + [COLORS['lmic']] + [COLORS['primary']]
    
    bars = ax2.barh(range(len(countries)), counts, color=colors_bar, 
                    edgecolor='white', linewidth=0.5, height=0.7)
    ax2.set_yticks(range(len(countries)))
    ax2.set_yticklabels(countries, fontsize=10)
    ax2.invert_yaxis()
    ax2.set_xlabel('Collaborative Trials', fontsize=10)
    ax2.set_title('B. Most Collaborative Countries', fontweight='bold', fontsize=12, pad=10)
    
    # Add value labels
    for bar, count in zip(bars, counts):
        ax2.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                str(count), va='center', fontsize=9)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=COLORS['primary'], label='HIC'),
        mpatches.Patch(facecolor=COLORS['lmic'], label='LMIC'),
    ]
    ax2.legend(handles=legend_elements, loc='lower right', fontsize=9)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    # =====================
    # Panel C: LMIC Partners in HIC-LMIC Collaborations
    # =====================
    ax3 = axes[1, 0]
    lmic_countries = ['China', 'Brazil', 'India', 'Egypt', 'Iran']
    lmic_counts = [21, 9, 7, 3, 1]
    
    bars = ax3.barh(range(len(lmic_countries)), lmic_counts, color=COLORS['lmic'],
                    edgecolor='white', linewidth=0.5, height=0.6)
    ax3.set_yticks(range(len(lmic_countries)))
    ax3.set_yticklabels(lmic_countries, fontsize=10)
    ax3.invert_yaxis()
    ax3.set_xlabel('HIC-LMIC Collaborations', fontsize=10)
    ax3.set_title('C. LMIC Countries in Collaborations', fontweight='bold', fontsize=12, pad=10)
    
    # Add value labels and percentages
    total_lmic = sum(lmic_counts)
    for bar, count in zip(bars, lmic_counts):
        pct = 100 * count / total_lmic
        ax3.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f'{count} ({pct:.0f}%)', va='center', fontsize=9)
    
    # Highlight China dominance
    ax3.text(0.5, -0.12, 'China = 51% of all LMIC collaboration', 
             transform=ax3.transAxes, ha='center', fontsize=10, 
             style='italic', color=COLORS['highlight'])
    
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    
    # =====================
    # Panel D: Key Statistics Table
    # =====================
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    # Create table data
    table_data = [
        ['Total collaborative trials', '200'],
        ['HIC-HIC collaborations', '162 (81%)'],
        ['HIC-LMIC collaborations', '38 (19%)'],
        ['LMIC-LMIC collaborations', '0 (0%)'],
        ['', ''],
        ['Top partnership', 'UK-USA (25)'],
        ['Top HIC-LMIC pair', 'China-USA (7)'],
        ['', ''],
        ['HIC-LMIC trend (25 yrs)', '0% → 21%'],
    ]
    
    # Draw table
    table = ax4.table(cellText=table_data,
                      colLabels=['Metric', 'Value'],
                      cellLoc='left',
                      loc='center',
                      colWidths=[0.55, 0.35])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)
    
    # Style header
    for i in range(2):
        table[(0, i)].set_facecolor(COLORS['primary'])
        table[(0, i)].set_text_props(color='white', fontweight='bold')
    
    # Alternate row colors
    for i in range(1, len(table_data) + 1):
        for j in range(2):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#F3F4F6')
            else:
                table[(i, j)].set_facecolor('white')
    
    ax4.set_title('D. Key Statistics', fontweight='bold', fontsize=12, pad=10, y=0.95)
    
    # Main title
    fig.suptitle('International Collaboration in Robotic Surgery Trials\n200 Multi-Country Studies (2001-2025)', 
                 fontweight='bold', fontsize=14, y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(OUT_DIR / 'fig_collab_summary.png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("Saved: fig_collab_summary.png")


def create_equity_summary():
    """Create a summary figure combining income trends and collaboration equity."""
    fig = plt.figure(figsize=(14, 8))
    
    # Create grid
    gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.3)
    
    # =====================
    # Panel A: Three-way split (HIC-only, HIC-LMIC, LMIC-only)
    # =====================
    ax1 = fig.add_subplot(gs[0, :2])
    
    # Load three-way split data
    import pandas as pd
    split_df = pd.read_csv(BASE_DIR / 'data' / 'three_way_split.csv')
    
    years = split_df['year'].values
    hic_only = split_df['hic_only'].values
    hic_lmic = split_df['hic_lmic_collab'].values
    lmic_only = split_df['lmic_only'].values
    
    # Stacked area chart (HIC on bottom, HIC-LMIC middle, LMIC on top)
    ax1.stackplot(years, hic_only, hic_lmic, lmic_only, 
                  colors=[COLORS['primary'], '#8B5CF6', COLORS['lmic']],
                  labels=['HIC-only', 'HIC-LMIC Collab', 'LMIC-only'],
                  alpha=0.85,
                  edgecolor='white', linewidth=0.5)
    
    ax1.set_xlabel('Year', fontweight='medium')
    ax1.set_ylabel('Share of Trials (%)', fontweight='medium')
    ax1.set_title('A. Trial Distribution by Income Level Over Time', fontweight='bold', fontsize=11)
    ax1.set_xlim(2001, 2025)
    ax1.set_ylim(0, 100)
    ax1.legend(loc='center right', framealpha=0.95, fontsize=9)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.yaxis.grid(True, linestyle='-', alpha=0.2, color='white')
    
    # Legend is sufficient - no additional text labels needed
    
    # =====================
    # Panel B: Collaboration Types (Donut)
    # Based on per-year data: ~363 multi-country trials (16.2% of 2,237)
    # Sample analysis shows: 79% HIC-HIC, 21% HIC-LMIC
    # =====================
    ax2 = fig.add_subplot(gs[0, 2])
    
    sizes = [79, 21]
    colors = [COLORS['primary'], COLORS['light']]
    
    wedges, texts, autotexts = ax2.pie(sizes, colors=colors, autopct='%1.0f%%',
                                        startangle=90, pctdistance=0.75,
                                        wedgeprops=dict(width=0.5, edgecolor='white'))
    
    for autotext in autotexts:
        autotext.set_fontweight('bold')
        autotext.set_fontsize(11)
    
    ax2.text(0, 0, 'n≈363', ha='center', va='center', fontsize=11, fontweight='bold')
    ax2.set_title('B. Collaboration Types', fontweight='bold', fontsize=11, pad=10)
    
    # Legend
    legend_labels = ['HIC-HIC', 'HIC-LMIC']
    ax2.legend(wedges, legend_labels, loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=2)
    
    # =====================
    # Panel C: Key Equity Metrics (Clean Table)
    # =====================
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.axis('off')
    
    # Table data - focus on LMIC breakdown (not shown in Panel A)
    table_data = [
        ['LMIC by Income Level:', '', '', ''],
        ['  Upper Middle', '6%', '22%', '+16pp'],
        ['  Lower Middle', '1%', '2%', '+1pp'],
        ['  Low Income', '0%', '0%', '—'],
        ['', '', '', ''],
        ['Key Metrics:', '', '', ''],
        ['  Countries with trials', '10', '27', '+17'],
        ['  LMIC countries', '2', '12', '+10'],
    ]
    
    col_labels = ['Metric', '2001-05', '2021-25', 'Δ']
    
    table = ax3.table(cellText=table_data,
                      colLabels=col_labels,
                      cellLoc='center',
                      loc='center',
                      colWidths=[0.42, 0.18, 0.18, 0.18])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.1, 1.6)
    
    # Style header row
    for i in range(4):
        table[(0, i)].set_facecolor(COLORS['primary'])
        table[(0, i)].set_text_props(color='white', fontweight='bold')
    
    # Style data rows
    for i in range(1, len(table_data) + 1):
        for j in range(4):
            cell = table[(i, j)]
            cell.set_facecolor('white' if i % 2 == 1 else '#F9FAFB')
            # Color the change column
            if j == 3:
                text = table_data[i-1][3]
                if '+' in text:
                    cell.set_text_props(color='#059669', fontweight='bold')
                elif '-' in text:
                    cell.set_text_props(color='#059669', fontweight='bold')  # HIC decrease is good
                elif text == '—':
                    cell.set_text_props(color=COLORS['highlight'])
            # Left-align metric column
            if j == 0:
                cell._loc = 'left'
                # Style section header
                if 'Breakdown' in table_data[i-1][0]:
                    cell.set_text_props(fontweight='bold', style='italic')
    
    ax3.set_title('C. 25-Year Change', fontweight='bold', fontsize=11, y=0.95)
    
    # =====================
    # Panel D: The China Effect
    # =====================
    ax4 = fig.add_subplot(gs[1, 1])
    
    categories = ['Upper\nMiddle', 'Lower\nMiddle', 'Low\nIncome']
    values = [22.4, 2.3, 0.0]
    colors_bar = [COLORS['secondary'], COLORS['light'], COLORS['lighter']]
    
    bars = ax4.bar(categories, values, color=colors_bar, edgecolor='white', width=0.6)
    ax4.set_ylabel('Share of Trials (%)', fontweight='medium')
    ax4.set_title('D. LMIC Breakdown (2021-25)', fontweight='bold', fontsize=11)
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    
    # Add value labels
    for bar, val in zip(bars, values):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}%', ha='center', fontsize=10, fontweight='bold')
    
    # Annotation about China
    ax4.text(0.5, -0.18, 'China = 90% of Upper Middle category', 
             transform=ax4.transAxes, ha='center', fontsize=9, style='italic', color=COLORS['highlight'])
    
    # =====================
    # Panel E: LMIC in Collaborations
    # =====================
    ax5 = fig.add_subplot(gs[1, 2])
    
    countries = ['China', 'Brazil', 'India', 'Egypt', 'Other']
    values = [21, 9, 7, 3, 1]
    
    wedges, texts, autotexts = ax5.pie(values, labels=countries, colors=[COLORS['secondary'], 
                                        COLORS['light'], '#A8B5C4', '#C4CDD8', COLORS['lighter']],
                                        autopct='%1.0f%%', startangle=90,
                                        wedgeprops=dict(edgecolor='white', linewidth=1))
    
    for autotext in autotexts:
        autotext.set_fontsize(9)
    for text in texts:
        text.set_fontsize(9)
    
    ax5.set_title('E. LMIC Collaboration Partners', fontweight='bold', fontsize=11, pad=10)
    
    # Main title
    fig.suptitle('Global Equity in Robotic Surgery Research\nA 25-Year Analysis of Clinical Trials', 
                 fontweight='bold', fontsize=14, y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(OUT_DIR / 'fig_equity_summary.png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("Saved: fig_equity_summary.png")


def main():
    print("Creating summary figures...\n")
    create_collaboration_summary()
    create_equity_summary()
    print(f"\n✓ Summary figures saved to: {OUT_DIR}")


if __name__ == '__main__':
    main()
