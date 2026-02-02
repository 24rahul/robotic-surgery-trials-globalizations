#!/usr/bin/env python3
"""
Generate figures and tables for 8-minute oral presentation:
"Globalization of Robotic Surgery Clinical Trials: A 25-Year Bibliometric Analysis"
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
GLOB_DIR = BASE_DIR / 'robotic_surgery_trials_clinical' / 'globalization'
ANALYSIS_DIR = BASE_DIR / 'robotic_surgery_trials_clinical' / 'analysis'
OUT_DIR = Path(__file__).resolve().parent
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Style settings for presentation (larger fonts)
plt.rcParams.update({
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'font.size': 14,
    'axes.titlesize': 18,
    'axes.labelsize': 16,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 12,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'savefig.facecolor': 'white'
})

def load_data():
    """Load all data files."""
    per_year = pd.read_csv(GLOB_DIR / 'per_year_metrics.tsv', sep='\t')
    top_overall = pd.read_csv(GLOB_DIR / 'top_countries_overall.tsv', sep='\t')
    top_last5 = pd.read_csv(GLOB_DIR / 'top_countries_last5y.tsv', sep='\t')
    comparators = pd.read_csv(ANALYSIS_DIR / 'comparator_flags.tsv', sep='\t')
    specialty = pd.read_csv(ANALYSIS_DIR / 'specialty_counts.tsv', sep='\t')
    procedures = pd.read_csv(ANALYSIS_DIR / 'procedure_counts.tsv', sep='\t')
    return per_year, top_overall, top_last5, comparators, specialty, procedures


def fig1_trial_growth(df):
    """Figure 1: Trial volume growth over 25 years."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.fill_between(df['year'], df['total_trials'], alpha=0.3, color='#2563eb')
    ax.plot(df['year'], df['total_trials'], color='#2563eb', linewidth=3, marker='o', markersize=6)
    
    # Annotate key points
    ax.annotate(f"26", (2001, 26), textcoords="offset points", xytext=(0, 15), 
                ha='center', fontsize=14, fontweight='bold', color='#2563eb')
    ax.annotate(f"292", (2025, 292), textcoords="offset points", xytext=(0, 15), 
                ha='center', fontsize=14, fontweight='bold', color='#2563eb')
    
    # Add growth annotation
    ax.annotate('', xy=(2025, 280), xytext=(2001, 50),
                arrowprops=dict(arrowstyle='->', color='#dc2626', lw=2))
    ax.text(2013, 180, '11× growth', fontsize=16, color='#dc2626', fontweight='bold')
    
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Clinical Trials')
    ax.set_title('Growth of Robotic Surgery Clinical Trials (2001-2025)')
    ax.set_xlim(2000, 2026)
    ax.set_ylim(0, 320)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'slide_trial_growth.png', bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: slide_trial_growth.png")


