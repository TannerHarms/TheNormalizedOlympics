"""
Plot medals per HDI trends over time.

Shows line plots of the top countries by medals per HDI point
over the last N Olympics, tracking how their normalized performance evolves.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from plotting.plotting_style import apply_plot_style, save_plot

# Configuration
START_YEAR = 1992  # Start year for analysis (inclusive)
END_YEAR = 2024  # End year for analysis (inclusive)
TOP_N_COUNTRIES = 10  # Number of top countries to show
MIN_PARTICIPATIONS = 4  # Minimum participations required to be included

# Paths
DATA_DIR = Path(__file__).parent.parent / 'data'
PLOTS_DIR = Path(__file__).parent.parent / 'plots'

# Apply styling
apply_plot_style()


def plot_per_hdi_trends():
    """Create line plots showing per HDI medal trends over time."""
    
    # Load normalized data
    summer_df = pd.read_csv(DATA_DIR / 'summer_olympics_normalized.csv')
    winter_df = pd.read_csv(DATA_DIR / 'winter_olympics_normalized.csv')
    
    for season, df in [('Summer', summer_df), ('Winter', winter_df)]:
        # Filter to year range
        df_filtered = df[(df['Year'] >= START_YEAR) & (df['Year'] <= END_YEAR)].copy()
        
        # Filter to countries with HDI data
        df_filtered = df_filtered[df_filtered['HDI'].notna()].copy()
        
        # Calculate per HDI metric
        df_filtered['Medals_Per_HDI'] = df_filtered['Total'] / df_filtered['HDI']
        
        # Filter to countries with minimum participations in this range
        country_counts = df_filtered.groupby('Country').size()
        qualified_countries = country_counts[country_counts >= MIN_PARTICIPATIONS].index
        df_recent = df_filtered[df_filtered['Country'].isin(qualified_countries)]
        
        # Find top and bottom countries by average per HDI performance
        country_avg = df_recent.groupby('Country')['Medals_Per_HDI'].mean()
        top_countries = country_avg.nlargest(TOP_N_COUNTRIES).index.tolist()
        bottom_countries = country_avg.nsmallest(TOP_N_COUNTRIES).index.tolist()
        
        print(f"\n{season} Olympics ({START_YEAR}-{END_YEAR}):")
        print(f"Countries with >={MIN_PARTICIPATIONS} participations: {len(qualified_countries)}")
        print(f"Top {TOP_N_COUNTRIES} countries by avg medals per HDI:")
        for country in top_countries:
            avg_val = country_avg[country]
            print(f"  {country}: {avg_val:.1f}")
        print(f"Bottom {TOP_N_COUNTRIES} countries:")
        for country in bottom_countries:
            avg_val = country_avg[country]
            print(f"  {country}: {avg_val:.1f}")
        
        # Create line plot
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Track actual years in the plot data
        plot_years = set()
        
        # Create color gradations based on ranking
        colormap = cm.Reds_r if season == 'Summer' else cm.Blues_r
        top_colors = [colormap(0.7 * i / (len(top_countries) - 1)) for i in range(len(top_countries))]
        bottom_colors = [colormap(0.7 * i / (len(bottom_countries) - 1)) for i in range(len(bottom_countries))]
        
        # Plot top countries (solid lines)
        for idx, country in enumerate(top_countries):
            country_data = df_recent[df_recent['Country'] == country].sort_values('Year')
            if len(country_data) > 0:
                plot_years.update(country_data['Year'].tolist())
                avg_val = country_avg[country]
                ax.plot(
                    country_data['Year'],
                    country_data['Medals_Per_HDI'],
                    marker='o',
                    linewidth=2.5,
                    markersize=8,
                    label=f'{country} (Top): {avg_val:.1f}',
                    color=top_colors[idx],
                    alpha=0.9,
                    linestyle='-'
                )
        
        # Plot bottom countries (dashed lines)
        for idx, country in enumerate(bottom_countries):
            country_data = df_recent[df_recent['Country'] == country].sort_values('Year')
            if len(country_data) > 0:
                plot_years.update(country_data['Year'].tolist())
                avg_val = country_avg[country]
                ax.plot(
                    country_data['Year'],
                    country_data['Medals_Per_HDI'],
                    marker='s',
                    linewidth=2.5,
                    markersize=8,
                    label=f'{country} (Bottom): {avg_val:.1f}',
                    color=bottom_colors[idx],
                    alpha=0.9,
                    linestyle='--'
                )
        
        # Sort years for axis ticks
        plot_years = sorted(plot_years)
        
        # Formatting
        ax.set_xlabel('Year', fontsize=16, weight='bold')
        ax.set_ylabel('Medals per HDI Point', fontsize=16, weight='bold')
        ax.set_title(
            f"Top & Bottom {TOP_N_COUNTRIES} Countries: Medals per HDI Over Time\\n"
            f"{season} Olympics ({START_YEAR}-{END_YEAR})",
            fontsize=18,
            weight='bold',
            pad=20
        )
        
        # Legend
        ax.legend(
            loc='best',
            framealpha=0.95,
            ncol=2
        )
        
        ax.grid(True, alpha=0.7)
        ax.set_xticks(plot_years)
        ax.set_xticklabels([str(int(y)) for y in plot_years], rotation=45, ha='right')
        
        # Save
        filename = PLOTS_DIR / f"{season.lower()}_per_HDI_trends_top_bottom_{TOP_N_COUNTRIES}.png"
        save_plot(fig, filename)
        print(f"Saved: {filename}")


if __name__ == '__main__':
    plot_per_hdi_trends()
