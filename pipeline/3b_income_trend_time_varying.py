#!/usr/bin/env python3
"""
Time-varying income-tier analysis.

Re-extracts country-trial participations from XML and applies the World Bank
income classification *for the publication year of each trial*, addressing the
anachronism in 3_income_trend.py (which applied a fixed 2024-25 classification).

Inputs:  filtered_data/robotic_*.xml, data/world_bank_income_historical.csv
Outputs: data/income_shares_by_year_tv.csv       (time-varying)
         data/income_shares_comparison.csv        (static vs time-varying)
"""
import pandas as pd
from pathlib import Path
from collections import defaultdict, Counter
import xml.etree.ElementTree as ET
from tqdm import tqdm

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
INPUT_DIR = BASE_DIR / 'filtered_data'

# Country normalization (mirror of 2_globalization_stats.py COUNTRY_MAP)
COUNTRY_MAP = {
    'united states': 'United States', 'usa': 'United States', 'u.s.a.': 'United States',
    'england': 'United Kingdom', 'united kingdom': 'United Kingdom', 'uk': 'United Kingdom',
    'scotland': 'United Kingdom', 'wales': 'United Kingdom',
    'germany': 'Germany', 'deutschland': 'Germany',
    'netherlands': 'Netherlands', 'holland': 'Netherlands',
    'switzerland': 'Switzerland', 'japan': 'Japan', 'italy': 'Italy',
    'russia': 'Russia', 'russian federation': 'Russia',
    'france': 'France',
    'china': 'China', 'pr china': 'China', "people's republic of china": 'China',
    'australia': 'Australia', 'brazil': 'Brazil', 'ireland': 'Ireland',
    'denmark': 'Denmark', 'spain': 'Spain', 'canada': 'Canada',
    'sweden': 'Sweden', 'norway': 'Norway', 'finland': 'Finland',
    'south korea': 'South Korea', 'republic of korea': 'South Korea', 'korea': 'South Korea',
    'india': 'India', 'singapore': 'Singapore', 'taiwan': 'Taiwan',
    'hong kong': 'Hong Kong', 'new zealand': 'New Zealand', 'israel': 'Israel',
    'saudi arabia': 'Saudi Arabia', 'uae': 'United Arab Emirates',
    'united arab emirates': 'United Arab Emirates', 'qatar': 'Qatar',
    'kuwait': 'Kuwait', 'turkey': 'Turkey', 'iran': 'Iran',
    'south africa': 'South Africa', 'egypt': 'Egypt', 'nigeria': 'Nigeria',
    'ethiopia': 'Ethiopia', 'kenya': 'Kenya',
}

# Name alignment from canonical (our scheme) -> World Bank canonical
NAME_TO_WB = {
    'United States': 'United States', 'United Kingdom': 'United Kingdom',
    'Germany': 'Germany', 'Netherlands': 'Netherlands', 'Switzerland': 'Switzerland',
    'Japan': 'Japan', 'Italy': 'Italy', 'Russia': 'Russian Federation',
    'France': 'France', 'China': 'China', 'Australia': 'Australia',
    'Brazil': 'Brazil', 'Ireland': 'Ireland', 'Denmark': 'Denmark',
    'Spain': 'Spain', 'Canada': 'Canada', 'Sweden': 'Sweden',
    'Norway': 'Norway', 'Finland': 'Finland', 'South Korea': 'Korea, Rep.',
    'India': 'India', 'Singapore': 'Singapore', 'Taiwan': 'Taiwan, China',
    'Hong Kong': 'Hong Kong SAR, China', 'New Zealand': 'New Zealand',
    'Israel': 'Israel', 'Saudi Arabia': 'Saudi Arabia',
    'United Arab Emirates': 'United Arab Emirates', 'Qatar': 'Qatar',
    'Kuwait': 'Kuwait', 'Turkey': 'Turkiye', 'Iran': 'Iran, Islamic Rep.',
    'South Africa': 'South Africa', 'Egypt': 'Egypt, Arab Rep.',
    'Nigeria': 'Nigeria', 'Ethiopia': 'Ethiopia', 'Kenya': 'Kenya',
}


def load_historical_lookup():
    df = pd.read_csv(DATA_DIR / 'world_bank_income_historical.csv')
    return df.set_index(['country_name', 'year'])['income_class'].to_dict()


