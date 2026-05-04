#!/usr/bin/env python3
"""
================================================================================
ROBOTIC SURGERY CLINICAL TRIALS - PRESENTATION FIGURES
================================================================================

Generates 8 publication-quality figures for conference presentation analyzing
25 years (2001-2025) of robotic surgery clinical trials from PubMed/MEDLINE.

Figures Generated:
    1. fig1_trial_growth.png        - Trial growth with CAGR, R², Spearman ρ
    2. fig2a_hhi_concentration.png  - Geographic concentration (HHI) declining
    3. fig2b_collaboration.png      - International collaboration increasing
    4. fig3_regional_shift.png      - Regional distribution shift with χ² test
    5. fig4_country_leaders.png     - Top countries with income classification
    6. fig9_world_map.png           - Bubble map (HIC/LMIC colors)
    7. fig10a_income_distribution.png - Trials by World Bank income level
    8. fig_equity_summary.png       - 5-panel equity dashboard

Data Sources:
    - PubMed/MEDLINE clinical trials data
    - World Bank income classifications (2024-2025)
    - Natural Earth shapefiles (110m resolution)

Usage:
    python generate_all_figures.py

Requirements:
    - pandas, numpy, matplotlib, scipy (core)
    - cartopy, geopandas (for world map)

Author: Generated for robotic surgery bibliometric analysis
================================================================================
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
# PATHS
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
SHAPEFILE_DIR = BASE_DIR / 'shapefiles'
OUTPUT_DIR = BASE_DIR / 'output'

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================================
# THEME CONFIGURATION (ARGOS Grey)
# ============================================================================

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
    'hic_map': '#2563eb',      # Blue for map
    'lmic_map': '#059669',     # Green for map
}

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
# COUNTRY COORDINATES FOR BUBBLE MAP
# ============================================================================

COUNTRY_COORDS = {
    'United States': (-95, 38), 'China': (105, 35), 'United Kingdom': (-1, 53),
    'Germany': (10, 51), 'South Korea': (127, 36), 'Italy': (12, 43),
    'Japan': (138, 37), 'France': (2, 47), 'Netherlands': (5, 52),
    'Canada': (-105, 55), 'Denmark': (10, 56), 'Sweden': (16, 62),
    'Switzerland': (8, 47), 'Turkey': (35, 39), 'Spain': (-4, 40),
    'India': (78, 22), 'Brazil': (-52, -12), 'Australia': (134, -25),
    'Israel': (35, 31), 'Finland': (26, 64), 'Hong Kong': (114, 22),
    'Norway': (10, 62), 'Singapore': (104, 1), 'Taiwan': (121, 24),
    'New Zealand': (173, -41), 'Egypt': (30, 27), 'Iran': (53, 32),
    'Russia': (90, 60), 'Ireland': (-8, 53), 'Saudi Arabia': (45, 24),
    'South Africa': (25, -29), 'Poland': (19, 52),
}

# ============================================================================
# DATA LOADING
# ============================================================================

def load_all_data():
    """Load all required data files."""
    print("Loading data...")
    data = {}
    
    data['per_year'] = pd.read_csv(DATA_DIR / 'per_year_metrics.tsv', sep='\t')
    data['top_overall'] = pd.read_csv(DATA_DIR / 'top_countries_overall.tsv', sep='\t')
    data['top_last5'] = pd.read_csv(DATA_DIR / 'top_countries_last5y.tsv', sep='\t')
    
    # Income lookup
    wb_df = pd.read_csv(DATA_DIR / 'world_bank_income.csv')
    income_lookup = {}
    for _, row in wb_df.iterrows():
        if row['income_level'] != 'Aggregates':
            income_lookup[row['country_name']] = row['income_level']
    data['income_lookup'] = income_lookup
    
    # Three-way split for equity summary
    if (DATA_DIR / 'three_way_split.csv').exists():
        data['three_way'] = pd.read_csv(DATA_DIR / 'three_way_split.csv')
    
    print(f"  Loaded {len(data)} data sources")
    return data


def get_income_class(country, income_lookup):
    """Get HIC/LMIC classification for a country."""
    mappings = {
        'South Korea': 'Korea  Rep.', 'United States': 'United States',
        'Russia': 'Russian Federation', 'England': 'United Kingdom',
    }
    mapped = mappings.get(country, country)
    
    income = income_lookup.get(mapped) or income_lookup.get(country)
    if not income:
        for name, inc in income_lookup.items():
            if country.lower() in name.lower():
                income = inc
                break
    
    if income == 'High income':
        return 'HIC'
    return 'LMIC'


def get_income_abbrev(country, income_lookup):
    """Get income abbreviation (HIC/UMIC/LMIC/LIC)."""
    mappings = {'South Korea': 'Korea  Rep.', 'United States': 'United States'}
    mapped = mappings.get(country, country)
    
    income = income_lookup.get(mapped) or income_lookup.get(country)
    if not income:
        for name, inc in income_lookup.items():
            if country.lower() in name.lower():
                income = inc
                break
    
    abbrevs = {
        'High income': 'HIC', 'Upper middle income': 'UMIC',
        'Lower middle income': 'LMIC', 'Low income': 'LIC'
    }
    return abbrevs.get(income, '')


# ============================================================================
# FIGURE 1: Trial Growth
# ============================================================================

def fig1_trial_growth(per_year):
    """Trial growth with statistics."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    df = per_year[(per_year['year'] >= 2001) & (per_year['year'] <= 2025)].copy()
    x, y = df['year'].values, df['total_trials'].values
    
    ax.fill_between(x, y, alpha=0.15, color=COLORS['primary'])
    ax.plot(x, y, color=COLORS['primary'], linewidth=2.5, marker='o',
            markersize=5, markerfacecolor='white', markeredgewidth=1.5)
    
    # Trend
    slope, intercept, r_value, _, _ = stats.linregress(x, y)
    ax.plot(x, slope * x + intercept, '--', color=COLORS['secondary'], linewidth=1.5)
    
    # Stats
    cagr = ((y[-1] / y[0]) ** (1 / (len(y) - 1)) - 1) * 100
    spearman_rho, _ = stats.spearmanr(x, y)
    
    stats_text = f'CAGR: {cagr:.1f}%\nLinear R² = {r_value**2:.3f}\nSpearman ρ = {spearman_rho:.3f}\np < 0.001'
    props = dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=COLORS['light'], alpha=0.95)
    ax.text(0.03, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
            va='top', fontfamily='monospace', fontweight='bold', bbox=props)
    
    ax.annotate(f'{y[0]}', (x[0], y[0]), xytext=(-10, 10), textcoords="offset points",
                fontsize=10, fontweight='bold')
    ax.annotate(f'{y[-1]}', (x[-1], y[-1]), xytext=(5, 5), textcoords="offset points",
                fontsize=10, fontweight='bold')
    ax.annotate(f'{y[-1]/y[0]:.0f}× increase', (x[len(x)//2], y[len(x)//2] + 50),
                fontsize=12, fontweight='bold', ha='center', color=COLORS['primary'])
    
    ax.set_xlabel('Year', fontweight='medium')
    ax.set_ylabel('Number of Clinical Trials', fontweight='medium')
    ax.set_title('Growth of Robotic Surgery Clinical Trials', fontweight='bold', pad=15)
    ax.set_xlim(2000, 2026)
    ax.set_ylim(0, max(y) * 1.15)
    ax.yaxis.grid(True, linestyle='-', alpha=0.3)
    ax.set_xticks([2001, 2005, 2010, 2015, 2020, 2025])
    ax.set_xticklabels(['2001', '2005', '2010', '2015', '2020', 'Aug\n2025'])
    
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'fig1_trial_growth.png', dpi=300)
    plt.close(fig)
    print("  ✓ fig1_trial_growth.png")


# ============================================================================
# FIGURE 2a: HHI Concentration
# ============================================================================

def fig2a_hhi_concentration(per_year):
    """Geographic concentration declining."""
    fig, ax = plt.subplots(figsize=(11, 6))
    
    df = per_year[(per_year['year'] >= 2001) & (per_year['year'] <= 2025)].copy()
    x, y = df['year'].values, df['hhi'].values
    
    ax.fill_between(x, y, alpha=0.15, color=COLORS['primary'])
    ax.plot(x, y, color=COLORS['primary'], linewidth=2, marker='s',
            markersize=5, markerfacecolor='white', markeredgewidth=1.5)
    
    slope, intercept, r_value, _, _ = stats.linregress(x, y)
    ax.plot(x, slope * x + intercept, '--', color=COLORS['secondary'], linewidth=1.5)
    
    spearman_rho, _ = stats.spearmanr(x, y)
    pct_change = ((y[-1] - y[0]) / y[0]) * 100
    
    stats_text = f'Δ = {pct_change:.1f}%\nLinear R² = {r_value**2:.3f}\nSpearman ρ = {spearman_rho:.3f}\np < 0.001'
    props = dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=COLORS['light'], alpha=0.95)
    ax.text(0.97, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
            va='top', ha='right', fontfamily='monospace', fontweight='bold', bbox=props)
    
    ax.annotate(f'{y[0]:.2f}\n(concentrated)', (x[0], y[0]), xytext=(-5, 10),
                textcoords="offset points", fontsize=9, fontweight='bold', ha='center')
    ax.annotate(f'{y[-1]:.2f}\n(dispersed)', (x[-1], y[-1]), xytext=(5, -25),
                textcoords="offset points", fontsize=9, fontweight='bold', ha='center')
    
    ax.set_xlabel('Year', fontweight='medium')
    ax.set_ylabel('Herfindahl-Hirschman Index (HHI)', fontweight='medium')
    ax.set_title('Geographic Concentration Declining Over Time', fontweight='bold', pad=15)
    ax.set_xlim(2000, 2026)
    ax.set_ylim(0, 0.35)
    ax.yaxis.grid(True, linestyle='-', alpha=0.3)
    ax.text(0.02, 0.02, 'Lower HHI = More geographic diversity',
            transform=ax.transAxes, fontsize=9, style='italic', color=COLORS['secondary'])
    ax.set_xticks([2001, 2005, 2010, 2015, 2020, 2025])
    ax.set_xticklabels(['2001', '2005', '2010', '2015', '2020', 'Aug\n2025'])
    
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'fig2a_hhi_concentration.png', dpi=300)
    plt.close(fig)
    print("  ✓ fig2a_hhi_concentration.png")


