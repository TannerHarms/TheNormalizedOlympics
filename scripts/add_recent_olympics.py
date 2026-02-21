"""
Add recent Olympics data (2018, 2020, 2022, 2024) to the existing dataset
Maintains the same format as the Kaggle data
"""

import pandas as pd
from pathlib import Path
import time
import requests
from io import StringIO

DATA_DIR = Path(__file__).parent.parent / "data"

# Setup headers to avoid 403 errors
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Recent Olympics to add
RECENT_OLYMPICS = {
    'summer': {
        2020: "2020_Summer_Olympics_medal_table",  # Held in 2021
        2024: "2024_Summer_Olympics_medal_table",
    },
    'winter': {
        2018: "2018_Winter_Olympics_medal_table",
        2022: "2022_Winter_Olympics_medal_table",
    }
}

# Country name → NOC code mapping for Wikipedia medal tables
COUNTRY_NAME_TO_NOC = {
    'United States': 'USA', 'China': 'CHN', 'Great Britain': 'GBR',
    'Japan': 'JPN', 'France': 'FRA', 'Italy': 'ITA', 'Australia': 'AUS',
    'Canada': 'CAN', 'South Korea': 'KOR', 'Netherlands': 'NED',
    'Spain': 'ESP', 'Brazil': 'BRA', 'Russia': 'RUS', 'ROC': 'ROC',
    'Germany': 'GER', 'New Zealand': 'NZL', 'Switzerland': 'SUI',
    'Sweden': 'SWE', 'Norway': 'NOR', 'Denmark': 'DEN', 'Finland': 'FIN',
    'Belgium': 'BEL', 'Poland': 'POL', 'Ukraine': 'UKR',
    'Czech Republic': 'CZE', 'Czechia': 'CZE', 'Austria': 'AUT',
    'Hungary': 'HUN', 'Mexico': 'MEX', 'Argentina': 'ARG',
    'South Africa': 'RSA', 'India': 'IND', 'Portugal': 'POR',
    'Greece': 'GRE', 'Turkey': 'TUR', 'Ireland': 'IRL',
    'Türkiye': 'TUR', 'Egypt': 'EGY', 'Jamaica': 'JAM',
    'Kenya': 'KEN', 'Ethiopia': 'ETH', 'Cuba': 'CUB',
    'Nigeria': 'NGR', 'Algeria': 'ALG', 'Morocco': 'MAR',
    'Tunisia': 'TUN', 'Colombia': 'COL', 'Chile': 'CHI',
    'Venezuela': 'VEN', 'Peru': 'PER', 'Ecuador': 'ECU',
    'Uruguay': 'URU', 'Pakistan': 'PAK', 'Thailand': 'THA',
    'Malaysia': 'MAS', 'Singapore': 'SGP', 'Indonesia': 'INA',
    'Philippines': 'PHI', 'Vietnam': 'VIE', 'Israel': 'ISR',
    'Iraq': 'IRQ', 'Iran': 'IRI', 'Saudi Arabia': 'KSA',
    'United Arab Emirates': 'UAE', 'Kuwait': 'KUW', 'Qatar': 'QAT',
    'Bahamas': 'BAH', 'Bahrain': 'BRN', 'Jordan': 'JOR',
    'Chinese Taipei': 'TPE', 'Hong Kong': 'HKG', 'Lebanon': 'LEB',
    'Syria': 'SYR', 'North Korea': 'PRK', 'Mongolia': 'MGL',
    'Kazakhstan': 'KAZ', 'Uzbekistan': 'UZB', 'Turkmenistan': 'TKM',
    'Kyrgyzstan': 'KGZ', 'Tajikistan': 'TJK', 'Afghanistan': 'AFG',
    'Bangladesh': 'BAN', 'Sri Lanka': 'SRI', 'Nepal': 'NEP',
    'Myanmar': 'MYA', 'Cambodia': 'CAM', 'Brunei': 'BRU',
    'Timor-Leste': 'TLS', 'Slovenia': 'SLO', 'Croatia': 'CRO',
    'Serbia': 'SRB', 'Bosnia and Herzegovina': 'BIH',
    'North Macedonia': 'MKD', 'Montenegro': 'MNE', 'Albania': 'ALB',
    'Kosovo': 'KOS', 'Bulgaria': 'BUL', 'Romania': 'ROU',
    'Moldova': 'MDA', 'Georgia': 'GEO', 'Armenia': 'ARM',
    'Azerbaijan': 'AZE', 'Belarus': 'BLR', 'Lithuania': 'LTU',
    'Latvia': 'LAT', 'Estonia': 'EST', 'Slovakia': 'SVK',
    'Iceland': 'ISL', 'Luxembourg': 'LUX', 'Malta': 'MLT',
    'Cyprus': 'CYP', 'Andorra': 'AND', 'Monaco': 'MON',
    'Liechtenstein': 'LIE', 'San Marino': 'SMR',
    'Trinidad and Tobago': 'TRI', 'Barbados': 'BAR',
    'Dominican Republic': 'DOM', 'Haiti': 'HAI', 'Puerto Rico': 'PUR',
    'Ghana': 'GHA', 'Zimbabwe': 'ZIM', 'Uganda': 'UGA',
    'Botswana': 'BOT', 'Namibia': 'NAM', 'Tanzania': 'TAN',
    'Zambia': 'ZAM', 'Senegal': 'SEN', 'Ivory Coast': 'CIV',
    "Côte d'Ivoire": 'CIV', 'Cameroon': 'CMR',
    'Burkina Faso': 'BUR', 'Mali': 'MLI', 'Niger': 'NIG',
    'Togo': 'TOG', 'Benin': 'BEN', 'Gabon': 'GAB',
    'Republic of the Congo': 'CGO', 'Congo': 'COD',
    'Angola': 'ANG', 'Mozambique': 'MOZ', 'Madagascar': 'MAD',
    'Mauritius': 'MRI', 'Seychelles': 'SEY',
    'Fiji': 'FIJ', 'Samoa': 'SAM', 'Tonga': 'TGA',
    'Papua New Guinea': 'PNG', 'Jamaica': 'JAM',
    'Bolivia': 'BOL', 'Paraguay': 'PAR', 'Guyana': 'GUY',
    'Suriname': 'SUR', 'Guatemala': 'GUA', 'Honduras': 'HON',
    'Nicaragua': 'NCA', 'Costa Rica': 'CRC', 'Panama': 'PAN',
    'El Salvador': 'ESA', 'Belize': 'BIZ',
    'Grenada': 'GRN', 'Dominica': 'DMA', 'Saint Lucia': 'LCA',
    'Bermuda': 'BER', 'Burundi': 'BDI',
    'Central African Republic': 'CAF', 'Chad': 'CHA',
    'Comoros': 'COM', 'Cape Verde': 'CPV', 'Cabo Verde': 'CPV',
    'Gambia': 'GAM', 'Guinea-Bissau': 'GBS',
    'Equatorial Guinea': 'GEQ', 'Guinea': 'GUI',
    'Lesotho': 'LES', 'Malawi': 'MAW', 'Mauritania': 'MTN',
    'Rwanda': 'RWA', 'Sierra Leone': 'SLE',
    'Eswatini': 'SWZ', 'Swaziland': 'SWZ',
    'Liberia': 'LBR', 'Libya': 'LBA', 'Sudan': 'SUD',
    'South Sudan': 'SSD', 'Eritrea': 'ERI', 'Djibouti': 'DJI',
    'Somalia': 'SOM', 'Yemen': 'YEM', 'Oman': 'OMA',
    'Maldives': 'MDV', 'Palestine': 'PLE',
    'Olympic Athletes from Russia': 'OAR',
    'Individual Neutral Athletes': 'AIN',
    'Refugee Olympic Team': 'EOR',
}

