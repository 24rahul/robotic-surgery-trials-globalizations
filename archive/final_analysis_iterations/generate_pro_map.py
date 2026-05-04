#!/usr/bin/env python3
"""
Professional GIS-quality world map for robotic surgery clinical trials.
Publication-ready cartographic design.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
from matplotlib.cm import ScalarMappable
from matplotlib import font_manager
import geopandas as gpd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
OUT_DIR = BASE_DIR / 'figures_elegant'

# Country name normalization
COUNTRY_NAME_MAP = {
    'United States': 'United States of America',
    'England': 'United Kingdom',
    'South Korea': 'South Korea',
    'Korea (South)': 'South Korea',
    'Russia': 'Russia',
    'Russia (Federation)': 'Russia',
    'Czech Republic': 'Czechia',
    'Georgia (Republic)': 'Georgia',
}

def normalize_country(name):
    return COUNTRY_NAME_MAP.get(name, name)


def create_professional_map():
    """Create publication-quality choropleth map."""
    print("Creating professional GIS map...")
    
    # Load data
    trials_df = pd.read_csv(DATA_DIR / 'top_countries_overall.tsv', sep='\t')
    trials_df['country_normalized'] = trials_df['country'].apply(normalize_country)
    trials_agg = trials_df.groupby('country_normalized')['total'].sum().reset_index()
    trials_agg.columns = ['country', 'trials']
    
    # Load world geometries
    world = gpd.read_file(BASE_DIR / 'ne_countries' / 'ne_110m_admin_0_countries.shp')
    world = world.rename(columns={'NAME': 'name'})
    world = world.merge(trials_agg, left_on='name', right_on='country', how='left')
    world['trials'] = world['trials'].fillna(0)
    
    # Create figure with Natural Earth projection (aesthetically pleasing)
    fig = plt.figure(figsize=(18, 10), facecolor='white')
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.EqualEarth())
    
    ax.set_global()
    
    # Professional cartographic colors
    ocean_color = '#e6f2f8'
    land_color = '#fafafa'
    border_color = '#b0b0b0'
    coastline_color = '#808080'
    
    # Add ocean with subtle texture effect
    ax.add_feature(cfeature.OCEAN, facecolor=ocean_color, zorder=0)
    ax.add_feature(cfeature.LAND, facecolor=land_color, zorder=0)
    
    # Add subtle graticules
    gl = ax.gridlines(draw_labels=False, linewidth=0.3, color='#d0d0d0', 
                      alpha=0.5, linestyle='-', zorder=1)
    
    # Professional sequential color palette (ColorBrewer YlGnBu inspired)
    colors = [
        '#ffffcc',  # Very light yellow
        '#c7e9b4',  # Light green
        '#7fcdbb',  # Teal
        '#41b6c4',  # Blue-teal
        '#2c7fb8',  # Medium blue
        '#253494',  # Dark blue
    ]
    cmap = LinearSegmentedColormap.from_list('YlGnBu', colors, N=256)
    
    # Discrete boundaries for cleaner visualization
    bounds = [1, 10, 25, 50, 100, 200, 400, 700]
    norm = BoundaryNorm(bounds, cmap.N)
    
    # Plot countries with trials
    for idx, row in world.iterrows():
        if row['geometry'] is None:
            continue
        
        trial_count = row['trials']
        
        if trial_count > 0:
            # Get color from colormap
            color = cmap(norm(trial_count))
            edge_color = '#505050'
            edge_width = 0.4
            alpha = 0.95
        else:
            color = '#f5f5f5'
            edge_color = '#d0d0d0'
            edge_width = 0.2
            alpha = 0.6
        
        try:
            ax.add_geometries(
                [row['geometry']], 
                crs=ccrs.PlateCarree(),
                facecolor=color,
                edgecolor=edge_color,
                linewidth=edge_width,
                alpha=alpha,
                zorder=2
            )
        except:
            pass
    
    # Add coastlines on top for crisp edges
    ax.coastlines(resolution='110m', linewidth=0.5, color=coastline_color, zorder=3)
    
    # Title with professional typography
    ax.set_title('Global Distribution of Robotic Surgery Clinical Trials', 
                 fontsize=20, fontweight='bold', color='#1a1a1a', 
                 pad=20, loc='center')
    
    # Subtitle
    fig.text(0.5, 0.91, '2001–2025  |  N = 2,259 trials across 45 countries', 
             ha='center', fontsize=12, color='#505050', style='italic')
    
    # Professional colorbar
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    
    # Position colorbar
    cbar_ax = fig.add_axes([0.25, 0.08, 0.5, 0.025])
    cbar = plt.colorbar(sm, cax=cbar_ax, orientation='horizontal', 
                        extend='max', spacing='proportional')
    
    cbar.set_label('Number of Clinical Trials', fontsize=11, labelpad=10, color='#303030')
    cbar.ax.tick_params(labelsize=9, colors='#303030')
    cbar.outline.set_edgecolor('#909090')
    cbar.outline.set_linewidth(0.5)
    
    # Custom tick labels
    cbar.set_ticks([1, 10, 25, 50, 100, 200, 400])
    cbar.set_ticklabels(['1', '10', '25', '50', '100', '200', '400+'])
    
    # Add data source
    fig.text(0.98, 0.02, 'Data: PubMed/MEDLINE  |  Classification: World Bank 2024-25', 
             ha='right', fontsize=8, color='#707070', style='italic')
    
    # Remove frame
    ax.spines['geo'].set_visible(False)
    
    fig.savefig(OUT_DIR / 'fig9_world_map.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print("  Saved: fig9_world_map.png")


def create_hic_lmic_professional():
    """Create professional HIC/LMIC choropleth."""
    print("Creating professional HIC/LMIC map...")
    
    # Load data
    trials_df = pd.read_csv(DATA_DIR / 'top_countries_overall.tsv', sep='\t')
    trials_df['country_normalized'] = trials_df['country'].apply(normalize_country)
    trials_agg = trials_df.groupby('country_normalized')['total'].sum().reset_index()
    trials_agg.columns = ['country', 'trials']
    
    # Load World Bank classification
    wb_df = pd.read_csv(BASE_DIR / 'world_bank_income.csv')
    wb_to_ne = {
        'United States': 'United States of America',
        'Korea, Rep.': 'South Korea',
        'Iran, Islamic Rep.': 'Iran',
        'Egypt, Arab Rep.': 'Egypt',
        'Turkiye': 'Turkey',
    }
    
    income_lookup = {}
    for _, row in wb_df.iterrows():
        name = row['country_name']
        income = row['income_level']
        if income == 'Aggregates':
            continue
        classification = 'HIC' if income == 'High income' else 'LMIC'
        income_lookup[name] = classification
        if name in wb_to_ne:
            income_lookup[wb_to_ne[name]] = classification
    
    # Load world geometries
    world = gpd.read_file(BASE_DIR / 'ne_countries' / 'ne_110m_admin_0_countries.shp')
    world = world.rename(columns={'NAME': 'name'})
    world = world.merge(trials_agg, left_on='name', right_on='country', how='left')
    world['trials'] = world['trials'].fillna(0)
    
    # Create figure
    fig = plt.figure(figsize=(18, 10), facecolor='white')
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.EqualEarth())
    
    ax.set_global()
    
    # Background
    ax.add_feature(cfeature.OCEAN, facecolor='#e8f4f8', zorder=0)
    ax.add_feature(cfeature.LAND, facecolor='#fafafa', zorder=0)
    
    # Graticules
    gl = ax.gridlines(draw_labels=False, linewidth=0.25, color='#c0c0c0', 
                      alpha=0.4, linestyle='-', zorder=1)
    
    # Professional diverging colors
    hic_color = '#2166ac'   # Professional blue
    lmic_color = '#1a9850'  # Professional green
    no_data_color = '#f0f0f0'
    
    hic_trials = 0
    lmic_trials = 0
    
    # Plot countries
    for idx, row in world.iterrows():
        if row['geometry'] is None:
            continue
        
        trial_count = row['trials']
        country_name = row['name']
        
        if trial_count > 0:
            is_hic = income_lookup.get(country_name, 'Unknown') == 'HIC'
            
            # Vary opacity by trial count for subtle depth
            max_trials = 676
            opacity = 0.5 + 0.5 * min(1, np.log1p(trial_count) / np.log1p(max_trials))
            
            if is_hic:
                color = hic_color
                hic_trials += trial_count
            else:
                color = lmic_color
                lmic_trials += trial_count
            
            edge_color = '#404040'
            edge_width = 0.5
        else:
            color = no_data_color
            opacity = 0.5
            edge_color = '#d0d0d0'
            edge_width = 0.2
        
        try:
            ax.add_geometries(
                [row['geometry']], 
                crs=ccrs.PlateCarree(),
                facecolor=color,
                edgecolor=edge_color,
                linewidth=edge_width,
                alpha=opacity,
                zorder=2
            )
        except:
            pass
    
    # Coastlines
    ax.coastlines(resolution='110m', linewidth=0.4, color='#606060', zorder=3)
    
    # Title
    ax.set_title('Robotic Surgery Clinical Trials by Country Income Classification', 
                 fontsize=20, fontweight='bold', color='#1a1a1a', pad=20)
    
    # Subtitle with statistics
    total = hic_trials + lmic_trials
    hic_pct = hic_trials / total * 100
    lmic_pct = lmic_trials / total * 100
    
    fig.text(0.5, 0.91, f'2001–2025  |  HIC: {hic_trials:,} trials ({hic_pct:.0f}%)  •  LMIC: {lmic_trials:,} trials ({lmic_pct:.0f}%)', 
             ha='center', fontsize=12, color='#505050', style='italic')
    
    # Professional legend
    legend_elements = [
        mpatches.Patch(facecolor=hic_color, edgecolor='#303030', linewidth=0.5,
                      label='High Income Countries (HIC)'),
        mpatches.Patch(facecolor=lmic_color, edgecolor='#303030', linewidth=0.5,
                      label='Low & Middle Income Countries (LMIC)'),
        mpatches.Patch(facecolor=no_data_color, edgecolor='#b0b0b0', linewidth=0.5,
                      label='No trials reported'),
    ]
    
    legend = ax.legend(handles=legend_elements, loc='lower left', 
                      fontsize=11, framealpha=0.95, edgecolor='#c0c0c0',
                      fancybox=False, shadow=False)
    legend.get_frame().set_linewidth(0.5)
    
    # Data source
    fig.text(0.98, 0.02, 'Income Classification: World Bank (2024-25)  |  Data: PubMed/MEDLINE', 
             ha='right', fontsize=8, color='#707070', style='italic')
    
    fig.text(0.02, 0.02, 'Color intensity reflects trial volume', 
             ha='left', fontsize=8, color='#707070', style='italic')
    
    ax.spines['geo'].set_visible(False)
    
    fig.savefig(OUT_DIR / 'fig9b_hic_lmic_map.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print("  Saved: fig9b_hic_lmic_map.png")


def main():
    print("Generating professional GIS maps...\n")
    create_professional_map()
    create_hic_lmic_professional()
    print(f"\n✓ Maps saved to: {OUT_DIR}")


if __name__ == '__main__':
    main()