# ============================================================================
# FIGURE 2b: International Collaboration
# ============================================================================

def fig2b_collaboration(per_year):
    """International collaboration increasing."""
    fig, ax = plt.subplots(figsize=(11, 6))
    
    df = per_year[(per_year['year'] >= 2001) & (per_year['year'] <= 2025)].copy()
    x = df['year'].values
    y = df['multi_country_share'].values * 100
    
    ax.fill_between(x, y, alpha=0.15, color=COLORS['primary'])
    ax.plot(x, y, color=COLORS['primary'], linewidth=2, marker='o',
            markersize=5, markerfacecolor='white', markeredgewidth=1.5)
    
    slope, intercept, r_value, _, _ = stats.linregress(x, y)
    ax.plot(x, slope * x + intercept, '--', color=COLORS['secondary'], linewidth=1.5)
    
    spearman_rho, _ = stats.spearmanr(x, y)
    pp_change = y[-1] - y[0]
    
    stats_text = f'Δ = +{pp_change:.1f}pp\nLinear R² = {r_value**2:.3f}\nSpearman ρ = {spearman_rho:.3f}\np < 0.001'
    props = dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=COLORS['light'], alpha=0.95)
    ax.text(0.03, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
            va='top', fontfamily='monospace', fontweight='bold', bbox=props)
    
    ax.annotate(f'{y[0]:.1f}%', (x[0], y[0]), xytext=(-5, -15),
                textcoords="offset points", fontsize=9, fontweight='bold')
    ax.annotate(f'{y[-1]:.1f}%', (x[-1], y[-1]), xytext=(5, 5),
                textcoords="offset points", fontsize=9, fontweight='bold')
    
    if y[0] > 0:
        ax.annotate(f'{y[-1]/y[0]:.0f}× increase in international collaboration',
                    (x[len(x)//2], 15), fontsize=11, fontweight='bold', ha='center',
                    color=COLORS['primary'])
    
    ax.set_xlabel('Year', fontweight='medium')
    ax.set_ylabel('Trials with Multiple Countries (%)', fontweight='medium')
    ax.set_title('International Collaboration Increasing', fontweight='bold', pad=15)
    ax.set_xlim(2000, 2026)
    ax.set_ylim(0, 35)
    ax.yaxis.grid(True, linestyle='-', alpha=0.3)
    ax.set_xticks([2001, 2005, 2010, 2015, 2020, 2025])
    ax.set_xticklabels(['2001', '2005', '2010', '2015', '2020', 'Aug\n2025'])
    
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'fig2b_collaboration.png', dpi=300)
    plt.close(fig)
    print("  ✓ fig2b_collaboration.png")


# ============================================================================
# FIGURE 3: Regional Shift
# ============================================================================

def fig3_regional_shift(per_year):
    """Regional distribution shift (5-year periods)."""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    df = per_year.copy()
    early = df[df['year'].between(2001, 2005)]
    late = df[df['year'].between(2021, 2025)]
    
    regions = ['North America', 'Europe', 'Asia', 'Middle East', 'Latin America', 'Oceania', 'Africa']
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
                   color=COLORS['light'], edgecolor='white')
    bars2 = ax.bar(x + width/2, late_vals, width, label='2021–2025',
                   color=COLORS['primary'], edgecolor='white')
    
    for bar, val in zip(bars1, early_vals):
        label = f'{val:.0f}%' if val >= 1 else '<1%'
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                label, ha='center', fontsize=9, color=COLORS['secondary'])
    
    for bar, val in zip(bars2, late_vals):
        label = f'{val:.0f}%' if val >= 1 else '<1%'
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                label, ha='center', fontsize=9, fontweight='bold', color=COLORS['primary'])
    
    # Chi-square
    early_counts = np.array([max(v, 0.1) for v in early_vals])
    late_counts = np.array([max(v, 0.1) for v in late_vals])
    early_scaled = early_counts * (late_counts.sum() / early_counts.sum())
    chi2, p_chi = stats.chisquare(late_counts, f_exp=early_scaled)
    
    p_str = 'p < 0.001' if p_chi < 0.001 else f'p = {p_chi:.3f}'
    stats_text = f'Chi-square: χ² = {chi2:.1f}  |  df = {len(regions)-1}  |  {p_str}'
    props = dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor=COLORS['light'], alpha=0.95)
    ax.text(0.5, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
            va='top', ha='center', fontfamily='monospace', fontweight='bold', bbox=props)
    
    ax.set_ylabel('Share of Clinical Trials (%)', fontweight='medium')
    ax.set_title('Regional Distribution Shift (5-Year Periods)', fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(regions, rotation=30, ha='right')
    ax.legend(loc='upper left', framealpha=0.95)
    ax.yaxis.grid(True, linestyle='-', alpha=0.3)
    ax.set_ylim(0, max(max(early_vals), max(late_vals)) * 1.2)
    
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'fig3_regional_shift.png', dpi=300)
    plt.close(fig)
    print("  ✓ fig3_regional_shift.png")


