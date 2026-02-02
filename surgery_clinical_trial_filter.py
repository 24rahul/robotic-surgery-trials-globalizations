#!/usr/bin/env python3
"""
Filter surgery-related clinical trials from clinical trial XML files.

This script filters clinical trial papers to only include surgery-related ones,
preserving complete XML structure and all metadata.
"""
import os
import json
from pathlib import Path
from tqdm import tqdm
import xml.etree.ElementTree as ET
import re
import logging
from datetime import datetime
import multiprocessing as mp
from functools import partial

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Surgery keywords from published peer-reviewed papers
SURGERY_KEYWORDS = [
    'surgery', 'surgical', 'surgeon', 'operative', 'operation',
    'preoperative', 'intraoperative', 'postoperative', 'perioperative',
    'operative procedure', 'operative procedures', 'surgical procedure', 'surgical procedures',
    'laparoscopic surgery', 'robotic surgery', 'minimally invasive surgery',
    'image-guided surgery', 'endoscopic surgery', 'open surgery',
    'reconstructive surgery', 'microsurgery', 'autonomous surgery',
    'arthroplasty', 'joint replacement', 'prosthesis implantation',
    'anastomosis', 'debridement', 'reoperation',
    'tumor resection', 'surgical biopsy', 'bypass surgery',
    'appendectomy', 'cholecystectomy', 'mastectomy', 'hysterectomy',
    'craniotomy', 'laparotomy',
    'surgical planning', 'surgical outcome', 'surgical outcomes',
    'surgical complication', 'surgical training', 'surgical simulation',
    'surgical performance', 'surgical risk prediction', 'surgical error detection',
    # Additional surgery-specific terms
    'cardiac surgery', 'cardiovascular surgery', 'thoracic surgery',
    'orthopedic surgery', 'neurosurgery', 'plastic surgery',
    'general surgery', 'vascular surgery', 'urologic surgery',
    'gynecologic surgery', 'otolaryngology', 'ophthalmologic surgery',
    'transplant surgery', 'trauma surgery', 'emergency surgery',
    'elective surgery', 'ambulatory surgery', 'day surgery',
    'surgical wound', 'surgical site', 'surgical incision',
    'surgical technique', 'surgical approach', 'surgical method',
    'surgical intervention', 'surgical treatment', 'surgical therapy',
    'surgical management', 'surgical care', 'surgical team',
    'surgical suite', 'operating room', 'operating theatre',
    'surgical instrument', 'surgical device', 'surgical tool',
    'surgical equipment', 'surgical robot', 'surgical navigation',
    'surgical guidance', 'surgical imaging', 'surgical visualization'
]
SURGERY_KEYWORDS = [k.lower() for k in SURGERY_KEYWORDS]

# Paths
CLINICAL_TRIALS_DIR = Path("data")
SURGERY_CLINICAL_TRIALS_DIR = Path("surgery_clinical_trials")
SURGERY_CLINICAL_TRIALS_DIR.mkdir(parents=True, exist_ok=True)

# Helper: check if any surgery keyword is in text
def contains_surgery_keyword(text):
    if not text:
        return False
    text = text.lower()
    
    # Use word boundary matching to avoid false positives
    for kw in SURGERY_KEYWORDS:
        # Create pattern with word boundaries for multi-word terms
        if ' ' in kw:
            pattern = r'\b' + re.escape(kw) + r'\b'
        else:
            # For single words, check for word boundaries
            pattern = r'\b' + re.escape(kw) + r'\b'
        
        if re.search(pattern, text):
            return True
    return False

def extract_text_for_search(article):
    """Extract all searchable text from a PubMed article."""
    text_parts = []
    
    # Title
    title = article.findtext('./MedlineCitation/Article/ArticleTitle', default='')
    if title:
        text_parts.append(title)
    
    # Abstract
    abstract_elem = article.find('./MedlineCitation/Article/Abstract/AbstractText')
    if abstract_elem is not None:
        if abstract_elem.text:
            text_parts.append(abstract_elem.text)
        else:
            # Handle structured abstracts
            for section in abstract_elem:
                if section.text:
                    text_parts.append(section.text)
    
    # MeSH terms
    for mesh_heading in article.findall('./MedlineCitation/MeshHeadingList/MeshHeading'):
        descriptor = mesh_heading.find('DescriptorName')
        if descriptor is not None and descriptor.text:
            text_parts.append(descriptor.text)
        # Add qualifiers
        for qualifier in mesh_heading.findall('QualifierName'):
            if qualifier.text:
                text_parts.append(qualifier.text)
    
    # Keywords
    for kw in article.findall('./MedlineCitation/Article/Abstract/AbstractText'):
        if kw.text:
            text_parts.append(kw.text)
    
    # Author affiliations
    for author in article.findall('./MedlineCitation/Article/AuthorList/Author'):
        for aff_info in author.findall('./AffiliationInfo/Affiliation'):
            if aff_info.text:
                text_parts.append(aff_info.text)
    
    # Journal title
    journal = article.findtext('./MedlineCitation/Article/Journal/Title', default='')
    if journal:
        text_parts.append(journal)
    
    return ' '.join(text_parts)

