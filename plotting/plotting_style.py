"""
Olympic Data Visualization Style Module

This module provides consistent styling for all Olympic data visualizations.
Import and use these functions to ensure plots follow the project style guide.

Usage:
    from plotting_style import apply_plot_style, MEDAL_COLORS, get_country_color
    
    apply_plot_style()  # Apply once at the start of your script
    fig, ax = setup_figure()
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
from typing import Optional, Tuple

# ============================================================================
# COLOR DEFINITIONS
# ============================================================================

# Medal colors for athlete-level statistics
MEDAL_COLORS = {
    'Gold': '#FFD700',
    'Silver': '#C0C0C0',
    'Bronze': '#CD7F32',
    'Winter': '#1f77b4',  # Blue for winter olympics
    'Summer': '#d62728',  # Red for summer olympics
}

# Country flag colors for medal counts and normalizations
COUNTRY_COLORS = {
    # Major Olympic powers with distinct flag colors
    'USA': '#B22234',           # Red from US flag
    'United States': '#B22234',
    'CHN': '#DE2910',           # Red from Chinese flag
    'China': '#DE2910',
    'RUS': '#0033A0',           # Blue from Russian flag
    'Russia': '#0033A0',
    'ROC': '#0033A0',           # Russian Olympic Committee
    'GER': '#000000',           # Black from German flag
    'Germany': '#000000',
    'GBR': '#012169',           # Blue from UK flag
    'Great Britain': '#012169',
    'FRA': '#0055A4',           # Blue from French flag
    'France': '#0055A4',
    'JPN': '#BC002D',           # Red from Japanese flag
    'Japan': '#BC002D',
    'AUS': '#00843D',           # Green from Australian flag
    'Australia': '#00843D',
    'ITA': '#009246',           # Green from Italian flag
    'Italy': '#009246',
    'CAN': '#FF0000',           # Red from Canadian flag
    'Canada': '#FF0000',
    'KOR': '#003478',           # Blue from South Korean flag
    'South Korea': '#003478',
    'NED': '#FF4F00',           # Orange from Dutch flag
    'Netherlands': '#FF4F00',
    'ESP': '#C60B1E',           # Red from Spanish flag
    'Spain': '#C60B1E',
    'BRA': '#009C3B',           # Green from Brazilian flag
    'Brazil': '#009C3B',
    'NOR': '#BA0C2F',           # Red from Norwegian flag
    'Norway': '#BA0C2F',
    'SWE': '#006AA7',           # Blue from Swedish flag
    'Sweden': '#006AA7',
    'SUI': '#FF0000',           # Red from Swiss flag
    'Switzerland': '#FF0000',
    'AUT': '#ED2939',           # Red from Austrian flag
    'Austria': '#ED2939',
    'HUN': '#436F4D',           # Green from Hungarian flag
    'Hungary': '#436F4D',
    'FIN': '#003580',           # Blue from Finnish flag
    'Finland': '#003580',
    'POL': '#DC143C',           # Red from Polish flag
    'Poland': '#DC143C',
    'DEN': '#C60C30',           # Red from Danish flag
    'Denmark': '#C60C30',
    'BEL': '#000000',           # Black from Belgian flag
    'Belgium': '#000000',
    'GRE': '#0D5EAF',           # Blue from Greek flag
    'Greece': '#0D5EAF',
    'CUB': '#002A8F',           # Blue from Cuban flag
    'Cuba': '#002A8F',
    'KEN': '#006600',           # Green from Kenyan flag
    'Kenya': '#006600',
    'JAM': '#009B3A',           # Green from Jamaican flag
    'Jamaica': '#009B3A',
    'ETH': '#078930',           # Green from Ethiopian flag
    'Ethiopia': '#078930',
    'UKR': '#005BBB',           # Blue from Ukrainian flag
    'Ukraine': '#005BBB',
    'NZL': '#00247D',           # Blue from New Zealand flag
    'New Zealand': '#00247D',
}

# ============================================================================
# MATPLOTLIB STYLE CONFIGURATION
# ============================================================================

def apply_plot_style():
    """
    Apply the standard Olympic plotting style to matplotlib.
    Call this once at the beginning of your script.
    """
    # Set the style parameters
    plt.style.use('default')  # Start with clean slate
    
    # Figure settings
    mpl.rcParams['figure.facecolor'] = 'white'
    mpl.rcParams['figure.edgecolor'] = 'white'
    mpl.rcParams['figure.dpi'] = 100  # Screen display
    mpl.rcParams['savefig.dpi'] = 300  # High res for saving
    mpl.rcParams['savefig.facecolor'] = 'white'
    mpl.rcParams['savefig.edgecolor'] = 'none'
    mpl.rcParams['savefig.bbox'] = 'tight'
    mpl.rcParams['savefig.pad_inches'] = 0.3
    
    # Axes settings
    mpl.rcParams['axes.facecolor'] = 'white'
    mpl.rcParams['axes.edgecolor'] = 'black'
    mpl.rcParams['axes.linewidth'] = 1.0
    mpl.rcParams['axes.grid'] = True
    mpl.rcParams['axes.axisbelow'] = True
    mpl.rcParams['axes.labelcolor'] = 'black'
    mpl.rcParams['axes.labelsize'] = 16
    mpl.rcParams['axes.titlesize'] = 18
    mpl.rcParams['axes.titleweight'] = 'bold'
    
    # Grid settings
    mpl.rcParams['grid.color'] = '#888888'
    mpl.rcParams['grid.linestyle'] = '--'
    mpl.rcParams['grid.linewidth'] = 0.7
    mpl.rcParams['grid.alpha'] = 0.7
    
    # Tick settings
    mpl.rcParams['xtick.color'] = 'black'
    mpl.rcParams['ytick.color'] = 'black'
    mpl.rcParams['xtick.labelsize'] = 13
    mpl.rcParams['ytick.labelsize'] = 13
    mpl.rcParams['xtick.direction'] = 'out'
    mpl.rcParams['ytick.direction'] = 'out'
    mpl.rcParams['xtick.major.width'] = 1.0
    mpl.rcParams['ytick.major.width'] = 1.0
    
    # Font settings
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Liberation Serif', 'Times']
    mpl.rcParams['font.size'] = 13
    
    # Legend settings
    mpl.rcParams['legend.frameon'] = True
    mpl.rcParams['legend.framealpha'] = 1.0
    mpl.rcParams['legend.edgecolor'] = 'black'
    mpl.rcParams['legend.facecolor'] = 'white'
    mpl.rcParams['legend.fontsize'] = 12
    
    # Text settings
    mpl.rcParams['text.color'] = 'black'


def setup_figure(figsize: Tuple[float, float] = (10, 6), 
                 title: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create a properly styled figure and axes.
    
    Args:
        figsize: Figure size as (width, height) in inches
        title: Optional title for the plot
        
    Returns:
        Tuple of (figure, axes)
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    if title:
        ax.set_title(title, pad=20)
    
    return fig, ax


def get_country_color(country_code: str, default_color: str = '#1f77b4') -> str:
    """
    Get the flag-based color for a country.
    
    Args:
        country_code: Country code (e.g., 'USA', 'CHN') or full name
        default_color: Color to return if country not found
        
    Returns:
        Hex color string
    """
    return COUNTRY_COLORS.get(country_code, default_color)


def get_medal_colors(medals: list) -> list:
    """
    Get colors for a list of medal types.
    
    Args:
        medals: List of medal types (e.g., ['Gold', 'Silver', 'Bronze'])
        
    Returns:
        List of color hex strings
    """
    return [MEDAL_COLORS.get(medal, '#808080') for medal in medals]


def save_plot(fig: plt.Figure, filepath: str, dpi: int = 300):
    """
    Save a plot with consistent settings.
    
    Args:
        fig: Matplotlib figure object
        filepath: Path where to save the file
        dpi: Dots per inch (default 300 for high quality)
    """
    from pathlib import Path
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    fig.savefig(filepath, 
                dpi=dpi,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none')
    print(f"✓ Saved: {filepath}")


# ============================================================================
# HELPER FUNCTIONS FOR COMMON PLOT TYPES
# ============================================================================

def style_bar_chart(ax: plt.Axes, 
                    xlabel: Optional[str] = None,
                    ylabel: Optional[str] = None,
                    title: Optional[str] = None):
    """
    Apply consistent styling to a bar chart.
    
    Args:
        ax: Matplotlib axes object
        xlabel: X-axis label
        ylabel: Y-axis label
        title: Plot title
    """
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12)
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    ax.spines['top'].set_visible(True)
    ax.spines['right'].set_visible(True)
    ax.grid(True, alpha=0.5, linestyle='--', linewidth=0.5)


def style_line_chart(ax: plt.Axes,
                     xlabel: Optional[str] = None,
                     ylabel: Optional[str] = None,
                     title: Optional[str] = None):
    """
    Apply consistent styling to a line chart.
    
    Args:
        ax: Matplotlib axes object
        xlabel: X-axis label
        ylabel: Y-axis label
        title: Plot title
    """
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12)
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    ax.spines['top'].set_visible(True)
    ax.spines['right'].set_visible(True)
    ax.grid(True, alpha=0.5, linestyle='--', linewidth=0.5)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Demonstrate the plotting style with example plots.
    """
    import numpy as np
    
    apply_plot_style()
    
    # Example 1: Medal type comparison
    fig1, ax1 = setup_figure(figsize=(8, 6), title="2016 Rio Olympics - USA Medals")
    medals = ['Gold', 'Silver', 'Bronze']
    counts = [46, 37, 38]
    colors = get_medal_colors(medals)
    ax1.bar(medals, counts, color=colors, edgecolor='black', linewidth=1.5)
    style_bar_chart(ax1, ylabel='Number of Medals')
    save_plot(fig1, 'example_medals.png')
    
    # Example 2: Country comparison
    fig2, ax2 = setup_figure(figsize=(12, 6), title="Top 5 Countries - 2016 Rio Olympics")
    countries = ['USA', 'CHN', 'GBR', 'RUS', 'GER']
    totals = [121, 70, 67, 56, 42]
    colors = [get_country_color(c) for c in countries]
    ax2.bar(countries, totals, color=colors, edgecolor='black', linewidth=1.5)
    style_bar_chart(ax2, ylabel='Total Medals')
    save_plot(fig2, 'example_countries.png')
    
    # Example 3: Time series
    fig3, ax3 = setup_figure(figsize=(12, 6), title="USA Olympic Performance Over Time")
    years = np.array([2000, 2004, 2008, 2012, 2016, 2020, 2024])
    totals = [92, 103, 112, 104, 121, 113, 126]
    ax3.plot(years, totals, marker='o', linewidth=2.5, markersize=8,
             color=get_country_color('USA'), label='USA')
    style_line_chart(ax3, xlabel='Year', ylabel='Total Medals')
    ax3.legend()
    save_plot(fig3, 'example_timeseries.png')
    
    print("\n✓ Example plots generated!")
    print("Check the current directory for example_*.png files")
