"""
Collect military spending and personnel data as TIME SERIES from World Bank API.

This replaces the previous hardcoded snapshot approach with actual API-sourced
time-series data from the World Bank's development indicators.

Data sources:
- MS.MIL.XPND.GD.ZS: Military expenditure (% of GDP) — World Bank/SIPRI
- MS.MIL.TOTL.P1: Armed forces personnel, total — World Bank/IISS

Using % of GDP avoids distortions from hyperinflation and exchange-rate
fluctuations (e.g. Venezuela) that plague per-capita USD figures.

Coverage tested:
- Military expenditure (% GDP): 2000-2023, excellent coverage across countries
- Armed forces personnel: 2000-2020, excellent coverage across countries
"""

import pandas as pd
import requests
import time
from pathlib import Path

data_dir = Path(__file__).parent.parent / "data"
WB_BASE_URL = "https://api.worldbank.org/v2"

# Load country codes from existing WB dataset
world_bank_data = pd.read_csv(data_dir / "world_bank_data.csv")
country_codes = world_bank_data['WB_Code'].unique()

# Retry-capable session
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    max_retries=requests.packages.urllib3.util.retry.Retry(
        total=5, backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
)
session.mount('https://', adapter)
session.mount('http://', adapter)


def fetch_wb_indicator(indicator_code, indicator_name, start_year=2000, end_year=2026):
    """Fetch a World Bank indicator for all countries via bulk API."""
    print(f"\nFetching {indicator_name} ({indicator_code})...")
    
    country_set = set(country_codes)
    all_data = []
    page = 1
    total_pages = 1
    
    while page <= total_pages:
        url = f"{WB_BASE_URL}/country/all/indicator/{indicator_code}"
        params = {
            'format': 'json',
            'per_page': 10000,
            'date': f'{start_year}:{end_year}',
            'page': page
        }
        
        for attempt in range(5):
            try:
                response = session.get(url, params=params, timeout=(10, 60))
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 1 and data[1]:
                        total_pages = data[0].get('pages', 1)
                        for record in data[1]:
                            country = record.get('countryiso3code', '')
                            if country in country_set and record['value'] is not None:
                                all_data.append({
                                    'WB_Code': country,
                                    'Year': int(record['date']),
                                    indicator_name: record['value']
                                })
                    print(f"  Page {page}/{total_pages} OK ({len(all_data)} records)")
                break
            except Exception as e:
                if attempt < 4:
                    wait = 2 ** attempt
                    print(f"  Retry {attempt+1} page {page}: {e} (wait {wait}s)")
                    time.sleep(wait)
                else:
                    print(f"  FAILED page {page}: {e}")
        page += 1
        time.sleep(0.5)
    
    df = pd.DataFrame(all_data)
    if not df.empty:
        countries_with_data = df['WB_Code'].nunique()
        year_range = f"{df['Year'].min()}-{df['Year'].max()}"
        print(f"  ✓ {len(df)} records, {countries_with_data} countries, years {year_range}")
    else:
        print(f"  ✗ No data returned")
    
    return df


def collect_military_data():
    """
    Collect military expenditure and personnel data from World Bank API.
    
    Produces a time-series CSV with:
    - WB_Code, Year
    - Military_Expenditure_Pct_GDP (% of GDP — immune to exchange-rate distortions)
    - Active_Military_Personnel (total persons)
    - Active_Military_Personnel_Thousands (computed from personnel / 1000)
    """
    
    # Fetch military expenditure (% of GDP)
    expenditure_df = fetch_wb_indicator(
        'MS.MIL.XPND.GD.ZS', 
        'Military_Expenditure_Pct_GDP'
    )
    
    # Fetch armed forces personnel (total)
    personnel_df = fetch_wb_indicator(
        'MS.MIL.TOTL.P1', 
        'Active_Military_Personnel'
    )
    
    # Merge expenditure and personnel
    if not expenditure_df.empty and not personnel_df.empty:
        merged = expenditure_df.merge(personnel_df, on=['WB_Code', 'Year'], how='outer')
    elif not expenditure_df.empty:
        merged = expenditure_df
    elif not personnel_df.empty:
        merged = personnel_df
    else:
        print("ERROR: No data collected!")
        return None
    
    merged['Year'] = merged['Year'].astype(int)
    
    # Round % GDP and compute derived columns
    merged['Military_Expenditure_Pct_GDP'] = merged['Military_Expenditure_Pct_GDP'].round(3)
    
    merged['Active_Military_Personnel_Thousands'] = (
        merged['Active_Military_Personnel'] / 1000
    ).round(1)
    
    # Sort
    merged = merged.sort_values(['WB_Code', 'Year']).reset_index(drop=True)
    
    # Save full time-series
    output_cols = [
        'WB_Code', 'Year',
        'Military_Expenditure_Pct_GDP',
        'Active_Military_Personnel',
        'Active_Military_Personnel_Thousands'
    ]
    output_df = merged[output_cols]
    
    output_file = data_dir / "military_data.csv"
    output_df.to_csv(output_file, index=False)
    
    print(f"\n{'=' * 60}")
    print(f"✓ Saved {output_file}")
    print(f"  Total records: {len(output_df)}")
    print(f"  Countries: {output_df['WB_Code'].nunique()}")
    print(f"  Year range: {output_df['Year'].min()}-{output_df['Year'].max()}")
    print(f"  With expenditure (% GDP) data: {output_df['Military_Expenditure_Pct_GDP'].notna().sum()}")
    print(f"  With personnel data: {output_df['Active_Military_Personnel'].notna().sum()}")
    
    # Summary by year
    print(f"\n  Coverage by year (countries with expenditure data):")
    year_coverage = output_df.groupby('Year')['Military_Expenditure_Pct_GDP'].apply(
        lambda x: x.notna().sum()
    )
    for year, count in year_coverage.items():
        print(f"    {year}: {count} countries")
    
    return output_df


if __name__ == "__main__":
    print("=" * 60)
    print("COLLECTING MILITARY DATA (TIME SERIES)")
    print("World Bank API: MS.MIL.XPND.GD.ZS + MS.MIL.TOTL.P1")
    print("=" * 60)
    collect_military_data()
