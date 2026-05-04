#!/usr/bin/env python3
"""
Generate supplementary materials for the manuscript.

Outputs (to output_preview/supplementary/):
  - Supplementary_Figure_S1.png/.pdf  PRISMA-style record-flow diagram
  - Supplementary_Figure_S2.png/.pdf  Equity dashboard (4 panels)
  - Supplementary_Figure_S3.png/.pdf  Non-HIC decomposition (China analysis)
  - Supplementary_Table_S1.csv         Historical WB classification lookup
  - Supplementary_Table_S2.csv         Static vs time-varying comparison
  - Supplementary_Table_S3.csv         Per-country counts by year
"""
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.patches import FancyBboxPatch
from matplotlib.gridspec import GridSpec

warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
OUT = BASE_DIR / 'output' / 'supplementary'
OUT.mkdir(parents=True, exist_ok=True)

# Style — matches main figures
INK = '#1A1A1A'
INK_SOFT = '#4A4A4A'
ACCENT = '#B4412E'
ACCENT_SOFT = '#D99889'
HIC_COLOR = '#2E4057'
UMIC_COLOR = '#6C8EBF'
LMIC_COLOR = '#9DB4CE'
LIC_COLOR = '#D1D9E0'
GRAY_1 = '#3B3B3B'
GRAY_2 = '#7A7A7A'
GRAY_3 = '#BFBFBF'
GRAY_LIGHT = '#E8E8E8'

plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'savefig.facecolor': 'white',
    'savefig.bbox': 'tight',
    'savefig.dpi': 600,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 9,
    'axes.titlesize': 10,
    'axes.labelsize': 9,
    'axes.edgecolor': INK_SOFT,
    'axes.linewidth': 0.8,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.frameon': False,
    'legend.fontsize': 8,
})


def panel_label(ax, letter, x=-0.14, y=1.06):
    ax.text(x, y, letter, transform=ax.transAxes,
            fontsize=11, fontweight='bold', ha='left', va='top', color=INK)


def save(fig, stem):
    fig.savefig(OUT / f'{stem}.png', dpi=600)
    fig.savefig(OUT / f'{stem}.pdf')
    plt.close(fig)
    print(f'  wrote {stem}.png and .pdf')


