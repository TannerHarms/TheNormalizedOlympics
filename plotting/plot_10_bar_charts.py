"""
Generate vertical bar charts of RAW normalization metrics by country.

For each metric, creates a single chart showing the raw metric values
(e.g., Population, GDP, Military Spending) — NOT normalized medal counts.
This gives context for how each normalization factor varies across countries.

If a metric has ≤ 30 countries, all are shown.
If > 30, the top 15 and bottom 15 are shown with a visual gap in the middle.

Uses an earth-tone pastel colormap descending from reddish (highest)
to bluish (lowest).  Data details are shown beneath each figure.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from pathlib import Path
import sys
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from plotting.plotting_style import apply_plot_style, save_plot

# Configuration
START_YEAR = 2000
END_YEAR = 2024
MAX_SHOW = 30        # show all bars if ≤ this many countries
TOP_N = 15           # number of top countries when splitting
BOT_N = 15           # number of bottom countries when splitting

DATA_DIR = Path(__file__).parent.parent / 'data'
PLOTS_DIR = Path(__file__).parent.parent / 'plots'

apply_plot_style()

# ============================================================================
# Earth-tone pastel colormap
# ============================================================================
def _earth_cmap():
    return mcolors.LinearSegmentedColormap.from_list('earth_pastel', [
        '#C97B6B', '#D4977A', '#DEB08C', '#DDBE93', '#D3C9A0',
        '#BDC9A3', '#A7C5AB', '#93BEB5', '#83B4BF', '#7BA7C2',
    ], N=256)

EARTH_CMAP = _earth_cmap()

# ============================================================================
# Metric definitions
#   norm_col    → normalised-medal column (used to verify metric exists)
#   raw_col     → raw data column to plot
#   name        → display name for y-axis / title
#   fmt         → Python format spec for bar labels
#   source      → citation text
# ============================================================================
METRICS = [
    {
        'norm_col': 'Medals_Per_Million',
        'raw_col': 'Population',
        'name': 'Population',
        'fmt': ',.0f',
        'source': 'World Bank Open Data (1980-2024)',
    },
    {
        'norm_col': 'Medals_Per_HDI',
        'raw_col': 'HDI',
        'name': 'Human Development Index',
        'fmt': '.3f',
        'source': 'UNDP Human Development Reports (1990-2021)',
    },
    {
        'norm_col': 'Medals_Per_Billion_GDP',
        'raw_col': 'GDP',
        'name': 'GDP (USD)',
        'fmt': ',.0f',
        'source': 'World Bank Open Data (1980-2024)',
    },
    {
        'norm_col': 'Medals_Per_GDP_Per_Capita',
        'raw_col': 'GDP_per_capita',
        'name': 'GDP Per Capita (USD)',
        'fmt': ',.0f',
        'source': 'World Bank Open Data (1980-2024)',
    },
    {
        'norm_col': 'Medals_Per_1000_SqKm',
        'raw_col': 'Land_Area_SqKm',
        'name': 'Land Area (sq km)',
        'fmt': ',.0f',
        'source': 'World Bank Open Data (1980-2024)',
    },
    {
        'norm_col': 'Medals_Per_1000_Km_Coastline',
        'raw_col': 'Coastline_Length_Km',
        'name': 'Coastline Length (km)',
        'fmt': ',.0f',
        'source': 'CIA World Factbook & manually compiled',
        'snapshot': True,
    },
    {
        'norm_col': 'Medals_Per_100m_Elevation',
        'raw_col': 'Average_Elevation_Meters',
        'name': 'Average Elevation (m)',
        'fmt': ',.0f',
        'source': 'CIA World Factbook & Wikipedia',
        'snapshot': True,
    },
    {
        'norm_col': 'Medals_Per_Degree_Temp',
        'raw_col': 'Avg_Temperature_C',
        'name': 'Average Temperature (°C)',
        'fmt': '.1f',
        'source': 'World Bank Climate Knowledge Portal & manually compiled',
        'snapshot': True,
    },
    {
        'norm_col': 'Medals_Per_100_Sunshine_Days',
        'raw_col': 'Sunshine_Days_Per_Year',
        'name': 'Sunshine Days Per Year',
        'fmt': '.0f',
        'source': 'Manually compiled from national weather services',
        'snapshot': True,
    },
    {
        'norm_col': 'Medals_Per_100_Cm_Snowfall',
        'raw_col': 'Avg_Snowfall_Cm_Per_Year',
        'name': 'Average Snowfall (cm/yr)',
        'fmt': '.0f',
        'source': 'Manually compiled from climate data sources',
        'snapshot': True,
    },
    {
        'norm_col': 'Medals_Per_Million_Internet_Users',
        'raw_col': 'Internet_Users_Pct',
        'name': 'Internet Users (% of Population)',
        'fmt': '.1f',
        'source': 'World Bank Open Data (1990-2024)',
    },
    {
        'norm_col': 'Medals_Per_University',
        'raw_col': 'Number_of_Universities',
        'name': 'Number of Universities',
        'fmt': ',.0f',
        'source': 'UNESCO Institute for Statistics & manually compiled (2024)',
    },
    {
        'norm_col': 'Medals_Per_Stadium',
        'raw_col': 'Professional_Sports_Stadiums',
        'name': 'Professional Sports Stadiums',
        'fmt': ',.0f',
        'source': 'Manually compiled from various sources (2024)',
    },
    {
        'norm_col': 'Medals_Per_Ski_Resort',
        'raw_col': 'Number_of_Ski_Resorts',
        'name': 'Number of Ski Resorts',
        'fmt': ',.0f',
        'source': 'Manually compiled from ski resort databases (2024)',
    },
    {
        'norm_col': 'Medals_Per_Pct_Healthcare_Spending',
        'raw_col': 'Healthcare_Spending_Pct_GDP',
        'name': 'Healthcare Spending (% of GDP)',
        'fmt': '.1f',
        'source': 'World Bank Open Data (2000-2024)',
    },
    {
        'norm_col': 'Medals_Per_Pct_Healthcare_Spending',
        'raw_col': 'Healthcare_Spending_USD',
        'name': 'Healthcare Spending (USD)',
        'fmt': ',.0f',
        'source': 'World Bank Open Data (2000-2024)',
    },
    {
        'norm_col': 'Medals_Per_Year_Life_Expectancy',
        'raw_col': 'Life_Expectancy_Years',
        'name': 'Life Expectancy (years)',
        'fmt': '.1f',
        'source': 'World Bank Open Data (1980-2024)',
    },
    {
        'norm_col': 'Medals_Per_100_Work_Hours',
        'raw_col': 'Avg_Work_Hours_Per_Year',
        'name': 'Average Work Hours Per Year',
        'fmt': ',.0f',
        'source': 'OECD Statistics (2000-2023, OECD countries only)',
    },
    {
        'norm_col': 'Medals_Per_Peace_Index_Point',
        'raw_col': 'Global_Peace_Index_Score',
        'name': 'Global Peace Index Score',
        'fmt': '.3f',
        'source': 'Institute for Economics & Peace (2024)',
    },
    {
        'norm_col': 'Medals_Per_Pct_Military_Spending',
        'raw_col': 'Military_Expenditure_Pct_GDP',
        'name': 'Military Expenditure (% of GDP)',
        'fmt': '.2f',
        'source': 'World Bank / SIPRI (2000-2023)',
    },
    {
        'norm_col': 'Medals_Per_Pct_Military_Spending',
        'raw_col': 'Military_Expenditure_USD',
        'name': 'Military Expenditure (USD)',
        'fmt': ',.0f',
        'source': 'World Bank / SIPRI (2000-2023)',
    },
    {
        'norm_col': 'Medals_Per_1000_Military_Personnel',
        'raw_col': 'Active_Military_Personnel_Thousands',
        'name': 'Active Military Personnel (thousands)',
        'fmt': ',.1f',
        'source': 'IISS Military Balance (2024)',
    },
    {
        'norm_col': 'Medals_Per_Pct_Education_Spending',
        'raw_col': 'Education_Spending_pct_GDP',
        'name': 'Education Spending (% of GDP)',
        'fmt': '.2f',
        'source': 'World Bank Open Data (1970-2023)',
    },
    {
        'norm_col': 'Medals_Per_Pct_Education_Spending',
        'raw_col': 'Education_Spending_USD',
        'name': 'Education Spending (USD)',
        'fmt': ',.0f',
        'source': 'World Bank Open Data (1970-2023)',
    },
]


# ============================================================================
# Compact value formatter
# ============================================================================
def _smart_label(val, fmt):
    """Format a value compactly for bar labels."""
    if abs(val) >= 1e12:
        return f'{val / 1e12:.1f}T'
    if abs(val) >= 1e9:
        return f'{val / 1e9:.1f}B'
    if abs(val) >= 1e6:
        return f'{val / 1e6:.1f}M'
    if abs(val) >= 1e4 and ',' in fmt:
        return f'{val / 1e3:.0f}k'
    return f'{val:{fmt}}'


# ============================================================================
# Core chart function
# ============================================================================
def create_metric_bar_chart(df_full, metric):
    """Create a vertical bar chart of one raw metric across countries.

    Picks the year with the best data coverage within [START_YEAR, END_YEAR].
    Returns (n_countries, year_used) or (0, None).
    """
    raw_col = metric['raw_col']
    name = metric['name']
    fmt = metric['fmt']
    source = metric['source']

    if raw_col not in df_full.columns:
        return 0, None

    # ---- filter to valid rows --------------------------------------------
    df = df_full[(df_full['Year'] >= START_YEAR) &
                 (df_full['Year'] <= END_YEAR)].copy()
    df = df.dropna(subset=[raw_col])
    df = df[df[raw_col] != 0]
    df = df[~df[raw_col].isin([float('inf'), float('-inf')])]

    if len(df) == 0:
        return 0, None

    # ---- pick year with best coverage ------------------------------------
    coverage = df.groupby('Year')[raw_col].count()
    best_year = int(coverage.idxmax())

    year_df = (df[df['Year'] == best_year]
               .drop_duplicates(subset='Country', keep='last')
               .sort_values(raw_col, ascending=False)
               .reset_index(drop=True))

    n_total = len(year_df)
    if n_total == 0:
        return 0, None

    # ---- decide: show all  vs  top/bottom with gap -----------------------
    show_gap = n_total > MAX_SHOW
    if show_gap:
        top_df = year_df.head(TOP_N)
        bot_df = year_df.tail(BOT_N)
        n_hidden = n_total - TOP_N - BOT_N
        n_bars = TOP_N + BOT_N + 1      # +1 for the gap spacer
    else:
        top_df = year_df
        bot_df = pd.DataFrame()
        n_hidden = 0
        n_bars = n_total

    # ---- build display arrays --------------------------------------------
    if show_gap:
        countries = (list(top_df['Country'].values)
                     + ['']
                     + list(bot_df['Country'].values))
        values = (list(top_df[raw_col].values)
                  + [0]
                  + list(bot_df[raw_col].values))
        is_gap = [False] * TOP_N + [True] + [False] * BOT_N
    else:
        countries = list(top_df['Country'].values)
        values = list(top_df[raw_col].values)
        is_gap = [False] * n_total

    n_display = len(values)

    # ---- colours (warm top → cool bottom) --------------------------------
    real_vals = [v for v, g in zip(values, is_gap) if not g]
    n_real = len(real_vals)
    norm = plt.Normalize(0, max(n_real - 1, 1))
    bar_colors = []
    rank = 0
    for g in is_gap:
        if g:
            bar_colors.append('none')
        else:
            bar_colors.append(EARTH_CMAP(norm(rank)))
            rank += 1

    # ---- detect heavy tail for log scale ---------------------------------
    real_vals_positive = [v for v in real_vals if v > 0]
    use_log_scale = False
    if len(real_vals_positive) > 5:
        max_val = max(real_vals_positive)
        median_val = np.median(real_vals_positive)
        if median_val > 0 and max_val / median_val > 10:
            use_log_scale = True

    # ---- figure sizing ---------------------------------------------------
    bar_w_in = 0.50                         # inches per bar
    fig_width = max(10, n_bars * bar_w_in + 3.5)
    fig_height = 8.5

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # ---- draw bars -------------------------------------------------------
    bar_w = 0.72
    x_pos = np.arange(n_display)
    for i, (v, c, g) in enumerate(zip(values, bar_colors, is_gap)):
        if g:
            continue
        ax.bar(i, v, width=bar_w, color=c, edgecolor='black', linewidth=1.2)

    # ---- gap annotation --------------------------------------------------
    if show_gap:
        gap_idx = TOP_N
        # Get values on either side of gap
        left_val = values[gap_idx - 1]
        right_val = values[gap_idx + 1]
        
        if use_log_scale and left_val > 0 and right_val > 0:
            # Use geometric mean between the two bars flanking the gap
            y_pos = np.sqrt(left_val * right_val)
        else:
            # Use arithmetic mean of the left value's half-height
            y_pos = left_val * 0.5
        
        # Draw ellipses
        ax.text(gap_idx, y_pos, '...',
                ha='center', va='center', fontsize=36,
                color='#888888', fontweight='bold')

    # ---- value labels above bars -----------------------------------------
    max_val = max(real_vals)
    label_fs = max(13, min(18, int(550 / n_display)))
    for i, (v, g) in enumerate(zip(values, is_gap)):
        if g:
            continue
        if use_log_scale and v > 0:
            label_y = v * 1.15
        else:
            label_y = v + max_val * 0.012
        ax.text(i, label_y, _smart_label(v, fmt),
                ha='center', va='bottom', fontsize=label_fs,
                color='#333333', rotation=90)

    # ---- axes ------------------------------------------------------------
    ax.set_xticks(x_pos)
    tick_fs = max(15, min(20, int(600 / n_display)))
    ax.set_xticklabels(countries, rotation=55, ha='right', fontsize=tick_fs)
    ax.set_xlim(-0.6, n_display - 0.4)
    
    if use_log_scale:
        ax.set_yscale('log')
        ax.set_ylim(bottom=min([v for v in real_vals if v > 0]) * 0.5,
                    top=max(real_vals) * 4.5)  # more headroom for log scale
    else:
        ax.set_ylim(0, max_val * 1.22)         # less headroom for linear scale
    
    ax.set_ylabel(name, fontsize=20)
    ax.tick_params(axis='y', labelsize=16)
    ax.grid(True, axis='y', alpha=0.3, linewidth=0.7)
    ax.grid(False, axis='x')

    # ---- apply tight_layout first to get axes position ------------------
    plt.tight_layout(rect=[0, 0.045, 1, 0.91])
    
    # ---- get left edge of axes for alignment ----------------------------
    ax_bbox = ax.get_position()
    left_edge = ax_bbox.x0
    
    # ---- title (aligned with axes, positioned above figure) -------------
    is_snapshot = metric.get('snapshot', False)
    if is_snapshot:
        fig.suptitle(f'{name} by Country',
                     fontsize=32, weight='bold', x=left_edge, ha='left', y=0.97)
    else:
        fig.suptitle(f'{name} by Country  ({best_year})',
                     fontsize=32, weight='bold', x=left_edge, ha='left', y=0.97)

    # ---- data details (aligned with axes) --------------------------------
    if show_gap:
        if is_snapshot:
            detail = (f'Showing top {TOP_N} and bottom {BOT_N} of '
                      f'{n_total} countries with data ({best_year} shown).  ')
        else:
            detail = (f'Showing top {TOP_N} and bottom {BOT_N} of '
                      f'{n_total} countries with data in {best_year}.  ')
    else:
        if is_snapshot:
            detail = f'{n_total} countries with data ({best_year} shown).  '
        else:
            detail = f'{n_total} countries with data in {best_year}.  '

    fig.text(left_edge, 0.02,
             f'{detail}Data: {source}.',
             ha='left', fontsize=11, style='italic', color='gray')
    
    fig.text(left_edge, 0.01,
             f'Prepared by Tanner D. Harms, {datetime.now().strftime("%B %Y")}',
             ha='left', fontsize=10, style='italic', color='gray')

    slug = (name.lower()
            .replace(' ', '_').replace('(', '').replace(')', '')
            .replace('/', '_').replace('%', 'pct').replace('°', 'deg'))
    
    # Save to dedicated context folder
    context_dir = PLOTS_DIR / 'context'
    context_dir.mkdir(exist_ok=True)
    
    filename = f'context_bar_{slug}.png'
    save_plot(fig, context_dir / filename)
    plt.close(fig)
    return n_total, best_year


# ============================================================================
# Main
# ============================================================================
def main():
    print('Loading dataset...')
    # Summer dataset has more countries; raw metrics are season-independent
    df = pd.read_csv(DATA_DIR / 'summer_olympics_all_metrics.csv')

    total = len(METRICS)
    print(f'\nGenerating context bar charts for {total} metrics...')
    print('=' * 60)

    success = 0
    for i, m in enumerate(METRICS, 1):
        n, yr = create_metric_bar_chart(df, m)
        if n > 0:
            success += 1
            if n <= MAX_SHOW:
                label = f'all {n}'
            else:
                label = f'top {TOP_N} + bottom {BOT_N} of {n}'
            print(f'[{i:2d}/{total}] ✓ {m["name"]:40s}  '
                  f'year={yr}  ({label} countries)')
        else:
            print(f'[{i:2d}/{total}] - {m["name"]:40s}  (no data)')

    print('\n' + '=' * 60)
    print(f'DONE — {success}/{total} context bar charts generated')
    print('=' * 60)


if __name__ == '__main__':
    main()
