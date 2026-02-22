"""
Script to collect additional normalization metrics for Olympic data analysis.

New metrics to collect:
1. Land area (sq km)
2. Average elevation (meters)
3. Coastal area/coastline length (km)
4. Average temperature (°C)
5. Days of sunshine per year
6. Number of universities
7. Number of professional sports stadiums
8. Internet users (number or %)
9. Coffee consumption (kg per capita)
10. Coca-Cola consumption (servings per capita)
11. Healthcare spending (% of GDP or $ per capita)
12. Life expectancy (years)
13. Number of cars (vehicles per 1000 people)
14. Average snowfall (cm per year)
15. Number of ski resorts
16. Average work hours (hours per year)
17. Country safety index (Global Peace Index or similar)

Data sources:
- World Bank API (for many metrics)
- Our World in Data
- CIA World Factbook
- National statistics agencies
- Manual compilation for some metrics
"""

import pandas as pd
import requests
import requests.adapters
import requests.packages.urllib3.util.retry
import time
from pathlib import Path

# World Bank API base
WB_BASE_URL = "https://api.worldbank.org/v2"

# Retry-capable session (solves SSL hangs)
session = requests.Session()
_adapter = requests.adapters.HTTPAdapter(
    max_retries=requests.packages.urllib3.util.retry.Retry(
        total=5, backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
)
session.mount('https://', _adapter)
session.mount('http://', _adapter)

# Load existing country codes
data_dir = Path(__file__).parent.parent / "data"
world_bank_data = pd.read_csv(data_dir / "world_bank_data.csv")
country_codes = set(world_bank_data['WB_Code'].unique())

def fetch_world_bank_indicator(indicator_code, indicator_name):
    """Fetch data from World Bank API for a specific indicator using bulk API."""
    print(f"\nFetching {indicator_name} ({indicator_code})...")
    
    all_data = []
    page = 1
    total_pages = 1
    
    while page <= total_pages:
        url = f"{WB_BASE_URL}/country/all/indicator/{indicator_code}"
        params = {
            'format': 'json',
            'per_page': 10000,
            'date': '1960:2026',
            'page': page
        }
        
        for attempt in range(5):
            try:
                response = session.get(url, params=params, timeout=(10, 60))
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 1 and data[1]:
                        # Get total pages from metadata
                        total_pages = data[0].get('pages', 1)
                        for record in data[1]:
                            country = record.get('countryiso3code', '')
                            if country in country_codes and record['value'] is not None:
                                all_data.append({
                                    'WB_Code': country,
                                    'Year': record['date'],
                                    indicator_name: record['value']
                                })
                    print(f"  Page {page}/{total_pages} OK ({len(all_data)} records so far)")
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
    print(f"  Collected {len(df)} records for {indicator_name}")
    return df

def collect_world_bank_metrics():
    """Collect all available metrics from World Bank."""
    
    indicators = {
        # Already have: Population, GDP, GDP per capita, Education spending
        
        # Geographic
        'AG.LND.TOTL.K2': 'Land_Area_SqKm',
        'AG.SRF.TOTL.K2': 'Surface_Area_SqKm',
        
        # Infrastructure & Development
        'IT.NET.USER.ZS': 'Internet_Users_Pct',
        'IS.VEH.NVEH.P3': 'Vehicles_Per_1000',
        
        # Health
        'SH.XPD.CHEX.GD.ZS': 'Healthcare_Spending_Pct_GDP',
        'SH.XPD.CHEX.PC.CD': 'Healthcare_Spending_Per_Capita_USD',
        'SP.DYN.LE00.IN': 'Life_Expectancy_Years',
        
        # Labor
        'SL.TLF.TOTL.IN': 'Labor_Force_Total',
        
        # Climate (limited in World Bank)
        'EN.ATM.CO2E.PC': 'CO2_Emissions_Per_Capita',  # Proxy for development
    }
    
    all_dfs = []
    
    for code, name in indicators.items():
        df = fetch_world_bank_indicator(code, name)
        if not df.empty:
            all_dfs.append(df)
        time.sleep(0.5)
    
    # Merge all dataframes
    if all_dfs:
        merged = all_dfs[0]
        for df in all_dfs[1:]:
            merged = merged.merge(df, on=['WB_Code', 'Year'], how='outer')
        
        output_path = data_dir / "additional_world_bank_data.csv"
        merged.to_csv(output_path, index=False)
        print(f"\n✓ Saved to {output_path}")
        return merged
    
    return None

def create_manual_data_templates():
    """Create CSV templates for metrics that need manual collection."""
    
    # Get list of countries from existing data
    wb_data = pd.read_csv(data_dir / "world_bank_data.csv")
    countries = wb_data[['WB_Code']].drop_duplicates().sort_values('WB_Code')
    
    # Template 1: Geographic features (mostly static)
    geo_template = countries.copy()
    geo_template['Average_Elevation_Meters'] = None
    geo_template['Coastline_Length_Km'] = None
    geo_template['Coastal_Area_SqKm'] = None
    geo_template['Notes'] = ''
    
    geo_path = data_dir / "geographic_features_template.csv"
    geo_template.to_csv(geo_path, index=False)
    print(f"✓ Created template: {geo_path}")
    
    # Template 2: Climate data
    climate_template = countries.copy()
    climate_template['Avg_Temperature_C'] = None
    climate_template['Sunshine_Days_Per_Year'] = None
    climate_template['Avg_Snowfall_Cm_Per_Year'] = None
    climate_template['Notes'] = ''
    
    climate_path = data_dir / "climate_features_template.csv"
    climate_template.to_csv(climate_path, index=False)
    print(f"✓ Created template: {climate_path}")
    
    # Template 3: Sports & Culture
    sports_template = countries.copy()
    sports_template['Year'] = 2024  # Most recent data
    sports_template['Number_of_Universities'] = None
    sports_template['Professional_Sports_Stadiums'] = None
    sports_template['Number_of_Ski_Resorts'] = None
    sports_template['Notes'] = ''
    
    sports_path = data_dir / "sports_culture_template.csv"
    sports_template.to_csv(sports_path, index=False)
    print(f"✓ Created template: {sports_path}")
    
    # Template 4: Consumption patterns
    consumption_template = countries.copy()
    consumption_template['Year'] = 2024
    consumption_template['Coffee_Consumption_Kg_Per_Capita'] = None
    consumption_template['Coca_Cola_Servings_Per_Capita'] = None
    consumption_template['Notes'] = ''
    
    consumption_path = data_dir / "consumption_template.csv"
    consumption_template.to_csv(consumption_path, index=False)
    print(f"✓ Created template: {consumption_path}")
    
    # Template 5: Work & Safety
    work_safety_template = countries.copy()
    work_safety_template['Year'] = 2024
    work_safety_template['Avg_Work_Hours_Per_Year'] = None
    work_safety_template['Global_Peace_Index_Score'] = None
    work_safety_template['Global_Peace_Index_Rank'] = None
    work_safety_template['Notes'] = ''
    
    work_path = data_dir / "work_safety_template.csv"
    work_safety_template.to_csv(work_path, index=False)
    print(f"✓ Created template: {work_path}")
    
    print("\n" + "="*60)
    print("MANUAL DATA COLLECTION REQUIRED")
    print("="*60)
    print("""
Templates created for metrics that require manual data collection:

1. geographic_features_template.csv
   - Average elevation (m): Wikipedia, GIS databases
   - Coastline length (km): CIA World Factbook
   - Coastal area (sq km): May need calculation

2. climate_features_template.csv
   - Average temperature (°C): Climate databases
   - Sunshine days/year: National weather services
   - Average snowfall (cm/year): Climate databases

3. sports_culture_template.csv
   - Number of universities: UNESCO, national education ministries
   - Professional sports stadiums: Manual compilation
   - Number of ski resorts: Ski resort databases

4. consumption_template.csv
   - Coffee consumption: International Coffee Organization
   - Coca-Cola consumption: Very difficult, may need proxies

5. work_safety_template.csv
   - Average work hours: OECD database
   - Global Peace Index: visionofhumanity.org

DATA SOURCES TO EXPLORE:
- CIA World Factbook: https://www.cia.gov/the-world-factbook/
- Our World in Data: https://ourworldindata.org/
- OECD Data: https://data.oecd.org/
- Global Peace Index: https://www.visionofhumanity.org/maps/
- UNESCO: http://data.uis.unesco.org/
- Climate data: https://climateknowledgeportal.worldbank.org/
    """)

def main():
    """Main execution function."""
    print("="*60)
    print("COLLECTING ADDITIONAL METRICS FOR OLYMPIC NORMALIZATION")
    print("="*60)
    
    # Step 1: Collect from World Bank API
    print("\n[1/2] Fetching data from World Bank API...")
    wb_data = collect_world_bank_metrics()
    
    # Step 2: Create templates for manual collection
    print("\n[2/2] Creating templates for manual data collection...")
    create_manual_data_templates()
    
    print("\n" + "="*60)
    print("DATA COLLECTION SETUP COMPLETE")
    print("="*60)
    print("""
NEXT STEPS:
1. Review additional_world_bank_data.csv for automated metrics
2. Fill in the template CSV files with manual data
3. Run the merge script to combine all metrics
4. Update plotting scripts to include new normalizations
    """)

if __name__ == "__main__":
    main()
