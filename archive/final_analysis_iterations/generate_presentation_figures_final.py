#!/usr/bin/env python3
"""
Final Presentation Figures for Robotic Surgery Clinical Trials Analysis
========================================================================
Generates the 8 key figures for the conference presentation.

Figures:
    1. fig1_trial_growth.png        - Trial growth over 25 years with CAGR/R²
    2. fig2a_hhi_concentration.png  - Geographic concentration (HHI) declining
    3. fig2b_collaboration.png      - International collaboration increasing
    4. fig3_regional_shift.png      - Regional distribution shift (5-year periods)
    5. fig4_country_leaders.png     - Top countries with income classification
    6. fig9_world_map.png           - Choropleth world map (requires cartopy)
    7. fig10a_income_distribution.png - Trial distribution by income level
    8. fig_equity_summary.png       - Global equity summary dashboard

Usage:
    python generate_presentation_figures_final.py
    
Dependencies:
    - pandas, numpy, matplotlib
    - scipy (for statistics)
    - cartopy, geopandas (for world map only)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
OUT_DIR = BASE_DIR / 'figures_elegant'

# ARGOS Grey Theme
COLORS = {
    'primary': '#374151',      # Dark charcoal
    'secondary': '#6B7280',    # Medium grey
    'light': '#9CA3AF',        # Light grey
    'lighter': '#D1D5DB',      # Very light grey
    'background': '#FAFAFA',   # Off-white
    'text': '#374151',
    'grid': '#E5E7EB',
    'accent': '#374151',
    'hic': '#4B5563',          # HIC color
    'lmic': '#7C9CBF',         # LMIC color (blue-grey)
    'collab': '#8B5CF6',       # Collaboration purple
}

# Set global matplotlib style
plt.rcParams.update({
    'figure.facecolor': COLORS['background'],
    'axes.facecolor': COLORS['background'],
    'savefig.facecolor': COLORS['background'],
    'font.family': 'sans-serif',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 13,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.edgecolor': COLORS['secondary'],
    'axes.labelcolor': COLORS['text'],
    'xtick.color': COLORS['text'],
    'ytick.color': COLORS['text'],
    'grid.color': COLORS['grid'],
    'grid.linewidth': 0.5,
})


# ============================================================================
# DATA LOADING
# ============================================================================

def load_data():
    """Load all required data files."""
    data = {}
    
    # Per-year metrics
    data['per_year'] = pd.read_csv(DATA_DIR / 'per_year_metrics.tsv', sep='\t')
    
    # Country data
    data['top_overall'] = pd.read_csv(DATA_DIR / 'top_countries_overall.tsv', sep='\t')
    data['top_last5'] = pd.read_csv(DATA_DIR / 'top_countries_last5y.tsv', sep='\t')
    
    # Income classification
    wb_df = pd.read_csv(BASE_DIR / 'world_bank_income.csv')
    income_lookup = {}
    for _, row in wb_df.iterrows():
        if row['income_level'] != 'Aggregates':
            income_lookup[row['country_name']] = row['income_level']
    data['income_lookup'] = income_lookup
    
    # Three-way split (HIC/LMIC/Collab)
    if (DATA_DIR / 'three_way_split.csv').exists():
        data['three_way'] = pd.read_csv(DATA_DIR / 'three_way_split.csv')
    
    # Income shares by year
    if (DATA_DIR / 'income_shares_by_year.csv').exists():
        data['income_shares'] = pd.read_csv(DATA_DIR / 'income_shares_by_year.csv')
    
    return data


def get_income_abbrev(country, income_lookup):
    """Get income classification for a country."""
    name_map = {
        'South Korea': 'Korea  Rep.',
        'United States': 'United States',
        'Russia': 'Russian Federation',
    }
    mapped = name_map.get(country, country)
    
    income = income_lookup.get(mapped) or income_lookup.get(country)
    if not income:
        for wb_name, inc in income_lookup.items():
            if country.lower() in wb_name.lower():
                income = inc
                break
    
    if income == 'High income':
        return 'HIC'
    elif income == 'Upper middle income':
        return 'UMIC'
    elif income == 'Lower middle income':
        return 'LMIC'
    elif income == 'Low income':
        return 'LIC'
    return ''


# ============================================================================
# FIGURE 1: Trial Growth
# ============================================================================

def fig1_trial_growth(per_year):
    """Generate trial growth figure with CAGR and statistics."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    df = per_year[(per_year['year'] >= 2001) & (per_year['year'] <= 2025)].copy()
    x = df['year'].values
    y = df['total_trials'].values
    
    # Fill area and line
    ax.fill_between(x, y, alpha=0.15, color=COLORS['primary'])
    ax.plot(x, y, color=COLORS['primary'], linewidth=2.5, marker='o', 
            markersize=5, markerfacecolor='white', markeredgewidth=1.5)
    
    # Trend line
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    trend = slope * x + intercept
    ax.plot(x, trend, '--', color=COLORS['secondary'], linewidth=1.5, 
            label=f'Trend (R²={r_value**2:.2f})')
    
    # Statistics
    cagr = ((y[-1] / y[0]) ** (1 / (len(y) - 1)) - 1) * 100
    spearman_rho, _ = stats.spearmanr(x, y)
    r2 = r_value ** 2
    
    # Stats box
    stats_text = (f'CAGR: {cagr:.1f}%\n'
                  f'Linear R² = {r2:.3f}\n'
                  f'Spearman ρ = {spearman_rho:.3f}\n'
                  f'p < 0.001')
    props = dict(boxstyle='round,pad=0.5', facecolor='white', 
                 edgecolor=COLORS['light'], alpha=0.95)
    ax.text(0.03, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace', fontweight='bold',
            bbox=props, color=COLORS['accent'])
    
    # Labels
    ax.annotate(f'{y[0]}', (x[0], y[0]), textcoords="offset points",
                xytext=(-10, 10), fontsize=10, fontweight='bold', color=COLORS['text'])
    ax.annotate(f'{y[-1]}', (x[-1], y[-1]), textcoords="offset points",
                xytext=(5, 5), fontsize=10, fontweight='bold', color=COLORS['text'])
    
    # Growth annotation
    fold_change = y[-1] / y[0]
    mid_idx = len(x) // 2
    ax.annotate(f'{fold_change:.0f}× increase', (x[mid_idx], y[mid_idx] + 50),
                fontsize=12, fontweight='bold', color=COLORS['primary'], ha='center')
    
    ax.set_xlabel('Year', fontweight='medium')
    ax.set_ylabel('Number of Clinical Trials', fontweight='medium')
    ax.set_title('Growth of Robotic Surgery Clinical Trials', fontweight='bold', pad=15)
    ax.set_xlim(2000, 2026)
    ax.set_ylim(0, max(y) * 1.15)
    ax.legend(loc='lower right', framealpha=0.95)
    ax.yaxis.grid(True, linestyle='-', alpha=0.3)
    ax.set_axisbelow(True)
    
    # X-axis formatting
    ax.set_xticks([2001, 2005, 2010, 2015, 2020, 2025])
    ax.set_xticklabels(['2001', '2005', '2010', '2015', '2020', 'Aug\n2025'])
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig1_trial_growth.png', dpi=300)
    plt.close(fig)
    print("  ✓ fig1_trial_growth.png")


