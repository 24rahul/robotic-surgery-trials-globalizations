## Robotic Surgery Clinical Trials: 25-Year Globalization Analysis (Deliverable)

This package contains the extracted data, analysis code, outputs, figures, and abstract for the 25-year globalization study of robotic surgery clinical trials.

### Directory Structure

- `data/`
  - `robotic_xml/`: Robotic surgery XML files (all robotic surgery papers from the surgery subset; one file per PubMed batch).
  - `clinical_xml/`: Clinical-trial-only robotic XML files (PublicationType contains "Randomized Controlled Trial" or includes "Clinical Trial").
- `code/`: All scripts to reproduce filtering and analysis.
- `outputs/`
  - `robotic_analysis/`: TSVs from descriptive stats on all robotic surgery papers (not restricted to clinical trials).
  - `clinical_analysis/`: TSVs from descriptive stats on clinical-trial-only robotic set.
  - `globalization/`: 25-year globalization metrics and figures for the clinical-trial-only set.
- `ABSTRACT.txt`: Final abstract text.
- `README.md`: This document.

### Data Provenance

- Source: PubMed baseline and updates (XML). Surgical subset was identified previously; robotic surgery subset was filtered using MeSH and keyword matching in titles/abstracts.
- Clinical-trial-only cohort is defined by PublicationType containing either "Randomized Controlled Trial" or the substring "Clinical Trial".

### Environment

- Python 3.10+
- Recommended packages: `tqdm`, `pandas`, `matplotlib` (install via `pip install -r requirements.txt` if needed).

### Scripts (in `code/`)

- `filter_robotic_surgery_trials.py`
  - Input: `../surgery_clinical_trials/*.xml`
  - Output: `../robotic_surgery_trials/robotic_*.xml`
  - Purpose: Extract robotic surgery papers from surgery clinical trials using MeSH and keyword rules; preserves full XML.

- `robotic_trials_stats.py`
  - Input: `../robotic_surgery_trials/robotic_*.xml`
  - Output TSVs: `../robotic_surgery_trials/analysis/`
  - Purpose: Descriptive statistics on the full robotic surgery set (yearly counts, specialties, procedures, design types, comparator signals, journals, countries).

- `filter_true_clinical_trials.py`
  - Input: `../robotic_surgery_trials/robotic_*.xml`
  - Output: `../robotic_surgery_trials_clinical/robotic_*.xml`
  - Inclusion: PublicationType == "Randomized Controlled Trial" OR PublicationType contains "Clinical Trial" (captures phases and variants).
  - Exclusion: All others (e.g., Comparative Study, Systematic Review, Meta-Analysis, Multicenter Study).

- `robotic_trials_stats_true_clinical.py`
  - Input: `../robotic_surgery_trials_clinical/robotic_*.xml`
  - Output TSVs: `../robotic_surgery_trials_clinical/analysis/`
  - Purpose: Descriptive statistics on the clinical-trial-only cohort.

- `robotic_globalization_25y.py`
  - Input: `../robotic_surgery_trials_clinical/robotic_*.xml`
  - Output TSVs: `../robotic_surgery_trials_clinical/globalization/`
  - Metrics per year (last 25 years window):
    - Total trials, number of active countries
    - Multi-country share (≥2 distinct countries per trial from affiliations)
    - Average countries per trial
    - HHI of country concentration
    - Regional shares (Europe, Asia, North America, Oceania, Latin America, Middle East, Africa)
    - Top countries overall and last-5-years; a sample of multi-country trials with PMIDs
  - Country attribution: parsed from author affiliations (normalized), with journal country as fallback.

- `robotic_globalization_figures.py`
  - Input: `../robotic_surgery_trials_clinical/globalization/per_year_metrics.tsv`
  - Output PNGs: `fig1_annual_trials_multicountry.png`, `fig2_regional_shares.png`

### How to Reproduce (from `extractions/Surgical RCTs/`)

1) Filter robotic surgery subset (already done):
```
python3 filter_robotic_surgery_trials.py
```

2) Descriptive stats on all robotic (already done):
```
python3 robotic_trials_stats.py
```

3) Restrict to true clinical trials (RCT or PublicationType contains "Clinical Trial"): 
```
python3 filter_true_clinical_trials.py
```

4) Descriptive stats on clinical-trial-only cohort:
```
python3 robotic_trials_stats_true_clinical.py
```

5) 25-year globalization metrics and figures:
```
python3 robotic_globalization_25y.py
python3 robotic_globalization_figures.py
```

### Outputs Summary

- Clinical-trial-only cohort size: 2,361 trials.
- Per-year metrics file: `outputs/globalization/per_year_metrics.tsv`
- Top countries overall and last 5 years: `outputs/globalization/top_countries_overall.tsv`, `top_countries_last5y.tsv`
- Figures: `outputs/globalization/fig1_annual_trials_multicountry.png`, `fig2_regional_shares.png`

### Notes and Assumptions

- Clinical-trial definition: strictly PublicationType-based as above; this excludes Comparative Study, Systematic Review, etc.
- Country parsing: best-effort from affiliations; if affiliations absent, falls back to journal country. Multi-country defined as ≥2 unique countries per trial.
- Specialty classification in stats scripts uses keyword heuristics on title/abstract and is intended for aggregate summaries.
- All XML outputs preserve PubMed structure inside a `PubmedArticleSet` container.

### Contact

This deliverable was generated automatically from your PubMed processing workspace. Scripts are self-contained and resolve paths relative to script locations for portability. 