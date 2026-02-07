"""
Merge Olympic medal data with all normalization data.

This creates a unified dataset with:
- Olympic medals (by country, year, season)
- Historical performance metrics
- Population, GDP, GDP per capita
- HDI (Human Development Index)
- Climate zone
- Education spending

From this we can calculate normalized metrics and perform comprehensive analysis.
"""

import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from scripts.country_mapping import NOC_TO_WB, get_wb_code

def load_olympic_data():
    """Load both Summer and Winter Olympics data with historical metrics."""
    data_dir = Path(__file__).parent.parent / 'data'
    
    print("Loading Olympic data...")
    
    summer = pd.read_csv(data_dir / 'summer_olympics_with_history.csv')
    winter = pd.read_csv(data_dir / 'winter_olympics_with_history.csv')
    
    print(f"  Summer: {len(summer)} records, {summer['Year'].min()}-{summer['Year'].max()}")
    print(f"  Winter: {len(winter)} records, {winter['Year'].min()}-{winter['Year'].max()}")
    print()
    
    return summer, winter


def load_normalization_data():
    """Load all normalization data (World Bank, HDI, climate, education)."""
    data_dir = Path(__file__).parent.parent / 'data'
    
    print("Loading normalization data...")
    
    # World Bank data
    wb = pd.read_csv(data_dir / 'world_bank_data.csv')
    print(f"  World Bank: {len(wb)} records")
    
    # HDI data
    hdi = pd.read_csv(data_dir / 'hdi_data.csv')
    print(f"  HDI: {len(hdi)} records")
    
    # Climate data
    climate = pd.read_csv(data_dir / 'climate_data.csv')
    print(f"  Climate: {len(climate)} countries")
    
    # Education spending
    education = pd.read_csv(data_dir / 'education_spending.csv')
    print(f"  Education: {len(education)} records")
    print()
    
    return wb, hdi, climate, education


def merge_all_data(olympic_df, wb_df, hdi_df, climate_df, education_df, season):
    """
    Merge Olympic data with all normalization factors.
    
    Args:
        olympic_df: Olympic medal counts with historical metrics
        wb_df: World Bank data (Population, GDP, GDP_per_capita)
        hdi_df: HDI data
        climate_df: Climate zone classification
        education_df: Education spending
        season: 'Summer' or 'Winter'
    
    Returns:
        Merged dataframe with all normalization factors
    """
    print(f"Merging {season} Olympics with all normalization data...")
    
    # Add WB_Code to Olympic data
    olympic_df = olympic_df.copy()
    olympic_df['WB_Code'] = olympic_df['Country'].map(get_wb_code)
    
    # Count unmapped countries
    unmapped = olympic_df[olympic_df['WB_Code'].isna()]
    if len(unmapped) > 0:
        print(f"  ⚠ {len(unmapped)} records with unmapped country codes:")
        for country in unmapped['Country'].unique()[:10]:
            print(f"    {country}")
        if len(unmapped['Country'].unique()) > 10:
            print(f"    ... and {len(unmapped['Country'].unique()) - 10} more")
        print()
    
    # Remove unmapped
    olympic_df = olympic_df[olympic_df['WB_Code'].notna()]
    
    # Merge with World Bank data
    merged = olympic_df.merge(
        wb_df,
        on=['WB_Code', 'Year'],
        how='left'
    )
    print(f"  ✓ Merged World Bank data")
    
    # Merge with HDI
    merged = merged.merge(
        hdi_df,
        on=['WB_Code', 'Year'],
        how='left'
    )
    print(f"  ✓ Merged HDI data")
    
    # Merge with climate (no year dimension)
    merged = merged.merge(
        climate_df,
        on='WB_Code',
        how='left'
    )
    print(f"  ✓ Merged climate data")
    
    # Merge with education
    merged = merged.merge(
        education_df,
        on=['WB_Code', 'Year'],
        how='left'
    )
    print(f"  ✓ Merged education data")
    
    # Check merge success
    total_records = len(merged)
    with_population = merged['Population'].notna().sum()
    with_gdp = merged['GDP'].notna().sum()
    with_hdi = merged['HDI'].notna().sum()
    with_education = merged['Education_Spending_pct_GDP'].notna().sum()
    with_climate = merged['Climate_Zone'].notna().sum()
    
    print(f"\n  Total records: {total_records}")
    print(f"  With population: {with_population} ({100*with_population/total_records:.1f}%)")
    print(f"  With GDP: {with_gdp} ({100*with_gdp/total_records:.1f}%)")
    print(f"  With HDI: {with_hdi} ({100*with_hdi/total_records:.1f}%)")
    print(f"  With climate: {with_climate} ({100*with_climate/total_records:.1f}%)")
    print(f"  With education: {with_education} ({100*with_education/total_records:.1f}%)")
    print()
    
    return merged


def calculate_normalized_metrics(df):
    """
    Calculate normalized medal metrics.
    
    Metrics:
    - Medals per capita (per million people)
    - Medals per billion USD GDP
    - Medals per $10K GDP per capita
    - Medals per HDI point
    """
    print("Calculating normalized metrics...")
    
    df = df.copy()
    
    # Medals per million people
    df['Medals_per_million_pop'] = (df['Total'] / df['Population']) * 1_000_000
    
    # Medals per billion USD GDP
    df['Medals_per_billion_GDP'] = (df['Total'] / df['GDP']) * 1_000_000_000
    
    # Medals per $10K GDP per capita
    df['Medals_per_10K_GDPpc'] = (df['Total'] / df['GDP_per_capita']) * 10_000
    
    # Medals per HDI point (0-1 scale)
    df['Medals_per_HDI'] = df['Total'] / df['HDI']
    
    # Gold medals with same normalization
    df['Gold_per_million_pop'] = (df['Gold'] / df['Population']) * 1_000_000
    df['Gold_per_billion_GDP'] = (df['Gold'] / df['GDP']) * 1_000_000_000
    df['Gold_per_10K_GDPpc'] = (df['Gold'] / df['GDP_per_capita']) * 10_000
    df['Gold_per_HDI'] = df['Gold'] / df['HDI']
    
    print("  ✓ Calculated 8 normalized metrics")
    print()
    
    return df


