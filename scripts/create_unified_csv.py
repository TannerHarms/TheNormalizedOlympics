"""
Create a single unified CSV file containing all normalization metrics.

Format matches world_bank_data.csv: WB_Code, Year, then all metric columns.
For static/snapshot metrics, the Year column indicates the reference year.

This file is the single source of truth for all normalization data used
to produce the Olympic medal visualizations.
"""

import pandas as pd
from pathlib import Path

data_dir = Path(__file__).parent.parent / "data"


def create_unified_csv():
    """Merge all normalization data sources into one CSV file."""
    
    print("Creating unified normalization metrics CSV...")
    print("=" * 60)
    
    # === TIME-SERIES DATA ===
    
    # World Bank core data (Population, GDP, GDP per capita)
    wb_core = pd.read_csv(data_dir / "world_bank_data.csv")
    print(f"World Bank core: {len(wb_core)} records, {wb_core['WB_Code'].nunique()} countries")
    
    # World Bank additional indicators
    wb_additional = pd.read_csv(data_dir / "additional_world_bank_data.csv")
    wb_additional['Year'] = wb_additional['Year'].astype(int)
    print(f"World Bank additional: {len(wb_additional)} records")
    
    # HDI data
    hdi = pd.read_csv(data_dir / "hdi_data.csv")
    print(f"HDI: {len(hdi)} records")
    
    # Education spending (time series from World Bank API)
    education = pd.read_csv(data_dir / "education_spending.csv")
    education['Year'] = education['Year'].astype(int)
    print(f"Education spending: {len(education)} records")
    
    # Merge time-series data
    unified = wb_core.merge(wb_additional, on=['WB_Code', 'Year'], how='outer')
    unified = unified.merge(hdi, on=['WB_Code', 'Year'], how='outer')
    unified = unified.merge(education, on=['WB_Code', 'Year'], how='left')
    
    print(f"\nTime-series base: {len(unified)} records, {unified['WB_Code'].nunique()} countries")
    
    # === STATIC / SNAPSHOT DATA ===
    # These get merged by WB_Code only (applied to all years)
    
    # Geographic features
    geo = pd.read_csv(data_dir / "geographic_features.csv")
    unified = unified.merge(geo, on='WB_Code', how='left')
    print(f"+ Geographic features: {geo['WB_Code'].nunique()} countries")
    
    # Climate features
    climate = pd.read_csv(data_dir / "climate_features.csv")
    unified = unified.merge(climate, on='WB_Code', how='left')
    print(f"+ Climate features: {climate['WB_Code'].nunique()} countries")
    
    # Sports & culture (2024 snapshot)
    sports = pd.read_csv(data_dir / "sports_culture_data.csv")
    sports_cols = ['WB_Code', 'Number_of_Universities', 'Number_of_Ski_Resorts', 'Professional_Sports_Stadiums']
    unified = unified.merge(sports[sports_cols], on='WB_Code', how='left')
    print(f"+ Sports & culture: {sports['WB_Code'].nunique()} countries")
    
    # Consumption data columns are manually estimated and not reliable enough
    # for normalization — skip coffee/cola consumption merge
    
    # Work hours (time series from OECD SDMX API, 2005-2023)
    work = pd.read_csv(data_dir / "work_hours_data.csv")
    work['Year'] = work['Year'].astype(int)
    work_cols = ['WB_Code', 'Year', 'Avg_Work_Hours_Per_Year']
    unified = unified.merge(work[work_cols], on=['WB_Code', 'Year'], how='left')
    print(f"+ Work hours: {work['WB_Code'].nunique()} countries (time-series)")
    
    # Global Peace Index (2024 snapshot)
    gpi = pd.read_csv(data_dir / "global_peace_index.csv")
    gpi_cols = ['WB_Code', 'Global_Peace_Index_Score']
    unified = unified.merge(gpi[gpi_cols], on='WB_Code', how='left')
    print(f"+ Peace Index: {gpi['WB_Code'].nunique()} countries")
    
    # Refugee data removed — manually compiled estimates are not reliable
    
    # Military data (time series from World Bank API, 2000-2023)
    military = pd.read_csv(data_dir / "military_data.csv")
    military['Year'] = military['Year'].astype(int)
    military_cols = ['WB_Code', 'Year', 'Military_Expenditure_Pct_GDP', 'Active_Military_Personnel_Thousands']
    unified = unified.merge(military[military_cols], on=['WB_Code', 'Year'], how='left')
    print(f"+ Military data: {military['WB_Code'].nunique()} countries (time-series)")
    
    # Sort by country and year
    unified = unified.sort_values(['WB_Code', 'Year']).reset_index(drop=True)
    
    # Remove any duplicate rows that arose from outer joins
    before = len(unified)
    unified = unified.drop_duplicates(subset=['WB_Code', 'Year'], keep='last')
    after = len(unified)
    if before != after:
        print(f"\nRemoved {before - after} duplicate WB_Code-Year rows")
    
    # Save
    output_path = data_dir / "all_normalization_metrics.csv"
    unified.to_csv(output_path, index=False)
    
    print(f"\n{'=' * 60}")
    print(f"Saved: {output_path}")
    print(f"  Records: {len(unified)}")
    print(f"  Countries: {unified['WB_Code'].nunique()}")
    print(f"  Year range: {unified['Year'].min():.0f} - {unified['Year'].max():.0f}")
    print(f"  Columns: {len(unified.columns)}")
    print(f"\nColumn list:")
    for i, col in enumerate(unified.columns, 1):
        non_null = unified[col].notna().sum()
        pct = 100 * non_null / len(unified)
        print(f"  {i:2d}. {col:<45s} ({pct:.0f}% coverage)")


if __name__ == "__main__":
    create_unified_csv()