def classify_time_varying(country_canonical, year, hist_lookup, fallback=None):
    wb_name = NAME_TO_WB.get(country_canonical)
    if not wb_name:
        return fallback
    # Clamp year to available range (1987-2025 covered)
    y = max(1987, min(2025, year))
    cls = hist_lookup.get((wb_name, y))
    if cls:
        return cls
    # Fallback: try adjacent year
    for offset in [1, -1, 2, -2, 3, -3]:
        cls = hist_lookup.get((wb_name, y + offset))
        if cls:
            return cls
    return fallback


def extract_year(article):
    for xpath in ['.//JournalIssue/PubDate/Year', './/ArticleDate/Year',
                  './/DateCreated/Year', './/DateCompleted/Year']:
        y = article.findtext(xpath)
        if y and y.isdigit():
            return int(y)
    return None


def extract_countries(article):
    texts = []
    for author in article.findall('.//Author'):
        aff = author.findtext('AffiliationInfo/Affiliation')
        if aff:
            texts.append(aff.lower())
    for aff in article.findall('.//AffiliationInfo/Affiliation'):
        if aff.text:
            texts.append(aff.text.lower())
    found = set()
    for t in texts:
        for needle, canon in COUNTRY_MAP.items():
            if needle in t:
                found.add(canon)
    return found


def main():
    hist = load_historical_lookup()
    files = sorted(INPUT_DIR.glob('robotic_*.xml'))

    # Per-year: income-tier SHARE of country-trial participations
    year_tier_counts = defaultdict(Counter)  # year -> {tier: count}
    year_totals = Counter()                  # year -> total participations
    year_trial_count = Counter()             # year -> unique trial count

    for f in tqdm(files, desc='Scanning XMLs'):
        try:
            tree = ET.parse(f)
            root = tree.getroot()
        except Exception:
            continue
        for art in root.findall('.//PubmedArticle'):
            y = extract_year(art)
            if y is None:
                continue
            countries = extract_countries(art)
            if not countries:
                continue
            year_trial_count[y] += 1
            for c in countries:
                tier = classify_time_varying(c, y, hist)
                if tier is None:
                    continue
                year_tier_counts[y][tier] += 1
                year_totals[y] += 1

    # Build output DF: per-year count of participations in each tier (time-varying)
    rows = []
    for y in sorted(year_trial_count.keys()):
        if y < 2001 or y > 2025:
            continue
        counts = year_tier_counts[y]
        total = year_totals[y]
        rows.append({
            'year': y,
            'trials': year_trial_count[y],
            'participations': total,
            'high_income': counts.get('high_income', 0),
            'upper_middle': counts.get('upper_middle', 0),
            'lower_middle': counts.get('lower_middle', 0),
            'low_income': counts.get('low_income', 0),
            'high_income_pct': counts.get('high_income', 0) / total * 100 if total else 0,
            'upper_middle_pct': counts.get('upper_middle', 0) / total * 100 if total else 0,
            'lower_middle_pct': counts.get('lower_middle', 0) / total * 100 if total else 0,
            'low_income_pct': counts.get('low_income', 0) / total * 100 if total else 0,
        })
    out = pd.DataFrame(rows)
    out.to_csv(DATA_DIR / 'income_shares_by_year_tv.csv', index=False)
    print(f'\nWrote {DATA_DIR / "income_shares_by_year_tv.csv"} ({len(out)} years)')

    # Summary
    total_part = out['participations'].sum()
    for tier in ['high_income', 'upper_middle', 'lower_middle', 'low_income']:
        pct = out[tier].sum() / total_part * 100
        print(f'  {tier}: {out[tier].sum()} ({pct:.2f}%)')

    # Early vs recent comparison
    early = out[out.year.between(2001, 2005)]
    recent = out[out.year.between(2021, 2025)]
    print('\n--- Income shift 2001-05 -> 2021-25 (time-varying) ---')
    for tier in ['high_income', 'upper_middle', 'lower_middle', 'low_income']:
        e_pct = early[tier].sum() / early['participations'].sum() * 100
        r_pct = recent[tier].sum() / recent['participations'].sum() * 100
        print(f'  {tier}: {e_pct:.1f}% -> {r_pct:.1f}% ({r_pct-e_pct:+.1f}pp)')


if __name__ == '__main__':
    main()
