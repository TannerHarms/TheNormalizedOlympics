# Extending Athlete Data to 2018-2024

## Overview

The original Kaggle dataset ("120 years of Olympic history") only covers through 2016. To extend coverage to 2024, we use updated Kaggle datasets that include recent Olympics.

## Data Sources

### Original Dataset (1896-2016)
- **Source**: [120 years of Olympic history](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results)
- **File**: `athlete_events.csv`
- **Coverage**: 1896-2016
- **Size**: 271,116 athlete records

### Extended Dataset (1896-2024)
- **Summer Olympics**: [Summer Olympics Medals (1896-2024)](https://www.kaggle.com/datasets/stefanydeoliveira/summer-olympics-medals-1896-2024) by Stefany De Oliveira
- **Winter Olympics**: [Olympic Summer & Winter Games, 1896-2022](https://www.kaggle.com/datasets/piterfm/olympic-games-medals-19862018) by Petro Ivaniuk
- **Coverage**: Through 2024 Paris Olympics and 2022 Beijing Winter Olympics
- **Purpose**: Fill gaps in athlete-level data for recent Olympics

## Workflow

### Step 1: Download Extended Data

```bash
python scripts/download_extended_athlete_data.py
```

This downloads:
- `olympics_dataset.csv` - Summer Olympics 1896-2024
- `olympic_athletes.csv` - Combined Summer/Winter through 2022

**Requirements**:
- Kaggle API installed: `pip install kaggle`
- Kaggle credentials in `~/.kaggle/kaggle.json`

### Step 2: Process and Merge

```bash
python scripts/process_extended_athlete_data.py
```

This creates:
- `athlete_events_extended.csv` - Combined dataset with 1896-2024 coverage
- Backup of original: `athlete_events_original_backup.csv`

### Step 3: Calculate Athlete Statistics

```bash
python scripts/add_athlete_medal_counts.py
```

This updates:
- `summer_olympics_all_metrics.csv` - Adds athlete columns for 2020, 2024
- `winter_olympics_all_metrics.csv` - Adds athlete columns for 2018, 2022

**Columns added**:
- `Total_Athletes`: Count of unique athletes per country/year
- `Individual_Medalists`: Count of unique medal-winning athletes
- `Total_Medals_Awarded`: Total medals given to individual athletes

## What Gets Filled

### Before (Original Data Only)

| Year | Country | Total | Total_Athletes | Individual_Medalists | Total_Medals_Awarded |
|------|---------|-------|----------------|---------------------|---------------------|
| 2016 | USA     | 121   | 567            | 137                 | 264                 |
| 2020 | USA     | 113   | NaN            | NaN                 | NaN                 |
| 2024 | USA     | 126   | NaN            | NaN                 | NaN                 |

### After (Extended Data)

| Year | Country | Total | Total_Athletes | Individual_Medalists | Total_Medals_Awarded |
|------|---------|-------|----------------|---------------------|---------------------|
| 2016 | USA     | 121   | 567            | 137                 | 264                 |
| 2020 | USA     | 113   | 615            | 140                 | 263                 |
| 2024 | USA     | 126   | 592            | 143                 | 281                 |

## Data Alignment Notes

### Column Mapping

The extended datasets have slightly different column names:

| Original | Extended |
|----------|----------|
| ID | player_id |
| Age | (not available) |
| Height | (not available) |
| Weight | (not available) |
| Games | (constructed from Year + Season) |

Missing columns (Age, Height, Weight) are filled with NaN for 2018-2024 data.

### Known Gaps

- **2017**: No Olympics (as expected)
- **Age/Height/Weight**: Not available in extended datasets for 2018-2024
- **Winter 2026**: Not yet held (Milano-Cortina)

## Alternative: Wikipedia Data

If Kaggle datasets are unavailable, Wikipedia provides:
- **Athlete counts by country**: Total team sizes (≈ Total_Athletes)
- **Medal tables**: Gold/Silver/Bronze by country

However, Wikipedia does NOT provide:
- Individual athlete names → Can't calculate Individual_Medalists
- Athlete-level medal data → Can't calculate Total_Medals_Awarded

Therefore, Kaggle extended datasets are strongly preferred.

## Verification

After running the pipeline, verify coverage:

```python
import pandas as pd

df = pd.read_csv('data/summer_olympics_all_metrics.csv')
print(df[df['Year'] >= 2016][['Year', 'Country', 'Total_Athletes']].head(20))
```

Expected: No NaN values for 2020 and 2024.

## Updates

- **February 2026**: Initial extension to cover through 2024 Paris Olympics
- **Future**: Will need updates after each Olympic Games (every 2 years)

## See Also

- [DATA_SOURCES.md](../DATA_SOURCES.md) - Complete data provenance
- [README.md](../README.md) - Full project documentation
