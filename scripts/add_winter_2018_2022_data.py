"""
Add athlete data for Winter Olympics 2018 and 2022 from olympic_results.csv

This script extracts Total_Athletes, Individual_Medalists, and Total_Medals_Awarded
from the olympic_results.csv file for PyeongChang 2018 and Beijing 2022, then
updates the winter_olympics_all_metrics.csv file.

NOTE: Since olympic_results.csv doesn't have full team rosters for 2018/2022,
Total_Medals_Awarded is estimated using country-specific historical multipliers
from 2014 (most recent year with complete athlete-level data).

Author: Tanner D. Harms
"""

import pandas as pd
from pathlib import Path
import numpy as np

# Paths
DATA_DIR = Path(__file__).parent.parent / 'data'
RAW_DIR = DATA_DIR / 'raw'
RESULTS_FILE = RAW_DIR / 'olympic_results.csv'
WINTER_METRICS_FILE = DATA_DIR / 'winter_olympics_all_metrics.csv'

def calculate_historical_multipliers(df_winter):
    """
    Calculate country-specific multipliers (Total_Medals_Awarded / Total)
    from 2014 Winter Olympics to use for estimating 2018/2022 values.
    
    Returns: dict of country_code -> multiplier
    """
    # Use 2014 as reference (most recent with complete data)
    df_2014 = df_winter[df_winter['Year'] == 2014].copy()
    
    multipliers = {}
    for _, row in df_2014.iterrows():
        if row['Total'] > 0:
            multiplier = row['Total_Medals_Awarded'] / row['Total']
            multipliers[row['Country']] = multiplier
    
    # Calculate overall average as fallback
    overall_mult = df_2014['Total_Medals_Awarded'].sum() / df_2014['Total'].sum()
    
    print(f"\nCalculated historical multipliers from 2014:")
    print(f"  Countries with data: {len(multipliers)}")
    print(f"  Overall average multiplier: {overall_mult:.3f}")
    print(f"  Sample multipliers:")
    for i, (code, mult) in enumerate(list(sorted(multipliers.items(), key=lambda x: x[1], reverse=True))[:5]):
        print(f"    {code}: {mult:.2f}")
    
    return multipliers, overall_mult

def extract_athlete_counts(df_results, game_slug, year):
    """
    Extract athlete counts AND medal counts from olympic_results.csv for a specific game.
    
    Returns dict with Total_Athletes, Individual_Medalists, Total_Medals_Awarded, Gold, Silver, Bronze, Total by country
    """
    # Filter to the specific game
    game_data = df_results[df_results['slug_game'] == game_slug].copy()
    
    print(f"\n{game_slug} ({year}):")
    print(f"  Total result rows: {len(game_data)}")
    
    # Use 3-letter country codes for consistency with existing data
    country_results = {}
    
    for country_code_3 in game_data['country_3_letter_code'].unique():
        if pd.isna(country_code_3):
            continue
            
        country_data = game_data[game_data['country_3_letter_code'] == country_code_3]
        
        # Extract athlete names from the data
        # The 'athlete_full_name' column contains individual athlete names
        # For team events, 'athletes' column may have multiple names
        all_athletes = set()
        
        for idx, row in country_data.iterrows():
            if pd.notna(row['athlete_full_name']):
                all_athletes.add(row['athlete_full_name'].strip())
            # Some rows have team rosters in 'athletes' column
            if pd.notna(row['athletes']):
                # Parse athletes field - may be comma, slash separated, or a single name
                athletes_str = str(row['athletes']).strip()
                if athletes_str:
                    found_sep = False
                    for sep in [',', '/']:
                        if sep in athletes_str:
                            found_sep = True
                            for name in athletes_str.split(sep):
                                name = name.strip()
                                if name:
                                    all_athletes.add(name)
                    if not found_sep:
                        # Single-name entry (no separator found)
                        all_athletes.add(athletes_str)
        
        total_athletes = len(all_athletes)
        
        # Count medalists (athletes who won any medal)
        medal_data = country_data[country_data['medal_type'].isin(['GOLD', 'SILVER', 'BRONZE'])]
        medalist_names = set()
        
        for idx, row in medal_data.iterrows():
            if pd.notna(row['athlete_full_name']):
                medalist_names.add(row['athlete_full_name'].strip())
            if pd.notna(row['athletes']):
                athletes_str = str(row['athletes']).strip()
                if athletes_str:
                    found_sep = False
                    for sep in [',', '/']:
                        if sep in athletes_str:
                            found_sep = True
                            for name in athletes_str.split(sep):
                                name = name.strip()
                                if name:
                                    medalist_names.add(name)
                    if not found_sep:
                        medalist_names.add(athletes_str)
        
        individual_medalists = len(medalist_names)
        
        # Count total medals awarded (may be more than official medal count due to team sports)
        # Each medal result row represents a medal awarded
        total_medals_awarded = len(medal_data)
        
        # Count official medal counts (by event, not by athlete)
        gold_medals = len(medal_data[medal_data['medal_type'] == 'GOLD'])
        silver_medals = len(medal_data[medal_data['medal_type'] == 'SILVER'])
        bronze_medals = len(medal_data[medal_data['medal_type'] == 'BRONZE'])
        total_medals = gold_medals + silver_medals + bronze_medals
        
        country_results[country_code_3] = {
            'Total_Athletes': total_athletes,
            'Individual_Medalists': individual_medalists,
            'Total_Medals_Awarded': total_medals_awarded,
            'Gold': gold_medals,
            'Silver': silver_medals,
            'Bronze': bronze_medals,
            'Total': total_medals
        }
    
    print(f"  Countries processed: {len(country_results)}")
    print(f"  Sample (first 3 countries):")
    for i, (code, stats) in enumerate(list(country_results.items())[:3]):
        print(f"    {code}: {stats['Total_Athletes']} athletes, {stats['Individual_Medalists']} medalists, {stats['Total']} total medals (G:{stats['Gold']}, S:{stats['Silver']}, B:{stats['Bronze']})")
    
    return country_results

