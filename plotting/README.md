# Plotting Scripts

Each script creates a specific set of visualizations. Run them individually to generate plots.

## Configuration

Edit the constants at the top of each script to customize:
- `N_OLYMPICS` — Number of recent Olympics to analyze
- `TOP_N` or `TOP_N_COUNTRIES` — Number of countries to show

## Scripts

### `plot_01_top_countries_cumulative.py`
Cumulative medals (Gold, Silver, Bronze stacked) for top 15 countries over last 10 Olympics.

**Generates:**
- `top_15_cumulative_summer_last_10.png`
- `top_15_cumulative_winter_last_10.png`

**Run:** `python plotting/plot_01_top_countries_cumulative.py`

---

### `plot_02_per_capita_trends.py`
Line plots showing medals per million population over time for top-performing countries.

**Generates:**
- `summer_per_capita_trends_top_10.png`
- `winter_per_capita_trends_top_10.png`

**Run:** `python plotting/plot_02_per_capita_trends.py`

---

### `plot_03_per_HDI_trends.py`
Line plots showing medals per HDI point over time for top-performing countries.

**Generates:**
- `summer_per_HDI_trends_top_10.png`
- `winter_per_HDI_trends_top_10.png`

**Run:** `python plotting/plot_03_per_HDI_trends.py`

---

### `plot_04_per_GDP_trends.py`
Line plots showing medals per billion USD GDP over time for top-performing countries.

**Generates:**
- `summer_per_GDP_trends_top_10.png`
- `winter_per_GDP_trends_top_10.png`

**Run:** `python plotting/plot_04_per_GDP_trends.py`

---

### `plot_05_medals_growth_trends.py`
Line plots showing medal counts normalized by each country's previous Olympics performance. Reveals which countries are consistently improving or declining relative to their own baseline.

**Generates:**
- `summer_medals_growth_trends_top_10.png`
- `winter_medals_growth_trends_top_10.png`

**Configuration:**
- `MIN_MEDALS = 5` - Minimum medals in previous Olympics to be included

**Run:** `python plotting/plot_05_medals_growth_trends.py`

---

### Legacy Bar Charts (Single Olympics)

These scripts show top/bottom performers for the most recent Olympics:
- `plot_02_per_capita_top_bottom.py` - Per capita bar charts
- `plot_03_per_HDI_top_bottom.py` - Per HDI bar charts  
- `plot_04_per_GDP_top_bottom.py` - Per GDP bar charts

---

## Adding New Plots

1. Copy one of the existing scripts as a template
2. Number it sequentially (e.g., `plot_05_...`)
3. Modify the plotting functions for your specific visualization
4. Update this README with the new script's details

## Notes

- All plots are saved to the `plots/` directory
- The `plotting_style.py` module provides consistent styling
- Scripts are designed to be run independently or as part of a batch
- Trend plots (02-04) show performance evolution over the last N Olympics
- Legacy top/bottom scripts show single-Olympics snapshots
