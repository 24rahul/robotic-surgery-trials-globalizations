#!/usr/bin/env python3
"""
Calculate three-way split: HIC-only, LMIC-only, HIC-LMIC collaboration per year.
"""
import pandas as pd
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'

def load_income_data():
    """Load World Bank income classification."""
    wb_path = DATA_DIR / 'world_bank_income.csv'
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
        'Taiwan': 'High income',
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


def main():
    income_lookup = load_income_data()
    
    # Load collaboration data
    collab_df = pd.read_csv(DATA_DIR / 'multi_country_examples.tsv', sep='\t')
    
    # Count HIC-LMIC collaborations per year
    hic_lmic_by_year = defaultdict(int)
    
    for _, row in collab_df.iterrows():
        year = row['year']
        countries = row['countries'].split(',')
        
        categories = [get_income_category(c.strip(), income_lookup) for c in countries]
        hic_count = categories.count('HIC')
        lmic_count = categories.count('LMIC')
        
        if hic_count > 0 and lmic_count > 0:
            hic_lmic_by_year[year] += 1
    
    # Load income shares data (total trials and HIC/LMIC breakdown)
    income_df = pd.read_csv(DATA_DIR / 'income_shares_by_year.csv')
    
    # Calculate three-way split
    results = []
    for _, row in income_df.iterrows():
        year = int(row['year'])
        total = row['total']
        
        # HIC-LMIC collaborations for this year
        hic_lmic_count = hic_lmic_by_year.get(year, 0)
        
        # HIC share from the data (as fraction of total)
        hic_pct = row['high_income']
        lmic_pct = 100 - hic_pct
        
        # Estimate HIC-only and LMIC-only counts
        # Total HIC trials = HIC share * total, but some are HIC-LMIC collabs
        # Total LMIC trials = LMIC share * total, but some are HIC-LMIC collabs
        
        # HIC-LMIC collaboration percentage
        hic_lmic_pct = (hic_lmic_count / total * 100) if total > 0 else 0
        
        # Adjusted HIC-only and LMIC-only
        # Assuming HIC-LMIC collabs count toward both HIC and LMIC shares
        hic_only_pct = max(0, hic_pct - hic_lmic_pct)
        lmic_only_pct = max(0, lmic_pct - hic_lmic_pct)
        
        # Normalize to 100%
        total_pct = hic_only_pct + lmic_only_pct + hic_lmic_pct
        if total_pct > 0:
            hic_only_pct = hic_only_pct / total_pct * 100
            lmic_only_pct = lmic_only_pct / total_pct * 100
            hic_lmic_pct = hic_lmic_pct / total_pct * 100
        
        results.append({
            'year': year,
            'total': total,
            'hic_only': round(hic_only_pct, 1),
            'lmic_only': round(lmic_only_pct, 1),
            'hic_lmic_collab': round(hic_lmic_pct, 1),
        })
    
    # Print results
    print("Year\tTotal\tHIC-only\tLMIC-only\tHIC-LMIC")
    for r in results:
        print(f"{r['year']}\t{r['total']}\t{r['hic_only']}%\t\t{r['lmic_only']}%\t\t{r['hic_lmic_collab']}%")
    
    # Save to CSV
    df = pd.DataFrame(results)
    df.to_csv(DATA_DIR / 'three_way_split.csv', index=False)
    print(f"\nSaved to: {DATA_DIR / 'three_way_split.csv'}")
    
    # Print averages for 2001-05 and 2021-25
    early = df[df['year'] <= 2005].mean()
    late = df[df['year'] >= 2021].mean()
    print(f"\n2001-2005 averages:")
    print(f"  HIC-only: {early['hic_only']:.1f}%")
    print(f"  LMIC-only: {early['lmic_only']:.1f}%")
    print(f"  HIC-LMIC: {early['hic_lmic_collab']:.1f}%")
    print(f"\n2021-2025 averages:")
    print(f"  HIC-only: {late['hic_only']:.1f}%")
    print(f"  LMIC-only: {late['lmic_only']:.1f}%")
    print(f"  HIC-LMIC: {late['hic_lmic_collab']:.1f}%")


if __name__ == '__main__':
    main()