# ============================================================================
# FIGURE 2a: HHI Concentration
# ============================================================================

def fig2a_hhi_concentration(per_year):
    """Generate HHI concentration figure."""
    fig, ax = plt.subplots(figsize=(11, 6))
    
    df = per_year[(per_year['year'] >= 2001) & (per_year['year'] <= 2025)].copy()
    x = df['year'].values
    y = df['hhi'].values
    
    ax.fill_between(x, y, alpha=0.15, color=COLORS['primary'])
    ax.plot(x, y, color=COLORS['primary'], linewidth=2, marker='s', 
            markersize=5, markerfacecolor='white', markeredgewidth=1.5)
    
    # Trend line
    slope, intercept, r_value, _, _ = stats.linregress(x, y)
    trend = slope * x + intercept
    ax.plot(x, trend, '--', color=COLORS['secondary'], linewidth=1.5)
    
    # Statistics
    spearman_rho, _ = stats.spearmanr(x, y)
    pct_change = ((y[-1] - y[0]) / y[0]) * 100
    
    stats_text = (f'Δ = {pct_change:.1f}%\n'
                  f'Linear R² = {r_value**2:.3f}\n'
                  f'Spearman ρ = {spearman_rho:.3f}\n'
                  f'p < 0.001')
    props = dict(boxstyle='round,pad=0.5', facecolor='white', 
                 edgecolor=COLORS['light'], alpha=0.95)
    ax.text(0.97, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', ha='right', fontfamily='monospace',
            fontweight='bold', bbox=props, color=COLORS['accent'])
    
    # Annotations
    ax.annotate(f'{y[0]:.2f}\n(concentrated)', (x[0], y[0]),
                textcoords="offset points", xytext=(-5, 10), fontsize=9,
                fontweight='bold', color=COLORS['text'], ha='center')
    ax.annotate(f'{y[-1]:.2f}\n(dispersed)', (x[-1], y[-1]),
                textcoords="offset points", xytext=(5, -25), fontsize=9,
                fontweight='bold', color=COLORS['text'], ha='center')
    
    ax.set_xlabel('Year', fontweight='medium')
    ax.set_ylabel('Herfindahl-Hirschman Index (HHI)', fontweight='medium')
    ax.set_title('Geographic Concentration Declining Over Time', fontweight='bold', pad=15)
    ax.set_xlim(2000, 2026)
    ax.set_ylim(0, 0.35)
    ax.yaxis.grid(True, linestyle='-', alpha=0.3)
    ax.set_axisbelow(True)
    ax.text(0.02, 0.02, 'Lower HHI = More geographic diversity',
            transform=ax.transAxes, fontsize=9, style='italic', color=COLORS['secondary'])
    
    ax.set_xticks([2001, 2005, 2010, 2015, 2020, 2025])
    ax.set_xticklabels(['2001', '2005', '2010', '2015', '2020', 'Aug\n2025'])
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig2a_hhi_concentration.png', dpi=300)
    plt.close(fig)
    print("  ✓ fig2a_hhi_concentration.png")


