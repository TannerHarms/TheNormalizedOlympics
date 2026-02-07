"""
Plot top/bottom 3 performers for each year individually.

Shows which countries ranked in the top 3 (or bottom 3) for each 
Olympic year, displaying country codes on the chart.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pathlib import Path
import sys
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from plotting.plotting_style import apply_plot_style, save_plot

# Configuration
START_YEAR = 1992  # Start year for analysis (inclusive)
END_YEAR = 2024  # End year for analysis (inclusive)
TOP_N = 3  # Number of top/bottom countries to show per year
MIN_MEDALS = 1  # Minimum medals required to be included

# Paths
DATA_DIR = Path(__file__).parent.parent / 'data'
PLOTS_DIR = Path(__file__).parent.parent / 'plots'

# Apply styling
apply_plot_style()

def create_yearly_rankings_plot(df, season, metric_name, metric_col, top_or_bottom='top'):
    """Create a plot showing top/bottom N countries for each year."""
    
    # Filter years
    df_filtered = df[(df['Year'] >= START_YEAR) & (df['Year'] <= END_YEAR)].copy()
    
    # Get unique years
    years = sorted(df_filtered['Year'].unique())
    
    if len(years) == 0:
        print(f"No data for {season} Olympics in year range")
        return
    
    print(f"\n{season} Olympics ({START_YEAR}-{END_YEAR}):")
    
    # For each year, get top/bottom N countries
    yearly_data = []
    for year in years:
        year_df = df_filtered[df_filtered['Year'] == year].copy()
        # Filter minimum medals
        year_df = year_df[year_df['Total'] >= MIN_MEDALS]
        
        if len(year_df) == 0:
            continue
            
        # Sort and get top/bottom N
        if top_or_bottom == 'top':
            year_df = year_df.nlargest(TOP_N, metric_col)
        else:
            year_df = year_df.nsmallest(TOP_N, metric_col)
        
        for idx, row in year_df.iterrows():
            yearly_data.append({
                'Year': year,
                'Country': row['Country'],
                'Value': row[metric_col],
                'Rank': idx
            })
    
    if len(yearly_data) == 0:
        print(f"No data available for {top_or_bottom} performers")
        return
    
    # Create plot
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Set up y-axis positions for each rank (1st, 2nd, 3rd)
    rank_positions = {0: 2, 1: 1, 2: 0}  # Top rank at top of chart
    
    # Plot each year
    for i, year in enumerate(years):
        year_data = [d for d in yearly_data if d['Year'] == year]
        
        for rank_idx, data in enumerate(year_data):
            if rank_idx >= TOP_N:
                break
            
            y_pos = rank_positions.get(rank_idx, rank_idx)
            
            # Plot country code as text
            ax.text(year, y_pos, data['Country'], 
                   ha='center', va='center',
                   fontsize=11, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', 
                           facecolor='lightblue' if top_or_bottom == 'top' else 'lightcoral',
                           edgecolor='black', linewidth=0.5, alpha=0.7))
    
    # Formatting
    ax.set_xlabel('Year', fontsize=16)
    ax.set_ylabel('Rank', fontsize=16)
    
    direction = 'Top' if top_or_bottom == 'top' else 'Bottom'
    ax.set_title(f'{season} Olympics: {direction} {TOP_N} Countries by {metric_name} (Each Year)',
                fontsize=18, pad=20)
    
    # Set y-axis
    ax.set_ylim(-0.5, 2.5)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(['3rd', '2nd', '1st'], fontsize=13)
    
    # Set x-axis
    ax.set_xlim(START_YEAR - 1, END_YEAR + 1)
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years], fontsize=13, rotation=45)
    
    # Grid
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout(pad=0.3)
    
    # Save
    filename = f'{season.lower()}_yearly_{metric_name.lower().replace(" ", "_").replace("/", "_")}_{top_or_bottom}_{TOP_N}.png'
    save_plot(fig, PLOTS_DIR / filename)
    print(f"✓ Saved: {PLOTS_DIR / filename}")


def main():
    # Load data
    summer_df = pd.read_csv(DATA_DIR / 'summer_olympics_normalized.csv')
    winter_df = pd.read_csv(DATA_DIR / 'winter_olympics_normalized.csv')
    
    # Calculate normalized metrics
    for df in [summer_df, winter_df]:
        df['Medals_Per_Million'] = df['Total'] / df['Population'] * 1_000_000
        df['Medals_Per_HDI'] = df['Total'] / df['HDI'] * 100
        df['Medals_Per_Billion_GDP'] = df['Total'] / df['GDP'] * 1_000_000_000
        df['GDP_Per_Capita'] = df['GDP'] / df['Population']
        df['Medals_Per_GDP_Per_Capita'] = df['Total'] / df['GDP_Per_Capita'] * 1000
    
    # Define metrics to plot
    metrics = [
        ('Medals Per Capita', 'Medals_Per_Million'),
        ('Medals Per HDI', 'Medals_Per_HDI'),
        ('Medals Per GDP', 'Medals_Per_Billion_GDP'),
        ('Medals Per GDP Per Capita', 'Medals_Per_GDP_Per_Capita'),
    ]
    
    # Create plots for each metric
    for metric_name, metric_col in metrics:
        # Summer top
        create_yearly_rankings_plot(summer_df, 'Summer', metric_name, metric_col, 'top')
        # Summer bottom
        create_yearly_rankings_plot(summer_df, 'Summer', metric_name, metric_col, 'bottom')
        # Winter top
        create_yearly_rankings_plot(winter_df, 'Winter', metric_name, metric_col, 'top')
        # Winter bottom
        create_yearly_rankings_plot(winter_df, 'Winter', metric_name, metric_col, 'bottom')


if __name__ == '__main__':
    main()
