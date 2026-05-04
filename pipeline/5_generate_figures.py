#!/usr/bin/env python3
"""
Generate journal-style figures for the robotic-surgery bibliometric manuscript.
Outputs to output_preview/ as PNG + PDF at 600 DPI, vector-friendly.

Figure 1:  Annual trial volume (single panel)
Figure 2:  HHI (A) and multi-country collaboration (B)
Figure 3:  Regional composition over time (A) and world bubble map (B)
Figure 4:  Income-tier distribution over time (A) and per-capita production (B)

Styling targets high-impact surgical journals (Annals of Surgery, JAMA Surgery,
BJS): pure white backgrounds, minimal chartjunk, Arial typography, neutral
greyscale with one accent color, panel labels (A/B) in bold top-left,
descriptive neutral titles (interpretation lives in the caption).
"""
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.gridspec import GridSpec
from scipy import stats

warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
SHAPE_DIR = BASE_DIR / 'shapefiles'
OUT = BASE_DIR / 'output'
OUT.mkdir(exist_ok=True)

# ----------------------------------------------------------------------------
# Journal style
# ----------------------------------------------------------------------------
INK = '#1A1A1A'         # primary ink
INK_SOFT = '#4A4A4A'    # secondary text / grid
ACCENT = '#B4412E'      # muted brick red (print-safe, matches JAMA/Annals)
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
    'savefig.edgecolor': 'none',
    'savefig.bbox': 'tight',
    'savefig.dpi': 600,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 9,
    'axes.titlesize': 10,
    'axes.titleweight': 'normal',
    'axes.labelsize': 9,
    'axes.labelcolor': INK,
    'axes.edgecolor': INK_SOFT,
    'axes.linewidth': 0.8,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.titlepad': 8,
    'xtick.color': INK,
    'ytick.color': INK,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'xtick.major.width': 0.8,
    'ytick.major.width': 0.8,
    'xtick.major.size': 3,
    'ytick.major.size': 3,
    'legend.frameon': False,
    'legend.fontsize': 8,
    'text.color': INK,
})

PANEL_LABEL_KW = dict(
    fontsize=11, fontweight='bold', ha='left', va='top', color=INK
)


def panel_label(ax, letter, x=-0.14, y=1.08):
    ax.text(x, y, letter, transform=ax.transAxes, **PANEL_LABEL_KW)


def save(fig, stem):
    fig.savefig(OUT / f'{stem}.png', dpi=600)
    fig.savefig(OUT / f'{stem}.pdf')
    plt.close(fig)
    print(f'  wrote {stem}.png and {stem}.pdf')


# ----------------------------------------------------------------------------
# Load data
# ----------------------------------------------------------------------------
def load():
    per_year = pd.read_csv(DATA_DIR / 'per_year_metrics.tsv', sep='\t')
    tv = pd.read_csv(DATA_DIR / 'income_shares_by_year_tv.csv')
    top_all = pd.read_csv(DATA_DIR / 'top_countries_overall.tsv', sep='\t')
    top_5y = pd.read_csv(DATA_DIR / 'top_countries_last5y.tsv', sep='\t')
    return per_year, tv, top_all, top_5y


# ----------------------------------------------------------------------------
# Figure 1: Annual trial volume
# ----------------------------------------------------------------------------
def figure_1(per_year):
    fig, ax = plt.subplots(figsize=(5.5, 3.4))
    years = per_year['year'].values
    counts = per_year['total_trials'].values

    # Light area fill under the curve
    ax.fill_between(years, counts, color=GRAY_2, alpha=0.18, zorder=2)
    # Primary series: line + open-circle markers
    ax.plot(years, counts, color=INK, linewidth=1.2, zorder=4)
    ax.plot(years, counts, marker='o', markersize=4.5,
            markerfacecolor='white', markeredgecolor=INK,
            markeredgewidth=0.9, linestyle='none', zorder=5)

    # Linear regression fit
    slope, intercept, r, p, _ = stats.linregress(years, counts)
    xfit = np.array([years.min(), years.max()])
    yfit = slope * xfit + intercept
    ax.plot(xfit, yfit, color=ACCENT, linewidth=1.1, linestyle='--',
            zorder=3, label='Linear fit')

    # Spearman
    rho, _ = stats.spearmanr(years, counts)

    # Annotation box — sparse, bottom-right style
    stats_text = (
        f'Slope = {slope:.2f} trials/yr\n'
        f'R² = {r**2:.3f}\n'
        f'Spearman ρ = {rho:.3f}\n'
        f'CAGR = 10.35%/yr'
    )
    ax.text(0.03, 0.97, stats_text, transform=ax.transAxes,
            fontsize=7.5, va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                      edgecolor=INK_SOFT, linewidth=0.5))

    ax.set_xlabel('Year of publication')
    ax.set_ylabel('Number of clinical trials')
    ax.set_xticks([2001, 2005, 2010, 2015, 2020, 2025])
    ax.set_xlim(2000, 2026)
    ax.set_ylim(0, max(counts) * 1.15)
    ax.grid(axis='y', color=GRAY_LIGHT, linewidth=0.5, zorder=1)

    fig.tight_layout()
    save(fig, 'Figure_1')


