#!/usr/bin/env python3
"""
Analyze international collaboration patterns in robotic surgery trials.
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
OUT_DIR = BASE_DIR / 'figures_elegant'

# ARGOS Theme Colors
COLORS = {
    'primary': '#374151',
    'secondary': '#6B7280',
    'light': '#9CA3AF',
    'lighter': '#D1D5DB',
    'background': '#FAFAFA',
    'text': '#374151',
    'grid': '#E5E7EB',
    'accent': '#374151',
    'hic': '#374151',
    'lmic': '#7C9CBF',
}

plt.rcParams.update({
    'figure.facecolor': COLORS['background'],
    'axes.facecolor': COLORS['background'],
    'savefig.facecolor': COLORS['background'],
    'font.family': 'sans-serif',
    'axes.spines.top': False,
    'axes.spines.right': False,
})


def load_income_data():
    """Load World Bank income classification."""
    wb_path = BASE_DIR / 'world_bank_income.csv'
    wb_df = pd.read_csv(wb_path)
    
    income_lookup = {}
    for _, row in wb_df.iterrows():
        name = row['country_name']
        income = row['income_level']
        if income != 'Aggregates':
            income_lookup[name] = income
    
    return income_lookup


def get_income_category(country, income_lookup):
    """Get HIC or LMIC for a country."""
    name_map = {
        'South Korea': 'Korea  Rep.',
        'Korea (South)': 'Korea  Rep.',
        'United States': 'United States',
        'England': 'United Kingdom',
        'Scotland': 'United Kingdom',
        'Wales': 'United Kingdom',
        'Russia': 'Russian Federation',
        'Iran': 'Iran, Islamic Rep.',
        'Egypt': 'Egypt, Arab Rep.',
        'Taiwan': 'High income',  # Direct classification
        'Hong Kong': 'Hong Kong SAR, China',
    }
    
    if country == 'Taiwan':
        return 'HIC'
    
    mapped = name_map.get(country, country)
    
    income = None
    if mapped in income_lookup:
        income = income_lookup[mapped]
    elif country in income_lookup:
        income = income_lookup[country]
    else:
        for wb_name, inc in income_lookup.items():
            if country.lower() in wb_name.lower() or wb_name.lower() in country.lower():
                income = inc
                break
    
    if income == 'High income':
        return 'HIC'
    elif income in ['Upper middle income', 'Lower middle income', 'Low income']:
        return 'LMIC'
    return 'Unknown'


def load_collaboration_data():
    """Load multi-country collaboration examples."""
    collab_path = DATA_DIR / 'multi_country_examples.tsv'
    df = pd.read_csv(collab_path, sep='\t')
    return df


def analyze_collaboration_types(df, income_lookup):
    """Categorize collaborations as HIC-HIC, HIC-LMIC, or LMIC-LMIC."""
    collab_types = {'HIC-HIC': 0, 'HIC-LMIC': 0, 'LMIC-LMIC': 0}
    collab_types_by_year = defaultdict(lambda: {'HIC-HIC': 0, 'HIC-LMIC': 0, 'LMIC-LMIC': 0})
    
    country_pairs = Counter()
    hic_lmic_pairs = []
    
    for _, row in df.iterrows():
        countries = row['countries'].split(',')
        year = row['year']
        
        # Get income categories for all countries
        categories = [get_income_category(c.strip(), income_lookup) for c in countries]
        
        hic_count = categories.count('HIC')
        lmic_count = categories.count('LMIC')
        
        if lmic_count == 0:
            collab_types['HIC-HIC'] += 1
            collab_types_by_year[year]['HIC-HIC'] += 1
        elif hic_count == 0:
            collab_types['LMIC-LMIC'] += 1
            collab_types_by_year[year]['LMIC-LMIC'] += 1
        else:
            collab_types['HIC-LMIC'] += 1
            collab_types_by_year[year]['HIC-LMIC'] += 1
            # Track HIC-LMIC pairs
            for c in countries:
                cat = get_income_category(c.strip(), income_lookup)
                if cat == 'LMIC':
                    hic_lmic_pairs.append(c.strip())
        
        # Count country pairs
        for pair in combinations(sorted([c.strip() for c in countries]), 2):
            country_pairs[pair] += 1
    
    return collab_types, collab_types_by_year, country_pairs, hic_lmic_pairs


def count_country_collaborations(df):
    """Count how often each country appears in collaborations."""
    country_collab_count = Counter()
    
    for _, row in df.iterrows():
        countries = row['countries'].split(',')
        for c in countries:
            country_collab_count[c.strip()] += 1
    
    return country_collab_count


def fig_collaboration_type_pie(collab_types):
    """Pie chart of collaboration types."""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    labels = ['HIC-HIC', 'HIC-LMIC', 'LMIC-LMIC']
    sizes = [collab_types[l] for l in labels]
    colors = [COLORS['primary'], COLORS['light'], COLORS['lmic']]
    
    # Only include non-zero values
    filtered = [(l, s, c) for l, s, c in zip(labels, sizes, colors) if s > 0]
    if not filtered:
        return
    
    labels, sizes, colors = zip(*filtered)
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                       autopct='%1.1f%%', startangle=90,
                                       wedgeprops=dict(edgecolor='white', linewidth=2))
    
    for autotext in autotexts:
        autotext.set_fontweight('bold')
        autotext.set_fontsize(11)
    
    ax.set_title('International Collaboration Types\nWho Collaborates With Whom?', 
                 fontweight='bold', pad=20)
    
    # Add counts
    legend_labels = [f'{l}: {s} trials' for l, s in zip(labels, sizes)]
    ax.legend(wedges, legend_labels, loc='lower center', 
              bbox_to_anchor=(0.5, -0.1), ncol=len(labels), framealpha=0.95)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig_collab_types.png', dpi=300)
    plt.close(fig)
    print("Saved: fig_collab_types.png")


def fig_collaboration_type_trend(collab_types_by_year):
    """Line chart showing collaboration type trends over time."""
    fig, ax = plt.subplots(figsize=(11, 6))
    
    years = sorted(collab_types_by_year.keys())
    years = [y for y in years if y >= 2001]
    
    hic_hic = [collab_types_by_year[y]['HIC-HIC'] for y in years]
    hic_lmic = [collab_types_by_year[y]['HIC-LMIC'] for y in years]
    
    # Calculate percentages
    totals = [h + l for h, l in zip(hic_hic, hic_lmic)]
    hic_lmic_pct = [100 * l / t if t > 0 else 0 for l, t in zip(hic_lmic, totals)]
    
    # 3-year moving average for smoothing
    def moving_avg(data, window=3):
        result = []
        for i in range(len(data)):
            start = max(0, i - window + 1)
            result.append(np.mean(data[start:i+1]))
        return result
    
    hic_lmic_smooth = moving_avg(hic_lmic_pct)
    
    ax.bar(years, hic_lmic, color=COLORS['lmic'], alpha=0.4, label='HIC-LMIC collaborations (n)')
    ax.bar(years, hic_hic, bottom=hic_lmic, color=COLORS['primary'], alpha=0.4, label='HIC-HIC collaborations (n)')
    
    ax2 = ax.twinx()
    ax2.plot(years, hic_lmic_smooth, color=COLORS['lmic'], linewidth=2.5, 
             marker='o', markersize=5, label='HIC-LMIC % (3-yr avg)', markerfacecolor='white')
    
    ax.set_xlabel('Year', fontweight='medium')
    ax.set_ylabel('Number of Collaborative Trials', fontweight='medium')
    ax2.set_ylabel('HIC-LMIC Share (%)', fontweight='medium', color=COLORS['lmic'])
    ax2.tick_params(axis='y', labelcolor=COLORS['lmic'])
    ax2.set_ylim(0, 100)
    
    ax.set_title('International Collaboration Trends\nAre HIC-LMIC Partnerships Increasing?', 
                 fontweight='bold', pad=15)
    
    # Combined legend
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', framealpha=0.95)
    
    ax.yaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax.set_axisbelow(True)
    
    # Add annotation for recent trend
    recent_avg = np.mean(hic_lmic_pct[-5:])
    early_avg = np.mean(hic_lmic_pct[:5]) if len(hic_lmic_pct) >= 5 else hic_lmic_pct[0]
    
    props = dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor=COLORS['light'], alpha=0.95)
    ax.text(0.97, 0.03, f'HIC-LMIC share:\n{early_avg:.0f}% → {recent_avg:.0f}%', 
            transform=ax.transAxes, fontsize=10, ha='right', va='bottom',
            fontweight='bold', bbox=props, color=COLORS['accent'])
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig_collab_trend.png', dpi=300)
    plt.close(fig)
    print("Saved: fig_collab_trend.png")


def fig_top_collaborating_countries(country_collab_count, income_lookup, top_n=15):
    """Bar chart of most collaborative countries."""
    fig, ax = plt.subplots(figsize=(10, 7))
    
    top_countries = country_collab_count.most_common(top_n)
    countries = [c for c, _ in top_countries]
    counts = [n for _, n in top_countries]
    
    # Color by income
    colors = [COLORS['hic'] if get_income_category(c, income_lookup) == 'HIC' else COLORS['lmic'] 
              for c in countries]
    
    bars = ax.barh(range(len(countries)), counts, color=colors, edgecolor='white', linewidth=0.5)
    
    ax.set_yticks(range(len(countries)))
    ax.set_yticklabels(countries)
    ax.invert_yaxis()
    ax.set_xlabel('Number of Collaborative Trials', fontweight='medium')
    ax.set_title('Most Collaborative Countries\nin Robotic Surgery Trials', fontweight='bold', pad=15)
    
    # Add value labels
    for i, (bar, count) in enumerate(zip(bars, counts)):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                str(count), va='center', fontsize=9, fontweight='medium')
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS['hic'], edgecolor='white', label='HIC'),
        Patch(facecolor=COLORS['lmic'], edgecolor='white', label='LMIC'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', framealpha=0.95)
    
    ax.xaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig_collab_countries.png', dpi=300)
    plt.close(fig)
    print("Saved: fig_collab_countries.png")


def fig_top_country_pairs(country_pairs, income_lookup, top_n=15):
    """Bar chart of top collaborating country pairs."""
    fig, ax = plt.subplots(figsize=(11, 7))
    
    top_pairs = country_pairs.most_common(top_n)
    pair_labels = [f'{p[0]} - {p[1]}' for p, _ in top_pairs]
    counts = [n for _, n in top_pairs]
    
    # Color by collaboration type
    def pair_type(pair):
        c1, c2 = pair
        cat1 = get_income_category(c1, income_lookup)
        cat2 = get_income_category(c2, income_lookup)
        if cat1 == 'HIC' and cat2 == 'HIC':
            return 'HIC-HIC'
        elif cat1 == 'LMIC' and cat2 == 'LMIC':
            return 'LMIC-LMIC'
        else:
            return 'HIC-LMIC'
    
    type_colors = {
        'HIC-HIC': COLORS['primary'],
        'HIC-LMIC': COLORS['light'],
        'LMIC-LMIC': COLORS['lmic']
    }
    
    colors = [type_colors[pair_type(p)] for p, _ in top_pairs]
    
    bars = ax.barh(range(len(pair_labels)), counts, color=colors, edgecolor='white', linewidth=0.5)
    
    ax.set_yticks(range(len(pair_labels)))
    ax.set_yticklabels(pair_labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('Number of Collaborative Trials', fontweight='medium')
    ax.set_title('Top Country Pairs in International Collaboration', fontweight='bold', pad=15)
    
    # Add value labels
    for bar, count in zip(bars, counts):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                str(count), va='center', fontsize=9, fontweight='medium')
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS['primary'], edgecolor='white', label='HIC-HIC'),
        Patch(facecolor=COLORS['light'], edgecolor='white', label='HIC-LMIC'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', framealpha=0.95)
    
    ax.xaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig_collab_pairs.png', dpi=300)
    plt.close(fig)
    print("Saved: fig_collab_pairs.png")


def fig_lmic_collaboration_partners(hic_lmic_pairs, income_lookup):
    """Which LMIC countries are involved in HIC-LMIC collaborations?"""
    if not hic_lmic_pairs:
        print("No HIC-LMIC collaborations found")
        return
    
    fig, ax = plt.subplots(figsize=(9, 5))
    
    lmic_counts = Counter(hic_lmic_pairs)
    top_lmic = lmic_counts.most_common(10)
    
    if not top_lmic:
        return
    
    countries = [c for c, _ in top_lmic]
    counts = [n for _, n in top_lmic]
    
    bars = ax.barh(range(len(countries)), counts, color=COLORS['lmic'], 
                   edgecolor='white', linewidth=0.5)
    
    ax.set_yticks(range(len(countries)))
    ax.set_yticklabels(countries)
    ax.invert_yaxis()
    ax.set_xlabel('Number of HIC-LMIC Collaborative Trials', fontweight='medium')
    ax.set_title('LMIC Countries in International Collaborations\nWho Benefits from HIC Partnerships?', 
                 fontweight='bold', pad=15)
    
    # Add value labels
    for bar, count in zip(bars, counts):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
                str(count), va='center', fontsize=9, fontweight='medium')
    
    ax.xaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig_lmic_collab.png', dpi=300)
    plt.close(fig)
    print("Saved: fig_lmic_collab.png")


def main():
    print("Analyzing international collaboration patterns...\n")
    
    # Load data
    income_lookup = load_income_data()
    df = load_collaboration_data()
    
    print(f"Total multi-country trials: {len(df)}")
    
    # Analyze collaboration types
    collab_types, collab_types_by_year, country_pairs, hic_lmic_pairs = \
        analyze_collaboration_types(df, income_lookup)
    
    # Count country collaborations
    country_collab_count = count_country_collaborations(df)
    
    # Print summary
    print(f"\nCollaboration breakdown:")
    total_collab = sum(collab_types.values())
    for ctype, count in collab_types.items():
        pct = 100 * count / total_collab if total_collab > 0 else 0
        print(f"  {ctype}: {count} ({pct:.1f}%)")
    
    print(f"\nTop collaborating countries:")
    for country, count in country_collab_count.most_common(10):
        cat = get_income_category(country, income_lookup)
        print(f"  {country} ({cat}): {count}")
    
    print(f"\nTop country pairs:")
    for pair, count in country_pairs.most_common(10):
        print(f"  {pair[0]} - {pair[1]}: {count}")
    
    # Generate figures
    print("\nGenerating figures...")
    fig_collaboration_type_pie(collab_types)
    fig_collaboration_type_trend(collab_types_by_year)
    fig_top_collaborating_countries(country_collab_count, income_lookup)
    fig_top_country_pairs(country_pairs, income_lookup)
    fig_lmic_collaboration_partners(hic_lmic_pairs, income_lookup)
    
    print(f"\n✓ Collaboration figures saved to: {OUT_DIR}")


if __name__ == '__main__':
    main()
