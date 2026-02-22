"""
Collect Human Development Index (HDI) data from UNDP.

Data source: UNDP Human Development Reports
URL: https://hdr.undp.org/data-center/documentation-and-downloads

HDI Components:
- Life expectancy at birth
- Expected years of schooling
- Mean years of schooling
- GNI per capita (PPP)
"""

import pandas as pd
import requests
import sys
from pathlib import Path
import time

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from scripts.country_mapping import NOC_TO_WB

def fetch_hdi_data():
    """
    Fetch HDI data from UNDP data API.
    
    UNDP API endpoint: https://hdr.undp.org/sites/default/files/2021-22_HDR/HDR21-22_Composite_indices_complete_time_series.csv
    
    Note: UNDP uses ISO3 country codes, same as World Bank.
    """
    print("=" * 70)
    print("COLLECTING HDI DATA FROM UNDP")
    print("=" * 70)
    print()
    
    # UNDP provides a direct CSV download with complete time series
    # This is the most recent complete dataset
    url = "https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Composite_indices_complete_time_series.csv"
    
    print(f"Fetching HDI data from UNDP...")
    print(f"URL: {url}")
    print()
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Save raw CSV
        raw_path = Path(__file__).parent.parent / 'data' / 'hdi_raw.csv'
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(raw_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ Downloaded raw HDI data")
        print(f"  Saved to: {raw_path}")
        print()
        
        # Read and process the CSV (try multiple encodings)
        for enc in ['utf-8', 'latin-1', 'cp1252', 'utf-8-sig']:
            try:
                df = pd.read_csv(raw_path, encoding=enc)
                print(f"Read CSV with encoding: {enc}")
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        else:
            raise ValueError("Could not decode HDI CSV with any known encoding")
        
        print(f"Raw data shape: {df.shape}")
        print(f"Columns: {list(df.columns)[:10]}...")  # Show first 10 columns
        print()
        
        return df
        
    except Exception as e:
        print(f"✗ Error fetching HDI data: {e}")
        return None


def process_hdi_data(raw_df):
    """
    Process raw UNDP HDI data into year-by-year format.
    
    The UNDP CSV has:
    - Rows for each country
    - Columns for different indicators and years
    - Format: country, iso3, hdi_1990, hdi_1991, ..., hdi_2021
    """
    print("-" * 70)
    print("PROCESSING HDI DATA")
    print("-" * 70)
    print()
    
    # Look for HDI columns (they typically have years in them)
    print("Available columns:")
    for col in raw_df.columns[:20]:  # Show first 20
        print(f"  - {col}")
    print()
    
    # The CSV structure varies by year, so we need to inspect it
    # Typical format has columns like: 'hdi_1990', 'hdi_1991', etc.
    # Or it might be in long format
    
    # Try to identify the structure
    if 'iso3' in raw_df.columns and 'year' in raw_df.columns and 'hdi' in raw_df.columns:
        # Long format - already in year-by-year format
        print("Detected long format (year-by-year)")
        processed_df = raw_df[['iso3', 'year', 'hdi']].copy()
        processed_df.columns = ['WB_Code', 'Year', 'HDI']
        
    elif 'iso3' in raw_df.columns:
        # Wide format - need to reshape
        print("Detected wide format (years as columns)")
        
        # Find HDI columns (year columns)
        hdi_cols = [col for col in raw_df.columns if col.startswith('hdi_') or col.isdigit()]
        
        if not hdi_cols:
            # Try alternative naming conventions
            hdi_cols = [col for col in raw_df.columns if any(str(year) in col for year in range(1990, 2025))]
        
        print(f"Found {len(hdi_cols)} HDI year columns")
        print(f"Sample columns: {hdi_cols[:5]}")
        print()
        
        # Reshape from wide to long
        id_col = 'iso3' if 'iso3' in raw_df.columns else 'ISO3'
        
        # Melt the dataframe
        processed_df = raw_df.melt(
            id_vars=[id_col],
            value_vars=hdi_cols,
            var_name='Year',
            value_name='HDI'
        )
        
        # Extract year from column name
        processed_df['Year'] = processed_df['Year'].str.extract(r'(\d{4})', expand=False)
        processed_df['Year'] = pd.to_numeric(processed_df['Year'], errors='coerce')
        
        # Rename iso3 column
        processed_df = processed_df.rename(columns={id_col: 'WB_Code'})
        
    else:
        print("✗ Could not identify CSV structure")
        return None
    
    # Clean the data
    processed_df = processed_df.dropna(subset=['WB_Code', 'Year'])
    processed_df['Year'] = processed_df['Year'].astype(int)
    processed_df['HDI'] = pd.to_numeric(processed_df['HDI'], errors='coerce')
    
    # Remove rows with no HDI value
    processed_df = processed_df.dropna(subset=['HDI'])
    
    # Remove duplicates - keep HDI in valid range (0.3-1.0)
    # Filter to reasonable HDI range
    processed_df = processed_df[(processed_df['HDI'] >= 0.3) & (processed_df['HDI'] <= 1.0)]
    
    # If still duplicates, keep first occurrence (main HDI value)
    processed_df = processed_df.drop_duplicates(subset=['WB_Code', 'Year'], keep='first')
    
    # Sort
    processed_df = processed_df.sort_values(['WB_Code', 'Year'])
    
    print(f"✓ Processed {len(processed_df)} records")
    print(f"  Countries: {processed_df['WB_Code'].nunique()}")
    print(f"  Year range: {processed_df['Year'].min()}-{processed_df['Year'].max()}")
    print()
    
    return processed_df


def main():
    # Fetch raw data
    raw_df = fetch_hdi_data()
    
    if raw_df is None:
        print("Failed to fetch HDI data")
        return
    
    # Process the data
    processed_df = process_hdi_data(raw_df)
    
    if processed_df is None:
        print("Failed to process HDI data")
        return
    
    # Save processed data
    output_path = Path(__file__).parent.parent / 'data' / 'hdi_data.csv'
    processed_df.to_csv(output_path, index=False)
    
    print("-" * 70)
    print("SAMPLE DATA (USA, most recent years)")
    print("-" * 70)
    usa_recent = processed_df[processed_df['WB_Code'] == 'USA'].tail(10)
    print(usa_recent.to_string(index=False))
    print()
    
    print("=" * 70)
    print("✓ HDI DATA COLLECTION COMPLETE!")
    print("=" * 70)
    print(f"Saved to: {output_path}")
    print(f"Total records: {len(processed_df):,}")
    print(f"Countries: {processed_df['WB_Code'].nunique()}")
    print(f"Year range: {processed_df['Year'].min()}-{processed_df['Year'].max()}")
    print()


if __name__ == '__main__':
    main()
