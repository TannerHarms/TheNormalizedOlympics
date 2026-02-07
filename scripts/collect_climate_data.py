"""
Collect climate data for Olympic performance analysis.

Key metrics for Olympic sports:
1. Average annual temperature - affects winter sports feasibility
2. Winter severity - cold days, snowfall potential
3. Climate zone classification

Data sources:
1. World Bank Climate API - historical temperature data
2. Climate zone classification based on latitude/temperature
"""

import pandas as pd
import requests
import sys
from pathlib import Path
import time

sys.path.append(str(Path(__file__).parent.parent))
from scripts.country_mapping import NOC_TO_WB

def fetch_world_bank_climate_data():
    """
    Fetch temperature data from World Bank Climate API.
    
    World Bank Climate Change Knowledge Portal API:
    http://climatedataapi.worldbank.org/climateweb/rest/v1/country/
    
    Unfortunately, this API provides projections, not historical data.
    Instead, we'll use average temperature by country from World Bank indicators.
    """
    print("=" * 70)
    print("COLLECTING CLIMATE DATA")
    print("=" * 70)
    print()
    
    # World Bank has some climate indicators
    # We'll focus on a simple classification based on latitude and existing knowledge
    
    # Alternative: Use geographical data and classify
    # For now, let's create a manual classification based on known climate zones
    
    print("Creating climate classification based on geography...")
    print()
    
    # Climate zones for winter sports analysis
    # 1 = Arctic/Subarctic (excellent winter sports)
    # 2 = Continental (good winter sports)
    # 3 = Temperate (moderate winter sports)
    # 4 = Mediterranean/Subtropical (limited winter sports)
    # 5 = Tropical (no winter sports)
    
    climate_data = {
        # Arctic/Subarctic - Tier 1 winter sports
        'NOR': 1, 'SWE': 1, 'FIN': 1, 'ISL': 1, 'GRL': 1,
        'CAN': 1, 'RUS': 1, 'EST': 1, 'LVA': 1, 'LTU': 1,
        
        # Continental - Tier 2 winter sports
        'USA': 2, 'AUT': 2, 'CHE': 2, 'DEU': 2, 'POL': 2,
        'CZE': 2, 'SVK': 2, 'SVN': 2, 'HRV': 2, 'BLR': 2,
        'UKR': 2, 'KAZ': 2, 'MNG': 2, 'CHN': 2, 'JPN': 2,
        'KOR': 2, 'PRK': 2, 'FRA': 2, 'ITA': 2, 'ROU': 2,
        'BGR': 2, 'SRB': 2, 'BIH': 2, 'MKD': 2, 'ALB': 2,
        'MNE': 2, 'GEO': 2, 'ARM': 2, 'AZE': 2, 'KGZ': 2,
        'TJK': 2, 'UZB': 2, 'TKM': 2,
        
        # Temperate - Tier 3 winter sports
        'GBR': 3, 'IRL': 3, 'NLD': 3, 'BEL': 3, 'LUX': 3,
        'DNK': 3, 'ESP': 3, 'PRT': 3, 'GRC': 3, 'TUR': 3,
        'CYP': 3, 'MLT': 3, 'ISR': 3, 'NZL': 3, 'ARG': 3,
        'CHL': 3, 'URY': 3, 'PRY': 3, 'AUS': 3, 'ZAF': 3,
        'JOR': 3, 'LBN': 3, 'SYR': 3, 'IRQ': 3, 'IRN': 3,
        'AFG': 3, 'PAK': 3, 'NPL': 3,
        
        # Mediterranean/Subtropical - Tier 4 (limited winter)
        'MAR': 4, 'DZA': 4, 'TUN': 4, 'LBY': 4, 'EGY': 4,
        'SAU': 4, 'YEM': 4, 'OMN': 4, 'ARE': 4, 'QAT': 4,
        'BHR': 4, 'KWT': 4, 'MEX': 4, 'BRA': 4, 'COL': 4,
        'VEN': 4, 'ECU': 4, 'PER': 4, 'BOL': 4, 'IND': 4,
        'BGD': 4, 'LKA': 4, 'MMR': 4, 'THA': 4, 'VNM': 4,
        'KHM': 4, 'LAO': 4, 'PHL': 4, 'MYS': 4,
        'SGP': 4, 'BRN': 4, 'IDN': 4, 'TLS': 4,
        
        # Tropical - Tier 5 (no winter sports)
        'NGA': 5, 'GHA': 5, 'CIV': 5, 'SEN': 5, 'MLI': 5,
        'BFA': 5, 'NER': 5, 'TCD': 5, 'SDN': 5, 'SSD': 5,
        'ETH': 5, 'ERI': 5, 'DJI': 5, 'SOM': 5, 'KEN': 5,
        'UGA': 5, 'RWA': 5, 'BDI': 5, 'TZA': 5, 'MOZ': 5,
        'ZMB': 5, 'ZWE': 5, 'MWI': 5, 'BWA': 5, 'NAM': 5,
        'AGO': 5, 'COD': 5, 'COG': 5, 'GAB': 5, 'CMR': 5,
        'CAF': 5, 'GNQ': 5, 'STP': 5, 'LBR': 5, 'SLE': 5,
        'GIN': 5, 'GMB': 5, 'GNB': 5, 'CPV': 5, 'CUB': 5,
        'JAM': 5, 'HTI': 5, 'DOM': 5, 'PRI': 5, 'TTO': 5,
        'BRB': 5, 'GRD': 5, 'VCT': 5, 'LCA': 5, 'DMA': 5,
        'ATG': 5, 'KNA': 5, 'BHS': 5, 'BLZ': 5, 'GTM': 5,
        'HND': 5, 'SLV': 5, 'NIC': 5, 'CRI': 5, 'PAN': 5,
        'GUY': 5, 'SUR': 5, 'FJI': 5, 'PNG': 5, 'SLB': 5,
        'VUT': 5, 'NCL': 5, 'PLW': 5, 'FSM': 5, 'MHL': 5,
        'KIR': 5, 'NRU': 5, 'TUV': 5, 'WSM': 5, 'TON': 5,
        'MDG': 5, 'MUS': 5, 'SYC': 5, 'COM': 5,
    }
    
    # Convert to DataFrame
    climate_df = pd.DataFrame([
        {'WB_Code': code, 'Climate_Zone': zone}
        for code, zone in climate_data.items()
    ])
    
    # Add descriptive labels
    zone_labels = {
        1: 'Arctic/Subarctic',
        2: 'Continental',
        3: 'Temperate',
        4: 'Mediterranean/Subtropical',
        5: 'Tropical'
    }
    
    climate_df['Climate_Description'] = climate_df['Climate_Zone'].map(zone_labels)
    
    print(f"✓ Classified {len(climate_df)} countries into climate zones")
    print()
    
    # Show distribution
    print("Climate zone distribution:")
    for zone in sorted(climate_df['Climate_Zone'].unique()):
        count = (climate_df['Climate_Zone'] == zone).sum()
        label = zone_labels[zone]
        print(f"  Zone {zone} ({label:25s}): {count:3d} countries")
    print()
    
    return climate_df


