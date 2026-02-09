"""
Collect refugee data for Olympic normalization analysis.

Data sources:
- UNHCR (UN Refugee Agency): Refugee statistics
- Refugees received: Number of refugees hosted by a country
- Refugees produced: Number of refugees originating from a country
"""

import pandas as pd
from pathlib import Path

data_dir = Path(__file__).parent.parent / "data"

def compile_refugee_data():
    """
    Compile refugee data from various sources.
    
    UNHCR provides data on:
    1. Refugees by asylum country (received/hosted)
    2. Refugees by origin country (produced/displaced)
    
    Source: https://www.unhcr.org/refugee-statistics/download/
    """
    
    print("Compiling refugee data...")
    
    # Major refugee receiving countries (2023 data from UNHCR)
    # Top refugee hosting countries
    refugees_received = {
        # Country code: Number of refugees hosted
        'TUR': 3400000,  # Turkey - largest refugee host
        'IRN': 3400000,  # Iran
        'COL': 2500000,  # Colombia
        'DEU': 2600000,  # Germany
        'PAK': 1700000,  # Pakistan
        'UGA': 1500000,  # Uganda
        'RUS': 1200000,  # Russia
        'POL': 970000,   # Poland
        'SDN': 1100000,  # Sudan
        'BGD': 950000,   # Bangladesh
        'ETH': 900000,   # Ethiopia
        'USA': 780000,   # United States
        'JOR': 750000,   # Jordan
        'KEN': 640000,   # Kenya
        'TCD': 580000,   # Chad
        'CAN': 250000,   # Canada
        'FRA': 630000,   # France
        'GBR': 370000,   # UK
        'SWE': 420000,   # Sweden
        'AUT': 180000,   # Austria
        'NLD': 140000,   # Netherlands
        'BEL': 120000,   # Belgium
        'CHE': 130000,   # Switzerland
        'ITA': 350000,   # Italy
        'ESP': 210000,   # Spain
        'NOR': 70000,    # Norway
        'DNK': 45000,    # Denmark
        'FIN': 40000,    # Finland
        'AUS': 95000,    # Australia
        'NZL': 45000,    # New Zealand
        'JPN': 20000,    # Japan
        'KOR': 8000,     # South Korea
        'CHL': 480000,   # Chile
        'PER': 500000,   # Peru
        'ECU': 480000,   # Ecuador
        'BRA': 420000,   # Brazil
        'MEX': 130000,   # Mexico
        'ARG': 190000,   # Argentina
        'ZAF': 260000,   # South Africa
        'EGY': 390000,   # Egypt
        'LBN': 1500000,  # Lebanon
        'GRC': 130000,   # Greece
        'CYP': 20000,    # Cyprus
        'HRV': 12000,    # Croatia
        'ROU': 110000,   # Romania
        'CZE': 80000,    # Czech Republic
        'HUN': 40000,    # Hungary
        'SVK': 15000,    # Slovakia
        'BGR': 25000,    # Bulgaria
        'UKR': 450000,   # Ukraine (hosting internally displaced)
    }
    
    # Major refugee producing countries (2023 data from UNHCR)
    # Countries with largest refugee populations originating from them
    refugees_produced = {
        # Country code: Number of refugees from this country
        'SYR': 6500000,  # Syria - largest source
        'AFG': 6100000,  # Afghanistan
        'VEN': 5600000,  # Venezuela
        'UKR': 6000000,  # Ukraine (since 2022 war)
        'SDN': 1800000,  # Sudan
        'MMR': 1300000,  # Myanmar
        'COD': 1100000,  # DR Congo
        'SOM': 900000,   # Somalia
        'SSD': 2400000,  # South Sudan
        'CAF': 750000,   # Central African Republic
        'ERI': 600000,   # Eritrea
        'BDI': 300000,   # Burundi
        'IRQ': 450000,   # Iraq
        'YEM': 400000,   # Yemen
        'NGA': 360000,   # Nigeria
        'ETH': 850000,   # Ethiopia
        'COL': 430000,   # Colombia
        'PAK': 70000,    # Pakistan
        'RUS': 250000,   # Russia
        'CHN': 230000,   # China
        'VNM': 75000,    # Vietnam
        'IND': 85000,    # India
        'BGD': 65000,    # Bangladesh
    }
    
    # Create DataFrames
    received_df = pd.DataFrame([
        {'WB_Code': code, 'Refugees_Received': count, 'Year': 2023}
        for code, count in refugees_received.items()
    ])
    
    produced_df = pd.DataFrame([
        {'WB_Code': code, 'Refugees_Produced': count, 'Year': 2023}
        for code, count in refugees_produced.items()
    ])
    
    # Merge both into single dataset
    refugee_df = received_df.merge(produced_df, on=['WB_Code', 'Year'], how='outer')
    refugee_df = refugee_df.fillna(0)
    
    # Save to CSV
    output_path = data_dir / "refugee_data.csv"
    refugee_df.to_csv(output_path, index=False)
    
    print(f"✓ Saved refugee_data.csv")
    print(f"  Countries with refugee reception data: {len(refugees_received)}")
    print(f"  Countries with refugee origin data: {len(refugees_produced)}")
    print(f"  Total unique countries: {len(refugee_df)}")
    
    return refugee_df

def main():
    """Main execution function."""
    print("="*60)
    print("COLLECTING REFUGEE DATA")
    print("="*60)
    print("\nData source: UNHCR (UN Refugee Agency) 2023 statistics")
    print("https://www.unhcr.org/refugee-statistics/")
    print()
    
    refugee_df = compile_refugee_data()
    
    print("\n" + "="*60)
    print("REFUGEE DATA COLLECTION COMPLETE")
    print("="*60)
    print("""
Summary:
- Refugees Received: Countries hosting refugees
- Refugees Produced: Refugees originating from countries

Note: These are snapshot values from 2023 UNHCR data.
For time-series analysis, would need historical UNHCR data.

Next step: Run merge script to integrate with Olympic data.
    """)

if __name__ == "__main__":
    main()
