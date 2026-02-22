"""
Add athlete data for Winter Olympics 2018 and 2022 from olympic_results.csv

This script extracts Total_Athletes, Individual_Medalists, and Total_Medals_Awarded
from the olympic_results.csv file for PyeongChang 2018 and Beijing 2022, then
updates the winter_olympics_all_metrics.csv file.

NOTE: Since olympic_results.csv doesn't have full team rosters for 2018/2022,
Total_Medals_Awarded is estimated using country-specific historical multipliers
from 2014 (most recent year with complete athlete-level data).

Author: Tanner D. Harms
"""

import pandas as pd
from pathlib import Path
import numpy as np

# Paths
DATA_DIR = Path(__file__).parent.parent / 'data'
RAW_DIR = DATA_DIR / 'raw'
RESULTS_FILE = RAW_DIR / 'olympic_results.csv'
WINTER_METRICS_FILE = DATA_DIR / 'winter_olympics_all_metrics.csv'

def calculate_historical_multipliers(df_winter):
    """
    Calculate overall average multipliers from 2014 Winter Olympics
    for estimating Total_Medals_Awarded and per-type Awarded counts.
    
    Uses global averages (not per-country) to avoid outliers from team
    sports like hockey that inflate individual country multipliers.
    
    Returns: dict of {overall, Gold, Silver, Bronze} multipliers
    """
    df_2014 = df_winter[df_winter['Year'] == 2014].copy()
    
    overall = {
        'overall': df_2014['Total_Medals_Awarded'].sum() / df_2014['Total'].sum()
    }
    for medal_type in ['Gold', 'Silver', 'Bronze']:
        total_events = df_2014[medal_type].sum()
        total_awarded = df_2014.get(f'{medal_type}_Awarded', pd.Series([0])).sum()
        overall[medal_type] = total_awarded / total_events if total_events > 0 else 1.0
    
    print(f"\nCalculated historical multipliers from 2014:")
    print(f"  Overall multipliers: TMA/Total={overall['overall']:.3f}, "
          f"GA/G={overall['Gold']:.3f}, SA/S={overall['Silver']:.3f}, BA/B={overall['Bronze']:.3f}")
    
    return overall

def _parse_names_from_row(row):
    """Extract athlete name(s) from a result row.
    
    The 'athletes' column may contain:
      - A plain name: "Francesco FRIEDRICH"
      - A Python repr of list-of-tuples: [('Name', 'url'), ('Name2', 'url2')]
      - Comma or slash separated names: "Name1, Name2"
    We must handle all formats and avoid counting URLs as names.
    """
    import ast
    names = set()
    if pd.notna(row['athlete_full_name']):
        names.add(row['athlete_full_name'].strip())
    if pd.notna(row['athletes']):
        athletes_str = str(row['athletes']).strip()
        if not athletes_str:
            return names
        # Try parsing as Python literal (list of tuples with URLs)
        if athletes_str.startswith('[') or athletes_str.startswith('('):
            try:
                parsed = ast.literal_eval(athletes_str)
                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, (list, tuple)) and len(item) >= 1:
                            names.add(str(item[0]).strip())
                        elif isinstance(item, str):
                            names.add(item.strip())
                elif isinstance(parsed, tuple) and len(parsed) >= 1:
                    # Single tuple like ('Name', 'url')
                    if isinstance(parsed[0], str) and not parsed[0].startswith('http'):
                        names.add(parsed[0].strip())
                return names
            except (ValueError, SyntaxError):
                pass  # Fall through to plain text parsing
        # Plain text: try comma/slash splitting
        for sep in [',', '/']:
            if sep in athletes_str:
                for name in athletes_str.split(sep):
                    name = name.strip()
                    if name and not name.startswith('http'):
                        names.add(name)
                return names
        # Single name
        if not athletes_str.startswith('http'):
            names.add(athletes_str)
    return names


