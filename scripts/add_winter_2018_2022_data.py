"""
Add athlete data for Winter Olympics 2018 and 2022 from olympic_results.csv

This script extracts Total_Athletes, Individual_Medalists, and Total_Medals_Awarded
from the olympic_results.csv file for PyeongChang 2018 and Beijing 2022, then
updates the winter_olympics_all_metrics.csv file.

Author: Tanner D. Harms, February 2026
"""

import pandas as pd
from pathlib import Path

# Paths
DATA_DIR = Path(__file__).parent.parent / 'data'
RAW_DIR = DATA_DIR / 'raw'
RESULTS_FILE = RAW_DIR / 'olympic_results.csv'
WINTER_METRICS_FILE = DATA_DIR / 'winter_olympics_all_metrics.csv'

def extract_athlete_counts(df_results, game_slug, year):
    """
    Extract athlete counts from olympic_results.csv for a specific game.
    
    Returns dict with Total_Athletes, Individual_Medalists, Total_Medals_Awarded by country
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
                # Parse athletes field - may be comma or slash separated
                athletes_str = str(row['athletes'])
                for sep in [',', '/']:
                    if sep in athletes_str:
                        for name in athletes_str.split(sep):
                            all_athletes.add(name.strip())
        
        total_athletes = len(all_athletes)
        
        # Count medalists (athletes who won any medal)
        medal_data = country_data[country_data['medal_type'].isin(['GOLD', 'SILVER', 'BRONZE'])]
        medalist_names = set()
        
        for idx, row in medal_data.iterrows():
            if pd.notna(row['athlete_full_name']):
                medalist_names.add(row['athlete_full_name'].strip())
            if pd.notna(row['athletes']):
                athletes_str = str(row['athletes'])
                for sep in [',', '/']:
                    if sep in athletes_str:
                        for name in athletes_str.split(sep):
                            medalist_names.add(name.strip())
        
        individual_medalists = len(medalist_names)
        
        # Count total medals awarded (may be more than official medal count due to team sports)
        # Each medal result row represents a medal awarded
        total_medals_awarded = len(medal_data)
        
        country_results[country_code_3] = {
            'Total_Athletes': total_athletes,
            'Individual_Medalists': individual_medalists,
            'Total_Medals_Awarded': total_medals_awarded
        }
    
    print(f"  Countries processed: {len(country_results)}")
    print(f"  Sample (first 3 countries):")
    for i, (code, stats) in enumerate(list(country_results.items())[:3]):
        print(f"    {code}: {stats['Total_Athletes']} athletes, {stats['Individual_Medalists']} medalists, {stats['Total_Medals_Awarded']} medals awarded")
    
    return country_results

def main():
    """Process Winter 2018 and 2022 data and update metrics file."""
    
    print("="*70)
    print("Adding Winter Olympics 2018 and 2022 Athlete Data")
    print("="*70)
    
    # Load olympic results
    print(f"\nLoading {RESULTS_FILE}...")
    df_results = pd.read_csv(RESULTS_FILE, low_memory=False)
    print(f"Loaded {len(df_results):,} result rows")
    
    # Extract data for 2018 and 2022
    winter_2018 = extract_athlete_counts(df_results, 'pyeongchang-2018', 2018)
    winter_2022 = extract_athlete_counts(df_results, 'beijing-2022', 2022)
    
    # Load existing winter metrics
    print(f"\nLoading {WINTER_METRICS_FILE}...")
    df_winter = pd.read_csv(WINTER_METRICS_FILE)
    print(f"Current shape: {df_winter.shape}")
    print(f"Current years: {sorted(df_winter['Year'].unique())}")
    
    # Check if 2018/2022 already exist
    has_2018 = 2018 in df_winter['Year'].values
    has_2022 = 2022 in df_winter['Year'].values
    
    if has_2018 or has_2022:
        print(f"\nWarning: Data already exists for years: {[y for y in [2018, 2022] if y in df_winter['Year'].values]}")
        response = input("Do you want to update existing rows? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborting.")
            return
            
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
        
        # Note: Other medal counts (Gold, Silver, Bronze, Total) should already be in the dataset
        # If not, we'd need to calculate them separately
        
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
        
        df_winter = pd.concat([df_winter, template_row.to_frame().T], ignore_index=True)
    
    # Sort by Country and Year
    df_winter = df_winter.sort_values(['Country', 'Year']).reset_index(drop=True)
    
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
