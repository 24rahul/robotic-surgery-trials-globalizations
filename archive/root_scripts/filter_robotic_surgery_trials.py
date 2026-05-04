#!/usr/bin/env python3
"""
Filter robotic surgery clinical trials from surgery clinical trials XML files.

- Scans titles, abstracts, and MeSH for robotic-related signals
- Writes per-file XML outputs preserving full PubMed XML structure
- Includes a progress bar and summary counts
"""
import xml.etree.ElementTree as ET
from pathlib import Path
import re
import logging
from tqdm import tqdm
import multiprocessing as mp
from functools import partial
from collections import Counter
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Resolve paths relative to this script's location so it works from any CWD
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / 'surgery_clinical_trials'
OUTPUT_DIR = BASE_DIR / 'robotic_surgery_trials'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Compile regex patterns for robotic surgery
ROBOTIC_PATTERNS = [
    r"\brobotic(?:-assisted)?\b",
    r"\brobot[-\s]?assisted\b",
    r"\bsurgical robot[s]?\b",
    r"\brobotics\b",
    r"\bda[\s-]?vinci\b",
    r"\btransoral robotic\b",
    r"\brobot[-\s]?assisted laparoscopic\b",
    r"\brobot[-\s]?assisted thoracoscopic\b",
    r"\brobotic[-\s]?assisted laparoscopic\b",
    r"\brobotic[-\s]?assisted thoracoscopic\b",
    # Common procedure-specific phrases
    r"\brobotic (?:prostatectomy|hysterectomy|colectomy|gastrectomy|nephrectomy|pancreatectomy|thyroidectomy|cholecystectomy|myomectomy)\b",
    # Abbreviations (word boundaries to reduce false matches)
    r"\bRALP\b",
    r"\bRARP\b",
    r"\bRAPN\b",
    r"\bRATS\b",
    r"\bTORS\b",
]
ROBOTIC_REGEXES = [re.compile(pat, flags=re.IGNORECASE) for pat in ROBOTIC_PATTERNS]

MESH_HITS = [
    'robotic surgical procedures',
    'robotics'
]


def extract_article_text(article: ET.Element) -> str:
    parts = []
    title = article.findtext('.//ArticleTitle', default='')
    if title:
        parts.append(title)
    # Abstract may be structured; gather all text
    for ab in article.findall('.//Abstract/AbstractText'):
        if ab.text:
            parts.append(ab.text)
    # Fallback: single AbstractText
    ab_single = article.findtext('.//AbstractText', default='')
    if ab_single:
        parts.append(ab_single)
    return ' '.join(parts)


def extract_mesh_terms(article: ET.Element):
    terms = []
    for mh in article.findall('.//MeshHeading'):
        desc = mh.find('DescriptorName')
        if desc is not None and desc.text:
            terms.append(desc.text.lower())
    return terms


def is_robotic_trial(article: ET.Element) -> bool:
    # MeSH check
    mesh_terms = extract_mesh_terms(article)
    if any(hit in mesh_terms for hit in MESH_HITS):
        return True
    # Text check
    text = extract_article_text(article)
    if not text:
        return False
    for rx in ROBOTIC_REGEXES:
        if rx.search(text):
            return True
    return False


def filter_single_file(xml_path: Path) -> tuple:
    """Filter one input XML into an output XML with only robotic trials.
    Returns (input_file_name, kept_count, total_count).
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        logger.error(f'Parse error {xml_path}: {e}')
        return (xml_path.name, 0, 0)

    articles = root.findall('.//PubmedArticle')
    total = len(articles)

    # Build output tree
    out_root = ET.Element('PubmedArticleSet')
    kept = 0
    for art in articles:
        try:
            if is_robotic_trial(art):
                out_root.append(art)
                kept += 1
        except Exception:
            continue

    out_path = OUTPUT_DIR / f"robotic_{xml_path.name}"
    ET.ElementTree(out_root).write(out_path, encoding='utf-8', xml_declaration=True)

    return (xml_path.name, kept, total)


def main():
    files = sorted(INPUT_DIR.glob('surgery_clinical_trials_*.xml'))
    if not files:
        logger.error(f'No input files found in {INPUT_DIR}')
        return

    logger.info(f'Filtering robotic surgery trials from {len(files)} files...')

    results = []
    with mp.Pool(processes=max(1, mp.cpu_count() - 1)) as pool:
        for name, kept, total in tqdm(pool.imap_unordered(filter_single_file, files), total=len(files), desc='Filtering'):
            results.append((name, kept, total))

    # Summary
    kept_total = sum(k for _, k, _ in results)
    total_total = sum(t for _, _, t in results)
    pct = (kept_total / total_total * 100) if total_total else 0.0
    logger.info(f'Kept {kept_total} robotic trials from {total_total} surgical trials ({pct:.2f}%)')

    # Write summary TSV
    summary_path = OUTPUT_DIR / 'robotic_filter_summary.tsv'
    with summary_path.open('w', encoding='utf-8') as f:
        f.write('file\tkept\tinput_total\n')
        for name, kept, total in sorted(results):
            f.write(f'{name}\t{kept}\t{total}\n')
        f.write(f'TOTAL\t{kept_total}\t{total_total}\n')

    logger.info(f'Summary written to {summary_path}')


if __name__ == '__main__':
    main() 