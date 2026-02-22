"""
Add athlete counts to Olympic datasets.

Computes from raw athlete_events.csv (or athlete_events_extended.csv):
  - Total_Athletes: total unique athletes sent by each country (per country/year)
  - Individual_Medalists: unique athletes who won at least one medal (per country/year)
  - Total_Medals_Awarded: total medal instances given to individual athletes (per country/year)
    (e.g., a 12-person basketball team winning gold = 12 medals awarded)

Data Coverage:
  - Original athlete_events.csv: 1896-2016 only
  - Extended athlete_events_extended.csv: 1896-2024 (if available)
  
To get 2018-2024 data:
  1. Run: python scripts/download_extended_athlete_data.py
  2. Run: python scripts/process_extended_athlete_data.py
  3. Run: python scripts/add_athlete_medal_counts.py
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"

def compute_athlete_medal_counts():
    """Compute athlete counts and medal stats from raw athlete data."""
    
    # Check for extended dataset first (includes 2018-2024), fall back to original
    athlete_file_extended = RAW_DIR / "athlete_events_extended.csv"
    athlete_file_original = RAW_DIR / "athlete_events.csv"
    
    if athlete_file_extended.exists():
        athlete_file = athlete_file_extended
        print("Using extended athlete dataset (includes 2018-2024)")
    elif athlete_file_original.exists():
        athlete_file = athlete_file_original
        print("Using original athlete dataset (1896-2016 only)")
        print("  To include 2018-2024: run python scripts/download_extended_athlete_data.py")
    else:
        print(f"ERROR: No athlete data found in {RAW_DIR}")
        return
    
    print("Loading raw athlete data...")
    df = pd.read_csv(athlete_file)
    print(f"  {len(df):,} total rows")
    print(f"  Years: {df['Year'].min()}-{df['Year'].max()}")
    
    # --- Total Athletes Sent ---
    # Count all unique athlete IDs per country/year/season (includes non-medalists)
    total_athletes = (
        df.groupby(['Year', 'Season', 'NOC'])['ID']
        .nunique()
        .reset_index(name='Total_Athletes')
    )
    
    # Filter to medal winners only
    # Note: Extended dataset uses "No medal" string, original used NaN
    medals = df[
        df['Medal'].notna() & 
        (df['Medal'] != 'No medal')
    ].copy()
    print(f"  {len(medals):,} medal-winning rows")
    
    # --- Individual Medalists ---
    # Count unique athlete IDs who won at least one medal, per country/year/season
    individual = (
        medals.groupby(['Year', 'Season', 'NOC'])['ID']
        .nunique()
        .reset_index(name='Individual_Medalists')
    )
    
    # --- Total Medals Awarded ---
    # Count every athlete-medal row (each team member counts)
    total_awarded = (
        medals.groupby(['Year', 'Season', 'NOC'])
        .size()
        .reset_index(name='Total_Medals_Awarded')
    )
    
    # --- Per-medal-type awarded counts ---
    # Gold_Awarded / Silver_Awarded / Bronze_Awarded: athlete-medal rows per type
    for medal_type in ['Gold', 'Silver', 'Bronze']:
        col_name = f'{medal_type}_Awarded'
        type_awarded = (
            medals[medals['Medal'] == medal_type]
            .groupby(['Year', 'Season', 'NOC'])
            .size()
            .reset_index(name=col_name)
        )
        total_awarded = total_awarded.merge(type_awarded, on=['Year', 'Season', 'NOC'], how='left')
        total_awarded[col_name] = total_awarded[col_name].fillna(0).astype(int)
    
    # --- Per-medal-type medalist counts (by highest medal won) ---
    # Assign each unique medalist to their highest medal: Gold > Silver > Bronze
    medal_rank = {'Gold': 3, 'Silver': 2, 'Bronze': 1}
    medals_ranked = medals.copy()
    medals_ranked['_rank'] = medals_ranked['Medal'].map(medal_rank)
    best_medal = (
        medals_ranked.groupby(['Year', 'Season', 'NOC', 'ID'])['_rank']
        .max()
        .reset_index()
    )
    rank_to_medal = {3: 'Gold', 2: 'Silver', 1: 'Bronze'}
    best_medal['_best'] = best_medal['_rank'].map(rank_to_medal)
    
    for medal_type in ['Gold', 'Silver', 'Bronze']:
        col_name = f'{medal_type}_Medalists'
        type_medalists = (
            best_medal[best_medal['_best'] == medal_type]
            .groupby(['Year', 'Season', 'NOC'])['ID']
            .nunique()
            .reset_index(name=col_name)
        )
        individual = individual.merge(type_medalists, on=['Year', 'Season', 'NOC'], how='left')
        individual[col_name] = individual[col_name].fillna(0).astype(int)
    
    # Merge all
    athlete_counts = total_athletes.merge(individual, on=['Year', 'Season', 'NOC'], how='left')
    athlete_counts = athlete_counts.merge(total_awarded, on=['Year', 'Season', 'NOC'], how='left')
    athlete_counts = athlete_counts.rename(columns={'NOC': 'Country'})
    
    # Fill NaN (countries with no medals) with 0
    for col in ['Individual_Medalists', 'Total_Medals_Awarded',
                'Gold_Awarded', 'Silver_Awarded', 'Bronze_Awarded',
                'Gold_Medalists', 'Silver_Medalists', 'Bronze_Medalists']:
        athlete_counts[col] = athlete_counts[col].fillna(0).astype(int)
    
    print(f"\nComputed counts for {len(athlete_counts):,} country-year-season combinations")
    
    # Show a sample
    usa_2016 = athlete_counts[
        (athlete_counts['Country'] == 'USA') & 
        (athlete_counts['Year'] == 2016)
    ]
    print("\nSample - USA 2016:")
    print(usa_2016.to_string(index=False))
    
    # Show some countries with no medals to verify Total_Athletes still works
    no_medals = athlete_counts[
        (athlete_counts['Individual_Medalists'] == 0) & 
        (athlete_counts['Year'] == 2016)
    ].head(3)
    if len(no_medals) > 0:
        print("\nSample - Countries with no medals in 2016:")
        print(no_medals[['Season', 'Country', 'Total_Athletes', 'Individual_Medalists']].to_string(index=False))
    
    return athlete_counts


def merge_into_all_metrics(athlete_counts):
    """Merge athlete counts into all_metrics CSVs."""
    
    for season, filename in [('Summer', 'summer_olympics_all_metrics.csv'),
                              ('Winter', 'winter_olympics_all_metrics.csv')]:
        filepath = DATA_DIR / filename
        print(f"\nUpdating {filename}...")
        
        df = pd.read_csv(filepath)
        orig_cols = len(df.columns)
        
        # Drop existing columns if re-running
        drop_cols = ['Total_Athletes', 'Individual_Medalists', 'Total_Medals_Awarded',
                     'Gold_Awarded', 'Silver_Awarded', 'Bronze_Awarded',
                     'Gold_Medalists', 'Silver_Medalists', 'Bronze_Medalists']
        for col in drop_cols:
            if col in df.columns:
                df = df.drop(columns=[col])
        
        # Filter athlete counts to this season
        merge_cols = ['Year', 'Country', 'Total_Athletes',
                      'Individual_Medalists', 'Gold_Medalists', 'Silver_Medalists', 'Bronze_Medalists',
                      'Total_Medals_Awarded', 'Gold_Awarded', 'Silver_Awarded', 'Bronze_Awarded']
        season_counts = athlete_counts[athlete_counts['Season'] == season][merge_cols]
        
        # Merge on Country + Year
        df = df.merge(season_counts, on=['Year', 'Country'], how='left')
        
        # Report coverage
        total_rows = len(df)
        filled = df['Total_Athletes'].notna().sum()
        missing = total_rows - filled
        
        pct = (filled / total_rows * 100) if total_rows > 0 else 0
        print(f"  {filled}/{total_rows} rows have athlete-level data ({pct:.1f}%)")
        
        # Show years with missing data
        missing_years = sorted(df[df['Total_Athletes'].isna()]['Year'].unique())
        if missing_years:
            print(f"  Years without athlete data: {missing_years}")
            if any(year >= 2018 for year in missing_years):
                print(f"    → To add 2018-2024: run download_extended_athlete_data.py")
        
        # Save
        df.to_csv(filepath, index=False)
        print(f"  Saved: {len(df.columns)} columns (was {orig_cols})")
        
        # Show top countries for most recent year with data
        latest_year = df[df['Total_Athletes'].notna()]['Year'].max()
        top = df[df['Year'] == latest_year].nlargest(5, 'Individual_Medalists')[
            ['Country', 'Year', 'Total_Athletes', 'Individual_Medalists', 'Total_Medals_Awarded', 'Total']
        ]
        print(f"\n  Top 5 by Individual Medalists ({season} {int(latest_year)}):")
        print(top.to_string(index=False))


if __name__ == "__main__":
    print("=" * 60)
    print("ADDING ATHLETE COUNTS TO OLYMPIC DATASETS")
    print("=" * 60)
    
    athlete_counts = compute_athlete_medal_counts()
    if athlete_counts is not None:
        merge_into_all_metrics(athlete_counts)
    
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
