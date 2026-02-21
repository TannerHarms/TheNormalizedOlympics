"""
Generate summary plots for ALL available medal types and metrics.

Medal Types:
- Medals by Event (Total)
- Individual Medalists
- Total Medals Awarded (to individual athletes)
- Total Athletes Sent
- Medals per Athlete Sent (ratio)
- Medals Awarded per Athlete Sent (ratio)

Author: Tanner D. Harms, February 2026
"""

import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the plotting function
from plotting.plot_08_summary_figures import create_summary_figure

DATA_DIR = Path(__file__).parent.parent / 'data'

def main():
    """Generate plots for all medal types and metrics."""
    
    # Load data
    print("Loading datasets with all metrics...")
    summer_df = pd.read_csv(DATA_DIR / 'summer_olympics_all_metrics.csv')
    winter_df = pd.read_csv(DATA_DIR / 'winter_olympics_all_metrics.csv')
    
    # Define medal types (what we're measuring)
    medal_types = [
        # Core medal counts
        ('Total', 'Medals by Event'),
        ('Individual_Medalists', 'Individual Medalists'),
        ('Total_Medals_Awarded', 'Total Medals Awarded'),
        ('Total_Athletes', 'Total Athletes Sent'),
    ]
    
    # Calculate ratio metrics for both datasets
    for df in [summer_df, winter_df]:
        # Medals per athlete ratios
        df['Medals_Per_Athlete'] = df['Total'] / df['Total_Athletes']
        df['Medals_Awarded_Per_Athlete'] = df['Total_Medals_Awarded'] / df['Total_Athletes']
    
    # Add ratio medal types
    medal_types.extend([
        ('Medals_Per_Athlete', 'Medals per Athlete Sent'),
        ('Medals_Awarded_Per_Athlete', 'Medals Awarded per Athlete Sent'),
    ])
    
    # Define normalization metrics
    normalization_metrics = [
        # Baseline (unnormalized)
        (None, 'Baseline'),  # Special case - will use medal_type column directly
        
        # Core normalization metrics
        ('Medals_Per_Million', 'Capita'),
        ('Medals_Per_HDI', 'HDI'),
        ('Medals_Per_Billion_GDP', 'GDP'),
        ('Medals_Per_GDP_Per_Capita', 'GDP Per Capita'),
        
        # Geographic metrics
        ('Medals_Per_1000_SqKm', '1000 Square Kilometers'),
        ('Medals_Per_1000_Km_Coastline', '1000 Km Coastline'),
        ('Medals_Per_100m_Elevation', '100m Elevation'),
        
        # Climate metrics
        ('Medals_Per_Degree_Temp', 'Degree Temperature'),
        ('Medals_Per_100_Sunshine_Days', '100 Sunshine Days'),
        ('Medals_Per_100_Cm_Snowfall', '100 Cm Snowfall'),
        
        # Infrastructure metrics
        ('Medals_Per_Million_Internet_Users', 'Million Internet Users'),
        ('Medals_Per_1000_Vehicles', '1000 Vehicles'),
        ('Medals_Per_University', 'University'),
        ('Medals_Per_Stadium', 'Sports Stadium'),
        ('Medals_Per_Ski_Resort', 'Ski Resort'),
        
        # Economic/Social metrics
        ('Medals_Per_Pct_Healthcare_Spending', 'Pct GDP Healthcare Spending'),
        ('Medals_Per_Year_Life_Expectancy', 'Year Life Expectancy'),
        ('Medals_Per_100_Work_Hours', '100 Work Hours Per Year'),
        
        # Cultural metrics
        ('Medals_Per_Million_Kg_Coffee', 'Million Kg Coffee'),
        ('Medals_Per_Million_Cola_Servings', 'Million Cola Servings'),
        ('Medals_Per_Peace_Index_Point', 'Peace Index Point'),
        
        # Refugee metrics
        ('Medals_Per_1000_Refugees_Received', '1000 Refugees Received'),
        ('Medals_Per_1000_Refugees_Produced', '1000 Refugees Produced'),
        
        # Military metrics
        ('Medals_Per_Pct_Military_Spending', 'Pct GDP Military Spending'),
        ('Medals_Per_1000_Military_Personnel', '1000 Military Personnel'),
        
        # Education metrics
        ('Medals_Per_Pct_Education_Spending', 'Pct GDP Education Spending'),
    ]
    
    total_combinations = len(medal_types) * len(normalization_metrics) * 2  # x2 for Summer/Winter
    print(f"\nGenerating plots for {len(medal_types)} medal types × {len(normalization_metrics)} metrics × 2 seasons = {total_combinations} total plots")
    print("="*70)
    
    success_count = 0
    skip_count = 0
    current = 0
    
    for medal_type_col, medal_type_display in medal_types:
        print(f"\n{'='*70}")
        print(f"MEDAL TYPE: {medal_type_display}")
        print(f"{'='*70}")
        
        for norm_col, norm_display in normalization_metrics:
            current += 2  # Summer + Winter
            print(f"\n[{current}/{total_combinations}] {medal_type_display} per {norm_display}")
            
            # For baseline (unnormalized), use the medal_type column directly
            if norm_col is None:
                metric_col = medal_type_col
            else:
                # Check if we need to calculate the normalized metric
                # For ratio medal types (Medals_Per_Athlete), we don't re-normalize
                if medal_type_col in ['Medals_Per_Athlete', 'Medals_Awarded_Per_Athlete']:
                    # These are already ratios - just use them directly for baseline
                    # For normalized metrics, skip (doesn't make sense to normalize a ratio)
                    if norm_col is None:
                        metric_col = medal_type_col
                    else:
                        print(f"  - Skipping normalization of ratio metric")
                        skip_count += 2
                        continue
                else:
                    metric_col = norm_col
            
            # Generate summer plot
            if medal_type_col in summer_df.columns:
                summer_data_count = summer_df[medal_type_col].notna().sum()
                if summer_data_count > 0:
                    try:
                        create_summary_figure(
                            summer_df, 
                            'Summer', 
                            norm_display, 
                            metric_col,
                            medal_type=medal_type_col,
                            medal_type_display=medal_type_display
                        )
                        success_count += 1
                        print(f"  [OK] Summer: {summer_data_count} data points")
                    except Exception as e:
                        print(f"  [FAIL] Summer failed: {e}")
                else:
                    print(f"  - Summer: No data available")
                    skip_count += 1
            else:
                print(f"  - Summer: Column {medal_type_col} not found")
                skip_count += 1
            
            # Generate winter plot
            if medal_type_col in winter_df.columns:
                winter_data_count = winter_df[medal_type_col].notna().sum()
                if winter_data_count > 0:
                    try:
                        create_summary_figure(
                            winter_df, 
                            'Winter', 
                            norm_display, 
                            metric_col,
                            medal_type=medal_type_col,
                            medal_type_display=medal_type_display
                        )
                        success_count += 1
                        print(f"  [OK] Winter: {winter_data_count} data points")
                    except Exception as e:
                        print(f"  [FAIL] Winter failed: {e}")
                else:
                    print(f"  - Winter: No data available")
                    skip_count += 1
            else:
                print(f"  - Winter: Column {medal_type_col} not found")
                skip_count += 1
    
    print("\n" + "="*70)
    print("GENERATION COMPLETE")
    print("="*70)
    print(f"Successfully generated: {success_count} plots")
    print(f"Skipped (no data or N/A): {skip_count}")
    print(f"Total attempted: {total_combinations}")
    print(f"\nPlots organized in: plots/{{medal_type}}/{{normalization_metric}}/")

if __name__ == "__main__":
    main()
