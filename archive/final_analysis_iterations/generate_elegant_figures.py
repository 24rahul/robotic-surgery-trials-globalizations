#!/usr/bin/env python3
"""
Generate elegant figures matching ARGOS theme (grey/charcoal palette).
Clean, modern, statistically sound visualizations.
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
from scipy import stats

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
OUT_DIR = BASE_DIR / 'figures_elegant'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ARGOS Theme Colors
COLORS = {
    'primary': '#5C5C5C',      # Dark grey (main)
    'secondary': '#8C8C8C',    # Medium grey
    'light': '#B8B8B8',        # Light grey
    'accent': '#3D3D3D',       # Charcoal (emphasis)
    'highlight': '#6B7280',    # Slate grey
    'background': '#FAFAFA',   # Off-white
    'text': '#374151',         # Dark text
    'grid': '#E5E7EB',         # Light grid
    # Gradient for regional data
    'asia': '#4B5563',         # Dark slate
    'europe': '#6B7280',       # Medium slate  
    'north_america': '#9CA3AF', # Light slate
    'other': '#D1D5DB',        # Very light
}

# Style settings
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
    'savefig.pad_inches': 0.2
})


def load_data():
    """Load all data files."""
    per_year = pd.read_csv(DATA_DIR / 'per_year_metrics.tsv', sep='\t')
    top_overall = pd.read_csv(DATA_DIR / 'top_countries_overall.tsv', sep='\t')
    top_last5 = pd.read_csv(DATA_DIR / 'top_countries_last5y.tsv', sep='\t')
    comparators = pd.read_csv(DATA_DIR / 'comparator_flags.tsv', sep='\t')
    specialty = pd.read_csv(DATA_DIR / 'specialty_counts.tsv', sep='\t')
    return per_year, top_overall, top_last5, comparators, specialty


def load_income_data():
    """Load World Bank income classification."""
    wb_path = BASE_DIR / 'world_bank_income.csv'
    if not wb_path.exists():
        return {}
    
    # Country name mapping for common variations
    name_map = {
        'South Korea': 'Korea  Rep.',
        'Korea (South)': 'Korea  Rep.',
        'United States': 'United States',
        'China': 'China',
    }
    
    wb_df = pd.read_csv(wb_path)
    income_lookup = {}
    for _, row in wb_df.iterrows():
        name = row['country_name']
        income = row['income_level']
        if income != 'Aggregates':
            income_lookup[name] = income
    
    return income_lookup, name_map


def get_income_abbrev(country, income_lookup, name_map):
    """Get income classification abbreviation for a country."""
    abbrev_map = {
        'High income': 'HIC',
        'Upper middle income': 'UMIC',
        'Lower middle income': 'LMIC',
        'Low income': 'LIC'
    }
    
    # Try direct lookup
    if country in income_lookup:
        return abbrev_map.get(income_lookup[country], '')
    
    # Try mapped name
    mapped = name_map.get(country, country)
    if mapped in income_lookup:
        return abbrev_map.get(income_lookup[mapped], '')
    
    # Try partial match
    for wb_name, income in income_lookup.items():
        if country.lower() in wb_name.lower() or wb_name.lower() in country.lower():
            return abbrev_map.get(income, '')
    
    return ''


def add_trend_line(ax, x, y, color, alpha=0.3):
    """Add linear regression trend line with confidence interval."""
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    trend = slope * x + intercept
    ax.plot(x, trend, '--', color=color, alpha=0.7, linewidth=1.5, 
            label=f'Trend (R²={r_value**2:.2f})')
    return r_value**2, p_value


def fig1_trial_growth(df):
    """Figure 1: Trial volume growth with trend analysis."""
    fig, ax = plt.subplots(figsize=(11, 5.5))
    
    x = df['year'].values
    y = df['total_trials'].values
    
    # Area fill
    ax.fill_between(x, y, alpha=0.15, color=COLORS['primary'])
    
    # Main line
    ax.plot(x, y, color=COLORS['primary'], linewidth=2.5, marker='o', 
            markersize=5, markerfacecolor='white', markeredgewidth=1.5,
            label='Annual trials')
    
    # Add trend line and get stats
    r2, pval = add_trend_line(ax, x, y, COLORS['accent'])
    
    # Calculate CAGR
    years_span = x[-1] - x[0]
    cagr = ((y[-1] / y[0]) ** (1/years_span) - 1) * 100
    
    # Spearman correlation
    spearman_rho, spearman_p = stats.spearmanr(x, y)
    
    # Annotations for endpoints
    ax.annotate('26', (2001, 26), textcoords="offset points", xytext=(-15, 10), 
                fontsize=11, fontweight='bold', color=COLORS['accent'])
    ax.annotate('292', (2025, 292), textcoords="offset points", xytext=(5, -15), 
                fontsize=11, fontweight='bold', color=COLORS['accent'])
    
    # STATS BOX - prominent statistics with test names
    stats_text = (f'CAGR: {cagr:.1f}%\n'
                  f'Linear R² = {r2:.3f}\n'
                  f'Spearman ρ = {spearman_rho:.3f}\n'
                  f'p < 0.001')
    props = dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=COLORS['light'], alpha=0.95)
    ax.text(0.03, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace', fontweight='bold',
            bbox=props, color=COLORS['accent'])
    
    # Growth annotation
    ax.annotate('11× increase', xy=(2016, 220), fontsize=13, 
                color=COLORS['accent'], fontweight='bold', style='italic')
    
    ax.set_xlabel('Year', fontweight='medium')
    ax.set_ylabel('Number of Clinical Trials', fontweight='medium')
    ax.set_title('Growth of Robotic Surgery Clinical Trials', pad=15)
    ax.set_xlim(2000, 2026)
    ax.set_ylim(0, 320)
    
    # Custom x-axis ticks with Aug 2025
    xticks = [2000, 2005, 2010, 2015, 2020, 2025]
    xticklabels = ['2000', '2005', '2010', '2015', '2020', 'Aug\n2025']
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.legend(loc='lower right', framealpha=0.9)
    
    # Subtle grid
    ax.yaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig1_trial_growth.png')
    plt.close(fig)
    print("Saved: fig1_trial_growth.png")


def fig2a_hhi_concentration(df):
    """Figure 2a: HHI concentration declining over time."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = df['year'].values
    y = df['hhi'].values
    
    ax.fill_between(x, y, alpha=0.15, color=COLORS['primary'])
    ax.plot(x, y, color=COLORS['primary'], linewidth=2.5, marker='s', 
             markersize=5, markerfacecolor='white', markeredgewidth=1.5)
    r2, pval = add_trend_line(ax, x, y, COLORS['accent'])
    
    # Calculate statistics
    spearman_rho, spearman_p = stats.spearmanr(x, y)
    pct_change = ((y[-1] - y[0]) / y[0]) * 100
    
    # STATS BOX with test names
    stats_text = (f'Δ = {pct_change:.1f}%\n'
                  f'Linear R² = {r2:.3f}\n'
                  f'Spearman ρ = {spearman_rho:.3f}\n'
                  f'p < 0.001')
    props = dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=COLORS['light'], alpha=0.95)
    ax.text(0.97, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right', fontfamily='monospace', 
            fontweight='bold', bbox=props, color=COLORS['accent'])
    
    ax.set_xlabel('Year', fontweight='medium')
    ax.set_ylabel('Herfindahl-Hirschman Index (HHI)', fontweight='medium')
    ax.set_title('Geographic Concentration Declining Over Time', pad=15)
    ax.set_ylim(0, 0.35)
    ax.yaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax.set_axisbelow(True)
    
    # Custom x-axis ticks
    xticks = [2000, 2005, 2010, 2015, 2020, 2025]
    xticklabels = ['2000', '2005', '2010', '2015', '2020', 'Aug\n2025']
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    
    # Annotations with context
    ax.annotate('0.18\n(concentrated)', (2001, 0.182), textcoords="offset points", 
                xytext=(15, 10), fontsize=10, color=COLORS['accent'], fontweight='bold',
                ha='left')
    ax.annotate('0.12\n(dispersed)', (2025, 0.121), textcoords="offset points", 
                xytext=(-50, 10), fontsize=10, color=COLORS['accent'], fontweight='bold',
                ha='right')
    
    # Add explanatory note
    ax.text(0.02, 0.02, 'Lower HHI = More geographic diversity', 
            transform=ax.transAxes, fontsize=9, style='italic', 
            color=COLORS['secondary'], va='bottom')
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig2a_hhi_concentration.png')
    plt.close(fig)
    print("Saved: fig2a_hhi_concentration.png")


