# Shifting Geography of Robotic Surgery Clinical Trials: A 25-Year Bibliometric Analysis of Research Redistribution and Persistent Income-Tier Inequity

**Rahul Gorijavolu, BS¹; Kaushik Madapati¹; Ife Shoyombo, MD, MS, MPH¹; Leo A. Celi, MD, MS, MPH; Joseph V. Sakran, MD, MPH, MPA¹**

¹[Institutional affiliations to be added]

**Corresponding Author:** [Contact information to be added]

**Word Count:** [To be calculated]
**Tables:** 2
**Figures:** 4
**Supplementary Tables:** 3
**Supplementary Figures:** 3

**Keywords:** robotic surgery; clinical trials; global surgery; health equity; bibliometric analysis; research capacity; low- and middle-income countries

---

## ABSTRACT

**Background.** Since the widespread adoption of the da Vinci Surgical System in 2000, robotic surgery has undergone rapid technological evolution, including new platforms and telesurgical applications. The geographic distribution of clinical trials that generate the evidence base for these technologies has not been comprehensively characterized across the full 25-year period of commercial deployment.

**Objective.** To characterize the temporal and geographic redistribution of robotic surgery clinical trials from 2001 through 2025 and to quantify persistent inequity in research participation across countries of different income levels.

**Methods.** We conducted a bibliometric analysis of 2,232 robotic surgery clinical trials indexed in PubMed/MEDLINE between January 1, 2001 and August 8, 2025. Country attribution was derived from author affiliations, with fallback to the MedlineJournalInfo/Country field when no affiliation-based country could be identified. Income classifications were applied on a year-specific basis using the World Bank's analytical history (1987–2021) with forward-fill through 2025, supplemented with published classifications for Turkey and Czechia where the source file contained post-rename rows only. Outcomes included annual trial volume, Herfindahl-Hirschman concentration (HHI), multi-country collaboration share, regional composition, and income-tier distribution. Temporal trends were tested using Spearman rank correlation with Benjamini-Hochberg adjustment for multiple comparisons. Income-tier inequity was evaluated against three null distributions: world population, gross domestic product (GDP), and global health research-and-development (R&D) expenditure.

