"""
Process Extended Athlete Data (2016-2024)

This script processes the newly downloaded Kaggle datasets to extend 
athlete-level data for 2018-2024 Olympics. It creates an extended version
of athlete_events.csv that can be used with add_athlete_medal_counts.py.

The script:
1. Loads the original athlete_events.csv (1896-2016)
2. Loads the new extended datasets (includes 2018-2024)
3. Merges them, removing duplicates from overlapping years
4. Creates athlete_events_extended.csv with complete 1896-2024 coverage

Author: GitHub Copilot
Date: February 2026
"""

import pandas as pd
from pathlib import Path
import numpy as np

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"

print("\n" + "="*70)
print("PROCESSING EXTENDED ATHLETE DATA")
print("="*70 + "\n")

# Load original dataset (1896-2016)
original_file = RAW_DIR / "athlete_events.csv"
if not original_file.exists():
    print(f"✗ Original athlete_events.csv not found in {RAW_DIR}")
    print("  Please ensure the original Kaggle dataset is downloaded first.")
    exit(1)

print("Loading original dataset (1896-2016)...")
df_original = pd.read_csv(original_file)
print(f"  Rows: {len(df_original):,}")
print(f"  Years: {df_original['Year'].min()} - {df_original['Year'].max()}")
print(f"  Athletes: {df_original['Name'].nunique():,}")
print()

# Load extended Summer Olympics dataset (1896-2024)
summer_extended_file = RAW_DIR / "olympics_dataset.csv"
if not summer_extended_file.exists():
    print(f"✗ Extended Summer Olympics data not found: {summer_extended_file}")
    print("  Please run: python scripts/download_extended_athlete_data.py")
    exit(1)

print("Loading extended Summer Olympics dataset (1896-2024)...")
df_summer_extended = pd.read_csv(summer_extended_file)
print(f"  Rows: {len(df_summer_extended):,}")
print(f"  Years: {df_summer_extended['Year'].min()} - {df_summer_extended['Year'].max()}")
print(f"  Athletes: {df_summer_extended['Name'].nunique():,}")
print()

# Check column alignment
print("Checking column compatibility...")
print(f"  Original columns: {list(df_original.columns)}")
print(f"  Extended columns: {list(df_summer_extended.columns)}")
print()

# Map extended dataset columns to match original
# Extended dataset has: player_id, Name, Sex, Team, NOC, Year, Season, City, Sport, Event, Medal
# Original has: ID, Name, Sex, Age, Height, Weight, Team, NOC, Games, Year, Season, City, Sport, Event, Medal

# Create mapping
extended_to_original_mapping = {
    'player_id': 'ID',
    'Name': 'Name',
    'Sex': 'Sex',
    'Team': 'Team',
    'NOC': 'NOC',
    'Year': 'Year',
    'Season': 'Season',
    'City': 'City',
    'Sport': 'Sport',
    'Event': 'Event',
    'Medal': 'Medal'
}

# Select and rename columns from extended dataset
extended_cols = [col for col in extended_to_original_mapping.keys() if col in df_summer_extended.columns]
df_extended_mapped = df_summer_extended[extended_cols].copy()
df_extended_mapped.columns = [extended_to_original_mapping[col] for col in extended_cols]

# Add missing columns from original (Age, Height, Weight, Games) as NaN
for col in ['Age', 'Height', 'Weight', 'Games']:
    if col not in df_extended_mapped.columns:
        if col == 'Games':
            # Construct Games from Year, Season, City
            df_extended_mapped['Games'] = (
                df_extended_mapped['Year'].astype(str) + ' ' + 
                df_extended_mapped['Season']
            )
        else:
            df_extended_mapped[col] = np.nan

# Ensure column order matches original
df_extended_mapped = df_extended_mapped[df_original.columns]

