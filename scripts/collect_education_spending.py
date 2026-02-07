"""
Collect education spending data from World Bank.

Indicator: SE.XPD.TOTL.GD.ZS
Government expenditure on education, total (% of GDP)

This helps analyze whether education investment correlates with Olympic success.
"""

import pandas as pd
import requests
import sys
from pathlib import Path
import time

sys.path.append(str(Path(__file__).parent.parent))
from scripts.country_mapping import NOC_TO_WB

def fetch_indicator_data(country_code, indicator, start_year=1960, end_year=2024):
    """
    Fetch a single indicator for a country from World Bank API.
    
    Args:
        country_code: ISO3 country code
        indicator: World Bank indicator code
        start_year: Start year
        end_year: End year
    
    Returns:
        List of {year, value} dicts
    """
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}"
    params = {
        'date': f'{start_year}:{end_year}',
        'format': 'json',
        'per_page': 1000
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if len(data) < 2:
            return []
        
        records = data[1] if isinstance(data, list) and len(data) > 1 else []
        
        result = []
        for record in records:
            if record.get('value') is not None:
                result.append({
                    'year': int(record['date']),
                    'value': float(record['value'])
                })
        
        return result
        
    except Exception as e:
        return []


def main():
    print("=" * 70)
    print("COLLECTING EDUCATION SPENDING DATA")
    print("=" * 70)
    print()
    
    # Load Olympic countries
    print("Loading Olympic countries...")
    data_dir = Path(__file__).parent.parent / 'data'
    
    summer = pd.read_csv(data_dir / 'summer_olympics_by_year.csv')
    winter = pd.read_csv(data_dir / 'winter_olympics_by_year.csv')
    
    # Get unique Olympic country codes
    olympic_countries = set(summer['Country'].unique()) | set(winter['Country'].unique())
    
    # Map to World Bank codes
    wb_countries = set()
    for noc in olympic_countries:
        wb_code = NOC_TO_WB.get(noc)
        if wb_code and len(wb_code) == 3:  # Valid ISO3 code
            wb_countries.add(wb_code)
    
    wb_countries = sorted(wb_countries)
    
    print(f"  Olympic countries: {len(olympic_countries)}")
    print(f"  Mapped to World Bank: {len(wb_countries)}")
    print()
    
    print("-" * 70)
    print("FETCHING EDUCATION SPENDING DATA")
    print("-" * 70)
    print()
    
    # World Bank indicator for education spending
    indicator = 'SE.XPD.TOTL.GD.ZS'  # Government expenditure on education (% of GDP)
    
    print(f"Indicator: {indicator}")
    print(f"Period: 1960-2024")
    print(f"Fetching data for {len(wb_countries)} countries...")
    print()
    
    all_data = []
    success_count = 0
    
    for i, country in enumerate(wb_countries, 1):
        print(f"  [{i}/{len(wb_countries)}] Fetching {country}...", end=' ')
        
        records = fetch_indicator_data(country, indicator)
        
        if records:
            for record in records:
                all_data.append({
                    'WB_Code': country,
                    'Year': record['year'],
                    'Education_Spending_pct_GDP': record['value']
                })
            success_count += 1
            print(f"✓ ({len(records)} records)")
        else:
            print("✗ (no data)")
        
        # Rate limiting
        time.sleep(0.1)
    
    print()
    print(f"✓ Successfully fetched data for {success_count}/{len(wb_countries)} countries")
    print()
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    if len(df) == 0:
        print("✗ No data collected")
        return
    
    # Sort
    df = df.sort_values(['WB_Code', 'Year'])
    
    # Save
    output_path = data_dir / 'education_spending.csv'
    df.to_csv(output_path, index=False)
    
    print("-" * 70)
    print("DATA SUMMARY")
    print("-" * 70)
    print(f"  Total records: {len(df):,}")
    print(f"  Countries: {df['WB_Code'].nunique()}")
    print(f"  Year range: {df['Year'].min()}-{df['Year'].max()}")
    print()
    
    # Coverage statistics
    print("Data coverage:")
    total_possible = len(wb_countries) * (2024 - 1960 + 1)
    coverage_pct = 100 * len(df) / total_possible
    print(f"  {len(df):,} / {total_possible:,} ({coverage_pct:.1f}%)")
    print()
    
    # Show sample
    print("-" * 70)
    print("SAMPLE DATA (USA, recent years)")
    print("-" * 70)
    usa_recent = df[df['WB_Code'] == 'USA'].tail(10)
    if len(usa_recent) > 0:
        print(usa_recent.to_string(index=False))
    else:
        print("No USA data available")
    print()
    
    # Show top spenders (most recent year with data)
    print("-" * 70)
    print("TOP EDUCATION SPENDERS (most recent year)")
    print("-" * 70)
    latest_year = df['Year'].max()
    latest_data = df[df['Year'] == latest_year].sort_values(
        'Education_Spending_pct_GDP', ascending=False
    ).head(10)
    
    print(f"\nYear: {latest_year}")
    print(latest_data.to_string(index=False))
    print()
    
    print("=" * 70)
    print("✓ EDUCATION SPENDING DATA COLLECTION COMPLETE!")
    print("=" * 70)
    print(f"Saved to: {output_path}")
    print()


if __name__ == '__main__':
    main()