# ============================================================================
# SUPPLEMENTARY FIGURE S1 — PRISMA-style record-flow diagram
# ============================================================================
def figure_s1():
    fig, ax = plt.subplots(figsize=(8.0, 9.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 13)
    ax.axis('off')

    def box(x, y, w, h, text, fc='white', ec=INK_SOFT, fontsize=8.5,
            fontweight='normal'):
        b = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                           boxstyle='round,pad=0.05',
                           linewidth=0.9, edgecolor=ec,
                           facecolor=fc, zorder=3)
        ax.add_patch(b)
        ax.text(x, y, text, ha='center', va='center',
                fontsize=fontsize, color=INK,
                fontweight=fontweight, zorder=4)

    def arrow(x1, y1, x2, y2):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->',
                                    color=INK_SOFT, lw=0.9),
                    zorder=2)

    def excl_box(x, y, w, h, text):
        box(x, y, w, h, text, fc='#FAFAFA', ec=GRAY_3,
            fontsize=7.5)

    # --- Identification ---
    ax.text(3, 12.55, 'Identification',
            ha='center', fontsize=9.5, fontweight='bold',
            color=INK)
    box(3, 11.75, 4.5, 0.85,
        'PubMed/MEDLINE 2025 annual baseline\n'
        '(release files 0001–1274) + daily updates\n'
        'through 8 August 2025',
        fontsize=8)
    box(3, 10.40, 4.5, 0.70,
        'Records identified via robotic surgery\n'
        'MeSH + free-text search',
        fontsize=8)
    arrow(3, 11.30, 3, 10.80)

    # --- Screening ---
    ax.text(3, 9.55, 'Screening',
            ha='center', fontsize=9.5, fontweight='bold',
            color=INK)
    box(3, 8.80, 4.5, 0.75,
        'Records assessed for inclusion\n'
        '(PublicationType filter applied)\n'
        'n = 2,361',
        fontsize=8)
    arrow(3, 10.02, 3, 9.22)

    excl_box(7.8, 8.80, 3.6, 0.65,
             'Excluded: publication year\n'
             'outside 2001–2025\n'
             'n = 124')
    arrow(5.27, 8.80, 5.95, 8.80)

    box(3, 7.45, 4.5, 0.70,
        'Records with publication year\n'
        '2001–2025\n'
        'n = 2,237',
        fontsize=8)
    arrow(3, 8.40, 3, 7.85)

    # --- Country attribution ---
    ax.text(3, 6.55, 'Country attribution',
            ha='center', fontsize=9.5, fontweight='bold',
            color=INK)
    box(3, 5.55, 4.5, 1.10,
        'Country identified from author affiliation\n'
        '(case-insensitive substring match against\n'
        'curated 47-country normalization dictionary)\n'
        'n = 2,025',
        fontsize=8)
    arrow(3, 7.10, 3, 6.15)

    # Right-hand branches for the 212 records without affiliation country
    excl_box(7.8, 5.55, 3.6, 1.10,
             'No affiliation-based country match\n'
             '(n = 212)\n'
             '  • Recovered via MedlineJournalInfo/\n'
             '    Country fallback: n = 207\n'
             '  • Excluded: no country identifiable\n'
             '    (n = 5)')
    arrow(5.27, 5.55, 5.95, 5.55)

    # Converge into cohort
    box(3, 3.95, 4.5, 0.75,
        'Trials with assignable country\n'
        '(2,025 from affiliation + 207 via fallback)\n'
        'n = 2,232',
        fontsize=8)
    arrow(3, 5.00, 3, 4.35)
    # Recovered arrow coming in from fallback box
    arrow(7.8, 4.95, 5.27, 3.95)

    # --- Included ---
    ax.text(3, 3.05, 'Included in analysis',
            ha='center', fontsize=9.5, fontweight='bold',
            color=INK)
    box(3, 2.05, 4.5, 1.00,
        'Final analytic cohort\n'
        '2,232 trials\n'
        '2,777 country-trial participations\n'
        '47 distinct contributing countries',
        fc='#F5F0EC', ec=ACCENT, fontsize=8.5,
        fontweight='bold')
    arrow(3, 3.55, 3, 2.60)

    excl_box(7.8, 2.05, 3.6, 1.00,
             'Income-tier classification:\n'
             '2,777 / 2,777 (100%) participations\n'
             'assigned an income tier under\n'
             'time-varying WB classification\n'
             '(OGHIST 1987–2021, forward-filled\n'
             'through 2025)')
    arrow(5.27, 2.05, 5.95, 2.05)

    save(fig, 'Supplementary_Figure_S1')