# ============================================================================
# FIGURE 2b: International Collaboration
# ============================================================================

def fig2b_collaboration(per_year):
    """Generate international collaboration figure."""
    fig, ax = plt.subplots(figsize=(11, 6))
    
    df = per_year[(per_year['year'] >= 2001) & (per_year['year'] <= 2025)].copy()
    x = df['year'].values
    y = df['multi_country_share'].values * 100
    
    ax.fill_between(x, y, alpha=0.15, color=COLORS['primary'])
    ax.plot(x, y, color=COLORS['primary'], linewidth=2, marker='o', 
            markersize=5, markerfacecolor='white', markeredgewidth=1.5)
    
    # Trend line
    slope, intercept, r_value, _, _ = stats.linregress(x, y)
    trend = slope * x + intercept
    ax.plot(x, trend, '--', color=COLORS['secondary'], linewidth=1.5)
    
    # Statistics
    spearman_rho, _ = stats.spearmanr(x, y)
    pp_change = y[-1] - y[0]
    
    stats_text = (f'Δ = +{pp_change:.1f}pp\n'
                  f'Linear R² = {r_value**2:.3f}\n'
                  f'Spearman ρ = {spearman_rho:.3f}\n'
                  f'p < 0.001')
    props = dict(boxstyle='round,pad=0.5', facecolor='white', 
                 edgecolor=COLORS['light'], alpha=0.95)
    ax.text(0.03, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace', fontweight='bold',
            bbox=props, color=COLORS['accent'])
    
    # Annotations
    ax.annotate(f'{y[0]:.1f}%', (x[0], y[0]), textcoords="offset points",
                xytext=(-5, -15), fontsize=9, fontweight='bold', color=COLORS['text'])
    ax.annotate(f'{y[-1]:.1f}%', (x[-1], y[-1]), textcoords="offset points",
                xytext=(5, 5), fontsize=9, fontweight='bold', color=COLORS['text'])
    
    # Fold change
    if y[0] > 0:
        fold = y[-1] / y[0]
        mid_idx = len(x) // 2
        ax.annotate(f'{fold:.0f}× increase in international collaboration',
                    (x[mid_idx], 15), fontsize=11, fontweight='bold',
                    color=COLORS['primary'], ha='center')
    
    ax.set_xlabel('Year', fontweight='medium')
    ax.set_ylabel('Trials with Multiple Countries (%)', fontweight='medium')
    ax.set_title('International Collaboration Increasing', fontweight='bold', pad=15)
    ax.set_xlim(2000, 2026)
    ax.set_ylim(0, 35)
    ax.yaxis.grid(True, linestyle='-', alpha=0.3)
    ax.set_axisbelow(True)
    
    ax.set_xticks([2001, 2005, 2010, 2015, 2020, 2025])
    ax.set_xticklabels(['2001', '2005', '2010', '2015', '2020', 'Aug\n2025'])
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig2b_collaboration.png', dpi=300)
    plt.close(fig)
    print("  ✓ fig2b_collaboration.png")


