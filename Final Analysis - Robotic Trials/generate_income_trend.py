#!/usr/bin/env python3
"""
Generate income-level trial shares over time.
Shows whether globalization has improved equity or is HIC→HIC redistribution.
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
import xml.etree.ElementTree as ET

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
OUT_DIR = BASE_DIR / 'figures_elegant'
INPUT_DIR = BASE_DIR.parent / 'robotic_surgery_trials_clinical'

# ARGOS Theme Colors
COLORS = {
    'high': '#374151',      # Dark charcoal
    'upper_mid': '#6B7280', # Medium grey
    'lower_mid': '#9CA3AF', # Light grey
    'low': '#D1D5DB',       # Very light
    'background': '#FAFAFA',
    'text': '#374151',
    'grid': '#E5E7EB',
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


def get_income_level(country, income_lookup):
    """Get income level for a country."""
    # Country name mappings
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
        'Taiwan': 'Taiwan, China',
        'Hong Kong': 'Hong Kong SAR, China',
    }
    
    mapped = name_map.get(country, country)
    
    if mapped in income_lookup:
        return income_lookup[mapped]
    if country in income_lookup:
        return income_lookup[country]
    
    # Partial match
    for wb_name, income in income_lookup.items():
        if country.lower() in wb_name.lower() or wb_name.lower() in country.lower():
            return income
    
    return 'Unknown'


def extract_year(article):
    """Extract publication year."""
    for path in ['.//PubDate/Year', './/PubMedPubDate[@PubStatus="pubmed"]/Year']:
        el = article.find(path)
        if el is not None and el.text:
            try:
                y = int(el.text)
                if 2001 <= y <= 2025:
                    return y
            except ValueError:
                pass
    return None


def extract_countries(article):
    """Extract countries from affiliations."""
    countries = set()
    for aff in article.findall('.//AffiliationInfo/Affiliation'):
        if aff.text:
            text = aff.text
            # Simple country extraction from affiliation text
            country_patterns = [
                ('United States', ['USA', 'United States', 'U.S.A']),
                ('China', ['China', 'P.R. China', 'PRC']),
                ('United Kingdom', ['United Kingdom', 'UK', 'England', 'Scotland', 'Wales']),
                ('Germany', ['Germany', 'Deutschland']),
                ('South Korea', ['Korea', 'South Korea', 'Republic of Korea']),
                ('Japan', ['Japan']),
                ('Italy', ['Italy', 'Italia']),
                ('France', ['France']),
                ('Netherlands', ['Netherlands', 'Holland']),
                ('Canada', ['Canada']),
                ('Australia', ['Australia']),
                ('Spain', ['Spain', 'España']),
                ('India', ['India']),
                ('Brazil', ['Brazil', 'Brasil']),
                ('Turkey', ['Turkey', 'Türkiye']),
                ('Iran', ['Iran']),
                ('Egypt', ['Egypt']),
                ('South Africa', ['South Africa']),
                ('Nigeria', ['Nigeria']),
                ('Taiwan', ['Taiwan']),
                ('Singapore', ['Singapore']),
                ('Belgium', ['Belgium']),
                ('Switzerland', ['Switzerland']),
                ('Sweden', ['Sweden']),
                ('Denmark', ['Denmark']),
                ('Norway', ['Norway']),
                ('Austria', ['Austria']),
                ('Poland', ['Poland']),
                ('Israel', ['Israel']),
                ('Saudi Arabia', ['Saudi Arabia']),
            ]
            for country, patterns in country_patterns:
                for p in patterns:
                    if p.lower() in text.lower():
                        countries.add(country)
                        break
    return countries


def process_xml_files():
    """Process XML files to get year-country data."""
    print("Processing XML files...")
    
    year_country_counts = defaultdict(Counter)  # year -> country -> count
    
    xml_files = sorted(INPUT_DIR.glob('robotic_surgery_clinical_trials_*.xml'))
    print(f"  Found {len(xml_files)} XML files")
    
    for xml_file in xml_files:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
        except Exception as e:
            continue
        
        for article in root.findall('.//PubmedArticle'):
            year = extract_year(article)
            if not year:
                continue
            
            countries = extract_countries(article)
            if not countries:
                countries = {'Unknown'}
            
            for country in countries:
                year_country_counts[year][country] += 1
    
    return year_country_counts


def calculate_income_shares(year_country_counts, income_lookup):
    """Calculate income-level shares per year."""
    years = sorted(year_country_counts.keys())
    
    data = []
    for year in years:
        country_counts = year_country_counts[year]
        
        income_totals = {
            'High income': 0,
            'Upper middle income': 0,
            'Lower middle income': 0,
            'Low income': 0,
            'Unknown': 0
        }
        
        for country, count in country_counts.items():
            income = get_income_level(country, income_lookup)
            if income in income_totals:
                income_totals[income] += count
            else:
                income_totals['Unknown'] += count
        
        total = sum(income_totals.values()) - income_totals['Unknown']
        if total > 0:
            data.append({
                'year': year,
                'total': total,
                'high_income': income_totals['High income'] / total * 100,
                'upper_middle': income_totals['Upper middle income'] / total * 100,
                'lower_middle': income_totals['Lower middle income'] / total * 100,
                'low_income': income_totals['Low income'] / total * 100,
            })
    
    return pd.DataFrame(data)


def create_income_trend_figure(df):
    """Create figure showing income-level shares over time."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = df['year'].values
    
    # Plot each income level
    ax.plot(x, df['high_income'], color=COLORS['high'], linewidth=2.5, 
            marker='o', markersize=5, label='High Income', markerfacecolor='white')
    ax.plot(x, df['upper_middle'], color=COLORS['upper_mid'], linewidth=2.5, 
            marker='s', markersize=5, label='Upper Middle Income', markerfacecolor='white')
    ax.plot(x, df['lower_middle'], color=COLORS['lower_mid'], linewidth=2.5, 
            marker='^', markersize=5, label='Lower Middle Income', markerfacecolor='white')
    ax.plot(x, df['low_income'], color=COLORS['low'], linewidth=2.5, 
            marker='d', markersize=5, label='Low Income', markerfacecolor='white')
    
    # Add reference line for LMIC population share (~84%)
    ax.axhline(y=84, color='#EF4444', linestyle='--', linewidth=1.5, alpha=0.7)
    ax.text(2002, 86, 'LMIC share of world population (~84%)', fontsize=9, 
            color='#EF4444', style='italic')
    
    # Add reference line for LMIC surgical burden (~93%)
    ax.axhline(y=93, color='#DC2626', linestyle=':', linewidth=1.5, alpha=0.7)
    ax.text(2002, 95, 'LMIC share of surgical disease burden (~93%)*', fontsize=9, 
            color='#DC2626', style='italic')
    
    ax.set_xlabel('Year', fontweight='medium')
    ax.set_ylabel('Share of Clinical Trials (%)', fontweight='medium')
    ax.set_title('Trial Distribution by Income Level Over Time\nHas Globalization Improved Equity?', 
                 fontweight='bold', pad=15)
    ax.set_xlim(2000, 2026)
    ax.set_ylim(0, 100)
    ax.legend(loc='center right', framealpha=0.95)
    ax.yaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax.set_axisbelow(True)
    
    # Source note
    ax.text(0.5, -0.12, '*Lancet Commission on Global Surgery, 2015', 
            transform=ax.transAxes, fontsize=8, ha='center', style='italic', color='#6B7280')
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig_income_trend.png', dpi=300)
    plt.close(fig)
    print("Saved: fig_income_trend.png")
    
    return df


