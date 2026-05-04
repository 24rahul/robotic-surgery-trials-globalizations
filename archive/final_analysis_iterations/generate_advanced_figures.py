#!/usr/bin/env python3
"""
Advanced figures with statistical analysis and world map visualization.
Uses official World Bank income classification data.
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
OUT_DIR = BASE_DIR / 'figures_elegant'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ARGOS Theme Colors
COLORS = {
    'primary': '#5C5C5C',
    'secondary': '#8C8C8C',
    'light': '#B8B8B8',
    'accent': '#3D3D3D',
    'highlight': '#6B7280',
    'background': '#FAFAFA',
    'text': '#374151',
    'grid': '#E5E7EB',
    'hic': '#4B5563',
    'lmic': '#9CA3AF',
}

# Country name mapping (our data -> World Bank names)
COUNTRY_NAME_MAP = {
    'United Kingdom': 'United Kingdom',
    'England': 'United Kingdom',
    'Scotland': 'United Kingdom', 
    'Wales': 'United Kingdom',
    'Korea (South)': 'Korea  Rep.',
    'South Korea': 'Korea  Rep.',
    'Russia': 'Russian Federation',
    'Russia (Federation)': 'Russian Federation',
    'China (Republic : 1949- )': 'Taiwan, China',
    'Taiwan': 'Taiwan, China',
    'Hong Kong': 'Hong Kong SAR, China',
    'Iran': 'Iran, Islamic Rep.',
    'Egypt': 'Egypt, Arab Rep.',
    'Venezuela': 'Venezuela, RB',
    'Syria': 'Syrian Arab Republic',
    'Czech Republic': 'Czechia',
}

# Country coordinates for map plotting
COUNTRY_COORDS = {
    'United States': (39.8, -98.5),
    'China': (35.0, 105.0),
    'United Kingdom': (54.0, -2.0),
    'Germany': (51.0, 9.0),
    'Korea, Rep.': (36.5, 127.5),
    'South Korea': (36.5, 127.5),
    'Italy': (42.5, 12.5),
    'Japan': (36.0, 138.0),
    'France': (46.0, 2.0),
    'Netherlands': (52.5, 5.75),
    'Canada': (56.0, -106.0),
    'Denmark': (56.0, 10.0),
    'Sweden': (62.0, 15.0),
    'Switzerland': (47.0, 8.0),
    'Turkey': (39.0, 35.0),
    'Spain': (40.0, -4.0),
    'India': (22.0, 78.0),
    'Brazil': (-10.0, -55.0),
    'Australia': (-25.0, 135.0),
    'Israel': (31.0, 35.0),
    'Finland': (64.0, 26.0),
    'Singapore': (1.3, 103.8),
    'Taiwan': (23.5, 121.0),
    'Hong Kong': (22.3, 114.2),
    'Norway': (62.0, 10.0),
    'New Zealand': (-41.0, 174.0),
    'Egypt': (27.0, 30.0),
    'Iran': (32.0, 53.0),
    'Russian Federation': (60.0, 100.0),
    'Russia': (60.0, 100.0),
    'South Africa': (-29.0, 24.0),
    'Poland': (52.0, 20.0),
    'Ireland': (53.5, -8.0),
    'Belgium': (50.8, 4.0),
    'Austria': (47.5, 14.5),
    'Greece': (39.0, 22.0),
    'Portugal': (39.5, -8.0),
    'Czechia': (50.0, 15.5),
    'Hungary': (47.0, 20.0),
    'Romania': (46.0, 25.0),
    'Serbia': (44.0, 21.0),
}

plt.rcParams.update({
    'figure.facecolor': COLORS['background'],
    'axes.facecolor': COLORS['background'],
    'savefig.facecolor': COLORS['background'],
    'font.family': 'sans-serif',
    'font.size': 12,
    'axes.titlesize': 16,
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 150,
    'savefig.dpi': 300,
})


def load_world_bank_data():
    """Load official World Bank income classification (full 4-category)."""
    wb_path = BASE_DIR / 'world_bank_income.csv'
    if not wb_path.exists():
        raise FileNotFoundError("World Bank data not found. Run the download script first.")
    
    wb_df = pd.read_csv(wb_path)
    
    # Create lookup dictionary with full income level
    income_lookup = {}
    for _, row in wb_df.iterrows():
        name = row['country_name']
        income = row['income_level']
        
        # Skip aggregates
        if income == 'Aggregates':
            continue
            
        income_lookup[name] = income
    
    return income_lookup


def get_hic_lmic(income_level):
    """Convert full income classification to HIC/LMIC binary."""
    if income_level == 'High income':
        return 'HIC'
    elif income_level in ['Upper middle income', 'Lower middle income', 'Low income']:
        return 'LMIC'
    return 'Unknown'


def load_data():
    """Load all data files."""
    per_year = pd.read_csv(DATA_DIR / 'per_year_metrics.tsv', sep='\t')
    top_overall = pd.read_csv(DATA_DIR / 'top_countries_overall.tsv', sep='\t')
    top_last5 = pd.read_csv(DATA_DIR / 'top_countries_last5y.tsv', sep='\t')
    return per_year, top_overall, top_last5


def normalize_country(name):
    """Normalize country names to World Bank format."""
    return COUNTRY_NAME_MAP.get(name, name)


def get_income_class(country, income_lookup):
    """Get income classification for a country using World Bank data."""
    normalized = normalize_country(country)
    
    # Direct lookup
    if normalized in income_lookup:
        return income_lookup[normalized]
    
    # Try original name
    if country in income_lookup:
        return income_lookup[country]
    
    # Try partial matching for common variations
    for wb_name, classification in income_lookup.items():
        if country.lower() in wb_name.lower() or wb_name.lower() in country.lower():
            return classification
    
    return 'Unknown'


def fig_world_map(top_overall, income_lookup):
    """Create a world map bubble chart showing trial distribution."""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    plotted = []
    max_trials = top_overall['total'].max()
    
    hic_count = 0
    lmic_count = 0
    
    for _, row in top_overall.iterrows():
        country = row['country']
        trials = row['total']
        
        # Get coordinates
        coord_key = country
        for key in COUNTRY_COORDS:
            if country.lower() in key.lower() or key.lower() in country.lower():
                coord_key = key
                break
        
        if coord_key in COUNTRY_COORDS and country not in plotted:
            lat, lon = COUNTRY_COORDS[coord_key]
            size = (trials / max_trials) * 2000 + 50
            
            income_full = get_income_class(country, income_lookup)
            income_group = get_hic_lmic(income_full)
            color = COLORS['hic'] if income_group == 'HIC' else COLORS['lmic']
            
            if income_group == 'HIC':
                hic_count += trials
            else:
                lmic_count += trials
            
            ax.scatter(lon, lat, s=size, c=color, alpha=0.7, 
                      edgecolors='white', linewidth=0.5, zorder=3)
            
            if trials >= 100:
                ax.annotate(f'{country}\n({trials})', (lon, lat), 
                           fontsize=8, ha='center', va='bottom',
                           xytext=(0, 8), textcoords='offset points',
                           color=COLORS['text'], fontweight='bold')
            plotted.append(country)
    
    # Continent outlines
    ax.plot([-130, -60, -60, -130, -130], [25, 25, 55, 55, 25], 
            color=COLORS['grid'], linewidth=0.5, zorder=1)
    ax.plot([-80, -35, -35, -80, -80], [-55, -55, 10, 10, -55], 
            color=COLORS['grid'], linewidth=0.5, zorder=1)
    ax.plot([-10, 40, 40, -10, -10], [35, 35, 70, 70, 35], 
            color=COLORS['grid'], linewidth=0.5, zorder=1)
    ax.plot([-20, 50, 50, -20, -20], [-35, -35, 35, 35, -35], 
            color=COLORS['grid'], linewidth=0.5, zorder=1)
    ax.plot([40, 145, 145, 40, 40], [0, 0, 55, 55, 0], 
            color=COLORS['grid'], linewidth=0.5, zorder=1)
    ax.plot([110, 155, 155, 110, 110], [-45, -45, -10, -10, -45], 
            color=COLORS['grid'], linewidth=0.5, zorder=1)
    
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 80)
    ax.set_xlabel('Longitude', fontweight='medium')
    ax.set_ylabel('Latitude', fontweight='medium')
    ax.set_title('Global Distribution of Robotic Surgery Clinical Trials\n(Bubble Size = Trial Count; World Bank Income Classification)', pad=15)
    
    hic_patch = mpatches.Patch(color=COLORS['hic'], label='High Income Countries (World Bank)', alpha=0.7)
    lmic_patch = mpatches.Patch(color=COLORS['lmic'], label='Low & Middle Income Countries (World Bank)', alpha=0.7)
    ax.legend(handles=[hic_patch, lmic_patch], loc='lower left', framealpha=0.9)
    
    ax.set_facecolor('#f0f4f8')
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig9_world_map.png')
    plt.close(fig)
    print("Saved: fig9_world_map.png")


def fig10a_income_distribution(top_overall, income_lookup):
    """Figure 10a: Trial distribution by all 4 World Bank income categories."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Count trials by each income category
    income_totals = {
        'High income': 0,
        'Upper middle income': 0,
        'Lower middle income': 0,
        'Low income': 0
    }
    unknown_total = 0
    
    for _, row in top_overall.iterrows():
        country = row['country']
        trials = row['total']
        income = get_income_class(country, income_lookup)
        
        if income in income_totals:
            income_totals[income] += trials
        else:
            unknown_total += trials
    
    # Order from highest to lowest income
    categories = ['High income', 'Upper middle income', 'Lower middle income', 'Low income']
    values = [income_totals[cat] for cat in categories]
    total = sum(values)
    percentages = [v / total * 100 if total > 0 else 0 for v in values]
    
    # Colors - gradient from dark to light grey
    colors = ['#4B5563', '#6B7280', '#9CA3AF', '#D1D5DB']
    
    # Create bars
    x = range(len(categories))
    bars = ax.bar(x, values, color=colors, edgecolor=COLORS['accent'], linewidth=1.2, width=0.65)
    
    # Add value labels
    for bar, val, pct in zip(bars, values, percentages):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30, 
                f'n = {val}\n({pct:.1f}%)', ha='center', fontsize=11, 
                fontweight='bold', color=COLORS['accent'])
    
    # Styling
    ax.set_ylabel('Number of Trials', fontweight='medium')
    ax.set_title('Trial Distribution by World Bank Income Classification', fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(['High\nIncome', 'Upper Middle\nIncome', 'Lower Middle\nIncome', 'Low\nIncome'])
    ax.set_ylim(0, max(values) * 1.3)
    ax.yaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax.set_axisbelow(True)
    
    # Source note
    ax.text(0.5, -0.18, 'Source: World Bank Country Classifications (2024-2025)', 
            transform=ax.transAxes, fontsize=9, ha='center', style='italic',
            color=COLORS['secondary'])
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig10a_income_distribution.png')
    plt.close(fig)
    print("Saved: fig10a_income_distribution.png")
    
    # Print summary
    print(f"\n  Income breakdown:")
    for cat, val, pct in zip(categories, values, percentages):
        print(f"    {cat}: {val} trials ({pct:.1f}%)")
    if unknown_total > 0:
        print(f"    Unknown: {unknown_total} trials")


def fig10b_top_countries(top_overall, income_lookup):
    """Figure 10b: Top 10 countries colored by income classification."""
    fig, ax = plt.subplots(figsize=(11, 6))
    
    # Get top 10 countries
    top10 = top_overall.head(10).copy()
    
    countries = top10['country'].tolist()
    values = top10['total'].tolist()
    
    # Color mapping for all 4 income levels - grey theme with more contrast
    income_colors = {
        'High income': '#374151',        # Dark charcoal
        'Upper middle income': '#9CA3AF', # Medium grey (lighter, more distinct)
        'Lower middle income': '#D1D5DB', # Light grey
        'Low income': '#F3F4F6'           # Very light grey
    }
    
    # Abbreviations for income levels
    income_abbrev = {
        'High income': 'HIC',
        'Upper middle income': 'UMIC',
        'Lower middle income': 'LMIC',
        'Low income': 'LIC'
    }
    
    colors = []
    country_labels = []
    for c in countries:
        income = get_income_class(c, income_lookup)
        colors.append(income_colors.get(income, '#E5E7EB'))
        abbrev = income_abbrev.get(income, '')
        country_labels.append(f"{c} ({abbrev})" if abbrev else c)
    
    # Create horizontal bar chart with labeled y-axis
    bars = ax.barh(country_labels[::-1], values[::-1], color=colors[::-1], 
                   edgecolor='white', linewidth=0.5, height=0.7)
    
    # Add value labels
    for bar, val in zip(bars, values[::-1]):
        ax.text(val + 8, bar.get_y() + bar.get_height()/2, str(val),
                va='center', fontsize=10, fontweight='bold', color=COLORS['text'])
    
    ax.set_xlabel('Number of Trials', fontweight='medium')
    ax.set_title('Top 10 Countries by Trial Volume', fontweight='bold', pad=15)
    ax.set_xlim(0, max(values) * 1.15)
    ax.xaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax.set_axisbelow(True)
    
    # Add legend with matching colors
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#374151', label='HIC = High income'),
        Patch(facecolor='#9CA3AF', label='UMIC = Upper middle income'),
        Patch(facecolor='#D1D5DB', label='LMIC = Lower middle income'),
        Patch(facecolor='#F3F4F6', edgecolor='#9CA3AF', label='LIC = Low income')
    ]
    ax.legend(handles=legend_elements, loc='lower right', framealpha=0.95, fontsize=9)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig10b_top_countries.png')
    plt.close(fig)
    print("Saved: fig10b_top_countries.png")


