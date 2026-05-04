#!/usr/bin/env python3
"""
Clean, elegant world map for robotic surgery clinical trials.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable
import geopandas as gpd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
OUT_DIR = BASE_DIR / 'figures_elegant'

# Country name mapping: our data -> Natural Earth
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

# Country centroids for labels
LABEL_POSITIONS = {
    'United States of America': (-100, 40, 'USA\n676'),
    'China': (105, 35, 'China\n322'),
    'United Kingdom': (-5, 55, 'UK\n293'),
    'Germany': (10, 51, 'Germany\n203'),
    'South Korea': (128, 36, 'S. Korea\n187'),
    'Italy': (12, 43, 'Italy\n163'),
    'Japan': (138, 36, 'Japan\n131'),
    'France': (2, 47, 'France\n103'),
    'India': (78, 22, 'India\n46'),
    'Brazil': (-52, -10, 'Brazil\n41'),
    'Australia': (134, -25, 'Australia\n37'),
    'Canada': (-100, 58, 'Canada\n86'),
}

def normalize_country(name):
    return COUNTRY_NAME_MAP.get(name, name)


def create_simple_map():
    """Create a clean, simple world map showing trial volume."""
    print("Creating simple trial volume map...")
    
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
    
    # Create figure - use PlateCarree for less distortion
    fig, ax = plt.subplots(figsize=(16, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    
    ax.set_extent([-150, 180, -50, 75], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.OCEAN, color='#f5f7fa', zorder=0)
    ax.coastlines(linewidth=0.3, color='#94a3b8')
    
    max_trials = trials_agg['trials'].max()
    
    # Simple blue gradient
    colors = ['#f1f5f9', '#dbeafe', '#93c5fd', '#3b82f6', '#1d4ed8', '#1e3a8a']
    cmap = LinearSegmentedColormap.from_list('blue_gradient', colors)
    norm = Normalize(vmin=0, vmax=max_trials)
    
    # Plot countries
    for idx, row in world.iterrows():
        if row['geometry'] is None:
            continue
        
        trial_count = row['trials']
        
        if trial_count > 0:
            color = cmap(norm(trial_count))
            edge_color = '#64748b'
            edge_width = 0.4
        else:
            color = '#f8fafc'
            edge_color = '#e2e8f0'
            edge_width = 0.2
        
        try:
            ax.add_geometries(
                [row['geometry']], 
                crs=ccrs.PlateCarree(),
                facecolor=color,
                edgecolor=edge_color,
                linewidth=edge_width,
                zorder=1
            )
        except:
            pass
    
    # Add country labels for top contributors
    for country, (lon, lat, label) in LABEL_POSITIONS.items():
        ax.annotate(
            label,
            xy=(lon, lat),
            xycoords=ccrs.PlateCarree()._as_mpl_transform(ax),
            fontsize=8,
            fontweight='bold',
            ha='center',
            va='center',
            color='#1e293b',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                     edgecolor='#cbd5e1', alpha=0.85, linewidth=0.5)
        )
    
    # Colorbar
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', pad=0.05, 
                        shrink=0.4, aspect=20)
    cbar.set_label('Number of Clinical Trials', fontsize=11, labelpad=8)
    cbar.ax.tick_params(labelsize=9)
    
    ax.set_title('Global Distribution of Robotic Surgery Clinical Trials (2001-2025)', 
                 fontsize=16, fontweight='bold', pad=15)
    
    # Remove axis frame
    ax.spines['geo'].set_visible(False)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig9_world_map.png', dpi=300, bbox_inches='tight',
                facecolor='white')
    plt.close(fig)
    print("  Saved: fig9_world_map.png")


def create_hic_lmic_map():
    """Create HIC vs LMIC map with clear distinction."""
    print("Creating HIC/LMIC map...")
    
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
    fig, ax = plt.subplots(figsize=(16, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    
    ax.set_extent([-150, 180, -50, 75], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.OCEAN, color='#f5f7fa', zorder=0)
    ax.coastlines(linewidth=0.3, color='#94a3b8')
    
    # Plot countries
    for idx, row in world.iterrows():
        if row['geometry'] is None:
            continue
        
        trial_count = row['trials']
        country_name = row['name']
        
        if trial_count > 0:
            is_hic = income_lookup.get(country_name, 'Unknown') == 'HIC'
            
            if is_hic:
                color = '#3b82f6'  # Blue for HIC
            else:
                color = '#10b981'  # Green/teal for LMIC
            
            edge_color = '#374151'
            edge_width = 0.5
        else:
            color = '#f1f5f9'
            edge_color = '#e2e8f0'
            edge_width = 0.2
        
        try:
            ax.add_geometries(
                [row['geometry']], 
                crs=ccrs.PlateCarree(),
                facecolor=color,
                edgecolor=edge_color,
                linewidth=edge_width,
                zorder=1
            )
        except:
            pass
    
    # Add labels
    for country, (lon, lat, label) in LABEL_POSITIONS.items():
        ax.annotate(
            label,
            xy=(lon, lat),
            xycoords=ccrs.PlateCarree()._as_mpl_transform(ax),
            fontsize=8,
            fontweight='bold',
            ha='center',
            va='center',
            color='#1e293b',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                     edgecolor='#94a3b8', alpha=0.9, linewidth=0.5)
        )
    
    # Legend
    hic_patch = mpatches.Patch(color='#3b82f6', label='High Income Countries (HIC)')
    lmic_patch = mpatches.Patch(color='#10b981', label='Low & Middle Income (LMIC)')
    none_patch = mpatches.Patch(color='#f1f5f9', edgecolor='#e2e8f0', 
                                linewidth=0.5, label='No trials reported')
    
    ax.legend(handles=[hic_patch, lmic_patch, none_patch], 
             loc='lower left', fontsize=10, framealpha=0.95)
    
    ax.set_title('Robotic Surgery Clinical Trials by Country Income Level (2001-2025)', 
                 fontsize=16, fontweight='bold', pad=15)
    
    fig.text(0.5, 0.02, 'Income Classification: World Bank (2024-2025)', 
             ha='center', fontsize=9, style='italic', color='#64748b')
    
    ax.spines['geo'].set_visible(False)
    
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(OUT_DIR / 'fig9b_hic_lmic_map.png', dpi=300, bbox_inches='tight',
                facecolor='white')
    plt.close(fig)
    print("  Saved: fig9b_hic_lmic_map.png")


def main():
    print("Generating world maps...\n")
    create_simple_map()
    create_hic_lmic_map()
    print(f"\n✓ Maps saved to: {OUT_DIR}")


if __name__ == '__main__':
    main()