def extract_athlete_counts(df_results, game_slug, year):
    """
    Extract athlete counts AND medal counts from olympic_results.csv for a specific game.
    
    Returns dict with Total_Athletes, Individual_Medalists, Total_Medals_Awarded,
    Gold, Silver, Bronze, Total, Gold_Medalists, Silver_Medalists, Bronze_Medalists
    by country.
    """
    # Filter to the specific game
    game_data = df_results[df_results['slug_game'] == game_slug].copy()
    
    print(f"\n{game_slug} ({year}):")
    print(f"  Total result rows: {len(game_data)}")
    
    MEDAL_RANK = {'GOLD': 3, 'SILVER': 2, 'BRONZE': 1}
    RANK_TO_LABEL = {3: 'Gold', 2: 'Silver', 1: 'Bronze'}
    
    country_results = {}
    
    for country_code_3 in game_data['country_3_letter_code'].unique():
        if pd.isna(country_code_3):
            continue
            
        country_data = game_data[game_data['country_3_letter_code'] == country_code_3]
        
        # --- All athletes (unique names) ---
        all_athletes = set()
        for _, row in country_data.iterrows():
            all_athletes |= _parse_names_from_row(row)
        total_athletes = len(all_athletes)
        
        # --- Medal data ---
        medal_data = country_data[country_data['medal_type'].isin(['GOLD', 'SILVER', 'BRONZE'])]
        
        # Track each medalist's highest medal for per-type medalist counts
        medalist_best = {}  # name -> highest rank
        for _, row in medal_data.iterrows():
            medal_rank = MEDAL_RANK[row['medal_type']]
            names = _parse_names_from_row(row)
            for name in names:
                if name in medalist_best:
                    medalist_best[name] = max(medalist_best[name], medal_rank)
                else:
                    medalist_best[name] = medal_rank
        
        individual_medalists = len(medalist_best)
        
        # Per-type medalist counts (by highest medal won)
        gold_medalists = sum(1 for r in medalist_best.values() if r == 3)
        silver_medalists = sum(1 for r in medalist_best.values() if r == 2)
        bronze_medalists = sum(1 for r in medalist_best.values() if r == 1)
        
        # Count event-based medal counts (Gold/Silver/Bronze/Total columns)
        gold_medals = len(medal_data[medal_data['medal_type'] == 'GOLD'])
        silver_medals = len(medal_data[medal_data['medal_type'] == 'SILVER'])
        bronze_medals = len(medal_data[medal_data['medal_type'] == 'BRONZE'])
        total_medals = gold_medals + silver_medals + bronze_medals
        
        country_results[country_code_3] = {
            'Total_Athletes': total_athletes,
            'Individual_Medalists': individual_medalists,
            'Gold_Medalists': gold_medalists,
            'Silver_Medalists': silver_medalists,
            'Bronze_Medalists': bronze_medalists,
            'Total_Medals_Awarded': 0,  # will be estimated later
            'Gold_Awarded': 0,
            'Silver_Awarded': 0,
            'Bronze_Awarded': 0,
            'Gold': gold_medals,
            'Silver': silver_medals,
            'Bronze': bronze_medals,
            'Total': total_medals
        }
    
    print(f"  Countries processed: {len(country_results)}")
    print(f"  Sample (first 3 medal-winning countries):")
    shown = 0
    for code, stats in country_results.items():
        if stats['Total'] > 0 and shown < 3:
            print(f"    {code}: {stats['Total_Athletes']} athletes, "
                  f"{stats['Individual_Medalists']} medalists "
                  f"(GM:{stats['Gold_Medalists']}/SM:{stats['Silver_Medalists']}/BM:{stats['Bronze_Medalists']}), "
                  f"{stats['Total']} events (G:{stats['Gold']},S:{stats['Silver']},B:{stats['Bronze']})")
            shown += 1
    
    return country_results

def _estimate_awarded(stats, overall):
    """Estimate Total_Medals_Awarded and per-type Awarded using 2014 overall multipliers.
    
    We use the global average multiplier per medal type (not per-country) because
    country-specific multipliers from a single year are unreliable — team sports
    like hockey create extreme outliers (e.g., CAN Gold 5.9x).
    """
    for medal_type in ['Gold', 'Silver', 'Bronze']:
        events = stats[medal_type]
        mult = overall.get(medal_type, 1.0)
        stats[f'{medal_type}_Awarded'] = int(round(events * mult)) if events > 0 else 0
    
    stats['Total_Medals_Awarded'] = (
        stats['Gold_Awarded'] + stats['Silver_Awarded'] + stats['Bronze_Awarded']
    )


def _set_row_from_stats(template_row, stats, year):
    """Set all medal/athlete columns on a template row from stats dict."""
    template_row['Year'] = year
    template_row['Total_Athletes'] = stats['Total_Athletes']
    template_row['Individual_Medalists'] = stats['Individual_Medalists']
    template_row['Total_Medals_Awarded'] = stats['Total_Medals_Awarded']
    template_row['Gold_Awarded'] = stats['Gold_Awarded']
    template_row['Silver_Awarded'] = stats['Silver_Awarded']
    template_row['Bronze_Awarded'] = stats['Bronze_Awarded']
    template_row['Gold_Medalists'] = stats['Gold_Medalists']
    template_row['Silver_Medalists'] = stats['Silver_Medalists']
    template_row['Bronze_Medalists'] = stats['Bronze_Medalists']
    template_row['Gold'] = stats['Gold']
    template_row['Silver'] = stats['Silver']
    template_row['Bronze'] = stats['Bronze']
    template_row['Total'] = stats['Total']
    return template_row


