#!/usr/bin/env python3
"""
Filter robotic surgery XMLs to only true clinical trials based on PublicationType.

Keeps PubmedArticle if PublicationTypeList contains either:
- Randomized Controlled Trial
- Any PublicationType containing the substring 'Clinical Trial' (e.g., 'Clinical Trial', 'Clinical Trial, Phase II', 'Pragmatic Clinical Trial')

Excludes records that do not meet the above (e.g., Comparative Study, Systematic Review, Meta-Analysis, Multicenter Study, Controlled Clinical Trial, Non-Randomized Controlled Trial).
"""
import xml.etree.ElementTree as ET
from pathlib import Path
import logging
from tqdm import tqdm
import multiprocessing as mp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / 'robotic_surgery_trials'
OUTPUT_DIR = BASE_DIR / 'robotic_surgery_trials_clinical'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def is_true_clinical_trial(article: ET.Element) -> bool:
    pts = [pt.text for pt in article.findall('.//PublicationTypeList/PublicationType') if pt.text]
    if not pts:
        return False
    for pt in pts:
        if pt == 'Randomized Controlled Trial':
            return True
        if 'Clinical Trial' in pt:
            return True
    return False


def filter_one(xml_path: Path) -> tuple[str, int, int]:
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        logger.error(f'Parse error {xml_path}: {e}')
        return (xml_path.name, 0, 0)

    arts = root.findall('.//PubmedArticle')
    total = len(arts)
    out_root = ET.Element('PubmedArticleSet')
    kept = 0
    for art in arts:
        try:
            if is_true_clinical_trial(art):
                out_root.append(art)
                kept += 1
        except Exception:
            continue

    out_path = OUTPUT_DIR / xml_path.name
    ET.ElementTree(out_root).write(out_path, encoding='utf-8', xml_declaration=True)
    return (xml_path.name, kept, total)


def main():
    files = sorted(INPUT_DIR.glob('robotic_*.xml'))
    if not files:
        logger.error(f'No input robotic XMLs in {INPUT_DIR}')
        return
    logger.info(f'Filtering to true clinical trials from {len(files)} files...')

    kept_total = 0
    total_total = 0
    with mp.Pool(processes=mp.cpu_count()-1 or 1) as pool:
        for name, kept, total in tqdm(pool.imap_unordered(filter_one, files), total=len(files), desc='Filtering'):
            kept_total += kept
            total_total += total
    pct = (kept_total/total_total*100) if total_total else 0
    logger.info(f'Kept {kept_total} true clinical trials from {total_total} robotic records ({pct:.2f}%)')

if __name__ == '__main__':
    main() 