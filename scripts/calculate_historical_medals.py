"""
Calculate historical Olympic medal totals for each country.

This creates cumulative medal counts (all-time totals up to each Olympic year)
to analyze whether past Olympic success correlates with future performance.

Hypothesis: Countries with strong Olympic traditions may have better infrastructure,
coaching, and culture that perpetuates success.
"""

import pandas as pd
from pathlib import Path

def calculate_historical_totals(df, season):
    """
    Calculate cumulative medal totals up to each year.
    
    Args:
        df: Olympic medal data (Year, Country, Gold, Silver, Bronze, Total)
        season: 'Summer' or 'Winter'
    
    Returns:
        DataFrame with historical totals added
    """
    print(f"Calculating historical totals for {season} Olympics...")
    
    df = df.copy()
    df = df.sort_values(['Country', 'Year'])
    
    # Initialize historical columns
    df['Historical_Gold'] = 0
    df['Historical_Silver'] = 0
    df['Historical_Bronze'] = 0
    df['Historical_Total'] = 0
    
    # For each country, calculate cumulative totals
    for country in df['Country'].unique():
        country_mask = df['Country'] == country
        country_data = df[country_mask].copy()
        
        # Calculate cumulative sum (excluding current year)
        cumsum_gold = country_data['Gold'].shift(1, fill_value=0).cumsum()
        cumsum_silver = country_data['Silver'].shift(1, fill_value=0).cumsum()
        cumsum_bronze = country_data['Bronze'].shift(1, fill_value=0).cumsum()
        cumsum_total = country_data['Total'].shift(1, fill_value=0).cumsum()
        
        # Update the dataframe
        df.loc[country_mask, 'Historical_Gold'] = cumsum_gold.values
        df.loc[country_mask, 'Historical_Silver'] = cumsum_silver.values
        df.loc[country_mask, 'Historical_Bronze'] = cumsum_bronze.values
        df.loc[country_mask, 'Historical_Total'] = cumsum_total.values
    
    print(f"  ✓ Calculated historical totals for {df['Country'].nunique()} countries")
    print()
    
    return df


def calculate_recent_performance(df, window=3):
    """
    Calculate average performance over recent Olympics.
    
    Args:
        df: Olympic medal data with historical totals
        window: Number of previous Olympics to average (default 3)
    
    Returns:
        DataFrame with recent average columns added
    """
    print(f"Calculating recent performance (last {window} Olympics)...")
    
    df = df.copy()
    df = df.sort_values(['Country', 'Year'])
    
    # Initialize recent performance columns
    df[f'Recent_{window}_Olympics_Avg'] = 0.0
    
    # For each country, calculate rolling average
    for country in df['Country'].unique():
        country_mask = df['Country'] == country
        country_data = df[country_mask].copy()
        
        # Calculate rolling mean (excluding current year)
        recent_avg = country_data['Total'].shift(1).rolling(
            window=window, min_periods=1
        ).mean().fillna(0)
        
        # Update the dataframe
        df.loc[country_mask, f'Recent_{window}_Olympics_Avg'] = recent_avg.values
    
    print(f"  ✓ Calculated recent averages for {df['Country'].nunique()} countries")
    print()
    
    return df


def main():
    print("=" * 70)
    print("CALCULATING HISTORICAL OLYMPIC PERFORMANCE METRICS")
    print("=" * 70)
    print()
    
    data_dir = Path(__file__).parent.parent / 'data'
    
    # Load Olympic data
    print("Loading Olympic data...")
    summer = pd.read_csv(data_dir / 'summer_olympics_by_year.csv')
    winter = pd.read_csv(data_dir / 'winter_olympics_by_year.csv')
    
    print(f"  Summer: {len(summer)} records")
    print(f"  Winter: {len(winter)} records")
    print()
    
    print("-" * 70)
    print("SUMMER OLYMPICS")
    print("-" * 70)
    
    # Calculate historical totals for Summer
    summer_with_history = calculate_historical_totals(summer, 'Summer')
    
    # Calculate recent performance
    summer_with_history = calculate_recent_performance(summer_with_history, window=3)
    
    # Save
    output_path = data_dir / 'summer_olympics_with_history.csv'
    summer_with_history.to_csv(output_path, index=False)
    print(f"✓ Saved: {output_path}")
    print()
    
    print("-" * 70)
    print("WINTER OLYMPICS")
    print("-" * 70)
    
    # Calculate historical totals for Winter
    winter_with_history = calculate_historical_totals(winter, 'Winter')
    
    # Calculate recent performance
    winter_with_history = calculate_recent_performance(winter_with_history, window=3)
    
    # Save
    output_path = data_dir / 'winter_olympics_with_history.csv'
    winter_with_history.to_csv(output_path, index=False)
    print(f"✓ Saved: {output_path}")
    print()
    
    print("-" * 70)
    print("SAMPLE: USA SUMMER OLYMPICS PROGRESSION")
    print("-" * 70)
    usa_summer = summer_with_history[summer_with_history['Country'] == 'USA']
    
    # Show every 4th Olympics for readability
    sample_years = [1960, 1976, 1992, 2008, 2024]
    usa_sample = usa_summer[usa_summer['Year'].isin(sample_years)]
    
    print("\nYear  Current_Total  Historical_Total  Recent_3_Avg")
    print("-" * 60)
    for _, row in usa_sample.iterrows():
        print(f"{row['Year']}  {row['Total']:13.0f}  "
              f"{row['Historical_Total']:16.0f}  "
              f"{row['Recent_3_Olympics_Avg']:12.1f}")
    print()
    
    print("-" * 70)
    print("SAMPLE: NORWAY WINTER OLYMPICS PROGRESSION")
    print("-" * 70)
    nor_winter = winter_with_history[winter_with_history['Country'] == 'NOR']
    
    # Show recent Olympics
    sample_years = [1994, 2002, 2010, 2018, 2022]
    nor_sample = nor_winter[nor_winter['Year'].isin(sample_years)]
    
    print("\nYear  Current_Total  Historical_Total  Recent_3_Avg")
    print("-" * 60)
    for _, row in nor_sample.iterrows():
        print(f"{row['Year']}  {row['Total']:13.0f}  "
              f"{row['Historical_Total']:16.0f}  "
              f"{row['Recent_3_Olympics_Avg']:12.1f}")
    print()
    
    print("=" * 70)
    print("✓ HISTORICAL CALCULATIONS COMPLETE!")
    print("=" * 70)
    print()
    print("Historical metrics created:")
    print("  • Historical_Total: All-time medal count before this Olympics")
    print("  • Recent_3_Olympics_Avg: Average medals in previous 3 Olympics")
    print()
    print("Use cases:")
    print("  • Test if Olympic tradition predicts performance")
    print("  • Control for country's athletic infrastructure/culture")
    print("  • Identify 'emerging' vs 'established' Olympic powers")
    print()


if __name__ == '__main__':
    main()