def main():
    """Process Winter 2018 and 2022 data and update metrics file."""
    
    print("="*70)
    print("Adding Winter Olympics 2018 and 2022 Athlete Data")
    print("="*70)
    
    # Load existing winter metrics first (needed for calculating multipliers)
    print(f"\nLoading {WINTER_METRICS_FILE}...")
    df_winter = pd.read_csv(WINTER_METRICS_FILE)
    print(f"Current shape: {df_winter.shape}")
    print(f"Current years: {sorted(df_winter['Year'].unique())}")
    
    # Calculate historical multipliers for estimating Total_Medals_Awarded
    multipliers, overall_mult = calculate_historical_multipliers(df_winter)
    
    # Load olympic results
    print(f"\nLoading {RESULTS_FILE}...")
    df_results = pd.read_csv(RESULTS_FILE, low_memory=False)
    print(f"Loaded {len(df_results):,} result rows")
    
    # Extract data for 2018 and 2022
    winter_2018 = extract_athlete_counts(df_results, 'pyeongchang-2018', 2018)
    winter_2022 = extract_athlete_counts(df_results, 'beijing-2022', 2022)
    
    # Estimate Total_Medals_Awarded using historical multipliers
    print(f"\nEstimating Total_Medals_Awarded using country-specific multipliers from 2014:")
    print("(olympic_results.csv lacks team roster data for 2018/2022)")
    for country_code, stats in winter_2018.items():
        mult = multipliers.get(country_code, overall_mult)
        original = stats['Total_Medals_Awarded']
        estimated = int(round(stats['Total'] * mult))
        stats['Total_Medals_Awarded'] = estimated
        print(f"  2018 {country_code}: Total={stats['Total']}, Estimated={estimated} (mult×{mult:.2f}, was {original})")
    
    for country_code, stats in winter_2022.items():
        mult = multipliers.get(country_code, overall_mult)
        original = stats['Total_Medals_Awarded']
        estimated = int(round(stats['Total'] * mult))
        stats['Total_Medals_Awarded'] = estimated
        print(f"  2022 {country_code}: Total={stats['Total']}, Estimated={estimated} (mult×{mult:.2f}, was {original})")
    
    # Check if 2018/2022 already exist
    has_2018 = 2018 in df_winter['Year'].values
    has_2022 = 2022 in df_winter['Year'].values
    
    if has_2018 or has_2022:
        print(f"\nInfo: Data already exists for years: {[y for y in [2018, 2022] if y in df_winter['Year'].values]}")
        print("Removing existing 2018/2022 data to update with corrected Total_Medals_Awarded...")
            
        # Remove existing 2018/2022 data
        df_winter = df_winter[~df_winter['Year'].isin([2018, 2022])]
        print(f"Removed existing 2018/2022 data. New shape: {df_winter.shape}")
    
    # Add new data for 2018
    print(f"\nAdding 2018 data...")
    for country_code, stats in winter_2018.items():
        # Find matching country in existing data
        existing_country = df_winter[df_winter['Country'] == country_code]
        
        if len(existing_country) == 0:
            print(f"  Warning: {country_code} not found in existing data, skipping")
            continue
        
        # Create new row based on most recent year's data structure
        template_row = existing_country.iloc[-1].copy()
        template_row['Year'] = 2018
        template_row['Total_Athletes'] = stats['Total_Athletes']
        template_row['Individual_Medalists'] = stats['Individual_Medalists']
        template_row['Total_Medals_Awarded'] = stats['Total_Medals_Awarded']
        template_row['Gold'] = stats['Gold']
        template_row['Silver'] = stats['Silver']
        template_row['Bronze'] = stats['Bronze']
        template_row['Total'] = stats['Total']
        
        df_winter = pd.concat([df_winter, template_row.to_frame().T], ignore_index=True)
    
    # Add new data for 2022
    print(f"\nAdding 2022 data...")
    for country_code, stats in winter_2022.items():
        existing_country = df_winter[df_winter['Country'] == country_code]
        
        if len(existing_country) == 0:
            print(f"  Warning: {country_code} not found in existing data, skipping")
            continue
        
        template_row = existing_country.iloc[-1].copy()
        template_row['Year'] = 2022
        template_row['Total_Athletes'] = stats['Total_Athletes']
        template_row['Individual_Medalists'] = stats['Individual_Medalists']
        template_row['Total_Medals_Awarded'] = stats['Total_Medals_Awarded']
        template_row['Gold'] = stats['Gold']
        template_row['Silver'] = stats['Silver']
        template_row['Bronze'] = stats['Bronze']
        template_row['Total'] = stats['Total']
        
        df_winter = pd.concat([df_winter, template_row.to_frame().T], ignore_index=True)
    
    # Sort by Country and Year BEFORE recalculating
    df_winter = df_winter.sort_values(['Country', 'Year']).reset_index(drop=True)
    
    # Recalculate all normalized metrics for 2018 and 2022 rows
    print(f"\nRecalculating normalized metrics for 2018/2022...")
    
    # Get boolean mask for 2018/2022 rows
    mask_2018_2022 = df_winter['Year'].isin([2018, 2022])
    rows_to_recalc = df_winter[mask_2018_2022]
    
    print(f"  Found {len(rows_to_recalc)} rows to recalculate")
    
    # Recalculate for each row
    for idx in rows_to_recalc.index:
        total = df_winter.at[idx, 'Total']
        population = df_winter.at[idx, 'Population']
        
        # Helper function to handle division by zero
        def safe_divide(numerator, denominator, multiplier=1):
            if pd.isna(denominator) or denominator == 0:
                return np.nan
            return (numerator / denominator) * multiplier
        
        # Basic metrics
        df_winter.at[idx, 'Medals_Per_Million'] = safe_divide(total, population, 1_000_000)
        df_winter.at[idx, 'Medals_Per_Billion_GDP'] = safe_divide(total, df_winter.at[idx, 'GDP'], 1_000_000_000)
        df_winter.at[idx, 'Medals_Per_GDP_Per_Capita'] = safe_divide(total, df_winter.at[idx, 'GDP_per_capita'], 10_000)
        df_winter.at[idx, 'Medals_Per_HDI'] = safe_divide(total, df_winter.at[idx, 'HDI'])
        
        # Geographic metrics
        df_winter.at[idx, 'Medals_Per_1000_SqKm'] = safe_divide(total, df_winter.at[idx, 'Land_Area_SqKm'], 1000)
        df_winter.at[idx, 'Medals_Per_1000_Km_Coastline'] = safe_divide(total, df_winter.at[idx, 'Coastline_Length_Km'], 1000)
        df_winter.at[idx, 'Medals_Per_100m_Elevation'] = safe_divide(total, df_winter.at[idx, 'Average_Elevation_Meters'], 100)
        
        # Climate metrics
        df_winter.at[idx, 'Medals_Per_Degree_Temp'] = safe_divide(total, abs(df_winter.at[idx, 'Avg_Temperature_C']))
        df_winter.at[idx, 'Medals_Per_100_Sunshine_Days'] = safe_divide(total, df_winter.at[idx, 'Sunshine_Days_Per_Year'], 100)
        df_winter.at[idx, 'Medals_Per_100_Cm_Snowfall'] = safe_divide(total, df_winter.at[idx, 'Avg_Snowfall_Cm_Per_Year'], 100)
        
        # Infrastructure metrics
        internet_users = df_winter.at[idx, 'Internet_Users_Pct'] * population / 100
        df_winter.at[idx, 'Medals_Per_Million_Internet_Users'] = safe_divide(total, internet_users, 1_000_000)
        vehicles = df_winter.at[idx, 'Vehicles_Per_1000'] * population / 1000
        df_winter.at[idx, 'Medals_Per_1000_Vehicles'] = safe_divide(total, vehicles, 1000)
        df_winter.at[idx, 'Medals_Per_University'] = safe_divide(total, df_winter.at[idx, 'Number_of_Universities'])
        df_winter.at[idx, 'Medals_Per_Stadium'] = safe_divide(total, df_winter.at[idx, 'Professional_Sports_Stadiums'])
        df_winter.at[idx, 'Medals_Per_Ski_Resort'] = safe_divide(total, df_winter.at[idx, 'Number_of_Ski_Resorts'])
        
        # Economic/Social metrics
        df_winter.at[idx, 'Medals_Per_Pct_Healthcare_Spending'] = safe_divide(total, df_winter.at[idx, 'Healthcare_Spending_Pct_GDP'])
        df_winter.at[idx, 'Medals_Per_Year_Life_Expectancy'] = safe_divide(total, df_winter.at[idx, 'Life_Expectancy_Years'])
        df_winter.at[idx, 'Medals_Per_100_Work_Hours'] = safe_divide(total, df_winter.at[idx, 'Avg_Work_Hours_Per_Year'], 100)
        
        # Cultural metrics
        df_winter.at[idx, 'Medals_Per_Peace_Index_Point'] = safe_divide(total, df_winter.at[idx, 'Global_Peace_Index_Score'])
        
        # Military metrics
        df_winter.at[idx, 'Medals_Per_Pct_Military_Spending'] = safe_divide(total, df_winter.at[idx, 'Military_Expenditure_Pct_GDP'])
        df_winter.at[idx, 'Medals_Per_1000_Military_Personnel'] = safe_divide(total, df_winter.at[idx, 'Active_Military_Personnel_Thousands'], 1000)
        
        # Education metrics
        df_winter.at[idx, 'Medals_Per_Pct_Education_Spending'] = safe_divide(total, df_winter.at[idx, 'Education_Spending_pct_GDP'])
    
    print(f"  ✓ Recalculated {len(rows_to_recalc)} rows with corrected normalized metrics")
    
    print(f"\nFinal shape: {df_winter.shape}")
    print(f"Final years: {sorted(df_winter['Year'].unique())}")
    
    # Save updated file
    print(f"\nSaving to {WINTER_METRICS_FILE}...")
    df_winter.to_csv(WINTER_METRICS_FILE, index=False)
    
    print("\n" + "="*70)
    print("SUCCESS: Winter Olympics 2018 and 2022 data added!")
    print("="*70)
    
    # Summary statistics
    print(f"\nSummary:")
    print(f"  2018: {len(winter_2018)} countries with athlete data")
    print(f"  2022: {len(winter_2022)} countries with athlete data")
    print(f"  Total rows in updated file: {len(df_winter)}")
    
    # Show coverage for 2018/2022
    coverage_2018 = df_winter[(df_winter['Year'] == 2018) & (df_winter['Total_Athletes'].notna())]
    coverage_2022 = df_winter[(df_winter['Year'] == 2022) & (df_winter['Total_Athletes'].notna())]
    print(f"  2018 coverage: {len(coverage_2018)} countries with athlete data")
    print(f"  2022 coverage: {len(coverage_2022)} countries with athlete data")

if __name__ == "__main__":
    main()