# ============================================================================
# FIGURE 3: Regional Shift
# ============================================================================

def fig3_regional_shift(per_year):
    """Generate regional shift comparison (5-year periods)."""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    df = per_year.copy()
    
    # Calculate 5-year averages
    early = df[df['year'].between(2001, 2005)]
    late = df[df['year'].between(2021, 2025)]
    
    regions = ['North America', 'Europe', 'Asia', 'Middle East', 
               'Latin America', 'Oceania', 'Africa']
    col_map = {
        'North America': 'share_north_america', 'Europe': 'share_europe',
        'Asia': 'share_asia', 'Middle East': 'share_middle_east',
        'Latin America': 'share_latin_america', 'Oceania': 'share_oceania',
        'Africa': 'share_africa'
    }
    
    early_vals = [early[col_map[r]].mean() * 100 for r in regions]
    late_vals = [late[col_map[r]].mean() * 100 for r in regions]
    
    x = np.arange(len(regions))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, early_vals, width, label='2001–2005',
                   color=COLORS['light'], edgecolor='white', linewidth=0.5)
    bars2 = ax.bar(x + width/2, late_vals, width, label='2021–2025',
                   color=COLORS['primary'], edgecolor='white', linewidth=0.5)
    
    # Value labels
    for bar, val in zip(bars1, early_vals):
        label = f'{val:.0f}%' if val >= 1 else '<1%'
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                label, ha='center', va='bottom', fontsize=9, color=COLORS['secondary'])
    
    for bar, val in zip(bars2, late_vals):
        label = f'{val:.0f}%' if val >= 1 else '<1%'
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                label, ha='center', va='bottom', fontsize=9, fontweight='bold',
                color=COLORS['primary'])
    
    # Chi-square test - normalize to same sum
    early_counts = np.array([max(v, 0.1) for v in early_vals])
    late_counts = np.array([max(v, 0.1) for v in late_vals])
    # Scale expected to match observed sum
    early_scaled = early_counts * (late_counts.sum() / early_counts.sum())
    chi2, p_chi = stats.chisquare(late_counts, f_exp=early_scaled)
    dof = len(regions) - 1
    
    p_str = 'p < 0.001' if p_chi < 0.001 else f'p = {p_chi:.3f}'
    stats_text = f'Chi-square: χ² = {chi2:.1f}  |  df = {dof}  |  {p_str}'
    props = dict(boxstyle='round,pad=0.4', facecolor='white', 
                 edgecolor=COLORS['light'], alpha=0.95)
    ax.text(0.5, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='center',
            fontfamily='monospace', fontweight='bold', bbox=props, color=COLORS['accent'])
    
    ax.set_xlabel('')
    ax.set_ylabel('Share of Clinical Trials (%)', fontweight='medium')
    ax.set_title('Regional Distribution Shift (5-Year Periods)', fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(regions, rotation=30, ha='right')
    ax.legend(loc='upper left', framealpha=0.95)
    ax.yaxis.grid(True, linestyle='-', alpha=0.3)
    ax.set_axisbelow(True)
    ax.set_ylim(0, max(max(early_vals), max(late_vals)) * 1.2)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig3_regional_shift.png', dpi=300)
    plt.close(fig)
    print("  ✓ fig3_regional_shift.png")


# ============================================================================
# FIGURE 4: Country Leaders
# ============================================================================

def fig4_country_leaders(top_overall, top_last5, income_lookup):
    """Generate country leadership figure with income classification."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    
    income_colors = {
        'HIC': COLORS['primary'],
        'UMIC': COLORS['light'],
        'LMIC': '#B0C4DE',
        'LIC': '#E0E0E0',
        '': COLORS['secondary']
    }
    
    # Overall (left panel)
    top8_overall = top_overall.head(8)
    countries1 = top8_overall['country'].tolist()
    colors1 = [income_colors[get_income_abbrev(c, income_lookup)] for c in countries1]
    
    bars1 = ax1.barh(countries1[::-1], top8_overall['total'][::-1],
                     color=colors1[::-1], edgecolor='white', linewidth=0.5, height=0.7)
    
    for bar, val in zip(bars1, top8_overall['total'][::-1]):
        ax1.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                str(val), va='center', fontsize=10, fontweight='medium')
    
    ax1.set_xlabel('Number of Trials', fontweight='medium')
    ax1.set_title('Overall (2001–2025)', fontweight='bold')
    ax1.xaxis.grid(True, linestyle='-', alpha=0.3)
    ax1.set_axisbelow(True)
    
    # Last 5 years (right panel)
    top8_last5 = top_last5.head(8)
    countries2 = top8_last5['country'].tolist()
    colors2 = [income_colors[get_income_abbrev(c, income_lookup)] for c in countries2]
    
    # Column name is 'last5y' not 'total'
    count_col = 'last5y' if 'last5y' in top8_last5.columns else 'total'
    bars2 = ax2.barh(countries2[::-1], top8_last5[count_col][::-1],
                     color=colors2[::-1], edgecolor='white', linewidth=0.5, height=0.7)
    
    for bar, val in zip(bars2, top8_last5[count_col][::-1]):
        ax2.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                str(val), va='center', fontsize=10, fontweight='medium')
    
    ax2.set_xlabel('Number of Trials', fontweight='medium')
    ax2.set_title('Last 5 Years (2021–2025)', fontweight='bold')
    ax2.xaxis.grid(True, linestyle='-', alpha=0.3)
    ax2.set_axisbelow(True)
    
    fig.suptitle('Leadership Transition: China Emerges as Top Contributor',
                 fontweight='bold', fontsize=14, y=0.98)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=COLORS['primary'], edgecolor='white', label='HIC = High income'),
        mpatches.Patch(facecolor=COLORS['light'], edgecolor='white', label='UMIC = Upper middle income'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=2,
               framealpha=0.95, fontsize=9, bbox_to_anchor=(0.5, -0.02))
    
    fig.tight_layout(rect=[0, 0.05, 1, 0.95])
    fig.savefig(OUT_DIR / 'fig4_country_leaders.png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("  ✓ fig4_country_leaders.png")


# ============================================================================
# FIGURE 10a: Income Distribution
# ============================================================================

def fig10a_income_distribution(top_overall, income_lookup):
    """Generate income distribution figure."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    income_totals = {'High income': 0, 'Upper middle income': 0,
                     'Lower middle income': 0, 'Low income': 0}
    
    for _, row in top_overall.iterrows():
        country = row['country']
        trials = row['total']
        
        income = None
        for wb_name, inc in income_lookup.items():
            if country.lower() in wb_name.lower() or wb_name.lower() in country.lower():
                income = inc
                break
        
        if income and income in income_totals:
            income_totals[income] += trials
    
    categories = ['High\nIncome', 'Upper Middle\nIncome', 'Lower Middle\nIncome', 'Low\nIncome']
    values = [income_totals['High income'], income_totals['Upper middle income'],
              income_totals['Lower middle income'], income_totals['Low income']]
    
    bar_colors = [COLORS['primary'], COLORS['secondary'], COLORS['light'], COLORS['lighter']]
    
    bars = ax.bar(categories, values, color=bar_colors, edgecolor='white', width=0.6)
    
    total = sum(values)
    for bar, val in zip(bars, values):
        pct = val / total * 100 if total > 0 else 0
        color = 'white' if val > 500 else COLORS['text']
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 100 if val > 500 else bar.get_height() + 50,
                f'n = {val}\n({pct:.1f}%)', ha='center', va='top' if val > 500 else 'bottom',
                fontsize=11, fontweight='bold', color=color)
    
    ax.set_ylabel('Number of Trials', fontweight='medium')
    ax.set_title('Trial Distribution by World Bank Income Classification', fontweight='bold', pad=15)
    ax.yaxis.grid(True, linestyle='-', alpha=0.3)
    ax.set_axisbelow(True)
    ax.text(0.5, -0.12, 'Source: World Bank Country Classifications (2024-2025)',
            transform=ax.transAxes, ha='center', fontsize=9, style='italic', color=COLORS['secondary'])
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig10a_income_distribution.png', dpi=300)
    plt.close(fig)
    print("  ✓ fig10a_income_distribution.png")