# ----------------------------------------------------------------------------
# Figure 2: Concentration (A) + Collaboration (B)
# ----------------------------------------------------------------------------
def figure_2(per_year):
    fig, axes = plt.subplots(1, 2, figsize=(8.5, 3.5))
    years = per_year['year'].values
    hhi_raw = per_year['hhi'].values * 10_000  # scale to DOJ convention
    mc = per_year['multi_country_share'].values * 100

    # ---- Panel A: HHI ----
    ax = axes[0]
    ax.plot(years, hhi_raw, color=INK, marker='o', markersize=4,
            markerfacecolor=GRAY_2, markeredgecolor=INK, linewidth=1.1)
    ax.axhline(1500, color=ACCENT, linewidth=0.7, linestyle=':', alpha=0.7)
    ax.axhline(2500, color=ACCENT, linewidth=0.7, linestyle=':', alpha=0.7)
    ax.text(2024.5, 1590, 'Moderate concentration',
            fontsize=7, color=ACCENT, va='bottom', ha='right')
    ax.text(2024.5, 2590, 'High concentration',
            fontsize=7, color=ACCENT, va='bottom', ha='right')

    rho_hhi, p_hhi = stats.spearmanr(years, per_year['hhi'])
    ax.text(0.97, 0.97, f'Spearman ρ = {rho_hhi:.3f}\np < 0.001',
            transform=ax.transAxes, fontsize=7.5, va='top', ha='right',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor=INK_SOFT, linewidth=0.5))

    ax.set_xlabel('Year')
    ax.set_ylabel('Herfindahl-Hirschman Index')
    ax.set_xlim(2000, 2025)
    ax.set_xticks([2001, 2005, 2010, 2015, 2020, 2025])
    ax.set_ylim(0, 3200)
    ax.grid(axis='y', color=GRAY_LIGHT, linewidth=0.5)
    panel_label(ax, 'A')

    # ---- Panel B: Multi-country share ----
    ax = axes[1]
    ax.plot(years, mc, color=INK, marker='o', markersize=4,
            markerfacecolor=GRAY_2, markeredgecolor=INK, linewidth=1.1)
    rho_mc, _ = stats.spearmanr(years, mc)
    ax.text(0.03, 0.97, f'Spearman ρ = {rho_mc:.3f}\np < 0.001',
            transform=ax.transAxes, fontsize=7.5, va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor=INK_SOFT, linewidth=0.5))

    ax.set_xlabel('Year')
    ax.set_ylabel('Trials with ≥2 countries (%)')
    ax.set_xlim(2000, 2026)
    ax.set_xticks([2001, 2005, 2010, 2015, 2020, 2025])
    ax.set_ylim(0, max(mc) * 1.15)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.grid(axis='y', color=GRAY_LIGHT, linewidth=0.5)
    panel_label(ax, 'B')

    fig.tight_layout()
    save(fig, 'Figure_2')