# ============================================================================
# SUPPLEMENTARY FIGURE S2 — Equity dashboard (4-panel)
# ============================================================================
def figure_s2():
    tv = pd.read_csv(DATA_DIR / 'income_shares_by_year_tv.csv')
    top = pd.read_csv(DATA_DIR / 'top_countries_overall.tsv', sep='\t')

    fig = plt.figure(figsize=(10, 8))
    gs = GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.32)

    # ---- A: Top 15 country contributors over time (heatmap-ish) ----
    ax = fig.add_subplot(gs[0, 0])
    detail = pd.read_csv(DATA_DIR / 'country_year_tier_detail.csv')
    top15 = top.head(15)['country'].tolist()
    pivot = detail[detail.country.isin(top15)].pivot_table(
        index='country', columns='year', values='count',
        aggfunc='sum', fill_value=0).reindex(top15)
    im = ax.imshow(pivot.values, aspect='auto', cmap='Blues',
                   interpolation='nearest')
    ax.set_yticks(range(len(top15)))
    ax.set_yticklabels(top15, fontsize=7.5)
    years = sorted(pivot.columns.tolist())
    tick_idx = [years.index(y) for y in [2001, 2005, 2010, 2015, 2020, 2025]
                if y in years]
    ax.set_xticks(tick_idx)
    ax.set_xticklabels([years[i] for i in tick_idx], fontsize=7.5)
    ax.set_xlabel('Year', fontsize=8)
    cbar = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label('Trials', fontsize=7.5)
    cbar.ax.tick_params(labelsize=7)
    panel_label(ax, 'A')

    # ---- B: Time-varying income-tier shares (line) ----
    ax = fig.add_subplot(gs[0, 1])
    ax.plot(tv.year, tv.high_income_pct, color=HIC_COLOR,
            linewidth=1.4, marker='o', markersize=3, label='HIC')
    ax.plot(tv.year, tv.upper_middle_pct, color=UMIC_COLOR,
            linewidth=1.4, marker='s', markersize=3, label='UMIC')
    ax.plot(tv.year, tv.lower_middle_pct, color=LMIC_COLOR,
            linewidth=1.4, marker='^', markersize=3, label='LMIC')
    ax.plot(tv.year, tv.low_income_pct, color=LIC_COLOR,
            linewidth=1.4, marker='v', markersize=3, label='LIC')
    ax.set_xlim(2001, 2025)
    ax.set_xticks([2001, 2005, 2010, 2015, 2020, 2025])
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.set_xlabel('Year')
    ax.set_ylabel('Share of income-classified participations')
    ax.legend(loc='center right', fontsize=7.5)
    ax.grid(axis='y', color=GRAY_LIGHT, linewidth=0.5)
    panel_label(ax, 'B')

    # ---- C: Trials per million population (log scale) ----
    ax = fig.add_subplot(gs[1, 0])
    counts = [tv['high_income'].sum(), tv['upper_middle'].sum(),
              tv['lower_middle'].sum(), tv['low_income'].sum()]
    pops = [1.25, 2.56, 3.44, 0.75]
    per_m = [c / (p * 1000) for c, p in zip(counts, pops)]
    labels = ['HIC', 'UMIC', 'LMIC', 'LIC']
    colors = [HIC_COLOR, UMIC_COLOR, LMIC_COLOR, LIC_COLOR]
    y_pos = np.arange(len(labels))[::-1]
    for yi, v, col in zip(y_pos, per_m, colors):
        if v > 0:
            ax.barh(yi, v, color=col, edgecolor=INK, linewidth=0.5)
        else:
            ax.barh(yi, 0.0011, color=col, edgecolor=INK_SOFT,
                    linewidth=0.5, alpha=0.5)
    ax.set_xscale('log')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_xlim(0.001, 5)
    ax.set_xlabel('Trials per million population')
    for yi, v, lbl in zip(y_pos, per_m, ['1.59', '0.15', '0.02', '0']):
        if v > 0:
            ax.text(v * 1.25, yi, lbl, va='center', fontsize=8)
        else:
            ax.text(0.0013, yi, '0', va='center', fontsize=8,
                    color=INK_SOFT, style='italic')
    ax.grid(axis='x', color=GRAY_LIGHT, linewidth=0.5, which='major')
    panel_label(ax, 'C')

    # ---- D: O/E ratios under three null distributions ----
    ax = fig.add_subplot(gs[1, 1])
    obs = np.array(counts)
    total = obs.sum()
    nulls = {
        'Population': np.array([0.156, 0.318, 0.429, 0.098]),
        'GDP': np.array([62.0, 30.0, 8.0, 0.5]),
        'Health R&D': np.array([0.89, 0.10, 0.009, 0.001]),
    }
    width = 0.25
    x = np.arange(4)
    for i, (label, shares) in enumerate(nulls.items()):
        exp = total * shares / shares.sum()
        oe = [o / e if e else 0 for o, e in zip(obs, exp)]
        offset = (i - 1) * width
        ax.bar(x + offset, oe, width, label=label,
               color=[GRAY_1, GRAY_2, GRAY_3][i],
               edgecolor=INK, linewidth=0.4)
        # Annotate LIC (index 3) explicitly since O/E=0 cannot
        # render on a log scale
        if oe[3] == 0:
            ax.text(3 + offset, 0.0065, '0',
                    ha='center', va='bottom', fontsize=6.5,
                    color=INK_SOFT, style='italic')
    ax.axhline(1.0, color=ACCENT, linewidth=0.8, linestyle='--',
               alpha=0.7)
    ax.text(3.4, 1.03, 'Expected = 1', fontsize=7,
            color=ACCENT, ha='right')
    ax.set_xticks(x)
    ax.set_xticklabels(['HIC', 'UMIC', 'LMIC', 'LIC'])
    ax.set_ylabel('Observed / Expected ratio')
    ax.set_yscale('log')
    ax.set_ylim(0.005, 10)
    ax.legend(title='Null distribution', loc='upper right',
              fontsize=7.5, title_fontsize=7.5)
    ax.grid(axis='y', color=GRAY_LIGHT, linewidth=0.5,
            which='major')
    panel_label(ax, 'D')

    save(fig, 'Supplementary_Figure_S2')