def fig_statistical_summary(per_year):
    """Create a figure with key statistical tests and metrics."""
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    
    x = per_year['year'].values
    y_trials = per_year['total_trials'].values
    y_hhi = per_year['hhi'].values
    y_collab = per_year['multi_country_share'].values * 100
    y_countries = per_year['num_countries'].values
    
    # 1. Trial Growth with CAGR
    ax1 = axes[0, 0]
    years_span = x[-1] - x[0]
    cagr = ((y_trials[-1] / y_trials[0]) ** (1/years_span) - 1) * 100
    slope, intercept, r, p, se = stats.linregress(x, y_trials)
    
    ax1.fill_between(x, y_trials, alpha=0.15, color=COLORS['primary'])
    ax1.plot(x, y_trials, color=COLORS['primary'], linewidth=2.5, marker='o', markersize=4)
    ax1.plot(x, slope*x + intercept, '--', color=COLORS['accent'], linewidth=1.5, alpha=0.7)
    
    stats_text = f'CAGR: {cagr:.1f}%\nR² = {r**2:.3f}\np < 0.001'
    ax1.text(0.05, 0.95, stats_text, transform=ax1.transAxes, fontsize=11,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax1.set_xlabel('Year', fontweight='medium')
    ax1.set_ylabel('Annual Trials', fontweight='medium')
    ax1.set_title('Trial Volume Growth\n(Compound Annual Growth Rate)', pad=10)
    ax1.yaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    
    # 2. HHI trend
    ax2 = axes[0, 1]
    slope_hhi, _, r_hhi, p_hhi, _ = stats.linregress(x, y_hhi)
    trend_direction = "Decreasing" if slope_hhi < 0 else "Increasing"
    
    ax2.fill_between(x, y_hhi, alpha=0.15, color=COLORS['secondary'])
    ax2.plot(x, y_hhi, color=COLORS['secondary'], linewidth=2.5, marker='s', markersize=4)
    ax2.plot(x, slope_hhi*x + (y_hhi[0] - slope_hhi*x[0]), '--', 
            color=COLORS['accent'], linewidth=1.5, alpha=0.7)
    
    stats_text = f'Trend: {trend_direction}\nR² = {r_hhi**2:.3f}\np < 0.001'
    ax2.text(0.95, 0.95, stats_text, transform=ax2.transAxes, fontsize=11,
            verticalalignment='top', ha='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax2.set_xlabel('Year', fontweight='medium')
    ax2.set_ylabel('HHI', fontweight='medium')
    ax2.set_title('Geographic Concentration\n(Herfindahl-Hirschman Index)', pad=10)
    ax2.yaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    
    # 3. Collaboration rate
    ax3 = axes[1, 0]
    slope_c, intercept_c, r_c, p_c, se_c = stats.linregress(x, y_collab)
    
    ax3.fill_between(x, y_collab, alpha=0.15, color=COLORS['highlight'])
    ax3.plot(x, y_collab, color=COLORS['highlight'], linewidth=2.5, marker='o', markersize=4)
    ax3.plot(x, slope_c*x + intercept_c, '--', color=COLORS['accent'], linewidth=1.5, alpha=0.7)
    
    stats_text = f'Rate of increase:\n+{slope_c:.2f}%/year\nR² = {r_c**2:.3f}'
    ax3.text(0.05, 0.95, stats_text, transform=ax3.transAxes, fontsize=11,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax3.set_xlabel('Year', fontweight='medium')
    ax3.set_ylabel('Multi-Country Trials (%)', fontweight='medium')
    ax3.set_title('International Collaboration Rate\n(Annual Change)', pad=10)
    ax3.yaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    
    # 4. Summary statistics table
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    total_trials = y_trials.sum()
    mean_countries = y_countries.mean()
    rho_trials, _ = stats.spearmanr(x, y_trials)
    rho_hhi, _ = stats.spearmanr(x, y_hhi)
    rho_collab, _ = stats.spearmanr(x, y_collab)
    
    table_data = [
        ['Metric', 'Value', 'Statistic'],
        ['─' * 15, '─' * 12, '─' * 15],
        ['Total Trials (2001-2025)', f'{total_trials:,}', ''],
        ['CAGR (Trial Growth)', f'{cagr:.1f}%', f'p < 0.001'],
        ['Mean Countries/Year', f'{mean_countries:.1f}', ''],
        ['', '', ''],
        ['Spearman rho (Year vs Trials)', f'{rho_trials:.3f}', f'p < 0.001'],
        ['Spearman rho (Year vs HHI)', f'{rho_hhi:.3f}', f'p < 0.001'],
        ['Spearman rho (Year vs Collab)', f'{rho_collab:.3f}', f'p < 0.001'],
        ['', '', ''],
        ['HHI Change (2001 to 2025)', f'{y_hhi[0]:.3f} to {y_hhi[-1]:.3f}', f'{((y_hhi[-1]-y_hhi[0])/y_hhi[0]*100):.1f}%'],
        ['Collab Change (2001 to 2025)', f'{y_collab[0]:.1f}% to {y_collab[-1]:.1f}%', f'+{y_collab[-1]-y_collab[0]:.1f}pp'],
    ]
    
    y_pos = 0.95
    for row in table_data:
        ax4.text(0.05, y_pos, row[0], transform=ax4.transAxes, fontsize=11, 
                fontfamily='monospace', fontweight='bold' if row[0].startswith('─') or y_pos > 0.9 else 'normal')
        ax4.text(0.55, y_pos, row[1], transform=ax4.transAxes, fontsize=11, fontfamily='monospace')
        ax4.text(0.80, y_pos, row[2], transform=ax4.transAxes, fontsize=11, fontfamily='monospace',
                color=COLORS['accent'])
        y_pos -= 0.075
    
    ax4.set_title('Summary Statistics', pad=10, fontweight='bold')
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig11_statistical_summary.png')
    plt.close(fig)
    print("Saved: fig11_statistical_summary.png")


def fig_top_countries_treemap(top_overall, income_lookup):
    """Create a treemap-style visualization of top countries."""
    import matplotlib.patches as patches
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    top15 = top_overall.head(15)
    total = top15['total'].sum()
    
    positions = [
        (0, 50, 40, 50),
        (40, 50, 30, 50),
        (70, 50, 30, 50),
        (0, 25, 25, 25),
        (25, 25, 25, 25),
        (50, 25, 25, 25),
        (75, 25, 25, 25),
        (0, 0, 20, 25),
        (20, 0, 20, 25),
        (40, 0, 15, 25),
        (55, 0, 15, 25),
        (70, 0, 10, 25),
        (80, 0, 10, 25),
        (90, 0, 10, 12.5),
        (90, 12.5, 10, 12.5),
    ]
    
    for i, (_, row) in enumerate(top15.iterrows()):
        if i >= len(positions):
            break
        x, y, w, h = positions[i]
        
        income_full = get_income_class(row['country'], income_lookup)
        income_group = get_hic_lmic(income_full)
        color = COLORS['hic'] if income_group == 'HIC' else COLORS['lmic']
        
        rect = patches.FancyBboxPatch((x+0.5, y+0.5), w-1, h-1,
                                       boxstyle="round,pad=0.02",
                                       facecolor=color, edgecolor='white',
                                       linewidth=2, alpha=0.85)
        ax.add_patch(rect)
        
        fontsize = max(8, min(14, int(w/3)))
        ax.text(x + w/2, y + h/2, f"{row['country']}\n{row['total']}", 
               ha='center', va='center', fontsize=fontsize,
               fontweight='bold', color='white')
    
    ax.set_title('Top 15 Countries by Clinical Trial Output\n(Dark = HIC, Light = LMIC; Source: World Bank)', 
                 pad=20, fontsize=14, fontweight='bold')
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig12_country_treemap.png')
    plt.close(fig)
    print("Saved: fig12_country_treemap.png")


def main():
    print("Loading data...")
    per_year, top_overall, top_last5 = load_data()
    
    print("Loading World Bank income classification...")
    income_lookup = load_world_bank_data()
    print(f"  Loaded {len(income_lookup)} country classifications")
    
    print("\nGenerating advanced figures...\n")
    fig_world_map(top_overall, income_lookup)
    fig10a_income_distribution(top_overall, income_lookup)
    fig10b_top_countries(top_overall, income_lookup)
    fig_statistical_summary(per_year)
    fig_top_countries_treemap(top_overall, income_lookup)
    
    print(f"\n✓ Advanced figures saved to: {OUT_DIR}")


if __name__ == '__main__':
    main()