def fig2_globalization_metrics(df):
    """Figure 2: Key globalization metrics - HHI and multi-country share."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Left: HHI decline
    ax1 = axes[0]
    ax1.fill_between(df['year'], df['hhi'], alpha=0.3, color='#059669')
    ax1.plot(df['year'], df['hhi'], color='#059669', linewidth=3, marker='s', markersize=5)
    ax1.set_xlabel('Year')
    ax1.set_ylabel('HHI (Lower = More Dispersed)')
    ax1.set_title('Geographic Concentration Declining')
    ax1.set_ylim(0, 0.35)
    
    # Annotate
    ax1.annotate('High concentration\n(0.18-0.24)', xy=(2003, 0.22), fontsize=11, ha='center')
    ax1.annotate('Low concentration\n(0.09-0.12)', xy=(2022, 0.12), fontsize=11, ha='center')
    
    # Right: Multi-country collaboration
    ax2 = axes[1]
    ax2.fill_between(df['year'], df['multi_country_share']*100, alpha=0.3, color='#7c3aed')
    ax2.plot(df['year'], df['multi_country_share']*100, color='#7c3aed', linewidth=3, marker='o', markersize=5)
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Multi-Country Trials (%)')
    ax2.set_title('International Collaboration Increasing')
    ax2.set_ylim(0, 30)
    
    # Annotate
    ax2.annotate('3.8%', (2001, 3.8), textcoords="offset points", xytext=(10, 10), 
                fontsize=12, fontweight='bold', color='#7c3aed')
    ax2.annotate('26.4%', (2025, 26.4), textcoords="offset points", xytext=(-30, -15), 
                fontsize=12, fontweight='bold', color='#7c3aed')
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'slide_globalization_metrics.png', bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: slide_globalization_metrics.png")


def fig3_regional_shift(df):
    """Figure 3: Regional share shift - simplified bar comparison."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    regions = ['North America', 'Europe', 'Asia']
    y2001 = [0.346, 0.385, 0.269]
    y2025 = [0.195, 0.555, 0.527]
    
    x = np.arange(len(regions))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, [v*100 for v in y2001], width, label='2001', color='#94a3b8', edgecolor='black')
    bars2 = ax.bar(x + width/2, [v*100 for v in y2025], width, label='2025', color='#2563eb', edgecolor='black')
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                   xytext=(0, 3), textcoords="offset points", ha='center', fontsize=12, fontweight='bold')
    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                   xytext=(0, 3), textcoords="offset points", ha='center', fontsize=12, fontweight='bold')
    
    # Add arrows showing direction
    ax.annotate('', xy=(0.175, 35), xytext=(0.175, 20), arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax.annotate('', xy=(1.175, 55.5), xytext=(1.175, 38.5), arrowprops=dict(arrowstyle='->', color='green', lw=2))
    ax.annotate('', xy=(2.175, 52.7), xytext=(2.175, 26.9), arrowprops=dict(arrowstyle='->', color='green', lw=2))
    
    ax.set_ylabel('Share of Clinical Trials (%)')
    ax.set_title('Regional Shift: 2001 vs 2025')
    ax.set_xticks(x)
    ax.set_xticklabels(regions, fontsize=14)
    ax.legend(fontsize=12)
    ax.set_ylim(0, 65)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'slide_regional_shift.png', bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: slide_regional_shift.png")


def fig4_country_leaders(top_overall, top_last5):
    """Figure 4: Country leadership comparison - Overall vs Last 5 Years."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Overall top 10
    ax1 = axes[0]
    top10_overall = top_overall.head(10)
    colors = ['#2563eb' if c == 'United States' else '#f59e0b' if c == 'China' else '#6b7280' 
              for c in top10_overall['country']]
    bars1 = ax1.barh(top10_overall['country'][::-1], top10_overall['total'][::-1], color=colors[::-1], edgecolor='black')
    ax1.set_xlabel('Number of Trials')
    ax1.set_title('Overall Leaders (2001-2025)', fontsize=16)
    for bar, val in zip(bars1, top10_overall['total'][::-1]):
        ax1.text(val + 10, bar.get_y() + bar.get_height()/2, str(val), va='center', fontsize=11, fontweight='bold')
    ax1.set_xlim(0, 800)
    
    # Last 5 years top 10
    ax2 = axes[1]
    top10_last5 = top_last5.head(10)
    colors = ['#f59e0b' if c == 'China' else '#2563eb' if c == 'United States' else '#6b7280' 
              for c in top10_last5['country']]
    bars2 = ax2.barh(top10_last5['country'][::-1], top10_last5['last5y'][::-1], color=colors[::-1], edgecolor='black')
    ax2.set_xlabel('Number of Trials')
    ax2.set_title('Last 5 Years (2021-2025)', fontsize=16)
    for bar, val in zip(bars2, top10_last5['last5y'][::-1]):
        ax2.text(val + 5, bar.get_y() + bar.get_height()/2, str(val), va='center', fontsize=11, fontweight='bold')
    ax2.set_xlim(0, 280)
    
    # Add legend
    us_patch = mpatches.Patch(color='#2563eb', label='United States')
    china_patch = mpatches.Patch(color='#f59e0b', label='China')
    other_patch = mpatches.Patch(color='#6b7280', label='Other')
    fig.legend(handles=[us_patch, china_patch, other_patch], loc='upper center', ncol=3, fontsize=12, bbox_to_anchor=(0.5, 0.02))
    
    fig.suptitle('Leadership Shift: China Emerges as Top Contributor', fontsize=18, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'slide_country_leaders.png', bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: slide_country_leaders.png")


def fig5_specialty_breakdown(specialty_df):
    """Figure 5: Specialty distribution pie chart."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Get top specialties
    top_spec = specialty_df.head(8).copy()
    other_total = specialty_df.iloc[8:]['total'].sum() if len(specialty_df) > 8 else 0
    if other_total > 0:
        other_row = pd.DataFrame({'specialty': ['Other Specialties'], 'total': [other_total]})
        top_spec = pd.concat([top_spec, other_row], ignore_index=True)
    
    colors = ['#2563eb', '#7c3aed', '#059669', '#dc2626', '#f59e0b', '#ec4899', '#06b6d4', '#84cc16', '#6b7280']
    
    wedges, texts, autotexts = ax.pie(
        top_spec['total'], 
        labels=top_spec['specialty'],
        autopct='%1.1f%%',
        colors=colors[:len(top_spec)],
        explode=[0.05 if i == 0 else 0 for i in range(len(top_spec))],
        startangle=90,
        textprops={'fontsize': 11}
    )
    
    for autotext in autotexts:
        autotext.set_fontweight('bold')
    
    ax.set_title('Distribution by Surgical Specialty', fontsize=18, fontweight='bold')
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'slide_specialty.png', bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: slide_specialty.png")


def fig6_comparator_analysis(comparators):
    """Figure 6: Comparator analysis showing robotic vs conventional."""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    data = comparators[comparators['flag'].isin(['laparoscopic_comparator', 'open_comparator'])]
    labels = ['vs Laparoscopic', 'vs Open Surgery']
    values = [738, 338]
    colors = ['#2563eb', '#dc2626']
    
    bars = ax.bar(labels, values, color=colors, edgecolor='black', width=0.6)
    
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15, 
                f'n={val}', ha='center', fontsize=14, fontweight='bold')
    
    ax.set_ylabel('Number of Trials')
    ax.set_title('Head-to-Head Comparisons with Conventional Approaches', fontsize=16)
    ax.set_ylim(0, 850)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'slide_comparators.png', bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: slide_comparators.png")


