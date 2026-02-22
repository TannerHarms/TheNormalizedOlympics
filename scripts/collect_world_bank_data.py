"""
Collect normalization data from World Bank API

This script fetches population, GDP, and GDP per capita data for all Olympic countries
from 1960 onwards (World Bank data availability).

Data sources:
- SP.POP.TOTL: Population, total
- NY.GDP.MKTP.CD: GDP (current US$)
- NY.GDP.PCAP.CD: GDP per capita (current US$)
"""

import pandas as pd
import requests
from pathlib import Path
import time
from country_mapping import get_wb_code, is_historical

DATA_DIR = Path(__file__).parent.parent / "data"

# World Bank indicator codes
INDICATORS = {
    'SP.POP.TOTL': 'Population',
    'NY.GDP.MKTP.CD': 'GDP',
    'NY.GDP.PCAP.CD': 'GDP_per_capita'
}

# World Bank API base URL
WB_API_BASE = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"

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

def fetch_indicator_data(country_code, indicator_code, start_year=1960, end_year=2026):
    """
    Fetch a single indicator for a country from World Bank API.
    
    Returns:
        DataFrame with columns: Year, value
    """
    url = WB_API_BASE.format(country=country_code, indicator=indicator_code)
    params = {
        'date': f'{start_year}:{end_year}',
        'format': 'json',
        'per_page': 1000
    }
    
    try:
        response = session.get(url, params=params, timeout=(10, 30))
        response.raise_for_status()
        
        data = response.json()
        
        if len(data) < 2 or not data[1]:
            return None
        
        # Parse the JSON response
        records = []
        for item in data[1]:
            if item['value'] is not None:
                records.append({
                    'Year': int(item['date']),
                    'value': float(item['value'])
                })
        
        if records:
            return pd.DataFrame(records)
        return None
        
    except Exception as e:
        return None


def fetch_world_bank_data(countries, indicators, start_year=1960, end_year=2026):
    """
    Fetch World Bank data for multiple countries and indicators.
    
    Args:
        countries: List of World Bank country codes
        indicators: Dict of {indicator_code: column_name}
        start_year: Starting year for data collection
        end_year: Ending year for data collection
    
    Returns:
        DataFrame with columns: WB_Code, Year, and indicator values
    """
    print(f"\nFetching data for {len(countries)} countries...")
    print(f"Period: {start_year}-{end_year}")
    print(f"Indicators: {', '.join(indicators.values())}")
    
    all_data = []
    failed_countries = []
    
    for i, country_code in enumerate(countries, 1):
        print(f"  [{i}/{len(countries)}] Fetching {country_code}...", end=" ", flush=True)
        
        try:
            country_data = {'WB_Code': country_code}
            indicator_dfs = {}
            
            # Fetch each indicator
            for ind_code, ind_name in indicators.items():
                df = fetch_indicator_data(country_code, ind_code, start_year, end_year)
                if df is not None:
                    indicator_dfs[ind_name] = df.set_index('Year')['value']
            
            if indicator_dfs:
                # Combine all indicators
                combined = pd.DataFrame(indicator_dfs)
                combined = combined.reset_index()
                combined.insert(0, 'WB_Code', country_code)
                
                all_data.append(combined)
                print(f"✓ ({len(combined)} records)")
            else:
                print("✗ No data")
                failed_countries.append(country_code)
            
            # Be nice to the API
            time.sleep(0.2)
            
        except Exception as e:
            print(f"✗ Error: {str(e)[:50]}")
            failed_countries.append(country_code)
            continue
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"\n✓ Successfully fetched data for {len(countries) - len(failed_countries)}/{len(countries)} countries")
        
        if failed_countries:
            print(f"✗ Failed countries: {', '.join(failed_countries[:10])}")
            if len(failed_countries) > 10:
                print(f"   ... and {len(failed_countries) - 10} more")
        
        return combined_df
    else:
        print("\n✗ No data fetched")
        return pd.DataFrame()


