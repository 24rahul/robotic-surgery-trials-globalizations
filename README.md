# Robotic Surgery Clinical Trials - Global Equity Analysis

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This repository contains a comprehensive bibliometric analysis of **25 years (2001-2025) of robotic surgery clinical trials** from PubMed/MEDLINE. The study examines global equity in robotic surgery research, investigating geographic distribution, international collaboration patterns, and participation of low- and middle-income countries (LMICs).

---

## ⭐ Quick Start - Final Presentation Figures

**For the final, clean codebase that generates all presentation figures:**

```bash
cd "Final Analysis - Robotic Trials/presentation_codebase"
pip install pandas numpy matplotlib scipy cartopy geopandas
python generate_all_figures.py
```

See [`Final Analysis - Robotic Trials/presentation_codebase/README.md`](Final%20Analysis%20-%20Robotic%20Trials/presentation_codebase/README.md) for detailed documentation.

---

## Repository Structure

```
robotic_surgery_trials/
│
├── 📁 Final Analysis - Robotic Trials/
│   │
│   ├── ⭐ presentation_codebase/          ← FINAL CLEAN CODEBASE
│   │   ├── generate_all_figures.py        # Single script generates all 8 figures
│   │   ├── README.md                      # Detailed documentation
│   │   ├── data/                          # Processed data files
│   │   ├── shapefiles/                    # Geographic data
│   │   └── output/                        # Generated figures
│   │
│   ├── data/                              # All processed data files
│   ├── figures/                           # Initial figure iterations
│   ├── figures_elegant/                   # Refined figures
│   ├── tables/                            # Summary tables
│   └── *.py                               # Various analysis scripts
│
├── 📁 robotic_surgery_trials/             # Raw PubMed data (all trials)
│   └── *.xml                              # ~9000 XML files (not in git)
│
├── 📁 robotic_surgery_trials_clinical/    # Filtered clinical trials
│   └── *.xml                              # ~3000 XML files (not in git)
│
├── 📁 presentation/                       # Earlier presentation drafts
│
└── *.py                                   # Data processing scripts
```

## Key Findings

| Metric | 2001-2005 | 2021-2025 | Change |
|--------|-----------|-----------|--------|
| Annual trials | 27 | 194 | +618% |
| Countries with trials | 10 | 26 | +16 |
| LMIC share | 6% | 25% | +19pp |
| International collaboration | 3% | 21% | +18pp |
| HHI (concentration) | 2012 | 982 | -51% |

### Critical Equity Gaps

- **China dominance**: 90% of LMIC trials come from China alone
- **Lower-middle income**: Only 2.3% of trials
- **Low income**: 0% of trials
- **No South-South collaboration**: All international collaborations involve HICs

## Data Pipeline

### 1. Data Collection
```bash
# PubMed search query
("Robotic Surgical Procedures"[MeSH] OR "robot-assisted"[tiab]) 
AND ("Clinical Trial"[pt] OR "clinical trial"[tiab])
```

### 2. Filtering
```bash
python filter_robotic_surgery_trials.py    # Initial filter
python filter_true_clinical_trials.py      # Strict clinical trial filter
```

### 3. Analysis
```bash
python robotic_trials_stats_true_clinical.py   # Generate metrics
```

### 4. Figure Generation
```bash
cd "Final Analysis - Robotic Trials/presentation_codebase"
python generate_all_figures.py
```

## Generated Figures

| # | Figure | Description |
|---|--------|-------------|
| 1 | `fig1_trial_growth.png` | 25-year trial growth with CAGR & R² |
| 2a | `fig2a_hhi_concentration.png` | Geographic concentration declining |
| 2b | `fig2b_collaboration.png` | International collaboration rising |
| 3 | `fig3_regional_shift.png` | Regional distribution with χ² test |
| 4 | `fig4_country_leaders.png` | Top 10 countries by income level |
| 5 | `fig9_world_map.png` | Global map with HIC/LMIC bubbles |
| 6 | `fig10a_income_distribution.png` | Trials by World Bank income level |
| 7 | `fig_equity_summary.png` | 3-panel equity dashboard |

## Requirements

### Core
```
pandas>=1.3.0
numpy>=1.20.0
matplotlib>=3.4.0
scipy>=1.7.0
```

### For World Maps
```
cartopy>=0.20.0
geopandas>=0.10.0
```

### Installation
```bash
# Using pip
pip install pandas numpy matplotlib scipy cartopy geopandas

# Using conda (recommended for cartopy)
conda install -c conda-forge pandas numpy matplotlib scipy cartopy geopandas
```

## Data Sources

| Data | Source | Notes |
|------|--------|-------|
| Clinical trials | PubMed/MEDLINE | 2001-2025, MeSH filtered |
| Income classifications | World Bank | 2024-2025 fiscal year |
| Geographic boundaries | Natural Earth | 110m resolution |

## Raw Data

The raw XML files from PubMed (~12,000 files) are excluded from git due to size.

To obtain the raw data:
1. Search PubMed with the query above
2. Export results in XML format
3. Place in `robotic_surgery_trials/` and `robotic_surgery_trials_clinical/`

## Citation

```
[Authors]. Global Equity in Robotic Surgery Research: 
A 25-Year Bibliometric Analysis of Clinical Trials. [Conference], 2026.
```

## License

MIT License - see [LICENSE](Final%20Analysis%20-%20Robotic%20Trials/presentation_codebase/LICENSE) for details.