# ============================================================================
# SUPPLEMENTARY FIGURE S3 — Non-HIC decomposition (China analysis)
# ============================================================================
def figure_s3():
    decomp = pd.read_csv(DATA_DIR / 'non_hic_decomposition.csv')
    detail = pd.read_csv(DATA_DIR / 'country_year_tier_detail.csv')

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))

    # ---- A: Non-HIC decomposition stacked area ----
    ax = axes[0]
    years = decomp['year'].values
    china = decomp['china'].values / decomp['total'].values * 100
    other_nh = decomp['non_hic_ex_china'].values / decomp['total'].values * 100
    ax.fill_between(years, 0, china, color=ACCENT, alpha=0.85,
                    label='China')
    ax.fill_between(years, china, china + other_nh, color=GRAY_2,
                    alpha=0.85, label='Other non-HIC countries')
    ax.set_xlim(2001, 2025)
    ax.set_xticks([2001, 2005, 2010, 2015, 2020, 2025])
    ax.set_ylim(0, 35)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.set_xlabel('Year')
    ax.set_ylabel('Share of country-trial participations')
    ax.legend(loc='upper left', fontsize=8)
    panel_label(ax, 'A')

    # ---- B: Within-non-HIC HHI over time ----
    ax = axes[1]
    nh_detail = detail[detail.tier.isin(
        ['upper_middle', 'lower_middle', 'low_income'])]
    yearly_hhi = []
    china_share = []
    yearly_n = []
    yrs = sorted(nh_detail.year.unique())
    for y in yrs:
        sub = nh_detail[nh_detail.year == y]
        tot = sub['count'].sum()
        yearly_n.append(tot)
        if tot == 0:
            yearly_hhi.append(np.nan)
            china_share.append(np.nan)
            continue
        by_c = sub.groupby('country')['count'].sum()
        hhi = sum((c / tot) ** 2 for c in by_c) * 10000
        yearly_hhi.append(hhi)
        china_share.append(by_c.get('China', 0) / tot * 100)

    # Threshold for "stable" annual estimate: ≥5 non-HIC participations
    LOW_N_THRESHOLD = 5
    is_stable = [n >= LOW_N_THRESHOLD for n in yearly_n]

    # Split series into stable (solid) vs low-n (faded)
    yrs_arr = np.array(yrs)
    hhi_arr = np.array(yearly_hhi, dtype=float)
    cs_arr = np.array(china_share, dtype=float)
    stable_mask = np.array(is_stable)

    # HHI: faded line for full series, bold markers only for stable years
    ax.plot(yrs_arr, hhi_arr, color=INK, linewidth=0.8,
            alpha=0.35, zorder=2)
    ax.plot(yrs_arr[stable_mask], hhi_arr[stable_mask],
            color=INK, linewidth=1.2, marker='o', markersize=3.5,
            markerfacecolor='white', markeredgecolor=INK,
            label='Within-non-HIC HHI (n ≥ 5)', zorder=3)
    ax.axhline(2500, color=ACCENT, linewidth=0.7,
               linestyle=':', alpha=0.6)
    ax.text(2024.7, 2700, 'High concentration\n(reference)',
            fontsize=7, color=ACCENT, ha='right')
    ax.set_xlim(2001, 2025)
    ax.set_xticks([2001, 2005, 2010, 2015, 2020, 2025])
    ax.set_ylim(0, 11000)
    ax.set_ylabel('Herfindahl-Hirschman Index\n'
                  '(within non-HIC participations)')
    ax.set_xlabel('Year')

    # Twin axis for China share
    ax2 = ax.twinx()
    ax2.plot(yrs_arr, cs_arr, color=ACCENT, linewidth=0.8,
             alpha=0.35, zorder=2)
    ax2.plot(yrs_arr[stable_mask], cs_arr[stable_mask],
             color=ACCENT, linewidth=1.0, marker='s',
             markersize=3, markerfacecolor=ACCENT,
             markeredgecolor=ACCENT,
             label='China share of non-HIC (n ≥ 5)', zorder=3)
    ax2.set_ylim(0, 105)
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax2.set_ylabel('China share of non-HIC participations',
                   color=ACCENT)
    ax2.tick_params(axis='y', colors=ACCENT)
    ax2.spines['right'].set_visible(True)
    ax2.spines['right'].set_color(ACCENT)
    ax2.spines['top'].set_visible(False)

    # In-figure note about faded segment
    ax.text(0.02, 0.04,
            'Faded segments: years with <5 non-HIC participations\n'
            '(estimates unstable due to small denominator)',
            transform=ax.transAxes, fontsize=6.5,
            color=INK_SOFT, style='italic', va='bottom')

    # Combined legend
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc='upper right', fontsize=7)
    panel_label(ax, 'B')

    fig.tight_layout()
    save(fig, 'Supplementary_Figure_S3')