def main():
    print("\n" + "="*70)
    print("COLLECTING WORLD BANK NORMALIZATION DATA")
    print("="*70)
    
    # Load Olympic data to get list of countries
    print("\nLoading Olympic data to identify countries...")
    summer_df = pd.read_csv(DATA_DIR / "summer_olympics_by_year.csv")
    winter_df = pd.read_csv(DATA_DIR / "winter_olympics_by_year.csv")
    
    # Get unique countries from both datasets
    all_noc_codes = set(summer_df['Country'].unique()) | set(winter_df['Country'].unique())
    print(f"  Found {len(all_noc_codes)} unique Olympic countries/codes")
    
    # Map to World Bank codes
    wb_codes = []
    unmapped = []
    historical = []
    
    for noc in all_noc_codes:
        wb_code = get_wb_code(noc)
        if wb_code:
            wb_codes.append(wb_code)
        elif is_historical(noc):
            historical.append(noc)
        else:
            unmapped.append(noc)
    
    # Remove duplicates (some NOCs map to same WB code)
    wb_codes = sorted(set(wb_codes))
    
    print(f"  Mapped to {len(wb_codes)} World Bank countries")
    print(f"  Historical countries (no current data): {len(historical)}")
    if historical:
        print(f"    {', '.join(sorted(historical))}")
    
    if unmapped:
        print(f"  ⚠ Unmapped countries: {len(unmapped)}")
        print(f"    {', '.join(sorted(unmapped)[:10])}")
        if len(unmapped) > 10:
            print(f"    ... and {len(unmapped) - 10} more")
    
    # Fetch the data
    print("\n" + "-"*70)
    print("FETCHING DATA FROM WORLD BANK API")
    print("-"*70)
    
    df = fetch_world_bank_data(wb_codes, INDICATORS, start_year=1960, end_year=2026)
    
    if df.empty:
        print("\n✗ No data collected. Exiting.")
        return
    
    # Clean up the data
    print("\n" + "-"*70)
    print("PROCESSING DATA")
    print("-"*70)
    
    print(f"  Raw records: {len(df)}")
    
    # Remove rows where all indicators are null
    indicator_cols = list(INDICATORS.values())
    df = df.dropna(subset=indicator_cols, how='all')
    print(f"  After removing empty rows: {len(df)}")
    
    # Reorder columns
    df = df[['WB_Code', 'Year'] + indicator_cols]
    
    # Sort by country and year
    df = df.sort_values(['WB_Code', 'Year'])
    
    # Save to CSV
    output_file = DATA_DIR / "world_bank_data.csv"
    df.to_csv(output_file, index=False)
    
    print(f"\n✓ Saved: {output_file}")
    print(f"  Total records: {len(df):,}")
    print(f"  Countries: {df['WB_Code'].nunique()}")
    print(f"  Year range: {int(df['Year'].min())}-{int(df['Year'].max())}")
    
    # Show sample
    print("\n" + "-"*70)
    print("SAMPLE DATA (USA, most recent 5 years)")
    print("-"*70)
    sample = df[df['WB_Code'] == 'USA'].tail(5)
    if not sample.empty:
        print(sample.to_string(index=False))
    
    # Show data coverage statistics
    print("\n" + "-"*70)
    print("DATA COVERAGE BY INDICATOR")
    print("-"*70)
    for col in indicator_cols:
        non_null = df[col].notna().sum()
        pct = 100 * non_null / len(df)
        print(f"  {col:20}: {non_null:,} / {len(df):,} ({pct:.1f}%)")
    
    print("\n" + "="*70)
    print("✓ WORLD BANK DATA COLLECTION COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Merge this data with Olympic medal data")
    print("  2. Calculate normalized metrics (medals per capita, etc.)")
    print("  3. Collect HDI data from UNDP")
    print("  4. Collect climate data")
    print("\n")


if __name__ == "__main__":
    main()
