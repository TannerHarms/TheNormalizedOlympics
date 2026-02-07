"""
Plot cumulative medals (Gold, Silver, Bronze, Total) for top 15 countries 
over the last N Olympics.

Separate plots for Summer and Winter Olympics.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from plotting.plotting_style import apply_plot_style, save_plot, get_country_color

# Configuration
START_YEAR = 1992  # Start year for analysis (inclusive)
END_YEAR = 2024  # End year for analysis (inclusive)
TOP_N_COUNTRIES = 15  # Number of top countries to show

# Paths
DATA_DIR = Path(__file__).parent.parent / 'data'
PLOTS_DIR = Path(__file__).parent.parent / 'plots'

# Apply styling
apply_plot_style()

def get_recent_olympics_cumulative(df, season, start_year, end_year):
    """
    Get cumulative medals for each country within the specified year range.
    
    Returns DataFrame with columns: Country, Gold, Silver, Bronze, Total
    """
    # Filter to year range
    df_filtered = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)].copy()
    
    # For each country, sum their medals in the year range
    cumulative_list = []
    
    for country in df_filtered['Country'].unique():
        country_data = df_filtered[df_filtered['Country'] == country]
        
        if len(country_data) > 0:
            cumulative_list.append({
                'Country': country,
                'Gold': country_data['Gold'].sum(),
                'Silver': country_data['Silver'].sum(),
                'Bronze': country_data['Bronze'].sum(),
                'Total': country_data['Total'].sum(),
                'N_Olympics': len(country_data),
                'Years': f"{country_data['Year'].min()}-{country_data['Year'].max()}"
            })
    
    cumulative = pd.DataFrame(cumulative_list)
    
    # Get the actual year range
    actual_years = sorted(df_filtered['Year'].unique())
    
    return cumulative, actual_years


def plot_top_countries_medals(cumulative, recent_years, season, top_n):
    """
    Create stacked bar chart showing Gold, Silver, Bronze for top countries.
    """
    # Sort by total and take top N
    top = cumulative.nlargest(top_n, 'Total').sort_values('Total', ascending=True)
    
    # Prepare data
    countries = top['Country'].tolist()
    gold = top['Gold'].values
    silver = top['Silver'].values
    bronze = top['Bronze'].values
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Create stacked horizontal bars
    y_pos = np.arange(len(countries))
    
    # Stack: Bronze (bottom), Silver (middle), Gold (top)
    p1 = ax.barh(y_pos, bronze, color='#CD7F32', label='Bronze', edgecolor='black', linewidth=0.5)
    p2 = ax.barh(y_pos, silver, left=bronze, color='#C0C0C0', label='Silver', edgecolor='black', linewidth=0.5)
    p3 = ax.barh(y_pos, gold, left=bronze+silver, color='#FFD700', label='Gold', edgecolor='black', linewidth=0.5)
    
    # Customize
    ax.set_yticks(y_pos)
    ax.set_yticklabels(countries, fontsize=11)
    ax.set_xlabel('Total Medals', fontsize=12, fontweight='bold')
    
    years_str = f"{min(recent_years)}–{max(recent_years)}"
    ax.set_title(
        f'Top {top_n} Countries by Total Medals\n{season} Olympics: Last {len(recent_years)} Games ({years_str})',
        fontsize=14,
        fontweight='bold',
        pad=20
    )
    
    # Add totals at the end of bars
    for i, (g, s, b) in enumerate(zip(gold, silver, bronze)):
        total = g + s + b
        ax.text(total + 1, i, f'{int(total)}', va='center', fontsize=10, fontweight='bold')
    
    # Legend
    ax.legend(loc='lower right', fontsize=11, framealpha=0.95)
    
    # Grid
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    return fig


def main():
    print("="*70)
    print("CUMULATIVE MEDALS: TOP COUNTRIES OVER RECENT OLYMPICS")
    print("="*70)
    print()
    
    # Load data
    summer = pd.read_csv(DATA_DIR / 'summer_olympics_by_year.csv')
    winter = pd.read_csv(DATA_DIR / 'winter_olympics_by_year.csv')
    
    # ===== SUMMER OLYMPICS =====
    print(f"Processing Summer Olympics ({START_YEAR}-{END_YEAR})...")
    cumulative_summer, years_summer = get_recent_olympics_cumulative(summer, 'Summer', START_YEAR, END_YEAR)
    
    print(f"  Years included: {min(years_summer)}–{max(years_summer)}")
    print(f"  Total countries: {len(cumulative_summer)}")
    print(f"  Top 5: {cumulative_summer.nlargest(5, 'Total')[['Country', 'Total']].to_string(index=False)}")
    print()
    
    # Create plot
    fig = plot_top_countries_medals(cumulative_summer, years_summer, 'Summer', TOP_N_COUNTRIES)
    
    # Save
    output_file = PLOTS_DIR / f'top_{TOP_N_COUNTRIES}_cumulative_summer_{START_YEAR}_{END_YEAR}.png'
    save_plot(fig, output_file)
    plt.close()
    
    print(f"  ✓ Saved: {output_file.name}")
    print()
    
    # ===== WINTER OLYMPICS =====
    print(f"Processing Winter Olympics ({START_YEAR}-{END_YEAR})...")
    cumulative_winter, years_winter = get_recent_olympics_cumulative(winter, 'Winter', START_YEAR, END_YEAR)
    
    print(f"  Years included: {min(years_winter)}–{max(years_winter)}")
    print(f"  Total countries: {len(cumulative_winter)}")
    print(f"  Top 5: {cumulative_winter.nlargest(5, 'Total')[['Country', 'Total']].to_string(index=False)}")
    print()
    
    # Create plot
    fig = plot_top_countries_medals(cumulative_winter, years_winter, 'Winter', TOP_N_COUNTRIES)
    
    # Save
    output_file = PLOTS_DIR / f'top_{TOP_N_COUNTRIES}_cumulative_winter_{START_YEAR}_{END_YEAR}.png'
    save_plot(fig, output_file)
    plt.close()
    
    print(f"  ✓ Saved: {output_file.name}")
    print()
    
    print("="*70)
    print("✓ PLOTS CREATED")
    print("="*70)


if __name__ == '__main__':
    main()