def create_lmic_combined_figure(df):
    """Create simplified HIC vs LMIC trend figure."""
    fig, ax = plt.subplots(figsize=(11, 6))
    
    x = df['year'].values
    
    # Combine LMIC categories
    lmic_share = df['upper_middle'] + df['lower_middle'] + df['low_income']
    hic_share = df['high_income']
    
    # Fill areas
    ax.fill_between(x, hic_share, alpha=0.3, color=COLORS['high'], label='_nolegend_')
    ax.fill_between(x, lmic_share, alpha=0.3, color='#7C9CBF', label='_nolegend_')
    
    # Lines
    ax.plot(x, hic_share, color=COLORS['high'], linewidth=2.5, 
            marker='o', markersize=5, label='High Income Countries (HIC)', markerfacecolor='white')
    ax.plot(x, lmic_share, color='#7C9CBF', linewidth=2.5, 
            marker='s', markersize=5, label='Low & Middle Income Countries (LMIC)', markerfacecolor='white')
    
    # Reference lines
    ax.axhline(y=16.4, color=COLORS['high'], linestyle='--', linewidth=1, alpha=0.5)
    ax.text(2024.5, 18, 'HIC pop.\n(16%)', fontsize=8, color=COLORS['high'], ha='left')
    
    ax.axhline(y=83.6, color='#7C9CBF', linestyle='--', linewidth=1, alpha=0.5)
    ax.text(2024.5, 80, 'LMIC pop.\n(84%)', fontsize=8, color='#5B82A8', ha='left')
    
    # Annotations
    ax.annotate(f'{hic_share.iloc[0]:.0f}%', (x[0], hic_share.iloc[0]), 
                textcoords="offset points", xytext=(-15, 8), fontsize=10, 
                fontweight='bold', color=COLORS['high'])
    ax.annotate(f'{hic_share.iloc[-1]:.0f}%', (x[-1], hic_share.iloc[-1]), 
                textcoords="offset points", xytext=(5, 8), fontsize=10, 
                fontweight='bold', color=COLORS['high'])
    
    ax.annotate(f'{lmic_share.iloc[0]:.0f}%', (x[0], lmic_share.iloc[0]), 
                textcoords="offset points", xytext=(-15, -15), fontsize=10, 
                fontweight='bold', color='#5B82A8')
    ax.annotate(f'{lmic_share.iloc[-1]:.0f}%', (x[-1], lmic_share.iloc[-1]), 
                textcoords="offset points", xytext=(5, -5), fontsize=10, 
                fontweight='bold', color='#5B82A8')
    
    ax.set_xlabel('Year', fontweight='medium')
    ax.set_ylabel('Share of Clinical Trials (%)', fontweight='medium')
    ax.set_title('HIC vs LMIC Trial Share Over Time\nThe Equity Gap Persists', 
                 fontweight='bold', pad=15)
    ax.set_xlim(2000, 2026)
    ax.set_ylim(0, 100)
    ax.legend(loc='center right', framealpha=0.95)
    ax.yaxis.grid(True, linestyle='-', alpha=0.3, color=COLORS['grid'])
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig_hic_lmic_trend.png', dpi=300)
    plt.close(fig)
    print("Saved: fig_hic_lmic_trend.png")


