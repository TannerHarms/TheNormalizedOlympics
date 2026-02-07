"""
Download and process Olympic data from Kaggle

Kaggle Dataset: "120 years of Olympic history: athletes and results"
URL: https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results

This dataset contains:
- 271,116 rows (one per athlete per event)
- Coverage: 1896-2016
- Includes: Name, Sex, Age, Height, Weight, Team, NOC, Games, Year, Season, City, Sport, Event, Medal

SETUP REQUIRED:
1. Install Kaggle API: pip install kaggle
2. Get Kaggle API credentials from https://www.kaggle.com/settings
3. Place kaggle.json in ~/.kaggle/ (or C:\\Users\\<username>\\.kaggle\\ on Windows)

Or manually:
1. Go to: https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results
2. Click "Download" 
3. Extract to the 'data/raw/' folder
"""

import pandas as pd
from pathlib import Path
import sys

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

print("\n" + "="*70)
print("KAGGLE OLYMPIC DATA DOWNLOADER")
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

if kaggle_available:
    print("\nAttempting to download dataset...")
    print("Dataset: heesoo37/120-years-of-olympic-history-athletes-and-results")
    
    try:
        # Download the dataset
        kaggle.api.dataset_download_files(
            'heesoo37/120-years-of-olympic-history-athletes-and-results',
            path=RAW_DIR,
            unzip=True
        )
        print(f"✓ Downloaded to {RAW_DIR}")
        
        # Check what files we got
        files = list(RAW_DIR.glob("*.csv"))
        print(f"\nFiles downloaded:")
        for f in files:
            print(f"  - {f.name}")
            
    except Exception as e:
        print(f"\n✗ Download failed: {e}")
        print("\nManual download instructions:")
        print("1. Go to: https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results")
        print("2. Click 'Download'")
        print(f"3. Extract athlete_events.csv to: {RAW_DIR}")
else:
    print("\n" + "="*70)
    print("MANUAL DOWNLOAD INSTRUCTIONS")
    print("="*70)
    print("\n1. Go to: https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results")
    print("2. Click 'Download' button")
    print(f"3. Extract the ZIP file")
    print(f"4. Copy 'athlete_events.csv' to: {RAW_DIR}")
    print("\nThen run: python scripts/process_kaggle_data.py")

print("\n" + "="*70 + "\n")
