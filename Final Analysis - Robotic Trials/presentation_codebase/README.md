# Robotic Surgery Clinical Trials - Global Equity Analysis

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This repository contains the analysis codebase for a conference presentation examining **25 years (2001-2025) of robotic surgery clinical trials** from PubMed/MEDLINE. The analysis focuses on global equity in robotic surgery research, investigating geographic distribution, international collaboration patterns, and the participation of low- and middle-income countries (LMICs).

**Key Question**: Has the globalization of robotic surgery research led to more equitable participation, or does a significant gap persist?

## Quick Start

```bash
# Install dependencies
pip install pandas numpy matplotlib scipy cartopy geopandas

# Generate all figures
python generate_all_figures.py
```

All 8 publication-quality figures will be saved to the `output/` folder.

## Figures Generated

| Figure | Filename | Description | Statistical Tests |
|--------|----------|-------------|-------------------|
| 1 | `fig1_trial_growth.png` | Trial growth over 25 years | Linear R², CAGR |
| 2a | `fig2a_hhi_concentration.png` | Geographic concentration trend | Linear R² |
| 2b | `fig2b_collaboration.png` | International collaboration trend | Spearman ρ |
| 3 | `fig3_regional_shift.png` | Regional distribution shift | Chi-square |
| 4 | `fig4_country_leaders.png` | Top 10 countries by trials | Income classification |
| 5 | `fig9_world_map.png` | Global trial distribution map | HIC/LMIC coloring |
| 6 | `fig10a_income_distribution.png` | Trials by World Bank income level | - |
| 7 | `fig_equity_summary.png` | 3-panel equity dashboard | Trend + collaboration |

## Key Findings

### Growth & Globalization
- **11× increase** in annual trials over 25 years
- **CAGR: 10.4%** compound annual growth rate
- Geographic concentration (HHI) **decreased from 2012 to 982** (more distributed)
- International collaboration **increased from 3% to 21%**

### Equity Gap
- LMIC share grew from **6% to 25%** of trials
- But **90% of LMIC trials are from China alone**
- Lower-middle income: only **2.3%** of trials
- Low income countries: **0%** of trials
- **No LMIC-LMIC collaborations** observed - all involve HICs

### Collaboration Patterns
- ~363 multi-country trials (16.2% of total)
- **79% HIC-HIC** collaborations
- **21% HIC-LMIC** collaborations
- **0% LMIC-LMIC** collaborations

## Directory Structure

```
presentation_codebase/
├── generate_all_figures.py    # Main script - generates all 8 figures
├── README.md                  # This documentation
├── data/                      # Input data files
│   ├── per_year_metrics.tsv       # Annual trial counts, HHI, collaboration rates
│   ├── top_countries_overall.tsv  # Country rankings (all years)
│   ├── top_countries_last5y.tsv   # Country rankings (2021-2025)
│   ├── three_way_split.csv        # HIC-only/LMIC-only/HIC-LMIC by year
│   ├── income_shares_by_year.csv  # Income level breakdown by year
│   └── world_bank_income.csv      # Official World Bank classifications
├── shapefiles/                # Natural Earth geographic data
│   └── ne_110m_admin_0_countries.*
└── output/                    # Generated figures (created automatically)
    └── *.png
```

## Data Sources

| Data | Source | Year |
|------|--------|------|
| Clinical trials | PubMed/MEDLINE | 2001-2025 |
| Income classifications | World Bank | 2024-2025 |
| Geographic boundaries | Natural Earth | 110m resolution |

### Data Processing Notes

- Trials identified using MeSH terms for robotic surgery AND clinical trials
- Country attribution based on author affiliations
- Multi-country trials counted once per country (explains regional shares >100%)
- World Bank income levels: High (HIC), Upper-middle, Lower-middle, Low (LMIC = non-HIC)

## Requirements

### Core Dependencies
```
pandas>=1.3.0
numpy>=1.20.0
matplotlib>=3.4.0
scipy>=1.7.0
```

### For World Map (fig9)
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

## Theme & Styling

All figures use a consistent **ARGOS grey/charcoal theme**:

| Element | Color | Hex |
|---------|-------|-----|
| Primary (HIC) | Dark charcoal | `#374151` |
| Secondary (LMIC) | Medium grey | `#6B7280` |
| Light | Light grey | `#9CA3AF` |
| Collaboration | Purple | `#8B5CF6` |
| Background | Off-white | `#FAFAFA` |

## Statistical Methods

| Test | Application | Interpretation |
|------|-------------|----------------|
| Linear R² | Trial growth, HHI trend | Goodness of fit |
| CAGR | Growth rate | Compound annual growth |
| Spearman ρ | Collaboration trend | Monotonic correlation |
| Chi-square | Regional shift | Distribution change significance |

## Usage Examples

### Generate specific figures only

```python
from generate_all_figures import *

# Load data
data = load_all_data()

# Generate only the world map
fig9_world_map(data)

# Generate only the equity summary
fig_equity_summary(data)
```

### Customize colors

```python
# Modify the COLORS dictionary in generate_all_figures.py
COLORS = {
    'primary': '#1E40AF',    # Change to blue
    'secondary': '#3B82F6',
    # ...
}
```

## Citation

If you use this analysis or figures, please cite:

```
[Author names]. Global Equity in Robotic Surgery Research: 
A 25-Year Analysis of Clinical Trials. [Conference], 2026.
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contact

For questions about the analysis or data, please open an issue on this repository.