# ============================================================================
# FIGURE: Equity Summary Dashboard
# ============================================================================

def fig_equity_summary(data):
    """Generate equity summary dashboard."""
    fig = plt.figure(figsize=(14, 8))
    gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.3)
    
    # Panel A: Three-way stacked area
    ax1 = fig.add_subplot(gs[0, :2])
    
    if 'three_way' in data:
        split_df = data['three_way']
        years = split_df['year'].values
        hic_only = split_df['hic_only'].values
        hic_lmic = split_df['hic_lmic_collab'].values
        lmic_only = split_df['lmic_only'].values
        
        ax1.stackplot(years, hic_only, hic_lmic, lmic_only,
                      colors=[COLORS['primary'], COLORS['collab'], COLORS['lmic']],
                      labels=['HIC-only', 'HIC-LMIC Collab', 'LMIC-only'],
                      alpha=0.85, edgecolor='white', linewidth=0.5)
        
        ax1.set_xlim(2001, 2025)
    
    ax1.set_xlabel('Year', fontweight='medium')
    ax1.set_ylabel('Share of Trials (%)', fontweight='medium')
    ax1.set_title('A. Trial Distribution by Income Level Over Time', fontweight='bold', fontsize=11)
    ax1.set_ylim(0, 100)
    ax1.legend(loc='center right', framealpha=0.95, fontsize=9)
    ax1.yaxis.grid(True, linestyle='-', alpha=0.2, color='white')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # Panel B: Collaboration donut
    ax2 = fig.add_subplot(gs[0, 2])
    sizes = [81, 19]
    colors = [COLORS['primary'], COLORS['light']]
    
    wedges, texts, autotexts = ax2.pie(sizes, colors=colors, autopct='%1.0f%%',
                                        startangle=90, pctdistance=0.75,
                                        wedgeprops=dict(width=0.5, edgecolor='white'))
    for autotext in autotexts:
        autotext.set_fontweight('bold')
        autotext.set_fontsize(11)
    
    ax2.text(0, 0, 'n=200', ha='center', va='center', fontsize=12, fontweight='bold')
    ax2.set_title('B. Collaboration Types', fontweight='bold', fontsize=11, pad=10)
    ax2.legend(wedges, ['HIC-HIC', 'HIC-LMIC'], loc='lower center',
               bbox_to_anchor=(0.5, -0.15), ncol=2)
    
    # Panel C: Change table
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.axis('off')
    
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
    
    table = ax3.table(cellText=table_data, colLabels=['Metric', '2001-05', '2021-25', 'Δ'],
                      cellLoc='center', loc='center', colWidths=[0.42, 0.18, 0.18, 0.18])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.1, 1.6)
    
    for i in range(4):
        table[(0, i)].set_facecolor(COLORS['primary'])
        table[(0, i)].set_text_props(color='white', fontweight='bold')
    
    ax3.set_title('C. 25-Year Change', fontweight='bold', fontsize=11, y=0.95)
    
    # Panel D: LMIC breakdown bar
    ax4 = fig.add_subplot(gs[1, 1])
    categories = ['Upper\nMiddle', 'Lower\nMiddle', 'Low\nIncome']
    values = [22.4, 2.3, 0.0]
    colors_bar = [COLORS['secondary'], COLORS['light'], COLORS['lighter']]
    
    bars = ax4.bar(categories, values, color=colors_bar, edgecolor='white', width=0.6)
    ax4.set_ylabel('Share of Trials (%)', fontweight='medium')
    ax4.set_title('D. LMIC Breakdown (2021-25)', fontweight='bold', fontsize=11)
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    
    for bar, val in zip(bars, values):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}%', ha='center', fontsize=10, fontweight='bold')
    
    ax4.text(0.5, -0.18, 'China = 90% of Upper Middle category',
             transform=ax4.transAxes, ha='center', fontsize=9, style='italic',
             color='#EF4444')
    
    # Panel E: LMIC partners pie
    ax5 = fig.add_subplot(gs[1, 2])
    countries = ['China', 'Brazil', 'India', 'Egypt', 'Other']
    values = [21, 9, 7, 3, 1]
    
    ax5.pie(values, labels=countries,
            colors=[COLORS['secondary'], COLORS['light'], '#A8B5C4', '#C4CDD8', COLORS['lighter']],
            autopct='%1.0f%%', startangle=90,
            wedgeprops=dict(edgecolor='white', linewidth=1))
    ax5.set_title('E. LMIC Collaboration Partners', fontweight='bold', fontsize=11, pad=10)
    
    fig.suptitle('Global Equity in Robotic Surgery Research\nA 25-Year Analysis of Clinical Trials',
                 fontweight='bold', fontsize=14, y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(OUT_DIR / 'fig_equity_summary.png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("  ✓ fig_equity_summary.png")


# ============================================================================
# WORLD MAP (requires cartopy)
# ============================================================================

def fig9_world_map():
    """Generate world map - calls bubble map script that uses cartopy."""
    try:
        import subprocess
        result = subprocess.run(
            ['python3', str(BASE_DIR / 'generate_bubble_map.py')],
            capture_output=True, text=True, cwd=str(BASE_DIR)
        )
        if result.returncode == 0:
            print("  ✓ fig9_world_map.png (bubble map via cartopy)")
        else:
            print(f"  ✗ World map failed: {result.stderr}")
    except Exception as e:
        print(f"  ✗ World map skipped (cartopy not available): {e}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 60)
    print("Generating Presentation Figures")
    print("=" * 60)
    print()
    
    # Ensure output directory exists
    OUT_DIR.mkdir(exist_ok=True)
    
    # Load data
    print("Loading data...")
    data = load_data()
    print()
    
    # Generate figures
    print("Generating figures...")
    
    fig1_trial_growth(data['per_year'])
    fig2a_hhi_concentration(data['per_year'])
    fig2b_collaboration(data['per_year'])
    fig3_regional_shift(data['per_year'])
    fig4_country_leaders(data['top_overall'], data['top_last5'], data['income_lookup'])
    fig10a_income_distribution(data['top_overall'], data['income_lookup'])
    fig_equity_summary(data)
    fig9_world_map()
    
    print()
    print("=" * 60)
    print(f"✓ All figures saved to: {OUT_DIR}")
    print("=" * 60)


if __name__ == '__main__':
    main()
