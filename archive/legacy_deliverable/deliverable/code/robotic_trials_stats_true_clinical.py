#!/usr/bin/env python3
"""
Compute descriptive statistics for TRUE clinical trial robotic surgery papers
(from robotic_surgery_trials_clinical directory).

Outputs TSVs into robotic_surgery_trials_clinical/analysis/
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter, defaultdict
import multiprocessing as mp
from tqdm import tqdm
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / 'robotic_surgery_trials_clinical'
ANALYSIS_DIR = INPUT_DIR / 'analysis'
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

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

PROCEDURE_KEYWORDS = [
    'prostatectomy', 'hysterectomy', 'colectomy', 'gastrectomy', 'nephrectomy', 'pancreatectomy',
    'thyroidectomy', 'cholecystectomy', 'myomectomy', 'lobectomy', 'esophagectomy', 'segmentectomy',
    'rectopexy', 'proctectomy', 'hepatectomy', 'adrenalectomy', 'appendectomy'
]

COMPARATOR_PATTERNS = {
    'laparoscopic_comparator': re.compile(r'\blaparoscop', re.IGNORECASE),
    'open_comparator': re.compile(r'\bopen (?:surgery|approach|procedure|colectomy|hysterectomy|\w+)', re.IGNORECASE),
    'noninferiority': re.compile(r'non[-\s]?inferior|non[-\s]?inferiority', re.IGNORECASE),
    'equivalence': re.compile(r'equivalence|equivalent', re.IGNORECASE)
}

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


def extract_year(article: ET.Element):
    year = article.findtext('.//JournalIssue/PubDate/Year')
    if year and year.isdigit():
        return int(year)
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


def extract_pubtypes(article: ET.Element):
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
    except Exception:
        return None

    local_year_counts = Counter()
    local_specialty_counts = Counter()
    local_procedure_counts = Counter()
    local_comparator_counts = Counter()
    local_journal_counts = Counter()
    local_country_counts = Counter()

    for article in root.findall('.//PubmedArticle'):
        text = extract_text(article)
        if not text:
            continue
        year = extract_year(article)
        if year:
            local_year_counts[year] += 1
        tl = text.lower()
        spec = classify_specialty(tl)
        local_specialty_counts[spec] += 1
        for proc in PROCEDURE_KEYWORDS:
            if proc in tl:
                local_procedure_counts[proc] += 1
        for name, rx in COMPARATOR_PATTERNS.items():
            if rx.search(text):
                local_comparator_counts[name] += 1
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
        'comparator_counts': local_comparator_counts,
        'journal_counts': local_journal_counts,
        'country_counts': local_country_counts
    }


def merge(results_list):
    m = {
        'year_counts': Counter(),
        'specialty_counts': Counter(),
        'procedure_counts': Counter(),
        'comparator_counts': Counter(),
        'journal_counts': Counter(),
        'country_counts': Counter()
    }
    for r in results_list:
        if not r:
            continue
        for k in m.keys():
            m[k].update(r[k])
    return m


def write_tsvs(m):
    with (ANALYSIS_DIR / 'yearly_counts.tsv').open('w') as f:
        f.write('year\tcount\n')
        for y in sorted(m['year_counts']):
            f.write(f'{y}\t{m["year_counts"][y]}\n')
    with (ANALYSIS_DIR / 'specialty_counts.tsv').open('w') as f:
        f.write('specialty\ttotal\n')
        for s,c in m['specialty_counts'].most_common():
            f.write(f'{s}\t{c}\n')
    with (ANALYSIS_DIR / 'procedure_counts.tsv').open('w') as f:
        f.write('procedure\ttotal\n')
        for p,c in m['procedure_counts'].most_common():
            f.write(f'{p}\t{c}\n')
    with (ANALYSIS_DIR / 'comparator_flags.tsv').open('w') as f:
        f.write('flag\ttotal\n')
        for n,c in m['comparator_counts'].most_common():
            f.write(f'{n}\t{c}\n')
    with (ANALYSIS_DIR / 'top_journals.tsv').open('w') as f:
        f.write('journal\ttotal\n')
        for j,c in m['journal_counts'].most_common(200):
            f.write(f'{j}\t{c}\n')
    with (ANALYSIS_DIR / 'country_counts.tsv').open('w') as f:
        f.write('country\ttotal\n')
        for c,cnt in m['country_counts'].most_common():
            f.write(f'{c}\t{cnt}\n')


def main():
    files = sorted(INPUT_DIR.glob('robotic_*.xml'))
    if not files:
        logger.error('No clinical robotic XMLs found')
        return
    logger.info(f'Analyzing {len(files)} clinical robotic XML files...')
    with mp.Pool(processes=max(1, mp.cpu_count()-1)) as pool:
        res = list(tqdm(pool.imap_unordered(process_file, files), total=len(files), desc='Processing'))
    m = merge([r for r in res if r])
    write_tsvs(m)
    total = sum(m['year_counts'].values())
    logger.info(f'Done. Total true clinical trials: {total}. TSVs in {ANALYSIS_DIR}')

if __name__ == '__main__':
    main() 