"""
Update by_year CSVs with Olympedia-scraped medal data.

This script:
1. Updates existing year/country rows with corrected Olympedia medal counts
2. Adds new year rows (e.g., 2026 Winter) from Olympedia data
3. Does NOT touch pre-Olympedia years — those retain original Kaggle data

by_year CSVs have 6 columns: Year, Country, Gold, Silver, Bronze, Total
Olympedia CSVs have additional columns (Total_Athletes, etc.) which are only
used by merge_all_new_data.py for all_metrics; this script only uses the 6 basics.
"""

import pandas as pd
from pathlib import Path

MEDAL_COLS = ['Gold', 'Silver', 'Bronze', 'Total']
BY_YEAR_COLS = ['Year', 'Country'] + MEDAL_COLS

def update_by_year(by_year_path, olympedia_path, season_label):
    """Update a by_year CSV with Olympedia corrections and new rows."""
    by = pd.read_csv(by_year_path)
    oly = pd.read_csv(olympedia_path)

    oly_years = sorted(oly['Year'].unique())
    print(f"\n{season_label}: by_year has {len(by)} rows, years {by['Year'].min()}-{by['Year'].max()}")
    print(f"  Olympedia has {len(oly)} rows for years {oly_years}")

    # --- Update existing year/country pairs ---
    existing_mask = by.set_index(['Year', 'Country']).index.isin(
        oly.set_index(['Year', 'Country']).index
    )
    n_updated = 0
    for _, orow in oly.iterrows():
        mask = (by['Year'] == orow['Year']) & (by['Country'] == orow['Country'])
        if mask.any():
            for col in MEDAL_COLS:
                old_val = by.loc[mask, col].values[0]
                new_val = int(orow[col])
                if old_val != new_val:
                    n_updated += 1
                    print(f"  Corrected {orow['Country']} {orow['Year']} {col}: {old_val} -> {new_val}")
                by.loc[mask, col] = new_val

    # --- Add new year rows ---
    existing_pairs = set(zip(by['Year'], by['Country']))
    new_rows = []
    for _, orow in oly.iterrows():
        if (orow['Year'], orow['Country']) not in existing_pairs:
            new_rows.append({col: orow[col] for col in BY_YEAR_COLS})
    
    if new_rows:
        by = pd.concat([by, pd.DataFrame(new_rows)], ignore_index=True)
        new_years = sorted(set(r['Year'] for r in new_rows))
        print(f"  Added {len(new_rows)} new rows for years {new_years}")

    by = by.sort_values(['Year', 'Country']).reset_index(drop=True)
    by.to_csv(by_year_path, index=False)
    print(f"  Saved: {by_year_path.name} ({len(by)} rows, years {by['Year'].min()}-{by['Year'].max()})")
    
    if n_updated == 0:
        print("  No medal corrections needed for existing rows.")
    
    return by

def main():
    data = Path(__file__).parent.parent / 'data'

    update_by_year(
        data / 'summer_olympics_by_year.csv',
        data / 'olympedia_summer.csv',
        'Summer'
    )
    update_by_year(
        data / 'winter_olympics_by_year.csv',
        data / 'olympedia_winter.csv',
        'Winter'
    )

if __name__ == '__main__':
    main()