def add_average_temperatures():
    """
    Add average annual temperature data from World Bank.
    
    World Bank indicator: AG.LND.PRCP.MM (precipitation) or
    we can use latitude as proxy for temperature.
    
    For simplicity, we'll add typical temperatures based on climate zones.
    """
    print("Adding typical temperature ranges by climate zone...")
    print()
    
    # Average annual temperatures (Celsius) by zone
    temp_ranges = {
        1: -5,   # Arctic/Subarctic: -10 to 0°C
        2: 5,    # Continental: 0 to 10°C
        3: 12,   # Temperate: 10 to 15°C
        4: 18,   # Mediterranean/Subtropical: 15 to 22°C
        5: 26    # Tropical: 22 to 30°C
    }
    
    # Winter coldness index (for winter sports suitability)
    # Higher = better for winter sports
    winter_index = {
        1: 10,  # Excellent winter conditions
        2: 7,   # Good winter conditions
        3: 4,   # Moderate winter conditions
        4: 2,   # Limited winter conditions
        5: 0    # No winter conditions
    }
    
    return temp_ranges, winter_index


def main():
    # Get climate classification
    climate_df = fetch_world_bank_climate_data()
    
    # Add temperature data
    temp_ranges, winter_index = add_average_temperatures()
    
    climate_df['Avg_Temp_C'] = climate_df['Climate_Zone'].map(temp_ranges)
    climate_df['Winter_Sports_Index'] = climate_df['Climate_Zone'].map(winter_index)
    
    # Save
    output_path = Path(__file__).parent.parent / 'data' / 'climate_data.csv'
    climate_df.to_csv(output_path, index=False)
    
    print("-" * 70)
    print("SAMPLE DATA")
    print("-" * 70)
    
    # Show examples from each zone
    for zone in [1, 2, 3, 4, 5]:
        sample = climate_df[climate_df['Climate_Zone'] == zone].head(3)
        if len(sample) > 0:
            print(f"\nZone {zone} - {sample.iloc[0]['Climate_Description']}:")
            for _, row in sample.iterrows():
                print(f"  {row['WB_Code']:3s}: {row['Avg_Temp_C']:3.0f}°C, "
                      f"Winter Index: {row['Winter_Sports_Index']}/10")
    
    print()
    print("=" * 70)
    print("✓ CLIMATE DATA COLLECTION COMPLETE!")
    print("=" * 70)
    print(f"Saved to: {output_path}")
    print(f"Total countries: {len(climate_df)}")
    print()
    print("Note: Climate zones are based on geographical classification.")
    print("Winter Sports Index (0-10): Higher = better natural conditions for winter sports")
    print()


if __name__ == '__main__':
    main()
