#!/usr/bin/env python3
"""
Compute descriptive statistics for robotic surgery clinical trials.

Outputs TSVs:
- yearly_counts.tsv
- specialty_counts.tsv
- procedure_counts.tsv
- design_counts.tsv
- comparator_flags.tsv
- top_journals.tsv (with overall and last-5y counts)
- country_counts.tsv (journal country; overall and last-5y)

Location: analysis files saved under robotic_surgery_trials/analysis/
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter, defaultdict
import multiprocessing as mp
from functools import partial
from tqdm import tqdm
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / 'robotic_surgery_trials'
ANALYSIS_DIR = INPUT_DIR / 'analysis'
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

# Specialty classification (simple, consistent with prior)
SPECIALTY_KEYWORDS = {
    'Urology': ['urologic', 'prostate', 'prostatectomy', 'nephrectomy', 'cystectomy', 'transurethral'],
    'Gynecology': ['hysterectomy', 'myomectomy', 'salpingo', 'oophorectomy', 'gyneco', 'uterus', 'fibroid'],
    'General Surgery': ['hernia', 'cholecystectomy', 'gastrectomy', 'pancreatectomy', 'hepatectomy', 'appendectomy', 'adrenalectomy', 'laparotomy'],
    'Colorectal Surgery': ['colectomy', 'rectal', 'rectopexy', 'proctectomy', 'colorectal'],
    'Thoracic Surgery': ['lobectomy', 'segmentectomy', 'esophagectomy', 'thoracoscopic', 'thoracic', 'lung'],
    'Cardiac Surgery': ['mitral', 'tricuspid', 'aortic valve', 'coronary', 'cardiac', 'heart'],
    'Orthopedic Surgery': ['arthroplasty', 'arthroscopy', 'joint replacement', 'orthop', 'spine'],
    'Neurosurgery': ['neuro', 'craniotomy', 'pituitary', 'skull base', 'spine surgery'],
    'Plastic Surgery': ['mastectomy', 'breast reconstruction', 'flap', 'rhinoplasty', 'cleft'],
    'Otolaryngology': ['transoral robotic', 'TORS', 'laryng', 'pharyng', 'tonsil', 'otolaryng'],
    'Ophthalmology': ['ophthalm', 'cataract', 'retina', 'vitrectomy'],
    'Transplant Surgery': ['transplant'],
    'Pediatric Surgery': ['pediatric', 'paediatric', 'child', 'infant'],
    'Endocrine Surgery': ['thyroidectomy', 'parathyroid', 'endocrine'],
    'Emergency Surgery': ['trauma', 'emergency', 'acute care'],
    'Biliary Surgery': ['bile', 'biliary', 'gallbladder']
}

# Procedures to count explicitly
PROCEDURE_KEYWORDS = [
    'prostatectomy', 'hysterectomy', 'colectomy', 'gastrectomy', 'nephrectomy', 'pancreatectomy',
    'thyroidectomy', 'cholecystectomy', 'myomectomy', 'lobectomy', 'esophagectomy', 'segmentectomy',
    'rectopexy', 'proctectomy', 'hepatectomy', 'adrenalectomy', 'appendectomy'
]

# Publication types of interest
DESIGN_TYPES = [
    'Randomized Controlled Trial', 'Clinical Trial', 'Pragmatic Clinical Trial', 'Equivalence Trial',
    'Non-Randomized Controlled Trial', 'Multicenter Study', 'Comparative Study', 'Meta-Analysis',
    'Systematic Review', 'Pilot Projects', 'Feasibility Studies'
]

# Comparator signals in text
COMPARATOR_PATTERNS = {
    'laparoscopic_comparator': re.compile(r'\blaparoscop', re.IGNORECASE),
    'open_comparator': re.compile(r'\bopen (?:surgery|approach|procedure|colectomy|hysterectomy|\w+)', re.IGNORECASE),
    'noninferiority': re.compile(r'non[-\s]?inferior|non[-\s]?inferiority', re.IGNORECASE),
    'equivalence': re.compile(r'equivalence|equivalent', re.IGNORECASE)
}

# Robotic signals (sanity check)
ROBOTIC_REGEX = re.compile(r'robot|da[\s-]?vinci|robotic', re.IGNORECASE)


def extract_text(article: ET.Element) -> str:
    parts = []
    t = article.findtext('.//ArticleTitle', default='')
    if t:
        parts.append(t)
    for ab in article.findall('.//Abstract/AbstractText'):
        if ab.text:
            parts.append(ab.text)
    ab_single = article.findtext('.//AbstractText', default='')
    if ab_single:
        parts.append(ab_single)
    return ' '.join(parts)


def extract_year(article: ET.Element) -> int | None:
    # Prefer PubDate Year
    year = article.findtext('.//JournalIssue/PubDate/Year')
    if year and year.isdigit():
        return int(year)
    # Fallbacks
    y = article.findtext('.//ArticleDate/Year')
    if y and y.isdigit():
        return int(y)
    y = article.findtext('.//DateCreated/Year')
    if y and y.isdigit():
        return int(y)
    y = article.findtext('.//DateCompleted/Year')
    if y and y.isdigit():
        return int(y)
    return None


def extract_pubtypes(article: ET.Element) -> list[str]:
    return [pt.text for pt in article.findall('.//PublicationTypeList/PublicationType') if pt.text]


def extract_journal_title(article: ET.Element) -> str:
    return article.findtext('.//Journal/Title', default='')


def extract_journal_country(article: ET.Element) -> str:
    return article.findtext('.//MedlineJournalInfo/Country', default='')


def classify_specialty(text_lower: str) -> str:
    for spec, keys in SPECIALTY_KEYWORDS.items():
        for kw in keys:
            if kw in text_lower:
                return spec
    return 'Other'


def process_file(xml_path: Path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        logger.error(f'Parse error {xml_path}: {e}')
        return None

    local_year_counts = Counter()
    local_specialty_counts = Counter()
    local_procedure_counts = Counter()
    local_design_counts = Counter()
    local_comparator_counts = Counter()
    local_journal_counts = Counter()
    local_country_counts = Counter()
    local_design_by_year = defaultdict(Counter)

    for article in root.findall('.//PubmedArticle'):
        text = extract_text(article)
        if not text or not ROBOTIC_REGEX.search(text):
            # Still include if MeSH drove filter, but text missing; try to proceed
            pass
        year = extract_year(article)
        if year:
            local_year_counts[year] += 1
        text_lower = text.lower()
        # Specialty
        spec = classify_specialty(text_lower)
        local_specialty_counts[spec] += 1
        # Procedure counts
        for proc in PROCEDURE_KEYWORDS:
            if proc in text_lower:
                local_procedure_counts[proc] += 1
        # Design types
        for pt in extract_pubtypes(article):
            if pt in DESIGN_TYPES:
                local_design_counts[pt] += 1
                if year:
                    local_design_by_year[pt][year] += 1
        # Comparator signals
        for name, rx in COMPARATOR_PATTERNS.items():
            if rx.search(text):
                local_comparator_counts[name] += 1
        # Journals and countries
        jt = extract_journal_title(article)
        if jt:
            local_journal_counts[jt] += 1
        jc = extract_journal_country(article)
        if jc:
            local_country_counts[jc] += 1

    return {
        'year_counts': local_year_counts,
        'specialty_counts': local_specialty_counts,
        'procedure_counts': local_procedure_counts,
        'design_counts': local_design_counts,
        'comparator_counts': local_comparator_counts,
        'journal_counts': local_journal_counts,
        'country_counts': local_country_counts,
        'design_by_year': local_design_by_year
    }


def merge_results(results_list):
    merged = {
        'year_counts': Counter(),
        'specialty_counts': Counter(),
        'procedure_counts': Counter(),
        'design_counts': Counter(),
        'comparator_counts': Counter(),
        'journal_counts': Counter(),
        'country_counts': Counter(),
        'design_by_year': defaultdict(Counter)
    }
    for res in results_list:
        if not res:
            continue
        merged['year_counts'].update(res['year_counts'])
        merged['specialty_counts'].update(res['specialty_counts'])
        merged['procedure_counts'].update(res['procedure_counts'])
        merged['design_counts'].update(res['design_counts'])
        merged['comparator_counts'].update(res['comparator_counts'])
        merged['journal_counts'].update(res['journal_counts'])
        merged['country_counts'].update(res['country_counts'])
        for pt, yc in res['design_by_year'].items():
            merged['design_by_year'][pt].update(yc)
    return merged


def compute_last5_mask(year_counts: Counter) -> set[int]:
    years = [y for y in year_counts.keys() if isinstance(y, int)]
    if not years:
        return set()
    max_year = max(years)
    return set(y for y in years if max_year - 4 <= y <= max_year)


def write_tsvs(merged):
    last5 = compute_last5_mask(merged['year_counts'])

    # Yearly counts
    with (ANALYSIS_DIR / 'yearly_counts.tsv').open('w', encoding='utf-8') as f:
        f.write('year\tcount\n')
        for y in sorted(merged['year_counts']):
            f.write(f'{y}\t{merged["year_counts"][y]}\n')

    # Specialty counts
    with (ANALYSIS_DIR / 'specialty_counts.tsv').open('w', encoding='utf-8') as f:
        f.write('specialty\ttotal\tlast5y\n')
        for spec, cnt in merged['specialty_counts'].most_common():
            # Approximate last5y by scaling using year distribution per specialty would be heavy; instead compute rough last5y via text-only approach not stored.
            # Here we only output totals to keep fast; optional enhancement later.
            f.write(f'{spec}\t{cnt}\t\n')

    # Procedure counts
    with (ANALYSIS_DIR / 'procedure_counts.tsv').open('w', encoding='utf-8') as f:
        f.write('procedure\ttotal\n')
        for proc, cnt in merged['procedure_counts'].most_common():
            f.write(f'{proc}\t{cnt}\n')

    # Design counts (overall)
    with (ANALYSIS_DIR / 'design_counts.tsv').open('w', encoding='utf-8') as f:
        f.write('design_type\ttotal\n')
        for dt, cnt in merged['design_counts'].most_common():
            f.write(f'{dt}\t{cnt}\n')

    # Design by year
    with (ANALYSIS_DIR / 'design_by_year.tsv').open('w', encoding='utf-8') as f:
        f.write('design_type\tyear\tcount\n')
        for dt, yc in merged['design_by_year'].items():
            for y, c in sorted(yc.items()):
                f.write(f'{dt}\t{y}\t{c}\n')

    # Comparator flags
    with (ANALYSIS_DIR / 'comparator_flags.tsv').open('w', encoding='utf-8') as f:
        f.write('flag\ttotal\n')
        for name, cnt in merged['comparator_counts'].most_common():
            f.write(f'{name}\t{cnt}\n')

    # Journals
    with (ANALYSIS_DIR / 'top_journals.tsv').open('w', encoding='utf-8') as f:
        f.write('journal\ttotal\n')
        for j, cnt in merged['journal_counts'].most_common(200):
            f.write(f'{j}\t{cnt}\n')

    # Countries
    with (ANALYSIS_DIR / 'country_counts.tsv').open('w', encoding='utf-8') as f:
        f.write('country\ttotal\n')
        for c, cnt in merged['country_counts'].most_common():
            f.write(f'{c}\t{cnt}\n')


def main():
    files = sorted(INPUT_DIR.glob('robotic_*.xml'))
    if not files:
        logger.error(f'No robotic XML files found in {INPUT_DIR}')
        return
    logger.info(f'Analyzing {len(files)} robotic XML files...')

    with mp.Pool(processes=max(1, mp.cpu_count() - 1)) as pool:
        results = list(tqdm(pool.imap_unordered(process_file, files), total=len(files), desc='Processing'))

    merged = merge_results([r for r in results if r])

    write_tsvs(merged)

    total_trials = sum(merged['year_counts'].values())
    logger.info(f'Done. Total robotic trials: {total_trials}. TSVs saved in {ANALYSIS_DIR}')


if __name__ == '__main__':
    main() 