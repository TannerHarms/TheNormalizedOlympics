"""
Interactive Olympic Normalization Dashboard using Plotly

Allows users to dynamically select:
- Medal type (Total, Individual Medalists, etc.)
- Normalization metric (Baseline, per Capita, per GDP, etc.)
- Year range for trend analysis (minimum 3 Olympics)
- Season (Summer/Winter)

Generates standalone HTML file for web embedding with custom JavaScript controls.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'plots' / 'interactive'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Configuration
MIN_MEDALS = 5
MIN_PARTICIPATIONS = 4

# Mapping from normalization column --> raw data column for context plots
# fmt is Python format spec, used only for reference; JS handles display formatting
NORM_TO_CONTEXT = {
    'Medals_Per_Million': {
        'raw_col': 'Population', 'name': 'Population',
        'source': 'World Bank Open Data (1980-2024)', 'snapshot': False,
    },
    'Medals_Per_HDI': {
        'raw_col': 'HDI', 'name': 'Human Development Index',
        'source': 'UNDP Human Development Reports (1990-2021)', 'snapshot': False,
    },
    'Medals_Per_Billion_GDP': {
        'raw_col': 'GDP', 'name': 'GDP (USD)',
        'source': 'World Bank Open Data (1980-2024)', 'snapshot': False,
    },
    'Medals_Per_GDP_Per_Capita': {
        'raw_col': 'GDP_per_capita', 'name': 'GDP Per Capita (USD)',
        'source': 'World Bank Open Data (1980-2024)', 'snapshot': False,
    },
    'Medals_Per_1000_SqKm': {
        'raw_col': 'Land_Area_SqKm', 'name': 'Land Area (sq km)',
        'source': 'World Bank Open Data (1980-2024)', 'snapshot': False,
    },
    'Medals_Per_1000_Km_Coastline': {
        'raw_col': 'Coastline_Length_Km', 'name': 'Coastline Length (km)',
        'source': 'CIA World Factbook & manually compiled', 'snapshot': True,
    },
    'Medals_Per_100m_Elevation': {
        'raw_col': 'Average_Elevation_Meters', 'name': 'Average Elevation (m)',
        'source': 'CIA World Factbook & Wikipedia', 'snapshot': True,
    },
    'Medals_Per_Degree_Temp': {
        'raw_col': 'Avg_Temperature_C', 'name': 'Average Temperature (deg C)',
        'source': 'World Bank Climate Knowledge Portal', 'snapshot': True,
    },
    'Medals_Per_100_Sunshine_Days': {
        'raw_col': 'Sunshine_Days_Per_Year', 'name': 'Sunshine Days Per Year',
        'source': 'Manually compiled from weather services', 'snapshot': True,
    },
    'Medals_Per_100_Cm_Snowfall': {
        'raw_col': 'Avg_Snowfall_Cm_Per_Year', 'name': 'Average Snowfall (cm/yr)',
        'source': 'Manually compiled from climate data', 'snapshot': True,
    },
    'Medals_Per_Million_Internet_Users': {
        'raw_col': 'Internet_Users_Pct', 'name': 'Internet Users (% of Pop.)',
        'source': 'World Bank Open Data (1990-2024)', 'snapshot': False,
    },
    'Medals_Per_1000_Vehicles': {
        'raw_col': 'Vehicles_Per_1000', 'name': 'Vehicles Per 1000 People',
        'source': 'World Bank Open Data', 'snapshot': False,
    },
    'Medals_Per_University': {
        'raw_col': 'Number_of_Universities', 'name': 'Number of Universities',
        'source': 'UNESCO & manually compiled (2024)', 'snapshot': True,
    },
    'Medals_Per_Stadium': {
        'raw_col': 'Professional_Sports_Stadiums', 'name': 'Professional Sports Stadiums',
        'source': 'Manually compiled (2024)', 'snapshot': True,
    },
    'Medals_Per_Ski_Resort': {
        'raw_col': 'Number_of_Ski_Resorts', 'name': 'Number of Ski Resorts',
        'source': 'Manually compiled (2024)', 'snapshot': True,
    },
    'Medals_Per_Pct_Healthcare_Spending': {
        'raw_col': 'Healthcare_Spending_Pct_GDP', 'name': 'Healthcare Spending (% of GDP)',
        'source': 'World Bank Open Data (2000-2024)', 'snapshot': False,
    },
    'Medals_Per_Year_Life_Expectancy': {
        'raw_col': 'Life_Expectancy_Years', 'name': 'Life Expectancy (years)',
        'source': 'World Bank Open Data (1980-2024)', 'snapshot': False,
    },
    'Medals_Per_100_Work_Hours': {
        'raw_col': 'Avg_Work_Hours_Per_Year', 'name': 'Average Work Hours Per Year',
        'source': 'OECD Statistics (2000-2023)', 'snapshot': True,
    },
    'Medals_Per_Peace_Index_Point': {
        'raw_col': 'Global_Peace_Index_Score', 'name': 'Global Peace Index Score',
        'source': 'Institute for Economics & Peace (2024)', 'snapshot': True,
    },
    'Medals_Per_Pct_Military_Spending': {
        'raw_col': 'Military_Expenditure_Pct_GDP', 'name': 'Military Expenditure (% of GDP)',
        'source': 'World Bank / SIPRI (2000-2023)', 'snapshot': False,
    },
    'Medals_Per_1000_Military_Personnel': {
        'raw_col': 'Active_Military_Personnel_Thousands', 'name': 'Active Military Personnel (thousands)',
        'source': 'IISS Military Balance (2024)', 'snapshot': True,
    },
    'Medals_Per_Pct_Education_Spending': {
        'raw_col': 'Education_Spending_pct_GDP', 'name': 'Education Spending (% of GDP)',
        'source': 'World Bank Open Data (1970-2023)', 'snapshot': False,
    },
    'Per_Athlete_Sent': {
        'raw_col': 'Total_Athletes', 'name': 'Total Athletes Sent',
        'source': 'Olympic Results (1896-2024)', 'snapshot': False,
    },
}

def load_data():
    """Load both summer and winter datasets."""
    print("Loading datasets...")
    summer_df = pd.read_csv(DATA_DIR / 'summer_olympics_all_metrics.csv')
    winter_df = pd.read_csv(DATA_DIR / 'winter_olympics_all_metrics.csv')
    
    # Calculate ratio metrics for both
    for df in [summer_df, winter_df]:
        df['Medals_Per_Athlete'] = df['Total'] / df['Total_Athletes']
        df['Individual_Medalists_Per_Athlete'] = df['Individual_Medalists'] / df['Total_Athletes']
        df['Medals_Awarded_Per_Athlete'] = df['Total_Medals_Awarded'] / df['Total_Athletes']
    
    return summer_df, winter_df

def get_available_olympics(df):
    """Get list of Olympic years."""
    return sorted(df['Year'].unique())

def filter_and_prepare_data(df, medal_col, metric_col, start_year, end_year):
    """Filter data by year range and prepare for plotting."""
    df_filtered = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)].copy()
    
    plot_col = metric_col
    
    # Remove invalid values
    df_filtered = df_filtered[
        df_filtered[plot_col].notna() & 
        np.isfinite(df_filtered[plot_col])
    ]
    # For most metrics, also remove zeros; but for Total_Athletes baseline,
    # keep zero-medal nations so delegation sizes are properly represented.
    # Always exclude rows where Total_Athletes == 0 (country not participating).
    if not (medal_col == 'Total_Athletes' and metric_col == medal_col):
        df_filtered = df_filtered[df_filtered[plot_col] != 0]
    else:
        df_filtered = df_filtered[df_filtered['Total_Athletes'] > 0]
    
    # Apply quality filters for non-baseline normalized metrics
    if metric_col != medal_col and medal_col != 'Total_Athletes':
        participations = df_filtered.groupby('Country')['Year'].transform('count')
        total_medals = df_filtered.groupby('Country')['Total'].transform('sum')
        df_filtered = df_filtered[
            (participations >= MIN_PARTICIPATIONS) &
            (total_medals >= MIN_MEDALS)
        ]
    
    return df_filtered, plot_col


def compute_context_data(df, norm_col):
    """Compute context data for raw normalization metric, per country per year.
    
    Returns per-country per-year values so JS can select by barYear and
    compute min/max range whiskers across the user's year range.
    """
    ctx_info = NORM_TO_CONTEXT.get(norm_col)
    if ctx_info is None:
        return None
    
    raw_col = ctx_info['raw_col']
    if raw_col not in df.columns:
        return None
    
    ctx_df = df.dropna(subset=[raw_col]).copy()
    ctx_df = ctx_df[ctx_df[raw_col] != 0]
    ctx_df = ctx_df[~ctx_df[raw_col].isin([float('inf'), float('-inf')])]
    
    if len(ctx_df) == 0:
        return None
    
    # Build per-country per-year data
    country_year_data = {}
    for _, row in ctx_df.drop_duplicates(subset=['Country', 'Year'], keep='last').iterrows():
        country = row['Country']
        year = str(int(row['Year']))
        val = float(row[raw_col])
        if country not in country_year_data:
            country_year_data[country] = {}
        country_year_data[country][year] = round(val, 4)
    
    # Log scale detection across all values
    all_vals = [v for cd in country_year_data.values() for v in cd.values() if v > 0]
    use_log = False
    if len(all_vals) > 5:
        mx = max(all_vals)
        md = float(np.median(all_vals))
        if md > 0 and mx / md > 10:
            use_log = True
    
    return {
        'type': 'normalization',
        'title': ctx_info['name'],
        'source': ctx_info['source'],
        'is_snapshot': ctx_info.get('snapshot', False),
        'data': country_year_data,
        'use_log': use_log,
    }


def compute_baseline_context_data(df, medal_col):
    """Compute baseline context data: stacked medal breakdown for all countries per year.
    
    Returns per-country per-year [gold, silver, bronze, nomedal, total] arrays so
    JS can render stacked medal bars matching the top bar chart style.
    """
    is_athlete_type = (medal_col == 'Total_Athletes')
    
    df_valid = df.dropna(subset=[medal_col]).copy()
    df_valid = df_valid[df_valid[medal_col] > 0]
    df_valid = df_valid.drop_duplicates(subset=['Country', 'Year'], keep='last')
    
    if len(df_valid) == 0:
        return None
    
    country_year_data = {}
    
    # Map medal_col to per-type breakdown columns
    MEDAL_BREAKDOWN = {
        'Total': ('Gold', 'Silver', 'Bronze'),
        'Total_Medals_Awarded': ('Gold_Awarded', 'Silver_Awarded', 'Bronze_Awarded'),
        'Individual_Medalists': ('Gold_Medalists', 'Silver_Medalists', 'Bronze_Medalists'),
    }
    has_direct_breakdown = (not is_athlete_type) and (medal_col in MEDAL_BREAKDOWN)
    if has_direct_breakdown:
        gold_col, silver_col, bronze_col = MEDAL_BREAKDOWN[medal_col]
        # Check columns actually exist in data
        has_direct_breakdown = all(c in df_valid.columns for c in [gold_col, silver_col, bronze_col])
    
    for _, row in df_valid.iterrows():
        country = row['Country']
        year = str(int(row['Year']))
        
        total_raw = float(row.get('Total', 0) or 0)
        medal_val = float(row[medal_col])
        gold = float(row.get('Gold', 0) or 0)
        silver = float(row.get('Silver', 0) or 0)
        bronze = float(row.get('Bronze', 0) or 0)
        
        if is_athlete_type:
            athletes = float(row.get('Total_Athletes', 0) or 0)
            medalists = float(row.get('Individual_Medalists', 0) or 0)
            if athletes > 0 and total_raw > 0:
                mp = medalists / athletes
                g = medal_val * mp * (gold / total_raw)
                s = medal_val * mp * (silver / total_raw)
                b = medal_val * mp * (bronze / total_raw)
                n = medal_val * (1 - mp)
            elif athletes > 0:
                # Country sent athletes but won no medals — all are non-medalists
                g = s = b = 0
                n = medal_val
            else:
                g = s = b = n = 0
        elif has_direct_breakdown:
            # Use actual per-type columns (exact counts)
            g = float(row.get(gold_col, 0) or 0)
            s = float(row.get(silver_col, 0) or 0)
            b = float(row.get(bronze_col, 0) or 0)
            n = 0
        else:
            if total_raw > 0:
                g = round((gold / total_raw) * medal_val)
                s = round((silver / total_raw) * medal_val)
                b = round((bronze / total_raw) * medal_val)
            else:
                g = s = b = 0
            n = 0
        
        if country not in country_year_data:
            country_year_data[country] = {}
        # [gold, silver, bronze, nomedal, total] -- compact for JSON
        country_year_data[country][year] = [
            round(g, 2), round(s, 2), round(b, 2), round(n, 2), round(medal_val, 2)
        ]
    
    return {
        'type': 'baseline',
        'is_athlete_type': is_athlete_type,
        'data': country_year_data,
        'use_log': False,
    }


def _compute_bar_data_for_year(df_filtered, plot_col, medal_col, year, top_n=10):
    """Compute stacked bar chart data for a specific Olympics year."""
    recent_df = df_filtered[df_filtered['Year'] == year].copy()
    if len(recent_df) == 0:
        return None
    
    metric_vals = recent_df[plot_col]
    has_medals = recent_df['Total'] > 0
    is_athlete_type = (medal_col == 'Total_Athletes')
    
    # Map medal_col to per-type breakdown columns
    MEDAL_BREAKDOWN = {
        'Total': ('Gold', 'Silver', 'Bronze'),
        'Total_Medals_Awarded': ('Gold_Awarded', 'Silver_Awarded', 'Bronze_Awarded'),
        'Individual_Medalists': ('Gold_Medalists', 'Silver_Medalists', 'Bronze_Medalists'),
    }
    
    recent_df['bronze_norm'] = 0.0
    recent_df['silver_norm'] = 0.0
    recent_df['gold_norm'] = 0.0
    recent_df['no_medal_norm'] = 0.0
    
    if is_athlete_type:
        medalist_prop = recent_df['Individual_Medalists'] / recent_df['Total_Athletes']
        no_medal_prop = 1 - medalist_prop
        recent_df.loc[has_medals, 'bronze_norm'] = (
            metric_vals[has_medals] * medalist_prop[has_medals] *
            (recent_df.loc[has_medals, 'Bronze'] / recent_df.loc[has_medals, 'Total'])
        )
        recent_df.loc[has_medals, 'silver_norm'] = (
            metric_vals[has_medals] * medalist_prop[has_medals] *
            (recent_df.loc[has_medals, 'Silver'] / recent_df.loc[has_medals, 'Total'])
        )
        recent_df.loc[has_medals, 'gold_norm'] = (
            metric_vals[has_medals] * medalist_prop[has_medals] *
            (recent_df.loc[has_medals, 'Gold'] / recent_df.loc[has_medals, 'Total'])
        )
        recent_df['no_medal_norm'] = metric_vals * no_medal_prop
    elif medal_col in MEDAL_BREAKDOWN:
        # Use per-type breakdown columns for accurate medal proportions.
        # Formula: (per_type_col / medal_total) * metric_vals
        #   - For baseline (plot_col == medal_col): reduces to per_type_col directly
        #   - For normalized: proportions the normalized value correctly
        gold_col, silver_col, bronze_col = MEDAL_BREAKDOWN[medal_col]
        has_breakdown = gold_col in recent_df.columns
        has_medal_total = recent_df[medal_col] > 0
        can_split = has_medals & has_medal_total
        if has_breakdown:
            recent_df.loc[can_split, 'gold_norm'] = (
                recent_df.loc[can_split, gold_col].fillna(0) /
                recent_df.loc[can_split, medal_col]
            ) * metric_vals[can_split]
            recent_df.loc[can_split, 'silver_norm'] = (
                recent_df.loc[can_split, silver_col].fillna(0) /
                recent_df.loc[can_split, medal_col]
            ) * metric_vals[can_split]
            recent_df.loc[can_split, 'bronze_norm'] = (
                recent_df.loc[can_split, bronze_col].fillna(0) /
                recent_df.loc[can_split, medal_col]
            ) * metric_vals[can_split]
        else:
            # Fallback: ratio split using event-based Gold/Total
            recent_df.loc[has_medals, 'gold_norm'] = (
                (recent_df.loc[has_medals, 'Gold'] / recent_df.loc[has_medals, 'Total']) * metric_vals[has_medals]
            )
            recent_df.loc[has_medals, 'silver_norm'] = (
                (recent_df.loc[has_medals, 'Silver'] / recent_df.loc[has_medals, 'Total']) * metric_vals[has_medals]
            )
            recent_df.loc[has_medals, 'bronze_norm'] = (
                (recent_df.loc[has_medals, 'Bronze'] / recent_df.loc[has_medals, 'Total']) * metric_vals[has_medals]
            )
    else:
        recent_df.loc[has_medals, 'bronze_norm'] = (
            (recent_df.loc[has_medals, 'Bronze'] / recent_df.loc[has_medals, 'Total']) * metric_vals[has_medals]
        )
        recent_df.loc[has_medals, 'silver_norm'] = (
            (recent_df.loc[has_medals, 'Silver'] / recent_df.loc[has_medals, 'Total']) * metric_vals[has_medals]
        )
        recent_df.loc[has_medals, 'gold_norm'] = (
            (recent_df.loc[has_medals, 'Gold'] / recent_df.loc[has_medals, 'Total']) * metric_vals[has_medals]
        )
    
    # Sort by visual bar total (sum of stacked components) so displayed bars
    # are monotonically decreasing.  This matters especially for Individual_Medalists
    # where Gold+Silver+Bronze medalists > unique Individual_Medalists.
    recent_df['_bar_total'] = (
        recent_df['gold_norm'] + recent_df['silver_norm'] +
        recent_df['bronze_norm'] + recent_df['no_medal_norm']
    )
    recent_sorted = recent_df.sort_values('_bar_total', ascending=False)
    top = recent_sorted.head(top_n)
    bottom = recent_sorted.tail(top_n)
    
    return {
        'top_countries': top['Country'].tolist(),
        'top_bronze': [round(float(v), 4) for v in top['bronze_norm'].tolist()],
        'top_silver': [round(float(v), 4) for v in top['silver_norm'].tolist()],
        'top_gold': [round(float(v), 4) for v in top['gold_norm'].tolist()],
        'top_nomedal': [round(float(v), 4) for v in top['no_medal_norm'].tolist()],
        'bottom_countries': bottom['Country'].tolist(),
        'bottom_bronze': [round(float(v), 4) for v in bottom['bronze_norm'].tolist()],
        'bottom_silver': [round(float(v), 4) for v in bottom['silver_norm'].tolist()],
        'bottom_gold': [round(float(v), 4) for v in bottom['gold_norm'].tolist()],
        'bottom_nomedal': [round(float(v), 4) for v in bottom['no_medal_norm'].tolist()],
    }


def compute_plot_data(df, medal_col, metric_col, start_year, end_year):
    """Compute all plot data for a given configuration.
    
    Matches the 3-panel MPL layout: stacked Gold/Silver/Bronze bars for
    top/bottom 10, plus dual-axis trend plot with Reds/Blues colormaps.
    """
    TOP_N = 10
    TOP_N_TRENDS = 6
    
    df_filtered, plot_col = filter_and_prepare_data(df, medal_col, metric_col, start_year, end_year)
    
    if len(df_filtered) == 0:
        return None
    
    is_athlete_type = (medal_col == 'Total_Athletes')
    most_recent_year = df_filtered['Year'].max()
    
    # Compute bar chart data for EVERY available year
    bar_data_by_year = {}
    for year in sorted(df_filtered['Year'].unique()):
        year_data = _compute_bar_data_for_year(df_filtered, plot_col, medal_col, int(year), TOP_N)
        if year_data:
            bar_data_by_year[str(int(year))] = year_data
    
    # --- Trend qualification (matching plot_08 logic) ---
    if medal_col == 'Total_Athletes':
        qualified_countries = df_filtered['Country'].unique()
    else:
        if medal_col in ['Medals_Per_Athlete', 'Medals_Awarded_Per_Athlete']:
            country_total_medals = df_filtered.groupby('Country')['Total'].sum()
        elif medal_col in df_filtered.columns:
            country_total_medals = df_filtered.groupby('Country')[medal_col].sum()
        else:
            country_total_medals = df_filtered.groupby('Country')['Total'].sum()
        qualified_by_medals = country_total_medals[country_total_medals >= MIN_MEDALS].index
        country_participations = df_filtered.groupby('Country')['Year'].nunique()
        qualified_by_parts = country_participations[country_participations >= MIN_PARTICIPATIONS].index
        qualified_countries = qualified_by_medals.intersection(qualified_by_parts)
    
    # Require 3+ data points for meaningful trends
    num_years = df_filtered['Year'].nunique()
    min_req = min(3, num_years)
    country_counts = df_filtered[df_filtered['Country'].isin(qualified_countries)].groupby('Country').size()
    final_trend_countries = country_counts[country_counts >= min_req].index
    df_trends = df_filtered[df_filtered['Country'].isin(final_trend_countries)]
    
    # Get top and bottom trend countries by median metric value
    if len(df_trends) == 0:
        median_metrics = pd.Series(dtype=float)
    else:
        median_metrics = df_trends.groupby('Country')[plot_col].median().sort_values(ascending=False)
    
    top_trend_names = median_metrics.head(TOP_N_TRENDS).index.tolist()
    bottom_trend_names = median_metrics.tail(TOP_N_TRENDS).index.tolist()
    
    # Compute trends sorted by median (matching MPL legend order)
    # Reds colormap for top performers
    red_palette = ['#67000d', '#a50f15', '#cb181d', '#ef3b2c', '#fb6a4a', '#fc9272']
    blue_palette = ['#08306b', '#08519c', '#2171b5', '#4292c6', '#6baed6', '#9ecae1']
    # Brighter variants for dark backgrounds (same hue families, light→dark gradient)
    # Index 0 = most extreme value = lightest/most visible on dark bg
    red_palette_dark = ['#ffb3b3', '#ff8080', '#ff4d4d', '#e02020', '#b31010', '#800a0a']
    blue_palette_dark = ['#b3d4ff', '#80b8ff', '#4d9cff', '#2080e0', '#1060b3', '#0a4080']
    
    top_trends_raw = []
    for country in top_trend_names:
        cd = df_trends[df_trends['Country'] == country].sort_values('Year')
        median_val = cd[plot_col].median()
        top_trends_raw.append((country, float(median_val), cd['Year'].tolist(), cd[plot_col].tolist()))
    top_trends_raw.sort(key=lambda x: x[1], reverse=True)
    
    bottom_trends_raw = []
    for country in bottom_trend_names:
        cd = df_trends[df_trends['Country'] == country].sort_values('Year')
        median_val = cd[plot_col].median()
        bottom_trends_raw.append((country, float(median_val), cd['Year'].tolist(), cd[plot_col].tolist()))
    bottom_trends_raw.sort(key=lambda x: x[1])
    
    top_trend_data = []
    for i, (country, med, yrs, vals) in enumerate(top_trends_raw):
        top_trend_data.append({
            'country': country,
            'median': round(med, 4),
            'years': [int(y) for y in yrs],
            'values': [round(float(v), 4) for v in vals],
            'color': red_palette[i] if i < len(red_palette) else '#fc9272',
            'color_dark': red_palette_dark[i] if i < len(red_palette_dark) else '#ff7777'
        })
    
    bottom_trend_data = []
    for i, (country, med, yrs, vals) in enumerate(bottom_trends_raw):
        bottom_trend_data.append({
            'country': country,
            'median': round(med, 4),
            'years': [int(y) for y in yrs],
            'values': [round(float(v), 4) for v in vals],
            'color': blue_palette[i] if i < len(blue_palette) else '#9ecae1',
            'color_dark': blue_palette_dark[i] if i < len(blue_palette_dark) else '#b3d9ff'
        })
    
    all_trend_years = sorted(df_trends['Year'].unique()) if len(df_trends) > 0 else []
    
    # All qualified country trends for dropdown selection
    all_country_trends = []
    for country in median_metrics.index:
        cd = df_trends[df_trends['Country'] == country].sort_values('Year')
        median_val = cd[plot_col].median()
        all_country_trends.append({
            'country': country,
            'median': round(float(median_val), 4),
            'years': [int(y) for y in cd['Year'].tolist()],
            'values': [round(float(v), 4) for v in cd[plot_col].tolist()],
        })
    all_country_trends.sort(key=lambda x: x['country'])
    
    # Coverage stats
    countries_with_data = len(df_filtered['Country'].unique())
    total_olympic_countries = len(df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]['Country'].unique())
    coverage_pct = int((countries_with_data / total_olympic_countries) * 100) if total_olympic_countries > 0 else 0
    
    return {
        'is_athlete_type': bool(is_athlete_type),
        'bar_data_by_year': bar_data_by_year,
        'top_trends': top_trend_data,
        'bottom_trends': bottom_trend_data,
        'all_country_trends': all_country_trends,
        'all_trend_years': [int(y) for y in all_trend_years],
        'most_recent_year': int(most_recent_year),
        'countries_with_data': int(countries_with_data),
        'total_olympic_countries': int(total_olympic_countries),
        'coverage_pct': int(coverage_pct),
        'num_olympics': int(len(df_filtered['Year'].unique()))
    }

def precompute_all_data(summer_df, winter_df):
    """Precompute data for all valid combinations."""
    # Define medal types (column_name, display_name)
    medal_types = [
        ('Total', 'Medals by Event'),
        ('Individual_Medalists', 'Individual Medalists'),
        ('Total_Medals_Awarded', 'Total Medals Awarded'),
        ('Total_Athletes', 'Total Athletes Sent'),
    ]
    
    # Define normalization metrics: (column_name_or_None, display_name, unit_suffix)
    # NOTE: Normalization columns in the CSV are shared (e.g., Medals_Per_Million)
    # regardless of which medal type is selected. The norm_col IS the metric column.
    norm_metrics = [
        (None, 'Baseline', ''),
        # Core normalization
        ('Medals_Per_Million', 'per Capita', ' per Million People'),
        ('Medals_Per_HDI', 'per HDI', ' per HDI Point'),
        ('Medals_Per_Billion_GDP', 'per GDP', ' per Billion GDP (USD)'),
        ('Medals_Per_GDP_Per_Capita', 'per GDP Per Capita', ' per $1000 GDP Per Capita'),
        # Geographic
        ('Medals_Per_1000_SqKm', 'per 1000 Sq Km', ' per 1000 Sq Km'),
        ('Medals_Per_1000_Km_Coastline', 'per Coastline', ' per 1000 Km Coastline'),
        ('Medals_Per_100m_Elevation', 'per Elevation', ' per 100m Elevation'),
        # Climate
        ('Medals_Per_Degree_Temp', 'per Temperature', ' per Degree Celsius'),
        ('Medals_Per_100_Sunshine_Days', 'per Sunshine', ' per 100 Sunshine Days'),
        ('Medals_Per_100_Cm_Snowfall', 'per Snowfall', ' per 100 Cm Snowfall'),
        # Infrastructure
        ('Medals_Per_Million_Internet_Users', 'per Million Internet Users', ' per Million Internet Users'),
        ('Medals_Per_1000_Vehicles', 'per 1000 Vehicles', ' per 1000 Vehicles'),
        ('Medals_Per_University', 'per University', ' per University'),
        ('Medals_Per_Stadium', 'per Sports Stadium', ' per Sports Stadium'),
        ('Medals_Per_Ski_Resort', 'per Ski Resort', ' per Ski Resort'),
        # Economic/Social
        ('Medals_Per_Pct_Healthcare_Spending', 'per Pct Healthcare Spending', ' per Pct GDP Healthcare'),
        ('Medals_Per_Year_Life_Expectancy', 'per Year Life Expectancy', ' per Year Life Expectancy'),
        ('Medals_Per_100_Work_Hours', 'per 100 Work Hours', ' per 100 Work Hours/Year'),
        # Cultural
        ('Medals_Per_Peace_Index_Point', 'per Peace Index Point', ' per Peace Index Point'),
        # Military
        ('Medals_Per_Pct_Military_Spending', 'per Pct Military Spending', ' per Pct GDP Military'),
        ('Medals_Per_1000_Military_Personnel', 'per 1000 Military Personnel', ' per 1000 Military Personnel'),
        # Education
        ('Medals_Per_Pct_Education_Spending', 'per Pct Education Spending', ' per Pct GDP Education'),
        # Per Athlete (special: column varies by medal type)
        ('Per_Athlete_Sent', 'per Athlete Sent', ' per Athlete Sent'),
    ]
    
    all_data = {}
    context_store = {}  # Separate dict to avoid JSON duplication
    
    print("\nPrecomputing data for all combinations...")
    
    for season_name, df in [('Summer', summer_df), ('Winter', winter_df)]:
        years = get_available_olympics(df)
        print(f"\n{season_name} Olympics: {len(years)} years ({min(years)}-{max(years)})")
        
        # Precompute normalization contexts per (norm_col, season)
        for norm_col, norm_display, norm_unit in norm_metrics:
            if norm_col is not None:
                cache_key = f"{season_name}|{norm_col}"
                if cache_key not in context_store:
                    ctx = compute_context_data(df, norm_col)
                    if ctx:
                        context_store[cache_key] = ctx
        
        # Precompute baseline contexts per (medal_col, season)
        for medal_col, medal_display in medal_types:
            cache_key = f"{season_name}|baseline|{medal_col}"
            if cache_key not in context_store:
                ctx = compute_baseline_context_data(df, medal_col)
                if ctx:
                    context_store[cache_key] = ctx
        
        for medal_col, medal_display in medal_types:
            for norm_col, norm_display, norm_unit in norm_metrics:
                # Determine metric column
                if norm_col is None:
                    # Baseline: use medal column directly
                    metric_col = medal_col
                    full_display = medal_display
                elif norm_col == 'Per_Athlete_Sent':
                    # Special case: per athlete column varies by medal type
                    per_athlete_map = {
                        'Total': 'Medals_Per_Athlete',
                        'Individual_Medalists': 'Individual_Medalists_Per_Athlete',
                        'Total_Medals_Awarded': 'Medals_Awarded_Per_Athlete',
                    }
                    if medal_col not in per_athlete_map:
                        continue  # Skip e.g. Total_Athletes / Total_Athletes = 1
                    metric_col = per_athlete_map[medal_col]
                    full_display = f"{medal_display} {norm_display}"
                else:
                    # Use the shared normalization column directly
                    metric_col = norm_col
                    full_display = f"{medal_display} {norm_display}"
                
                # Check if metric exists in dataframe
                if metric_col not in df.columns:
                    print(f"  - {season_name} | {medal_display} | {norm_display}: Column '{metric_col}' not found")
                    continue
                
                # Key must match JS getDataKey(): season|medalType|normalization
                # For baseline: normalization = medalType; for others: normalization = norm_col
                key_col = medal_col if norm_col is None else norm_col
                key = f"{season_name}|{medal_col}|{key_col}"
                
                try:
                    start_year = min(years)
                    end_year = max(years)
                    data = compute_plot_data(df, medal_col, metric_col, start_year, end_year)
                    
                    if data is None or data['num_olympics'] < 3:
                        print(f"  X {season_name} | {medal_display} | {norm_display}: Insufficient data")
                        continue
                    
                    data['display_name'] = full_display
                    data['unit_suffix'] = norm_unit
                    data['available_years'] = [int(y) for y in years]
                    
                    # Attach context key (not data -- avoids JSON duplication)
                    if norm_col is not None:
                        data['context_key'] = f"{season_name}|{norm_col}"
                    else:
                        data['context_key'] = f"{season_name}|baseline|{medal_col}"
                    
                    all_data[key] = data
                    
                    print(f"  + {season_name} | {medal_display} | {norm_display}: {data['num_olympics']} Olympics")
                    
                except Exception as e:
                    print(f"  X {season_name} | {medal_display} | {norm_display}: {e}")
                    continue
    
    print(f"\nTotal valid combinations: {len(all_data)}")
    print(f"Context store entries: {len(context_store)}")
    return all_data, medal_types, norm_metrics, context_store

def create_html_dashboard(all_data, medal_types, norm_metrics, summer_years, winter_years, context_store):
    """Create standalone HTML file matching the matplotlib summary figure style.
    
    3-panel layout:
    - Top left: Stacked vertical bar chart (Gold/Silver/Bronze) for top 10
    - Top right: Stacked vertical bar chart for bottom 10
    - Bottom: Full-width dual-axis trend plot (Reds for top, Blues for bottom)
    """
    
    # Build dropdown options
    norm_options_html = '<option value="baseline">Baseline (No Normalization)</option>\n'
    for norm_col, display, _ in norm_metrics:
        if norm_col is not None:
            norm_options_html += f'                    <option value="{norm_col}">{display}</option>\n'
    
    medal_options_html = ""
    for col, display in medal_types:
        medal_options_html += f'                    <option value="{col}">{display}</option>\n'
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Interactive Olympic Medal Normalization Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
        :root {{
            --bg: #ffffff;
            --fg: #000000;
            --bg-secondary: #f5f5f5;
            --border: #cccccc;
            --border-input: #999999;
            --input-bg: #ffffff;
            --grid-color: rgba(136,136,136,0.3);
            --axis-line: #000000;
            --annotation-color: #000000;
            --legend-bg: rgba(255,255,255,0.95);
            --legend-border: #000000;
            --bar-outline: #000000;
            --ctx-label: #333333;
            --footer-color: gray;
            --disclaimer-color: #999999;
            --error-bg: #fdecea;
            --error-border: #d32f2f;
            --error-color: #d32f2f;
            --ctx-border: #cccccc;
            --ctx-toggle-bg: #ffffff;
            --ctx-toggle-color: #333333;
            --ctx-toggle-border: #888888;
            --ctx-toggle-hover-bg: #f0f0f0;
            --ctx-toggle-active-bg: #333333;
            --ctx-toggle-active-color: #ffffff;
            --shadow-bar: rgba(0,0,0,0.13);
            --shadow-bar-hover: rgba(0,0,0,0.35);
            --trend-yaxis-left: darkred;
            --trend-yaxis-right: darkblue;
        }}
        body.dark-theme {{
            --bg: #1a1a2e;
            --fg: #e0e0e0;
            --bg-secondary: #16213e;
            --border: #3a3a5c;
            --border-input: #555577;
            --input-bg: #22224a;
            --grid-color: rgba(200,200,200,0.15);
            --axis-line: #888888;
            --annotation-color: #e0e0e0;
            --legend-bg: rgba(26,26,46,0.95);
            --legend-border: #666688;
            --bar-outline: #888888;
            --ctx-label: #bbbbcc;
            --footer-color: #888899;
            --disclaimer-color: #666677;
            --error-bg: #3a1a1a;
            --error-border: #ff5555;
            --error-color: #ff5555;
            --ctx-border: #3a3a5c;
            --ctx-toggle-bg: #22224a;
            --ctx-toggle-color: #bbbbcc;
            --ctx-toggle-border: #555577;
            --ctx-toggle-hover-bg: #2a2a5a;
            --ctx-toggle-active-bg: #5555aa;
            --ctx-toggle-active-color: #ffffff;
            --shadow-bar: rgba(0,0,0,0.35);
            --shadow-bar-hover: rgba(0,0,0,0.6);
            --trend-yaxis-left: #ff6666;
            --trend-yaxis-right: #6699ff;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            font-family: 'Times New Roman', 'DejaVu Serif', Georgia, serif;
            margin: 0;
            padding: 20px;
            background-color: var(--bg);
            color: var(--fg);
            transition: background-color 0.3s, color 0.3s;
        }}
        .dashboard-container {{
            max-width: 1400px;
            margin: 0 auto;
            background: var(--bg);
            padding: 20px 30px 10px 30px;
        }}
        .suptitle {{
            font-size: 32px;
            font-weight: bold;
            color: var(--fg);
            margin: 0 0 20px 0;
            text-align: left;
        }}
        .controls {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
            margin-bottom: 15px;
            padding: 15px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 4px;
        }}
        .control-group {{
            display: flex;
            flex-direction: column;
        }}
        .control-group label {{
            font-weight: bold;
            margin-bottom: 4px;
            font-size: 13px;
            color: var(--fg);
        }}
        select, input[type="number"] {{
            padding: 6px 8px;
            border: 1px solid var(--border-input);
            border-radius: 3px;
            background: var(--input-bg);
            color: var(--fg);
            font-family: 'Times New Roman', serif;
            font-size: 13px;
        }}
        .top-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 5px;
        }}
        .plot-cell {{
            width: 100%;
            height: 480px;
        }}
        #plotTrends {{
            width: 100%;
            height: 520px;
            margin-bottom: 5px;
        }}
        .trend-controls {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 6px 0 10px 0;
            padding: 6px 10px;
            font-family: 'Times New Roman', serif;
            font-size: 14px;
            color: var(--fg);
        }}
        .trend-controls label {{
            font-weight: bold;
            white-space: nowrap;
        }}
        .trend-controls select {{
            padding: 4px 8px;
            border: 1px solid var(--ctx-border);
            border-radius: 4px;
            background: var(--bg);
            color: var(--fg);
            font-family: 'Times New Roman', serif;
            font-size: 13px;
            min-width: 180px;
        }}
        .trend-controls .ctx-toggle {{
            margin-left: 8px;
        }}
        #contextSection {{
            margin-top: 20px;
            border-top: 2px solid var(--ctx-border);
            padding-top: 15px;
        }}
        #contextTitle {{
            font-size: 28px;
            font-weight: bold;
            color: var(--fg);
            margin: 0 0 10px 0;
            text-align: left;
        }}
        #plotContext {{
            width: 100%;
            height: 500px;
            margin-bottom: 5px;
        }}
        .context-footer {{
            font-size: 11px;
            font-style: italic;
            color: var(--footer-color);
            line-height: 1.6;
            margin-top: 3px;
        }}
        .context-header {{
            display: flex;
            align-items: center;
            gap: 18px;
            margin-bottom: 10px;
        }}
        .ctx-toggle {{
            font-family: 'Times New Roman', Georgia, serif;
            font-size: 14px;
            padding: 4px 14px;
            border: 1.5px solid var(--ctx-toggle-border);
            border-radius: 4px;
            background: var(--ctx-toggle-bg);
            cursor: pointer;
            color: var(--ctx-toggle-color);
            transition: background 0.15s, border-color 0.15s, color 0.15s;
        }}
        .ctx-toggle:hover {{ background: var(--ctx-toggle-hover-bg); border-color: #555; }}
        .ctx-toggle.active {{ background: var(--ctx-toggle-active-bg); color: var(--ctx-toggle-active-color); border-color: var(--ctx-toggle-active-bg); }}
        .ctx-rank-input {{
            font-family: 'Times New Roman', Georgia, serif;
            font-size: 14px;
            width: 55px;
            padding: 3px 6px;
            border: 1.5px solid var(--ctx-toggle-border);
            border-radius: 4px;
            text-align: center;
            background: var(--input-bg);
            color: var(--fg);
        }}
        .ctx-rank-label {{
            font-family: 'Times New Roman', Georgia, serif;
            font-size: 14px;
            color: var(--ctx-label);
        }}
        /* Bar drop shadow and hover highlight */
        .trace.bars .point>path {{
            filter: drop-shadow(1px 2px 3px var(--shadow-bar));
            transition: filter 0.15s ease, stroke-width 0.15s ease;
        }}
        .trace.bars .point>path:hover {{
            filter: drop-shadow(2px 3px 7px var(--shadow-bar-hover));
            stroke-width: 2.5px;
        }}
        .footer {{
            font-size: 11px;
            font-style: italic;
            color: var(--footer-color);
            line-height: 1.6;
            margin-top: 5px;
        }}
        #errorBox {{
            display: none;
            padding: 12px;
            background: var(--error-bg);
            border-left: 4px solid var(--error-border);
            margin-bottom: 10px;
            font-weight: bold;
            color: var(--error-color);
        }}
        /* Theme toggle: subtle icon */
        .theme-toggle-wrap {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px;
        }}
        #themeToggle {{
            background: none;
            border: none;
            cursor: pointer;
            font-size: 22px;
            line-height: 1;
            padding: 2px 4px;
            color: var(--ctx-label);
            opacity: 0.6;
            transition: opacity 0.2s, color 0.2s;
            font-family: 'Times New Roman', Georgia, serif;
        }}
        #themeToggle:hover {{
            opacity: 1;
        }}
        /* Plotly modebar icons in dark mode */
        body.dark-theme .modebar-btn path {{
            fill: var(--fg) !important;
        }}
        body.dark-theme .modebar-btn:hover path {{
            fill: #ffffff !important;
        }}
        /* Select dropdown options in dark mode */
        body.dark-theme select option {{
            background: var(--input-bg);
            color: var(--fg);
        }}
        /* Save-PDF button */
        #printBtn {{
            background: none;
            border: none;
            cursor: pointer;
            font-size: 16px;
            line-height: 1;
            padding: 2px 4px;
            color: var(--ctx-label);
            opacity: 0.6;
            transition: opacity 0.2s, color 0.2s;
            font-family: 'Times New Roman', Georgia, serif;
        }}
        #printBtn:hover {{ opacity: 1; }}
        #printBtn.saving {{
            pointer-events: none;
            opacity: 0.3;
        }}
        .footer a {{
            color: var(--ctx-label);
            text-decoration: underline;
            text-underline-offset: 2px;
        }}
        .footer a:hover {{
            opacity: 0.7;
        }}
        /* Data Sources collapsible */
        .data-sources {{
            margin-top: 12px;
            border: 1px solid var(--border);
            border-radius: 4px;
            font-style: normal;
        }}
        .data-sources summary {{
            cursor: pointer;
            padding: 8px 14px;
            font-weight: bold;
            font-size: 13px;
            color: var(--fg);
            background: var(--bg-secondary);
            border-radius: 4px;
            list-style: none;
            user-select: none;
        }}
        .data-sources summary::-webkit-details-marker {{ display: none; }}
        .data-sources summary::before {{
            content: '\\25B6\\FE0E';
            display: inline-block;
            margin-right: 8px;
            font-size: 11px;
            transition: transform 0.2s;
        }}
        .data-sources[open] summary::before {{
            transform: rotate(90deg);
        }}
        .data-sources .ds-body {{
            padding: 14px 18px;
            font-size: 12px;
            line-height: 1.7;
            color: var(--fg);
        }}
        .data-sources .ds-body h3 {{
            font-size: 14px;
            margin: 14px 0 6px 0;
            color: var(--fg);
        }}
        .data-sources .ds-body h3:first-child {{ margin-top: 0; }}
        .data-sources .ds-body table {{
            border-collapse: collapse;
            width: 100%;
            margin: 6px 0 10px 0;
            font-size: 11.5px;
        }}
        .data-sources .ds-body th,
        .data-sources .ds-body td {{
            text-align: left;
            padding: 4px 10px;
            border-bottom: 1px solid var(--border);
        }}
        .data-sources .ds-body th {{
            font-weight: bold;
            background: var(--bg-secondary);
        }}
        .data-sources .ds-body ul {{
            margin: 4px 0 10px 0;
            padding-left: 20px;
        }}
        .data-sources .ds-body li {{ margin-bottom: 3px; }}
        .data-sources .ds-body a {{
            color: var(--ctx-label);
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="theme-toggle-wrap">
            <button id="themeToggle" title="Toggle light/dark theme">&#9789;</button>
            <button id="printBtn" title="Save as PNG">&#128190;</button>
        </div>
        <div class="controls">
            <div class="control-group">
                <label for="season">Season</label>
                <select id="season">
                    <option value="Summer">Summer Olympics</option>
                    <option value="Winter">Winter Olympics</option>
                </select>
            </div>
            <div class="control-group">
                <label for="medalType">Medal Category</label>
                <select id="medalType">
                    {medal_options_html}
                </select>
            </div>
            <div class="control-group">
                <label for="normalization">Normalization</label>
                <select id="normalization">
                    {norm_options_html}
                </select>
            </div>
            <div class="control-group">
                <label for="startYear">Start Year</label>
                <input type="number" id="startYear" min="1896" max="2024" value="{min(summer_years)}" step="4">
            </div>
            <div class="control-group">
                <label for="endYear">End Year</label>
                <input type="number" id="endYear" min="1896" max="2024" value="{max(summer_years)}" step="4">
            </div>
            <div class="control-group">
                <label for="barYear">Bar Chart Year</label>
                <select id="barYear"></select>
            </div>
        </div>
        
        <div id="suptitle" class="suptitle"></div>
        <div id="errorBox"></div>
        
        <div class="top-row">
            <div id="plotTopBars" class="plot-cell"></div>
            <div id="plotBottomBars" class="plot-cell"></div>
        </div>
        <div id="plotTrends"></div>
        <div class="trend-controls">
            <label for="trendCountrySelect">Highlight Nation:</label>
            <select id="trendCountrySelect"><option value="">\u2014 None \u2014</option></select>
            <button id="toggleTopBottom" class="ctx-toggle" title="Toggle top/bottom performer lines">Hide Top/Bottom</button>
        </div>
        
        <div id="contextSection" style="display:none;">
            <div class="context-header">
                <div id="contextTitle"></div>
                <span class="ctx-rank-label">Ranks</span>
                <input type="number" id="ctxRankFrom" class="ctx-rank-input" value="1" min="1" title="Start rank">
                <span class="ctx-rank-label">&ndash;</span>
                <input type="number" id="ctxRankTo" class="ctx-rank-input" value="30" min="1" title="End rank">
                <button id="ctxLogToggle" class="ctx-toggle" title="Toggle logarithmic scale">Log Scale</button>
            </div>
            <div id="plotContext"></div>
            <div class="context-footer">
                <span id="contextSource"></span>
            </div>
        </div>
        
        <div class="footer">
            <span id="coverageText"></span><br>
            <span id="sourceText"></span><br>
            Prepared by <a href="https://substack.com/@tannerharms" target="_blank">Tanner D. Harms</a>, {datetime.now().strftime('%B %d, %Y')}.
            <a href="https://github.com/TannerHarms/TheNormalizedOlympics" target="_blank">View on GitHub</a>.<br><br>
            <span style="font-size:10px; color:var(--disclaimer-color);">Disclaimer: This visualization is provided for informational and educational purposes only. The data is aggregated from publicly available sources and may contain errors, omissions, or inaccuracies. No warranty, express or implied, is made regarding the accuracy, completeness, or reliability of the information presented. The author assumes no liability for any decisions, actions, or consequences arising from the use or interpretation of this content. This is not an official publication of the International Olympic Committee or any affiliated organization.</span>

            <details class="data-sources">
                <summary>Data Sources &amp; Methodology</summary>
                <div class="ds-body">
                    <h3>Olympic Medal Data</h3>
                    <table>
                        <tr><th>Source</th><th>Coverage</th><th>Notes</th></tr>
                        <tr><td><a href="https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results" target="_blank">Kaggle: 120 Years of Olympic History</a></td><td>1896&ndash;2016</td><td>271,116 athlete records (CC0: Public Domain)</td></tr>
                        <tr><td><a href="https://www.olympedia.org/" target="_blank">Olympedia.org</a></td><td>2018&ndash;2026</td><td>Direct scrape of per-country results; cross-checked against official medal tables</td></tr>
                    </table>
                    <p>Medals are deduplicated: team events count once per country, not per athlete. Metrics include total athletes sent, individual medalists, event-level medals, and athlete-level medals awarded.</p>

                    <h3>Normalization Indicators (Time-Series)</h3>
                    <table>
                        <tr><th>Indicator</th><th>Source</th><th>Coverage</th></tr>
                        <tr><td>Population, GDP, GDP per Capita</td><td><a href="https://data.worldbank.org/" target="_blank">World Bank API</a> (CC-BY 4.0)</td><td>1960&ndash;2024, 125 countries</td></tr>
                        <tr><td>Internet Users, Vehicles/1000, Healthcare, Life Expectancy, Labor Force, Land/Surface Area</td><td><a href="https://data.worldbank.org/" target="_blank">World Bank API</a></td><td>1960&ndash;2024 (varies)</td></tr>
                        <tr><td>Human Development Index (HDI)</td><td><a href="https://hdr.undp.org/" target="_blank">UNDP HDR</a> (CC-BY 3.0 IGO)</td><td>1990&ndash;2023</td></tr>
                        <tr><td>Military Expenditure &amp; Personnel</td><td><a href="https://data.worldbank.org/" target="_blank">World Bank</a> (SIPRI/IISS)</td><td>2000&ndash;2023</td></tr>
                        <tr><td>Average Work Hours</td><td><a href="https://data-explorer.oecd.org/" target="_blank">OECD SDMX API</a></td><td>2000&ndash;2023, 45 countries</td></tr>
                        <tr><td>Education Spending (% GDP)</td><td><a href="https://data.worldbank.org/" target="_blank">World Bank</a></td><td>1970&ndash;2023 (sparse)</td></tr>
                    </table>

                    <h3>Normalization Indicators (Static/Snapshot)</h3>
                    <table>
                        <tr><th>Indicator</th><th>Source</th><th>Notes</th></tr>
                        <tr><td>Coastline Length, Average Elevation</td><td>CIA World Factbook, Wikipedia</td><td>85 countries</td></tr>
                        <tr><td>Avg Temperature, Snowfall, Sunshine Days</td><td>World Bank Climate Portal</td><td>53 countries; national averages</td></tr>
                        <tr><td>Universities, Ski Resorts, Stadiums</td><td>UNESCO, manual compilation</td><td>54 countries; 2024 snapshot</td></tr>
                        <tr><td>Global Peace Index</td><td><a href="https://www.visionofhumanity.org/" target="_blank">IEP</a></td><td>GPI 2024; 47 countries</td></tr>
                        <tr><td>Refugees Received/Produced</td><td><a href="https://www.unhcr.org/refugee-statistics/" target="_blank">UNHCR</a></td><td>2023 snapshot; 66 countries</td></tr>
                    </table>

                    <h3>Methodology</h3>
                    <ul>
                        <li><strong>Year matching:</strong> Each Olympic edition is matched to the nearest available year for each country and indicator. For example, 2026 Winter Olympics uses 2024 population data where 2026 is unavailable.</li>
                        <li><strong>Normalization formula:</strong> Medals (or athletes) divided by the selected denominator. For per-capita metrics, results are scaled for readability (e.g., medals per million people).</li>
                        <li><strong>Historical countries:</strong> Soviet Union, Yugoslavia, etc. are mapped to modern successor states using contemporary economic data.</li>
                        <li><strong>Coverage gaps:</strong> Smaller nations often lack data for niche metrics. Coverage ranges from ~24% (ski resorts) to ~99% (population).</li>
                        <li><strong>GDP is in current US dollars,</strong> not PPP or inflation-adjusted.</li>
                    </ul>

                    <h3>Data Limitations</h3>
                    <ul>
                        <li>Snapshot metrics (refugees, peace index, consumption) are applied uniformly across all Olympic years.</li>
                        <li>OECD work-hours data covers only 45 member/partner countries; no data for China, India, or most African nations.</li>
                        <li>Climate and geographic values are national approximations; large countries have wide regional variation.</li>
                        <li>Vehicles per 1000 has very sparse coverage (~2% for recent years).</li>
                    </ul>

                    <p style="margin-top:12px;">Full documentation and all collection scripts are available in the <a href="https://github.com/TannerHarms/TheNormalizedOlympics" target="_blank">GitHub repository</a>.</p>
                </div>
            </details>
        </div>
    </div>
    
    <script>
        var allData = {json.dumps(all_data)};
        var contextStore = {json.dumps(context_store)};
        var summerYears = {json.dumps(summer_years)};
        var winterYears = {json.dumps(winter_years)};
        
        // Shared Plotly layout defaults matching MPL style
        // Theme definitions: direct JS objects for reliable color lookup
        var THEMES = {{
            light: {{
                bg: '#ffffff', fg: '#000000', bgSecondary: '#f5f5f5',
                axisLine: '#000000', annotation: '#000000',
                gridColor: 'rgba(136,136,136,0.3)',
                legendBg: 'rgba(255,255,255,0.95)', legendBorder: '#000000',
                barOutline: '#000000',
                trendLeft: 'darkred', trendRight: 'darkblue'
            }},
            dark: {{
                bg: '#1a1a2e', fg: '#e0e0e0', bgSecondary: '#16213e',
                axisLine: '#888888', annotation: '#e0e0e0',
                gridColor: 'rgba(200,200,200,0.15)',
                legendBg: 'rgba(26,26,46,0.95)', legendBorder: '#666688',
                barOutline: '#555577',
                trendLeft: '#ff6666', trendRight: '#6699ff'
            }}
        }};
        function TH() {{ return document.body.classList.contains('dark-theme') ? THEMES.dark : THEMES.light; }}
        function FONT() {{ var t = TH(); return {{ family: 'Times New Roman, DejaVu Serif, Georgia, serif', color: t.fg }}; }}
        function GRID_STYLE() {{ var t = TH(); return {{ gridcolor: t.gridColor, griddash: 'dash', gridwidth: 0.7, zeroline: false }}; }}
        var MEDAL_COLORS = {{
            Bronze: '#CD7F32', Silver: '#C0C0C0', Gold: '#FFD700', NoMedal: '#36454F'
        }};
        
        function showError(msg) {{
            var box = document.getElementById('errorBox');
            box.style.display = 'block';
            box.textContent = msg;
        }}
        function hideError() {{
            document.getElementById('errorBox').style.display = 'none';
        }}
        
        function getDataKey() {{
            var season = document.getElementById('season').value;
            var medalType = document.getElementById('medalType').value;
            var normalization = document.getElementById('normalization').value;
            var metricCol = (normalization === 'baseline') ? medalType : normalization;
            return season + '|' + medalType + '|' + metricCol;
        }}
        
        function makeStackedBarTraces(countries, bronze, silver, gold, nomedal, isAthlete, showLegend, isNormalized) {{
            var traces = [];
            var legendGroup = showLegend ? 'bars' : 'bars2';
            var barLine = TH().barOutline;
            var mFmt = isNormalized ? '.4g' : (isAthlete ? '.2f' : '.0f');
            if (isAthlete) {{
                traces.push({{
                    x: countries, y: nomedal, type: 'bar', name: 'No Medal',
                    marker: {{ color: MEDAL_COLORS.NoMedal, line: {{ color: barLine, width: 1.5 }} }},
                    legendgroup: legendGroup, showlegend: showLegend,
                    hovertemplate: '<b>%{{x}}</b><br>No Medal: %{{y:.2f}}<extra></extra>'
                }});
            }}
            traces.push({{
                x: countries, y: bronze, type: 'bar', name: 'Bronze',
                marker: {{ color: MEDAL_COLORS.Bronze, line: {{ color: barLine, width: 1.5 }} }},
                legendgroup: legendGroup, showlegend: showLegend,
                hovertemplate: '<b>%{{x}}</b><br>Bronze: %{{y:' + mFmt + '}}<extra></extra>'
            }});
            traces.push({{
                x: countries, y: silver, type: 'bar', name: 'Silver',
                marker: {{ color: MEDAL_COLORS.Silver, line: {{ color: barLine, width: 1.5 }} }},
                legendgroup: legendGroup, showlegend: showLegend,
                hovertemplate: '<b>%{{x}}</b><br>Silver: %{{y:' + mFmt + '}}<extra></extra>'
            }});
            traces.push({{
                x: countries, y: gold, type: 'bar', name: 'Gold',
                marker: {{ color: MEDAL_COLORS.Gold, line: {{ color: barLine, width: 1.5 }} }},
                legendgroup: legendGroup, showlegend: showLegend,
                hovertemplate: '<b>%{{x}}</b><br>Gold: %{{y:' + mFmt + '}}<extra></extra>'
            }});
            return traces;
        }}
        
        // Hover-fade for bar charts: dim bars not at the hovered x-position
        function attachBarHoverFade(divId) {{
            var div = document.getElementById(divId);
            div.on('plotly_hover', function(evtData) {{
                if (!evtData || !evtData.points || !evtData.points.length) return;
                var hoveredX = evtData.points[0].x;
                var gd = div;
                var nTraces = gd.data.length;
                for (var ti = 0; ti < nTraces; ti++) {{
                    var trace = gd.data[ti];
                    if (!trace.x) continue;
                    var opArr = [];
                    for (var xi = 0; xi < trace.x.length; xi++) {{
                        opArr.push(trace.x[xi] === hoveredX ? 1 : 0.25);
                    }}
                    Plotly.restyle(gd, {{ 'marker.opacity': [opArr] }}, [ti]);
                }}
            }});
            div.on('plotly_unhover', function() {{
                var gd = div;
                var nTraces = gd.data.length;
                for (var ti = 0; ti < nTraces; ti++) {{
                    if (!gd.data[ti].x) continue;
                    var ones = gd.data[ti].x.map(function() {{ return 1; }});
                    Plotly.restyle(gd, {{ 'marker.opacity': [ones] }}, [ti]);
                }}
            }});
        }}
        
        // --- Trend plot state (persisted across updatePlot calls) ---
        var _trendData = null;
        var _trendStartYear = 0;
        var _trendEndYear = 9999;
        var _hideTopBottom = false;
        var _trendPlotConfig = null;
        
        function renderTrendPlot() {{
            var data = _trendData;
            if (!data) return;
            var startYear = _trendStartYear;
            var endYear = _trendEndYear;
            var t = TH();
            var _dark = document.body.classList.contains('dark-theme');
            var plotConfig = _trendPlotConfig || {{ displayModeBar: true, displaylogo: false, responsive: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'] }};
            
            var trendTraces = [];
            var numTopBottom = 0;
            
            if (!_hideTopBottom) {{
                // Top performers (Reds, circle markers, solid lines) - left y-axis
                for (var ti = 0; ti < data.top_trends.length; ti++) {{
                    var ct = data.top_trends[ti];
                    var tColor = _dark ? ct.color_dark : ct.color;
                    var tx = [], ty = [];
                    for (var j = 0; j < ct.years.length; j++) {{
                        if (ct.years[j] >= startYear && ct.years[j] <= endYear) {{
                            tx.push(ct.years[j]);
                            ty.push(ct.values[j]);
                        }}
                    }}
                    trendTraces.push({{
                        x: tx, y: ty, type: 'scatter', mode: 'lines+markers',
                        name: ct.country + ': ' + ct.median.toFixed(3),
                        legendgroup: 'top',
                        legendgrouptitle: (ti === 0) ? {{ text: 'Top Performers', font: {{ size: 14, family: FONT().family, color: t.annotation }} }} : undefined,
                        marker: {{ symbol: 'circle', size: 8, color: tColor }},
                        line: {{ color: tColor, width: 2.5, dash: 'solid' }},
                        hovertemplate: '<b>' + ct.country + '</b><br>Year: %{{x}}<br>Value: %{{y:.3f}}<br>Median: ' + ct.median.toFixed(3) + '<extra></extra>'
                    }});
                }}
                
                // Bottom performers (Blues, square markers, dashed lines) - right y-axis
                for (var b = 0; b < data.bottom_trends.length; b++) {{
                    var cb = data.bottom_trends[b];
                    var bColor = _dark ? cb.color_dark : cb.color;
                    var bx = [], by = [];
                    for (var k = 0; k < cb.years.length; k++) {{
                        if (cb.years[k] >= startYear && cb.years[k] <= endYear) {{
                            bx.push(cb.years[k]);
                            by.push(cb.values[k]);
                        }}
                    }}
                    trendTraces.push({{
                        x: bx, y: by, yaxis: 'y2',
                        type: 'scatter', mode: 'lines+markers',
                        name: cb.country + ': ' + cb.median.toFixed(3),
                        legendgroup: 'bottom',
                        legendgrouptitle: (b === 0) ? {{ text: 'Bottom Performers', font: {{ size: 14, family: FONT().family, color: t.annotation }} }} : undefined,
                        marker: {{ symbol: 'square', size: 8, color: bColor }},
                        line: {{ color: bColor, width: 2.5, dash: 'dash' }},
                        hovertemplate: '<b>' + cb.country + '</b><br>Year: %{{x}}<br>Value: %{{y:.3f}}<br>Median: ' + cb.median.toFixed(3) + '<extra></extra>'
                    }});
                }}
                numTopBottom = trendTraces.length;
            }}
            
            // Selected country from dropdown (green line)
            var selectedCountry = document.getElementById('trendCountrySelect').value;
            var selectedTraceIdx = -1;
            if (selectedCountry && data.all_country_trends) {{
                for (var sc = 0; sc < data.all_country_trends.length; sc++) {{
                    if (data.all_country_trends[sc].country === selectedCountry) {{
                        var scData = data.all_country_trends[sc];
                        var sx = [], sy = [];
                        for (var si = 0; si < scData.years.length; si++) {{
                            if (scData.years[si] >= startYear && scData.years[si] <= endYear) {{
                                sx.push(scData.years[si]);
                                sy.push(scData.values[si]);
                            }}
                        }}
                        if (sx.length > 0) {{
                            selectedTraceIdx = trendTraces.length;
                            var greenColor = _dark ? '#44ff88' : '#118833';
                            trendTraces.push({{
                                x: sx, y: sy, type: 'scatter', mode: 'lines+markers',
                                name: scData.country + ': ' + scData.median.toFixed(3),
                                legendgroup: 'selected',
                                legendgrouptitle: {{ text: 'Selected Nation', font: {{ size: 14, family: FONT().family, color: t.annotation }} }},
                                marker: {{ symbol: 'diamond', size: 10, color: greenColor }},
                                line: {{ color: greenColor, width: 3.5, dash: 'solid' }},
                                hovertemplate: '<b>' + scData.country + '</b><br>Year: %{{x}}<br>Value: %{{y:.3f}}<br>Median: ' + scData.median.toFixed(3) + '<extra></extra>'
                            }});
                        }}
                        break;
                    }}
                }}
            }}
            
            // Build x-axis tick values from trend years in selected range
            var tickYears = [];
            for (var ay = 0; ay < data.all_trend_years.length; ay++) {{
                if (data.all_trend_years[ay] >= startYear && data.all_trend_years[ay] <= endYear) {{
                    tickYears.push(data.all_trend_years[ay]);
                }}
            }}
            
            var trendLayout = {{
                font: FONT(),
                margin: {{ l: 80, r: 80, t: 30, b: 80 }},
                plot_bgcolor: 'rgba(0,0,0,0)',
                paper_bgcolor: 'rgba(0,0,0,0)',
                xaxis: {{
                    tickvals: tickYears,
                    ticktext: tickYears.map(function(y) {{ return String(y); }}),
                    tickangle: -45,
                    tickfont: {{ size: 18, family: FONT().family, color: t.fg }},
                    showline: true, linewidth: 1, linecolor: t.axisLine, mirror: true
                }},
                yaxis: {{
                    side: 'left',
                    tickfont: {{ size: 18, color: t.trendLeft, family: FONT().family }},
                    showline: true, linewidth: 1, linecolor: t.axisLine,
                    gridcolor: t.gridColor, griddash: 'dash', gridwidth: 0.7, zeroline: false
                }},
                yaxis2: {{
                    side: 'right', overlaying: 'y',
                    tickfont: {{ size: 18, color: t.trendRight, family: FONT().family }},
                    showline: true, linewidth: 1, linecolor: t.axisLine,
                    zeroline: false, showgrid: false
                }},
                showlegend: true,
                legend: {{
                    x: 1.08, y: 1, xanchor: 'left', yanchor: 'top',
                    bgcolor: t.legendBg,
                    bordercolor: t.legendBorder, borderwidth: 1,
                    font: {{ size: 14, family: FONT().family, color: t.fg }},
                    tracegroupgap: 20,
                    traceorder: 'grouped'
                }},
                hovermode: 'closest',
                annotations: [{{
                    text: '<b>Trends</b>',
                    xref: 'paper', yref: 'paper', x: 0.02, y: 0.98,
                    showarrow: false, xanchor: 'left', yanchor: 'top',
                    font: {{ size: 24, family: FONT().family, color: t.annotation }}
                }}]
            }};
            Plotly.newPlot('plotTrends', trendTraces, trendLayout, plotConfig);
            
            // Line highlighting on hover: dim all other traces, bold the hovered one
            var trendDiv = document.getElementById('plotTrends');
            trendDiv.on('plotly_hover', function(eventData) {{
                var hoveredIndex = eventData.points[0].curveNumber;
                var update = {{}};
                for (var i = 0; i < trendTraces.length; i++) {{
                    if (i === hoveredIndex) {{
                        update['line.width'] = update['line.width'] || [];
                        update['marker.size'] = update['marker.size'] || [];
                        update['opacity'] = update['opacity'] || [];
                        update['line.width'].push(4);
                        update['marker.size'].push(11);
                        update['opacity'].push(1);
                    }} else {{
                        update['line.width'] = update['line.width'] || [];
                        update['marker.size'] = update['marker.size'] || [];
                        update['opacity'] = update['opacity'] || [];
                        update['line.width'].push(1.5);
                        update['marker.size'].push(6);
                        update['opacity'].push(0.2);
                    }}
                }}
                var indices = [];
                for (var idx = 0; idx < trendTraces.length; idx++) indices.push(idx);
                Plotly.restyle(trendDiv, {{
                    'line.width': update['line.width'],
                    'marker.size': update['marker.size'],
                    'opacity': update['opacity']
                }}, indices);
            }});
            trendDiv.on('plotly_unhover', function() {{
                var widths = [], sizes = [], opacities = [];
                for (var i = 0; i < trendTraces.length; i++) {{
                    widths.push(i === selectedTraceIdx ? 3.5 : 2.5);
                    sizes.push(i === selectedTraceIdx ? 10 : 8);
                    opacities.push(1);
                }}
                var indices = [];
                for (var idx = 0; idx < trendTraces.length; idx++) indices.push(idx);
                Plotly.restyle(trendDiv, {{
                    'line.width': widths,
                    'marker.size': sizes,
                    'opacity': opacities
                }}, indices);
            }});
            
            // Legend hover highlighting
            (function attachLegendHover() {{
                var legendItems = trendDiv.querySelectorAll('.legend .traces');
                var numTraces = trendTraces.length;
                
                function highlightTrace(hoveredIdx) {{
                    var update = {{ 'line.width': [], 'marker.size': [], 'opacity': [] }};
                    for (var i = 0; i < numTraces; i++) {{
                        if (i === hoveredIdx) {{
                            update['line.width'].push(4);
                            update['marker.size'].push(11);
                            update['opacity'].push(1);
                        }} else {{
                            update['line.width'].push(1.5);
                            update['marker.size'].push(6);
                            update['opacity'].push(0.2);
                        }}
                    }}
                    var indices = [];
                    for (var idx = 0; idx < numTraces; idx++) indices.push(idx);
                    Plotly.restyle(trendDiv, update, indices);
                }}
                
                function resetTraces() {{
                    var widths = [], sizes = [], opacities = [];
                    for (var i = 0; i < numTraces; i++) {{
                        widths.push(i === selectedTraceIdx ? 3.5 : 2.5);
                        sizes.push(i === selectedTraceIdx ? 10 : 8);
                        opacities.push(1);
                    }}
                    var indices = [];
                    for (var idx = 0; idx < numTraces; idx++) indices.push(idx);
                    Plotly.restyle(trendDiv, {{ 'line.width': widths, 'marker.size': sizes, 'opacity': opacities }}, indices);
                }}
                
                for (var li = 0; li < legendItems.length; li++) {{
                    (function(idx) {{
                        legendItems[idx].addEventListener('mouseenter', function() {{ highlightTrace(idx); }});
                        legendItems[idx].addEventListener('mouseleave', function() {{ resetTraces(); }});
                    }})(li);
                }}
            }})();
        }}
        
        function updatePlot() {{
            try {{
                hideError();
                if (typeof Plotly === 'undefined') {{
                    showError('Plotly library failed to load. Check your internet connection and refresh.');
                    return;
                }}
                
                var t = TH();
                
                var key = getDataKey();
                var data = allData[key];
                
                if (!data) {{
                    var mt = document.getElementById('medalType').value;
                    var nm = document.getElementById('normalization').value;
                    if ((mt === 'Medals_Per_Athlete' || mt === 'Medals_Awarded_Per_Athlete') && nm !== 'baseline') {{
                        showError('Ratio metrics (per athlete) cannot be further normalized. Select Baseline.');
                    }} else {{
                        showError('No data available for this combination.');
                    }}
                    Plotly.purge('plotTopBars');
                    Plotly.purge('plotBottomBars');
                    Plotly.purge('plotTrends');
                    document.getElementById('suptitle').textContent = '';
                    return;
                }}
                
                var startYear = parseInt(document.getElementById('startYear').value);
                var endYear = parseInt(document.getElementById('endYear').value);
                var years = [];
                for (var yi = 0; yi < data.available_years.length; yi++) {{
                    if (data.available_years[yi] >= startYear && data.available_years[yi] <= endYear) {{
                        years.push(data.available_years[yi]);
                    }}
                }}
                if (years.length < 3) {{
                    showError('Please select a range with at least 3 Olympics.');
                    return;
                }}
                
                // Suptitle matching MPL style
                document.getElementById('suptitle').textContent = 
                    document.getElementById('season').value + ' Olympics ' + data.display_name;
                
                // Populate bar year dropdown from available years with bar data
                var barYearSelect = document.getElementById('barYear');
                var availableBarYears = Object.keys(data.bar_data_by_year).map(Number).sort(function(a,b){{ return a-b; }});
                var prevBarYear = barYearSelect.value ? parseInt(barYearSelect.value) : null;
                barYearSelect.innerHTML = '';
                for (var by = 0; by < availableBarYears.length; by++) {{
                    var opt = document.createElement('option');
                    opt.value = String(availableBarYears[by]);
                    opt.textContent = String(availableBarYears[by]);
                    barYearSelect.appendChild(opt);
                }}
                // Default to previous selection if still valid, else most recent
                if (prevBarYear && data.bar_data_by_year[String(prevBarYear)]) {{
                    barYearSelect.value = String(prevBarYear);
                }} else {{
                    barYearSelect.value = String(data.most_recent_year);
                }}
                var selectedBarYear = barYearSelect.value;
                var barData = data.bar_data_by_year[selectedBarYear];
                
                if (!barData) {{
                    showError('No bar chart data for year ' + selectedBarYear);
                    return;
                }}
                
                var plotConfig = {{ displayModeBar: true, displaylogo: false, responsive: true,
                    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'] }};
                
                // ---- Top bars: Top Performers ----
                var isNorm = document.getElementById('normalization').value !== 'baseline';
                var topTraces = makeStackedBarTraces(
                    barData.top_countries, barData.top_bronze, barData.top_silver,
                    barData.top_gold, barData.top_nomedal, data.is_athlete_type, false, isNorm
                );
                var topLayout = {{
                    barmode: 'stack',
                    font: FONT(),
                    margin: {{ l: 70, r: 15, t: 30, b: 120 }},
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    xaxis: {{
                        tickangle: -45,
                        tickfont: {{ size: 18, family: FONT().family, color: t.fg }},
                        showline: true, linewidth: 1, linecolor: t.axisLine, mirror: true,
                        showgrid: false
                    }},
                    yaxis: Object.assign({{
                        showline: true, linewidth: 1, linecolor: t.axisLine, mirror: true,
                        tickfont: {{ size: 18, color: t.fg }}
                    }}, GRID_STYLE()),
                    showlegend: false,
                    annotations: [{{
                        text: '<b>Top Performers ' + selectedBarYear + '</b>',
                        xref: 'paper', yref: 'paper', x: 0.98, y: 0.98,
                        showarrow: false, xanchor: 'right', yanchor: 'top',
                        font: {{ size: 24, family: FONT().family, color: t.annotation }}
                    }}]
                }};
                Plotly.newPlot('plotTopBars', topTraces, topLayout, plotConfig);
                attachBarHoverFade('plotTopBars');
                
                // ---- Bottom bars: Bottom Performers ----
                var botTraces = makeStackedBarTraces(
                    barData.bottom_countries, barData.bottom_bronze, barData.bottom_silver,
                    barData.bottom_gold, barData.bottom_nomedal, data.is_athlete_type, false, isNorm
                );
                var botLayout = {{
                    barmode: 'stack',
                    font: FONT(),
                    margin: {{ l: 70, r: 15, t: 30, b: 120 }},
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    xaxis: {{
                        tickangle: -45,
                        tickfont: {{ size: 18, family: FONT().family, color: t.fg }},
                        showline: true, linewidth: 1, linecolor: t.axisLine, mirror: true,
                        showgrid: false
                    }},
                    yaxis: Object.assign({{
                        showline: true, linewidth: 1, linecolor: t.axisLine, mirror: true,
                        tickfont: {{ size: 18, color: t.fg }}
                    }}, GRID_STYLE()),
                    showlegend: false,
                    annotations: [{{
                        text: '<b>Bottom Performers ' + selectedBarYear + '</b>',
                        xref: 'paper', yref: 'paper', x: 0.98, y: 0.98,
                        showarrow: false, xanchor: 'right', yanchor: 'top',
                        font: {{ size: 24, family: FONT().family, color: t.annotation }}
                    }}]
                }};
                Plotly.newPlot('plotBottomBars', botTraces, botLayout, plotConfig);
                attachBarHoverFade('plotBottomBars');
                
                // ---- Trend plot: store state and render ----
                _trendData = data;
                _trendStartYear = startYear;
                _trendEndYear = endYear;
                _trendPlotConfig = plotConfig;
                
                // Populate nation dropdown (preserve selection if still valid)
                var trendSelect = document.getElementById('trendCountrySelect');
                var prevSelected = trendSelect.value;
                trendSelect.innerHTML = '<option value="">\u2014 None \u2014</option>';
                if (data.all_country_trends) {{
                    for (var ci = 0; ci < data.all_country_trends.length; ci++) {{
                        var opt = document.createElement('option');
                        opt.value = data.all_country_trends[ci].country;
                        opt.textContent = data.all_country_trends[ci].country;
                        trendSelect.appendChild(opt);
                    }}
                }}
                // Restore previous selection if country still exists in list
                if (prevSelected) {{
                    for (var ri = 0; ri < trendSelect.options.length; ri++) {{
                        if (trendSelect.options[ri].value === prevSelected) {{
                            trendSelect.value = prevSelected;
                            break;
                        }}
                    }}
                }}
                
                // Update toggle button text
                var togBtn = document.getElementById('toggleTopBottom');
                togBtn.textContent = _hideTopBottom ? 'Show Top/Bottom' : 'Hide Top/Bottom';
                if (_hideTopBottom) togBtn.classList.add('active');
                else togBtn.classList.remove('active');
                
                renderTrendPlot();
                
                // ---- Context plot: baseline medal bars or raw normalization metric ----
                var ctxSection = document.getElementById('contextSection');
                var ctxKey = data.context_key;
                var ctx = ctxKey ? contextStore[ctxKey] : null;
                
                if (ctx) {{
                    ctxSection.style.display = 'block';
                    var ctxYear = String(selectedBarYear);
                    var logBtn = document.getElementById('ctxLogToggle');
                    var useLog = logBtn.classList.contains('active');
                    var rankFrom = parseInt(document.getElementById('ctxRankFrom').value) || 1;
                    var rankTo = parseInt(document.getElementById('ctxRankTo').value) || 30;
                    if (rankFrom < 1) rankFrom = 1;
                    if (rankTo < rankFrom) rankTo = rankFrom;
                    
                    // Earth-tone palette for normalization bars
                    var EARTH = [
                        '#C97B6B','#CE8673','#D4917A','#D99C82','#DEA78C',
                        '#DDB293','#DDBE93','#D8C49A','#D3C9A0','#CBCAA1',
                        '#BDC9A3','#B2C7A7','#A7C5AB','#9CC2B0','#93BEB5',
                        '#8BB9BA','#83B4BF','#7EAEC1','#7BA7C2','#7BA7C2'
                    ];
                    
                    var ctxTraces = [];
                    var ctxTitle = '';
                    var ctxSource = '';
                    var yAxisTitle = '';
                    var isStacked = false;
                    var nTotal = 0;
                    
                    if (ctx.type === 'baseline') {{
                        isStacked = true;
                        var countries = [], golds = [], silvers = [], bronzes = [];
                        var nomedals = [], totals = [];
                        
                        for (var country in ctx.data) {{
                            var cd = ctx.data[country];
                            if (cd[ctxYear]) {{
                                var d = cd[ctxYear]; // [g, s, b, n, t]
                                countries.push(country);
                                golds.push(d[0]);
                                silvers.push(d[1]);
                                bronzes.push(d[2]);
                                nomedals.push(d[3]);
                                totals.push(d[4]);
                            }}
                        }}
                        
                        // Sort descending by total
                        var idx = totals.map(function(v,i){{ return i; }});
                        idx.sort(function(a,b){{ return totals[b] - totals[a]; }});
                        nTotal = idx.length;
                        
                        // Apply rank slice (1-based)
                        var lo = Math.max(0, rankFrom - 1);
                        var hi = Math.min(nTotal, rankTo);
                        idx = idx.slice(lo, hi);
                        
                        var sC = idx.map(function(i){{ return countries[i]; }});
                        var sG = idx.map(function(i){{ return golds[i]; }});
                        var sS = idx.map(function(i){{ return silvers[i]; }});
                        var sB = idx.map(function(i){{ return bronzes[i]; }});
                        var sN = idx.map(function(i){{ return nomedals[i]; }});
                        
                        if (ctx.is_athlete_type) {{
                            ctxTraces.push({{
                                x: sC, y: sN, type: 'bar', name: 'No Medal',
                                marker: {{ color: MEDAL_COLORS.NoMedal, line: {{ color: t.barOutline, width: 0.8 }} }},
                                hovertemplate: '<b>%{{x}}</b><br>No Medal: %{{y:.2f}}<extra></extra>',
                                legendgroup: 'ctx', showlegend: true
                            }});
                        }}
                        var hFmt = ctx.is_athlete_type ? '.2f' : '.0f';
                        ctxTraces.push({{
                            x: sC, y: sB, type: 'bar', name: 'Bronze',
                            marker: {{ color: MEDAL_COLORS.Bronze, line: {{ color: t.barOutline, width: 0.8 }} }},
                            hovertemplate: '<b>%{{x}}</b><br>Bronze: %{{y:' + hFmt + '}}<extra></extra>',
                            legendgroup: 'ctx', showlegend: true
                        }});
                        ctxTraces.push({{
                            x: sC, y: sS, type: 'bar', name: 'Silver',
                            marker: {{ color: MEDAL_COLORS.Silver, line: {{ color: t.barOutline, width: 0.8 }} }},
                            hovertemplate: '<b>%{{x}}</b><br>Silver: %{{y:' + hFmt + '}}<extra></extra>',
                            legendgroup: 'ctx', showlegend: true
                        }});
                        ctxTraces.push({{
                            x: sC, y: sG, type: 'bar', name: 'Gold',
                            marker: {{ color: MEDAL_COLORS.Gold, line: {{ color: t.barOutline, width: 0.8 }} }},
                            hovertemplate: '<b>%{{x}}</b><br>Gold: %{{y:' + hFmt + '}}<extra></extra>',
                            legendgroup: 'ctx', showlegend: true
                        }});
                        
                        ctxTitle = data.display_name + ' \u2014 Ranks ' + rankFrom + '\u2013' + Math.min(rankTo, nTotal) + ' of ' + nTotal + ' (' + ctxYear + ')';
                        yAxisTitle = data.display_name;
                        ctxSource = 'Olympic Medals: Kaggle (1896-2016) & Olympedia.org (2018-2026). Year shown: ' + ctxYear + '.';
                        
                    }} else {{
                        // Normalization context: earth-tone bars for raw metric
                        var countries = [], values = [];
                        
                        for (var country in ctx.data) {{
                            var cd = ctx.data[country];
                            if (cd[ctxYear] !== undefined) {{
                                countries.push(country);
                                values.push(cd[ctxYear]);
                            }}
                        }}
                        
                        // Sort descending
                        var idx = values.map(function(v,i){{ return i; }});
                        idx.sort(function(a,b){{ return values[b] - values[a]; }});
                        nTotal = idx.length;
                        
                        // Apply rank slice
                        var lo = Math.max(0, rankFrom - 1);
                        var hi = Math.min(nTotal, rankTo);
                        idx = idx.slice(lo, hi);
                        
                        var sC = idx.map(function(i){{ return countries[i]; }});
                        var sV = idx.map(function(i){{ return values[i]; }});
                        
                        // Earth-tone colors by position in slice
                        var sColors = sC.map(function(c, i) {{
                            var ci = Math.round(i * (EARTH.length - 1) / Math.max(sC.length - 1, 1));
                            return EARTH[ci];
                        }});
                        
                        ctxTraces.push({{
                            x: sC, y: sV, type: 'bar',
                            marker: {{ color: sColors, line: {{ color: t.barOutline, width: 0.8 }} }},
                            hovertemplate: '<b>%{{x}}</b><br>' + ctx.title + ': %{{y:,.2f}}<extra></extra>',
                            showlegend: false
                        }});
                        
                        ctxTitle = ctx.title + ' \u2014 Ranks ' + rankFrom + '\u2013' + Math.min(rankTo, nTotal) + ' of ' + nTotal + ' (' + ctxYear + ')';
                        yAxisTitle = ctx.title;
                        ctxSource = ctx.source + '. Year shown: ' + ctxYear + '.';
                    }}
                    
                    document.getElementById('contextTitle').textContent = ctxTitle;
                    
                    // Auto-detect log if not manually toggled
                    if (!logBtn.dataset.userSet) {{
                        logBtn.classList.toggle('active', ctx.use_log);
                        useLog = ctx.use_log;
                    }}
                    
                    // Update rank max hint
                    document.getElementById('ctxRankTo').max = nTotal;
                    document.getElementById('ctxRankFrom').max = nTotal;
                    
                    var ctxLayout = {{
                        barmode: isStacked ? 'stack' : undefined,
                        font: FONT(),
                        margin: {{ l: 80, r: 20, t: 30, b: 120 }},
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        xaxis: {{
                            tickangle: -55,
                            tickfont: {{ size: 13, family: FONT().family, color: t.fg }},
                            showline: true, linewidth: 1, linecolor: t.axisLine, mirror: true,
                            showgrid: false
                        }},
                        yaxis: {{
                            title: {{ text: yAxisTitle, font: {{ size: 18, family: FONT().family, color: t.fg }} }},
                            type: useLog ? 'log' : 'linear',
                            showline: true, linewidth: 1, linecolor: t.axisLine, mirror: true,
                            tickfont: {{ size: 14, color: t.fg }},
                            gridcolor: t.gridColor, griddash: 'dash', gridwidth: 0.7,
                            zeroline: false
                        }},
                        showlegend: isStacked,
                        legend: {{ x: 0.98, y: 0.98, xanchor: 'right', yanchor: 'top',
                                   font: {{ size: 14, family: FONT().family, color: t.fg }} }}
                    }};
                    Plotly.newPlot('plotContext', ctxTraces, ctxLayout, plotConfig);
                    attachBarHoverFade('plotContext');
                    
                    document.getElementById('contextSource').textContent = ctxSource;
                }} else {{
                    ctxSection.style.display = 'none';
                    Plotly.purge('plotContext');
                }}
                
                // Update footer text
                var numOlympics = years.length;
                var minY = Math.min.apply(null, years);
                var maxY = Math.max.apply(null, years);
                document.getElementById('coverageText').textContent = 
                    'Trend values show median. Coverage: ' + data.countries_with_data + '/' + 
                    data.total_olympic_countries + ' participating nations in range (' + 
                    minY + '-' + maxY + ') (' + data.coverage_pct + '%). ' +
                    'Bar charts show top/bottom 10 from ' + selectedBarYear + '.';
                document.getElementById('sourceText').textContent = 
                    'Olympic Medals: Kaggle (1896-2016) & Olympedia.org (2018-2026).';
                    
            }} catch (e) {{
                showError('Error rendering plots: ' + e.message);
                console.error('Dashboard error:', e);
            }}
        }}
        
        function updateYearOptions() {{
            var season = document.getElementById('season').value;
            var years = season === 'Summer' ? summerYears : winterYears;
            var minY = Math.min.apply(null, years);
            var maxY = Math.max.apply(null, years);
            document.getElementById('startYear').min = minY;
            document.getElementById('startYear').max = maxY;
            document.getElementById('startYear').value = minY;
            document.getElementById('endYear').min = minY;
            document.getElementById('endYear').max = maxY;
            document.getElementById('endYear').value = maxY;
        }}
        
        // Event listeners
        document.getElementById('season').addEventListener('change', function() {{
            updateYearOptions();
            updatePlot();
        }});
        document.getElementById('medalType').addEventListener('change', updatePlot);
        document.getElementById('normalization').addEventListener('change', updatePlot);
        document.getElementById('startYear').addEventListener('change', updatePlot);
        document.getElementById('endYear').addEventListener('change', updatePlot);
        document.getElementById('barYear').addEventListener('change', updatePlot);
        document.getElementById('ctxLogToggle').addEventListener('click', function() {{
            this.classList.toggle('active');
            this.dataset.userSet = '1';
            updatePlot();
        }});
        document.getElementById('ctxRankFrom').addEventListener('change', updatePlot);
        document.getElementById('ctxRankTo').addEventListener('change', updatePlot);
        // Trend controls: nation dropdown and top/bottom toggle
        document.getElementById('trendCountrySelect').addEventListener('change', function() {{
            renderTrendPlot();
        }});
        document.getElementById('toggleTopBottom').addEventListener('click', function() {{
            _hideTopBottom = !_hideTopBottom;
            this.textContent = _hideTopBottom ? 'Show Top/Bottom' : 'Hide Top/Bottom';
            if (_hideTopBottom) this.classList.add('active');
            else this.classList.remove('active');
            renderTrendPlot();
        }});
        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', function() {{
            document.body.classList.toggle('dark-theme');
            var dark = document.body.classList.contains('dark-theme');
            this.innerHTML = dark ? '&#9788;' : '&#9789;';
            updatePlot();
        }});
        // Save as PDF
        document.getElementById('printBtn').addEventListener('click', function() {{
            var btn = this;
            if (btn.classList.contains('saving')) return;
            btn.classList.add('saving');
            var origText = btn.innerHTML;
            btn.innerHTML = '&#8987;';

            var container = document.querySelector('.dashboard-container');
            // Hide controls and modebar for clean capture
            var controls = document.querySelector('.controls');
            var toggleWrap = document.querySelector('.theme-toggle-wrap');
            var modebars = document.querySelectorAll('.modebar-container');
            var ctxBtns = document.querySelectorAll('.context-header button, .context-header input, .ctx-rank-label');
            var trendCtrls = document.querySelector('.trend-controls');
            controls.style.display = 'none';
            toggleWrap.style.display = 'none';
            modebars.forEach(function(m) {{ m.style.display = 'none'; }});
            ctxBtns.forEach(function(el) {{ el.style.display = 'none'; }});
            if (trendCtrls) trendCtrls.style.display = 'none';

            // Force light theme for PDF
            var wasDark = document.body.classList.contains('dark-theme');
            if (wasDark) {{
                document.body.classList.remove('dark-theme');
                updatePlot();
            }}

            // Small delay to let Plotly re-render in light mode
            setTimeout(function() {{
                html2canvas(container, {{
                    scale: 2,
                    useCORS: true,
                    backgroundColor: '#ffffff',
                    logging: false
                }}).then(function(canvas) {{
                    // Build filename from current selections
                    var season = document.getElementById('season').value;
                    var medal = document.getElementById('medalType').options[document.getElementById('medalType').selectedIndex].text;
                    var norm = document.getElementById('normalization').options[document.getElementById('normalization').selectedIndex].text;
                    var fname = (season + '_' + medal + '_' + norm).replace(/[^a-zA-Z0-9]+/g, '_').replace(/_+/g, '_').replace(/^_|_$/g, '') + '.png';

                    var link = document.createElement('a');
                    link.download = fname;
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                }}).catch(function(err) {{
                    console.error('PNG export failed:', err);
                    alert('PNG export failed. See console for details.');
                }}).finally(function() {{
                    // Restore UI
                    controls.style.display = '';
                    toggleWrap.style.display = '';
                    modebars.forEach(function(m) {{ m.style.display = ''; }});
                    ctxBtns.forEach(function(el) {{ el.style.display = ''; }});
                    if (trendCtrls) trendCtrls.style.display = '';
                    if (wasDark) {{
                        document.body.classList.add('dark-theme');
                        updatePlot();
                    }}
                    btn.innerHTML = origText;
                    btn.classList.remove('saving');
                }});
            }}, wasDark ? 600 : 100);
        }});
        // Reset log toggle user override when metric changes
        document.getElementById('normalization').addEventListener('change', function() {{
            document.getElementById('ctxLogToggle').dataset.userSet = '';
        }});
        document.getElementById('medalType').addEventListener('change', function() {{
            document.getElementById('ctxLogToggle').dataset.userSet = '';
        }});
        
        // Render on load
        if (typeof Plotly !== 'undefined') {{
            updatePlot();
        }} else {{
            window.addEventListener('load', function() {{
                if (typeof Plotly !== 'undefined') {{ updatePlot(); }}
                else {{ showError('Plotly library failed to load. Check internet connection and refresh.'); }}
            }});
        }}
    </script>
</body>
</html>"""
    
    return html_content

