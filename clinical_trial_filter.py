#!/usr/bin/env python3

import xml.etree.ElementTree as ET
from pathlib import Path
import logging
import multiprocessing as mp
from functools import partial
from tqdm import tqdm
import json
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Clinical Trial Publication Types
CLINICAL_TRIAL_PUBLICATION_TYPES = [
    'Randomized Controlled Trial',
    'Clinical Trial',
    'Controlled Clinical Trial',
    'Clinical Trial, Phase I',
    'Clinical Trial, Phase II', 
    'Clinical Trial, Phase III',
    'Clinical Trial, Phase IV',
    'Multicenter Study',
    'Comparative Study'
]

# Directories
EXTRACTED_BASELINE_DIR = Path("../../extracted/baseline")
EXTRACTED_UPDATES_DIR = Path("../../extracted/updates")
OUTPUT_DIR = Path("data")

def is_clinical_trial_publication(article):
    """Check if article is a clinical trial based on publication type."""
    pub_types = article.findall('./MedlineCitation/Article/PublicationTypeList/PublicationType')
    for pub_type in pub_types:
        if pub_type.text in CLINICAL_TRIAL_PUBLICATION_TYPES:
            return True
    return False

def filter_clinical_trials_from_xml(input_path, output_path):
    """Filter clinical trial papers from a single XML file using exact same approach as debug script."""
    logger.info(f"Processing {input_path.name}...")
    
    try:
        with open(input_path, 'r', encoding='utf-8') as in_file:
            # Write XML header
            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                out_file.write('<PubmedArticleSet>\n')
                
                # Use exact same approach as debug script
                context = ET.iterparse(in_file, events=('end',))
                
                matched_count = 0
                processed_count = 0
                
                logger.info(f"Processing articles in {input_path.name}...")
                
                for event, elem in context:
                    if elem.tag == 'PubmedArticle':
                        processed_count += 1
                        
                        # Check if it's a clinical trial - exact same logic as debug script
                        if is_clinical_trial_publication(elem):
                            matched_count += 1
                            
                            # Write the article to output
                            article_xml = ET.tostring(elem, encoding='unicode')
                            out_file.write(article_xml + '\n')
                        
                        # Update progress every 1000 articles
                        if processed_count % 1000 == 0:
                            logger.info(f"Processed {processed_count} articles, found {matched_count} clinical trials in {input_path.name}")
                        
                        # Clear element to free memory
                        elem.clear()
                
                # Close XML structure
                out_file.write('</PubmedArticleSet>\n')
                
                logger.info(f"Clinical trial filter: {matched_count}/{processed_count} papers matched in {input_path.name}")
                return matched_count
                
    except ET.ParseError as e:
        logger.error(f"XML parsing error in {input_path}: {e}")
        return 0
    except Exception as e:
        logger.error(f"Failed to process {input_path}: {e}")
        return 0

def process_single_file(xml_file, output_dir):
    """Process a single XML file for clinical trials."""
    # Skip hidden files and system files
    if xml_file.name.startswith('._') or xml_file.name.startswith('.'):
        logger.warning(f"Skipping hidden file: {xml_file.name}")
        return 0
    
    # Check if file is valid XML
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if not first_line.startswith('<?xml'):
                logger.warning(f"Skipping non-XML file: {xml_file.name}")
                return 0
    except Exception as e:
        logger.warning(f"Cannot read file {xml_file.name}: {e}")
        return 0
    
    output_file = output_dir / f"clinical_trials_{xml_file.name}"
    return filter_clinical_trials_from_xml(xml_file, output_file)

def main():
    """Main function to filter clinical trial papers from PubMed data using parallel processing."""
    logger.info("Loading PubMed data...")
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Get baseline XML files (exclude hidden files)
    baseline_xml_files = [f for f in EXTRACTED_BASELINE_DIR.glob('*.xml') if not f.name.startswith('._')]
    updates_xml_files = [f for f in EXTRACTED_UPDATES_DIR.glob('*.xml') if not f.name.startswith('._')]
    all_xml_files = baseline_xml_files + updates_xml_files
    
    # Debug: Print first few files being processed
    logger.info(f"First 5 baseline files: {[f.name for f in baseline_xml_files[:5]]}")
    logger.info(f"First 5 updates files: {[f.name for f in updates_xml_files[:5]]}")
    
    if not all_xml_files:
        logger.error(f"No XML files found in {EXTRACTED_BASELINE_DIR} or {EXTRACTED_UPDATES_DIR}")
        logger.error(f"Baseline directory exists: {EXTRACTED_BASELINE_DIR.exists()}")
        logger.error(f"Updates directory exists: {EXTRACTED_UPDATES_DIR.exists()}")
        logger.error(f"Baseline files found: {len(baseline_xml_files)}")
        logger.error(f"Updates files found: {len(updates_xml_files)}")
        return
    
    logger.info(f"Found {len(baseline_xml_files)} baseline files and {len(updates_xml_files)} updates files to process")
    logger.info(f"Total files to process: {len(all_xml_files)}")
    
    # Process files in smaller batches to avoid memory issues
    batch_size = 10
    total_clinical_trial_papers = 0
    successful_files = 0
    failed_files = 0
    
    logger.info(f"Processing files in batches of {batch_size}")
    
    # Process files in normal order (forwards)
    for i in range(0, len(all_xml_files), batch_size):
        batch = all_xml_files[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(all_xml_files) + batch_size - 1)//batch_size} ({len(batch)} files)")
        
        # Determine number of processes (use fewer cores for smaller batches)
        num_processes = min(4, len(batch), mp.cpu_count() - 1)
        logger.info(f"Using {num_processes} parallel processes for this batch")
        
        # Create partial function with fixed output directory
        process_func = partial(process_single_file, output_dir=OUTPUT_DIR)
        
        with mp.Pool(processes=num_processes) as pool:
            # Use imap to get results as they complete
            results = list(tqdm(
                pool.imap(process_func, batch),
                total=len(batch),
                desc=f"Batch {i//batch_size + 1}"
            ))
            
            for result in results:
                if result > 0:
                    total_clinical_trial_papers += result
                    successful_files += 1
                else:
                    failed_files += 1
    
    logger.info(f"Processing complete!")
    logger.info(f"Successful files: {successful_files}")
    logger.info(f"Failed files: {failed_files}")
    logger.info(f"Total clinical trial papers found: {total_clinical_trial_papers:,}")
    logger.info(f"Clinical trial papers saved as XML files in: {OUTPUT_DIR}")
    
    # Create summary
    summary = {
        'processing_date': datetime.now().isoformat(),
        'baseline_files_processed': len(baseline_xml_files),
        'updates_files_processed': len(updates_xml_files),
        'total_files_processed': len(all_xml_files),
        'successful_files': successful_files,
        'failed_files': failed_files,
        'clinical_trial_papers_found': total_clinical_trial_papers,
        'clinical_trial_publication_types_used': CLINICAL_TRIAL_PUBLICATION_TYPES,
        'output_directory': str(OUTPUT_DIR),
        'batch_size_used': batch_size
    }
    
    with open(OUTPUT_DIR / 'clinical_trial_filtering_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Summary saved to: {OUTPUT_DIR / 'clinical_trial_filtering_summary.json'}")

if __name__ == "__main__":
    main() 