**Results.** Annual trial volume increased from a mean of 27 trials per year during 2001–2005 to 194 per year during 2021–2025 (compound annual growth rate 10.35%; Spearman *ρ* = 0.983; *q* < 0.001). Geographic concentration declined (HHI 2,012 → 982; *ρ* = −0.793; *q* < 0.001), the number of participating countries per year rose from 10 to 26, and multi-country collaboration rose from 3.1% to 21.2% of trials. Asia's share of country-trial participations rose from 15.2% to 39.5% (+24.3 percentage points), Europe's rose from 35.3% to 53.4%, North America's declined from 39.3% to 25.0%, and Africa's remained below 1%. Of 2,777 country-trial participations across 47 contributing countries, 81.7% originated in high-income countries (HICs), 15.7% in upper-middle-income (UMICs), 2.6% in lower-middle-income (LMICs), and 0.04% in low-income countries (LICs; one trial, Pakistan 2004 when classified as low-income). When compared with world-population shares, this deviation was extreme (*χ*² = 9,328; Cohen's *w* = 1.83); against GDP the effect was smaller (*w* = 0.42); and against global health-R&D expenditure HICs were approximately at expected frequency (observed/expected = 0.92). Normalized by population, trial-production rates spanned three orders of magnitude (1.81 HIC / 0.17 UMIC / 0.021 LMIC / 0.001 LIC trials per million) — an 86-fold HIC-to-LMIC and ~1,800-fold HIC-to-LIC gap. No LMIC-only collaborative trials were identified across the 25-year period.

**Conclusions.** Over 25 years, robotic surgery clinical trials have undergone substantial geographic redistribution, but not globalization. The apparent diversification masks near-complete absence from Africa and zero contribution from low-income countries. The magnitude of income-tier inequity is consistent with that seen in global health research more broadly, suggesting that the disparities observed are structural to medical-research infrastructure rather than specific to robotic surgery — and that addressing them requires upstream investment in research capacity and in surgical care delivery itself, in the context of the ongoing global-surgery gap described by the Lancet Commission on Global Surgery.

---

## INTRODUCTION

The landscape of surgical innovation has been fundamentally transformed by robotic-assisted surgical systems. Following the U.S. Food and Drug Administration (FDA) clearance of the da Vinci Surgical System in 2000, robotic-assisted approaches have been evaluated across specialties in large randomized controlled trials, including colorectal resection (ROLARR),¹ transthoracic esophagectomy (ROBOT),² and radical cystectomy (RAZOR).³ The market has diversified in recent years with the introduction of the Hugo system from Medtronic (Conformité Européenne [CE] Mark 2021; FDA clearance 2025) and the Versius system from CMR Surgical (CE Mark 2019; FDA De Novo authorization 2024),⁴ and with the emergence of platforms developed in Asia, such as the SSI Mantra system, for which a dual-console telesurgical configuration has been evaluated in animal-model and early clinical validation work in India.⁵

The clinical-trial literature is the primary mechanism through which these technologies are evaluated and translated into practice. Where that evidence is generated shapes which patient populations, healthcare systems, and resource contexts are represented in the cumulative evidence base.⁶,⁷ Bibliometric analyses of oncology trials have shown that the distribution of participating countries does not track research or disease-burden capacity — for example, a study of oncology randomized trials conducted by high-income-country (HIC) sponsors between 2014 and 2017 found that upper-middle-income and lower-middle-income countries were included only selectively, with participation patterns unrelated to national cancer research output,⁶ and a contemporaneous global analysis identified "little research conducted in, and relevant to," the problems of low- and middle-income countries (LMICs).⁷ Comparable disparities have been documented in gynecologic oncology,⁸ but the specific trajectory of robotic surgery research — a resource-intensive technology with potentially different global-diffusion dynamics — has not been quantitatively characterized over the full 25-year period of commercial availability.

This study examines the full trajectory of published robotic surgery clinical trials from 2001 through 2025. We characterize temporal growth, geographic concentration, international collaboration, regional composition, and income-tier distribution. We apply the World Bank's year-specific income classification (rather than a fixed contemporary classification) to avoid anachronism in the treatment of countries whose classifications have changed over the study period. We benchmark observed income-tier inequity against population, GDP, and global health-R&D distributions. Finally, we decompose non-HIC participation to determine whether the observed temporal trends reflect broad-based redistribution across countries or concentration within a small number of contributors.

---

## METHODS

### Study Design and Data Source

We conducted a bibliometric analysis of robotic surgery clinical trials indexed in the U.S. National Library of Medicine's PubMed/MEDLINE database between January 1, 2001 and August 8, 2025. The starting date corresponds to the first full calendar year following FDA clearance of the da Vinci Surgical System in 2000. Source data were drawn from the 2025 PubMed annual baseline (release files 0001–1274) supplemented with daily update files through the August 8 cutoff. No trial registry or other secondary source was used; all inclusion, country attribution, and date information derives from MEDLINE records.

### Inclusion Criteria

A PubmedArticle record was retained in the analytic cohort if its PublicationTypeList element contained either the term "Randomized Controlled Trial" or any PublicationType entry containing the substring "Clinical Trial." This includes "Clinical Trial," "Clinical Trial, Phase I" through "Phase IV," and "Pragmatic Clinical Trial." Records tagged exclusively as Comparative Study, Systematic Review, Meta-Analysis, Multicenter Study, or Observational Study — without an accompanying clinical-trial tag — were excluded. Robotic surgery relevance was established by the prior upstream filter of the MEDLINE corpus using the Medical Subject Heading "Robotic Surgical Procedures" combined with free-text matches for "robotic" and "robot-assisted." A record-flow diagram documenting records screened, filtered, and retained at each stage is provided as Supplementary Figure S1.

### Country Attribution

For each retained record, we extracted all AffiliationInfo/Affiliation strings attached to individual-author and collective-author elements. Free-text affiliation strings were lower-cased and matched, by case-insensitive substring search, against a curated dictionary of country-name variants covering 47 canonical economies, including common name variants (e.g., "england" → United Kingdom; "pr china" → China; "republic of korea" → South Korea; "czechia" → Czech Republic). The dictionary was expanded beyond initial major producers to ensure coverage of additional high-income, upper-middle-income, lower-middle-income, and low-income economies with non-trivial robotic-surgery-trial activity. When no country could be identified from any author affiliation, we used the MedlineJournalInfo/Country field (with matching country-name normalization) as a secondary attribution; 207 of 2,232 trials (9.3%) used this fallback. Records with no identifiable country were excluded from analysis. Each unique country appearing in a trial's affiliation set was counted once per trial. Countries were mapped to geographic regions (North America, Europe, Asia, Oceania, Latin America, Middle East, Africa) using the standard UN geoscheme with manual adjustments appropriate to the analysis.

### Time-Varying Income Classification

Each country-trial participation was assigned an income-tier classification corresponding to the publication year of the trial, using the World Bank's official Country Analytical History (OGHIST) record. This file provides per-country, per-calendar-year classification into high-income (HIC), upper-middle-income (UMIC), lower-middle-income (LMIC), or low-income (LIC) categories based on Atlas-method gross national income per capita. OGHIST covers calendar years 1987 through 2021; for publication years 2022 through 2025, we forward-filled using the current 2024–25 operational classification, with fallback to the 2021 OGHIST classification where the current classification was unavailable. This approach corrects an anachronism that would otherwise arise from applying a fixed contemporary classification: notably, China was classified LMIC until 2010 and UMIC thereafter; South Korea was UMIC until the late 1990s and HIC thereafter; Poland was UMIC until 2008 and HIC thereafter; Saudi Arabia was UMIC until 2003 and HIC thereafter. Two country-name transitions in the OGHIST source file required manual supplementation: (i) Turkey, for which the source contained only post-2022 "Türkiye" rows, was supplemented with 1987–2021 Atlas-method classifications (LMIC 1987–2003; UMIC 2004–2017; LMIC 2018; UMIC 2019–2021) drawn from prior World Bank analytical publications; and (ii) Czechia, for which a similar pre-rename gap was observed, was supplemented with published classifications (UMIC through 2006; HIC from 2007 onward). The full historical lookup used is provided as Supplementary Table S1, and a sensitivity comparison between the time-varying approach and a fixed 2024–25 classification is presented as Supplementary Table S2. Under this approach, 100% of country-trial participations received an assignable income-tier classification.

### Outcome Measures

The primary outcomes were annual trial volume; annual geographic concentration of country-trial participations as measured by the Herfindahl-Hirschman Index; annual proportion of trials with affiliations from two or more distinct countries; annual regional composition of participations; and annual income-tier distribution of participations. The Herfindahl-Hirschman Index was computed per year as the sum of squared country shares multiplied by 10,000. Intuitively, the index summarizes how unevenly trial production is distributed across producing countries: a value of 10,000 corresponds to a single country producing all trials, whereas a value of 1,000 corresponds approximately to ten countries each producing an equal 10% share. We applied the categorical thresholds established in the U.S. Department of Justice and Federal Trade Commission Horizontal Merger Guidelines, where values below 1,500 indicate an unconcentrated distribution, 1,500 to 2,500 indicate moderate concentration, and values above 2,500 indicate high concentration. These thresholds were originally derived for antitrust assessment of market concentration but have been applied in prior bibliometric work to quantify producer-base concentration in research output, and we adopt the same categorical interpretation here as a relative reference rather than a regulatory benchmark. Multi-country collaboration was characterized both by the annual proportion of trials involving two or more countries and by the mean number of distinct country affiliations per trial. For multi-country trials, we additionally characterized the income-tier composition of the collaborating country set (HIC-only, LMIC-only, or cross-income HIC–LMIC).

### Statistical Analysis

Annual trial volume was modeled as a function of calendar year using ordinary least-squares linear regression; the coefficient of determination R² and two-tailed significance of the year coefficient are reported. Compound annual growth rate was computed from the five-year mean trial counts at the beginning and end of the study window, as $(\bar{n}_{2021\text{–}25}/\bar{n}_{2001\text{–}05})^{1/20} - 1$. Temporal monotonic trends in the Herfindahl-Hirschman Index, multi-country share, mean country count per trial, regional shares, and income-tier shares were evaluated using the Spearman rank correlation coefficient. Because the analysis involves a family of fourteen related temporal-trend tests, we applied the Benjamini-Hochberg false-discovery-rate correction across this family and report both raw and adjusted p-values; results are reported as statistically significant if the Benjamini-Hochberg-adjusted p-value was less than 0.05.

To evaluate income-tier inequity, we applied Pearson χ² goodness-of-fit tests comparing observed country-trial participations against three null distributions. The first null assumes that trial participations are distributed in proportion to world population by income tier using the World Bank's 2024 population estimates (HIC 15.6%, UMIC 31.8%, LMIC 42.9%, LIC 9.8%). The second null assumes distribution in proportion to gross domestic product by income tier using World Bank 2024 GDP estimates. The third null assumes distribution in proportion to global health research-and-development expenditure by income tier, using published estimates that HICs account for approximately 89%, UMICs 10%, LMICs 1%, and LICs 0.1% of global health-R&D spending. Effect size was reported as Cohen's *w*, calculated as $w = \sqrt{\chi^2/N}$, where conventional thresholds of 0.1, 0.3, and 0.5 correspond to small, medium, and large effects. For each null, observed-to-expected ratios are reported per tier.

Two-tailed α was set at 0.05. All analyses were conducted in Python 3.13 using pandas (v2.2), NumPy (v1.26), and SciPy (v1.13). Geographic visualizations used Cartopy with Natural Earth administrative boundaries at 1:110m resolution.

### Data and Code Availability

All data-processing scripts, intermediate data files, and figure-generation code are publicly available at [repository DOI to be added upon acceptance] under the MIT License. The pipeline is fully reproducible from the PubMed/MEDLINE baseline release. The historical World Bank classification lookup used is archived with the code.

### Ethical Considerations

The analysis used exclusively publicly available bibliometric metadata and involved no human subjects. Institutional review board review was not required.

---

## RESULTS

### Cohort

We identified 2,232 robotic surgery clinical trials published between January 1, 2001 and August 8, 2025, contributed by authors from 47 distinct countries. Country attribution from the unified affiliation-plus-journal-country extraction yielded 2,777 country-trial participations, of which 2,777 (100%) were assigned an income tier under the time-varying World Bank classification. Summary cohort characteristics are shown in Table 1.

### Growth in Trial Volume

Annual publication volume increased from a mean of 27.0 trials per year during 2001–2005 to 193.6 trials per year during 2021–2025, a 7.17-fold rise (Figure 1). The compound annual growth rate across this 20-year interval was 10.35% per year. Linear regression of annual trial count on calendar year yielded a slope of 8.17 trials per year (R² = 0.798; *p* = 1.9 × 10⁻⁹), and the Spearman rank correlation confirmed a near-perfect monotonic increase (*ρ* = 0.983; *q* < 0.001 after Benjamini-Hochberg correction across the family of fourteen temporal-trend tests).

### Declining Geographic Concentration and Rising International Collaboration

Mean annual Herfindahl-Hirschman Index of country-trial participations declined from 2,012 during 2001–2005 — classified as moderately concentrated under U.S. Department of Justice thresholds — to 982 during 2021–2025, crossing into the unconcentrated range (Figure 2A). The declining trend was statistically robust (Spearman *ρ* = −0.793; *q* < 0.001). The number of distinct countries contributing trials in a single calendar year rose from a mean of 10.4 during 2001–2005 to 25.6 during 2021–2025, peaking at 27 in 2023 (*ρ* = 0.880; *q* < 0.001). Over the same interval, the proportion of trials with affiliations from two or more countries rose from 3.1% to 21.2% (Figure 2B; *ρ* = 0.783; *q* < 0.001), and the mean number of distinct country affiliations per trial rose from 1.03 to 1.28 (*ρ* = 0.772; *q* < 0.001). These four metrics together indicate substantial apparent diversification in the producer base of robotic surgery trials.

### Regional Redistribution and Shifting Country Leadership

Regional composition of country-trial participations shifted markedly across the 25-year period (Figure 3A). The Asian share of participations rose from 15.2% during 2001–2005 to 39.5% during 2021–2025, nearly tripling (*ρ* = 0.816; *q* < 0.001). The European share rose from 35.3% to 53.4% (*ρ* = 0.748; *q* < 0.001). The North American share declined from 39.3% to 25.0% (*ρ* = −0.714; *q* < 0.001) — the only major region to lose share. The Latin American share rose modestly from 0.0% to 2.5% (*ρ* = 0.739; *q* < 0.001). The Middle Eastern share showed no significant change (4.6% to 4.0%; *ρ* = 0.050; *q* = 0.812). The African share remained below 1% throughout the study period and showed no significant temporal trend (0.7% to 0.6%; *ρ* = 0.314; *q* = 0.147).

The United States led all country-level contributors across the 25-year period, with 612 country-trial participations (22.0% of the 2,777 total), followed by China (318; 11.5%), the United Kingdom (292; 10.5%), South Korea (188; 6.8%), Germany (178; 6.4%), Italy (161; 5.8%), Japan (119; 4.3%), France (99; 3.6%), the Netherlands (84; 3.0%), and Canada (83; 3.0%). These top ten countries accounted for 76.8% of all country-trial participations, and the top three alone accounted for 44.0%. In the most recent five years, China surpassed the United States as the leading single contributor, with 238 participations compared with 198 (Figure 3B; Table 1). The United Kingdom (143), Germany (85), Italy (71), and South Korea (63) completed the top six in the 2021–2025 window.

### Persistent Income-Tier Inequity

Of the 2,777 country-trial participations with assigned income tier, 2,268 (81.7%) originated in high-income countries, 435 (15.7%) in upper-middle-income countries, 73 (2.6%) in lower-middle-income countries, and 1 (0.04%) in a low-income country (Pakistan in 2004, when classified LIC under the Atlas-method GNI per capita threshold). When normalized by 2024 population estimates, trial-production rates spanned three orders of magnitude: 1.81 trials per million population in HICs, 0.17 in UMICs, 0.021 in LMICs, and 0.001 in LICs — an 86-fold disparity between HIC and LMIC production rates, and an approximately 1,800-fold disparity between HIC and LIC production rates (Figure 4B).

Income-tier shares shifted over time (Figure 4A), with HIC share declining from 87.0% during 2001–2005 to 75.1% during 2021–2025 (*ρ* = −0.475; *q* = 0.021) and UMIC share rising from 5.8% to 22.8% (*ρ* = 0.748; *q* < 0.001). LMIC share did not exhibit a significant temporal trend (6.5% → 2.1%; *ρ* = −0.111; *q* = 0.642), and LIC participation occurred in only a single year across the study window. The aggregate non-HIC share of country-trial participations rose from 13.0% to 24.9% over the study window; a decomposition of this trend by contributing country — including sensitivity analysis excluding the single largest non-HIC contributor — is presented in the Supplementary Material (Supplementary Figure S3). No trials involving authors exclusively from LMICs or LICs — that is, collaborative trials without any HIC participant — were identified across the 25-year period.

### Benchmarking Inequity Against Multiple Reference Distributions

The magnitude of income-tier inequity depends substantially on the reference distribution to which observed participations are compared. Table 2 (lower panel) presents χ² goodness-of-fit results against three alternative null distributions. Under a population-proportional null, the deviation was extreme (*χ*² = 9,328; df = 3; *p* < 0.001; Cohen's *w* = 1.83). HIC participations were 5.24 times their population-proportional expectation, UMIC participations were 0.49 times, LMIC participations 0.06 times, and LIC participations 0.004 times. Under a GDP-proportional null, effect magnitude was substantially smaller though still large (*χ*² = 478; *p* < 0.001; *w* = 0.42), with HIC at 1.32 times expected and LMIC at 0.33 times. Under a global health-R&D-proportional null — which itself encodes structural concentration of biomedical research in high-income settings — the observed distribution was closest to expectation (*χ*² = 199; *p* < 0.001; *w* = 0.27), with HIC participations at 0.92 times expected and UMIC participations at 1.57 times expected. A multi-panel equity summary displaying per-country contributions, time-varying income-tier shares, per-million production rates, and observed-to-expected ratios under each null is provided as Supplementary Figure S2.

---

## DISCUSSION

This bibliometric analysis of 2,232 robotic surgery clinical trials over 25 years reveals a field that has undergone substantial geographic redistribution without a corresponding expansion of the set of populations represented in its evidence base. Absolute trial volume has grown more than sevenfold, geographic concentration has declined across multiple metrics, and international collaboration has risen meaningfully. Yet when the data are examined by income tier — and particularly when income classifications are applied on a year-specific basis — the apparent diversification is substantially more limited than initial metrics suggest. More than four-fifths of country-trial participations over the 25-year period originated in high-income countries, only a single participation was recorded from a low-income country, and the rise in non-HIC participation is concentrated within a small number of upper-middle-income contributors rather than reflecting broad-based diversification (Supplementary Figure S3).

**Redistribution, not globalization.** The pattern observed here is best characterized as redistribution within a broadening HIC and UMIC producer base rather than globalization of the research enterprise. The word "globalization" implies extension to previously excluded regions. The data show expansion into a handful of high-capacity UMICs while Africa and the low-income world remain effectively absent from the producer base of robotic surgery research. Latin America's modest emergence (0.0% to 2.5% of participations) represents real progress from a very low base but does not change the fundamental pattern. A decomposition of non-HIC participation by contributing country (Supplementary Figure S3) reveals that the aggregate rise in non-HIC share (13.0% during 2001–2005 to 24.9% during 2021–2025) is attributable entirely to China, whose share rose from 3.6% to 18.7% over the same interval. Non-HIC participation *excluding* China declined over the study period, from 9.4% during 2001–2005 to 6.2% during 2021–2025, and within-non-HIC concentration remained extreme throughout (China accounted for 77.8% of non-HIC participations in 2021–2025). The headline metric of "broader geographic participation" therefore reflects the emergence of a single upper-middle-income research producer rather than a genuine diversification of contributors. This distinction matters for how the findings are interpreted and acted upon.

**Research equity and technology access are distinct problems.** Robotic surgical platforms remain expensive, with capital costs in the range of approximately US$1.5–2.5 million per unit plus substantial recurring disposable costs, and penetration in many LMICs is limited or nonexistent. The absence of robotic surgery trials in the low-income world is therefore not only — and perhaps not primarily — a research-system failure. It reflects the underlying absence of the technology itself in those settings. This distinction has direct implications for policy. Research-capacity interventions (investigator training, regulatory harmonization, funding mechanisms) will not address the substantive inequity if the technology being studied is unavailable; conversely, technology-access interventions (platform cost reduction, donation or subsidy programs, indigenous platform development) will not automatically generate a robust research footprint without parallel investment in research infrastructure. The two interventions are complementary but not substitutable.

**Robotic surgery research is not uniquely inequitable.** The multi-null χ² analysis places the observed inequity in comparative context. Against a population-proportional reference, the inequity is extreme (*w* = 1.83). Against a GDP-proportional reference, it is smaller but still large (*w* = 0.42). Against global health R&D expenditure, HIC participations are approximately at expected frequency (observed/expected = 0.92), with UMICs somewhat over-represented and low-income countries near-entirely absent. This comparison suggests that robotic surgery research inequity substantially inherits the distribution of global biomedical research capacity more broadly, rather than representing a disparity specific to robotic surgery. The practical implication is that remedies confined to this field — convening panels, targeted consortia — are unlikely to move the distribution materially without upstream investment in research infrastructure across the broader medical-research ecosystem.

**The global-surgery context.** The Lancet Commission on Global Surgery documented in 2015 that approximately five billion people lack access to safe, affordable surgical and anaesthesia care when needed,⁹ a finding subsequently reinforced by modelling work showing that more than two billion people cannot receive surgical care on the basis of operating-theatre density alone.¹⁰ A decade later, the 2025 *Lancet* follow-up on surgical health policy reported that progress toward the Commission's 2030 targets has been "too slow and too patchy," with an unmet surgical need that continues to concentrate in low- and lower-middle-income countries.¹¹ In that context, the allocation of incremental surgical-research investment between cutting-edge robotic technologies and fundamental surgical capacity is a matter of active debate. The findings presented here do not resolve that debate, but they sharpen it: the accelerating investment in robotic surgery research documented over the 2001–2025 window has not, in practice, reached the populations with the largest unmet surgical need. Whether robotic surgery should be a priority for research capacity-building in low-income settings — given the platform costs, maintenance requirements, and opportunity costs — is a question the present data inform but do not settle. What the data make clear is that existing patterns of international collaboration have not meaningfully expanded the set of low-income populations contributing to or represented in the robotic surgery evidence base, and that absent substantive change to the structural drivers of biomedical research capacity¹² — which itself remains heavily concentrated in HIC settings — this pattern is unlikely to shift through incremental collaboration alone.

---

## LIMITATIONS

Several methodological limitations warrant consideration. First, our reliance on author affiliation as a proxy for trial conduct may not accurately capture the location of patient enrollment, data collection, or principal investigator leadership. A trial physically conducted at one site may list co-authors with affiliations in other countries, inflating apparent multi-country participation. A sensitivity analysis restricted to first- or corresponding-author country would partially address this but is unlikely to change the core findings materially, given that the overall patterns of HIC dominance, the concentration of non-HIC contributions within a small number of UMICs, and the absence of low-income-country participation are evident at both any-affiliation and primary-affiliation levels in the underlying data. A formal sensitivity analysis using primary affiliation is provided in Supplementary Table S3.

Second, country attribution via substring matching against a curated dictionary excludes trials from countries not represented in the dictionary. Countries such as Mexico, Argentina, Colombia, Chile, Morocco, Ghana, Pakistan, Bangladesh, Vietnam, Thailand, Indonesia, and the Philippines — each of which has some clinical-trial activity — are not explicitly captured unless recovered through the MedlineJournalInfo/Country fallback. This limitation likely biases our LMIC counts downward and may somewhat understate the absolute number of LMIC participations, though it is unlikely to alter the qualitative conclusion of HIC and China dominance.

Third, publication year is an imperfect proxy for trial-conduct year. Publication lag, typically one to five years, introduces noise into the temporal trends and may obscure short-term dynamics. Linkage to trial-registration dates via ClinicalTrials.gov would provide greater precision but would also introduce incomplete-registration bias, as a non-trivial proportion of clinical-trial publications are not linked to registry records, particularly for studies conducted outside the United States and Europe.

Fourth, the inclusion filter — PublicationType containing "Clinical Trial" or "Randomized Controlled Trial" — aggregates studies with heterogeneous design (phase I feasibility work, pilot studies, pragmatic trials, definitive RCTs) and specialty focus (urology, gynecology, colorectal, thoracic, cardiac, otolaryngology). Geographic and income-tier patterns may differ across these strata, and the present analysis does not stratify by trial type or specialty. This is a direction for future work and a meaningful limitation of the present findings. Where specialty and trial-type information are reliably available in MEDLINE metadata, systematic stratification could identify whether the observed disparities are uniform or concentrated in specific subfields.

Fifth, the World Bank's analytical history record covers calendar years 1987 through 2021; for 2022–2025 we relied on forward-filled current classifications. This introduces a modest risk of misclassification for countries whose income status may have changed in those recent years, although the transitions are small in number and unlikely to affect the dominant patterns reported here.

Finally, the analysis does not capture the qualitative dimensions of research participation — whether LMIC authors on collaborative trials hold substantive design, data-access, or publication responsibilities, or whether participation is nominal. Qualitative or mixed-methods investigation of these dimensions is a natural extension of the present quantitative work.

---

## CONCLUSIONS

Over a 25-year period, robotic surgery clinical trials have undergone substantial geographic redistribution but have not globalized. Trial volume has grown more than sevenfold; concentration has declined; regional participation has shifted toward Europe and Asia; and international collaboration has risen. Yet high-income countries continue to produce more than four-fifths of country-trial participations, and low-income countries remain entirely absent from the producer base. The magnitude of the observed disparity is comparable to that seen in global health research more broadly, suggesting that remedies specific to robotic surgery are unlikely to materially change the distribution without upstream investment in global research infrastructure and, more fundamentally, in equitable access to safe surgical care worldwide.

---

## ACKNOWLEDGMENTS

[To be added]

## FUNDING

This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

## CONFLICTS OF INTEREST

The authors declare no conflicts of interest.

---

## TABLES

### Table 1. Cohort characteristics and leading country contributors to robotic surgery clinical trials, 2001–2025

**Panel A — Cohort summary**

| Characteristic | Value |
|---|---|
| Total trials | 2,232 |
| Country-trial participations (affiliation + journal-country fallback) | 2,777 |
| Participations with assigned income tier (time-varying WB) | 2,777 (100%) |
| Distinct contributing countries | 47 |
| Publication window | January 1, 2001 – August 8, 2025 |
| Data source | PubMed/MEDLINE 2025 annual baseline + daily updates |
| Mean trials/year, 2001–2005 | 27.0 |
| Mean trials/year, 2021–2025 | 193.6 |
| Fold increase, early vs. recent 5-year window | 7.17× |
| Compound annual growth rate (period averages) | 10.35% |

**Panel B — Top 10 country contributors, overall and 2021–2025**

| Rank | Country | Overall (n) | 2021–2025 (n) | Income tier (current) |
|---|---|---:|---:|:---|
| 1 | United States | 612 | 198 | HIC |
| 2 | China | 318 | 238 | UMIC |
| 3 | United Kingdom | 292 | 143 | HIC |
| 4 | South Korea | 188 | 63 | HIC |
| 5 | Germany | 178 | 85 | HIC |
| 6 | Italy | 161 | 71 | HIC |
| 7 | Japan | 119 | 56 | HIC |
| 8 | France | 99 | 46 | HIC |
| 9 | Netherlands | 84 | 42 | HIC |
| 10 | Canada | 83 | 34 | HIC |

*Note.* In the most recent five years, China surpassed the United States as the leading single contributor. The ten countries shown account for 76.8% of country-trial participations across the full 25-year period. A full-ranking supplementary table is provided as Table S3.

---

### Table 2. Statistical tests

**Panel A — Temporal trend tests (Spearman rank correlation, Benjamini-Hochberg adjusted)**

| Outcome | *ρ* | *p* (raw) | *q* (BH) | Significant at *q* < 0.05 |
|---|---:|---:|---:|:---:|
| Annual trial volume | 0.983 | 2.1 × 10⁻¹⁸ | 3.0 × 10⁻¹⁷ | Yes |
| Distinct countries per year | 0.880 | 6.7 × 10⁻⁹ | 4.7 × 10⁻⁸ | Yes |
| Asia regional share | 0.816 | 6.8 × 10⁻⁷ | 3.2 × 10⁻⁶ | Yes |
| Multi-country trial share | 0.783 | 3.6 × 10⁻⁶ | 1.0 × 10⁻⁵ | Yes |
| Mean countries per trial | 0.772 | 6.1 × 10⁻⁶ | 1.4 × 10⁻⁵ | Yes |
| Europe regional share | 0.748 | 1.7 × 10⁻⁵ | 3.0 × 10⁻⁵ | Yes |
| UMIC income-tier share | 0.748 | 1.7 × 10⁻⁵ | 3.0 × 10⁻⁵ | Yes |
| Latin America regional share | 0.739 | 2.4 × 10⁻⁵ | 3.8 × 10⁻⁵ | Yes |
| Herfindahl-Hirschman Index | −0.793 | 2.2 × 10⁻⁶ | 7.9 × 10⁻⁶ | Yes |
| North America regional share | −0.714 | 6.1 × 10⁻⁵ | 8.6 × 10⁻⁵ | Yes |
| HIC income-tier share | −0.475 | 0.016 | 0.021 | Yes |
| Africa regional share | 0.314 | 0.126 | 0.147 | No |
| LMIC income-tier share | −0.111 | 0.596 | 0.642 | No |
| Middle East regional share | 0.050 | 0.812 | 0.812 | No |

**Panel B — Goodness-of-fit of income-tier distribution against three null distributions**

| Null distribution | *χ²* | df | *p* | Cohen's *w* | O/E HIC | O/E UMIC | O/E LMIC | O/E LIC |
|---|---:|:---:|---:|---:|---:|---:|---:|---:|
| Population-proportional (WB 2024) | 9,328 | 3 | <10⁻³⁰⁰ | 1.83 | 5.24 | 0.49 | 0.061 | 0.004 |
| GDP-proportional (WB 2024) | 478 | 3 | 2.9 × 10⁻¹⁰³ | 0.42 | 1.32 | 0.53 | 0.330 | 0.072 |
| Global health-R&D-proportional (approx.) | 199 | 3 | 6.3 × 10⁻⁴³ | 0.27 | 0.92 | 1.57 | 2.92 | 0.36 |

*Note.* *O/E* denotes observed-to-expected ratio; *N* = 2,777 country-trial participations. Under the health-R&D null, HICs are approximately at expected frequency (O/E ≈ 0.92), suggesting that the observed HIC concentration in robotic surgery trials approximates the underlying distribution of global biomedical research activity. All three nulls reject equality with *p* far below 0.001, but Cohen's *w* varies from very large (*w* = 1.83) under the population null to medium (*w* = 0.27) under the health-R&D null, indicating substantial dependence of effect magnitude on the reference distribution chosen.

---

## FIGURE LEGENDS

**Figure 1. Annual volume of robotic surgery clinical trial publications, 2001–2025.** Bars show annual trial counts; dashed line shows fitted linear regression (slope = 8.17 trials/year; R² = 0.798; *p* = 1.9 × 10⁻⁹). Compound annual growth rate based on five-year mean counts at the start and end of the window was 10.35% per year. Spearman rank correlation of year and annual count was *ρ* = 0.983 (*q* < 0.001 after Benjamini-Hochberg correction). Annual volume rose from a mean of 27.0 trials/year during 2001–2005 to 193.6 trials/year during 2021–2025.

**Figure 2. Geographic concentration and international collaboration over time.** Panel A: Annual Herfindahl-Hirschman Index (HHI) of country-trial participations, 2001–2025. The HHI summarizes how unevenly trial production is distributed across countries (10,000 = single country produces all trials; ~1,000 = roughly ten countries with equal share). Dashed horizontal reference lines mark the U.S. Department of Justice and Federal Trade Commission Horizontal Merger Guideline thresholds for moderate concentration (1,500) and high concentration (2,500); these thresholds were originally derived for antitrust analysis and are applied here as relative benchmarks for research-producer concentration. HHI declined from a mean of 2,012 during 2001–2005 to 982 during 2021–2025 (Spearman *ρ* = −0.793; *q* < 0.001). Panel B: Annual proportion of trials with affiliations from two or more distinct countries. Multi-country share rose from a mean of 3.1% during 2001–2005 to 21.2% during 2021–2025 (*ρ* = 0.783; *q* < 0.001).

**Figure 3. Regional and country-level composition of trial participations.** Panel A: Stacked proportional area plot of annual regional shares of country-trial participations, 2001–2025. Asia (dark shade) rose from 15.2% to 39.5%; Europe (medium shade) rose from 35.3% to 53.4%; North America (light shade) declined from 39.3% to 25.0%; Latin America, Africa, Middle East, and Oceania shares are shown as narrow layers. Panel B: Cumulative-period world bubble map showing country-trial participations across the full 25-year window. Bubble area is proportional to trial count; shading distinguishes high-income from lower-income contributors. Substantial activity is visible in North America, Europe, and East Asia; Africa and most of Latin America are effectively absent.

**Figure 4. Income-tier distribution and per-capita production by income tier.** Panel A: Stacked proportional plot of annual income-tier shares of country-trial participations, using time-varying World Bank classification, 2001–2025. HIC share declined from 87.0% during 2001–2005 to 75.1% during 2021–2025; UMIC share rose from 5.8% to 22.8%; LMIC share showed no significant temporal trend (6.5% to 2.1%; *q* = 0.642); LIC participation occurred in only a single year. Panel B: Cumulative trial production per million population by income tier, 2001–2025, plotted on a log scale. HICs produced 1.81 trials per million population; UMICs 0.17; LMICs 0.021; LICs 0.001 (a single trial from Pakistan in 2004) — an 86-fold gap between HIC and LMIC production rates and an approximately 1,800-fold gap between HIC and LIC rates.

---

## SUPPLEMENTARY MATERIALS

**Supplementary Table S1.** Full historical World Bank income classification lookup used in time-varying attribution, by country and calendar year, 1987–2025 (OGHIST 1987–2021 + forward-fill 2022–2025).

**Supplementary Table S2.** Sensitivity comparison of income-tier shares under static 2024–25 classification versus time-varying classification, with attention to countries undergoing classification transitions during the study window (notably China, South Korea, Poland, Saudi Arabia, Brazil, India).

**Supplementary Table S3.** Per-country raw counts of country-trial participations by year, 2001–2025, and sensitivity analysis using primary (first or corresponding) author affiliation only.

**Supplementary Figure S1.** Record-flow diagram: MEDLINE records screened, robotic surgery filter applied, clinical-trial-type filter applied, final analytic cohort, and attrition at each step including records without identifiable country attribution.

**Supplementary Figure S2.** Equity dashboard (multi-panel): per-country trial counts for the top 15 contributors over time; time-varying income-tier distribution; per-million-population production rate by income tier; observed-to-expected ratios under each of the three null distributions.

**Supplementary Figure S3.** Decomposition of non-HIC country-trial participations, 2001–2025. Panel A: Annual non-HIC share of participations, stratified into contribution from the single largest non-HIC contributor (China) versus all other non-HIC countries combined. The aggregate non-HIC share rose from 13.0% during 2001–2005 to 24.9% during 2021–2025, driven entirely by China's rise from 3.6% to 18.7%; the non-HIC share excluding China *declined* over the same interval from 9.4% to 6.2%. Panel B: Year-by-year Herfindahl-Hirschman Index computed across non-HIC countries alone, indicating that concentration within the non-HIC producer subset remained high throughout the study period; early-year values with small denominators (n < 5 non-HIC participations) are faded to reflect estimation instability.

---

## REFERENCES

1. Jayne D, Pigazzi A, Marshall H, et al. Effect of Robotic-Assisted vs Conventional Laparoscopic Surgery on Risk of Conversion to Open Laparotomy Among Patients Undergoing Resection for Rectal Cancer: The ROLARR Randomized Clinical Trial. *JAMA*. 2017;318(16):1569-1580. doi:10.1001/jama.2017.7219

2. van der Sluis PC, van der Horst S, May AM, et al. Robot-assisted Minimally Invasive Thoracolaparoscopic Esophagectomy Versus Open Transthoracic Esophagectomy for Resectable Esophageal Cancer: A Randomized Controlled Trial. *Ann Surg*. 2019;269(4):621-630. doi:10.1097/SLA.0000000000003031

3. Parekh DJ, Reis IM, Castle EP, et al. Robot-assisted radical cystectomy versus open radical cystectomy in patients with bladder cancer (RAZOR): an open-label, randomised, phase 3, non-inferiority trial. *Lancet*. 2018;391(10139):2525-2536. doi:10.1016/S0140-6736(18)30996-6

4. Ngu JC, Lin CC, Sia CJ, Teo NZ. A narrative review of the Medtronic Hugo RAS and technical comparison with the Intuitive da Vinci robotic surgical system. *J Robot Surg*. 2024;18(1):99. doi:10.1007/s11701-024-01838-5

5. Srivastava SP, Srivastava VP, Singh A, et al. Evaluating the efficacy of telesurgery with dual console SSI Mantra Surgical Robotic System: experiment on animal model and clinical trials. *J Robot Surg*. 2024;18(1):391. doi:10.1007/s11701-024-02148-6

6. Rubagumya F, Hopman WM, Gyawali B, et al. Participation of Lower and Upper Middle-Income Countries in Clinical Trials Led by High-Income Countries. *JAMA Netw Open*. 2022;5(8):e2227252. doi:10.1001/jamanetworkopen.2022.27252

7. Pramesh CS, Badwe RA, Bhoo-Pathy N, et al. Priorities for cancer research in low- and middle-income countries: a global perspective. *Nat Med*. 2022;28(4):649-657. doi:10.1038/s41591-022-01738-x

8. Grover S, Xu M, Jhingran A, et al. Clinical trials in low and middle-income countries — Successes and challenges. *Gynecol Oncol Rep*. 2016;19:5-9. doi:10.1016/j.gore.2016.11.007

9. Meara JG, Leather AJM, Hagander L, et al. Global Surgery 2030: evidence and solutions for achieving health, welfare, and economic development. *Lancet*. 2015;386(9993):569-624. doi:10.1016/S0140-6736(15)60160-X

10. Alkire BC, Raykar NP, Shrime MG, et al. Global access to surgical care: a modelling study. *Lancet Glob Health*. 2015;3(6):e316-323. doi:10.1016/S2214-109X(15)70115-4

11. Nepogodiev D, Picciochi M, Ademuyiwa A, et al. Surgical health policy 2025-35: strengthening essential services for tomorrow's needs. *Lancet*. 2025;406(10505):860-880. doi:10.1016/S0140-6736(25)00985-7

12. Viergever RF, Hendriks TCC. The 10 largest public and philanthropic funders of health research in the world: what they fund and how they distribute their funds. *Health Res Policy Syst*. 2016;14:12. doi:10.1186/s12961-015-0074-z

---

### Reference verification note

Each reference above has been verified against PubMed records (DOI and citation confirmed as of April 2026). Regulatory information for the Hugo RAS (FDA clearance, December 2025) and CMR Versius (FDA De Novo, October 2024) platforms has been described in the peer-reviewed literature and in FDA 510(k)/De Novo database entries; authors are advised to cross-check FDA decision dates against the FDA 510(k) database (https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm) at time of submission, as regulatory events can be updated. No press releases, preprints, or gray-literature sources are included in the primary reference list.
