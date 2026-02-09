"""
Merge all collected metrics into the summer/winter Olympics normalized datasets.
"""

import pandas as pd
from pathlib import Path

data_dir = Path(__file__).parent.parent / "data"

def merge_all_metrics():
    """Merge all collected metrics into Olympic datasets."""
    
    # Load Olympic data
    print("Loading Olympic datasets...")
    summer_df = pd.read_csv(data_dir / "summer_olympics_normalized.csv")
    winter_df = pd.read_csv(data_dir / "winter_olympics_normalized.csv")
    
    print(f"Summer Olympics: {len(summer_df)} records")
    print(f"Winter Olympics: {len(winter_df)} records")
    
    # Load all additional data sources
    print("\nLoading additional metrics...")
    
    # World Bank data (time series)
    wb_additional = pd.read_csv(data_dir / "additional_world_bank_data.csv")
    wb_additional['Year'] = wb_additional['Year'].astype(int)
    print(f"  - World Bank additional: {len(wb_additional)} records")
    
    # Geographic (static)
    geo_df = pd.read_csv(data_dir / "geographic_features.csv")
    print(f"  - Geographic features: {len(geo_df)} records")
    
    # Climate (static)
    climate_df = pd.read_csv(data_dir / "climate_features.csv")
    print(f"  - Climate features: {len(climate_df)} records")
    
    # Sports & culture (2024 snapshot)
    sports_df = pd.read_csv(data_dir / "sports_culture_data.csv")
    print(f"  - Sports & culture: {len(sports_df)} records")
    
    # Consumption (2024 snapshot)
    consumption_df = pd.read_csv(data_dir / "consumption_data.csv")
    print(f"  - Consumption data: {len(consumption_df)} records")
    
    # Work hours (time series from OECD SDMX API, 2005-2023)
    work_df = pd.read_csv(data_dir / "work_hours_data.csv")
    work_df['Year'] = work_df['Year'].astype(int)
    print(f"  - Work hours: {len(work_df)} records ({work_df['WB_Code'].nunique()} countries, time-series)")
    
    # Global Peace Index (2024 snapshot)
    gpi_df = pd.read_csv(data_dir / "global_peace_index.csv")
    print(f"  - Global Peace Index: {len(gpi_df)} records")
    
    # Refugee data (2023 snapshot)
    refugee_df = pd.read_csv(data_dir / "refugee_data.csv")
    print(f"  - Refugee data: {len(refugee_df)} records")
    
    # Military data (time series from World Bank API, 2000-2023)
    military_df = pd.read_csv(data_dir / "military_data.csv")
    military_df['Year'] = military_df['Year'].astype(int)
    print(f"  - Military data: {len(military_df)} records ({military_df['WB_Code'].nunique()} countries, time-series)")
    
    # Merge function for both seasons
    def merge_season(df, season_name):
        print(f"\nMerging {season_name} Olympics...")
        
        # WB_Code already exists from merge_all_data.py (proper World Bank codes)
        # Do NOT overwrite with Country column (which contains NOC codes)
        
        # Merge World Bank time series data
        df = df.merge(wb_additional, on=['WB_Code', 'Year'], how='left')
        
        # Merge static data (no year dependency)
        df = df.merge(geo_df, on='WB_Code', how='left')
        df = df.merge(climate_df, on='WB_Code', how='left')
        
        # Merge snapshot data (apply to all years)
        df = df.merge(sports_df[['WB_Code', 'Number_of_Universities', 
                                   'Number_of_Ski_Resorts', 'Professional_Sports_Stadiums']], 
                      on='WB_Code', how='left')
        df = df.merge(consumption_df[['WB_Code', 'Coffee_Consumption_Kg_Per_Capita', 
                                       'Coca_Cola_Servings_Per_Capita']], 
                      on='WB_Code', how='left')
        df = df.merge(work_df[['WB_Code', 'Year', 'Avg_Work_Hours_Per_Year']], 
                      on=['WB_Code', 'Year'], how='left')
        df = df.merge(gpi_df[['WB_Code', 'Global_Peace_Index_Score']], 
                      on='WB_Code', how='left')
        df = df.merge(refugee_df[['WB_Code', 'Refugees_Received', 'Refugees_Produced']], 
                      on='WB_Code', how='left')
        df = df.merge(military_df[['WB_Code', 'Year', 'Military_Expenditure_Pct_GDP', 'Active_Military_Personnel_Thousands']], 
                      on=['WB_Code', 'Year'], how='left')
        
        return df
    
    summer_merged = merge_season(summer_df, "Summer")
    winter_merged = merge_season(winter_df, "Winter")
    
    # Calculate new normalized metrics
    print("\nCalculating normalized metrics...")
    
    for df, season in [(summer_merged, "Summer"), (winter_merged, "Winter")]:
        # Calculate absolute spending values from percentage of GDP
        df['Healthcare_Spending_USD'] = df['Healthcare_Spending_Per_Capita_USD'] * df['Population']
        df['Military_Expenditure_USD'] = df['GDP'] * (df['Military_Expenditure_Pct_GDP'] / 100)
        df['Education_Spending_USD'] = df['GDP'] * (df['Education_Spending_pct_GDP'] / 100)

        # For unnormalized metrics, the 'normalized' value is just the total medals
        df['Total_Medals_Summer'] = df['Total_Medals']
        df['Total_Medals_Winter'] = df['Total_Medals']

        # Original basic metrics (matching column names from summer_olympics_normalized.csv)
        df['Medals_Per_Million'] = df['Total'] / df['Population'] * 1_000_000
        df['Medals_Per_Billion_GDP'] = df['Total'] / df['GDP'] * 1_000_000_000
        df['Medals_Per_GDP_Per_Capita'] = df['Total'] / df['GDP_per_capita'] * 10_000
        df['Medals_Per_HDI'] = df['Total'] / df['HDI']
        
        # Land area
        df['Medals_Per_1000_SqKm'] = df['Total'] / df['Land_Area_SqKm'] * 1000
        
        # Coastline
        df['Medals_Per_1000_Km_Coastline'] = df['Total'] / df['Coastline_Length_Km'] * 1000
        
        # Elevation
        df['Medals_Per_100m_Elevation'] = df['Total'] / df['Average_Elevation_Meters'] * 100
        
        # Temperature
        df['Medals_Per_Degree_Temp'] = df['Total'] / df['Avg_Temperature_C'].abs()
        
        # Sunshine
        df['Medals_Per_100_Sunshine_Days'] = df['Total'] / df['Sunshine_Days_Per_Year'] * 100
        
        # Snowfall
        df['Medals_Per_100_Cm_Snowfall'] = df['Total'] / df['Avg_Snowfall_Cm_Per_Year'] * 100
        
        # Internet users
        df['Medals_Per_Million_Internet_Users'] = df['Total'] / (df['Internet_Users_Pct'] * df['Population'] / 100) * 1_000_000
        
        # Vehicles
        df['Medals_Per_1000_Vehicles'] = df['Total'] / (df['Vehicles_Per_1000'] * df['Population'] / 1000) * 1000
        
        # Universities
        df['Medals_Per_University'] = df['Total'] / df['Number_of_Universities']
        
        # Sports stadiums
        df['Medals_Per_Stadium'] = df['Total'] / df['Professional_Sports_Stadiums']
        
        # Ski resorts
        df['Medals_Per_Ski_Resort'] = df['Total'] / df['Number_of_Ski_Resorts']
        
        # Healthcare spending (per percentage point of GDP)
        df['Medals_Per_Pct_Healthcare_Spending'] = df['Total'] / df['Healthcare_Spending_Pct_GDP']
        
        # Life expectancy
        df['Medals_Per_Year_Life_Expectancy'] = df['Total'] / df['Life_Expectancy_Years']
        
        # Work hours
        df['Medals_Per_100_Work_Hours'] = df['Total'] / df['Avg_Work_Hours_Per_Year'] * 100
        
        # Coffee consumption
        df['Medals_Per_Million_Kg_Coffee'] = df['Total'] / (df['Coffee_Consumption_Kg_Per_Capita'] * df['Population']) * 1_000_000
        
        # Cola consumption
        df['Medals_Per_Million_Cola_Servings'] = df['Total'] / (df['Coca_Cola_Servings_Per_Capita'] * df['Population']) * 1_000_000
        
        # Peace index
        df['Medals_Per_Peace_Index_Point'] = df['Total'] / df['Global_Peace_Index_Score']
        
        # Refugees
        df['Medals_Per_1000_Refugees_Received'] = df['Total'] / df['Refugees_Received'] * 1000
        df['Medals_Per_1000_Refugees_Produced'] = df['Total'] / df['Refugees_Produced'] * 1000
        
        # Military
        df['Medals_Per_Pct_Military_Spending'] = df['Total'] / df['Military_Expenditure_Pct_GDP']
        df['Medals_Per_1000_Military_Personnel'] = df['Total'] / df['Active_Military_Personnel_Thousands'] * 1000
        
        # Education spending
        df['Medals_Per_Pct_Education_Spending'] = df['Total'] / df['Education_Spending_pct_GDP']
        
        print(f"  {season}: Added 22 new normalized metrics")
    
    # Save merged datasets
    print("\nSaving merged datasets...")
    summer_merged.to_csv(data_dir / "summer_olympics_all_metrics.csv", index=False)
    winter_merged.to_csv(data_dir / "winter_olympics_all_metrics.csv", index=False)
    
    print(f"✓ Saved summer_olympics_all_metrics.csv ({len(summer_merged)} records, {len(summer_merged.columns)} columns)")
    print(f"✓ Saved winter_olympics_all_metrics.csv ({len(winter_merged)} records, {len(winter_merged.columns)} columns)")
    
    # Print summary of available metrics
    print("\n" + "="*60)
    print("AVAILABLE NORMALIZED METRICS")
    print("="*60)
    
    metrics = [col for col in summer_merged.columns if col.startswith('Medals_Per_')]
    for i, metric in enumerate(metrics, 1):
        print(f"{i:2d}. {metric}")
    
    print(f"\nTotal: {len(metrics)} metrics available for visualization")
    
    return summer_merged, winter_merged

if __name__ == "__main__":
    print("="*60)
    print("MERGING ALL METRICS INTO OLYMPIC DATASETS")
    print("="*60)
    merge_all_metrics()