# ----------------------------------------------------------------------------
# Figure 3: Regional composition (A) + World bubble map (B)
# ----------------------------------------------------------------------------
def figure_3(per_year, top_all):
    fig = plt.figure(figsize=(8.5, 7.5))
    gs = GridSpec(2, 1, height_ratios=[1.0, 1.15], hspace=0.35, figure=fig)

    # ---- Panel A: Regional stacked area ----
    ax = fig.add_subplot(gs[0])
    years = per_year['year'].values
    regions = [
        ('share_north_america', 'North America', GRAY_1),
        ('share_europe',        'Europe',        GRAY_2),
        ('share_asia',          'Asia',          ACCENT),
        ('share_middle_east',   'Middle East',   ACCENT_SOFT),
        ('share_latin_america', 'Latin America', UMIC_COLOR),
        ('share_oceania',       'Oceania',       LMIC_COLOR),
        ('share_africa',        'Africa',        GRAY_3),
    ]
    stack = np.array([per_year[col].values * 100 for col, _, _ in regions])
    labels = [lbl for _, lbl, _ in regions]
    colors = [c for _, _, c in regions]

    ax.stackplot(years, stack, labels=labels, colors=colors,
                 edgecolor='white', linewidth=0.4)
    ax.set_xlim(2001, 2025)
    ax.set_ylim(0, 100)
    ax.set_xticks([2001, 2005, 2010, 2015, 2020, 2025])
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.set_xlabel('Year')
    ax.set_ylabel('Share of country-trial participations')
    ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0),
              frameon=False, fontsize=8, borderaxespad=0)
    panel_label(ax, 'A')

    # ---- Panel B: World bubble map ----
    try:
        import geopandas as gpd
        world = gpd.read_file(
            SHAPE_DIR / 'ne_110m_admin_0_countries.shp')

        ax = fig.add_subplot(gs[1])
        world.plot(
            ax=ax, color=GRAY_LIGHT,
            edgecolor='white', linewidth=0.4)

        coords = {
            'United States': (-98, 39), 'China': (105, 35),
            'United Kingdom': (-1, 53), 'Germany': (10, 51),
            'South Korea': (127, 36), 'Italy': (12, 43),
            'Japan': (138, 37), 'France': (2, 47),
            'Netherlands': (5, 52), 'Canada': (-105, 55),
            'Denmark': (10, 56), 'Sweden': (16, 62),
            'Switzerland': (8, 47), 'Turkey': (35, 39),
            'Spain': (-4, 40), 'India': (78, 22),
            'Brazil': (-52, -12), 'Australia': (134, -25),
            'Israel': (35, 31), 'Finland': (26, 64),
            'Hong Kong': (114, 22), 'Norway': (10, 62),
            'Singapore': (104, 1), 'Taiwan': (121, 24),
            'New Zealand': (173, -41), 'Egypt': (30, 27),
            'Iran': (53, 32), 'Russia': (90, 60),
            'Ireland': (-8, 53), 'Saudi Arabia': (45, 24),
            'South Africa': (25, -29),
        }
        hic = {'United States', 'United Kingdom', 'Germany',
               'South Korea', 'Italy', 'Japan', 'France',
               'Netherlands', 'Canada', 'Denmark', 'Sweden',
               'Switzerland', 'Spain', 'Australia', 'Israel',
               'Finland', 'Hong Kong', 'Norway', 'Singapore',
               'Taiwan', 'New Zealand', 'Ireland', 'Saudi Arabia'}

        for _, row in top_all.iterrows():
            c = row['country']
            n = row['total']
            if c not in coords:
                continue
            x, y = coords[c]
            color = HIC_COLOR if c in hic else ACCENT
            ax.scatter(x, y, s=n * 1.2, color=color, alpha=0.75,
                       edgecolor=INK, linewidth=0.4, zorder=5)

        # Combined legend: income category + size scale
        income_handles = [
            plt.Line2D([], [], marker='o', color='w',
                       markerfacecolor=HIC_COLOR, markersize=9,
                       markeredgecolor=INK, label='High-income'),
            plt.Line2D([], [], marker='o', color='w',
                       markerfacecolor=ACCENT, markersize=9,
                       markeredgecolor=INK,
                       label='Upper-/lower-middle-income'),
        ]
        size_handles = []
        for n, lbl in [(100, '100'), (300, '300'), (600, '600')]:
            size_handles.append(
                plt.Line2D(
                    [], [], marker='o', color='w',
                    markerfacecolor='none',
                    markersize=np.sqrt(n * 1.2),
                    markeredgecolor=INK_SOFT,
                    label=f'{lbl} participations'))

        leg1 = ax.legend(
            handles=income_handles, loc='lower left',
            bbox_to_anchor=(0.0, 0.02), frameon=False,
            fontsize=7.5, title='Income classification',
            title_fontsize=7.5)
        ax.add_artist(leg1)
        ax.legend(
            handles=size_handles, loc='lower right',
            bbox_to_anchor=(1.0, 0.02), frameon=False,
            fontsize=7, labelspacing=1.0,
            title='Trial participations',
            title_fontsize=7.5)

        ax.set_xlim(-180, 180)
        ax.set_ylim(-60, 85)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        panel_label(ax, 'B', x=0.0, y=1.04)

    except Exception as e:
        print(f'  [warn] world map skipped: {e}')
        ax = fig.add_subplot(gs[1])
        ax.text(0.5, 0.5, '[World map not rendered]',
                ha='center', va='center', transform=ax.transAxes)
        panel_label(ax, 'B')

    save(fig, 'Figure_3')


