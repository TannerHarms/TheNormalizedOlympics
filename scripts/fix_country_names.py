"""
Fix country names in Olympics data - convert full names to NOC codes.
"""

import pandas as pd
from pathlib import Path

# Comprehensive country name to NOC code mapping
NAME_TO_CODE = {
    'United States': 'USA',
    'China': 'CHN',
    'Great Britain': 'GBR',
    'Japan': 'JPN',
    'Australia': 'AUS',
    'Italy': 'ITA',
    'Germany': 'GER',
    'Netherlands': 'NED',
    'France': 'FRA',
    'Canada': 'CAN',
    'Brazil': 'BRA',
    'New Zealand': 'NZL',
    'Hungary': 'HUN',
    'South Korea': 'KOR',
    'Ukraine': 'UKR',
    'Spain': 'ESP',
    'Cuba': 'CUB',
    'Poland': 'POL',
    'Switzerland': 'SUI',
    'Czech Republic': 'CZE',
    'Kenya': 'KEN',
    'Norway': 'NOR',
    'Jamaica': 'JAM',
    'Croatia': 'CRO',
    'Georgia': 'GEO',
    'Chinese Taipei': 'TPE',
    'Belgium': 'BEL',
    'Thailand': 'THA',
    'Kazakhstan': 'KAZ',
    'Israel': 'ISR',
    'Sweden': 'SWE',
    'Iran': 'IRI',
    'Serbia': 'SRB',
    'Uzbekistan': 'UZB',
    'Argentina': 'ARG',
    'Mexico': 'MEX',
    'Denmark': 'DEN',
    'Finland': 'FIN',
    'Venezuela': 'VEN',
    'Austria': 'AUT',
    'Egypt': 'EGY',
    'Indonesia': 'INA',
    'Ethiopia': 'ETH',
    'Portugal': 'POR',
    'Greece': 'GRE',
    'Qatar': 'QAT',
    'Singapore': 'SGP',
    'Bahrain': 'BRN',
    'Slovakia': 'SVK',
    'South Africa': 'RSA',
    'Slovenia': 'SLO',
    'Belarus': 'BLR',
    'Turkey': 'TUR',
    'Colombia': 'COL',
    'Tunisia': 'TUN',
    'Dominican Republic': 'DOM',
    'Algeria': 'ALG',
    'Romania': 'ROU',
    'Ecuador': 'ECU',
    'Puerto Rico': 'PUR',
    'Ireland': 'IRL',
    'Azerbaijan': 'AZE',
    'Armenia': 'ARM',
    'Kyrgyzstan': 'KGZ',
    'Mongolia': 'MGL',
    'Bermuda': 'BER',
    'Morocco': 'MAR',
    'India': 'IND',
    'Uganda': 'UGA',
    'San Marino': 'SMR',
    'Latvia': 'LAT',
    'Fiji': 'FIJ',
    'Lithuania': 'LTU',
    'North Macedonia': 'MKD',
    'Hong Kong': 'HKG',
    'Philippines': 'PHI',
    'Burkina Faso': 'BUR',
    'Kosovo': 'KOS',
    'Cote d\'Ivoire': 'CIV',
    'Ivory Coast': 'CIV',
    'Ghana': 'GHA',
    'Grenada': 'GRN',
    'Jordan': 'JOR',
    'Namibia': 'NAM',
    'Syria': 'SYR',
    'Burundi': 'BDI',
    'Botswana': 'BOT',
    'Moldova': 'MDA',
    'Estonia': 'EST',
    'Bulgaria': 'BUL',
    'Bahamas': 'BAH',
    'Saudi Arabia': 'KSA',
    'Kuwait': 'KUW',
    'North Korea': 'PRK',
    'Nigeria': 'NGR',
    'Peru': 'PER',
    'Tajikistan': 'TJK',
    'Turkmenistan': 'TKM',
    'Liechtenstein': 'LIE',
    'Olympic Athletes from Russia': 'OAR',
    'Individual Neutral Athletes': 'AIN',
    'Refugee Olympic Team': 'EOR',
    'Chile': 'CHI',
    'Cyprus': 'CYP',
    'Dominica': 'DMA',
    'Albania': 'ALB',
    'Malaysia': 'MAS',
    'Trinidad and Tobago': 'TRI',
    'Barbados': 'BAR',
    'Zimbabwe': 'ZIM',
    'Uganda': 'UGA',
    'Pakistan': 'PAK',
    'Vietnam': 'VIE',
    'Guatemala': 'GUA',
    'Cameroon': 'CMR',
    'Cape Verde': 'CPV',
    'Mongolia': 'MGL',
    'Sri Lanka': 'SRI',
    'Paraguay': 'PAR',
    'Honduras': 'HON',
    'Costa Rica': 'CRC',
    'Panama': 'PAN',
    'Lithuania': 'LTU',
    'Latvia': 'LAT',
    'Romania': 'ROU',
    'Luxembourg': 'LUX',
    'Montenegro': 'MNE',
    'Bosnia and Herzegovina': 'BIH',
    'North Macedonia': 'MKD',
    'Iceland': 'ISL',
    'Myanmar': 'MYA',
    'Colombia': 'COL',
    'Haiti': 'HAI',
    'Zambia': 'ZAM',
    'Tanzania': 'TAN',
    'Senegal': 'SEN',
    'Niger': 'NIG',
    'Madagascar': 'MAD',
    'Bolivia': 'BOL',
    'Uruguay': 'URU',
    'Saint Lucia': 'LCA',
}

def fix_country_names(df):
    """Convert full country names to NOC codes"""
    # First, map any full names to codes
    df['Country'] = df['Country'].replace(NAME_TO_CODE)
    return df


def main():
    data_dir = Path(__file__).parent.parent / 'data'
    
    print("="*70)
    print("FIXING COUNTRY NAMES IN OLYMPICS DATA")
    print("="*70)
    print()
    
    # Fix summer_olympics_by_year.csv
    print("Fixing summer_olympics_by_year.csv...")
    summer_path = data_dir / 'summer_olympics_by_year.csv'
    summer = pd.read_csv(summer_path)
    
    print(f"  Before: {summer['Country'].nunique()} unique countries")
    print(f"  Sample 2020: {summer[summer['Year'] == 2020]['Country'].unique()[:10].tolist()}")
    
    summer = fix_country_names(summer)
    summer.to_csv(summer_path, index=False)
    
    print(f"  After: {summer['Country'].nunique()} unique countries")
    print(f"  Sample 2020: {summer[summer['Year'] == 2020]['Country'].unique()[:10].tolist()}")
    print(f"  ✓ Saved")
    print()
    
    # Fix winter_olympics_by_year.csv
    print("Fixing winter_olympics_by_year.csv...")
    winter_path = data_dir / 'winter_olympics_by_year.csv'
    winter = pd.read_csv(winter_path)
    
    print(f"  Before: {winter['Country'].nunique()} unique countries")
    print(f"  Sample 2022: {winter[winter['Year'] == 2022]['Country'].unique()[:10].tolist()}")
    
    winter = fix_country_names(winter)
    winter.to_csv(winter_path, index=False)
    
    print(f"  After: {winter['Country'].nunique()} unique countries")
    print(f"  Sample 2022: {winter[winter['Year'] == 2022]['Country'].unique()[:10].tolist()}")
    print(f"  ✓ Saved")
    print()
    
    print("="*70)
    print("✓ COUNTRY NAMES FIXED!")
    print("="*70)
    print()
    print("Next: Recalculate historical totals and re-merge data")
    print()


if __name__ == '__main__':
    main()
