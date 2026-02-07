# Normalizing the Olympics

Which countries truly perform best at the Olympics when you account for population, wealth, development, and climate? This project normalizes Olympic medal counts by economic and demographic factors to answer that question.

Covers **Summer Olympics (1896–2024)** and **Winter Olympics (1924–2022)**.

## Project Structure

```
NormalizingTheOlympics/
├── data/
│   ├── raw/                              # Raw Kaggle dataset (athlete_events.csv)
│   ├── summer_olympics_by_year.csv       # Country-year medal counts (Summer)
│   ├── winter_olympics_by_year.csv       # Country-year medal counts (Winter)
│   ├── summer_olympics_with_history.csv  # + cumulative historical metrics
│   ├── winter_olympics_with_history.csv  # + cumulative historical metrics
│   ├── world_bank_data.csv              # Population, GDP, GDP per capita
│   ├── hdi_data.csv                     # Human Development Index
│   ├── climate_data.csv                 # Climate zone classification
│   ├── education_spending.csv           # Education spending (% of GDP)
│   ├── summer_olympics_normalized.csv   # Final merged dataset (Summer)
│   └── winter_olympics_normalized.csv   # Final merged dataset (Winter)
├── scripts/
│   ├── download_kaggle_data.py          # Step 1: Download Kaggle dataset
│   ├── process_kaggle_data.py           # Step 2: Aggregate to country-year totals
│   ├── add_recent_olympics.py           # Step 3: Scrape Wikipedia for 2018–2024
│   ├── fix_country_names.py             # Step 4: Convert full names → NOC codes
│   ├── collect_world_bank_data.py       # Step 5: Fetch World Bank indicators
│   ├── collect_hdi_data.py              # Step 6: Fetch UNDP HDI data
│   ├── collect_climate_data.py          # Step 7: Climate zone classification
│   ├── collect_education_spending.py    # Step 8: Education spending data
│   ├── country_mapping.py              # NOC ↔ World Bank code mapping
│   ├── calculate_historical_medals.py   # Step 9: Cumulative medal histories
│   ├── merge_all_data.py               # Step 10: Merge all data + normalize
│   ├── create_analysis_plots.py         # Step 11: Generate quick analysis plots
│   └── plotting_style.py               # Shared matplotlib styling (legacy)
├── plotting/                            # Individual plotting scripts
│   ├── plotting_style.py               # Shared matplotlib styling
│   ├── plot_01_top_countries_cumulative.py
│   ├── plot_02_per_capita_top_bottom.py
│   ├── plot_03_per_HDI_top_bottom.py
│   ├── plot_04_per_GDP_top_bottom.py
│   └── README.md                        # Plotting documentation
├── plots/                               # Generated visualizations
├── tests/                               # Test suite
├── DATA_SOURCES.md                      # Data provenance documentation
└── requirements.txt                     # Python dependencies
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Data Pipeline

Run scripts in order. Steps 1–8 collect data (require internet access); steps 9–11 process locally.

```bash
# Collect Olympic data
python scripts/download_kaggle_data.py         # Kaggle API credentials required
python scripts/process_kaggle_data.py
python scripts/add_recent_olympics.py
python scripts/fix_country_names.py

# Collect normalization data
python scripts/collect_world_bank_data.py
python scripts/collect_hdi_data.py
python scripts/collect_climate_data.py
python scripts/collect_education_spending.py

# Process and analyze
python scripts/calculate_historical_medals.py
python scripts/merge_all_data.py
python scripts/create_analysis_plots.py
```

## Normalization Metrics

Each country-year record includes these normalized measures:

| Metric | Formula | Purpose |
|--------|---------|---------|
| Medals per million population | Total ÷ Population × 10⁶ | Size-adjusted performance |
| Medals per billion USD GDP | Total ÷ GDP × 10⁹ | Wealth-adjusted performance |
| Medals per $10K GDP/capita | Total ÷ GDP per capita × 10⁴ | Development-adjusted performance |
| Medals per HDI point | Total ÷ HDI | Human development efficiency |

Gold medal variants of each metric are also calculated.

## Data Sources

See [DATA_SOURCES.md](DATA_SOURCES.md) for full provenance, URLs, and coverage statistics.

- **Olympic medals**: Kaggle (1896–2016) + Wikipedia (2018–2024)
- **Population & GDP**: World Bank Open Data API (1960–2024)
- **HDI**: UNDP Human Development Reports (1990–2021)
- **Climate zones**: Manual classification by geography (183 countries)
- **Education spending**: World Bank indicator SE.XPD.TOTL.GD.ZS

## Analysis Plots

1. **Absolute vs Per Capita Rankings** — How rankings shift when adjusting for population
2. **GDP Efficiency** — Which countries win the most medals relative to their economy
3. **Climate vs Winter Sports** — How geography predicts Winter Olympics success
4. **Population vs Medals** — The (weak) correlation between population size and medals
5. **USA vs China Trends** — Superpower medal competition over time
6. **Historical vs Current** — Does Olympic tradition predict current performance?
