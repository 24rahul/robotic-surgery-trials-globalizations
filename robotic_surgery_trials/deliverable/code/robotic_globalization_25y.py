#!/usr/bin/env python3
"""
25-year globalization analysis for robotic surgery true clinical trials.

Inputs: robotic_surgery_trials_clinical/robotic_*.xml
Outputs (robotic_surgery_trials_clinical/globalization/):
- per_year_metrics.tsv (year, total, num_countries, multi_country_share, avg_countries_per_trial, HHI, region shares, US share)
- top_countries_overall.tsv
- top_countries_last5y.tsv
- multi_country_examples.tsv (pmid, year, countries) [sample]
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter, defaultdict
import logging
from tqdm import tqdm
import math

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / 'robotic_surgery_trials_clinical'
OUT_DIR = INPUT_DIR / 'globalization'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Country normalization map (substring -> canonical)
COUNTRY_MAP = {
    'united states': 'United States', 'usa': 'United States', 'u.s.a.': 'United States',
    'england': 'United Kingdom', 'united kingdom': 'United Kingdom', 'uk': 'United Kingdom', 'scotland': 'United Kingdom', 'wales': 'United Kingdom',
    'germany': 'Germany', 'deutschland': 'Germany',
    'netherlands': 'Netherlands', 'holland': 'Netherlands',
    'switzerland': 'Switzerland',
    'japan': 'Japan',
    'italy': 'Italy',
    'russia': 'Russia', 'russian federation': 'Russia',
    'france': 'France',
    'china': 'China', 'pr china': 'China', 'people\'s republic of china': 'China',
    'australia': 'Australia',
    'brazil': 'Brazil',
    'ireland': 'Ireland',
    'denmark': 'Denmark',
    'spain': 'Spain',
    'canada': 'Canada',
    'sweden': 'Sweden',
    'norway': 'Norway',
    'finland': 'Finland',
    'south korea': 'South Korea', 'republic of korea': 'South Korea', 'korea': 'South Korea',
    'india': 'India',
    'singapore': 'Singapore',
    'taiwan': 'Taiwan',
    'hong kong': 'Hong Kong',
    'new zealand': 'New Zealand',
    'israel': 'Israel',
    'saudi arabia': 'Saudi Arabia', 'uae': 'United Arab Emirates', 'united arab emirates': 'United Arab Emirates', 'qatar': 'Qatar', 'kuwait': 'Kuwait', 'turkey': 'Turkey', 'iran': 'Iran',
    'south africa': 'South Africa', 'egypt': 'Egypt', 'nigeria': 'Nigeria', 'ethiopia': 'Ethiopia', 'kenya': 'Kenya'
}

# Region mapping
REGION_MAP = {
    'United States': 'North America', 'Canada': 'North America',
    'United Kingdom': 'Europe', 'Germany': 'Europe', 'Netherlands': 'Europe', 'Switzerland': 'Europe', 'Italy': 'Europe', 'France': 'Europe', 'Spain': 'Europe', 'Ireland': 'Europe', 'Denmark': 'Europe', 'Sweden': 'Europe', 'Norway': 'Europe', 'Finland': 'Europe', 'Russia': 'Europe',
    'China': 'Asia', 'Japan': 'Asia', 'South Korea': 'Asia', 'India': 'Asia', 'Singapore': 'Asia', 'Taiwan': 'Asia', 'Hong Kong': 'Asia',
    'Australia': 'Oceania', 'New Zealand': 'Oceania',
    'Brazil': 'Latin America',
    'Israel': 'Middle East', 'Saudi Arabia': 'Middle East', 'United Arab Emirates': 'Middle East', 'Qatar': 'Middle East', 'Kuwait': 'Middle East', 'Turkey': 'Middle East', 'Iran': 'Middle East',
    'South Africa': 'Africa', 'Egypt': 'Africa', 'Nigeria': 'Africa', 'Ethiopia': 'Africa', 'Kenya': 'Africa'
}


def extract_year(article: ET.Element):
    for xpath in ['.//JournalIssue/PubDate/Year', './/ArticleDate/Year', './/DateCreated/Year', './/DateCompleted/Year']:
        y = article.findtext(xpath)
        if y and y.isdigit():
            return int(y)
    return None


def extract_affiliation_countries(article: ET.Element):
    texts = []
    for author in article.findall('.//Author'):
        aff = author.findtext('AffiliationInfo/Affiliation')
        if aff:
            texts.append(aff.lower())
    # Also check collective affiliations
    for aff in article.findall('.//AffiliationInfo/Affiliation'):
        if aff.text:
            texts.append(aff.text.lower())
    found = set()
    for t in texts:
        for needle, canon in COUNTRY_MAP.items():
            if needle in t:
                found.add(canon)
    return found


def extract_journal_country(article: ET.Element):
    jc = article.findtext('.//MedlineJournalInfo/Country')
    return jc.strip() if jc else ''


def hhi_from_counts(counter: Counter) -> float:
    total = sum(counter.values())
    if total == 0:
        return 0.0
    return sum((c/total)**2 for c in counter.values())


def analyze():
    files = sorted(INPUT_DIR.glob('robotic_*.xml'))
    if not files:
        logger.error('No clinical robotic XMLs found')
        return

    per_year_country_counts = defaultdict(Counter)  # year -> country -> trials
    per_year_multi_country_trials = Counter()
    per_year_total_trials = Counter()
    per_year_countries_per_trial_sum = Counter()
    multi_country_examples = []

    all_years = set()
    for f in tqdm(files, desc='Scanning'):
        tree = ET.parse(f)
        root = tree.getroot()
        for art in root.findall('.//PubmedArticle'):
            y = extract_year(art)
            if y is None:
                continue
            all_years.add(y)
            # Determine countries from affiliations; fallback to journal country if none
            countries = extract_affiliation_countries(art)
            if not countries:
                jc = extract_journal_country(art)
                if jc:
                    countries = {jc}
            if not countries:
                continue
            per_year_total_trials[y] += 1
            for c in countries:
                per_year_country_counts[y][c] += 1
            per_year_countries_per_trial_sum[y] += len(countries)
            if len(countries) >= 2:
                per_year_multi_country_trials[y] += 1
                pmid = art.findtext('.//PMID') or ''
                if len(multi_country_examples) < 200:
                    multi_country_examples.append((pmid, y, ','.join(sorted(countries))))

    if not all_years:
        logger.error('No years detected')
        return

    max_year = max(all_years)
    start_year = max_year - 24

    # Aggregate metrics per year
    with (OUT_DIR / 'per_year_metrics.tsv').open('w', encoding='utf-8') as f:
        headers = [
            'year','total_trials','num_countries','multi_country_share','avg_countries_per_trial','hhi',
            'share_us','share_europe','share_asia','share_north_america','share_oceania','share_latin_america','share_middle_east','share_africa'
        ]
        f.write('\t'.join(headers) + '\n')
        for y in sorted(range(start_year, max_year+1)):
            total = per_year_total_trials.get(y, 0)
            country_counts = per_year_country_counts.get(y, Counter())
            num_countries = len(country_counts)
            multi_share = (per_year_multi_country_trials.get(y, 0)/total) if total else 0.0
            avg_countries = (per_year_countries_per_trial_sum.get(y, 0)/total) if total else 0.0
            hhi = hhi_from_counts(country_counts)
            # Region shares
            region_counts = Counter()
            for c, cnt in country_counts.items():
                region = REGION_MAP.get(c, 'Other')
                region_counts[region] += cnt
            def share(x):
                return (x/total) if total else 0.0
            share_us = share(country_counts.get('United States', 0))
            share_eu = share(sum(cnt for r, cnt in region_counts.items() if r == 'Europe'))
            share_asia = share(sum(cnt for r, cnt in region_counts.items() if r == 'Asia'))
            share_na = share(sum(cnt for r, cnt in region_counts.items() if r == 'North America'))
            share_oc = share(sum(cnt for r, cnt in region_counts.items() if r == 'Oceania'))
            share_latam = share(sum(cnt for r, cnt in region_counts.items() if r == 'Latin America'))
            share_me = share(sum(cnt for r, cnt in region_counts.items() if r == 'Middle East'))
            share_af = share(sum(cnt for r, cnt in region_counts.items() if r == 'Africa'))
            row = [
                y, total, num_countries,
                f"{multi_share:.3f}", f"{avg_countries:.2f}", f"{hhi:.3f}",
                f"{share_us:.3f}", f"{share_eu:.3f}", f"{share_asia:.3f}", f"{share_na:.3f}", f"{share_oc:.3f}", f"{share_latam:.3f}", f"{share_me:.3f}", f"{share_af:.3f}"
            ]
            f.write('\t'.join(map(str, row)) + '\n')

    # Top countries overall and last 5y
    overall = Counter()
    last5 = Counter()
    for y, cc in per_year_country_counts.items():
        for c, cnt in cc.items():
            overall[c] += cnt
            if y >= max_year - 4:
                last5[c] += cnt
    with (OUT_DIR / 'top_countries_overall.tsv').open('w', encoding='utf-8') as f:
        f.write('country\ttotal\n')
        for c, cnt in overall.most_common():
            f.write(f'{c}\t{cnt}\n')
    with (OUT_DIR / 'top_countries_last5y.tsv').open('w', encoding='utf-8') as f:
        f.write('country\tlast5y\n')
        for c, cnt in last5.most_common():
            f.write(f'{c}\t{cnt}\n')

    # Save sample of multi-country trials
    with (OUT_DIR / 'multi_country_examples.tsv').open('w', encoding='utf-8') as f:
        f.write('pmid\tyear\tcountries\n')
        for pmid, y, cs in multi_country_examples:
            f.write(f'{pmid}\t{y}\t{cs}\n')

    logger.info(f'Done. Metrics saved in {OUT_DIR}. Window: {start_year}-{max_year}.')


if __name__ == '__main__':
    analyze() 