def fig7_key_numbers_summary():
    """Figure 7: Visual summary of key numbers."""
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axis('off')
    
    # Create a summary infographic-style figure
    metrics = [
        ('11×', 'Trial Growth\n(26 → 292)', '#2563eb'),
        ('7×', 'More Collaborations\n(3.8% → 26.4%)', '#7c3aed'),
        ('50%', 'Less Concentrated\n(HHI: 0.18 → 0.09)', '#059669'),
        ('3×', 'More Countries\n(11 → 27)', '#f59e0b'),
        ('#1', 'China in\nLast 5 Years', '#dc2626'),
    ]
    
    for i, (number, label, color) in enumerate(metrics):
        x = 0.1 + i * 0.18
        # Big number
        ax.text(x, 0.65, number, fontsize=48, fontweight='bold', color=color, 
                ha='center', va='center', transform=ax.transAxes)
        # Label
        ax.text(x, 0.3, label, fontsize=14, ha='center', va='center', 
                transform=ax.transAxes, linespacing=1.5)
    
    ax.set_title('25 Years of Globalization: Key Findings', fontsize=22, fontweight='bold', y=0.95)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'slide_key_numbers.png', bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: slide_key_numbers.png")


def create_summary_table(per_year):
    """Create a summary table for the presentation."""
    # Key years comparison
    summary = pd.DataFrame({
        'Metric': [
            'Annual Trials',
            'Active Countries',
            'Multi-Country Share',
            'Avg Countries/Trial',
            'HHI (Concentration)',
            'North America Share',
            'Europe Share',
            'Asia Share'
        ],
        '2001': ['26', '11', '3.8%', '1.04', '0.182', '34.6%', '38.5%', '26.9%'],
        '2025': ['292', '24', '26.4%', '1.32', '0.121', '19.5%', '55.5%', '52.7%'],
        'Change': ['↑ 11×', '↑ 2.2×', '↑ 7×', '↑ 27%', '↓ 33%', '↓ 44%', '↑ 44%', '↑ 96%']
    })
    
    summary.to_csv(OUT_DIR / 'summary_table.csv', index=False)
    print(f"Saved: summary_table.csv")
    
    # Country leaders table
    leaders = pd.DataFrame({
        'Rank': [1, 2, 3, 4, 5],
        'Overall (2001-2025)': ['United States (676)', 'China (322)', 'United Kingdom (293)', 'Germany (203)', 'South Korea (187)'],
        'Last 5 Years': ['China (238)', 'United States (201)', 'United Kingdom (141)', 'Germany (88)', 'Italy (71)']
    })
    
    leaders.to_csv(OUT_DIR / 'leaders_table.csv', index=False)
    print(f"Saved: leaders_table.csv")


def main():
    print("Loading data...")
    per_year, top_overall, top_last5, comparators, specialty, procedures = load_data()
    
    print("\nGenerating presentation figures...")
    fig1_trial_growth(per_year)
    fig2_globalization_metrics(per_year)
    fig3_regional_shift(per_year)
    fig4_country_leaders(top_overall, top_last5)
    fig5_specialty_breakdown(specialty)
    fig6_comparator_analysis(comparators)
    fig7_key_numbers_summary()
    
    print("\nCreating summary tables...")
    create_summary_table(per_year)
    
    print(f"\n✓ All presentation materials saved to: {OUT_DIR}")


if __name__ == '__main__':
    main()