def main():
    """Generate interactive dashboard."""
    print("="*70)
    print("INTERACTIVE OLYMPIC DASHBOARD GENERATOR")
    print("="*70)
    
    # Load data
    summer_df, winter_df = load_data()
    
    # Get available years
    summer_years = get_available_olympics(summer_df)
    winter_years = get_available_olympics(winter_df)
    
    # Precompute all data
    all_data, medal_types, norm_metrics, context_store = precompute_all_data(summer_df, winter_df)
    
    if not all_data:
        print("\n[ERROR] No valid data combinations found!")
        return
    
    # Create HTML dashboard
    print("\n" + "="*70)
    print("GENERATING HTML DASHBOARD")
    print("="*70)
    
    # Convert numpy types to native Python types for JSON serialization
    summer_years_py = [int(y) for y in summer_years]
    winter_years_py = [int(y) for y in winter_years]
    
    html_content = create_html_dashboard(all_data, medal_types, norm_metrics, summer_years_py, winter_years_py, context_store)
    
    # Save HTML file
    output_file = OUTPUT_DIR / 'olympic_dashboard.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n[SUCCESS] Interactive dashboard saved!")
    print(f"[FILE] Location: {output_file.absolute()}")
    print(f"[DATA] Combinations: {len(all_data)} valid metric combinations")
    print(f"\n[WEB] Open in browser:")
    print(f"   file:///{output_file.absolute()}")
    print(f"\n[EMBED] To embed on website:")
    print(f"   <iframe src=\"your-url/olympic_dashboard.html\"")
    print(f"           width=\"100%\" height=\"1000px\"")
    print(f"           frameborder=\"0\"></iframe>")
    print("\n" + "="*70)

if __name__ == '__main__':
    main()
