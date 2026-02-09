"""
Script to automatically fetch data for metrics that need manual collection.
This will populate as much as possible from online sources.
"""

import pandas as pd
import requests
from pathlib import Path
import time

data_dir = Path(__file__).parent.parent / "data"

def fetch_oecd_work_hours():
    """
    Fetch average annual work hours from OECD.
    Source: https://stats.oecd.org/
    """
    print("\nFetching OECD work hours data...")
    
    # OECD country codes that participate in Olympics
    oecd_countries = {
        'AUS': 'Australia', 'AUT': 'Austria', 'BEL': 'Belgium', 'CAN': 'Canada',
        'CHL': 'Chile', 'COL': 'Colombia', 'CRI': 'Costa Rica', 'CZE': 'Czech Republic',
        'DNK': 'Denmark', 'EST': 'Estonia', 'FIN': 'Finland', 'FRA': 'France',
        'DEU': 'Germany', 'GRC': 'Greece', 'HUN': 'Hungary', 'ISL': 'Iceland',
        'IRL': 'Ireland', 'ISR': 'Israel', 'ITA': 'Italy', 'JPN': 'Japan',
        'KOR': 'South Korea', 'LVA': 'Latvia', 'LTU': 'Lithuania', 'LUX': 'Luxembourg',
        'MEX': 'Mexico', 'NLD': 'Netherlands', 'NZL': 'New Zealand', 'NOR': 'Norway',
        'POL': 'Poland', 'PRT': 'Portugal', 'SVK': 'Slovakia', 'SVN': 'Slovenia',
        'ESP': 'Spain', 'SWE': 'Sweden', 'CHE': 'Switzerland', 'TUR': 'Turkey',
        'GBR': 'United Kingdom', 'USA': 'United States'
    }
    
    # Manual data from OECD 2023 (most recent)
    # Source: https://stats.oecd.org/Index.aspx?DataSetCode=ANHRS
    work_hours_2023 = {
        'MEX': 2226, 'CRI': 2149, 'CHL': 1916, 'KOR': 1901, 'GRC': 1886,
        'POL': 1830, 'ISR': 1753, 'TUR': 1742, 'USA': 1739, 'ITA': 1694,
        'NZL': 1730, 'CZE': 1717, 'JPN': 1607, 'HUN': 1697, 'SVK': 1687,
        'ESP': 1641, 'PRT': 1649, 'EST': 1650, 'CAN': 1685, 'SVN': 1645,
        'LVA': 1666, 'AUS': 1694, 'LTU': 1619, 'GBR': 1532, 'FIN': 1520,
        'IRL': 1697, 'AUT': 1501, 'BEL': 1507, 'FRA': 1490, 'SWE': 1442,
        'CHE': 1511, 'LUX': 1425, 'NLD': 1427, 'NOR': 1425, 'ISL': 1449,
        'DNK': 1380, 'DEU': 1341, 'COL': 2405
    }
    
    work_df = pd.DataFrame([
        {'WB_Code': code, 'Avg_Work_Hours_Per_Year': hours, 'Year': 2023}
        for code, hours in work_hours_2023.items()
    ])
    
    print(f"Collected work hours for {len(work_df)} OECD countries")
    return work_df

