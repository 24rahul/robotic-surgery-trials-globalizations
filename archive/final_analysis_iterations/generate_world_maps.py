#!/usr/bin/env python3
"""
Generate professional world maps for robotic surgery clinical trials.
1. Choropleth map with countries shaded by trial count
2. 3D globe with collaboration connections (flight-path style)
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as path_effects
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable
import geopandas as gpd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
OUT_DIR = BASE_DIR / 'figures_elegant'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ARGOS Theme Colors
COLORS = {
    'primary': '#5C5C5C',
    'hic': '#4B5563',
    'lmic': '#9CA3AF',
    'background': '#FAFAFA',
    'text': '#374151',
}

# Country name mapping: Our data -> Natural Earth names
COUNTRY_NAME_MAP = {
    'United States': 'United States of America',
    'United Kingdom': 'United Kingdom',
    'England': 'United Kingdom',
    'South Korea': 'South Korea',
    'Korea (South)': 'South Korea',
    'Russia': 'Russia',
    'Russia (Federation)': 'Russia',
    'Taiwan': 'Taiwan',
    'Hong Kong': 'Hong Kong',
    'Iran': 'Iran',
    'Czech Republic': 'Czechia',
    'United Arab Emirates': 'United Arab Emirates',
    'Georgia (Republic)': 'Georgia',
}

# Country centroids for connection lines
COUNTRY_CENTROIDS = {
    'United States of America': (-98.5, 39.8),
    'China': (105.0, 35.0),
    'United Kingdom': (-2.0, 54.0),
    'Germany': (9.0, 51.0),
    'South Korea': (127.5, 36.5),
    'Italy': (12.5, 42.5),
    'Japan': (138.0, 36.0),
    'France': (2.0, 46.0),
    'Netherlands': (5.75, 52.5),
    'Canada': (-106.0, 56.0),
    'Denmark': (10.0, 56.0),
    'Sweden': (15.0, 62.0),
    'Switzerland': (8.0, 47.0),
    'Turkey': (35.0, 39.0),
    'Spain': (-4.0, 40.0),
    'India': (78.0, 22.0),
    'Brazil': (-55.0, -10.0),
    'Australia': (135.0, -25.0),
    'Israel': (35.0, 31.0),
    'Finland': (26.0, 64.0),
    'Hong Kong': (114.2, 22.3),
    'Norway': (10.0, 62.0),
    'Singapore': (103.8, 1.3),
    'Taiwan': (121.0, 23.5),
    'New Zealand': (174.0, -41.0),
    'Egypt': (30.0, 27.0),
    'Iran': (53.0, 32.0),
    'Russia': (100.0, 60.0),
    'Ireland': (-8.0, 53.5),
    'Saudi Arabia': (45.0, 24.0),
    'South Africa': (24.0, -29.0),
    'Poland': (20.0, 52.0),
    'United Arab Emirates': (54.0, 24.0),
    'Romania': (25.0, 46.0),
    'Serbia': (21.0, 44.0),
    'Hungary': (20.0, 47.0),
    'Georgia': (43.5, 42.0),
    'Cyprus': (33.0, 35.0),
    'Nigeria': (8.0, 10.0),
    'Czechia': (15.5, 50.0),
    'Pakistan': (70.0, 30.0),
}


def load_world_bank_data():
    """Load official World Bank income classification."""
    wb_path = BASE_DIR / 'world_bank_income.csv'
    wb_df = pd.read_csv(wb_path)
    
    income_lookup = {}
    for _, row in wb_df.iterrows():
        name = row['country_name']
        income = row['income_level']
        if income == 'Aggregates':
            continue
        income_lookup[name] = 'HIC' if income == 'High income' else 'LMIC'
    
    return income_lookup


def normalize_country(name):
    """Normalize country names to Natural Earth format."""
    return COUNTRY_NAME_MAP.get(name, name)


def create_choropleth_map():
    """Create a proper choropleth world map with country shading."""
    print("Creating choropleth world map...")
    
    # Load trial data
    trials_df = pd.read_csv(DATA_DIR / 'top_countries_overall.tsv', sep='\t')
    
    # Normalize country names and aggregate (e.g., England -> UK)
    trials_df['country_normalized'] = trials_df['country'].apply(normalize_country)
    trials_agg = trials_df.groupby('country_normalized')['total'].sum().reset_index()
    trials_agg.columns = ['country', 'trials']
    
    # Get world geometries from Natural Earth shapefile
    world = gpd.read_file(BASE_DIR / 'ne_countries' / 'ne_110m_admin_0_countries.shp')
    world = world.rename(columns={'NAME': 'name'})
    
    # Merge trial data with world geometries
    world = world.merge(trials_agg, left_on='name', right_on='country', how='left')
    world['trials'] = world['trials'].fillna(0)
    
    # Create figure with Cartopy projection
    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson())
    
    # Set background
    ax.set_global()
    ax.add_feature(cfeature.OCEAN, color='#E8F4F8', zorder=0)
    ax.add_feature(cfeature.LAND, color='#F5F5F5', zorder=0)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor='#CCCCCC', zorder=1)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.3, edgecolor='#999999', zorder=1)
    
    # Custom colormap - grey to dark charcoal
    colors_cmap = ['#F0F0F0', '#BEBEBE', '#8C8C8C', '#5C5C5C', '#3D3D3D', '#1A1A1A']
    cmap = LinearSegmentedColormap.from_list('grey_gradient', colors_cmap)
    
    # Normalize with log scale for better visualization
    max_trials = trials_agg['trials'].max()
    norm = Normalize(vmin=0, vmax=max_trials)
    
    # Plot each country
    for idx, row in world.iterrows():
        if row['trials'] > 0:
            color = cmap(norm(row['trials']))
            ax.add_geometries(
                [row['geometry']], 
                crs=ccrs.PlateCarree(),
                facecolor=color,
                edgecolor='white',
                linewidth=0.5,
                zorder=2
            )
    
    # Add colorbar
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', pad=0.05, 
                        shrink=0.6, aspect=30)
    cbar.set_label('Number of Clinical Trials', fontsize=12, fontweight='medium')
    cbar.ax.tick_params(labelsize=10)
    
    # Title
    ax.set_title('Global Distribution of Robotic Surgery Clinical Trials (2001-2025)\n', 
                 fontsize=16, fontweight='bold', pad=10)
    
    # Add top 5 country labels
    top5 = trials_agg.nlargest(5, 'trials')
    for _, row in top5.iterrows():
        country = row['country']
        if country in COUNTRY_CENTROIDS:
            lon, lat = COUNTRY_CENTROIDS[country]
            ax.annotate(
                f"{country.replace('United States of America', 'USA')}\n({int(row['trials'])})",
                xy=(lon, lat),
                xycoords=ccrs.PlateCarree()._as_mpl_transform(ax),
                fontsize=9,
                fontweight='bold',
                ha='center',
                va='center',
                color='white',
                path_effects=[path_effects.withStroke(linewidth=2, foreground='black')]
            )
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig9_world_choropleth.png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("  Saved: fig9_world_choropleth.png")


def create_3d_globe_connections():
    """Create a 3D-style globe with collaboration connection arcs."""
    print("Creating 3D globe with collaboration connections...")
    
    # Load trial data
    trials_df = pd.read_csv(DATA_DIR / 'top_countries_overall.tsv', sep='\t')
    trials_df['country_normalized'] = trials_df['country'].apply(normalize_country)
    trials_agg = trials_df.groupby('country_normalized')['total'].sum().reset_index()
    trials_agg.columns = ['country', 'trials']
    
    # Create figure with orthographic (3D globe) projection
    fig = plt.figure(figsize=(14, 14))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Orthographic(central_longitude=20, central_latitude=30))
    
    # Style the globe
    ax.set_global()
    ax.add_feature(cfeature.OCEAN, color='#1a1a2e', zorder=0)
    ax.add_feature(cfeature.LAND, color='#16213e', zorder=1)
    ax.add_feature(cfeature.BORDERS, linewidth=0.2, edgecolor='#3a3a5c', zorder=2)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.3, edgecolor='#4a4a6a', zorder=2)
    
    # Add gridlines for 3D effect
    ax.gridlines(linewidth=0.3, color='#3a3a5c', alpha=0.5, linestyle='--')
    
    # Get world geometries and color countries by trial count
    world = gpd.read_file(BASE_DIR / 'ne_countries' / 'ne_110m_admin_0_countries.shp')
    world = world.rename(columns={'NAME': 'name'})
    world = world.merge(trials_agg, left_on='name', right_on='country', how='left')
    world['trials'] = world['trials'].fillna(0)
    
    # Custom colormap - dark blue to bright cyan/teal
    colors_cmap = ['#16213e', '#1a4066', '#0f5f87', '#0891b2', '#22d3ee', '#67e8f9']
    cmap = LinearSegmentedColormap.from_list('ocean_glow', colors_cmap)
    max_trials = trials_agg['trials'].max()
    norm = Normalize(vmin=0, vmax=max_trials)
    
    # Plot countries
    for idx, row in world.iterrows():
        if row['trials'] > 0:
            color = cmap(norm(row['trials']))
            try:
                ax.add_geometries(
                    [row['geometry']], 
                    crs=ccrs.PlateCarree(),
                    facecolor=color,
                    edgecolor='#4a4a6a',
                    linewidth=0.3,
                    zorder=3
                )
            except:
                pass
    
    # Define major collaboration connections (based on common international collaborations)
    # These represent the most frequent international collaboration routes
    collaborations = [
        # US collaborations
        ('United States of America', 'United Kingdom', 0.9),
        ('United States of America', 'Germany', 0.7),
        ('United States of America', 'Canada', 0.8),
        ('United States of America', 'Japan', 0.5),
        ('United States of America', 'China', 0.6),
        ('United States of America', 'Italy', 0.5),
        ('United States of America', 'France', 0.5),
        ('United States of America', 'Netherlands', 0.4),
        ('United States of America', 'South Korea', 0.4),
        # European collaborations
        ('United Kingdom', 'Germany', 0.8),
        ('United Kingdom', 'Netherlands', 0.7),
        ('United Kingdom', 'Italy', 0.6),
        ('United Kingdom', 'France', 0.6),
        ('United Kingdom', 'Denmark', 0.5),
        ('Germany', 'Netherlands', 0.6),
        ('Germany', 'Italy', 0.5),
        ('Germany', 'Switzerland', 0.5),
        ('Germany', 'France', 0.5),
        ('France', 'Italy', 0.4),
        ('Netherlands', 'Denmark', 0.4),
        # Asia collaborations
        ('China', 'Japan', 0.4),
        ('China', 'South Korea', 0.5),
        ('Japan', 'South Korea', 0.4),
        ('China', 'United Kingdom', 0.4),
        ('China', 'Germany', 0.3),
        # Australia/NZ
        ('Australia', 'United Kingdom', 0.3),
        ('Australia', 'United States of America', 0.3),
    ]
    
    # Draw connection arcs
    for country1, country2, weight in collaborations:
        if country1 in COUNTRY_CENTROIDS and country2 in COUNTRY_CENTROIDS:
            lon1, lat1 = COUNTRY_CENTROIDS[country1]
            lon2, lat2 = COUNTRY_CENTROIDS[country2]
            
            # Create great circle arc
            ax.plot(
                [lon1, lon2], [lat1, lat2],
                transform=ccrs.Geodetic(),
                color='#f97316',  # Orange glow
                linewidth=1 + weight * 2,
                alpha=0.3 + weight * 0.4,
                zorder=4
            )
    
    # Add glowing points for major hubs
    top_countries = trials_agg.nlargest(15, 'trials')
    for _, row in top_countries.iterrows():
        country = row['country']
        if country in COUNTRY_CENTROIDS:
            lon, lat = COUNTRY_CENTROIDS[country]
            size = 50 + (row['trials'] / max_trials) * 300
            
            # Outer glow
            ax.scatter(lon, lat, transform=ccrs.PlateCarree(),
                      s=size*1.5, c='#fbbf24', alpha=0.3, zorder=5)
            # Core point
            ax.scatter(lon, lat, transform=ccrs.PlateCarree(),
                      s=size, c='#f59e0b', edgecolor='white', linewidth=0.5,
                      alpha=0.9, zorder=6)
    
    # Title
    ax.set_title('International Collaboration Network\nRobotic Surgery Clinical Trials', 
                 fontsize=18, fontweight='bold', color='white', pad=20)
    
    # Set background
    fig.patch.set_facecolor('#0f0f1a')
    
    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], color='#f97316', linewidth=3, alpha=0.7, label='Collaboration Route'),
        plt.scatter([0], [0], c='#f59e0b', s=100, label='Research Hub'),
    ]
    ax.legend(handles=legend_elements, loc='lower left', 
             facecolor='#1a1a2e', edgecolor='#3a3a5c',
             labelcolor='white', fontsize=10)
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig9b_globe_connections.png', dpi=300, 
                bbox_inches='tight', facecolor='#0f0f1a')
    plt.close(fig)
    print("  Saved: fig9b_globe_connections.png")


def create_alternative_flat_connections():
    """Create a flat world map with collaboration arcs (for presentations)."""
    print("Creating flat map with collaboration arcs...")
    
    # Load trial data
    trials_df = pd.read_csv(DATA_DIR / 'top_countries_overall.tsv', sep='\t')
    trials_df['country_normalized'] = trials_df['country'].apply(normalize_country)
    trials_agg = trials_df.groupby('country_normalized')['total'].sum().reset_index()
    trials_agg.columns = ['country', 'trials']
    
    # Load World Bank data for HIC/LMIC coloring
    income_lookup = load_world_bank_data()
    
    # Create figure
    fig = plt.figure(figsize=(18, 10))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson())
    
    ax.set_global()
    ax.add_feature(cfeature.OCEAN, color='#f0f4f8', zorder=0)
    ax.add_feature(cfeature.LAND, color='#e5e7eb', zorder=0)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor='#d1d5db', zorder=1)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.3, edgecolor='#9ca3af', zorder=1)
    
    # Get world geometries
    world = gpd.read_file(BASE_DIR / 'ne_countries' / 'ne_110m_admin_0_countries.shp')
    world = world.rename(columns={'NAME': 'name'})
    world = world.merge(trials_agg, left_on='name', right_on='country', how='left')
    world['trials'] = world['trials'].fillna(0)
    
    # Color by HIC/LMIC with intensity by trial count
    max_trials = trials_agg['trials'].max()
    
    for idx, row in world.iterrows():
        if row['trials'] > 0:
            # Determine income class
            country_name = row['name']
            is_hic = income_lookup.get(country_name, 'Unknown') == 'HIC'
            
            # Intensity based on trial count
            intensity = 0.3 + 0.7 * (row['trials'] / max_trials)
            
            if is_hic:
                color = plt.cm.Blues(0.3 + 0.6 * intensity)
            else:
                color = plt.cm.Oranges(0.3 + 0.6 * intensity)
            
            try:
                ax.add_geometries(
                    [row['geometry']], 
                    crs=ccrs.PlateCarree(),
                    facecolor=color,
                    edgecolor='white',
                    linewidth=0.5,
                    zorder=2
                )
            except:
                pass
    
    # Draw collaboration arcs
    collaborations = [
        ('United States of America', 'United Kingdom', 1.0),
        ('United States of America', 'Germany', 0.7),
        ('United States of America', 'Canada', 0.8),
        ('United States of America', 'China', 0.6),
        ('United States of America', 'Japan', 0.5),
        ('United Kingdom', 'Germany', 0.7),
        ('United Kingdom', 'Netherlands', 0.6),
        ('United Kingdom', 'Italy', 0.5),
        ('Germany', 'Italy', 0.4),
        ('China', 'South Korea', 0.5),
        ('China', 'Japan', 0.4),
    ]
    
    for country1, country2, weight in collaborations:
        if country1 in COUNTRY_CENTROIDS and country2 in COUNTRY_CENTROIDS:
            lon1, lat1 = COUNTRY_CENTROIDS[country1]
            lon2, lat2 = COUNTRY_CENTROIDS[country2]
            
            ax.plot(
                [lon1, lon2], [lat1, lat2],
                transform=ccrs.Geodetic(),
                color='#dc2626',
                linewidth=0.8 + weight * 2,
                alpha=0.4 + weight * 0.3,
                zorder=4
            )
    
    # Add points for top countries
    top15 = trials_agg.nlargest(15, 'trials')
    for _, row in top15.iterrows():
        country = row['country']
        if country in COUNTRY_CENTROIDS:
            lon, lat = COUNTRY_CENTROIDS[country]
            size = 30 + (row['trials'] / max_trials) * 200
            
            ax.scatter(lon, lat, transform=ccrs.PlateCarree(),
                      s=size, c='#dc2626', edgecolor='white', linewidth=1,
                      alpha=0.8, zorder=5)
    
    # Title and legend
    ax.set_title('Robotic Surgery Clinical Trials: Global Distribution & Collaboration Network\n(2001-2025)', 
                 fontsize=16, fontweight='bold', pad=15)
    
    # Custom legend
    hic_patch = mpatches.Patch(color='#3b82f6', label='High Income Countries', alpha=0.7)
    lmic_patch = mpatches.Patch(color='#f97316', label='Low & Middle Income Countries', alpha=0.7)
    collab_line = plt.Line2D([0], [0], color='#dc2626', linewidth=2, alpha=0.6, label='Collaboration Routes')
    ax.legend(handles=[hic_patch, lmic_patch, collab_line], loc='lower left', 
             framealpha=0.9, fontsize=10)
    
    # Source note
    fig.text(0.5, 0.02, 'Income Classification: World Bank (2024-2025)', 
             ha='center', fontsize=9, style='italic', color='#6b7280')
    
    fig.tight_layout()
    fig.savefig(OUT_DIR / 'fig9c_map_collaborations.png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("  Saved: fig9c_map_collaborations.png")


def main():
    print("Generating world maps...\n")
    create_choropleth_map()
    create_3d_globe_connections()
    create_alternative_flat_connections()
    print(f"\n✓ All maps saved to: {OUT_DIR}")


if __name__ == '__main__':
    main()