def main():
    print("=" * 70)
    print("MERGING OLYMPIC AND NORMALIZATION DATA")
    print("=" * 70)
    print()
    
    # Load data
    summer, winter = load_olympic_data()
    wb, hdi, climate, education = load_normalization_data()
    
    print("-" * 70)
    print("SUMMER OLYMPICS")
    print("-" * 70)
    
    # Filter Summer Olympics to World Bank years (1960+)
    summer_filtered = summer[summer['Year'] >= 1960].copy()
    print(f"Filtered to {len(summer_filtered)} records (1960+)")
    print()
    
    # Merge Summer
    summer_merged = merge_all_data(summer_filtered, wb, hdi, climate, education, 'Summer')
    
    # Calculate normalized metrics
    summer_merged = calculate_normalized_metrics(summer_merged)
    
    # Save
    output_path = Path(__file__).parent.parent / 'data' / 'summer_olympics_normalized.csv'
    summer_merged.to_csv(output_path, index=False)
    print(f"✓ Saved: {output_path}")
    print()
    
    print("-" * 70)
    print("WINTER OLYMPICS")
    print("-" * 70)
    
    # Filter Winter Olympics to World Bank years (1960+)
    winter_filtered = winter[winter['Year'] >= 1960].copy()
    print(f"Filtered to {len(winter_filtered)} records (1960+)")
    print()
    
    # Merge Winter
    winter_merged = merge_all_data(winter_filtered, wb, hdi, climate, education, 'Winter')
    
    # Calculate normalized metrics
    winter_merged = calculate_normalized_metrics(winter_merged)
    
    # Save
    output_path = Path(__file__).parent.parent / 'data' / 'winter_olympics_normalized.csv'
    winter_merged.to_csv(output_path, index=False)
    print(f"✓ Saved: {output_path}")
    print()
    
    print("-" * 70)
    print("SAMPLE: USA 2020 (TOKYO) - SUMMER")
    print("-" * 70)
    sample = summer_merged[(summer_merged['Country'] == 'USA') & (summer_merged['Year'] == 2020)]
    if len(sample) > 0:
        sample_row = sample.iloc[0]
        print(f"  Medals: {sample_row['Total']:.0f} (Gold: {sample_row['Gold']:.0f})")
        print(f"  Population: {sample_row['Population']:,.0f}")
        print(f"  GDP: ${sample_row['GDP']:,.0f}")
        print(f"  GDP per capita: ${sample_row['GDP_per_capita']:,.2f}")
        print(f"  HDI: {sample_row['HDI']:.3f}")
        print(f"  Climate Zone: {sample_row['Climate_Description']}")
        print(f"  Historical Total: {sample_row['Historical_Total']:.0f}")
        print()
        print(f"  Medals per million people: {sample_row['Medals_per_million_pop']:.3f}")
        print(f"  Medals per billion GDP: {sample_row['Medals_per_billion_GDP']:.3f}")
        print(f"  Medals per $10K GDP/capita: {sample_row['Medals_per_10K_GDPpc']:.3f}")
        print(f"  Medals per HDI: {sample_row['Medals_per_HDI']:.2f}")
    print()
    
    print("-" * 70)
    print("SAMPLE: NORWAY 2022 (BEIJING) - WINTER")
    print("-" * 70)
    sample = winter_merged[(winter_merged['Country'] == 'NOR') & (winter_merged['Year'] == 2022)]
    if len(sample) > 0:
        sample_row = sample.iloc[0]
        print(f"  Medals: {sample_row['Total']:.0f} (Gold: {sample_row['Gold']:.0f})")
        print(f"  Population: {sample_row['Population']:,.0f}")
        print(f"  GDP: ${sample_row['GDP']:,.0f}")
        print(f"  GDP per capita: ${sample_row['GDP_per_capita']:,.2f}")
        print(f"  HDI: {sample_row['HDI']:.3f}")
        print(f"  Climate Zone: {sample_row['Climate_Description']}")
        print(f"  Winter Sports Index: {sample_row['Winter_Sports_Index']}/10")
        print(f"  Historical Total: {sample_row['Historical_Total']:.0f}")
        print()
        print(f"  Medals per million people: {sample_row['Medals_per_million_pop']:.3f}")
        print(f"  Medals per billion GDP: {sample_row['Medals_per_billion_GDP']:.3f}")
        print(f"  Medals per $10K GDP/capita: {sample_row['Medals_per_10K_GDPpc']:.3f}")
        print(f"  Medals per HDI: {sample_row['Medals_per_HDI']:.2f}")
    print()
    
    print("=" * 70)
    print("✓ DATA MERGE COMPLETE!")
    print("=" * 70)
    print()
    print("Normalized datasets created:")
    print(f"  • summer_olympics_normalized.csv ({len(summer_merged)} records)")
    print(f"  • winter_olympics_normalized.csv ({len(winter_merged)} records)")
    print()
    print("Ready for analysis and visualization!")
    print()


if __name__ == '__main__':
    main()
