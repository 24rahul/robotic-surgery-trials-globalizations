# Robotic Surgery Clinical Trials — Global Equity Analysis

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Bibliometric analysis of **25 years (2001–2025) of robotic surgery clinical trials** from PubMed/MEDLINE, examining geographic distribution, international collaboration, and income-tier inequity in research participation.

## Quick Start

```bash
pip install pandas numpy matplotlib scipy tqdm cartopy geopandas python-docx
python pipeline/5_generate_figures.py     # main figures → output/
python pipeline/6_generate_supplements.py # supplemental figs/tables → output/supplementary/
python pipeline/7_convert_to_docx.py      # manuscript .docx files → manuscript/
```

## Repository Structure

```
robotic_surgery_trials/
├── pipeline/                 Ordered analysis scripts (1 → 7)
│   ├── 1_filter_clinical_trials.py        raw_data/ → filtered_data/
│   ├── 2_globalization_stats.py           filtered_data/ → data/*.tsv
│   ├── 3_income_trend.py                  data/world_bank_income.csv → data/income_shares_by_year.csv
│   ├── 3b_income_trend_time_varying.py    OGHIST → data/income_shares_by_year_tv.csv
│   ├── 4_three_way_split.py               data/three_way_split.csv
│   ├── 5_generate_figures.py              data/ → output/Figure_1..4.{png,pdf}
│   ├── 6_generate_supplements.py          data/ → output/supplementary/Supplementary_Figure_S1..3 + Table S1..3
│   └── 7_convert_to_docx.py               manuscript/manuscript.md → manuscript/*.docx
├── data/                     Processed data (intermediates + figure inputs)
├── raw_data/                 Raw PubMed MEDLINE XML (gitignored)
├── filtered_data/            Clinical-trial-filtered XML (gitignored)
├── shapefiles/               Natural Earth 1:110m country boundaries
├── output/                   Final figures
│   ├── Figure_1..4.{png,pdf}             Main manuscript figures (600 DPI)
│   └── supplementary/                    Supplementary figures (PNG/PDF) + tables (CSV)
├── manuscript/               Manuscript source + submission-ready Word documents
│   ├── manuscript.md                     Markdown source of record
│   ├── Manuscript.docx                   Main paper (text + tables + figures embedded)
│   ├── Supplementary_Tables.docx
│   └── Supplementary_Figures.docx
└── archive/                  Superseded iterations and legacy artifacts
    ├── final_analysis_iterations/
    ├── legacy_deliverable/
    ├── old_figures/                      Stale figures from initial codebase
    ├── old_pipeline/                     Initial figure-generation script
    ├── presentation/
    └── root_scripts/
```

## Pipeline

Each script is idempotent and uses `pathlib` to resolve paths relative to the repo root — run from anywhere.

| Step | Script | Reads | Writes |
|---|---|---|---|
| 1 | `1_filter_clinical_trials.py` | `raw_data/robotic_*.xml` | `filtered_data/robotic_*.xml` |
| 2 | `2_globalization_stats.py` | `filtered_data/robotic_*.xml` | `data/per_year_metrics.tsv`, `data/top_countries_*.tsv` |
| 3 | `3_income_trend.py` | `filtered_data/` + `data/world_bank_income.csv` | `data/income_shares_by_year.csv` |
| 3b | `3b_income_trend_time_varying.py` | `filtered_data/` + `data/world_bank_income_historical.csv` | `data/income_shares_by_year_tv.csv` |
| 4 | `4_three_way_split.py` | `data/income_shares_by_year.csv` | `data/three_way_split.csv` |
| 5 | `5_generate_figures.py` | `data/` + `shapefiles/` | `output/Figure_1..4.{png,pdf}` |
| 6 | `6_generate_supplements.py` | `data/` | `output/supplementary/` |
| 7 | `7_convert_to_docx.py` | `manuscript/manuscript.md` + `output/` | `manuscript/*.docx` |

## Key Findings

| Metric | 2001–2005 | 2021–2025 |
|---|---:|---:|
| Annual trials | 27 | 194 |
| Distinct contributing countries / yr | 10 | 26 |
| HHI (geographic concentration) | 2,012 | 982 |
| Multi-country collaboration share | 3.1% | 21.2% |
| HIC share of country-trial participations | 87.0% | 75.1% |
| LMIC share | 6.5% | 2.1% |
| Non-HIC share *excluding China* | 9.4% | 6.2% |

**Headline equity findings (2001–2025 cumulative, time-varying World Bank classification):**
- 2,232 trials; 2,777 country-trial participations; 47 contributing countries
- HIC 81.7% / UMIC 15.7% / LMIC 2.6% / LIC 0.04% (one trial)
- Per-million population production: HIC 1.81 / UMIC 0.17 / LMIC 0.021 / LIC 0.001 (≈86-fold HIC–LMIC gap)
- Aggregate non-HIC rise (13.0% → 24.9%) is entirely driven by China; non-HIC excluding China declined from 9.4% to 6.2%

## Data Sources

| Data | Source | Notes |
|---|---|---|
| Clinical trials | PubMed/MEDLINE | 2025 annual baseline + daily updates through 8 Aug 2025 |
| Income classifications | World Bank OGHIST 1987–2021 + 2024–25 forward-fill | Turkey/Czechia pre-rename rows manually supplemented |
| Country boundaries | Natural Earth | 1:110m resolution |

### Raw XML

Raw PubMed XML files are excluded from git. To regenerate from scratch:

1. Download the PubMed MEDLINE baseline into `raw_data/`
2. Run `pipeline/1_filter_clinical_trials.py` (populates `filtered_data/`)
3. Run steps 2 → 7 to regenerate `data/`, `output/`, and `manuscript/*.docx`

## Citation

```
[Authors]. Shifting Geography of Robotic Surgery Clinical Trials:
A 25-Year Bibliometric Analysis of Research Redistribution and
Persistent Income-Tier Inequity. [Journal], 2026.
```

## License

MIT — see [LICENSE](LICENSE).
