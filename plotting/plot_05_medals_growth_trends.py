"""
Plot medals growth trends relative to previous Olympics.

Shows line plots of countries' medal counts normalized by their own
previous Olympics performance, revealing which countries are improving
or declining relative to their own baseline.
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
TOP_N_COUNTRIES = 10  # Number of top countries to show
MIN_MEDALS = 5  # Minimum medals in previous Olympics to be included

# Paths
DATA_DIR = Path(__file__).parent.parent / 'data'
PLOTS_DIR = Path(__file__).parent.parent / 'plots'

# Apply styling
apply_plot_style()


def plot_growth_trends():
    """Create line plots showing medal growth relative to previous Olympics."""
    
    # Load normalized data
    summer_df = pd.read_csv(DATA_DIR / 'summer_olympics_normalized.csv')
    winter_df = pd.read_csv(DATA_DIR / 'winter_olympics_normalized.csv')
    
    for season, df in [('Summer', summer_df), ('Winter', winter_df)]:
        # Filter to year range
        df_filtered = df[(df['Year'] >= START_YEAR) & (df['Year'] <= END_YEAR)].copy()
        
        # Calculate growth ratio for each country based on year-over-year in this range
        growth_data = []
        for country in df_filtered['Country'].unique():
            country_data = df_filtered[df_filtered['Country'] == country].sort_values('Year')
            
            if len(country_data) < 2:
                continue
            
            # Calculate year-over-year growth ratios
            for i in range(1, len(country_data)):
                prev_medals = country_data.iloc[i-1]['Total']
                curr_medals = country_data.iloc[i]['Total']
                year = country_data.iloc[i]['Year']
                
                # Only include if previous Olympics had minimum medals
                if prev_medals >= MIN_MEDALS:
                    growth_ratio = curr_medals / prev_medals
                    growth_data.append({
                        'Country': country,
                        'Year': year,
                        'Growth_Ratio': growth_ratio,
                        'Prev_Medals': prev_medals,
                        'Curr_Medals': curr_medals
                    })
        
        if not growth_data:
            print(f"No {season} data with sufficient medals")
            continue
            
        growth_df = pd.DataFrame(growth_data)
        
        if growth_df.empty:
            print(f"No {season} growth data available")
            continue
        
        # Find countries with best average growth
        country_avg_growth = growth_df.groupby('Country')['Growth_Ratio'].mean()
        
        # Find countries with best average growth
        country_avg_growth = growth_df.groupby('Country')['Growth_Ratio'].mean()
        # Sort by how close to 1.0 (stable/growing), preferring growth over 1.0
        country_avg_growth = country_avg_growth.sort_values(ascending=False)
        
        # Get top growers
        top_countries = country_avg_growth.head(TOP_N_COUNTRIES).index.tolist()
        
        # Get year range from actual data
        year_range = sorted(growth_df['Year'].unique())
        
        print(f"\n{season} Olympics ({START_YEAR}-{END_YEAR}):")
        print(f"Growth data years: {year_range[0]}-{year_range[-1]}")
        print(f"Top {TOP_N_COUNTRIES} countries by avg growth ratio:")
        for country in top_countries:
            avg_val = country_avg_growth[country]
            print(f"  {country}: {avg_val:.2f}x")
        
        # Create line plot
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Track actual years in the plot data
        plot_years = set()
        
        # Create color gradations based on ranking
        colormap = cm.Reds_r if season == 'Summer' else cm.Blues_r
        colors = [colormap(0.7 * i / (len(top_countries) - 1)) for i in range(len(top_countries))]
        
        # Plot each country
        for idx, country in enumerate(top_countries):
            country_growth = growth_df[growth_df['Country'] == country].sort_values('Year')
            if len(country_growth) > 0:
                plot_years.update(country_growth['Year'].tolist())
                avg_growth = country_avg_growth[country]
                ax.plot(
                    country_growth['Year'],
                    country_growth['Growth_Ratio'],
                    marker='o',
                    linewidth=2.5,
                    markersize=8,
                    label=f'{country}: {avg_growth:.2f}x',
                    color=colors[idx],
                    alpha=0.9
                )
        
        # Sort years for axis ticks
        plot_years = sorted(plot_years)
        
        # Add reference line at 1.0 (no change)
        ax.axhline(y=1.0, color='gray', linestyle='--', linewidth=1.5, alpha=0.5, label='No change')
        
        # Formatting
        ax.set_xlabel('Year', fontsize=16, weight='bold')
        ax.set_ylabel('Medal Ratio (Current / Previous Olympics)', fontsize=16, weight='bold')
        ax.set_title(
            f"Top {TOP_N_COUNTRIES} Countries: Medal Growth vs Previous Olympics\\n"
            f"{season} Olympics ({START_YEAR}-{END_YEAR})\\n"
            f"(Minimum {MIN_MEDALS} medals in previous Olympics)",
            fontsize=18,
            weight='bold',
            pad=20
        )
        
        # Legend
        ax.legend(
            loc='upper left',
            bbox_to_anchor=(1.02, 1),
            fontsize=10,
            frameon=True
        )
        
        ax.grid(True, alpha=0.3)
        ax.set_xticks(plot_years)
        ax.set_xticklabels([str(int(y)) for y in plot_years], rotation=45)
        
        # Add horizontal shading for growth zones
        ymin, ymax = ax.get_ylim()
        ax.axhspan(1.0, ymax, alpha=0.05, color='green', zorder=0)
        ax.axhspan(ymin, 1.0, alpha=0.05, color='red', zorder=0)
        
        plt.tight_layout()
        
        # Save
        filename = PLOTS_DIR / f"{season.lower()}_medals_growth_trends_top_{TOP_N_COUNTRIES}.png"
        save_plot(fig, filename)
        print(f"Saved: {filename}")


if __name__ == '__main__':
    plot_growth_trends()