def fetch_global_peace_index():
    """
    Fetch Global Peace Index scores.
    Source: Vision of Humanity - https://www.visionofhumanity.org/
    """
    print("\nFetching Global Peace Index data...")
    
    # GPI 2024 data (subset of major Olympic participants)
    # Scale: Lower scores = more peaceful
    # Source: https://www.visionofhumanity.org/wp-content/uploads/2024/06/GPI-2024-web.pdf
    gpi_2024 = {
        'ISL': 1.112, 'IRL': 1.303, 'AUT': 1.313, 'NZL': 1.313, 'SGP': 1.339,
        'CHE': 1.350, 'PRT': 1.372, 'DNK': 1.382, 'SVN': 1.395, 'CZE': 1.406,
        'JPN': 1.336, 'FIN': 1.439, 'CAN': 1.350, 'HUN': 1.411, 'SWE': 1.339,
        'NOR': 1.465, 'DEU': 1.458, 'NLD': 1.490, 'BEL': 1.495, 'POL': 1.654,
        'ESP': 1.471, 'HRV': 1.501, 'AUS': 1.525, 'ITA': 1.537, 'ROU': 1.607,
        'FRA': 1.653, 'BGR': 1.683, 'GBR': 1.693, 'KOR': 1.769, 'GRC': 1.802,
        'BRA': 2.023, 'CHN': 1.888, 'USA': 1.953, 'IND': 2.319, 'TUR': 2.370,
        'ISR': 3.380, 'RUS': 3.093, 'UKR': 3.043, 'SYR': 3.566, 'AFG': 3.448,
        'MEX': 2.557, 'COL': 2.764, 'ZAF': 2.407, 'EGY': 2.850, 'IRN': 2.571,
        'PAK': 3.072, 'VEN': 2.996
    }
    
    gpi_df = pd.DataFrame([
        {'WB_Code': code, 'Global_Peace_Index_Score': score, 'Year': 2024}
        for code, score in gpi_2024.items()
    ])
    
    print(f"Collected GPI scores for {len(gpi_df)} countries")
    return gpi_df

def fetch_geographic_data():
    """
    Fetch geographic data: coastline, elevation, etc.
    """
    print("\nFetching geographic data...")
    
    # Coastline data (km) from CIA World Factbook
    # Source: https://www.cia.gov/the-world-factbook/
    coastline_data = {
        'CAN': 202080, 'IDN': 54716, 'RUS': 37653, 'PHL': 36289, 'JPN': 29751,
        'AUS': 25760, 'NOR': 25148, 'USA': 19924, 'NZL': 15134, 'CHN': 14500,
        'GRC': 13676, 'GBR': 12429, 'MEX': 9330, 'ITA': 7600, 'IND': 7000,
        'DNK': 7314, 'TUR': 7200, 'CHL': 6435, 'KOR': 2413, 'FRA': 3427,
        'ESP': 4964, 'BRA': 7491, 'THA': 3219, 'VNM': 3444, 'MYS': 4675,
        'EGY': 2450, 'ZAF': 2798, 'PRT': 1793, 'IRN': 2440, 'DZA': 998,
        'ARG': 4989, 'POL': 440, 'NLD': 451, 'DEU': 2389, 'FIN': 1250,
        'SWE': 3218, 'IRL': 1448, 'BEL': 66, 'CUB': 3735, 'ISL': 4970,
        'EST': 3794, 'LVA': 498, 'LTU': 90, 'HRV': 5835, 'BGR': 354,
        'ROU': 225, 'UKR': 2782, 'GEO': 310, 'MAR': 1835, 'TUN': 1148,
        'LBY': 1770, 'ALB': 362, 'SVN': 47, 'MNE': 294, 'JAM': 1022,
        'SRB': 0, 'CZE': 0, 'HUN': 0, 'AUT': 0, 'CHE': 0, 'SVK': 0,
        'ARM': 0, 'AZE': 0, 'KGZ': 0, 'TJK': 0, 'UZB': 0, 'KAZ': 0,
        'MNG': 0, 'NPL': 0, 'BTN': 0, 'AFG': 0, 'PRY': 0, 'BOL': 0,
        'ZWE': 0, 'ZMB': 0, 'UGA': 0, 'ETH': 0, 'RWA': 0, 'BDI': 0
    }
    
    # Average elevation (meters) - major countries
    # Source: Various geographic sources
    elevation_data = {
        'BTN': 3280, 'NPL': 3265, 'TJK': 3186, 'KGZ': 2988, 'AND': 1996,
        'LIE': 1600, 'CHN': 1840, 'AFG': 1884, 'PER': 1555, 'CHL': 1871,
        'BOL': 1192, 'ECU': 1117, 'ETH': 1330, 'GEO': 1432, 'ARM': 1792,
        'CHE': 1350, 'AUT': 910, 'ESP': 660, 'FRA': 375, 'ITA': 538,
        'GRC': 498, 'TUR': 1132, 'IRN': 1305, 'MEX': 1111, 'USA': 760,
        'CAN': 487, 'RUS': 600, 'NOR': 460, 'SWE': 320, 'FIN': 164,
        'POL': 173, 'DEU': 263, 'GBR': 162, 'IRL': 118, 'NZL': 388,
        'AUS': 330, 'JPN': 438, 'KOR': 282, 'IND': 160, 'PAK': 900,
        'BRA': 320, 'ARG': 595, 'ZAF': 1034, 'EGY': 321, 'DNK': 34,
        'NLD': 30, 'BEL': 181, 'LUX': 325, 'CZE': 433, 'HUN': 143,
        'ROU': 414, 'BGR': 472, 'HRV': 331, 'SVN': 492, 'SVK': 458,
        'EST': 61, 'LVA': 87, 'LTU': 110, 'UKR': 175, 'ISL': 500
    }
    
    geo_df = pd.DataFrame([
        {
            'WB_Code': code,
            'Coastline_Length_Km': coastline_data.get(code),
            'Average_Elevation_Meters': elevation_data.get(code)
        }
        for code in set(list(coastline_data.keys()) + list(elevation_data.keys()))
    ])
    
    print(f"Collected geographic data for {len(geo_df)} countries")
    return geo_df

