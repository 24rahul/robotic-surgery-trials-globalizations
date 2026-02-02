#!/usr/bin/env python3
"""
Professional proportional symbol (bubble) map for robotic surgery trials.
Based on best practices from cartography research.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import geopandas as gpd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
OUT_DIR = BASE_DIR / 'figures_elegant'

# Country centroids (lon, lat)
COUNTRY_COORDS = {
    'United States': (-95, 38),
    'China': (105, 35),
    'United Kingdom': (-1, 53),
    'Germany': (10, 51),
    'South Korea': (127, 36),
    'Italy': (12, 43),
    'Japan': (138, 37),
    'France': (2, 47),
    'Netherlands': (5, 52),
    'Canada': (-105, 55),
    'Denmark': (10, 56),
    'Sweden': (16, 62),
    'Switzerland': (8, 47),
    'Turkey': (35, 39),
    'Spain': (-4, 40),
    'India': (78, 22),
    'Brazil': (-52, -12),
    'Australia': (134, -25),
    'Israel': (35, 31),
    'Finland': (26, 64),
    'Hong Kong': (114, 22),
    'Norway': (10, 62),
    'Singapore': (104, 1),
    'Taiwan': (121, 24),
    'New Zealand': (173, -41),
    'Egypt': (30, 27),
    'Iran': (53, 32),
    'Russia': (90, 60),
    'Russia (Federation)': (90, 60),
    'Ireland': (-8, 53),
    'Saudi Arabia': (45, 24),
    'South Africa': (25, -29),
    'Poland': (19, 52),
    'United Arab Emirates': (54, 24),
    'Romania': (25, 46),
    'England': (-1, 53),
    'Korea (South)': (127, 36),
}

# World Bank income classification
def load_income_class():
    wb_df = pd.read_csv(BASE_DIR / 'world_bank_income.csv')
    income = {}
    for _, row in wb_df.iterrows():
        if row['income_level'] != 'Aggregates':
            income[row['country_name']] = 'HIC' if row['income_level'] == 'High income' else 'LMIC'
    # Add mappings
    income['United States'] = 'HIC'
    income['South Korea'] = 'HIC'
    income['United Kingdom'] = 'HIC'
    income['England'] = 'HIC'
    income['Korea (South)'] = 'HIC'
    income['Russia'] = 'LMIC'
    income['Russia (Federation)'] = 'LMIC'
    income['Iran'] = 'LMIC'
    income['Egypt'] = 'LMIC'
    income['Turkey'] = 'LMIC'
    income['Turkiye'] = 'LMIC'
    return income


def create_bubble_map():
    """Create beautiful proportional symbol map."""
    print("Creating proportional symbol map...")
    
    # Load data
    trials_df = pd.read_csv(DATA_DIR / 'top_countries_overall.tsv', sep='\t')
    income_class = load_income_class()
    
    # Create figure with clean projection
    fig = plt.figure(figsize=(18, 10), facecolor='#fafafa')
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson())
    
    ax.set_global()
    
    # Elegant background - light land, subtle ocean
    ax.add_feature(cfeature.OCEAN, facecolor='#e8f1f5', zorder=0)
    ax.add_feature(cfeature.LAND, facecolor='#f5f5f5', edgecolor='#d0d0d0', 
                   linewidth=0.3, zorder=1)
    ax.coastlines(resolution='110m', linewidth=0.4, color='#a0a0a0', zorder=2)
    
    # Subtle graticules
    gl = ax.gridlines(draw_labels=False, linewidth=0.2, color='#c8c8c8', 
                      alpha=0.5, linestyle='-', zorder=1)
    
    # Colors
    hic_color = '#2563eb'   # Professional blue
    lmic_color = '#059669'  # Professional green
    
    # Calculate bubble sizes - area proportional to value
    max_trials = trials_df['total'].max()
    
    # Plot bubbles - largest first (so small ones are on top)
    trials_sorted = trials_df.sort_values('total', ascending=False)
    
    hic_total = 0
    lmic_total = 0
    
    for _, row in trials_sorted.iterrows():
        country = row['country']
        trials = row['total']
        
        if country not in COUNTRY_COORDS:
            continue
        
        lon, lat = COUNTRY_COORDS[country]
        
        # Area proportional to value (so radius ~ sqrt)
        # Scale: max bubble = 2500 points area
        area = (trials / max_trials) * 2500
        
        # Get income class
        is_hic = income_class.get(country, 'Unknown') == 'HIC'
        color = hic_color if is_hic else lmic_color
        
        if is_hic:
            hic_total += trials
        else:
            lmic_total += trials
        
        # Draw shadow/glow first
        ax.scatter(lon, lat, transform=ccrs.PlateCarree(),
                  s=area * 1.15, c='#000000', alpha=0.08, zorder=3)
        
        # Draw main bubble
        ax.scatter(lon, lat, transform=ccrs.PlateCarree(),
                  s=area, c=color, alpha=0.75, 
                  edgecolor='white', linewidth=1.2, zorder=4)
        
        # Add labels for top countries
        if trials >= 100:
            # Offset label position for readability
            offset_x = 8 if lon < 0 else 8
            offset_y = 8
            
            ax.annotate(f'{trials}', 
                       xy=(lon, lat), 
                       xycoords=ccrs.PlateCarree()._as_mpl_transform(ax),
                       fontsize=9, fontweight='bold', color='#1a1a1a',
                       ha='center', va='center',
                       zorder=5)
    
    # Title
    fig.suptitle('Global Distribution of Robotic Surgery Clinical Trials', 
                 fontsize=22, fontweight='bold', color='#1a1a1a', y=0.95)
    
    # Subtitle with stats
    total = hic_total + lmic_total
    fig.text(0.5, 0.89, f'2001–2025  •  {total:,} trials across 45 countries', 
             ha='center', fontsize=13, color='#505050')
    
    # Legend - bubble sizes
    legend_sizes = [50, 200, 500]
    legend_labels = ['50', '200', '500']
    
    legend_bubbles = []
    for size in legend_sizes:
        area = (size / max_trials) * 2500
        legend_bubbles.append(plt.scatter([], [], s=area, c='#808080', alpha=0.6,
                                          edgecolor='white', linewidth=1))
    
    # Color legend
    hic_patch = mpatches.Patch(facecolor=hic_color, edgecolor='white', 
                               linewidth=1, alpha=0.75,
                               label=f'High Income (HIC): {hic_total:,}')
    lmic_patch = mpatches.Patch(facecolor=lmic_color, edgecolor='white',
                                linewidth=1, alpha=0.75,
                                label=f'Low/Middle Income (LMIC): {lmic_total:,}')
    
    # Add legends
    legend1 = ax.legend(legend_bubbles, legend_labels, 
                       title='Number of Trials', title_fontsize=10,
                       loc='lower right', fontsize=9, framealpha=0.95,
                       labelspacing=1.5, borderpad=1)
    ax.add_artist(legend1)
    
    legend2 = ax.legend(handles=[hic_patch, lmic_patch],
                       title='Income Classification', title_fontsize=10,
                       loc='lower left', fontsize=10, framealpha=0.95)
    
    # Source
    fig.text(0.98, 0.02, 'Data: PubMed/MEDLINE  •  Income: World Bank 2024-25', 
             ha='right', fontsize=8, color='#707070', style='italic')
    
    fig.text(0.02, 0.02, 'Bubble area proportional to trial count', 
             ha='left', fontsize=8, color='#707070', style='italic')
    
    ax.spines['geo'].set_visible(False)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.92])
    fig.savefig(OUT_DIR / 'fig9_world_map.png', dpi=300, bbox_inches='tight',
                facecolor='#fafafa', edgecolor='none')
    plt.close(fig)
    print("  Saved: fig9_world_map.png")


def create_minimal_bubble_map():
    """Create ultra-clean minimal bubble map."""
    print("Creating minimal bubble map...")
    
    # Load data
    trials_df = pd.read_csv(DATA_DIR / 'top_countries_overall.tsv', sep='\t')
    
    # Create figure
    fig = plt.figure(figsize=(18, 9), facecolor='white')
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson())
    
    ax.set_global()
    
    # Ultra minimal background
    ax.add_feature(cfeature.OCEAN, facecolor='#f8fafc', zorder=0)
    ax.add_feature(cfeature.LAND, facecolor='#ffffff', edgecolor='#e2e8f0', 
                   linewidth=0.2, zorder=1)
    
    # Single color gradient - darker = more trials
    max_trials = trials_df['total'].max()
    
    trials_sorted = trials_df.sort_values('total', ascending=False)
    
    for _, row in trials_sorted.iterrows():
        country = row['country']
        trials = row['total']
        
        if country not in COUNTRY_COORDS:
            continue
        
        lon, lat = COUNTRY_COORDS[country]
        
        # Size
        area = (trials / max_trials) * 3000
        
        # Color intensity based on value
        intensity = 0.4 + 0.6 * (trials / max_trials)
        color = (0.15, 0.38, 0.85, intensity)  # Blue with varying alpha
        
        # Shadow
        ax.scatter(lon, lat, transform=ccrs.PlateCarree(),
                  s=area * 1.1, c='#1e40af', alpha=0.1, zorder=3)
        
        # Bubble
        ax.scatter(lon, lat, transform=ccrs.PlateCarree(),
                  s=area, c=[color], 
                  edgecolor='white', linewidth=1.5, zorder=4)
    
    # Title
    ax.set_title('Robotic Surgery Clinical Trials by Country', 
                 fontsize=20, fontweight='bold', color='#0f172a', pad=20)
    
    fig.text(0.5, 0.92, '2001–2025', ha='center', fontsize=12, color='#64748b')
    
    # Size legend
    for i, (size, label) in enumerate([(50, '50'), (200, '200'), (600, '600+')]):
        area = (size / max_trials) * 3000
        x_pos = 0.85
        y_pos = 0.25 - i * 0.06
        
        ax.scatter([0.85], [0.25 - i * 0.08], transform=ax.transAxes,
                  s=area * 0.3, c='#3b82f6', alpha=0.7,
                  edgecolor='white', linewidth=1, zorder=10)
        fig.text(x_pos + 0.04, y_pos - 0.015, label, fontsize=9, 
                color='#374151', va='center')
    
    fig.text(0.85, 0.32, 'Trials', fontsize=10, fontweight='bold', 
            color='#1f2937', ha='center')
    
    ax.spines['geo'].set_visible(False)
    
    fig.savefig(OUT_DIR / 'fig9b_bubble_minimal.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print("  Saved: fig9b_bubble_minimal.png")


def main():
    print("Generating professional bubble maps...\n")
    create_bubble_map()
    create_minimal_bubble_map()
    print(f"\n✓ Maps saved to: {OUT_DIR}")


if __name__ == '__main__':
    main()
