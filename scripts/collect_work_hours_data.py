"""
Collect OECD average annual hours worked per worker as TIME SERIES.

This replaces the previous hardcoded snapshot approach with data from the
OECD SDMX API (data explorer).

Data source:
- OECD.ELS.SAE / DSD_HW@DF_AVG_ANN_HRS_WKD
  "Average annual hours actually worked per worker"

Coverage tested:
- 48 OECD/partner countries
- Years: 2005-2023 (some countries have data from 2000)
- Measure: Hours per year per person (total employment, actual hours)

Note: This is OECD data only — not available for most non-OECD countries.
The 3-letter country codes from OECD use ISO 3166-1 alpha-3, which matches
World Bank country codes (WB_Code).
"""

import pandas as pd
import requests
from pathlib import Path

data_dir = Path(__file__).parent.parent / "data"


def collect_work_hours_data():
    """
    Fetch average annual hours worked per worker from the OECD SDMX API.
    
    Uses the DF_AVG_ANN_HRS_WKD dataflow with filters for:
    - Total employment (LABOUR_FORCE_STATUS=EMP)
    - Total workers (WORKER_STATUS=_T)
    - Annual frequency (WORK_PERIOD=A)
    - Actual hours (HOURS_TYPE=ACTUAL)
    """
    
    print("Fetching OECD average annual hours worked...")
    
    # OECD SDMX API endpoint
    # 13 dimensions, using wildcards for most, filtering for total/actual/annual
    url = (
        "https://sdmx.oecd.org/public/rest/data/"
        "OECD.ELS.SAE,DSD_HW@DF_AVG_ANN_HRS_WKD,/"
        ".............A"  # 13 dots + A for annual frequency at end
        "?startPeriod=2000&endPeriod=2026"
    )
    
    headers = {'Accept': 'application/vnd.sdmx.data+json'}
    
    response = requests.get(url, headers=headers, timeout=60)
    
    if response.status_code != 200:
        print(f"ERROR: OECD API returned status {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return None
    
    data = response.json()
    datasets = data.get('data', {}).get('dataSets', [])
    
    if not datasets:
        print("ERROR: No datasets returned")
        return None
    
    # Parse dimension values
    structure = data['data']['structures'][0]
    series_dims = structure['dimensions']['series']
    obs_dims = structure['dimensions']['observation']
    
    # Get country codes (REF_AREA dimension)
    ref_area_dim = next(d for d in series_dims if d['id'] == 'REF_AREA')
    country_values = ref_area_dim['values']
    
    # Get time periods
    time_dim = obs_dims[0]
    time_values = time_dim['values']
    
    # Get labour force status dimension
    lfs_dim = next(d for d in series_dims if d['id'] == 'LABOUR_FORCE_STATUS')
    lfs_values = lfs_dim['values']
    
    # Get worker status dimension
    ws_dim = next(d for d in series_dims if d['id'] == 'WORKER_STATUS')
    ws_values = ws_dim['values']
    
    print(f"  Countries: {len(country_values)}")
    print(f"  Time periods: {len(time_values)} ({time_values[0]['id']}-{time_values[-1]['id']})")
    print(f"  Labour force statuses: {[v['id'] for v in lfs_values]}")
    print(f"  Worker statuses: {[v['id'] for v in ws_values]}")
    
    # Parse series data
    # We want: LABOUR_FORCE_STATUS=EMP (Employment), WORKER_STATUS=_T (Total)
    series_data = datasets[0].get('series', {})
    
    # Find the indices for our target filters
    emp_idx = next((i for i, v in enumerate(lfs_values) if v['id'] == 'EMP'), None)
    total_worker_idx = next((i for i, v in enumerate(ws_values) if v['id'] == '_T'), None)
    
    # Find dimension positions
    dim_positions = {d['id']: i for i, d in enumerate(series_dims)}
    lfs_pos = dim_positions['LABOUR_FORCE_STATUS']
    ws_pos = dim_positions['WORKER_STATUS']
    ref_area_pos = dim_positions['REF_AREA']
    
    all_records = []
    
    for series_key, series_val in series_data.items():
        key_parts = series_key.split(':')
        
        # Filter: only total employment, total workers
        if int(key_parts[lfs_pos]) != emp_idx:
            continue
        if int(key_parts[ws_pos]) != total_worker_idx:
            continue
        
        country_idx = int(key_parts[ref_area_pos])
        country_code = country_values[country_idx]['id']
        
        observations = series_val.get('observations', {})
        for time_idx_str, obs_val in observations.items():
            time_idx = int(time_idx_str)
            year = int(time_values[time_idx]['id'])
            hours = obs_val[0]  # First element is the value
            
            if hours is not None:
                all_records.append({
                    'WB_Code': country_code,
                    'Year': year,
                    'Avg_Work_Hours_Per_Year': round(hours, 1)
                })
    
    df = pd.DataFrame(all_records)
    
    if df.empty:
        print("ERROR: No records parsed!")
        return None
    
    # Remove aggregate codes (OECD average, EU, etc.) - keep only real country codes
    aggregate_codes = ['OECD', 'EU27_2020', 'EA19', 'EA20', 'G7', 'G20']
    df = df[~df['WB_Code'].isin(aggregate_codes)]
    
    # Sort
    df = df.sort_values(['WB_Code', 'Year']).reset_index(drop=True)
    
    # Save
    output_file = data_dir / "work_hours_data.csv"
    df.to_csv(output_file, index=False)
    
    print(f"\n{'=' * 60}")
    print(f"✓ Saved {output_file}")
    print(f"  Total records: {len(df)}")
    print(f"  Countries: {df['WB_Code'].nunique()}")
    print(f"  Year range: {df['Year'].min()}-{df['Year'].max()}")
    print(f"  Countries: {sorted(df['WB_Code'].unique().tolist())}")
    
    # Coverage by year
    print(f"\n  Coverage by year:")
    for year, group in df.groupby('Year'):
        print(f"    {year}: {len(group)} countries")
    
    return df


if __name__ == "__main__":
    print("=" * 60)
    print("COLLECTING WORK HOURS DATA (TIME SERIES)")
    print("OECD SDMX API: DF_AVG_ANN_HRS_WKD")
    print("=" * 60)
    collect_work_hours_data()