def fetch_medal_table(year, wiki_page):
    """Fetch medal table from Wikipedia for a specific Olympics"""
    url = f"https://en.wikipedia.org/wiki/{wiki_page}"
    
    try:
        print(f"  Fetching {year}...", end=" ", flush=True)
        
        # Fetch page with headers
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        # Read all tables from the page
        tables = pd.read_html(StringIO(response.text))
        
        # Find the main medal table
        for table in tables:
            # Check if this looks like a medal table
            cols_str = str(table.columns).lower()
            if 'gold' in cols_str and 'silver' in cols_str and 'bronze' in cols_str:
                if len(table) >= 20:  # Main medal table should have many countries
                    df = table.copy()
                    
                    # Flatten multi-level columns if needed
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = [' '.join(str(c).strip() for c in col if str(c).strip() != 'nan') 
                                     for col in df.columns]
                    
                    # Find the relevant columns
                    # Country column
                    country_col = None
                    for col in df.columns:
                        col_lower = str(col).lower()
                        if any(x in col_lower for x in ['noc', 'nation', 'team', 'country']):
                            country_col = col
                            break
                    
                    if country_col is None:
                        country_col = df.columns[0]
                    
                    # Medal columns
                    gold_col = [c for c in df.columns if 'gold' in str(c).lower()][0]
                    silver_col = [c for c in df.columns if 'silver' in str(c).lower()][0]
                    bronze_col = [c for c in df.columns if 'bronze' in str(c).lower()][0]
                    total_cols = [c for c in df.columns if 'total' in str(c).lower()]
                    total_col = total_cols[0] if total_cols else None
                    
                    # Create result dataframe with proper structure
                    result = pd.DataFrame({
                        'Year': year,
                        'Country': df[country_col].astype(str),
                        'Gold': pd.to_numeric(df[gold_col], errors='coerce').fillna(0),
                        'Silver': pd.to_numeric(df[silver_col], errors='coerce').fillna(0),
                        'Bronze': pd.to_numeric(df[bronze_col], errors='coerce').fillna(0),
                    })
                    
                    if total_col:
                        result['Total'] = pd.to_numeric(df[total_col], errors='coerce').fillna(0)
                    else:
                        result['Total'] = result['Gold'] + result['Silver'] + result['Bronze']
                    
                    # Clean country names (remove footnotes, special characters, unicode issues)
                    result['Country'] = result['Country'].str.replace(r'\s*\[.*?\]', '', regex=True)
                    result['Country'] = result['Country'].str.replace(r'\s*\(.*?\)', '', regex=True)
                    result['Country'] = result['Country'].str.strip()
                    result['Country'] = result['Country'].str.replace(r'[\*\u2020\u2021\u00a0]+', '', regex=True)
                    result['Country'] = result['Country'].str.strip()
                    
                    # Remove rows with no medals or invalid countries
                    result = result[result['Total'] > 0]
                    result = result[result['Country'].str.len() > 0]
                    result = result[~result['Country'].str.lower().str.contains('total|rank', na=False)]
                    
                    # Convert country names to NOC codes
                    result['Country'] = result['Country'].map(
                        lambda name: COUNTRY_NAME_TO_NOC.get(name, name)
                    )
                    
                    # Reorder columns to match existing format
                    result = result[['Year', 'Country', 'Gold', 'Silver', 'Bronze', 'Total']]
                    
                    # Report any unmapped names (still full names, not NOC codes)
                    unmapped = result[result['Country'].str.len() > 3]['Country'].tolist()
                    if unmapped:
                        print(f"⚠ Unmapped names: {unmapped}", end=" ")
                    
                    print(f"✓ ({len(result)} countries)")
                    return result
        
        print("✗ Table not found")
        return None
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def add_recent_data(season):
    """Add or update recent Olympics data for a season (summer or winter).
    
    For years that already exist in the by_year CSV:
      - Updates medal counts from Wikipedia (authoritative source)
      - Preserves zero-medal participating countries from extended athlete data
    For years that don't exist yet:
      - Adds the full Wikipedia medal table
    """
    
    # Determine file paths
    filename = f"{season}_olympics_by_year.csv"
    filepath = DATA_DIR / filename
    
    if not filepath.exists():
        print(f"✗ File not found: {filename}")
        return False
    
    # Load existing data
    existing_df = pd.read_csv(filepath)
    existing_years = set(existing_df['Year'].unique())
    
    print(f"\n{season.upper()} OLYMPICS")
    print("-" * 70)
    print(f"Current data: {int(existing_df['Year'].min())}-{int(existing_df['Year'].max())}")
    print(f"Updating/adding recent games from Wikipedia medal tables...")
    
    # Collect recent Olympics data from Wikipedia
    olympics_to_process = RECENT_OLYMPICS[season]
    updated = False
    
    for year in sorted(olympics_to_process.keys()):
        wiki_page = olympics_to_process[year]
        wiki_df = fetch_medal_table(year, wiki_page)
        if wiki_df is None:
            continue
        time.sleep(0.5)  # Be nice to Wikipedia
        
        if year in existing_years:
            # Year exists — update medal counts from Wikipedia while keeping all participants
            year_mask = existing_df['Year'] == year
            existing_year = existing_df[year_mask].copy()
            
            # Set all medal counts to 0 for this year (will be filled from Wikipedia)
            existing_year[['Gold', 'Silver', 'Bronze', 'Total']] = 0
            
            # Update with Wikipedia medal counts
            for _, wiki_row in wiki_df.iterrows():
                country = wiki_row['Country']
                country_mask = existing_year['Country'] == country
                if country_mask.any():
                    existing_year.loc[country_mask, 'Gold'] = int(wiki_row['Gold'])
                    existing_year.loc[country_mask, 'Silver'] = int(wiki_row['Silver'])
                    existing_year.loc[country_mask, 'Bronze'] = int(wiki_row['Bronze'])
                    existing_year.loc[country_mask, 'Total'] = int(wiki_row['Total'])
                else:
                    # Country won medals but wasn't in participant list — add them
                    new_row = pd.DataFrame([{
                        'Year': year,
                        'Country': country,
                        'Gold': int(wiki_row['Gold']),
                        'Silver': int(wiki_row['Silver']),
                        'Bronze': int(wiki_row['Bronze']),
                        'Total': int(wiki_row['Total']),
                    }])
                    existing_year = pd.concat([existing_year, new_row], ignore_index=True)
            
            # Replace this year's data in the main dataframe
            existing_df = pd.concat([existing_df[~year_mask], existing_year], ignore_index=True)
            
            medal_winners = existing_year[existing_year['Total'] > 0].shape[0]
            participants = len(existing_year)
            print(f"    Updated {year}: {medal_winners} medal winners, {participants} total participants")
            updated = True
        else:
            # New year — add Wikipedia data directly
            existing_df = pd.concat([existing_df, wiki_df], ignore_index=True)
            print(f"    Added {year}: {len(wiki_df)} countries")
            updated = True
    
    if not updated:
        print("No updates needed")
        return False
    
    # Sort and save
    existing_df = existing_df.sort_values(['Year', 'Total'], ascending=[True, False])
    existing_df.to_csv(filepath, index=False)
    
    print(f"\n✓ Updated {filename}")
    print(f"  Years now: {int(existing_df['Year'].min())}-{int(existing_df['Year'].max())}")
    print(f"  Total records: {len(existing_df)}")
    
    return True


# Main execution
print("\n" + "="*70)
print("ADDING RECENT OLYMPICS DATA")
print("="*70)

success_summer = add_recent_data('summer')
success_winter = add_recent_data('winter')

print("\n" + "="*70)
if success_summer or success_winter:
    print("✓ RECENT DATA ADDED SUCCESSFULLY!")
    print("="*70)
    print("\nYour dataset now includes:")
    print("  - Summer Olympics: 1896-2024")
    print("  - Winter Olympics: 1924-2022")
    print("\nRun 'python scripts/preview_yearly_data.py' to see updated data")
else:
    print("⚠ NO NEW DATA ADDED")
    print("="*70)

print("\n")
