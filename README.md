# Normalizing the Olympics

Which countries truly perform best at the Olympics when you account for population, wealth, geography, climate, and culture? This project normalizes Olympic medal counts by 25 different metrics to answer that question.

Covers **Summer Olympics (1896–2024)** and **Winter Olympics (1924–2022)**, with analysis focused on the **modern Olympic era (2000–2024)**.

## Project Structure

```
NormalizingTheOlympics/
├── data/
│   ├── raw/                              # Raw Kaggle dataset (athlete_events.csv)
│   ├── all_normalization_metrics.csv     # Unified normalization data (all metrics)
│   ├── summer_olympics_all_metrics.csv   # Final Summer dataset (medals + all metrics)
│   ├── winter_olympics_all_metrics.csv   # Final Winter dataset (medals + all metrics)
│   ├── summer_olympics_normalized.csv    # Intermediate: medals + core metrics
│   ├── winter_olympics_normalized.csv    # Intermediate: medals + core metrics
│   ├── world_bank_data.csv              # Population, GDP, GDP per capita
│   ├── additional_world_bank_data.csv   # Land area, internet, healthcare, etc.
│   ├── hdi_data.csv                     # Human Development Index
│   ├── climate_data.csv                 # Climate zone classification
│   ├── climate_features.csv             # Temperature, snowfall, sunshine
│   ├── geographic_features.csv          # Coastline, elevation
│   ├── sports_culture_data.csv          # Universities, stadiums, ski resorts
│   ├── consumption_data.csv             # Coffee, cola consumption
│   ├── work_hours_data.csv              # OECD work hours
│   ├── global_peace_index.csv           # Global Peace Index scores
│   ├── refugee_data.csv                 # UNHCR refugee statistics
│   ├── military_data.csv                # Military spending & personnel
│   └── education_spending.csv           # Education spending (% of GDP)
├── scripts/
│   ├── download_kaggle_data.py          # Download Kaggle dataset
│   ├── process_kaggle_data.py           # Aggregate to country-year totals
│   ├── add_recent_olympics.py           # Add 2018–2024 data (legacy Wikipedia scraper)
│   ├── scrape_olympedia.py             # Direct Olympedia scraper (2018–2024)
│   ├── merge_all_new_data.py           # Merge Olympedia data into all_metrics CSVs
│   ├── fix_country_names.py             # Convert full names → NOC codes
│   ├── collect_world_bank_data.py       # Fetch World Bank core indicators
│   ├── collect_additional_metrics.py    # Fetch World Bank additional indicators
│   ├── collect_hdi_data.py              # Fetch UNDP HDI data
│   ├── collect_climate_data.py          # Climate zone classification
│   ├── collect_education_spending.py    # Education spending data
│   ├── collect_refugee_data.py          # UNHCR refugee statistics
│   ├── collect_military_data.py         # Military spending & personnel
│   ├── fetch_manual_metrics.py          # Geographic, climate, culture data
│   ├── country_mapping.py              # NOC ↔ World Bank code mapping
│   ├── calculate_historical_medals.py   # Cumulative medal histories
│   ├── merge_all_data.py               # Merge core data + normalize
│   ├── merge_all_metrics.py            # Merge all additional metrics
│   └── create_unified_csv.py           # Create unified normalization CSV
├── plotting/
│   ├── plotting_style.py               # Shared matplotlib styling
│   ├── plot_08_summary_figures.py      # Core 3-panel summary figure engine
│   ├── plot_09_all_metrics.py          # Batch runner for all 25 metrics
│   ├── plot_01–07_*.py                 # Legacy individual metric plots
│   └── README.md                       # Plotting documentation
├── plots/                              # Generated visualizations (49 PNGs)
├── tests/
│   └── test_pipeline.py                # Data integrity tests
├── DATA_SOURCES.md                     # Full data provenance documentation
└── requirements.txt                    # Python dependencies
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Data Pipeline

Run scripts in order. Steps 1–8 collect data (require internet); steps 9–12 process locally.

```bash
# Step 1: Collect Olympic medal data
python scripts/download_kaggle_data.py
python scripts/process_kaggle_data.py
python scripts/add_recent_olympics.py
python scripts/fix_country_names.py

