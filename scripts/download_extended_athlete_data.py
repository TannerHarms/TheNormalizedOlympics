"""
Download Extended Olympic Athlete Data (1896-2024)

This script downloads updated Kaggle datasets that extend athlete-level data
through 2024, allowing us to calculate Individual_Medalists, Total_Athletes,
and Total_Medals_Awarded for recent Olympics (2018-2024).

Data Sources:
- Summer Olympics (1896-2024): stefanydeoliveira/summer-olympics-medals-1896-2024
- Winter Olympics (through 2022): piterfm/olympic-games-medals-19862018
- Paris 2024: piterfm/paris-2024-olympic-summer-games

This replaces/extends the original athlete_events.csv (which only went to 2016).

SETUP REQUIRED:
1. Install Kaggle API: pip install kaggle
2. Get Kaggle API credentials from https://www.kaggle.com/settings
3. Place kaggle.json in ~/.kaggle/ (or C:\\Users\\<username>\\.kaggle\\ on Windows)

Author: GitHub Copilot
Date: February 2026
"""

import pandas as pd
from pathlib import Path
import sys

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

print("\n" + "="*70)
print("EXTENDED OLYMPIC ATHLETE DATA DOWNLOADER")
print("="*70 + "\n")

# Check if Kaggle is installed
try:
    import kaggle
    kaggle_available = True
    print("✓ Kaggle API is installed")
except ImportError:
    kaggle_available = False
    print("✗ Kaggle API not installed")
    print("  Install with: pip install kaggle")
    print("\nPlease install Kaggle API and try again.")
    sys.exit(1)

# Dataset information
datasets = {
    'summer_extended': {
        'name': 'stefanydeoliveira/summer-olympics-medals-1896-2024',
        'file': 'olympics_dataset.csv',
        'description': 'Summer Olympics 1896-2024 (athlete-level)',
        'coverage': '1896-2024'
    },
    'winter_extended': {
        'name': 'piterfm/olympic-games-medals-19862018',
        'file': 'olympic_athletes.csv',
        'description': 'Summer & Winter Olympics 1896-2022',
        'coverage': '1896-2022 (includes Winter 2018, 2022)'
    }
}

print("\nDatasets to download:")
for key, info in datasets.items():
    print(f"  • {info['description']}")
    print(f"    Source: {info['name']}")
    print(f"    Coverage: {info['coverage']}")
    print()

# Download Summer Olympics Extended (1896-2024)
print("="*70)
print("DOWNLOADING SUMMER OLYMPICS DATA (1896-2024)")
print("="*70 + "\n")

try:
    kaggle.api.dataset_download_files(
        datasets['summer_extended']['name'],
        path=RAW_DIR,
        unzip=True
    )
    print(f"✓ Downloaded: {datasets['summer_extended']['description']}")
    
    # Check if file exists
    summer_file = RAW_DIR / datasets['summer_extended']['file']
    if summer_file.exists():
        df_summer = pd.read_csv(summer_file)
        print(f"  Rows: {len(df_summer):,}")
        print(f"  Columns: {list(df_summer.columns)}")
        print(f"  Years: {df_summer['Year'].min()} - {df_summer['Year'].max()}")
        print(f"  Athletes: {df_summer['Name'].nunique():,}")
    else:
        print(f"✗ Expected file not found: {datasets['summer_extended']['file']}")
        
except Exception as e:
    print(f"✗ Error downloading Summer Olympics data: {e}")
    print("\nPossible reasons:")
    print("  1. No Kaggle API credentials configured")
    print("  2. No internet connection")
    print("  3. Dataset name changed or removed")

# Download Winter/Combined Olympics (through 2022)
print("\n" + "="*70)
print("DOWNLOADING WINTER OLYMPICS DATA (1896-2022)")
print("="*70 + "\n")

try:
    kaggle.api.dataset_download_files(
        datasets['winter_extended']['name'],
        path=RAW_DIR,
        unzip=True
    )
    print(f"✓ Downloaded: {datasets['winter_extended']['description']}")
    
    # Check if file exists
    winter_file = RAW_DIR / datasets['winter_extended']['file']
    if winter_file.exists():
        df_winter = pd.read_csv(winter_file)
        print(f"  Rows: {len(df_winter):,}")
        print(f"  Columns: {list(df_winter.columns)}")
        
        # Filter to just Winter Olympics
        if 'discipline_title' in df_winter.columns:
            winter_only = df_winter[df_winter['discipline_title'].notna()]
            print(f"  Years: {winter_only['Games'].nunique()} games")
        else:
            print("  (Structure may differ - check manually)")
    else:
        print(f"✗ Expected file not found: {datasets['winter_extended']['file']}")
        
except Exception as e:
    print(f"✗ Error downloading Winter Olympics data: {e}")

# Summary and next steps
print("\n" + "="*70)
print("DOWNLOAD COMPLETE")
print("="*70 + "\n")

print("Downloaded files:")
for file in RAW_DIR.glob("*.csv"):
    size_mb = file.stat().st_size / (1024 * 1024)
    print(f"  • {file.name} ({size_mb:.1f} MB)")

print("\n" + "="*70)
print("NEXT STEPS")
print("="*70 + "\n")

print("1. Run: python scripts/process_extended_athlete_data.py")
print("   This will process the new data into the format needed for")
print("   your add_athlete_medal_counts.py script.")
print()
print("2. The extended data will allow calculating:")
print("   - Total_Athletes (for 2018-2024)")
print("   - Individual_Medalists (for 2018-2024)")
print("   - Total_Medals_Awarded (for 2018-2024)")
print()
print("3. Re-run: python scripts/add_athlete_medal_counts.py")
print("   to update all_metrics CSVs with complete 2018-2024 data")

print("\n" + "="*70)
print("DATA INSPECTION")
print("="*70 + "\n")

# Quick data inspection
summer_file = RAW_DIR / 'olympics_dataset.csv'
if summer_file.exists():
    print("Summer Olympics Dataset Preview:")
    df = pd.read_csv(summer_file, nrows=5)
    print(df.to_string())
    print()
    
    # Check recent years
    df_full = pd.read_csv(summer_file)
    recent_years = df_full[df_full['Year'] >= 2016].groupby('Year').size()
    print("Recent Olympics row counts:")
    print(recent_years)
    print()
    
    # Check for 2024 data
    if 2024 in df_full['Year'].values:
        print("✓ 2024 Paris Olympics data is present!")
        paris_2024 = df_full[df_full['Year'] == 2024]
        print(f"  Athletes in 2024: {paris_2024['Name'].nunique():,}")
        print(f"  Countries in 2024: {paris_2024['NOC'].nunique()}")
        print(f"  Events in 2024: {paris_2024['Event'].nunique()}")
    else:
        print("⚠ No 2024 data found in dataset")

print("\n" + "="*70)