def main():
    """Process Winter 2018 and 2022 data and update metrics file."""
    
    print("="*70)
    print("Adding Winter Olympics 2018 and 2022 Athlete Data")
    print("="*70)
    
    # Load existing winter metrics first (needed for calculating multipliers)
    print(f"\nLoading {WINTER_METRICS_FILE}...")
    df_winter = pd.read_csv(WINTER_METRICS_FILE)
    print(f"Current shape: {df_winter.shape}")
    print(f"Current years: {sorted(df_winter['Year'].unique())}")
    
    # Calculate historical multipliers for estimating awarded counts
    overall = calculate_historical_multipliers(df_winter)
    
    # Load olympic results
    print(f"\nLoading {RESULTS_FILE}...")
    df_results = pd.read_csv(RESULTS_FILE, low_memory=False)
    print(f"Loaded {len(df_results):,} result rows")
    
    # Extract data for 2018 and 2022
    winter_2018 = extract_athlete_counts(df_results, 'pyeongchang-2018', 2018)
    winter_2022 = extract_athlete_counts(df_results, 'beijing-2022', 2022)
    
    # Estimate Total_Medals_Awarded and per-type Awarded using historical multipliers
    print(f"\nEstimating Awarded counts using overall multipliers from 2014:")
    for label, game_data in [('2018', winter_2018), ('2022', winter_2022)]:
        for country_code, stats in game_data.items():
            if stats['Total'] > 0:
                _estimate_awarded(stats, overall)
                print(f"  {label} {country_code}: events G:{stats['Gold']}/S:{stats['Silver']}/B:{stats['Bronze']}={stats['Total']} "
                      f"-> awarded GA:{stats['Gold_Awarded']}/SA:{stats['Silver_Awarded']}/BA:{stats['Bronze_Awarded']}={stats['Total_Medals_Awarded']}")
    
    # Check if 2018/2022 already exist
    has_2018 = 2018 in df_winter['Year'].values
    has_2022 = 2022 in df_winter['Year'].values
    
    if has_2018 or has_2022:
        print(f"\nInfo: Data already exists for years: {[y for y in [2018, 2022] if y in df_winter['Year'].values]}")
        print("Removing existing 2018/2022 data to replace with updated values...")
        df_winter = df_winter[~df_winter['Year'].isin([2018, 2022])]
        print(f"Removed existing 2018/2022 data. New shape: {df_winter.shape}")
    
    # Add new data for 2018 and 2022
    for year, game_data in [(2018, winter_2018), (2022, winter_2022)]:
        print(f"\nAdding {year} data...")
        added = 0
        for country_code, stats in game_data.items():
            existing_country = df_winter[df_winter['Country'] == country_code]
            if len(existing_country) == 0:
                print(f"  Warning: {country_code} not found in existing data, skipping")
                continue
            template_row = existing_country.iloc[-1].copy()
            _set_row_from_stats(template_row, stats, year)
            df_winter = pd.concat([df_winter, template_row.to_frame().T], ignore_index=True)
            added += 1
        print(f"  Added {added} countries for {year}")
    
    # Sort by Country and Year BEFORE recalculating
    df_winter = df_winter.sort_values(['Country', 'Year']).reset_index(drop=True)
    
    # Recalculate all normalized metrics for 2018 and 2022 rows
    print(f"\nRecalculating normalized metrics for 2018/2022...")
    
    # Get boolean mask for 2018/2022 rows
    mask_2018_2022 = df_winter['Year'].isin([2018, 2022])
    rows_to_recalc = df_winter[mask_2018_2022]
    
    print(f"  Found {len(rows_to_recalc)} rows to recalculate")
    
    # Recalculate for each row
    for idx in rows_to_recalc.index:
        total = df_winter.at[idx, 'Total']
        population = df_winter.at[idx, 'Population']
        
        # Helper function to handle division by zero
        def safe_divide(numerator, denominator, multiplier=1):
            if pd.isna(denominator) or denominator == 0:
                return np.nan
            return (numerator / denominator) * multiplier
        
        # Basic metrics
        df_winter.at[idx, 'Medals_Per_Million'] = safe_divide(total, population, 1_000_000)
        df_winter.at[idx, 'Medals_Per_Billion_GDP'] = safe_divide(total, df_winter.at[idx, 'GDP'], 1_000_000_000)
        df_winter.at[idx, 'Medals_Per_GDP_Per_Capita'] = safe_divide(total, df_winter.at[idx, 'GDP_per_capita'], 10_000)
        df_winter.at[idx, 'Medals_Per_HDI'] = safe_divide(total, df_winter.at[idx, 'HDI'])
        
        # Geographic metrics
        df_winter.at[idx, 'Medals_Per_1000_SqKm'] = safe_divide(total, df_winter.at[idx, 'Land_Area_SqKm'], 1000)
        df_winter.at[idx, 'Medals_Per_1000_Km_Coastline'] = safe_divide(total, df_winter.at[idx, 'Coastline_Length_Km'], 1000)
        df_winter.at[idx, 'Medals_Per_100m_Elevation'] = safe_divide(total, df_winter.at[idx, 'Average_Elevation_Meters'], 100)
        
        # Climate metrics
        df_winter.at[idx, 'Medals_Per_Degree_Temp'] = safe_divide(total, abs(df_winter.at[idx, 'Avg_Temperature_C']))
        df_winter.at[idx, 'Medals_Per_100_Sunshine_Days'] = safe_divide(total, df_winter.at[idx, 'Sunshine_Days_Per_Year'], 100)
        df_winter.at[idx, 'Medals_Per_100_Cm_Snowfall'] = safe_divide(total, df_winter.at[idx, 'Avg_Snowfall_Cm_Per_Year'], 100)
        
        # Infrastructure metrics
        internet_users = df_winter.at[idx, 'Internet_Users_Pct'] * population / 100
        df_winter.at[idx, 'Medals_Per_Million_Internet_Users'] = safe_divide(total, internet_users, 1_000_000)
        vehicles = df_winter.at[idx, 'Vehicles_Per_1000'] * population / 1000
        df_winter.at[idx, 'Medals_Per_1000_Vehicles'] = safe_divide(total, vehicles, 1000)
        df_winter.at[idx, 'Medals_Per_University'] = safe_divide(total, df_winter.at[idx, 'Number_of_Universities'])
        df_winter.at[idx, 'Medals_Per_Stadium'] = safe_divide(total, df_winter.at[idx, 'Professional_Sports_Stadiums'])
        df_winter.at[idx, 'Medals_Per_Ski_Resort'] = safe_divide(total, df_winter.at[idx, 'Number_of_Ski_Resorts'])
        
        # Economic/Social metrics
        df_winter.at[idx, 'Medals_Per_Pct_Healthcare_Spending'] = safe_divide(total, df_winter.at[idx, 'Healthcare_Spending_Pct_GDP'])
        df_winter.at[idx, 'Medals_Per_Year_Life_Expectancy'] = safe_divide(total, df_winter.at[idx, 'Life_Expectancy_Years'])
        df_winter.at[idx, 'Medals_Per_100_Work_Hours'] = safe_divide(total, df_winter.at[idx, 'Avg_Work_Hours_Per_Year'], 100)
        
        # Cultural metrics
        df_winter.at[idx, 'Medals_Per_Peace_Index_Point'] = safe_divide(total, df_winter.at[idx, 'Global_Peace_Index_Score'])
        
        # Military metrics
        df_winter.at[idx, 'Medals_Per_Pct_Military_Spending'] = safe_divide(total, df_winter.at[idx, 'Military_Expenditure_Pct_GDP'])
        df_winter.at[idx, 'Medals_Per_1000_Military_Personnel'] = safe_divide(total, df_winter.at[idx, 'Active_Military_Personnel_Thousands'], 1000)
        
        # Education metrics
        df_winter.at[idx, 'Medals_Per_Pct_Education_Spending'] = safe_divide(total, df_winter.at[idx, 'Education_Spending_pct_GDP'])
    
    print(f"  ✓ Recalculated {len(rows_to_recalc)} rows with corrected normalized metrics")
    
    print(f"\nFinal shape: {df_winter.shape}")
    print(f"Final years: {sorted(df_winter['Year'].unique())}")
    
    # Save updated file
    print(f"\nSaving to {WINTER_METRICS_FILE}...")
    df_winter.to_csv(WINTER_METRICS_FILE, index=False)
    
    print("\n" + "="*70)
    print("SUCCESS: Winter Olympics 2018 and 2022 data added!")
    print("="*70)
    
    # Summary statistics
    print(f"\nSummary:")
    print(f"  2018: {len(winter_2018)} countries with athlete data")
    print(f"  2022: {len(winter_2022)} countries with athlete data")
    print(f"  Total rows in updated file: {len(df_winter)}")
    
    # Show coverage for 2018/2022
    coverage_2018 = df_winter[(df_winter['Year'] == 2018) & (df_winter['Total_Athletes'].notna())]
    coverage_2022 = df_winter[(df_winter['Year'] == 2022) & (df_winter['Total_Athletes'].notna())]
    print(f"  2018 coverage: {len(coverage_2018)} countries with athlete data")
    print(f"  2022 coverage: {len(coverage_2022)} countries with athlete data")

if __name__ == "__main__":
    main()