# Step 2: Collect normalization data
python scripts/collect_world_bank_data.py
python scripts/collect_additional_metrics.py
python scripts/collect_hdi_data.py
python scripts/collect_climate_data.py
python scripts/collect_education_spending.py
python scripts/collect_refugee_data.py
python scripts/collect_military_data.py
python scripts/fetch_manual_metrics.py

# Step 3: Process and merge
python scripts/calculate_historical_medals.py
python scripts/merge_all_data.py
python scripts/merge_all_metrics.py
python scripts/create_unified_csv.py

# Step 4: Generate visualizations
python plotting/plot_09_all_metrics.py
```

## Normalization Metrics (25 total)

| Category | Metric | Formula | Source |
|----------|--------|---------|--------|
| **Core (4)** | Per Capita | Total ÷ Population × 10⁶ | World Bank |
| | Per HDI | Total ÷ HDI | UNDP |
| | Per GDP | Total ÷ GDP × 10⁹ | World Bank |
| | Per GDP/Capita | Total ÷ GDP per capita × 10⁴ | World Bank |
| **Geographic (3)** | Per 1000 km² | Total ÷ Land Area × 10³ | World Bank |
| | Per 1000 km Coastline | Total ÷ Coastline × 10³ | CIA World Factbook |
| | Per 100m Elevation | Total ÷ Elevation × 100 | CIA World Factbook |
| **Climate (3)** | Per °C Temperature | Total ÷ \|Avg Temp\| | WB Climate Portal |
| | Per 100 Sunshine Days | Total ÷ Sunshine Days × 100 | National weather services |
| | Per 100 cm Snowfall | Total ÷ Snowfall × 100 | Climate databases |
| **Infrastructure (5)** | Per M Internet Users | Total ÷ Internet Users × 10⁶ | World Bank |
| | Per 1000 Vehicles | Total ÷ Vehicles × 10³ | World Bank |
| | Per University | Total ÷ Universities | UNESCO |
| | Per Stadium | Total ÷ Stadiums | Manually compiled |
| | Per Ski Resort | Total ÷ Ski Resorts | Ski resort databases |
| **Economic (3)** | Per $B Healthcare | Total ÷ Healthcare Spending × 10⁹ | World Bank |
| | Per Year Life Expectancy | Total ÷ Life Expectancy | World Bank |
| | Per 100 Work Hours | Total ÷ Work Hours × 100 | OECD |
| **Cultural (3)** | Per M kg Coffee | Total ÷ Coffee Consumption × 10⁶ | Intl Coffee Org |
| | Per M Cola Servings | Total ÷ Cola Servings × 10⁶ | Consumption data |
| | Per Peace Index Point | Total ÷ GPI Score | Inst. Economics & Peace |
| **Humanitarian (2)** | Per 1000 Refugees Received | Total ÷ Refugees Hosted × 10³ | UNHCR |
| | Per 1000 Refugees Produced | Total ÷ Refugees Originated × 10³ | UNHCR |
| **Military (2)** | Per % GDP Military Spending | Total ÷ Mil. Expenditure % GDP | World Bank / SIPRI |
| | Per 1000 Military Personnel | Total ÷ Active Personnel × 10³ | IISS |

## Data Sources

See [DATA_SOURCES.md](DATA_SOURCES.md) for full provenance, URLs, coverage statistics, and methodological notes.

## Key Methodological Notes

- **Time range**: Analysis focuses on 2000–2024 (modern Olympic era)
- **Country selection**: Minimum 4 Olympic participations and 5 total medals required
- **Trend selection**: Countries ranked by peak (max) performance, not average
- **Snapshot data**: Some metrics (refugees, military, peace index, etc.) are 2023–2024 snapshots applied uniformly across years
- **Historical countries**: USSR, Yugoslavia, etc. mapped to successor states using modern economic data
- **Medal deduplication**: Team events count as one medal per event, not per athlete
