"""
Process Kaggle Olympic dataset to create year-by-year medal counts

Input: athlete_events.csv (from Kaggle)
Output: summer_olympics_by_year.csv, winter_olympics_by_year.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"

print("\n" + "="*70)
print("PROCESSING KAGGLE OLYMPIC DATA")
print("="*70 + "\n")

# Check if the raw data file exists
athlete_file = RAW_DIR / "athlete_events.csv"

if not athlete_file.exists():
    print(f"✗ File not found: {athlete_file}")
    print("\nPlease download the data first:")
    print("  python scripts/download_kaggle_data.py")
    print("\nOr manually download from:")
    print("  https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results")
    exit(1)

print(f"✓ Found data file: {athlete_file.name}")
print("Loading data...")

# Load the athlete-level data
df = pd.read_csv(athlete_file)
print(f"  Loaded {len(df):,} rows")
print(f"  Columns: {', '.join(df.columns)}")

# Filter only medal winners (Gold, Silver, Bronze)
medals_df = df[df['Medal'].notna()].copy()
print(f"\n✓ Filtered to {len(medals_df):,} medal-winning performances (individual athletes)")

# CRITICAL: Count medals by EVENT, not by athlete
# This ensures team events count as 1 medal, not 12 medals (for 12 team members)
print("\nAggregating medals by country and year...")
print("  (Counting one medal per event, not per athlete)")

# Drop duplicate medal awards for the same event
# (keeps only one row per Year/Season/NOC/Event/Medal combination)
medals_unique = medals_df.drop_duplicates(subset=['Year', 'Season', 'NOC', 'Event', 'Medal'])
print(f"  After deduplication: {len(medals_unique):,} unique event medals")

# Count medals for each country, year, season, and medal type
medal_counts = medals_unique.groupby(['Year', 'Season', 'NOC', 'Medal']).size().reset_index(name='Count')

# Pivot to get Gold, Silver, Bronze as columns
medal_pivot = medal_counts.pivot_table(
    index=['Year', 'Season', 'NOC'],
    columns='Medal',
    values='Count',
    fill_value=0
).reset_index()

# Ensure all medal columns exist
for medal_type in ['Gold', 'Silver', 'Bronze']:
    if medal_type not in medal_pivot.columns:
        medal_pivot[medal_type] = 0

# Calculate total
medal_pivot['Total'] = medal_pivot['Gold'] + medal_pivot['Silver'] + medal_pivot['Bronze']

# Rename NOC to Country for consistency
medal_pivot = medal_pivot.rename(columns={'NOC': 'Country'})

# Split into Summer and Winter
summer_by_year = medal_pivot[medal_pivot['Season'] == 'Summer'][['Year', 'Country', 'Gold', 'Silver', 'Bronze', 'Total']].copy()
winter_by_year = medal_pivot[medal_pivot['Season'] == 'Winter'][['Year', 'Country', 'Gold', 'Silver', 'Bronze', 'Total']].copy()

# Sort by Year and Total medals
summer_by_year = summer_by_year.sort_values(['Year', 'Total'], ascending=[True, False])
winter_by_year = winter_by_year.sort_values(['Year', 'Total'], ascending=[True, False])

# Save to CSV
summer_output = DATA_DIR / "summer_olympics_by_year.csv"
winter_output = DATA_DIR / "winter_olympics_by_year.csv"

summer_by_year.to_csv(summer_output, index=False)
winter_by_year.to_csv(winter_output, index=False)

print(f"\n✓ Summer Olympics data saved: {summer_output.name}")
print(f"  Years covered: {summer_by_year['Year'].min()}-{summer_by_year['Year'].max()}")
print(f"  Total rows: {len(summer_by_year):,}")
print(f"  Unique countries: {summer_by_year['Country'].nunique()}")
print(f"  Sample years: {sorted(summer_by_year['Year'].unique())[:5]}...")

print(f"\n✓ Winter Olympics data saved: {winter_output.name}")
print(f"  Years covered: {winter_by_year['Year'].min()}-{winter_by_year['Year'].max()}")
print(f"  Total rows: {len(winter_by_year):,}")
print(f"  Unique countries: {winter_by_year['Country'].nunique()}")
print(f"  Sample years: {sorted(winter_by_year['Year'].unique())[:5]}...")

# Show a preview
print("\n" + "-"*70)
print("PREVIEW: Recent Summer Olympics (Top 5 countries)")
print("-"*70)
recent_summer = summer_by_year[summer_by_year['Year'] == summer_by_year['Year'].max()].head()
print(recent_summer.to_string(index=False))

print("\n" + "-"*70)
print("PREVIEW: Recent Winter Olympics (Top 5 countries)")
print("-"*70)
recent_winter = winter_by_year[winter_by_year['Year'] == winter_by_year['Year'].max()].head()
print(recent_winter.to_string(index=False))

print("\n" + "="*70)
print("✓ DATA PROCESSING COMPLETE!")
print("="*70)
print("\nNext steps:")
print("  1. Review the generated CSV files")
print("  2. Add 2020 and 2024 Olympics data manually (not in Kaggle dataset)")
print("  3. Run python scripts/preview_data.py to see all data")
print("\n")
