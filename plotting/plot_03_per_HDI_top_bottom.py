"""
Plot medals normalized by HDI (Human Development Index) for medal-winning countries.

Shows:
- Top 10 countries by medals per HDI point
- Bottom 10 countries by medals per HDI point

Separate plots for Summer and Winter Olympics (most recent games).
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from plotting.plotting_style import apply_plot_style, save_plot, get_country_color

# Configuration
TOP_N = 10  # Top and bottom N countries to show

# Paths
DATA_DIR = Path(__file__).parent.parent / 'data'
PLOTS_DIR = Path(__file__).parent.parent / 'plots'

# Apply styling
apply_plot_style()


def plot_normalized_medals(df, metric_col, metric_name, season, year, top_n=10):
    """
    Create plots showing top and bottom N countries by a normalized metric.
    
    Returns: (fig_top, fig_bottom)
    """
    # Filter to most recent year with medals and HDI data
    recent = df[df['Year'] == year].copy()
    recent = recent[recent['Total'] > 0]  # Only medal winners
    recent = recent[recent[metric_col].notna()]  # Only with HDI data
    
    if len(recent) == 0:
        print(f"  ⚠ No data for {season} {year}")
        return None, None
    
    # Sort by metric
    recent_sorted = recent.sort_values(metric_col, ascending=False)
    
    # Top N
    top = recent_sorted.head(top_n)
    
    # Bottom N (reverse order for display)
    bottom = recent_sorted.tail(top_n).iloc[::-1]
    
    # === TOP N PLOT ===
    fig_top, ax_top = plt.subplots(figsize=(12, 8))
    
    countries_top = top['Country'].tolist()
    values_top = top[metric_col].values
    colors_top = [get_country_color(c) for c in countries_top]
    
    y_pos = np.arange(len(countries_top))
    ax_top.barh(y_pos, values_top, color=colors_top, edgecolor='black', linewidth=1)
    ax_top.set_yticks(y_pos)
    ax_top.set_yticklabels(countries_top, fontsize=11)
    ax_top.set_xlabel(metric_name, fontsize=12, fontweight='bold')
    ax_top.set_title(
        f'Top {top_n} Countries by {metric_name}\n{season} Olympics {year}',
        fontsize=14,
        fontweight='bold',
        pad=20
    )
    ax_top.invert_yaxis()
    
    # Add values at end of bars
    for i, (val, total, hdi) in enumerate(zip(values_top, top['Total'].values, top['HDI'].values)):
        ax_top.text(val + val*0.02, i, f'{val:.1f} ({int(total)} medals, HDI={hdi:.3f})', 
                   va='center', fontsize=9)
    
    ax_top.grid(axis='x', alpha=0.3, linestyle='--')
    ax_top.set_axisbelow(True)
    
    # === BOTTOM N PLOT ===
    fig_bottom, ax_bottom = plt.subplots(figsize=(12, 8))
    
    countries_bottom = bottom['Country'].tolist()
    values_bottom = bottom[metric_col].values
    colors_bottom = [get_country_color(c, '#999999') for c in countries_bottom]
    
    y_pos = np.arange(len(countries_bottom))
    ax_bottom.barh(y_pos, values_bottom, color=colors_bottom, edgecolor='black', linewidth=1)
    ax_bottom.set_yticks(y_pos)
    ax_bottom.set_yticklabels(countries_bottom, fontsize=11)
    ax_bottom.set_xlabel(metric_name, fontsize=12, fontweight='bold')
    ax_bottom.set_title(
        f'Bottom {top_n} Medal Winners by {metric_name}\n{season} Olympics {year}',
        fontsize=14,
        fontweight='bold',
        pad=20
    )
    ax_bottom.invert_yaxis()
    
    # Add values at end of bars
    for i, (val, total, hdi) in enumerate(zip(values_bottom, bottom['Total'].values, bottom['HDI'].values)):
        ax_bottom.text(val + val*0.02, i, f'{val:.1f} ({int(total)} medals, HDI={hdi:.3f})', 
                      va='center', fontsize=9)
    
    ax_bottom.grid(axis='x', alpha=0.3, linestyle='--')
    ax_bottom.set_axisbelow(True)
    
    return fig_top, fig_bottom


def main():
    print("="*70)
    print("HDI-NORMALIZED MEDALS: TOP & BOTTOM PERFORMERS")
    print("="*70)
    print()
    
    # Load normalized data
    summer = pd.read_csv(DATA_DIR / 'summer_olympics_normalized.csv')
    winter = pd.read_csv(DATA_DIR / 'winter_olympics_normalized.csv')
    
    # Get most recent years
    summer_year = summer['Year'].max()
    winter_year = winter['Year'].max()
    
    # ===== SUMMER: PER HDI =====
    print(f"Summer {summer_year}: Medals per HDI point")
    medal_winners = summer[(summer.Year==summer_year) & (summer.Total > 0)]
    with_hdi = medal_winners[medal_winners.Medals_per_HDI.notna()]
    print(f"  Medal winners: {len(medal_winners)}")
    print(f"  With HDI data: {len(with_hdi)} ({100*len(with_hdi)/len(medal_winners):.0f}%)")
    
    fig_top, fig_bottom = plot_normalized_medals(
        summer, 
        'Medals_per_HDI',
        'Medals per HDI Point',
        'Summer',
        summer_year,
        TOP_N
    )
    
    if fig_top:
        save_plot(fig_top, PLOTS_DIR / f'summer_{summer_year}_per_HDI_TOP_{TOP_N}.png')
        plt.close(fig_top)
        print(f"  ✓ Saved: summer_{summer_year}_per_HDI_TOP_{TOP_N}.png")
    
    if fig_bottom:
        save_plot(fig_bottom, PLOTS_DIR / f'summer_{summer_year}_per_HDI_BOTTOM_{TOP_N}.png')
        plt.close(fig_bottom)
        print(f"  ✓ Saved: summer_{summer_year}_per_HDI_BOTTOM_{TOP_N}.png")
    
    print()
    
    # ===== WINTER: PER HDI =====
    print(f"Winter {winter_year}: Medals per HDI point")
    medal_winners = winter[(winter.Year==winter_year) & (winter.Total > 0)]
    with_hdi = medal_winners[medal_winners.Medals_per_HDI.notna()]
    print(f"  Medal winners: {len(medal_winners)}")
    print(f"  With HDI data: {len(with_hdi)} ({100*len(with_hdi)/len(medal_winners):.0f}%)")
    
    fig_top, fig_bottom = plot_normalized_medals(
        winter, 
        'Medals_per_HDI',
        'Medals per HDI Point',
        'Winter',
        winter_year,
        TOP_N
    )
    
    if fig_top:
        save_plot(fig_top, PLOTS_DIR / f'winter_{winter_year}_per_HDI_TOP_{TOP_N}.png')
        plt.close(fig_top)
        print(f"  ✓ Saved: winter_{winter_year}_per_HDI_TOP_{TOP_N}.png")
    
    if fig_bottom:
        save_plot(fig_bottom, PLOTS_DIR / f'winter_{winter_year}_per_HDI_BOTTOM_{TOP_N}.png')
        plt.close(fig_bottom)
        print(f"  ✓ Saved: winter_{winter_year}_per_HDI_BOTTOM_{TOP_N}.png")
    
    print()
    print("="*70)
    print("✓ PLOTS CREATED")
    print("="*70)


if __name__ == '__main__':
    main()
