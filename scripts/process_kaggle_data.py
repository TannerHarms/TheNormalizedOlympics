"""
Process Kaggle Olympic dataset to create year-by-year medal counts

Input: athlete_events_extended.csv (preferred) or athlete_events.csv (fallback)
Output: summer_olympics_by_year.csv, winter_olympics_by_year.csv

Includes ALL participating countries, not just medal winners.
Countries that sent athletes but won zero medals get 0 for all medal columns.
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"

print("\n" + "="*70)
print("PROCESSING KAGGLE OLYMPIC DATA")
print("="*70 + "\n")

# Prefer extended dataset (includes 2018-2024), fall back to original
extended_file = RAW_DIR / "athlete_events_extended.csv"
original_file = RAW_DIR / "athlete_events.csv"

if extended_file.exists():
    athlete_file = extended_file
    print(f"✓ Using extended dataset: {athlete_file.name} (includes 2018-2024)")
elif original_file.exists():
    athlete_file = original_file
    print(f"✓ Using original dataset: {athlete_file.name} (1896-2016 only)")
    print("  To include 2018-2024: run python scripts/download_extended_athlete_data.py")
else:
    print(f"✗ No athlete data found in {RAW_DIR}")
    print("\nPlease download the data first:")
    print("  python scripts/download_kaggle_data.py")
    exit(1)

print("Loading data...")

# Load the athlete-level data
df = pd.read_csv(athlete_file)
print(f"  Loaded {len(df):,} rows")
print(f"  Columns: {', '.join(df.columns)}")

# ── Step 1: Get ALL participating countries per Year/Season ──────────────
# This ensures non-medal-winning countries are included
all_participants = (
    df.groupby(['Year', 'Season', 'NOC'])['ID']
    .nunique()
    .reset_index(name='_athlete_count')
)[['Year', 'Season', 'NOC']].copy()

print(f"\n✓ Found {len(all_participants):,} country-year-season participation records")
print(f"  Unique countries (all time): {all_participants['NOC'].nunique()}")

# ── Step 2: Count medals by EVENT (not by athlete) ──────────────────────
# Handle both NaN (original data) and "No medal" string (extended data)
medals_df = df[df['Medal'].notna() & (df['Medal'] != 'No medal')].copy()
print(f"\n✓ Filtered to {len(medals_df):,} medal-winning performances")

# CRITICAL: Count medals by EVENT, not by athlete
# This ensures team events count as 1 medal, not 12 medals (for 12 team members)
print("\nAggregating medals by country and year...")
print("  (Counting one medal per event, not per athlete)")

# Drop duplicate medal awards for the same event
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

medal_pivot['Total'] = medal_pivot['Gold'] + medal_pivot['Silver'] + medal_pivot['Bronze']

# ── Step 3: Merge participants with medal counts ────────────────────────
# Left join ensures ALL participants are included (zero-medal countries get NaN → 0)
combined = all_participants.merge(
    medal_pivot[['Year', 'Season', 'NOC', 'Gold', 'Silver', 'Bronze', 'Total']],
    on=['Year', 'Season', 'NOC'],
    how='left'
)

# Fill NaN medal counts with 0 (countries that participated but won nothing)
for col in ['Gold', 'Silver', 'Bronze', 'Total']:
    combined[col] = combined[col].fillna(0).astype(int)

# Rename NOC to Country for consistency
combined = combined.rename(columns={'NOC': 'Country'})

# Report on zero-medal countries
zero_medal = combined[combined['Total'] == 0]
has_medals = combined[combined['Total'] > 0]
print(f"\n✓ Combined: {len(combined):,} records")
print(f"  Countries with medals: {has_medals['Country'].nunique()}")
print(f"  Countries with 0 medals (but participated): {zero_medal['Country'].nunique()}")

# Split into Summer and Winter
summer_by_year = combined[combined['Season'] == 'Summer'][['Year', 'Country', 'Gold', 'Silver', 'Bronze', 'Total']].copy()
winter_by_year = combined[combined['Season'] == 'Winter'][['Year', 'Country', 'Gold', 'Silver', 'Bronze', 'Total']].copy()

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
recent_summer = summer_by_year[summer_by_year['Year'] == summer_by_year['Year'].max()]
print(f"  Countries in {int(summer_by_year['Year'].max())}: {len(recent_summer)} ({recent_summer[recent_summer['Total']>0].shape[0]} with medals)")

print(f"\n✓ Winter Olympics data saved: {winter_output.name}")
print(f"  Years covered: {winter_by_year['Year'].min()}-{winter_by_year['Year'].max()}")
print(f"  Total rows: {len(winter_by_year):,}")
print(f"  Unique countries: {winter_by_year['Country'].nunique()}")
recent_winter = winter_by_year[winter_by_year['Year'] == winter_by_year['Year'].max()]
print(f"  Countries in {int(winter_by_year['Year'].max())}: {len(recent_winter)} ({recent_winter[recent_winter['Total']>0].shape[0]} with medals)")

# Show a preview
print("\n" + "-"*70)
print("PREVIEW: Recent Summer Olympics (Top 5 countries)")
print("-"*70)
recent_summer_top = summer_by_year[summer_by_year['Year'] == summer_by_year['Year'].max()].head()
print(recent_summer_top.to_string(index=False))

print("\n" + "-"*70)
print(f"PREVIEW: Recent Summer Olympics (Bottom 5 countries - zero-medal participants)")
print("-"*70)
recent_summer_bottom = summer_by_year[
    (summer_by_year['Year'] == summer_by_year['Year'].max()) & (summer_by_year['Total'] == 0)
].tail()
print(recent_summer_bottom.to_string(index=False))

print("\n" + "="*70)
print("✓ DATA PROCESSING COMPLETE!")
print("="*70)
print("\nNext steps:")
print("  1. Review the generated CSV files")
print("  2. Run python scripts/calculate_historical_medals.py")
print("  3. Run python scripts/merge_all_data.py")
print("\n")