def filter_surgery_from_clinical_trials_xml(input_path, output_path):
    """Filter clinical trial XML file for surgery-related papers, preserving complete XML structure."""
    try:
        # Create output file with proper XML structure
        with open(output_path, 'w', encoding='utf-8') as out_file:
            # Write XML header
            out_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            out_file.write('<PubmedArticleSet>\n')
            
            # Process articles
            context = ET.iterparse(input_path, events=("end",))
            matched_count = 0
            processed_count = 0
            
            for event, elem in context:
                if elem.tag.endswith("PubmedArticle"):
                    processed_count += 1
                    
                    # Extract all searchable text
                    searchable_text = extract_text_for_search(elem)
                    
                    # Check if article contains surgery keywords
                    if contains_surgery_keyword(searchable_text):
                        # Write the complete article XML
                        article_xml = ET.tostring(elem, encoding='unicode', method='xml')
                        out_file.write(article_xml + '\n')
                        matched_count += 1
                    
                    # Clear element to free memory
                    elem.clear()
            
            # Close XML structure
            out_file.write('</PubmedArticleSet>\n')
            
            logger.info(f"Surgery filter: {matched_count}/{processed_count} papers matched in {input_path.name}")
            return matched_count
            
    except Exception as e:
        logger.error(f"Failed to process {input_path}: {e}")
        return 0

def process_single_surgery_file(clinical_trial_file, output_dir):
    """Process a single clinical trial XML file for surgery papers."""
    output_file = output_dir / f"surgery_{clinical_trial_file.name}"
    return filter_surgery_from_clinical_trials_xml(clinical_trial_file, output_file)

def main():
    """Main function to filter surgery clinical trials using parallel processing."""
    logger.info("Loading clinical trial papers...")
    
    # Check if clinical trials directory exists
    if not CLINICAL_TRIALS_DIR.exists():
        logger.error(f"Clinical trials directory not found: {CLINICAL_TRIALS_DIR}")
        logger.error("Please run clinical_trial_filter.py first")
        return
    
    # Get clinical trial XML files
    clinical_trial_xml_files = list(CLINICAL_TRIALS_DIR.glob('clinical_trials_*.xml'))
    if not clinical_trial_xml_files:
        logger.error(f"No clinical trial XML files found in {CLINICAL_TRIALS_DIR}")
        logger.error("Please run clinical_trial_filter.py first")
        return
    
    logger.info(f"Found {len(clinical_trial_xml_files)} clinical trial XML files to process")
    
    # Process files in smaller batches to avoid memory issues
    batch_size = 10
    total_surgery_clinical_trials = 0
    successful_files = 0
    failed_files = 0
    
    logger.info(f"Processing files in batches of {batch_size}")
    
    # Process files in batches
    for i in range(0, len(clinical_trial_xml_files), batch_size):
        batch = clinical_trial_xml_files[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(clinical_trial_xml_files) + batch_size - 1)//batch_size} ({len(batch)} files)")
        
        # Determine number of processes (use fewer cores for smaller batches)
        num_processes = min(4, len(batch), mp.cpu_count() - 1)
        logger.info(f"Using {num_processes} parallel processes for this batch")
        
        # Create partial function with fixed output directory
        process_func = partial(process_single_surgery_file, output_dir=SURGERY_CLINICAL_TRIALS_DIR)
        
        with mp.Pool(processes=num_processes) as pool:
            # Use imap to get results as they complete
            results = list(tqdm(
                pool.imap(process_func, batch),
                total=len(batch),
                desc=f"Batch {i//batch_size + 1}"
            ))
            
            for result in results:
                if result > 0:
                    total_surgery_clinical_trials += result
                    successful_files += 1
                else:
                    failed_files += 1
    
    logger.info(f"Processing complete!")
    logger.info(f"Successful files: {successful_files}")
    logger.info(f"Failed files: {failed_files}")
    logger.info(f"Total surgery clinical trial papers found: {total_surgery_clinical_trials:,}")
    logger.info(f"Surgery clinical trial papers saved as XML files in: {SURGERY_CLINICAL_TRIALS_DIR}")
    
    # Create summary
    summary = {
        'processing_date': datetime.now().isoformat(),
        'clinical_trial_files_processed': len(clinical_trial_xml_files),
        'successful_files': successful_files,
        'failed_files': failed_files,
        'surgery_clinical_trial_papers_found': total_surgery_clinical_trials,
        'surgery_keywords_used': SURGERY_KEYWORDS,
        'output_directory': str(SURGERY_CLINICAL_TRIALS_DIR),
        'batch_size_used': batch_size
    }
    
    with open(SURGERY_CLINICAL_TRIALS_DIR / 'surgery_clinical_trial_filtering_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Summary saved to: {SURGERY_CLINICAL_TRIALS_DIR / 'surgery_clinical_trial_filtering_summary.json'}")

if __name__ == "__main__":
    main() 