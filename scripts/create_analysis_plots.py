"""
Generate comprehensive Olympic normalization analysis plots.

This script creates visualizations comparing:
1. Absolute vs normalized medal rankings
2. Time-series trends
3. Efficiency analysis (medals per resource unit)
4. Climate vs winter sports performance
5. Historical success vs current performance
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from scripts.plotting_style import apply_plot_style, save_plot, MEDAL_COLORS, get_country_color

# Apply consistent plot styling
apply_plot_style()

# Load data
data_dir = Path(__file__).parent.parent / 'data'
plots_dir = Path(__file__).parent.parent / 'plots'

print("Loading normalized Olympic data...")
summer = pd.read_csv(data_dir / 'summer_olympics_normalized.csv')
winter = pd.read_csv(data_dir / 'winter_olympics_normalized.csv')

print(f"Summer: {len(summer)} records")
print(f"Winter: {len(winter)} records")
print()

# Get most recent year
summer_recent = summer[summer['Year'] == summer['Year'].max()].copy()
winter_recent = winter[winter['Year'] == winter['Year'].max()].copy()

print(f"Most recent Summer Olympics: {summer['Year'].max()}")
print(f"Most recent Winter Olympics: {winter['Year'].max()}")
print()

# === PLOT 1: Absolute vs Per Capita Rankings (Summer) ===
print("Creating Plot 1: Absolute vs Per Capita Rankings (Summer)...")

# Top 15 by absolute medals
top_absolute = summer_recent.nlargest(15, 'Total').copy()

# Top 15 by per capita (must have medals)
top_per_capita = summer_recent[summer_recent['Total'] > 0].nlargest(15, 'Medals_per_million_pop').copy()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# Absolute medals
countries = top_absolute['Country'].tolist()
medals = top_absolute['Total'].tolist()
colors = [get_country_color(c) for c in countries]

ax1.barh(range(len(countries)), medals, color=colors)
ax1.set_yticks(range(len(countries)))
ax1.set_yticklabels(countries)
ax1.set_xlabel('Total Medals')
ax1.set_title(f'Top 15 Countries by Absolute Medals\n{summer["Year"].max()} Summer Olympics')
ax1.invert_yaxis()
ax1.grid(axis='x', alpha=0.3)

# Per capita medals
countries_pc = top_per_capita['Country'].tolist()
medals_pc = top_per_capita['Medals_per_million_pop'].tolist()
colors_pc = [get_country_color(c) for c in countries_pc]

ax2.barh(range(len(countries_pc)), medals_pc, color=colors_pc)
ax2.set_yticks(range(len(countries_pc)))
ax2.set_yticklabels(countries_pc)
ax2.set_xlabel('Medals per Million Population')
ax2.set_title(f'Top 15 Countries by Medals per Capita\n{summer["Year"].max()} Summer Olympics')
ax2.invert_yaxis()
ax2.grid(axis='x', alpha=0.3)

# Style already applied globally
save_plot(fig, plots_dir / 'summer_absolute_vs_percapita.png')
plt.close()

print("  ✓ Saved summer_absolute_vs_percapita.png")
print()

# === PLOT 2: GDP Efficiency (Summer) ===
print("Creating Plot 2: GDP Efficiency (Summer)...")

# Top 15 by medals per billion GDP (must have medals and GDP data)
top_gdp_eff = summer_recent[
    (summer_recent['Total'] > 0) & 
    (summer_recent['Medals_per_billion_GDP'].notna())
].nlargest(15, 'Medals_per_billion_GDP').copy()

fig, ax = plt.subplots(figsize=(12, 8))

countries = top_gdp_eff['Country'].tolist()
efficiency = top_gdp_eff['Medals_per_billion_GDP'].tolist()
colors = [get_country_color(c) for c in countries]

ax.barh(range(len(countries)), efficiency, color=colors)
ax.set_yticks(range(len(countries)))
ax.set_yticklabels(countries)
ax.set_xlabel('Medals per Billion USD GDP')
ax.set_title(f'Most GDP-Efficient Olympic Nations\n{summer["Year"].max()} Summer Olympics')
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

# Style already applied globally
save_plot(fig, plots_dir / 'summer_gdp_efficiency.png')
plt.close()

print("  ✓ Saved summer_gdp_efficiency.png")
print()

# === PLOT 3: Climate vs Winter Sports Performance ===
print("Creating Plot 3: Climate vs Winter Sports Performance...")

# Average medals by climate zone (Winter Olympics)
winter_by_climate = winter_recent.groupby('Climate_Description').agg({
    'Total': 'sum',
    'Country': 'count'
}).reset_index()
winter_by_climate.columns = ['Climate_Zone', 'Total_Medals', 'Country_Count']
winter_by_climate['Avg_Medals_per_Country'] = winter_by_climate['Total_Medals'] / winter_by_climate['Country_Count']
winter_by_climate = winter_by_climate.sort_values('Avg_Medals_per_Country', ascending=False)

fig, ax = plt.subplots(figsize=(12, 6))

zones = winter_by_climate['Climate_Zone'].tolist()
avg_medals = winter_by_climate['Avg_Medals_per_Country'].tolist()

ax.bar(range(len(zones)), avg_medals, color='#4682B4', edgecolor='black', linewidth=1.5)
ax.set_xticks(range(len(zones)))
ax.set_xticklabels(zones, rotation=45, ha='right')
ax.set_ylabel('Average Medals per Country')
ax.set_title(f'Winter Olympics Performance by Climate Zone\n{winter["Year"].max()} Winter Olympics')
ax.grid(axis='y', alpha=0.3)

# Style already applied globally
save_plot(fig, plots_dir / 'winter_climate_performance.png')
plt.close()

print("  ✓ Saved winter_climate_performance.png")
print()

# === PLOT 4: Population vs Medals (Scatter) ===
print("Creating Plot 4: Population vs Medals Scatter...")

# Filter to countries with data
summer_scatter = summer_recent[
    (summer_recent['Population'].notna()) & 
    (summer_recent['Total'] > 0)
].copy()

fig, ax = plt.subplots(figsize=(12, 8))

# Create scatter plot
x = summer_scatter['Population'] / 1_000_000  # Convert to millions
y = summer_scatter['Total']

# Color by region would be nice, but we'll use medal count
colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(x)))

ax.scatter(x, y, s=100, alpha=0.6, c=colors, edgecolors='black', linewidth=0.5)

# Label top performers
top_5 = summer_scatter.nlargest(5, 'Total')
for _, row in top_5.iterrows():
    ax.annotate(
        row['Country'],
        xy=(row['Population'] / 1_000_000, row['Total']),
        xytext=(5, 5),
        textcoords='offset points',
        fontsize=10,
        fontweight='bold'
    )

ax.set_xlabel('Population (Millions)')
ax.set_ylabel('Total Medals')
ax.set_title(f'Population vs Medal Count\n{summer["Year"].max()} Summer Olympics')
ax.set_xscale('log')
ax.grid(True, alpha=0.3)

# Style already applied globally
save_plot(fig, plots_dir / 'summer_population_vs_medals.png')
plt.close()

print("  ✓ Saved summer_population_vs_medals.png")
print()

# === PLOT 5: USA vs China Over Time ===
print("Creating Plot 5: USA vs China Medal Trends...")

# Get USA and China data over time
usa_summer = summer[summer['Country'] == 'USA'].sort_values('Year')
chn_summer = summer[summer['Country'] == 'CHN'].sort_values('Year')

fig, ax = plt.subplots(figsize=(14, 7))

ax.plot(usa_summer['Year'], usa_summer['Total'], 
        marker='o', linewidth=2.5, label='USA', color=get_country_color('USA'))
ax.plot(chn_summer['Year'], chn_summer['Total'], 
        marker='s', linewidth=2.5, label='China', color=get_country_color('CHN'))

ax.set_xlabel('Year')
ax.set_ylabel('Total Medals')
ax.set_title('USA vs China: Summer Olympics Medal Count Over Time')
ax.legend(loc='best', fontsize=12)
ax.grid(True, alpha=0.3)

# Style already applied globally
save_plot(fig, plots_dir / 'usa_vs_china_trend.png')
plt.close()

print("  ✓ Saved usa_vs_china_trend.png")
print()

# === PLOT 6: Historical Success vs Current Performance ===
print("Creating Plot 6: Historical Success vs Current Performance...")

# Filter to countries with historical data
summer_hist = summer_recent[
    (summer_recent['Historical_Total'] > 0) &
    (summer_recent['Total'] > 0)
].copy()

if len(summer_hist) == 0:
    print("  ⚠ No data for historical analysis")
    print()
else:
    fig, ax = plt.subplots(figsize=(12, 8))

    x = summer_hist['Historical_Total'].values
    y = summer_hist['Total'].values

    # Color by whether they over/under-performed relative to trend
    if len(x) > 1:
        z_color = np.polyfit(x, y, 1)
        predicted = np.poly1d(z_color)(x)
        colors = ['#2E8B57' if actual >= pred else '#DC143C' for actual, pred in zip(y, predicted)]
    else:
        colors = ['#2E8B57'] * len(x)

    ax.scatter(x, y, s=100, alpha=0.6, c=colors, edgecolors='black', linewidth=0.5)

    # Add trend line if we have enough data
    if len(x) > 1:
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        ax.plot(x, p(x), "r--", alpha=0.8, linewidth=2, label=f'Trend: y={z[0]:.4f}x+{z[1]:.1f}')

    # Label some interesting countries
    interesting = summer_hist[
        ((summer_hist['Total'] / summer_hist['Historical_Total'] > 0.05) |
         (summer_hist['Total'] > 50))
    ].nlargest(8, 'Total')

    for _, row in interesting.iterrows():
        ax.annotate(
            row['Country'],
            xy=(row['Historical_Total'], row['Total']),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=9
        )

    ax.set_xlabel('Historical Medal Count (All-time before this Olympics)')
    ax.set_ylabel(f'Current Medal Count ({summer["Year"].max()})')
    ax.set_title('Does Olympic Tradition Predict Performance?')
    if len(x) > 1:
        ax.legend()
    ax.grid(True, alpha=0.3)

    # Style already applied globally
    save_plot(fig, plots_dir / 'historical_vs_current.png')
    plt.close()

    print("  ✓ Saved historical_vs_current.png")
    print()

print("=" * 70)
print("✓ ALL PLOTS CREATED SUCCESSFULLY!")
print("=" * 70)
print()
print(f"Plots saved to: {plots_dir}")
print()
print("Generated plots:")
print("  1. summer_absolute_vs_percapita.png - Rankings comparison")
print("  2. summer_gdp_efficiency.png - Most economically efficient")
print("  3. winter_climate_performance.png - Climate impact")
print("  4. summer_population_vs_medals.png - Population correlation")
print("  5. usa_vs_china_trend.png - Superpower competition")
print("  6. historical_vs_current.png - Tradition vs performance")
print()
