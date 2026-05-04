#!/usr/bin/env python3
"""
Generate figures for 25-year globalization analysis of robotic surgery clinical trials.

Reads: robotic_surgery_trials_clinical/globalization/per_year_metrics.tsv
Writes PNGs into the same globalization/ directory:
- fig1_annual_trials_multicountry.png
- fig2_regional_shares.png
"""
from pathlib import Path
import logging
import pandas as pd
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
PER_YEAR = BASE_DIR / 'robotic_surgery_trials_clinical' / 'globalization' / 'per_year_metrics.tsv'
OUT_DIR = BASE_DIR / 'robotic_surgery_trials_clinical' / 'globalization'

plt.rcParams.update({
    'figure.dpi': 140,
    'savefig.dpi': 140,
    'axes.spines.top': False,
    'axes.spines.right': False
})


def load_data():
    df = pd.read_csv(PER_YEAR, sep='\t')
    df = df.sort_values('year')
    return df


def fig1_annual_trials_multicountry(df):
    fig, ax1 = plt.subplots(figsize=(9, 4.5))
    ax1.plot(df['year'], df['total_trials'], color='#1f77b4', linewidth=2, label='Total trials')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Total trials', color='#1f77b4')
    ax1.tick_params(axis='y', labelcolor='#1f77b4')

    ax2 = ax1.twinx()
    ax2.plot(df['year'], df['multi_country_share'] * 100.0, color='#d62728', linewidth=2, linestyle='--', label='Multi-country share (%)')
    ax2.set_ylabel('Multi-country share (%)', color='#d62728')
    ax2.tick_params(axis='y', labelcolor='#d62728')

    # Legend combining both axes
    lines, labels = [], []
    for ax in (ax1, ax2):
        lns, lbs = ax.get_legend_handles_labels()
        lines.extend(lns)
        labels.extend(lbs)
    ax1.legend(lines, labels, loc='upper left')

    fig.tight_layout()
    out = OUT_DIR / 'fig1_annual_trials_multicountry.png'
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    logger.info(f'Saved {out}')


def fig2_regional_shares(df):
    # Stacked area of regional shares
    regions = [
        'share_europe', 'share_asia', 'share_north_america', 'share_oceania',
        'share_latin_america', 'share_middle_east', 'share_africa'
    ]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.stackplot(df['year'], [df[c] for c in regions], labels=[r.replace('share_', '').replace('_', ' ').title() for r in regions], colors=colors, alpha=0.9)
    ax.set_xlabel('Year')
    ax.set_ylabel('Regional share of trials')
    ax.set_ylim(0, 1)
    ax.legend(loc='upper left', ncol=2, fontsize=8)

    fig.tight_layout()
    out = OUT_DIR / 'fig2_regional_shares.png'
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    logger.info(f'Saved {out}')


def main():
    df = load_data()
    fig1_annual_trials_multicountry(df)
    fig2_regional_shares(df)

if __name__ == '__main__':
    main() 