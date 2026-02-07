"""
Plot medals per GDP trends over time with dual y-axes.

Shows line plots with top performers on left axis and bottom performers on right axis.
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
TOP_N_COUNTRIES = 6  # Number of top countries to show
MIN_PARTICIPATIONS = 4  # Minimum participations required to be included
MIN_MEDALS = 5  # Minimum total medals across all years to be included

# Paths
DATA_DIR = Path(__file__).parent.parent / 'data'
PLOTS_DIR = Path(__file__).parent.parent / 'plots'

# Apply styling
apply_plot_style()


def plot_per_gdp_trends_dual():
    """Create line plots showing per GDP medal trends with dual y-axes."""
    
    # Load normalized data
    summer_df = pd.read_csv(DATA_DIR / 'summer_olympics_normalized.csv')
    winter_df = pd.read_csv(DATA_DIR / 'winter_olympics_normalized.csv')
    
    for season, df in [('Summer', summer_df), ('Winter', winter_df)]:
        # Filter to year range
        df_filtered = df[(df['Year'] >= START_YEAR) & (df['Year'] <= END_YEAR)].copy()
        
        # Filter to countries with GDP data
        df_filtered = df_filtered[df_filtered['GDP'].notna()].copy()
        
        # Calculate per GDP metric (medals per billion USD)
        df_filtered['Medals_Per_Billion_GDP'] = (
            df_filtered['Total'] / df_filtered['GDP'] * 1_000_000_000
        )
        
        # Filter to countries with minimum participations in this range
        country_counts = df_filtered.groupby('Country').size()
        qualified_countries = country_counts[country_counts >= MIN_PARTICIPATIONS].index
        df_recent = df_filtered[df_filtered['Country'].isin(qualified_countries)]
        
        # Filter to countries with minimum total medals
        country_total_medals = df_recent.groupby('Country')['Total'].sum()
        qualified_countries = country_total_medals[country_total_medals >= MIN_MEDALS].index
        df_recent = df_recent[df_recent['Country'].isin(qualified_countries)]
        
        # Find top and bottom countries by average per GDP performance
        country_avg = df_recent.groupby('Country')['Medals_Per_Billion_GDP'].mean()
        top_countries = country_avg.nlargest(TOP_N_COUNTRIES).index.tolist()
        bottom_countries = country_avg.nsmallest(TOP_N_COUNTRIES).index.tolist()
        
        print(f"\n{season} Olympics ({START_YEAR}-{END_YEAR}):")
        print(f"Countries with >={MIN_PARTICIPATIONS} participations and >={MIN_MEDALS} total medals: {len(qualified_countries)}")
        print(f"Top {TOP_N_COUNTRIES} countries by avg medals per billion GDP:")
        for country in top_countries:
            avg_val = country_avg[country]
            print(f"  {country}: {avg_val:.2f}")
        print(f"Bottom {TOP_N_COUNTRIES} countries:")
        for country in bottom_countries:
            avg_val = country_avg[country]
            print(f"  {country}: {avg_val:.2f}")
        
        # ===== DUAL AXES PLOT =====
        fig, ax = plt.subplots(figsize=(14, 8))
        ax2 = ax.twinx()  # Create second y-axis
        
        # Track actual years in the plot data
        plot_years = set()
        
        # Create color gradations based on ranking
        top_colors = [cm.Reds_r(0.7 * i / (len(top_countries) - 1)) for i in range(len(top_countries))]
        bottom_colors = [cm.Blues_r(0.7 * i / (len(bottom_countries) - 1)) for i in range(len(bottom_countries))]
        
        # Plot top countries on left axis
        top_lines = []
        top_labels = []
        for idx, country in enumerate(top_countries):
            country_data = df_recent[df_recent['Country'] == country].sort_values('Year')
            if len(country_data) > 0:
                plot_years.update(country_data['Year'].tolist())
                avg_val = country_avg[country]
                line, = ax.plot(
                    country_data['Year'],
                    country_data['Medals_Per_Billion_GDP'],
                    marker='o',
                    linewidth=2.5,
                    markersize=8,
                    label=f'{country}: {avg_val:.4f}',
                    color=top_colors[idx],
                    alpha=0.9
                )
                top_lines.append(line)
                top_labels.append(f'{country}: {avg_val:.4f}')
        
        # Plot bottom countries on right axis
        bottom_lines = []
        bottom_labels = []
        for idx, country in enumerate(bottom_countries):
            country_data = df_recent[df_recent['Country'] == country].sort_values('Year')
            if len(country_data) > 0:
                plot_years.update(country_data['Year'].tolist())
                avg_val = country_avg[country]
                line, = ax2.plot(
                    country_data['Year'],
                    country_data['Medals_Per_Billion_GDP'],
                    marker='s',
                    linewidth=2.5,
                    markersize=8,
                    label=f'{country}: {avg_val:.4f}',
                    color=bottom_colors[idx],
                    alpha=0.9,
                    linestyle='--'
                )
                bottom_lines.append(line)
                bottom_labels.append(f'{country}: {avg_val:.4f}')
        
        # Set x-axis ticks to actual years in data
        plot_years = sorted(plot_years)
        ax.set_xticks(plot_years)
        ax.set_xticklabels([str(int(y)) for y in plot_years], rotation=45, ha='right')
        
        # Formatting
        ax.set_xlabel('Year', fontsize=16, weight='bold')
        ax.set_ylabel('Top Performers - Medals per Billion USD GDP', fontsize=16, weight='bold')
        ax2.set_ylabel('Bottom Performers - Medals per Billion USD GDP', fontsize=16, weight='bold')
        ax.set_title(
            f"Top & Bottom {TOP_N_COUNTRIES} Countries: Medals per GDP Over Time\n"
            f"{season} Olympics ({START_YEAR}-{END_YEAR})",
            fontsize=18,
            weight='bold',
            pad=20
        )
        
        # Create two separate legends on the right side
        legend_top = ax.legend(top_lines, top_labels, loc='upper left', bbox_to_anchor=(1.15, 1.015), 
                               framealpha=0.95, title='Top Performers')
        legend_bottom = ax2.legend(bottom_lines, bottom_labels, loc='lower left', bbox_to_anchor=(1.15, 0.0), 
                                   framealpha=0.95, title='Bottom Performers')
        
        # Add the first legend back (matplotlib removes it when creating the second)
        ax.add_artist(legend_top)
        
        ax.grid(True, alpha=0.7)
        
        # Save plot
        filename = f'{season.lower()}_per_GDP_trends_dual_axes_{TOP_N_COUNTRIES}.png'
        output_file = PLOTS_DIR / filename
        save_plot(fig, output_file)
        plt.close()
        print(f"✓ Saved: {output_file}")


if __name__ == '__main__':
    plot_per_gdp_trends_dual()