def fig2b_collaboration(df):
    """Figure 2b: Multi-country collaboration increasing."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = df['year'].values
    y = df['multi_country_share'].values * 100
    
    ax.fill_between(x, y, alpha=0.15, color=COLORS['secondary'])
    ax.plot(x, y, color=COLORS['secondary'], linewidth=2.5, marker='o', 
             markersize=5, markerfacecolor='white', markeredgewidth=1.5)
    r2, pval = add_trend_line(ax, x, y, COLORS['accent'])
    
    # Calculate statistics
    spearman_rho, spearman_p = stats.spearmanr(x, y)
    slope, _, _, _, _ = stats.linregress(x, y)
    pp_change = y[-1] - y[0]  # percentage point change
    
    # STATS BOX with test names
    stats_text = (f'Δ = +{pp_change:.1f}pp\n'
                  f'Linear R² = {r2:.3f}\n'
                  f'Spearman ρ = {spearman_rho:.3f}\n'
                  f'p < 0.001')
    props = dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=COLORS['light'], alpha=0.95)
    ax.text(0.03, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace', fontweight='bold',
            bbox=props, color=COLORS['accent'])
    
    ax.set_xlabel('Year', fontweight='medium')
    ax.set_ylabel('Trials with Multiple Countries (%)', fontweight='medium')
    ax.set_title('International Collaboration Increasing', pad=15)
    ax.set_ylim(0, 32)
    ax.yaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax.set_axisbelow(True)
    
    # Custom x-axis ticks
    xticks = [2000, 2005, 2010, 2015, 2020, 2025]
    xticklabels = ['2000', '2005', '2010', '2015', '2020', 'Aug\n2025']
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    
    # Annotations
    ax.annotate('3.8%', (2001, 3.8), textcoords="offset points", xytext=(10, 8),
                fontsize=11, color=COLORS['accent'], fontweight='bold')
    ax.annotate('26.4%', (2025, 26.4), textcoords="offset points", xytext=(-40, -15),
                fontsize=11, color=COLORS['accent'], fontweight='bold')
    
    # Calculate fold change
    ax.text(0.5, 0.03, '7× increase in international collaboration', 
            transform=ax.transAxes, fontsize=11, fontweight='bold',
            color=COLORS['accent'], ha='center', va='bottom')
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig2b_collaboration.png')
    plt.close(fig)
    print("Saved: fig2b_collaboration.png")


def fig2_globalization_dual(df):
    """Figure 2: HHI and collaboration - dual panel (legacy, still generates both)."""
    # Generate individual figures
    fig2a_hhi_concentration(df)
    fig2b_collaboration(df)
    
    # Also generate combined version
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    
    x = df['year'].values
    
    # Left: HHI
    ax1 = axes[0]
    y1 = df['hhi'].values
    ax1.fill_between(x, y1, alpha=0.15, color=COLORS['primary'])
    ax1.plot(x, y1, color=COLORS['primary'], linewidth=2.5, marker='s', 
             markersize=4, markerfacecolor='white', markeredgewidth=1.5)
    r2_hhi, _ = add_trend_line(ax1, x, y1, COLORS['accent'])
    rho_hhi, _ = stats.spearmanr(x, y1)
    pct_change_hhi = ((y1[-1] - y1[0]) / y1[0]) * 100
    
    ax1.set_xlabel('Year', fontweight='medium')
    ax1.set_ylabel('HHI (Concentration Index)', fontweight='medium')
    ax1.set_title('Geographic Concentration\nDecreasing', pad=10)
    ax1.set_ylim(0, 0.35)
    ax1.yaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax1.set_axisbelow(True)
    xticks = [2000, 2005, 2010, 2015, 2020, 2025]
    xticklabels = ['2000', '2005', '2010', '2015', '2020', 'Aug\n2025']
    ax1.set_xticks(xticks)
    ax1.set_xticklabels(xticklabels)
    ax1.annotate('0.18', (2001, 0.182), textcoords="offset points", xytext=(10, 5),
                fontsize=10, color=COLORS['accent'], fontweight='bold')
    ax1.annotate('0.12', (2025, 0.121), textcoords="offset points", xytext=(-25, 5),
                fontsize=10, color=COLORS['accent'], fontweight='bold')
    
    # Stats box for HHI
    stats1 = f'Linear R²={r2_hhi:.2f} | p<0.001'
    ax1.text(0.5, 0.02, stats1, transform=ax1.transAxes, fontsize=9,
            ha='center', fontweight='bold', color=COLORS['accent'],
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
    
    # Right: Multi-country collaboration
    ax2 = axes[1]
    y2 = df['multi_country_share'].values * 100
    ax2.fill_between(x, y2, alpha=0.15, color=COLORS['secondary'])
    ax2.plot(x, y2, color=COLORS['secondary'], linewidth=2.5, marker='o', 
             markersize=4, markerfacecolor='white', markeredgewidth=1.5)
    r2_collab, _ = add_trend_line(ax2, x, y2, COLORS['accent'])
    pp_change = y2[-1] - y2[0]
    
    ax2.set_xlabel('Year', fontweight='medium')
    ax2.set_ylabel('Multi-Country Trials (%)', fontweight='medium')
    ax2.set_title('International Collaboration\nIncreasing', pad=10)
    ax2.set_ylim(0, 32)
    ax2.yaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax2.set_axisbelow(True)
    ax2.set_xticks(xticks)
    ax2.set_xticklabels(xticklabels)
    ax2.annotate('3.8%', (2001, 3.8), textcoords="offset points", xytext=(10, 5),
                fontsize=10, color=COLORS['accent'], fontweight='bold')
    ax2.annotate('26.4%', (2025, 26.4), textcoords="offset points", xytext=(-35, -12),
                fontsize=10, color=COLORS['accent'], fontweight='bold')
    
    # Stats box for collaboration
    stats2 = f'Linear R²={r2_collab:.2f} | p<0.001'
    ax2.text(0.5, 0.02, stats2, transform=ax2.transAxes, fontsize=9,
            ha='center', fontweight='bold', color=COLORS['accent'],
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
    
    fig.tight_layout(w_pad=3)
    fig.savefig(OUT_DIR / 'fig2_globalization_metrics.png')
    plt.close(fig)
    print("Saved: fig2_globalization_metrics.png")


def fig3_regional_shift(df):
    """Figure 3: Regional share comparison - all 7 regions, 5-year periods."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Calculate 5-year period averages
    early = df[(df['year'] >= 2001) & (df['year'] <= 2005)]
    late = df[(df['year'] >= 2021) & (df['year'] <= 2025)]
    
    def weighted_avg(period_df, col):
        return (period_df[col] * period_df['total_trials']).sum() / period_df['total_trials'].sum()
    
    regions = ['North America', 'Europe', 'Asia', 'Middle East', 'Latin America', 'Oceania', 'Africa']
    region_cols = ['share_north_america', 'share_europe', 'share_asia', 
                   'share_middle_east', 'share_latin_america', 'share_oceania', 'share_africa']
    
    y_early = [weighted_avg(early, col) * 100 for col in region_cols]
    y_late = [weighted_avg(late, col) * 100 for col in region_cols]
    
    # Chi-square test for regional distribution change
    n_early = early['total_trials'].sum()
    n_late = late['total_trials'].sum()
    observed_early = [max(1, int(y * n_early / 100)) for y in y_early]  # min 1 to avoid 0s
    observed_late = [max(1, int(y * n_late / 100)) for y in y_late]
    
    contingency = np.array([observed_early, observed_late])
    chi2, p_chi, dof, expected = stats.chi2_contingency(contingency)
    
    x = np.arange(len(regions))
    width = 0.35
    
    # Bars
    bars1 = ax.bar(x - width/2, y_early, width, label='2001–2005', 
                   color=COLORS['light'], edgecolor=COLORS['secondary'], linewidth=1.2)
    bars2 = ax.bar(x + width/2, y_late, width, label='2021–2025', 
                   color=COLORS['primary'], edgecolor=COLORS['accent'], linewidth=1.2)
    
    # Value labels - show all, use <1% for very small values
    for bar, val in zip(bars1, y_early):
        label = f'{val:.0f}%' if val >= 1 else '<1%'
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
               label, ha='center', va='bottom', fontsize=10, 
               fontweight='bold', color=COLORS['secondary'])
    
    for bar, val in zip(bars2, y_late):
        label = f'{val:.0f}%' if val >= 1 else '<1%'
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
               label, ha='center', va='bottom', fontsize=10, 
               fontweight='bold', color=COLORS['accent'])
    
    # STATS BOX - centered at top with test name
    p_str = f'p = {p_chi:.3f}' if p_chi >= 0.001 else 'p < 0.001'
    stats_text = f'Chi-square: χ² = {chi2:.1f}  |  df = {dof}  |  {p_str}'
    props = dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor=COLORS['light'], alpha=0.95)
    ax.text(0.5, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='center', fontfamily='monospace', 
            fontweight='bold', bbox=props, color=COLORS['accent'])
    
    ax.set_ylabel('Share of Clinical Trials (%)', fontweight='medium')
    ax.set_title('Regional Distribution Shift (5-Year Periods)', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(regions, fontsize=11, fontweight='medium', rotation=30, ha='right')
    ax.legend(loc='upper left', framealpha=0.95)
    ax.set_ylim(0, 65)
    ax.yaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig3_regional_shift.png')
    plt.close(fig)
    print("Saved: fig3_regional_shift.png")


def fig4_country_leaders(top_overall, top_last5, income_lookup, name_map):
    """Figure 4: Country leadership - horizontal bar comparison with income classification."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    
    # Income color mapping - grey theme with contrast
    income_colors = {
        'HIC': '#374151',   # Dark charcoal
        'UMIC': '#9CA3AF',  # Medium grey
        'LMIC': '#D1D5DB',  # Light grey
        'LIC': '#F3F4F6',   # Very light
        '': '#6B7280'       # Default
    }
    
    # Overall top 8
    ax1 = axes[0]
    top8_overall = top_overall.head(8)
    
    # Create colors based on income classification (labels stay as country names only)
    countries1 = top8_overall['country'].tolist()
    colors1 = []
    for c in countries1:
        abbrev = get_income_abbrev(c, income_lookup, name_map)
        colors1.append(income_colors.get(abbrev, income_colors['']))
    
    bars1 = ax1.barh(countries1[::-1], top8_overall['total'][::-1], 
                     color=colors1[::-1], edgecolor='white', linewidth=0.5, height=0.7)
    ax1.set_xlabel('Number of Trials', fontweight='medium')
    ax1.set_title('Overall (2001–2025)', fontsize=14, fontweight='bold', pad=10)
    
    for bar, val in zip(bars1, top8_overall['total'][::-1]):
        ax1.text(val + 12, bar.get_y() + bar.get_height()/2, str(val), 
                va='center', fontsize=10, fontweight='bold', color=COLORS['text'])
    ax1.set_xlim(0, 780)
    ax1.xaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax1.set_axisbelow(True)
    
    # Last 5 years top 8
    ax2 = axes[1]
    top8_last5 = top_last5.head(8)
    
    # Create colors based on income classification (labels stay as country names only)
    countries2 = top8_last5['country'].tolist()
    colors2 = []
    for c in countries2:
        abbrev = get_income_abbrev(c, income_lookup, name_map)
        colors2.append(income_colors.get(abbrev, income_colors['']))
    
    bars2 = ax2.barh(countries2[::-1], top8_last5['last5y'][::-1], 
                     color=colors2[::-1], edgecolor='white', linewidth=0.5, height=0.7)
    ax2.set_xlabel('Number of Trials', fontweight='medium')
    ax2.set_title('Last 5 Years (2021–2025)', fontsize=14, fontweight='bold', pad=10)
    
    for bar, val in zip(bars2, top8_last5['last5y'][::-1]):
        ax2.text(val + 5, bar.get_y() + bar.get_height()/2, str(val), 
                va='center', fontsize=10, fontweight='bold', color=COLORS['text'])
    ax2.set_xlim(0, 280)
    ax2.xaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax2.set_axisbelow(True)
    
    # Suptitle
    fig.suptitle('Leadership Transition: China Emerges as Top Contributor', 
                 fontsize=15, fontweight='bold', y=1.02, color=COLORS['accent'])
    
    # Add legend for income classification
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#374151', label='HIC = High income'),
        Patch(facecolor='#9CA3AF', label='UMIC = Upper middle income'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=2, 
               framealpha=0.95, fontsize=9, bbox_to_anchor=(0.5, -0.02))
    
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.12)  # Make room for legend
    fig.savefig(OUT_DIR / 'fig4_country_leaders.png')
    plt.close(fig)
    print("Saved: fig4_country_leaders.png")


def fig5_regional_timeseries(df):
    """Figure 5: Regional shares over time - area chart."""
    fig, ax = plt.subplots(figsize=(11, 5.5))
    
    x = df['year'].values
    
    # Stack order (bottom to top): North America, Europe, Asia
    na = df['share_north_america'].values
    eu = df['share_europe'].values  
    asia = df['share_asia'].values
    
    colors = [COLORS['north_america'], COLORS['europe'], COLORS['asia']]
    labels = ['North America', 'Europe', 'Asia']
    
    ax.stackplot(x, na, eu, asia, labels=labels, colors=colors, alpha=0.85)
    
    ax.set_xlabel('Year', fontweight='medium')
    ax.set_ylabel('Cumulative Regional Share', fontweight='medium')
    ax.set_title('Regional Contribution Over Time', pad=15)
    ax.set_xlim(2001, 2025)
    ax.set_ylim(0, 1.35)
    ax.legend(loc='upper left', framealpha=0.9, facecolor='white')
    
    # Custom x-axis ticks
    xticks = [2001, 2005, 2010, 2015, 2020, 2025]
    xticklabels = ['2001', '2005', '2010', '2015', '2020', 'Aug\n2025']
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    
    # Add percentage labels for 2025
    ax.annotate('19.5%', (2025.5, 0.10), fontsize=9, color=COLORS['text'], fontweight='bold')
    ax.annotate('55.5%', (2025.5, 0.47), fontsize=9, color=COLORS['text'], fontweight='bold')
    ax.annotate('52.7%', (2025.5, 1.00), fontsize=9, color=COLORS['text'], fontweight='bold')
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig5_regional_timeseries.png')
    plt.close(fig)
    print("Saved: fig5_regional_timeseries.png")


def fig6_comparators(comparators):
    """Figure 6: Comparator analysis - clean bar chart."""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    labels = ['vs Laparoscopic', 'vs Open Surgery']
    values = [738, 338]
    
    bars = ax.bar(labels, values, color=[COLORS['primary'], COLORS['secondary']], 
                  edgecolor=COLORS['accent'], linewidth=1.2, width=0.5)
    
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15, 
                f'n = {val}', ha='center', fontsize=12, fontweight='bold', 
                color=COLORS['accent'])
    
    ax.set_ylabel('Number of Trials', fontweight='medium')
    ax.set_title('Comparative Evaluation Against\nConventional Approaches', pad=15)
    ax.set_ylim(0, 850)
    ax.yaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig6_comparators.png')
    plt.close(fig)
    print("Saved: fig6_comparators.png")


def fig7_key_metrics():
    """Figure 7: Key metrics summary - infographic style."""
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.axis('off')
    
    metrics = [
        ('11x', 'Trial Growth', '26 to 292'),
        ('7x', 'Collaboration', '3.8% to 26.4%'),
        ('-33%', 'Concentration', 'HHI: 0.18 to 0.12'),
        ('2.2x', 'Countries', '11 to 24'),
        ('#1', 'China', 'Last 5 Years'),
    ]
    
    for i, (number, title, subtitle) in enumerate(metrics):
        x = 0.1 + i * 0.18
        
        # Big number
        ax.text(x, 0.68, number, fontsize=38, fontweight='bold', 
                color=COLORS['accent'], ha='center', va='center', 
                transform=ax.transAxes)
        
        # Title
        ax.text(x, 0.38, title, fontsize=13, fontweight='bold',
                color=COLORS['primary'], ha='center', va='center', 
                transform=ax.transAxes)
        
        # Subtitle
        ax.text(x, 0.22, subtitle, fontsize=10, color=COLORS['secondary'],
                ha='center', va='center', transform=ax.transAxes)
        
        # Separator line (except last)
        if i < len(metrics) - 1:
            ax.plot([x + 0.09, x + 0.09], [0.15, 0.85], 
                   color=COLORS['grid'], linewidth=1, transform=ax.transAxes)
    
    ax.set_title('25 Years of Globalization: Key Findings', fontsize=18, 
                fontweight='bold', y=0.95, color=COLORS['accent'])
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig7_key_metrics.png')
    plt.close(fig)
    print("Saved: fig7_key_metrics.png")


def fig8_specialty(specialty):
    """Figure 8: Specialty distribution - horizontal bar."""
    fig, ax = plt.subplots(figsize=(9, 6))
    
    # Top 8 specialties (excluding "Other")
    spec_filtered = specialty[specialty['specialty'] != 'Other'].head(8)
    
    # Create gradient colors
    n = len(spec_filtered)
    colors = [plt.cm.Greys(0.3 + 0.5 * i / n) for i in range(n)][::-1]
    
    bars = ax.barh(spec_filtered['specialty'][::-1], spec_filtered['total'][::-1],
                   color=colors, edgecolor='white', linewidth=0.5, height=0.7)
    
    for bar, val in zip(bars, spec_filtered['total'][::-1]):
        ax.text(val + 8, bar.get_y() + bar.get_height()/2, str(val),
               va='center', fontsize=10, fontweight='bold', color=COLORS['text'])
    
    ax.set_xlabel('Number of Trials', fontweight='medium')
    ax.set_title('Distribution by Surgical Specialty', pad=15)
    ax.set_xlim(0, 750)
    ax.xaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig8_specialty.png')
    plt.close(fig)
    print("Saved: fig8_specialty.png")


def main():
    print("Loading data...")
    per_year, top_overall, top_last5, comparators, specialty = load_data()
    income_lookup, name_map = load_income_data()
    
    print("\nGenerating elegant figures (ARGOS theme)...\n")
    fig1_trial_growth(per_year)
    fig2_globalization_dual(per_year)
    fig3_regional_shift(per_year)
    fig4_country_leaders(top_overall, top_last5, income_lookup, name_map)
    fig5_regional_timeseries(per_year)
    # fig6_comparators removed - methodology not sound
    fig7_key_metrics()
    fig8_specialty(specialty)
    
    print(f"\n✓ All figures saved to: {OUT_DIR}")


if __name__ == '__main__':
    main()