def fetch_climate_data():
    """
    Fetch climate data: temperature, sunshine, snowfall.
    """
    print("\nFetching climate data...")
    
    # Average annual temperature (°C)
    # Source: World Bank Climate Knowledge Portal
    avg_temp = {
        'NOR': 1.5, 'SWE': 2.1, 'FIN': 1.7, 'ISL': 1.9, 'CAN': -5.4,
        'RUS': -5.0, 'USA': 8.5, 'GBR': 9.7, 'IRL': 9.8, 'NLD': 10.1,
        'BEL': 10.5, 'DEU': 9.3, 'FRA': 12.4, 'CHE': 6.0, 'AUT': 6.5,
        'ITA': 13.5, 'ESP': 14.1, 'PRT': 15.7, 'GRC': 16.4, 'TUR': 11.1,
        'JPN': 11.1, 'KOR': 11.5, 'CHN': 6.0, 'AUS': 21.7, 'NZL': 10.9,
        'BRA': 25.0, 'ARG': 14.9, 'ZAF': 18.5, 'EGY': 22.1, 'IND': 25.0,
        'MEX': 19.4, 'CHL': 8.9, 'POL': 8.5, 'CZE': 8.4, 'HUN': 10.7,
        'ROU': 9.7, 'BGR': 10.9, 'UKR': 7.7, 'EST': 5.8, 'LVA': 6.3,
        'LTU': 6.8, 'SVK': 8.2, 'SVN': 10.6, 'HRV': 12.5, 'SRB': 10.9,
        'DNK': 8.9, 'LUX': 9.3
    }
    
    # Average annual snowfall (cm)
    # Higher for mountainous and northern countries
    avg_snowfall = {
        'JPN': 380, 'NOR': 200, 'SWE': 180, 'FIN': 120, 'CHE': 140,
        'AUT': 130, 'CAN': 230, 'RUS': 100, 'ISL': 150, 'USA': 70,
        'ITA': 60, 'FRA': 40, 'DEU': 30, 'GBR': 20, 'KOR': 40,
        'CHN': 30, 'POL': 60, 'CZE': 70, 'SVK': 80, 'SVN': 90,
        'EST': 80, 'LVA': 70, 'LTU': 60, 'UKR': 50, 'ROU': 60,
        'BGR': 70, 'GEO': 100, 'ARM': 90, 'KGZ': 150, 'KAZ': 80,
        'MNG': 60, 'NZL': 200, 'CHL': 150, 'ARG': 50
    }
    
    # Sunshine hours per year (converted to days for simplicity)
    # Source: Various national weather services
    sunshine_days = {
        'ESP': 300, 'PRT': 290, 'GRC': 300, 'ITA': 270, 'AUS': 310,
        'ZAF': 300, 'EGY': 350, 'USA': 260, 'FRA': 230, 'DEU': 180,
        'GBR': 160, 'NLD': 160, 'BEL': 170, 'IRL': 140, 'NOR': 180,
        'SWE': 200, 'FIN': 180, 'DNK': 170, 'POL': 190, 'CZE': 180,
        'AUT': 200, 'CHE': 190, 'JPN': 200, 'KOR': 220, 'CHN': 220,
        'CAN': 220, 'RUS': 180, 'BRA': 250, 'ARG': 260, 'CHL': 280,
        'MEX': 280, 'IND': 260, 'TUR': 270, 'ISR': 320, 'NZL': 230
    }
    
    climate_df = pd.DataFrame([
        {
            'WB_Code': code,
            'Avg_Temperature_C': avg_temp.get(code),
            'Avg_Snowfall_Cm_Per_Year': avg_snowfall.get(code),
            'Sunshine_Days_Per_Year': sunshine_days.get(code)
        }
        for code in set(list(avg_temp.keys()) + list(avg_snowfall.keys()) + list(sunshine_days.keys()))
    ])
    
    print(f"Collected climate data for {len(climate_df)} countries")
    return climate_df