def main():
    print("Generating income trend analysis...\n")
    
    # Load income data
    income_lookup = load_income_data()
    print(f"Loaded {len(income_lookup)} country income classifications")
    
    # Process XML files to get year-country data
    year_country_counts = process_xml_files()
    
    # Calculate income shares per year
    df = calculate_income_shares(year_country_counts, income_lookup)
    
    # Print summary
    print(f"\nIncome shares (first vs last 5 years):")
    early = df[df['year'] <= 2005].mean()
    late = df[df['year'] >= 2021].mean()
    print(f"  High Income:        {early['high_income']:.1f}% → {late['high_income']:.1f}%")
    print(f"  Upper Middle:       {early['upper_middle']:.1f}% → {late['upper_middle']:.1f}%")
    print(f"  Lower Middle:       {early['lower_middle']:.1f}% → {late['lower_middle']:.1f}%")
    print(f"  Low Income:         {early['low_income']:.1f}% → {late['low_income']:.1f}%")
    
    # Create figures
    print("\nCreating figures...")
    create_income_trend_figure(df)
    create_lmic_combined_figure(df)
    
    # Save data
    df.to_csv(DATA_DIR / 'income_shares_by_year.csv', index=False)
    print(f"\nSaved data to: {DATA_DIR / 'income_shares_by_year.csv'}")
    
    print(f"\n✓ Income trend figures saved to: {OUT_DIR}")


if __name__ == '__main__':
    main()