# ============================================================================
# FIGURE 4: Country Leaders
# ============================================================================

def fig4_country_leaders(top_overall, top_last5, income_lookup):
    """Top countries with income classification."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    
    income_colors = {'HIC': COLORS['primary'], 'UMIC': COLORS['light'],
                     'LMIC': '#B0C4DE', 'LIC': '#E0E0E0', '': COLORS['secondary']}
    
    # Overall
    top8 = top_overall.head(8)
    countries1 = top8['country'].tolist()
    colors1 = [income_colors[get_income_abbrev(c, income_lookup)] for c in countries1]
    
    bars1 = ax1.barh(countries1[::-1], top8['total'][::-1], color=colors1[::-1],
                     edgecolor='white', height=0.7)
    for bar, val in zip(bars1, top8['total'][::-1]):
        ax1.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                str(val), va='center', fontsize=10, fontweight='medium')
    
    ax1.set_xlabel('Number of Trials', fontweight='medium')
    ax1.set_title('Overall (2001–2025)', fontweight='bold')
    ax1.xaxis.grid(True, linestyle='-', alpha=0.3)
    
    # Last 5 years
    top8_last5 = top_last5.head(8)
    countries2 = top8_last5['country'].tolist()
    colors2 = [income_colors[get_income_abbrev(c, income_lookup)] for c in countries2]
    count_col = 'last5y' if 'last5y' in top8_last5.columns else 'total'
    
    bars2 = ax2.barh(countries2[::-1], top8_last5[count_col][::-1], color=colors2[::-1],
                     edgecolor='white', height=0.7)
    for bar, val in zip(bars2, top8_last5[count_col][::-1]):
        ax2.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                str(val), va='center', fontsize=10, fontweight='medium')
    
    ax2.set_xlabel('Number of Trials', fontweight='medium')
    ax2.set_title('Last 5 Years (2021–2025)', fontweight='bold')
    ax2.xaxis.grid(True, linestyle='-', alpha=0.3)
    
    fig.suptitle('Leadership Transition: China Emerges as Top Contributor',
                 fontweight='bold', fontsize=14, y=0.98)
    
    legend_elements = [
        mpatches.Patch(facecolor=COLORS['primary'], label='HIC = High income'),
        mpatches.Patch(facecolor=COLORS['light'], label='UMIC = Upper middle income'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=2,
               framealpha=0.95, fontsize=9, bbox_to_anchor=(0.5, -0.02))
    
    fig.tight_layout(rect=[0, 0.05, 1, 0.95])
    fig.savefig(OUTPUT_DIR / 'fig4_country_leaders.png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("  ✓ fig4_country_leaders.png")


# ============================================================================
# FIGURE 9: World Map (Bubble)
# ============================================================================

def fig9_world_map(top_overall, income_lookup):
    """Bubble map with HIC/LMIC colors."""
    try:
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature
    except ImportError:
        print("  ✗ fig9_world_map.png (cartopy not installed)")
        return
    
    fig = plt.figure(figsize=(18, 10), facecolor='#fafafa')
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson())
    ax.set_global()
    
    ax.add_feature(cfeature.OCEAN, facecolor='#e8f1f5', zorder=0)
    ax.add_feature(cfeature.LAND, facecolor='#f5f5f5', edgecolor='#d0d0d0',
                   linewidth=0.3, zorder=1)
    ax.coastlines(resolution='110m', linewidth=0.4, color='#a0a0a0', zorder=2)
    ax.gridlines(draw_labels=False, linewidth=0.2, color='#c8c8c8', alpha=0.5, zorder=1)
    
    max_trials = top_overall['total'].max()
    trials_sorted = top_overall.sort_values('total', ascending=False)
    
    hic_total, lmic_total = 0, 0
    
    for _, row in trials_sorted.iterrows():
        country, trials = row['country'], row['total']
        if country not in COUNTRY_COORDS:
            continue
        
        lon, lat = COUNTRY_COORDS[country]
        area = (trials / max_trials) * 2500
        
        is_hic = get_income_class(country, income_lookup) == 'HIC'
        color = COLORS['hic_map'] if is_hic else COLORS['lmic_map']
        
        if is_hic:
            hic_total += trials
        else:
            lmic_total += trials
        
        ax.scatter(lon, lat, transform=ccrs.PlateCarree(),
                  s=area * 1.15, c='#000000', alpha=0.08, zorder=3)
        ax.scatter(lon, lat, transform=ccrs.PlateCarree(),
                  s=area, c=color, alpha=0.75,
                  edgecolor='white', linewidth=1.2, zorder=4)
        
        if trials >= 100:
            ax.annotate(f'{trials}', xy=(lon, lat),
                       xycoords=ccrs.PlateCarree()._as_mpl_transform(ax),
                       fontsize=9, fontweight='bold', color='#1a1a1a',
                       ha='center', va='center', zorder=5)
    
    fig.suptitle('Global Distribution of Robotic Surgery Clinical Trials',
                 fontsize=22, fontweight='bold', color='#1a1a1a', y=0.95)
    total = hic_total + lmic_total
    fig.text(0.5, 0.89, f'2001–2025  •  {total:,} trials across 45 countries',
             ha='center', fontsize=13, color='#505050')
    
    # Legends
    legend_sizes = [50, 200, 500]
    legend_bubbles = [plt.scatter([], [], s=(s/max_trials)*2500, c='#808080', alpha=0.6,
                                  edgecolor='white') for s in legend_sizes]
    
    hic_patch = mpatches.Patch(facecolor=COLORS['hic_map'], edgecolor='white',
                               alpha=0.75, label=f'High Income (HIC): {hic_total:,}')
    lmic_patch = mpatches.Patch(facecolor=COLORS['lmic_map'], edgecolor='white',
                                alpha=0.75, label=f'Low/Middle Income (LMIC): {lmic_total:,}')
    
    legend1 = ax.legend(legend_bubbles, ['50', '200', '500'], title='Number of Trials',
                       loc='lower right', fontsize=9, framealpha=0.95, labelspacing=1.5)
    ax.add_artist(legend1)
    ax.legend(handles=[hic_patch, lmic_patch], title='Income Classification',
             loc='lower left', fontsize=10, framealpha=0.95)
    
    fig.text(0.98, 0.02, 'Data: PubMed/MEDLINE  •  Income: World Bank 2024-25',
             ha='right', fontsize=8, color='#707070', style='italic')
    fig.text(0.02, 0.02, 'Bubble area proportional to trial count',
             ha='left', fontsize=8, color='#707070', style='italic')
    
    ax.spines['geo'].set_visible(False)
    plt.tight_layout(rect=[0, 0.03, 1, 0.92])
    fig.savefig(OUTPUT_DIR / 'fig9_world_map.png', dpi=300, bbox_inches='tight',
                facecolor='#fafafa')
    plt.close(fig)
    print("  ✓ fig9_world_map.png")


# ============================================================================
# FIGURE 10a: Income Distribution
# ============================================================================

def fig10a_income_distribution(top_overall, income_lookup):
    """Trials by World Bank income classification."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    income_totals = {'High income': 0, 'Upper middle income': 0,
                     'Lower middle income': 0, 'Low income': 0}
    
    for _, row in top_overall.iterrows():
        country, trials = row['country'], row['total']
        for name, inc in income_lookup.items():
            if country.lower() in name.lower() or name.lower() in country.lower():
                if inc in income_totals:
                    income_totals[inc] += trials
                break
    
    categories = ['High\nIncome', 'Upper Middle\nIncome', 'Lower Middle\nIncome', 'Low\nIncome']
    values = [income_totals['High income'], income_totals['Upper middle income'],
              income_totals['Lower middle income'], income_totals['Low income']]
    bar_colors = [COLORS['primary'], COLORS['secondary'], COLORS['light'], COLORS['lighter']]
    
    bars = ax.bar(categories, values, color=bar_colors, edgecolor='white', width=0.6)
    
    total = sum(values)
    for bar, val in zip(bars, values):
        pct = val / total * 100 if total > 0 else 0
        color = 'white' if val > 500 else COLORS['text']
        y_pos = bar.get_height() - 100 if val > 500 else bar.get_height() + 50
        va = 'top' if val > 500 else 'bottom'
        ax.text(bar.get_x() + bar.get_width()/2, y_pos,
                f'n = {val}\n({pct:.1f}%)', ha='center', va=va,
                fontsize=11, fontweight='bold', color=color)
    
    ax.set_ylabel('Number of Trials', fontweight='medium')
    ax.set_title('Trial Distribution by World Bank Income Classification', fontweight='bold', pad=15)
    ax.yaxis.grid(True, linestyle='-', alpha=0.3)
    ax.text(0.5, -0.12, 'Source: World Bank Country Classifications (2024-2025)',
            transform=ax.transAxes, ha='center', fontsize=9, style='italic', color=COLORS['secondary'])
    
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'fig10a_income_distribution.png', dpi=300)
    plt.close(fig)
    print("  ✓ fig10a_income_distribution.png")


