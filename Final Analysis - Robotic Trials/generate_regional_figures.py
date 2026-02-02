#!/usr/bin/env python3
"""
Generate improved regional distribution visualizations.
Compare 5-year periods instead of single years.
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
OUT_DIR = BASE_DIR / 'figures_elegant'

# ARGOS Theme Colors (matching generate_elegant_figures.py)
COLORS = {
    'primary': '#5C5C5C',
    'secondary': '#8C8C8C',
    'light': '#B8B8B8',
    'accent': '#3D3D3D',
    'highlight': '#6B7280',
    'background': '#FAFAFA',
    'text': '#374151',
    'grid': '#E5E7EB',
    'early': '#B8B8B8',  # Light grey for early period
    'late': '#5C5C5C',   # Dark grey for late period
}

plt.rcParams.update({
    'figure.facecolor': COLORS['background'],
    'axes.facecolor': COLORS['background'],
    'savefig.facecolor': COLORS['background'],
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica Neue', 'Arial', 'DejaVu Sans'],
    'font.size': 12,
    'axes.titlesize': 16,
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,
    'axes.labelcolor': COLORS['text'],
    'axes.edgecolor': COLORS['light'],
    'axes.linewidth': 0.8,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'xtick.color': COLORS['text'],
    'ytick.color': COLORS['text'],
    'legend.fontsize': 10,
    'legend.frameon': False,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': False,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})


def load_data():
    df = pd.read_csv(DATA_DIR / 'per_year_metrics.tsv', sep='\t')
    return df


def calculate_period_averages(df):
    """Calculate weighted averages for 5-year periods."""
    early = df[(df['year'] >= 2001) & (df['year'] <= 2005)]
    late = df[(df['year'] >= 2021) & (df['year'] <= 2025)]
    
    # Weighted average by number of trials
    def weighted_avg(period_df, col):
        return (period_df[col] * period_df['total_trials']).sum() / period_df['total_trials'].sum()
    
    regions = ['share_north_america', 'share_europe', 'share_asia', 
               'share_oceania', 'share_latin_america', 'share_middle_east', 'share_africa']
    
    early_avg = {r: weighted_avg(early, r) * 100 for r in regions}
    late_avg = {r: weighted_avg(late, r) * 100 for r in regions}
    
    return early_avg, late_avg


def fig_regional_comparison(df):
    """Bar chart comparing 2001-2005 vs 2021-2025."""
    print("Creating regional comparison (5-year periods)...")
    
    early_avg, late_avg = calculate_period_averages(df)
    
    # All regions
    regions = ['North America', 'Europe', 'Asia', 'Middle East', 'Latin America', 'Oceania', 'Africa']
    region_keys = ['share_north_america', 'share_europe', 'share_asia', 
                   'share_middle_east', 'share_latin_america', 'share_oceania', 'share_africa']
    
    early_vals = [early_avg[k] for k in region_keys]
    late_vals = [late_avg[k] for k in region_keys]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(regions))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, early_vals, width, label='2001–2005', 
                   color=COLORS['light'], edgecolor=COLORS['secondary'], linewidth=1.2)
    bars2 = ax.bar(x + width/2, late_vals, width, label='2021–2025', 
                   color=COLORS['primary'], edgecolor=COLORS['accent'], linewidth=1.2)
    
    # Value labels
    for bar, val in zip(bars1, early_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
               f'{val:.0f}%', ha='center', va='bottom', fontsize=11, 
               fontweight='bold', color=COLORS['secondary'])
    
    for bar, val in zip(bars2, late_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
               f'{val:.0f}%', ha='center', va='bottom', fontsize=11, 
               fontweight='bold', color=COLORS['accent'])
    
    ax.set_ylabel('Share of Clinical Trials (%)', fontweight='medium')
    ax.set_title('Regional Distribution Shift\n(5-Year Period Comparison)', pad=15, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(regions, fontweight='medium')
    ax.set_ylim(0, 60)
    plt.xticks(rotation=30, ha='right')
    ax.legend(loc='upper right', framealpha=0.95)
    ax.yaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig3_regional_shift.png', dpi=300, facecolor='white')
    plt.close(fig)
    print("  Saved: fig3_regional_shift.png")


def fig_slope_chart(df):
    """Slope chart showing regional trajectory."""
    print("Creating slope chart...")
    
    early_avg, late_avg = calculate_period_averages(df)
    
    # All regions
    regions = ['North America', 'Europe', 'Asia', 'Middle East', 'Latin America', 'Oceania', 'Africa']
    region_keys = ['share_north_america', 'share_europe', 'share_asia',
                   'share_middle_east', 'share_latin_america', 'share_oceania', 'share_africa']
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Grey theme colors - gradient from light to dark
    colors = {
        'North America': '#9CA3AF', 
        'Europe': '#4B5563', 
        'Asia': '#1F2937',
        'Middle East': '#6B7280',
        'Latin America': '#374151',
        'Oceania': '#D1D5DB',
        'Africa': '#111827'
    }
    
    for region, key in zip(regions, region_keys):
        early = early_avg[key]
        late = late_avg[key]
        
        color = colors[region]
        
        # Draw slope line
        ax.plot([0, 1], [early, late], color=color, linewidth=3, alpha=0.8)
        
        # Draw endpoints
        ax.scatter([0], [early], color=color, s=120, zorder=5, edgecolor='white', linewidth=2)
        ax.scatter([1], [late], color=color, s=120, zorder=5, edgecolor='white', linewidth=2)
        
        # Labels
        ax.text(-0.08, early, f'{region}\n{early:.0f}%', ha='right', va='center', 
               fontsize=11, fontweight='bold', color=color)
        ax.text(1.08, late, f'{region}\n{late:.0f}%', ha='left', va='center',
               fontsize=11, fontweight='bold', color=color)
    
    ax.set_xlim(-0.3, 1.3)
    ax.set_ylim(0, 60)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['2001–2005', '2021–2025'], fontsize=13, fontweight='bold')
    ax.set_ylabel('Share of Clinical Trials (%)', fontweight='medium')
    ax.set_title('Regional Shift Over 25 Years', pad=15, fontweight='bold', fontsize=16)
    
    # Remove spines
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_color(COLORS['grid'])
    ax.yaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax.set_axisbelow(True)
    ax.tick_params(bottom=False)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig3b_slope_chart.png', dpi=300, facecolor='white')
    plt.close(fig)
    print("  Saved: fig3b_slope_chart.png")


def fig_change_chart(df):
    """Horizontal bar showing absolute change."""
    print("Creating change chart...")
    
    early_avg, late_avg = calculate_period_averages(df)
    
    # All regions, sorted by change
    all_regions = ['Asia', 'Europe', 'Latin America', 'Oceania', 'Middle East', 'Africa', 'North America']
    all_keys = ['share_asia', 'share_europe', 'share_latin_america', 'share_oceania', 
                'share_middle_east', 'share_africa', 'share_north_america']
    
    changes = [late_avg[k] - early_avg[k] for k in all_keys]
    
    # Sort by change
    sorted_data = sorted(zip(all_regions, changes), key=lambda x: x[1], reverse=True)
    regions = [x[0] for x in sorted_data]
    changes = [x[1] for x in sorted_data]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Grey theme - dark for positive, light for negative
    colors = [COLORS['accent'] if c > 0 else COLORS['light'] for c in changes]
    
    bars = ax.barh(regions, changes, color=colors, edgecolor='white', linewidth=1.5, height=0.6)
    
    # Add value labels
    for bar, change, region in zip(bars, changes, regions):
        x_pos = change + (1 if change > 0 else -1)
        ha = 'left' if change > 0 else 'right'
        sign = '+' if change > 0 else ''
        ax.text(x_pos, bar.get_y() + bar.get_height()/2, 
               f'{sign}{change:.0f} pp', ha=ha, va='center',
               fontsize=12, fontweight='bold', color=COLORS['accent'])
    
    ax.axvline(x=0, color=COLORS['accent'], linewidth=1.5)
    ax.set_xlabel('Change in Share (percentage points)', fontweight='medium')
    ax.set_title('Regional Share Change: 2001–2005 vs 2021–2025', pad=15, fontweight='bold')
    ax.set_xlim(-25, 35)
    ax.xaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax.set_axisbelow(True)
    
    # Add annotations
    ax.text(0.98, 0.02, 'pp = percentage points', transform=ax.transAxes,
           fontsize=9, style='italic', color=COLORS['secondary'], ha='right')
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig3c_change_chart.png', dpi=300, facecolor='white')
    plt.close(fig)
    print("  Saved: fig3c_change_chart.png")


def main():
    print("Generating regional figures...\n")
    df = load_data()
    
    # Print period averages for reference
    early, late = calculate_period_averages(df)
    print("Period averages:")
    print(f"  2001-2005: NA={early['share_north_america']:.1f}%, EU={early['share_europe']:.1f}%, Asia={early['share_asia']:.1f}%")
    print(f"  2021-2025: NA={late['share_north_america']:.1f}%, EU={late['share_europe']:.1f}%, Asia={late['share_asia']:.1f}%")
    print()
    
    fig_regional_comparison(df)
    fig_slope_chart(df)
    fig_change_chart(df)
    
    print(f"\n✓ Regional figures saved to: {OUT_DIR}")


if __name__ == '__main__':
    main()
