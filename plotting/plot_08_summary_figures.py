"""
Create summary figures with bar charts for most recent Olympics and trend lines.

Three-panel layout:
- Top left: Bar chart of top 10 performers from most recent Olympics (stacked: Bronze/Silver/Gold)
- Top right: Bar chart of bottom 10 performers from most recent Olympics (stacked: Bronze/Silver/Gold)
- Bottom: Dual-axes line plot showing best and worst performers over time (2000-2024)
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
TOP_N_COUNTRIES = 10  # Number of top/bottom countries to show
MIN_PARTICIPATIONS = 4  # Minimum participations required to be included
MIN_MEDALS = 5  # Minimum total medals across all years to be included
TOP_N_TRENDS = 6  # Number of countries to show in bottom trend plot

# Paths
DATA_DIR = Path(__file__).parent.parent / 'data'
PLOTS_DIR = Path(__file__).parent.parent / 'plots'

# Apply styling
apply_plot_style()

# Data source descriptions for each metric
DATA_SOURCES = {
    'Total Medals (Summer)': 'Olympic Medals: Kaggle (1896-2016) & Wikipedia (2018-2024).',
    'Total Medals (Winter)': 'Olympic Medals: Kaggle (1896-2016) & Wikipedia (2018-2024).',
    'Capita': 'Population: World Bank Open Data (1980-2024)',
    'HDI': 'Human Development Index: UNDP Human Development Reports (1990-2021)',
    'GDP': 'GDP: World Bank Open Data (1980-2024)',
    'GDP Per Capita': 'GDP & Population: World Bank Open Data (1980-2024)',
    '1000 Square Kilometers': 'Land Area: World Bank Open Data (1980-2024)',
    '1000 Km Coastline': 'Coastline Length: CIA World Factbook & manually compiled',
    '100m Elevation': 'Average Elevation: CIA World Factbook & Wikipedia',
    'Degree Temperature': 'Avg Temperature: World Bank Climate Knowledge Portal & manually compiled',
    '100 Sunshine Days': 'Sunshine Days: Manually compiled from national weather services',
    '100 Cm Snowfall': 'Snowfall: Manually compiled from climate data sources',
    'Million Internet Users': 'Internet Users: World Bank Open Data (1990-2024)',
    '1000 Vehicles': 'Vehicles: World Bank Open Data (sparse coverage)',
    'University': 'Universities: UNESCO Institute for Statistics & manually compiled (2024)',
    'Sports Stadium': 'Large Stadiums: Manually compiled from various sources (2024)',
    'Ski Resort': 'Ski Resorts: Manually compiled from ski resort databases (2024)',
    'Billion Healthcare Spending': 'Healthcare Spending: World Bank Open Data (2000-2024)',
    'Year Life Expectancy': 'Life Expectancy: World Bank Open Data (1980-2024)',
    '100 Work Hours Per Year': 'Work Hours: OECD Statistics (2023, OECD countries only)',
    'Million Kg Coffee': 'Coffee Consumption: International Coffee Organization (2024)',
    'Million Cola Servings': 'Soft Drinks: Estimated from various consumption data (2024)',
    'Peace Index Point': 'Safety: Global Peace Index by Institute for Economics & Peace (2024)',
    '1000 Refugees Received': 'Refugees Hosted: UNHCR Refugee Statistics (2023). Higher = hosting more refugees while winning medals',
    '1000 Refugees Produced': 'Refugees Originating: UNHCR Refugee Statistics (2023)',
    'Pct GDP Military Spending': 'Military Expenditure (% of GDP): World Bank / SIPRI (2000-2023)',
    '1000 Military Personnel': 'Active Military Personnel: IISS Military Balance (2024)'
}


def create_summary_figure(df, season, metric_name, metric_col, medal_type='Total', medal_type_display='Medals'):
    """Create a 3-panel summary figure with bar charts and trend lines.
    
    Args:
        df: DataFrame with Olympic data
        season: 'Summer' or 'Winter'
        metric_name: Display name of normalization metric (e.g., 'Capita', 'GDP')
        metric_col: Column name of normalization metric
        medal_type: Column name of medal type to plot (e.g., 'Total', 'Individual_Medalists')
        medal_type_display: Display name for medal type (e.g., 'Medals', 'Individual Medalists')
    """
    
    # Filter years
    df_filtered = df[(df['Year'] >= START_YEAR) & (df['Year'] <= END_YEAR)].copy()
    
    # Check if medal_type column exists
    if medal_type not in df_filtered.columns:
        print(f"  Column {medal_type} not found in dataset")
        return
    
    # Drop rows with NaN in medal_type column
    df_filtered = df_filtered.dropna(subset=[medal_type])
    
    # Drop rows with NaN or zero values in the specific metric column
    # Zero values cause divide-by-zero errors (e.g., landlocked countries with coastline, countries with no refugees)
    # For baseline (Total), we only filter NaN and inf, not zero
    df_filtered = df_filtered.dropna(subset=[metric_col])
    if metric_col != 'Total' and not metric_col.startswith(medal_type):
        df_filtered = df_filtered[df_filtered[metric_col] != 0]
    df_filtered = df_filtered[~df_filtered[metric_col].isin([float('inf'), float('-inf')])]
    
    # Get most recent year (use 2024 for summer, 2022 for winter when available)
    if season == 'Summer' and 2024 in df_filtered['Year'].values:
        most_recent_year = 2024
    elif season == 'Winter' and 2022 in df_filtered['Year'].values:
        most_recent_year = 2022
    elif season == 'Summer' and 2020 in df_filtered['Year'].values:
        most_recent_year = 2020  # Fallback if 2024 not available
    else:
        most_recent_year = df_filtered['Year'].max()
    
    if len(df_filtered) == 0:
        print(f"No data for {season} Olympics")
        return
    
    print(f"\n{season} Olympics ({START_YEAR}-{END_YEAR}):")
    print(f"All countries with data: {df_filtered['Country'].nunique()}")
    
    # Get most recent Olympics data for bar charts (NO FILTERS - show all countries)
    recent_df = df_filtered[df_filtered['Year'] == most_recent_year].copy()
    if len(recent_df) == 0:
        print(f"No data for most recent year {most_recent_year}")
        return
    
    # For medal types (not Total_Athletes), filter out countries with zero medals in the specific year
    # This prevents division by zero when calculating normalized bar heights
    if medal_type != 'Total_Athletes':
        recent_df = recent_df[recent_df['Total'] > 0].copy()
        if len(recent_df) == 0:
            print(f"No countries with medals in {most_recent_year}")
            return
    
    # Now apply filters ONLY for trend line qualification
    # These filters determine which countries appear in the trend plots, not the bar charts
    if medal_type == 'Total_Athletes':
        # For Total_Athletes, include all countries in trends
        qualified_trend_countries = df_filtered['Country'].unique()
    else:
        # For medal types, use standard medal and participation filters FOR TRENDS ONLY
        # For ratio metrics (Medals_Per_Athlete, Medals_Awarded_Per_Athlete), 
        # we need to check the underlying medal count (Total) rather than summing ratios
        if medal_type in ['Medals_Per_Athlete', 'Medals_Awarded_Per_Athlete']:
            # Use Total medals for qualification check
            country_total_medals = df_filtered.groupby('Country')['Total'].sum()
        else:
            # Use the actual medal type for qualification
            country_total_medals = df_filtered.groupby('Country')[medal_type].sum()
        
        qualified_by_medals = country_total_medals[country_total_medals >= MIN_MEDALS].index
        
        # Count participations
        country_participations = df_filtered.groupby('Country')['Year'].nunique()
        qualified_by_participations = country_participations[country_participations >= MIN_PARTICIPATIONS].index
        
        # Intersection of both qualifications
        qualified_trend_countries = qualified_by_medals.intersection(qualified_by_participations)
        
        print(f"Countries qualified for trends (>={MIN_PARTICIPATIONS} participations and >={MIN_MEDALS} total medals): {len(qualified_trend_countries)}")
    
    # Calculate normalized medal counts for each medal type
    # Use the ratio of individual medal to total medals, scaled by the metric value
    total_norm = recent_df[metric_col]
    # Show stacked Gold/Silver/Bronze for medal-related types and ratio metrics
    if medal_type in ['Total', 'Total_Medals_By_Event', 'Individual_Medalists', 'Total_Medals_Awarded', 
                      'Medals_Per_Athlete', 'Medals_Awarded_Per_Athlete']:
        recent_df['Bronze_norm'] = (recent_df['Bronze'] / recent_df['Total']) * total_norm
        recent_df['Silver_norm'] = (recent_df['Silver'] / recent_df['Total']) * total_norm
        recent_df['Gold_norm'] = (recent_df['Gold'] / recent_df['Total']) * total_norm
        recent_df['NoMedal_norm'] = 0
    elif medal_type == 'Total_Athletes':
        # For Total_Athletes, show breakdown by medal type plus non-medalists
        # Calculate proportion of athletes who are medalists (handle division by zero)
        medalists_proportion = recent_df['Individual_Medalists'] / recent_df['Total_Athletes']
        # Non-medalists proportion
        no_medal_proportion = 1 - medalists_proportion
        
        # Break down medalists by medal type (using medal counts as proxy)
        # For countries with 0 total medals, set all medal bars to 0
        medal_breakdown = recent_df['Total'] > 0
        recent_df['Bronze_norm'] = 0.0
        recent_df['Silver_norm'] = 0.0
        recent_df['Gold_norm'] = 0.0
        recent_df.loc[medal_breakdown, 'Bronze_norm'] = (
            total_norm[medal_breakdown] * 
            medalists_proportion[medal_breakdown] * 
            (recent_df.loc[medal_breakdown, 'Bronze'] / recent_df.loc[medal_breakdown, 'Total'])
        )
        recent_df.loc[medal_breakdown, 'Silver_norm'] = (
            total_norm[medal_breakdown] * 
            medalists_proportion[medal_breakdown] * 
            (recent_df.loc[medal_breakdown, 'Silver'] / recent_df.loc[medal_breakdown, 'Total'])
        )
        recent_df.loc[medal_breakdown, 'Gold_norm'] = (
            total_norm[medal_breakdown] * 
            medalists_proportion[medal_breakdown] * 
            (recent_df.loc[medal_breakdown, 'Gold'] / recent_df.loc[medal_breakdown, 'Total'])
        )
        recent_df['NoMedal_norm'] = total_norm * no_medal_proportion
    
    recent_df['metric'] = recent_df[metric_col]
    recent_sorted = recent_df.sort_values('metric', ascending=False)
    
    # Get top and bottom countries from most recent Olympics (ALL countries, no filters)
    top_recent = recent_sorted.head(TOP_N_COUNTRIES)
    bottom_recent = recent_sorted.tail(TOP_N_COUNTRIES)
    
    # Apply additional trend filter: require 3+ data points for meaningful trends
    # This combines with the medal/participation filters already applied above
    num_years_in_data = df_filtered['Year'].nunique()
    min_required_years = min(3, num_years_in_data)  # Use 3 or all years if less than 3
    
    # Filter to countries that meet BOTH the medal/participation requirements AND the 3+ year requirement
    country_counts = df_filtered[df_filtered['Country'].isin(qualified_trend_countries)].groupby('Country').size()
    final_trend_countries = country_counts[country_counts >= min_required_years].index
    df_trends = df_filtered[df_filtered['Country'].isin(final_trend_countries)]
    
    print(f"Countries in trend lines (also require {min_required_years}+ years): {len(final_trend_countries)}")
    
    # Calculate metrics for trends: use MAX value instead of average for trend selection
    max_metrics = df_trends.groupby('Country')[metric_col].max().sort_values(ascending=False)
    
    # Get top and bottom countries for trends (based on max value, not average)
    top_trend_countries = max_metrics.head(TOP_N_TRENDS).index.tolist()
    bottom_trend_countries = max_metrics.tail(TOP_N_TRENDS).index.tolist()
    
    # Create figure with 3 subplots
    fig = plt.figure(figsize=(18, 12))
    
    # Convert metric name for supertitle
    if metric_col == medal_type or metric_col == 'Total':
        # Baseline case - unnormalized
        suptitle = f'{season} Olympics {medal_type_display}'
    else:
        # Normalized case
        metric_short = metric_name
        suptitle = f'{season} Olympics {medal_type_display} per {metric_short}'
    
    # Add suptitle with season (left-aligned with left edge of plots, raised higher)
    fig.suptitle(suptitle, fontsize=32, weight='bold', 
                 x=0.08, y=0.99, ha='left')
    
    # Create bottom plot first to get legend dimensions
    bottom_left = 0.08
    bottom_right = 0.75
    bottom_bottom = 0.08
    bottom_top = 0.50
    bottom_width = bottom_right - bottom_left
    
    # Create bottom axes and temporary top axes
    ax_bottom = fig.add_axes([bottom_left, bottom_bottom, bottom_width, bottom_top - bottom_bottom])
    
    # Top plots - create with temporary positions
    top_bottom = 0.58
    top_top = 0.94
    top_height = top_top - top_bottom
    
    # Temporary equal width for both
    temp_width = 0.35
    gap = 0.05
    ax_top_left = fig.add_axes([bottom_left, top_bottom, temp_width, top_height])
    ax_top_right = fig.add_axes([bottom_left + temp_width + gap, top_bottom, temp_width, top_height])
    
    # Color schemes
    medal_colors = {'Bronze': '#CD7F32', 'Silver': '#C0C0C0', 'Gold': '#FFD700', 'NoMedal': '#36454F'}
    
    # ===== TOP LEFT: Top performers bar chart =====
    countries = top_recent['Country'].values
    bronze = top_recent['Bronze_norm'].values
    silver = top_recent['Silver_norm'].values
    gold = top_recent['Gold_norm'].values
    no_medal = top_recent['NoMedal_norm'].values
    
    x = np.arange(len(countries))
    width = 0.6
    
    if medal_type == 'Total_Athletes':
        # For Total_Athletes, stack no medal on bottom, then Bronze, Silver, Gold
        bars0 = ax_top_left.bar(x, no_medal, width, label='No Medal', 
                                color=medal_colors['NoMedal'], edgecolor='black', linewidth=1.5)
        bars1 = ax_top_left.bar(x, bronze, width, bottom=no_medal, label='Bronze', color=medal_colors['Bronze'], 
                                edgecolor='black', linewidth=1.5)
        bars2 = ax_top_left.bar(x, silver, width, bottom=no_medal+bronze, label='Silver', color=medal_colors['Silver'],
                                edgecolor='black', linewidth=1.5)
        bars3 = ax_top_left.bar(x, gold, width, bottom=no_medal+bronze+silver, label='Gold', color=medal_colors['Gold'],
                                edgecolor='black', linewidth=1.5)
    else:
        # For medal types, just stack Bronze, Silver, Gold
        bars1 = ax_top_left.bar(x, bronze, width, label='Bronze', color=medal_colors['Bronze'], 
                                edgecolor='black', linewidth=1.5)
        bars2 = ax_top_left.bar(x, silver, width, bottom=bronze, label='Silver', color=medal_colors['Silver'],
                                edgecolor='black', linewidth=1.5)
        bars3 = ax_top_left.bar(x, gold, width, bottom=bronze+silver, label='Gold', color=medal_colors['Gold'],
                                edgecolor='black', linewidth=1.5)
    
    ax_top_left.set_xticks(x)
    ax_top_left.set_xticklabels(countries, rotation=45, ha='right', fontsize=18)
    ax_top_left.set_xlim(-0.5, len(countries) - 0.5)
    # Add padding above highest bar
    if medal_type == 'Total_Athletes':
        max_height = (bronze + silver + gold + no_medal).max()
    else:
        max_height = (bronze + silver + gold).max()
    ax_top_left.set_ylim(0, max_height * 1.08)
    ax_top_left.tick_params(axis='y', labelsize=18)
    ax_top_left.grid(True, alpha=0.3, axis='y')
    
    # Add text annotation inside subplot (15 points offset from edges)
    ax_top_left.annotate(f'Top Performers {most_recent_year}', 
                         xy=(1, 1), xycoords='axes fraction',
                         xytext=(-15, -15), textcoords='offset points',
                         fontsize=24, weight='bold', ha='right', va='top')
    
    # ===== TOP RIGHT: Bottom performers bar chart =====
    countries_bottom = bottom_recent['Country'].values
    bronze_bottom = bottom_recent['Bronze_norm'].values
    silver_bottom = bottom_recent['Silver_norm'].values
    gold_bottom = bottom_recent['Gold_norm'].values
    no_medal_bottom = bottom_recent['NoMedal_norm'].values
    
    x_bottom = np.arange(len(countries_bottom))
    
    if medal_type == 'Total_Athletes':
        # For Total_Athletes, stack no medal on bottom, then Bronze, Silver, Gold
        ax_top_right.bar(x_bottom, no_medal_bottom, width, label='No Medal', color=medal_colors['NoMedal'], 
                        edgecolor='black', linewidth=1.5)
        ax_top_right.bar(x_bottom, bronze_bottom, width, bottom=no_medal_bottom, label='Bronze', 
                        color=medal_colors['Bronze'], edgecolor='black', linewidth=1.5)
        ax_top_right.bar(x_bottom, silver_bottom, width, bottom=no_medal_bottom+bronze_bottom, label='Silver', 
                        color=medal_colors['Silver'], edgecolor='black', linewidth=1.5)
        ax_top_right.bar(x_bottom, gold_bottom, width, bottom=no_medal_bottom+bronze_bottom+silver_bottom, label='Gold', 
                        color=medal_colors['Gold'], edgecolor='black', linewidth=1.5)
    else:
        # For medal types, just stack Bronze, Silver, Gold
        ax_top_right.bar(x_bottom, bronze_bottom, width, label='Bronze', color=medal_colors['Bronze'],
                        edgecolor='black', linewidth=1.5)
        ax_top_right.bar(x_bottom, silver_bottom, width, bottom=bronze_bottom, label='Silver', 
                        color=medal_colors['Silver'], edgecolor='black', linewidth=1.5)
        ax_top_right.bar(x_bottom, gold_bottom, width, bottom=bronze_bottom+silver_bottom, label='Gold', 
                        color=medal_colors['Gold'], edgecolor='black', linewidth=1.5)
    
    ax_top_right.set_xticks(x_bottom)
    ax_top_right.set_xticklabels(countries_bottom, rotation=45, ha='right', fontsize=18)
    ax_top_right.set_xlim(-0.5, len(countries_bottom) - 0.5)
    # Add padding above highest bar (extra padding for baseline to fit text)
    if medal_type == 'Total_Athletes':
        max_height_bottom = (bronze_bottom + silver_bottom + gold_bottom + no_medal_bottom).max()
    else:
        max_height_bottom = (bronze_bottom + silver_bottom + gold_bottom).max()
    if metric_col == 'Total':
        ax_top_right.set_ylim(0, max_height_bottom * 1.15)  # More space for baseline
    else:
        ax_top_right.set_ylim(0, max_height_bottom * 1.08)
    ax_top_right.tick_params(axis='y', labelsize=18)
    ax_top_right.grid(True, alpha=0.3, axis='y')
    
    # Add text annotation inside subplot (15 points offset from edges)
    ax_top_right.annotate(f'Bottom Performers {most_recent_year}', 
                          xy=(1, 1), xycoords='axes fraction',
                          xytext=(-15, -15), textcoords='offset points',
                          fontsize=24, weight='bold', ha='right', va='top')
    
    # ===== BOTTOM: Dual-axes trend plot =====
    ax2 = ax_bottom.twinx()
    
    # Calculate medians for all selected countries and sort by median
    # This ensures legend values are in order matching color intensity
    top_country_medians = []
    for country in top_trend_countries:
        country_data = df_trends[df_trends['Country'] == country]
        median_val = country_data[metric_col].median()
        top_country_medians.append((country, median_val))
    
    # Sort by median descending for top performers (highest first)
    top_country_medians.sort(key=lambda x: x[1], reverse=True)
    
    bottom_country_medians = []
    for country in bottom_trend_countries:
        country_data = df_trends[df_trends['Country'] == country]
        median_val = country_data[metric_col].median()
        bottom_country_medians.append((country, median_val))
    
    # Sort by median ascending for bottom performers (lowest first)
    bottom_country_medians.sort(key=lambda x: x[1])
    
    # Plot top performers
    top_colors = [cm.Reds_r(0.7 * i / (len(top_country_medians) - 1)) for i in range(len(top_country_medians))]
    top_lines = []
    top_labels = []
    
    for idx, (country, median_medals) in enumerate(top_country_medians):
        country_data = df_trends[df_trends['Country'] == country].sort_values('Year')
        
        line, = ax_bottom.plot(country_data['Year'], 
                               country_data[metric_col],
                               marker='o', linestyle='-', linewidth=2.5,
                               color=top_colors[idx],
                               label=f"{country}: {median_medals:.3f}")
        top_lines.append(line)
        top_labels.append(f"{country}: {median_medals:.3f}")
    
    # Plot bottom performers
    bottom_colors = [cm.Blues_r(0.7 * i / (len(bottom_country_medians) - 1)) for i in range(len(bottom_country_medians))]
    bottom_lines = []
    bottom_labels = []
    
    for idx, (country, median_medals) in enumerate(bottom_country_medians):
        country_data = df_trends[df_trends['Country'] == country].sort_values('Year')
        
        line, = ax2.plot(country_data['Year'], 
                        country_data[metric_col],
                        marker='s', linestyle='--', linewidth=2.5,
                        color=bottom_colors[idx],
                        label=f"{country}: {median_medals:.3f}")
        bottom_lines.append(line)
        bottom_labels.append(f"{country}: {median_medals:.3f}")
    
    # Formatting
    # Add text annotation inside subplot (15 points offset from edges)
    ax_bottom.annotate('Trends', 
                       xy=(0, 1), xycoords='axes fraction',
                       xytext=(15, -15), textcoords='offset points',
                       fontsize=24, weight='bold', ha='left', va='top')
    
    # Set x-axis
    years = sorted(df_trends['Year'].unique())
    ax_bottom.set_xticks(years)
    ax_bottom.set_xticklabels([str(int(y)) for y in years], rotation=45, ha='right', fontsize=18)
    
    # Color y-axis labels
    ax_bottom.tick_params(axis='y', labelcolor='darkred', labelsize=18)
    ax2.tick_params(axis='y', labelcolor='darkblue', labelsize=18)
    
    # Legends with exact alignment - using 'upper left' and 'lower left' 
    # so left edge is at bbox_to_anchor x, and top/bottom edges are at bbox_to_anchor y
    # Use same transform (ax_bottom) for both to ensure consistent positioning
    legend_top = ax_bottom.legend(top_lines, top_labels, loc='upper left', bbox_to_anchor=(1.08, 1.0), 
                                  framealpha=0.95, title='Top Performers', fontsize=14, title_fontsize=14,
                                  borderpad=0.6, labelspacing=0.5, handlelength=2.0, handletextpad=0.8)
    legend_bottom = ax_bottom.legend(bottom_lines, bottom_labels, loc='lower left', bbox_to_anchor=(1.08, 0.0), 
                                     framealpha=0.95, title='Bottom Performers', fontsize=14, title_fontsize=14,
                                     borderpad=0.6, labelspacing=0.5, handlelength=2.0, handletextpad=0.8)
    ax_bottom.add_artist(legend_top)
    
    ax_bottom.grid(True, alpha=0.3)
    
    # Add extra space at top for text annotation
    y1_min, y1_max = ax_bottom.get_ylim()
    y2_min, y2_max = ax2.get_ylim()
    ax_bottom.set_ylim(y1_min, y1_max * 1.08)
    ax2.set_ylim(y2_min, y2_max * 1.08)
    
    # Set fixed width for both legends to ensure perfect alignment
    # 260 points is large enough for longest country names + values
    FIXED_LEGEND_WIDTH = 260
    fig.canvas.draw()
    legend_top.get_frame().set_width(FIXED_LEGEND_WIDTH)
    legend_bottom.get_frame().set_width(FIXED_LEGEND_WIDTH)
    
    # Now position based on fixed width
    fig.canvas.draw()
    bbox_top = legend_top.get_window_extent().transformed(fig.transFigure.inverted())
    legend_right_edge = bbox_top.x1
    legend_left_pos = legend_right_edge - bbox_top.width
    legend_x_axes = (legend_left_pos - bottom_left) / bottom_width
    
    legend_top.set_bbox_to_anchor((legend_x_axes, 1.0), transform=ax_bottom.transAxes)
    legend_bottom.set_bbox_to_anchor((legend_x_axes, 0.0), transform=ax_bottom.transAxes)
    
    # Redraw to get updated positions
    fig.canvas.draw()
    bbox_top = legend_top.get_window_extent().transformed(fig.transFigure.inverted())
    bbox_bottom = legend_bottom.get_window_extent().transformed(fig.transFigure.inverted())
    legend_right_edge = max(bbox_top.x1, bbox_bottom.x1)
    
    # Now reposition top axes with exact alignment to legend right edge
    top_width = (legend_right_edge - bottom_left - gap) / 2
    ax_top_left.set_position([bottom_left, top_bottom, top_width, top_height])
    ax_top_right.set_position([bottom_left + top_width + gap, top_bottom, top_width, top_height])
    
    # Add data source text at bottom left
    data_source = DATA_SOURCES.get(metric_name, 'Data sources vary by metric')
    
    # Calculate coverage: what % of countries with Olympic medals in this time period have this metric data
    # Use year-filtered data as base to ensure consistent denominator across all metrics
    df_year_filtered = df[(df['Year'] >= START_YEAR) & (df['Year'] <= END_YEAR)].copy()
    total_olympic_countries = len(df_year_filtered['Country'].unique())
    
    # For baseline metrics, show data availability before qualification filters
    # For normalized metrics, show how many qualified countries have the normalization data
    if metric_col == medal_type or metric_col == 'Total':
        # Baseline: check data availability for medal_type column
        df_with_medal_data = df_year_filtered.dropna(subset=[medal_type])
        countries_with_data = len(df_with_medal_data['Country'].unique())
    else:
        # Normalized: show qualified countries (after filters)
        countries_with_data = len(df_filtered['Country'].unique())
    
    coverage_pct = (countries_with_data / total_olympic_countries) * 100
    
    coverage_text = f'Trend values show median. Coverage: {countries_with_data}/{total_olympic_countries} medal-winning nations in range ({START_YEAR}-{END_YEAR}) ({coverage_pct:.0f}%). '
    if metric_col == medal_type or metric_col == 'Total':
        if medal_type == 'Total_Athletes':
            coverage_text += f'Bar charts show all {len(recent_df)} countries from {most_recent_year}. Trend lines show all countries with 3+ years.'
        else:
            coverage_text += f'Bar charts show all {len(recent_df)} countries from {most_recent_year}. Trend lines filtered (≥{MIN_PARTICIPATIONS} participations, ≥{MIN_MEDALS} medals, 3+ years).'
    elif metric_name in ['University', 'Sports Stadium', 'Ski Resort', 'Million Kg Coffee', 
                       'Million Cola Servings', '100 Work Hours Per Year', 'Peace Index Point',
                       '1000 Refugees Received', '1000 Refugees Produced', '1000 Military Personnel']:
        coverage_text += '2023-2024 snapshot averaged across all years.'
    elif metric_name in ['100 Sunshine Days', '100 Cm Snowfall', 'Degree Temperature']:
        coverage_text += 'Climate data averaged across space and time.'
    elif metric_name in ['100m Elevation', '1000 Km Coastline', '1000 Square Kilometers']:
        coverage_text += 'Static geographic data.'
    else:
        coverage_text += 'Time-series data where available.'
    
    fig.text(0.08, 0.013, coverage_text,
             ha='left', fontsize=10, style='italic', color='gray')
    
    # Data source line
    if metric_col == 'Total':
        fig.text(0.08, 0.002, f'Data: {data_source}',
                 ha='left', fontsize=11, style='italic', color='gray')
    else:
        fig.text(0.08, 0.002, f'Data: {data_source}. Olympic Medals: Kaggle (1896-2016) & Wikipedia (2018-2024)',
                 ha='left', fontsize=11, style='italic', color='gray')
    
    # Author and date line
    fig.text(0.08, -0.009, 'Prepared by Tanner D. Harms, February 2026',
             ha='left', fontsize=10, style='italic', color='gray')
    
    # Save - use consistent folder naming
    MEDAL_TYPE_FOLDERS = {
        'Total': 'medals_by_event',
        'Individual_Medalists': 'individual_medalists',
        'Total_Medals_Awarded': 'total_medals_awarded',
        'Total_Athletes': 'total_athletes_sent',
        'Medals_Per_Athlete': 'medals_per_athlete_sent',
        'Medals_Awarded_Per_Athlete': 'medals_awarded_per_athlete_sent',
    }
    
    METRIC_FOLDERS = {
        'Baseline': 'baseline',
        'Capita': 'capita',
        'HDI': 'hdi',
        'GDP': 'gdp',
        'GDP Per Capita': 'gdp_per_capita',
        '1000 Square Kilometers': '1000_square_kilometers',
        '1000 Km Coastline': '1000_km_coastline',
        '100m Elevation': '100m_elevation',
        'Degree Temperature': 'degree_temperature',
        '100 Sunshine Days': '100_sunshine_days',
        '100 Cm Snowfall': '100_cm_snowfall',
        'Million Internet Users': 'million_internet_users',
        '1000 Vehicles': '1000_vehicles',
        'University': 'university',
        'Sports Stadium': 'sports_stadium',
        'Ski Resort': 'ski_resort',
        'Pct GDP Healthcare Spending': 'pct_gdp_healthcare_spending',
        'Year Life Expectancy': 'year_life_expectancy',
        '100 Work Hours Per Year': '100_work_hours_per_year',
        'Million Kg Coffee': 'million_kg_coffee',
        'Million Cola Servings': 'million_cola_servings',
        'Peace Index Point': 'peace_index_point',
        '1000 Refugees Received': '1000_refugees_received',
        '1000 Refugees Produced': '1000_refugees_produced',
        'Pct GDP Military Spending': 'pct_gdp_military_spending',
        '1000 Military Personnel': '1000_military_personnel',
        'Pct GDP Education Spending': 'pct_gdp_education_spending',
    }
    
    # Build folder path: plots/{medal_type}/{norm_metric}/
    medal_folder = MEDAL_TYPE_FOLDERS.get(medal_type, medal_type.lower())
    
    # For baseline/unnormalized, use 'baseline' as metric folder
    if metric_col == medal_type or metric_col == 'Total' or metric_name in ['Total Medals (Summer)', 'Total Medals (Winter)']:
        norm_folder = 'baseline'
    else:
        norm_folder = METRIC_FOLDERS.get(metric_name, metric_name.lower().replace(" ", "_").replace("/", "_"))
    
    # Create nested directory structure
    output_dir = PLOTS_DIR / medal_folder / norm_folder
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f'{season.lower()}_summary.png'
    save_plot(fig, output_dir / filename)
    print(f"✓ Saved: {output_dir / filename}")
    plt.close()


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
    
    # Create summary figures for each metric
    for metric_name, metric_col in metrics:
        create_summary_figure(summer_df, 'Summer', metric_name, metric_col)
        create_summary_figure(winter_df, 'Winter', metric_name, metric_col)


if __name__ == '__main__':
    main()
