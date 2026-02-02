# Deliverable Datasheet

Expected extraction produces a top-level folder: `deliverable/` with the structure below.

## Directory tree (top levels)

.
./code
./data
./data/clinical_xml
./data/robotic_xml
./outputs
./outputs/clinical_analysis
./outputs/globalization
./outputs/robotic_analysis

## File counts

- Robotic XML files: 1481
- Clinical-trial XML files: 1481
- Robotic analysis TSVs: 8
- Clinical analysis TSVs: 6
- Globalization files (TSV+PNG): 6

## Sizes (du -sh)

128K	/Volumes/T7/PubMed Data/extractions/Surgical RCTs/robotic_surgery_trials/deliverable/ABSTRACT.txt
1.6M	/Volumes/T7/PubMed Data/extractions/Surgical RCTs/robotic_surgery_trials/deliverable/code
905M	/Volumes/T7/PubMed Data/extractions/Surgical RCTs/robotic_surgery_trials/deliverable/data
128K	/Volumes/T7/PubMed Data/extractions/Surgical RCTs/robotic_surgery_trials/deliverable/DATASHEET.md
5.9M	/Volumes/T7/PubMed Data/extractions/Surgical RCTs/robotic_surgery_trials/deliverable/outputs
128K	/Volumes/T7/PubMed Data/extractions/Surgical RCTs/robotic_surgery_trials/deliverable/README.md

## Key files and SHA256

3a509f2b9518d4c8a7a2b4fff6fc8d860bd7902b71181fa3e1222116666076a1  /Volumes/T7/PubMed Data/extractions/Surgical RCTs/robotic_surgery_trials/deliverable/ABSTRACT.txt
1b98c2d43e03dade1b3e6edec77e66dca40083a53e50ab4589dca1a410173466  /Volumes/T7/PubMed Data/extractions/Surgical RCTs/robotic_surgery_trials/deliverable/README.md
39a236cd9c97e69dfa83b247522bbb49e267cae1e9c70f0624ad8f1a606da562  /Volumes/T7/PubMed Data/extractions/Surgical RCTs/robotic_surgery_trials/deliverable/outputs/globalization/per_year_metrics.tsv
a2cfacf5c34c5948e085b836ab5a69d0ee9370d73abfdf1e0fb45df8ced2c437  /Volumes/T7/PubMed Data/extractions/Surgical RCTs/robotic_surgery_trials/deliverable/outputs/globalization/fig1_annual_trials_multicountry.png
c3e351f221219fd140f54ef84360c8003da8a27cd93882b9454d2d4333ef1771  /Volumes/T7/PubMed Data/extractions/Surgical RCTs/robotic_surgery_trials/deliverable/outputs/globalization/fig2_regional_shares.png
26d1acff3b1c6d24b5bfc7e1fd9e7647eefd90e10d39d5955bad384c8c31a9ab  /Volumes/T7/PubMed Data/extractions/Surgical RCTs/robotic_surgery_trials/deliverable/outputs/globalization/top_countries_overall.tsv
d75185f0e6f2d39f8d6f198f9f0bc5d6a39f77eea385cd20960c68690615c5a1  /Volumes/T7/PubMed Data/extractions/Surgical RCTs/robotic_surgery_trials/deliverable/outputs/globalization/top_countries_last5y.tsv

## How to verify after upload

1. Extract: `tar -xzf deliverable_YYYYMMDD_HHMM.tar.gz`
2. Confirm tree matches sections above.
3. Recompute checksums (macOS):
   `shasum -a 256 ABSTRACT.txt README.md outputs/globalization/*.png outputs/globalization/*.tsv`
   and compare to values listed here.