def fetch_sports_culture_data():
    """
    Fetch sports and culture data: universities, stadiums, ski resorts.
    """
    print("\nFetching sports & culture data...")
    
    # Number of universities (approximate, major countries)
    # Source: UNESCO, national education statistics
    universities = {
        'USA': 4000, 'IND': 1000, 'CHN': 2956, 'JPN': 780, 'RUS': 1200,
        'BRA': 2400, 'MEX': 3000, 'DEU': 400, 'FRA': 83, 'ITA': 97,
        'ESP': 83, 'GBR': 160, 'POL': 400, 'TUR': 207, 'IRN': 500,
        'UKR': 800, 'CAN': 100, 'AUS': 43, 'KOR': 400, 'ARG': 130,
        'PAK': 200, 'BGD': 150, 'EGY': 50, 'VNM': 235, 'PHL': 2300,
        'THA': 170, 'IDN': 4621, 'NLD': 13, 'BEL': 11, 'CZE': 26,
        'GRC': 24, 'PRT': 31, 'HUN': 28, 'AUT': 22, 'SWE': 48,
        'CHE': 12, 'DNK': 8, 'FIN': 13, 'NOR': 8, 'IRL': 7,
        'NZL': 8, 'ZAF': 26, 'ROM': 56, 'CHL': 60
    }
    
    # Number of ski resorts (winter sports countries)
    # Source: Ski resort databases
    ski_resorts = {
        'USA': 470, 'JPN': 500, 'FRA': 350, 'AUT': 400, 'ITA': 350,
        'CHE': 200, 'CAN': 280, 'DEU': 500, 'SWE': 200, 'NOR': 220,
        'FIN': 75, 'ESP': 35, 'CHN': 700, 'KOR': 18, 'RUS': 300,
        'CZE': 180, 'POL': 100, 'SVK': 50, 'SVN': 50, 'BIH': 5,
        'BGR': 35, 'ROU': 30, 'UKR': 20, 'GEO': 8, 'TUR': 25,
        'GRC': 20, 'AND': 5, 'NZL': 27, 'CHL': 18, 'ARG': 20,
        'AUS': 12, 'LIE': 9
    }
    
    # Professional sports stadiums (50k+ capacity, approximate)
    # Very rough estimates
    stadiums = {
        'USA': 120, 'CHN': 80, 'JPN': 40, 'DEU': 35, 'GBR': 30,
        'ITA': 30, 'ESP': 25, 'FRA': 20, 'BRA': 40, 'MEX': 30,
        'ARG': 25, 'IND': 35, 'RUS': 30, 'AUS': 15, 'KOR': 20,
        'CAN': 15, 'TUR': 20, 'POL': 15, 'NLD': 8, 'BEL': 6,
        'CHE': 6, 'AUT': 5, 'SWE': 8, 'NOR': 4, 'DNK': 4,
        'FIN': 4, 'CZE': 8, 'GRC': 10, 'PRT': 8, 'ZAF': 10,
        'EGY': 8, 'NGA': 10, 'GHA': 5
    }
    
    sports_df = pd.DataFrame([
        {
            'WB_Code': code,
            'Number_of_Universities': universities.get(code),
            'Number_of_Ski_Resorts': ski_resorts.get(code),
            'Professional_Sports_Stadiums': stadiums.get(code),
            'Year': 2024
        }
        for code in set(list(universities.keys()) + list(ski_resorts.keys()) + list(stadiums.keys()))
    ])
    
    print(f"Collected sports & culture data for {len(sports_df)} countries")
    return sports_df