# ----------------------------------------------------------------------------
# Figure 4: Income-tier over time (A) + Per-capita production (B)
# ----------------------------------------------------------------------------
def figure_4(tv):
    fig, axes = plt.subplots(1, 2, figsize=(8.5, 3.6),
                             gridspec_kw={'width_ratios': [1.6, 1.0]})

    # ---- Panel A: Income-tier stacked area ----
    ax = axes[0]
    years = tv['year'].values
    hic = tv['high_income_pct'].values
    umic = tv['upper_middle_pct'].values
    lmic = tv['lower_middle_pct'].values
    lic = tv['low_income_pct'].values

    ax.stackplot(years, hic, umic, lmic, lic,
                 labels=['High', 'Upper-middle', 'Lower-middle', 'Low'],
                 colors=[HIC_COLOR, UMIC_COLOR, LMIC_COLOR, LIC_COLOR],
                 edgecolor='white', linewidth=0.3)
    ax.set_xlim(2001, 2025)
    ax.set_ylim(0, 100)
    ax.set_xticks([2001, 2005, 2010, 2015, 2020, 2025])
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.set_xlabel('Year')
    ax.set_ylabel('Share of income-classified participations')
    ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5),
              frameon=False, fontsize=8, title='Income tier',
              title_fontsize=8)
    panel_label(ax, 'A')

    # ---- Panel B: Per-million production (log scale) ----
    ax = axes[1]
    counts = [tv['high_income'].sum(), tv['upper_middle'].sum(),
              tv['lower_middle'].sum(), tv['low_income'].sum()]
    # 2024 WB population by tier, billions
    pops = [1.25, 2.56, 3.44, 0.75]
    per_m = [c / (p * 1000) for c, p in zip(counts, pops)]
    labels = ['HIC', 'UMIC', 'LMIC', 'LIC']
    colors = [HIC_COLOR, UMIC_COLOR, LMIC_COLOR, LIC_COLOR]
    # Dynamic value labels computed from data
    value_lbls = [f'{v:.2f}' if v >= 0.01 else f'{v:.3f}'
                  for v in per_m]

    y = np.arange(len(labels))[::-1]
    for yi, v, col in zip(y, per_m, colors):
        if v >= 0.001:
            ax.barh(yi, v, color=col, edgecolor=INK, linewidth=0.5)
        else:
            ax.barh(yi, 0.0011, color=LIC_COLOR,
                    edgecolor=INK_SOFT, linewidth=0.5, alpha=0.5)

    ax.set_xscale('log')
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlim(0.001, 5)
    ax.set_xlabel('Trials per million population')

    # Value labels next to each bar
    for yi, v, lbl in zip(y, per_m, value_lbls):
        if v >= 0.001:
            ax.text(max(v, 0.0013) * 1.25, yi, lbl, va='center',
                    fontsize=8, color=INK)
        else:
            ax.text(0.0013, yi, '0', va='center', fontsize=8,
                    color=INK_SOFT, style='italic')

    ax.grid(axis='x', color=GRAY_LIGHT, linewidth=0.5, which='major')
    panel_label(ax, 'B')

    fig.tight_layout()
    save(fig, 'Figure_4')


# ----------------------------------------------------------------------------
def main():
    print(f'Writing journal-style figures to: {OUT}')
    per_year, tv, top_all, top_5y = load()
    figure_1(per_year)
    figure_2(per_year)
    figure_3(per_year, top_all)
    figure_4(tv)
    print('Done.')


if __name__ == '__main__':
    main()
