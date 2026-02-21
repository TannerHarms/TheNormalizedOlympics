"""
Compare height and weight distributions of male athletes across different sports using REAL data:
- Olympic athletes (male, 2012-2016)
- NFL players
- Champions League soccer players  
- CrossFit athletes (optional)
- Marathon runners (optional)

Generates comparison visualizations with dynamically sized plots based on available datasets.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# Add plotting directory to path to import style
sys.path.insert(0, str(Path(__file__).parent))
from plotting_style import apply_plot_style

# Set up paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PLOT_DIR = PROJECT_ROOT / 'plots' / 'athlete_body_comparison'
PLOT_DIR.mkdir(parents=True, exist_ok=True)

def load_olympic_data():
    """Load Olympic athlete data for males only, filtered to recent games (2012-2016)."""
    print("Loading Olympic athlete data (2012-2016 - Recent)...")
    
    # Try processed file first
    processed_file = DATA_DIR / 'olympics_recent_male_athletes.csv'
    
    if processed_file.exists():
        df = pd.read_csv(processed_file)
        print(f"Loaded {len(df)} male Olympic athletes")
        print(f"Height: {df['height_cm'].min():.1f} - {df['height_cm'].max():.1f} cm (mean: {df['height_cm'].mean():.1f})")
        print(f"Weight: {df['weight_kg'].min():.1f} - {df['weight_kg'].max():.1f} kg (mean: {df['weight_kg'].mean():.1f})")
        return df[['height_cm', 'weight_kg']]
    
    print(f"❌ Olympic data not found: {processed_file}")
    return None

def load_nfl_data():
    """Load NFL player data."""
    print("\nLoading NFL player data...")
    
    # Try real data first
    nfl_file_real = DATA_DIR / 'nfl_player_data_real.csv'
    
    if not nfl_file_real.exists():
        print(f"❌ NFL data not found: {nfl_file_real}")
        return None
    
    df = pd.read_csv(nfl_file_real)
    
    print(f"Loaded {len(df)} NFL players (REAL)")
    print(f"Height: {df['height_cm'].min():.1f} - {df['height_cm'].max():.1f} cm (mean: {df['height_cm'].mean():.1f})")
    print(f"Weight: {df['weight_kg'].min():.1f} - {df['weight_kg'].max():.1f} kg (mean: {df['weight_kg'].mean():.1f})")
    
    return df[['height_cm', 'weight_kg']]

def load_champions_league_data():
    """Load Champions League player data."""
    print("\nLoading Champions League player data...")
    
    # Try real data
    cl_file_real = DATA_DIR / 'champions_league_player_data_real.csv'
    
    if not cl_file_real.exists():
        print(f"❌ Champions League data not found: {cl_file_real}")
        return None
    
    df = pd.read_csv(cl_file_real)
    
    print(f"Loaded {len(df)} Champions League players (REAL)")
    print(f"Height: {df['height_cm'].min():.1f} - {df['height_cm'].max():.1f} cm (mean: {df['height_cm'].mean():.1f})")
    print(f"Weight: {df['weight_kg'].min():.1f} - {df['weight_kg'].max():.1f} kg (mean: {df['weight_kg'].mean():.1f})")
    
    return df[['height_cm', 'weight_kg']]

def load_crossfit_data():
    """Load CrossFit athlete data (optional)."""
    print("\nLoading CrossFit athlete data...")
    
    cf_file = DATA_DIR / 'crossfit_athlete_data_real.csv'
    
    if not cf_file.exists():
        print(f"⚠ CrossFit data not found (optional)")
        return None
    
    df = pd.read_csv(cf_file)
    print(f"Loaded {len(df)} CrossFit athletes")
    return df[['height_cm', 'weight_kg']]

def load_marathon_data():
    """Load marathon runner data (optional)."""
    print("\nLoading marathon runner data...")
    
    marathon_file = DATA_DIR / 'marathon_runner_data.csv'
    
    if not marathon_file.exists():
        print(f"⚠ Marathon data not found (optional)")
        return None
    
    df = pd.read_csv(marathon_file)
    print(f"Loaded {len(df)} marathon runners")
    return df[['height_cm', 'weight_kg']]

def create_comparison_plot():
    """Create comparison plot of height and weight distributions."""
    print("\n" + "="*80)
    print("Creating comparison plots...")
    print("="*80)
    
    # Load all datasets
    olympic_data = load_olympic_data()
    nfl_data = load_nfl_data()
    cl_data = load_champions_league_data()
    cf_data = load_crossfit_data()
    marathon_data = load_marathon_data()

    # Apply consistent plotting style
    apply_plot_style()
    
    # Define colors for each sport
    colors = {
        'Olympics': '#1f77b4',
        'NFL': '#2ca02c',
        'Champions League': '#d62728',
        'CrossFit': '#ff7f0e',
        'Marathon': '#9467bd'
    }
    
    # Build dataset list (only include available data)
    datasets = []
    if olympic_data is not None:
        datasets.append((olympic_data, 'Olympics', 'Olympics 2012-2016 (Recent)'))
    if nfl_data is not None:
        datasets.append((nfl_data, 'NFL', 'NFL (Historical Rosters)'))
    if cl_data is not None:
        datasets.append((cl_data, 'Champions League', 'Champions League (FIFA 23)'))
    if cf_data is not None:
        datasets.append((cf_data, 'CrossFit', 'CrossFit Games'))
    if marathon_data is not None:
        datasets.append((marathon_data, 'Marathon', 'Elite Marathon Runners'))
    
    if len(datasets) == 0:
        print("❌ No datasets available for plotting!")
        return
    
    # Create figure with dynamic rows
    nrows = len(datasets)
    fig, axes = plt.subplots(nrows, 2, figsize=(16, 4.5 * nrows))
    fig.suptitle('Male Athlete Body Composition Comparison (Real Data)',
                 fontsize=20, fontweight='bold', y=0.995)
    
    # Handle single row case
    if nrows == 1:
        axes = axes.reshape(1, -1)
    
    # Plot each sport
    for row_idx, (data, sport_name, full_label) in enumerate(datasets):
        color = colors[sport_name]
        
        # Height distribution (left column)
        ax_height = axes[row_idx, 0]
        ax_height.hist(data['height_cm'].dropna(), bins=50, color=color,
                      alpha=0.7, edgecolor='black', linewidth=0.5)
        
        # Add mean and median lines
        mean_height = data['height_cm'].mean()
        median_height = data['height_cm'].median()
        ax_height.axvline(mean_height, color='red', linestyle='--',
                         linewidth=2, label=f'Mean: {mean_height:.1f} cm')
        ax_height.axvline(median_height, color='blue', linestyle='--',
                         linewidth=2, label=f'Median: {median_height:.1f} cm')
        
        ax_height.set_xlabel('Height (cm)', fontsize=12, fontweight='bold')
        ax_height.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax_height.set_title(f'{full_label} - Height Distribution',
                           fontsize=13, fontweight='bold')
        ax_height.legend(loc='upper right', fontsize=10)
        ax_height.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add sample size annotation
        n = len(data['height_cm'].dropna())
        ax_height.text(0.02, 0.98, f'n = {n:,}',
                      transform=ax_height.transAxes,
                      verticalalignment='top',
                      bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                      fontsize=10)
        
        # Weight distribution (right column)
        ax_weight = axes[row_idx, 1]
        ax_weight.hist(data['weight_kg'].dropna(), bins=50, color=color,
                      alpha=0.7, edgecolor='black', linewidth=0.5)
        
        # Add mean and median lines
        mean_weight = data['weight_kg'].mean()
        median_weight = data['weight_kg'].median()
        ax_weight.axvline(mean_weight, color='red', linestyle='--',
                         linewidth=2, label=f'Mean: {mean_weight:.1f} kg')
        ax_weight.axvline(median_weight, color='blue', linestyle='--',
                         linewidth=2, label=f'Median: {median_weight:.1f} kg')
        
        ax_weight.set_xlabel('Weight (kg)', fontsize=12, fontweight='bold')
        ax_weight.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax_weight.set_title(f'{full_label} - Weight Distribution',
                           fontsize=13, fontweight='bold')
        ax_weight.legend(loc='upper right', fontsize=10)
        ax_weight.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add sample size annotation
        n = len(data['weight_kg'].dropna())
        ax_weight.text(0.02, 0.98, f'n = {n:,}',
                      transform=ax_weight.transAxes,
                      verticalalignment='top',
                      bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                      fontsize=10)
    
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    
    # Save figure
    output_file = PLOT_DIR / 'male_athlete_body_comparison_real.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Plot saved to: {output_file}")
    
    plt.close()

def create_summary_statistics():
    """Create a summary table of statistics for all sports."""
    print("\n" + "="*80)
    print("Creating summary statistics...")
    print("="*80)
    
    # Load all datasets
    datasets = {
        'Olympics (2012-2016)': load_olympic_data(),
        'NFL': load_nfl_data(),
        'Champions League': load_champions_league_data(),
        'CrossFit': load_crossfit_data(),
        'Marathon': load_marathon_data()
    }
    
    # Calculate statistics
    stats = []
    for name, data in datasets.items():
        if data is None:
            continue
            
        stats.append({
            'Sport': name,
            'Sample Size': len(data),
            'Height Mean (cm)': data['height_cm'].mean(),
            'Height Std (cm)': data['height_cm'].std(),
            'Height Median (cm)': data['height_cm'].median(),
            'Height Min (cm)': data['height_cm'].min(),
            'Height Max (cm)': data['height_cm'].max(),
            'Weight Mean (kg)': data['weight_kg'].mean(),
            'Weight Std (kg)': data['weight_kg'].std(),
            'Weight Median (kg)': data['weight_kg'].median(),
            'Weight Min (kg)': data['weight_kg'].min(),
            'Weight Max (kg)': data['weight_kg'].max(),
        })
    
    if not stats:
        print("❌ No data available for statistics")
        return None
    
    stats_df = pd.DataFrame(stats)
    
    # Save to CSV
    output_file = PLOT_DIR / 'athlete_body_comparison_statistics_real.csv'
    stats_df.to_csv(output_file, index=False, float_format='%.2f')
    print(f"\n✓ Statistics saved to: {output_file}")
    
    # Print to console
    print("\n" + "="*80)
    print("SUMMARY STATISTICS (REAL DATA)")
    print("="*80)
    for col in stats_df.columns:
        if 'cm' in col or 'kg' in col:
            stats_df[col] = stats_df[col].apply(lambda x: f"{x:.1f}")
    print(stats_df.to_string(index=False))
    print("="*80)
    
    return stats_df

if __name__ == '__main__':
    print("\n" + "="*80)
    print("MALE ATHLETE BODY COMPOSITION COMPARISON (REAL DATA)")
    print("="*80)
    
    # Generate plots
    create_comparison_plot()
    
    # Generate summary statistics
    create_summary_statistics()
    
    print("\n" + "="*80)
    print("✓ All plots and statistics generated successfully!")
    print(f"✓ Output directory: {PLOT_DIR}")
    print("="*80)
