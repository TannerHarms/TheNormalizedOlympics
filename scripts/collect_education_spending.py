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

# Retry-capable session
_session = requests.Session()
_adapter = requests.adapters.HTTPAdapter(
    max_retries=requests.packages.urllib3.util.retry.Retry(
        total=5, backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
)
_session.mount('https://', _adapter)
_session.mount('http://', _adapter)

def fetch_indicator_data(country_code, indicator, start_year=1960, end_year=2026):
    """Legacy per-country fetch — kept for compatibility but unused."""
    pass


def fetch_all_bulk(indicator, wb_countries, start_year=1960, end_year=2026):
    """
    Fetch a WB indicator for ALL countries in one bulk API call.
    Much faster and more reliable than per-country fetching.
    """
    wb_set = set(wb_countries)
    all_data = []
    page = 1
    total_pages = 1
    
    while page <= total_pages:
        url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}"
        params = {
            'date': f'{start_year}:{end_year}',
            'format': 'json',
            'per_page': 10000,
            'page': page
        }
        
        for attempt in range(5):
            try:
                response = _session.get(url, params=params, timeout=(10, 60))
                response.raise_for_status()
                data = response.json()
                
                if len(data) > 1 and data[1]:
                    total_pages = data[0].get('pages', 1)
                    for record in data[1]:
                        country = record.get('countryiso3code', '')
                        if country in wb_set and record.get('value') is not None:
                            all_data.append({
                                'WB_Code': country,
                                'Year': int(record['date']),
                                'Education_Spending_pct_GDP': float(record['value'])
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
    
    return all_data


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
    print(f"Period: 1960-2026")
    print(f"Fetching bulk data for {len(wb_countries)} countries...")
    print()
    
    all_data = fetch_all_bulk(indicator, wb_countries)
    
    success_count = len(set(r['WB_Code'] for r in all_data))
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