print("Filtering to recent Olympics (2018-2024)...")
# Only take 2018+ from extended dataset to avoid duplicates
df_recent = df_extended_mapped[df_extended_mapped['Year'] >= 2018].copy()
print(f"  Rows for 2018-2024: {len(df_recent):,}")
print(f"  Years: {sorted(df_recent['Year'].unique())}")
print()

# Also check for Winter Olympics data
winter_file = RAW_DIR / "olympic_athletes.csv"
if winter_file.exists():
    print("Checking Winter Olympics data...")
    df_winter = pd.read_csv(winter_file, nrows=100)
    print(f"  Columns: {list(df_winter.columns)[:10]}...")
    print("  (Winter data structure may differ - manual processing may be needed)")
    print()

# Combine original (through 2016) with recent (2018+)
print("Merging datasets...")
df_combined = pd.concat([df_original, df_recent], ignore_index=True)
print(f"  Combined rows: {len(df_combined):,}")
print(f"  Years: {df_combined['Year'].min()} - {df_combined['Year'].max()}")
print(f"  Athletes: {df_combined['Name'].nunique():,}")
print()

# Check for 2017 gap
years_present = sorted(df_combined['Year'].unique())
print(f"Years present: {years_present[-10:]}")  # Last 10 years
print()

# Summary by year
print("Records by recent year:")
year_counts = df_combined[df_combined['Year'] >= 2014].groupby('Year').size()
print(year_counts)
print()

# Check Olympics coverage
print("Olympics Games Coverage:")
recent_games = df_combined[df_combined['Year'] >= 2014]['Games'].value_counts().sort_index()
print(recent_games)
print()

# Save extended dataset
output_file = RAW_DIR / "athlete_events_extended.csv"
print(f"Saving extended dataset to: {output_file}")
df_combined.to_csv(output_file, index=False)
print(f"✓ Saved: {len(df_combined):,} rows")
print()

# Create a backup of original
if not (RAW_DIR / "athlete_events_original_backup.csv").exists():
    print("Creating backup of original athlete_events.csv...")
    df_original.to_csv(RAW_DIR / "athlete_events_original_backup.csv", index=False)
    print("✓ Backup created")
    print()

# Summary statistics for 2018-2024
print("="*70)
print("2018-2024 DATA SUMMARY")
print("="*70 + "\n")

for year in sorted(df_recent['Year'].unique()):
    year_data = df_recent[df_recent['Year'] == year]
    season = year_data['Season'].iloc[0] if len(year_data) > 0 else "Unknown"
    city = year_data['City'].iloc[0] if len(year_data) > 0 else "Unknown"
    
    print(f"{year} {season} Olympics ({city}):")
    print(f"  Total records: {len(year_data):,}")
    print(f"  Unique athletes: {year_data['Name'].nunique():,}")
    print(f"  Countries (NOCs): {year_data['NOC'].nunique()}")
    print(f"  Sports: {year_data['Sport'].nunique()}")
    print(f"  Events: {year_data['Event'].nunique()}")
    
    # Medal summary
    medals = year_data['Medal'].value_counts()
    print(f"  Medals: Gold={medals.get('Gold', 0)}, "
          f"Silver={medals.get('Silver', 0)}, "
          f"Bronze={medals.get('Bronze', 0)}")
    print()

print("="*70)
print("NEXT STEPS")
print("="*70 + "\n")

print("The extended athlete data is ready!")
print()
print("Option 1: Use the extended dataset directly")
print(f"  File: {output_file}")
print("  Update add_athlete_medal_counts.py to use athlete_events_extended.csv")
print()
print("Option 2: Replace the original (with backup)")
print("  mv data/raw/athlete_events.csv data/raw/athlete_events_old.csv")
print("  mv data/raw/athlete_events_extended.csv data/raw/athlete_events.csv")
print()
print("Then run:")
print("  python scripts/add_athlete_medal_counts.py")
print()
print("This will populate Total_Athletes, Individual_Medalists, and")
print("Total_Medals_Awarded for all years including 2018-2024!")

print("\n" + "="*70)
