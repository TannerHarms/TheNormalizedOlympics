"""
Add recent Olympics data (2018, 2020, 2022, 2024) to the existing dataset
Maintains the same format as the Kaggle data
"""

import pandas as pd
from pathlib import Path
import time
import requests
from io import StringIO

DATA_DIR = Path(__file__).parent.parent / "data"

# Setup headers to avoid 403 errors
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Recent Olympics to add
RECENT_OLYMPICS = {
    'summer': {
        2020: "2020_Summer_Olympics_medal_table",  # Held in 2021
        2024: "2024_Summer_Olympics_medal_table",
    },
    'winter': {
        2018: "2018_Winter_Olympics_medal_table",
        2022: "2022_Winter_Olympics_medal_table",
    }
}

def fetch_medal_table(year, wiki_page):
    """Fetch medal table from Wikipedia for a specific Olympics"""
    url = f"https://en.wikipedia.org/wiki/{wiki_page}"
    
    try:
        print(f"  Fetching {year}...", end=" ", flush=True)
        
        # Fetch page with headers
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        # Read all tables from the page
        tables = pd.read_html(StringIO(response.text))
        
        # Find the main medal table
        for table in tables:
            # Check if this looks like a medal table
            cols_str = str(table.columns).lower()
            if 'gold' in cols_str and 'silver' in cols_str and 'bronze' in cols_str:
                if len(table) >= 20:  # Main medal table should have many countries
                    df = table.copy()
                    
                    # Flatten multi-level columns if needed
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = [' '.join(str(c).strip() for c in col if str(c).strip() != 'nan') 
                                     for col in df.columns]
                    
                    # Find the relevant columns
                    # Country column
                    country_col = None
                    for col in df.columns:
                        col_lower = str(col).lower()
                        if any(x in col_lower for x in ['noc', 'nation', 'team', 'country']):
                            country_col = col
                            break
                    
                    if country_col is None:
                        country_col = df.columns[0]
                    
                    # Medal columns
                    gold_col = [c for c in df.columns if 'gold' in str(c).lower()][0]
                    silver_col = [c for c in df.columns if 'silver' in str(c).lower()][0]
                    bronze_col = [c for c in df.columns if 'bronze' in str(c).lower()][0]
                    total_cols = [c for c in df.columns if 'total' in str(c).lower()]
                    total_col = total_cols[0] if total_cols else None
                    
                    # Create result dataframe with proper structure
                    result = pd.DataFrame({
                        'Year': year,
                        'Country': df[country_col].astype(str),
                        'Gold': pd.to_numeric(df[gold_col], errors='coerce').fillna(0),
                        'Silver': pd.to_numeric(df[silver_col], errors='coerce').fillna(0),
                        'Bronze': pd.to_numeric(df[bronze_col], errors='coerce').fillna(0),
                    })
                    
                    if total_col:
                        result['Total'] = pd.to_numeric(df[total_col], errors='coerce').fillna(0)
                    else:
                        result['Total'] = result['Gold'] + result['Silver'] + result['Bronze']
                    
                    # Clean country names (remove footnotes, special characters, unicode issues)
                    result['Country'] = result['Country'].str.replace(r'\s*\[.*?\]', '', regex=True)
                    result['Country'] = result['Country'].str.replace(r'\s*\(.*?\)', '', regex=True)
                    result['Country'] = result['Country'].str.strip()
                    result['Country'] = result['Country'].str.replace(r'[\*\u2020\u2021\u00a0]+', '', regex=True)
                    result['Country'] = result['Country'].str.strip()
                    
                    # Remove rows with no medals or invalid countries
                    result = result[result['Total'] > 0]
                    result = result[result['Country'].str.len() > 0]
                    result = result[~result['Country'].str.lower().str.contains('total|rank', na=False)]
                    
                    # Reorder columns to match existing format
                    result = result[['Year', 'Country', 'Gold', 'Silver', 'Bronze', 'Total']]
                    
                    print(f"✓ ({len(result)} countries)")
                    return result
        
        print("✗ Table not found")
        return None
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def add_recent_data(season):
    """Add recent Olympics data for a season (summer or winter)"""
    
    # Determine file paths
    filename = f"{season}_olympics_by_year.csv"
    filepath = DATA_DIR / filename
    
    if not filepath.exists():
        print(f"✗ File not found: {filename}")
        return False
    
    # Load existing data
    existing_df = pd.read_csv(filepath)
    max_existing_year = int(existing_df['Year'].max())
    
    print(f"\n{season.upper()} OLYMPICS")
    print("-" * 70)
    print(f"Current data: {int(existing_df['Year'].min())}-{max_existing_year}")
    print(f"Adding recent games...")
    
    # Collect recent Olympics data
    recent_data = []
    olympics_to_add = RECENT_OLYMPICS[season]
    
    for year in sorted(olympics_to_add.keys()):
        if year > max_existing_year:
            wiki_page = olympics_to_add[year]
            df = fetch_medal_table(year, wiki_page)
            if df is not None:
                recent_data.append(df)
            time.sleep(0.5)  # Be nice to Wikipedia
    
    if not recent_data:
        print("No new data to add")
        return False
    
    # Combine with existing data
    combined_df = pd.concat([existing_df] + recent_data, ignore_index=True)
    combined_df = combined_df.sort_values(['Year', 'Total'], ascending=[True, False])
    
    # Save updated data
    combined_df.to_csv(filepath, index=False)
    
    print(f"\n✓ Updated {filename}")
    print(f"  Years now: {int(combined_df['Year'].min())}-{int(combined_df['Year'].max())}")
    print(f"  Total records: {len(combined_df)}")
    print(f"  Added: {len(combined_df) - len(existing_df)} new records")
    
    return True


# Main execution
print("\n" + "="*70)
print("ADDING RECENT OLYMPICS DATA")
print("="*70)

success_summer = add_recent_data('summer')
success_winter = add_recent_data('winter')

print("\n" + "="*70)
if success_summer or success_winter:
    print("✓ RECENT DATA ADDED SUCCESSFULLY!")
    print("="*70)
    print("\nYour dataset now includes:")
    print("  - Summer Olympics: 1896-2024")
    print("  - Winter Olympics: 1924-2022")
    print("\nRun 'python scripts/preview_yearly_data.py' to see updated data")
else:
    print("⚠ NO NEW DATA ADDED")
    print("="*70)

print("\n")
