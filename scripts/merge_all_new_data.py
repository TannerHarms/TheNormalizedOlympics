"""
Merge improved athlete & medal data into the all_metrics CSVs.

Data sources (all from Olympedia.org):
  - 2018 Winter, 2020 Summer, 2022 Winter, 2024 Summer, 2026 Winter:
      Our direct Olympedia scrape (scripts/scrape_olympedia.py)
      Cache verified against official medal tables.

Strategy:
  - Pre-2018: keep existing Kaggle pipeline data
  - 2018+: REPLACE athlete + medal columns with Olympedia scrape data
  - Recompute historical, rolling-avg, and normalized metrics

Usage:
    python scripts/merge_all_new_data.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Columns that we replace with new authoritative data
REPLACE_COLS = [
    "Total_Athletes", "Individual_Medalists",
    "Gold", "Silver", "Bronze", "Total",
    "Gold_Medalists", "Silver_Medalists", "Bronze_Medalists",
    "Total_Medals_Awarded", "Gold_Awarded", "Silver_Awarded", "Bronze_Awarded",
]

MEDAL_COLS = ["Gold", "Silver", "Bronze", "Total"]
HISTORICAL_COLS = [
    "Historical_Gold", "Historical_Silver", "Historical_Bronze", "Historical_Total",
    "Recent_3_Olympics_Avg",
]


def load_new_data(season: str) -> pd.DataFrame:
    """
    Load new data for a season from our Olympedia scrape.
    Returns a DataFrame with Year, Country, and REPLACE_COLS.
    """
    oly_path = DATA_DIR / f"olympedia_{season.lower()}.csv"
    if not oly_path.exists():
        print(f"    WARNING: No new data found for {season} — {oly_path} missing")
        return pd.DataFrame()
    
    oly = pd.read_csv(oly_path)
    oly = oly[["Year", "Country"] + [c for c in REPLACE_COLS if c in oly.columns]]
    print(f"    Olympedia {season}: {len(oly)} rows, years={sorted(oly['Year'].unique())}")
    return oly


def merge_for_season(season: str, metrics_file: str):
    """Merge new data into an all_metrics CSV for one season."""
    print(f"\n{'='*60}")
    print(f"  MERGING {season.upper()} OLYMPICS")
    print(f"{'='*60}")
    
    # Load current all_metrics data
    metrics_path = DATA_DIR / metrics_file
    df = pd.read_csv(metrics_path)
    original_cols = list(df.columns)
    print(f"  Current: {len(df)} rows, years={sorted(df['Year'].unique())}")
    
    # Load new data from Olympedia scrape
    new_data = load_new_data(season)
    if new_data.empty:
        return
    
    new_years = sorted(new_data["Year"].unique())
    existing_years = sorted(set(df["Year"].unique()) & set(new_years))
    added_years = sorted(set(new_years) - set(df["Year"].unique()))
    
    print(f"\n  Years to UPDATE (replace cols): {existing_years}")
    print(f"  Years to ADD (new rows): {added_years}")
    
    # ===================================================================
    # STEP 1: Update existing years — replace REPLACE_COLS
    # ===================================================================
    for year in existing_years:
        new_year = new_data[new_data["Year"] == year][["Year", "Country"] + REPLACE_COLS].copy()
        
        # Clear old values for this year
        mask = df["Year"] == year
        for col in REPLACE_COLS:
            if col in df.columns:
                df.loc[mask, col] = np.nan
        
        # Build the year slice without the replace cols, then merge new values
        df_year = df[mask].drop(columns=REPLACE_COLS, errors="ignore")
        df_year = df_year.merge(new_year, on=["Year", "Country"], how="left")
        
        # Add countries in new data but not in our existing rows
        existing_countries = set(df_year["Country"])
        new_countries = set(new_year["Country"]) - existing_countries
        if new_countries:
            print(f"    {year}: Adding {len(new_countries)} new countries")
            for noc in sorted(new_countries):
                noc_row = new_year[new_year["Country"] == noc].iloc[0]
                row_dict = {"Year": year, "Country": noc}
                for col in REPLACE_COLS:
                    row_dict[col] = noc_row[col]
                df_year = pd.concat([df_year, pd.DataFrame([row_dict])], ignore_index=True)
        
        # Swap back into main df
        df = pd.concat([df[df["Year"] != year], df_year], ignore_index=True)
        
        # Countries in old data but NOT in new data get NaN — fill with 0
        mask_year = df["Year"] == year
        for col in REPLACE_COLS:
            if col in df.columns:
                df.loc[mask_year, col] = pd.to_numeric(
                    df.loc[mask_year, col], errors="coerce"
                ).fillna(0).astype(int)
        
        n_with_data = new_year["Total_Athletes"].notna().sum()
        print(f"    {year}: Merged {n_with_data} countries with athlete data")
    
    # ===================================================================
    # STEP 2: Add new years (e.g. 2026)
    # ===================================================================
    for year in added_years:
        new_year = new_data[new_data["Year"] == year].copy()
        
        # Carry forward normalization metrics from the most recent year
        latest_year = df["Year"].max()
        df_latest = df[df["Year"] == latest_year].copy()
        
        skip = set(REPLACE_COLS + ["Year", "Country"] + HISTORICAL_COLS)
        carry_cols = [c for c in df.columns if c not in skip]
        
        new_rows = []
        for _, nrow in new_year.iterrows():
            noc = nrow["Country"]
            row_dict = {"Year": year, "Country": noc}
            for col in REPLACE_COLS:
                row_dict[col] = nrow.get(col, np.nan)
            
            # Carry forward from latest year
            prev = df_latest[df_latest["Country"] == noc]
            if not prev.empty:
                for col in carry_cols:
                    if col in prev.columns:
                        row_dict[col] = prev.iloc[0][col]
            new_rows.append(row_dict)
        
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        print(f"    {year}: Added {len(new_rows)} country rows (new year)")
    
    # ===================================================================
    # STEP 2b: Refresh time-series normalization data for ALL years
    # ===================================================================
    # The carry-forward in Step 2 (and the original pipeline for 2018/2022)
    # may have stale values.  Re-join authoritative time-series data using
    # the closest available year (prefer exact match, else nearest prior).
    print(f"\n  Refreshing time-series normalization data for all years...")
    
    # Define each time-series data source: (file, join_cols, value_cols)
    TS_SOURCES = [
        ("world_bank_data.csv",          ["WB_Code", "Year"], ["Population", "GDP", "GDP_per_capita"]),
        ("additional_world_bank_data.csv",["WB_Code", "Year"], [
            "Land_Area_SqKm", "Surface_Area_SqKm", "Internet_Users_Pct",
            "Vehicles_Per_1000", "Healthcare_Spending_Pct_GDP",
            "Healthcare_Spending_Per_Capita_USD", "Life_Expectancy_Years",
            "Labor_Force_Total",
        ]),
        ("hdi_data.csv",                  ["WB_Code", "Year"], ["HDI"]),
        ("military_data.csv",             ["WB_Code", "Year"], [
            "Military_Expenditure_Pct_GDP", "Active_Military_Personnel_Thousands",
        ]),
        ("work_hours_data.csv",           ["WB_Code", "Year"], ["Avg_Work_Hours_Per_Year"]),
        ("education_spending.csv",        ["WB_Code", "Year"], ["Education_Spending_pct_GDP"]),
    ]
    
    olympic_years = sorted(df["Year"].unique())
    
    for src_file, join_keys, value_cols in TS_SOURCES:
        src_path = DATA_DIR / src_file
        if not src_path.exists():
            print(f"    SKIP {src_file} — not found")
            continue
        
        src = pd.read_csv(src_path)
        src["Year"] = src["Year"].astype(int)
        
        # Only keep columns we need (avoid pulling in extra cols like
        # Active_Military_Personnel which may duplicate)
        keep = [k for k in join_keys] + [c for c in value_cols if c in src.columns]
        src = src[keep].copy()
        
        # For each value column, do a per-country nearest-year merge
        
        for vcol in value_cols:
            if vcol not in src.columns:
                continue
            if vcol not in df.columns:
                df[vcol] = np.nan
            
            # Drop rows where this column is NaN so year-mapping only
            # considers years that actually have data for each country
            src_valid = src[src[vcol].notna()][["WB_Code", "Year", vcol]].copy()
            
            # Per-country nearest-year merge: for each (WB_Code, OlympicYear),
            # find the source year with actual data closest to OlympicYear
            # (prefer exact, then nearest prior, then nearest future)
            wb_codes = df["WB_Code"].dropna().unique()
            lookup_rows = []
            for wbc in wb_codes:
                country_src = src_valid[src_valid["WB_Code"] == wbc]
                if country_src.empty:
                    continue
                country_years = sorted(country_src["Year"].unique())
                for oy in olympic_years:
                    if oy in country_years:
                        best_year = oy
                    else:
                        prior = [y for y in country_years if y <= oy]
                        if prior:
                            best_year = max(prior)
                        else:
                            future = [y for y in country_years if y > oy]
                            best_year = min(future) if future else None
                    if best_year is None:
                        continue
                    val = country_src.loc[country_src["Year"] == best_year, vcol].iloc[0]
                    lookup_rows.append({"WB_Code": wbc, "Year": oy, f"_new_{vcol}": val})
            
            if not lookup_rows:
                continue
            lookup = pd.DataFrame(lookup_rows)
            
            # Merge and overwrite
            df = df.merge(lookup, on=["WB_Code", "Year"], how="left")
            mask = df[f"_new_{vcol}"].notna()
            df.loc[mask, vcol] = df.loc[mask, f"_new_{vcol}"]
            df.drop(columns=[f"_new_{vcol}"], inplace=True)
        
        print(f"    ✓ {src_file}: refreshed {value_cols}")
    
    # Also recompute derived spending columns that depend on refreshed data
    if "Healthcare_Spending_Per_Capita_USD" in df.columns and "Population" in df.columns:
        df["Healthcare_Spending_USD"] = pd.to_numeric(
            df["Healthcare_Spending_Per_Capita_USD"], errors="coerce"
        ) * pd.to_numeric(df["Population"], errors="coerce")
    if "GDP" in df.columns and "Military_Expenditure_Pct_GDP" in df.columns:
        df["Military_Expenditure_USD"] = pd.to_numeric(
            df["GDP"], errors="coerce"
        ) * (pd.to_numeric(df["Military_Expenditure_Pct_GDP"], errors="coerce") / 100)
    if "GDP" in df.columns and "Education_Spending_pct_GDP" in df.columns:
        df["Education_Spending_USD"] = pd.to_numeric(
            df["GDP"], errors="coerce"
        ) * (pd.to_numeric(df["Education_Spending_pct_GDP"], errors="coerce") / 100)
    
    # ===================================================================
    # STEP 3: Merge historical medal columns from with_history
    # ===================================================================
    # with_history CSVs are computed from the FULL by_year data (back to
    # 1896/1924), so Historical_* values correctly include pre-1960 medals.
    # We must NOT recompute them within the 1960+ window of all_metrics.
    print(f"\n  Merging historical columns from {season}_olympics_with_history.csv...")
    hist_cols = ["Historical_Gold", "Historical_Silver", "Historical_Bronze",
                 "Historical_Total", "Recent_3_Olympics_Avg"]
    wh_path = DATA_DIR / f"{season}_olympics_with_history.csv"
    if wh_path.exists():
        wh = pd.read_csv(wh_path)
        wh = wh[wh["Year"] >= df["Year"].min()]
        wh_sub = wh[["Year", "Country"] + hist_cols]
        df = df.drop(columns=hist_cols, errors="ignore")
        df = df.merge(wh_sub, on=["Year", "Country"], how="left")
        for col in hist_cols:
            df[col] = df[col].fillna(0)
        # Restore column order: Historical_* right after Total
        cols = list(df.columns)
        total_idx = cols.index("Total") + 1
        for hc in hist_cols:
            cols.remove(hc)
        for i, hc in enumerate(hist_cols):
            cols.insert(total_idx + i, hc)
        df = df[cols]
        print(f"    ✓ Merged from with_history ({len(wh_sub)} rows)")
    else:
        # Fallback: recompute within all_metrics (loses pre-1960 history)
        print(f"    WARNING: {wh_path.name} not found, recomputing in-window...")
        df = df.sort_values(["Country", "Year"]).reset_index(drop=True)
        for medal_col, hist_col in [("Gold", "Historical_Gold"), ("Silver", "Historical_Silver"),
                                     ("Bronze", "Historical_Bronze"), ("Total", "Historical_Total")]:
            if hist_col not in df.columns:
                df[hist_col] = 0
            df[medal_col] = pd.to_numeric(df[medal_col], errors="coerce").fillna(0).astype(int)
            df[hist_col] = df.groupby("Country")[medal_col].transform(
                lambda x: x.shift(1, fill_value=0).cumsum()
            )
        if "Recent_3_Olympics_Avg" not in df.columns:
            df["Recent_3_Olympics_Avg"] = 0.0
        df["Recent_3_Olympics_Avg"] = df.groupby("Country")["Total"].transform(
            lambda x: x.shift(1).rolling(3, min_periods=1).mean().fillna(0)
        )
    
    # ===================================================================
    # STEP 4: Recompute Medals_Per_* normalized metrics
    # ===================================================================
    print(f"  Recomputing Medals_Per_* normalized metrics...")
    
    normalization_pairs = {
        "Medals_Per_Million": ("Total", "Population", 1e6),
        "Medals_Per_Billion_GDP": ("Total", "GDP", 1e9),
        "Medals_Per_GDP_Per_Capita": ("Total", "GDP_per_capita", 1e4),
        "Medals_Per_HDI": ("Total", "HDI", 1),
        "Medals_Per_1000_SqKm": ("Total", "Land_Area_SqKm", 1e3),
        "Medals_Per_1000_Km_Coastline": ("Total", "Coastline_Length_Km", 1e3),
        "Medals_Per_100m_Elevation": ("Total", "Average_Elevation_Meters", 100),
        "Medals_Per_Degree_Temp": ("Total", "Avg_Temperature_C", 1),
        "Medals_Per_100_Sunshine_Days": ("Total", "Sunshine_Days_Per_Year", 100),
        "Medals_Per_100_Cm_Snowfall": ("Total", "Avg_Snowfall_Cm_Per_Year", 100),
        "Medals_Per_Million_Internet_Users": ("Total", "Internet_Users_Pct", 1e6),
        "Medals_Per_1000_Vehicles": ("Total", "Vehicles_Per_1000", 1e3),
        "Medals_Per_University": ("Total", "Number_of_Universities", 1),
        "Medals_Per_Stadium": ("Total", "Professional_Sports_Stadiums", 1),
        "Medals_Per_Ski_Resort": ("Total", "Number_of_Ski_Resorts", 1),
        "Medals_Per_Pct_Healthcare_Spending": ("Total", "Healthcare_Spending_Pct_GDP", 1),
        "Medals_Per_Year_Life_Expectancy": ("Total", "Life_Expectancy_Years", 1),
        "Medals_Per_100_Work_Hours": ("Total", "Avg_Work_Hours_Per_Year", 100),
        "Medals_Per_Peace_Index_Point": ("Total", "Global_Peace_Index_Score", 1),
        "Medals_Per_Pct_Military_Spending": ("Total", "Military_Expenditure_Pct_GDP", 1),
        "Medals_Per_1000_Military_Personnel": ("Total", "Active_Military_Personnel_Thousands", 1e3),
        "Medals_Per_Pct_Education_Spending": ("Total", "Education_Spending_pct_GDP", 1),
    }
    
    for norm_col, (num_col, denom_col, scale) in normalization_pairs.items():
        if norm_col in df.columns and denom_col in df.columns:
            denom = pd.to_numeric(df[denom_col], errors="coerce").replace(0, np.nan)
            num = pd.to_numeric(df[num_col], errors="coerce").fillna(0)
            df[norm_col] = np.where(
                denom.notna() & (num > 0),
                num / (denom / scale),
                0.0
            )
    
    # Also the lowercase variants
    lowercase_pairs = {
        "Medals_per_million_pop": ("Total", "Population", 1e6),
        "Medals_per_billion_GDP": ("Total", "GDP", 1e9),
        "Medals_per_10K_GDPpc": ("Total", "GDP_per_capita", 1e4),
        "Medals_per_HDI": ("Total", "HDI", 1),
        "Gold_per_million_pop": ("Gold", "Population", 1e6),
        "Gold_per_billion_GDP": ("Gold", "GDP", 1e9),
        "Gold_per_10K_GDPpc": ("Gold", "GDP_per_capita", 1e4),
        "Gold_per_HDI": ("Gold", "HDI", 1),
    }
    
    for norm_col, (num_col, denom_col, scale) in lowercase_pairs.items():
        if norm_col in df.columns and denom_col in df.columns:
            denom = pd.to_numeric(df[denom_col], errors="coerce").replace(0, np.nan)
            num = pd.to_numeric(df[num_col], errors="coerce").fillna(0)
            df[norm_col] = np.where(
                denom.notna() & (num > 0),
                num / (denom / scale),
                0.0
            )
    
    # ===================================================================
    # STEP 5: Save — preserve original column order
    # ===================================================================
    # Ensure all original columns exist, add any new ones at the end
    for col in original_cols:
        if col not in df.columns:
            df[col] = np.nan
    
    # Order: original cols first, then any new
    extra_cols = [c for c in df.columns if c not in original_cols]
    df = df[original_cols + extra_cols]
    
    df = df.sort_values(["Year", "Country"]).reset_index(drop=True)
    df.to_csv(metrics_path, index=False)
    
    print(f"\n  SAVED: {metrics_path.name}")
    print(f"    {len(df)} rows, {len(df.columns)} columns")
    print(f"    Years: {sorted(df['Year'].unique())}")
    
    # Validation
    for year in sorted(new_years):
        yd = df[df["Year"] == year]
        ta = yd["Total_Athletes"].notna().sum()
        ta_sum = pd.to_numeric(yd["Total_Athletes"], errors="coerce").sum()
        tot_sum = yd["Total"].sum()
        print(f"    {year}: {len(yd)} countries, "
              f"Total_Athletes filled={ta}, sum(TA)={int(ta_sum)}, sum(Total)={int(tot_sum)}")


def main():
    print("=" * 60)
    print("  MERGE NEW DATA INTO ALL-METRICS CSVs")
    print("  Source: Olympedia scrape (2018-2026)")
    print("=" * 60)
    
    # Show what's available
    for fname in ["olympedia_summer.csv", "olympedia_winter.csv"]:
        path = DATA_DIR / fname
        if path.exists():
            df = pd.read_csv(path)
            print(f"  Found {fname}: {len(df)} rows, years={sorted(df['Year'].unique())}")
        else:
            print(f"  Missing {fname}")
    
    merge_for_season("Winter", "winter_olympics_all_metrics.csv")
    merge_for_season("Summer", "summer_olympics_all_metrics.csv")
    
    print(f"\n{'='*60}")
    print("  DONE")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