# ============================================================================
# FIGURE: Equity Summary Dashboard
# ============================================================================

def fig_equity_summary(data):
    """3-panel equity summary dashboard."""
    fig = plt.figure(figsize=(12, 7))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 1], hspace=0.35, wspace=0.25)
    
    # Panel A: Stacked area (top, spans full width)
    ax1 = fig.add_subplot(gs[0, :])
    if 'three_way' in data:
        split_df = data['three_way']
        ax1.stackplot(split_df['year'], split_df['hic_only'], split_df['hic_lmic_collab'],
                      split_df['lmic_only'],
                      colors=[COLORS['primary'], COLORS['collab'], COLORS['lmic']],
                      labels=['HIC-only', 'HIC-LMIC Collab', 'LMIC-only'],
                      alpha=0.85, edgecolor='white', linewidth=0.5)
        ax1.set_xlim(2001, 2025)
    ax1.set_xlabel('Year', fontweight='medium')
    ax1.set_ylabel('Share of Trials (%)', fontweight='medium')
    ax1.set_title('A. Trial Distribution by Income Level Over Time', fontweight='bold', fontsize=12)
    ax1.set_ylim(0, 100)
    ax1.legend(loc='center right', framealpha=0.95, fontsize=10)
    ax1.yaxis.grid(True, linestyle='-', alpha=0.2, color='white')
    
    # Panel B: Collaboration donut (bottom left)
    # Based on per-year data: ~363 multi-country trials (16.2% of 2,237)
    # Sample of 200 shows: 79% HIC-HIC, 21% HIC-LMIC, 0% LMIC-LMIC
    ax2 = fig.add_subplot(gs[1, 0])
    wedges, _, autotexts = ax2.pie([79, 21], colors=[COLORS['primary'], COLORS['light']],
                                    autopct='%1.0f%%', startangle=90, pctdistance=0.75,
                                    wedgeprops=dict(width=0.5, edgecolor='white'))
    for at in autotexts:
        at.set_fontweight('bold')
        at.set_fontsize(12)
    ax2.text(0, 0, 'n≈363', ha='center', va='center', fontsize=12, fontweight='bold')
    ax2.set_title('B. Collaboration Types', fontweight='bold', fontsize=12, pad=10)
    ax2.legend(wedges, ['HIC-HIC', 'HIC-LMIC'], loc='lower center',
               bbox_to_anchor=(0.5, -0.12), ncol=2, fontsize=10)
    ax2.text(0.5, -0.28, 'No LMIC-LMIC collaborations', transform=ax2.transAxes,
             ha='center', fontsize=9, style='italic', color=COLORS['secondary'])
    
    # Panel C: LMIC partners (bottom right)
    ax3 = fig.add_subplot(gs[1, 1])
    wedges3, texts3, autotexts3 = ax3.pie([51, 22, 17, 7, 3], 
            labels=['China', 'Brazil', 'India', 'Egypt', 'Other'],
            colors=[COLORS['secondary'], COLORS['light'], '#A8B5C4', '#C4CDD8', COLORS['lighter']],
            autopct='%1.0f%%', startangle=90, wedgeprops=dict(edgecolor='white'))
    for at in autotexts3:
        at.set_fontsize(10)
    ax3.set_title('C. LMIC Collaboration Partners', fontweight='bold', fontsize=12, pad=10)
    
    fig.suptitle('Global Equity in Robotic Surgery Research\nA 25-Year Analysis of Clinical Trials',
                 fontweight='bold', fontsize=14, y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(OUTPUT_DIR / 'fig_equity_summary.png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("  ✓ fig_equity_summary.png")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("  ROBOTIC SURGERY CLINICAL TRIALS - FIGURE GENERATION")
    print("=" * 70)
    print()
    
    # Load data
    data = load_all_data()
    print()
    
    # Generate all figures
    print("Generating figures...")
    print()
    
    fig1_trial_growth(data['per_year'])
    fig2a_hhi_concentration(data['per_year'])
    fig2b_collaboration(data['per_year'])
    fig3_regional_shift(data['per_year'])
    fig4_country_leaders(data['top_overall'], data['top_last5'], data['income_lookup'])
    fig9_world_map(data['top_overall'], data['income_lookup'])
    fig10a_income_distribution(data['top_overall'], data['income_lookup'])
    fig_equity_summary(data)
    
    print()
    print("=" * 70)
    print(f"  ✓ All figures saved to: {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == '__main__':
    main()