# ============================================================================
# SUPPLEMENTARY TABLES (CSV exports)
# ============================================================================
def tables():
    # S1 — Historical WB classification lookup (already exists)
    src = DATA_DIR / 'world_bank_income_historical.csv'
    out = OUT / 'Supplementary_Table_S1_historical_WB_classifications.csv'
    pd.read_csv(src).to_csv(out, index=False)
    print(f'  wrote {out.name}')

    # S2 — Static vs time-varying comparison
    static = pd.read_csv(DATA_DIR / 'income_shares_by_year.csv')
    tv = pd.read_csv(DATA_DIR / 'income_shares_by_year_tv.csv')
    rows = []
    for tier_col, tier_label in [
        ('high_income', 'High income'),
        ('upper_middle', 'Upper-middle income'),
        ('lower_middle', 'Lower-middle income'),
        ('low_income', 'Low income'),
    ]:
        # Static: weighted by 'total' trials in static file
        st_total = static['total'].sum()
        st_pct = (static['total'] * static[tier_col]).sum() / st_total
        # Time-varying: counts directly
        tv_total = tv['participations'].sum()
        tv_pct = tv[tier_col].sum() / tv_total * 100
        rows.append({
            'Income tier': tier_label,
            'Static 2024–25 classification (%)': round(st_pct, 2),
            'Time-varying classification (%)': round(tv_pct, 2),
            'Difference (pp)': round(tv_pct - st_pct, 2),
        })
    s2 = pd.DataFrame(rows)
    out = OUT / 'Supplementary_Table_S2_static_vs_time_varying.csv'
    s2.to_csv(out, index=False)
    print(f'  wrote {out.name}')

    # S3 — Per-country counts by year (matrix)
    detail = pd.read_csv(DATA_DIR / 'country_year_tier_detail.csv')
    pivot = detail.pivot_table(index='country', columns='year',
                               values='count', aggfunc='sum',
                               fill_value=0)
    pivot['Total'] = pivot.sum(axis=1)
    pivot = pivot.sort_values('Total', ascending=False)
    out = OUT / 'Supplementary_Table_S3_country_year_counts.csv'
    pivot.to_csv(out)
    print(f'  wrote {out.name}')


# ============================================================================
def main():
    print(f'Writing supplementary materials to: {OUT}')
    figure_s1()
    figure_s2()
    figure_s3()
    tables()
    print('Done.')


if __name__ == '__main__':
    main()