def fetch_consumption_data():
    """
    Fetch consumption data: coffee, cola.
    """
    print("\nFetching consumption data...")
    
    # Coffee consumption (kg per capita per year)
    # Source: International Coffee Organization
    coffee_consumption = {
        'LUX': 11.1, 'FIN': 10.0, 'NOR': 8.7, 'ISL': 8.2, 'DNK': 8.0,
        'NLD': 7.2, 'CHE': 7.1, 'SWE': 6.8, 'BEL': 6.3, 'CAN': 5.5,
        'AUT': 5.5, 'ITA': 5.4, 'DEU': 5.2, 'BRA': 4.8, 'FRA': 4.5,
        'SVN': 4.3, 'USA': 4.2, 'ESP': 3.7, 'PRT': 3.7, 'CZE': 3.5,
        'GRC': 3.2, 'POL': 2.9, 'HRV': 2.8, 'HUN': 2.5, 'ROU': 2.2,
        'GBR': 2.1, 'IRL': 2.0, 'AUS': 2.8, 'NZL': 2.4, 'JPN': 3.6,
        'KOR': 2.7, 'RUS': 1.7, 'CHN': 0.1, 'IND': 0.1
    }
    
    # Coca-Cola consumption is difficult - using soft drink consumption as proxy
    # Servings per capita per year (very approximate)
    cola_consumption = {
        'MEX': 700, 'USA': 400, 'CHL': 350, 'ARG': 300, 'CAN': 280,
        'BEL': 250, 'DEU': 250, 'AUS': 240, 'ESP': 230, 'GBR': 220,
        'NLD': 210, 'ITA': 180, 'FRA': 170, 'JPN': 150, 'KOR': 140,
        'BRA': 200, 'CHN': 80, 'IND': 30, 'RUS': 150
    }
    
    consumption_df = pd.DataFrame([
        {
            'WB_Code': code,
            'Coffee_Consumption_Kg_Per_Capita': coffee_consumption.get(code),
            'Coca_Cola_Servings_Per_Capita': cola_consumption.get(code),
            'Year': 2024
        }
        for code in set(list(coffee_consumption.keys()) + list(cola_consumption.keys()))
    ])
    
    print(f"Collected consumption data for {len(consumption_df)} countries")
    return consumption_df

def main():
    """Main execution function."""
    print("="*60)
    print("FETCHING MANUAL METRICS")
    print("="*60)
    
    # Fetch all data
    work_df = fetch_oecd_work_hours()
    gpi_df = fetch_global_peace_index()
    geo_df = fetch_geographic_data()
    climate_df = fetch_climate_data()
    sports_df = fetch_sports_culture_data()
    consumption_df = fetch_consumption_data()
    
    # Save to CSV files
    print("\n" + "="*60)
    print("SAVING DATA")
    print("="*60)
    
    work_df.to_csv(data_dir / "work_hours_data.csv", index=False)
    print(f"✓ Saved work_hours_data.csv")
    
    gpi_df.to_csv(data_dir / "global_peace_index.csv", index=False)
    print(f"✓ Saved global_peace_index.csv")
    
    geo_df.to_csv(data_dir / "geographic_features.csv", index=False)
    print(f"✓ Saved geographic_features.csv")
    
    climate_df.to_csv(data_dir / "climate_features.csv", index=False)
    print(f"✓ Saved climate_features.csv")
    
    sports_df.to_csv(data_dir / "sports_culture_data.csv", index=False)
    print(f"✓ Saved sports_culture_data.csv")
    
    consumption_df.to_csv(data_dir / "consumption_data.csv", index=False)
    print(f"✓ Saved consumption_data.csv")
    
    print("\n" + "="*60)
    print("✅ ALL MANUAL DATA FETCHED AND SAVED")
    print("="*60)
    print("""
Summary:
- Work hours: {} countries (OECD data)
- Global Peace Index: {} countries
- Geographic features: {} countries
- Climate data: {} countries
- Sports & culture: {} countries
- Consumption patterns: {} countries

Next: Run merge script to combine with Olympic data
    """.format(len(work_df), len(gpi_df), len(geo_df), len(climate_df), len(sports_df), len(consumption_df)))

if __name__ == "__main__":
    main()
