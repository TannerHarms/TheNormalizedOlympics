"""
Comprehensive mapping of Olympic NOC codes to World Bank country codes

Olympic data uses NOC (National Olympic Committee) codes like 'USA', 'GBR', 'GER'
World Bank uses ISO 3166-1 alpha-3 codes like 'USA', 'GBR', 'DEU'

This mapping handles all the differences and historical changes.
"""

# Mapping from Olympic NOC codes to World Bank ISO3 codes
NOC_TO_WB = {
    # Major countries (mostly same)
    'USA': 'USA',
    'CHN': 'CHN',
    'GBR': 'GBR',
    'JPN': 'JPN',
    'FRA': 'FRA',
    'ITA': 'ITA',
    'AUS': 'AUS',
    'CAN': 'CAN',
    'KOR': 'KOR',  # South Korea
    'NED': 'NLD',  # Netherlands
    'ESP': 'ESP',
    'BRA': 'BRA',
    'RUS': 'RUS',
    'GER': 'DEU',  # Germany
    'NZL': 'NZL',
    'SUI': 'CHE',  # Switzerland
    'SWE': 'SWE',
    'NOR': 'NOR',
    'DEN': 'DNK',  # Denmark
    'FIN': 'FIN',
    'BEL': 'BEL',
    'POL': 'POL',
    'UKR': 'UKR',
    'CZE': 'CZE',
    'AUT': 'AUT',
    'HUN': 'HUN',
    'MEX': 'MEX',
    'ARG': 'ARG',
    'RSA': 'ZAF',  # South Africa
    'IND': 'IND',
    'POR': 'PRT',  # Portugal
    'GRE': 'GRC',  # Greece
    'TUR': 'TUR',
    'IRL': 'IRL',
    'EGY': 'EGY',
    'JAM': 'JAM',
    'KEN': 'KEN',
    'ETH': 'ETH',
    'CUB': 'CUB',
    'NGR': 'NGA',  # Nigeria
    'ALG': 'DZA',  # Algeria
    'MAR': 'MAR',
    'TUN': 'TUN',
    'COL': 'COL',
    'CHI': 'CHL',  # Chile
    'VEN': 'VEN',
    'PER': 'PER',
    'ECU': 'ECU',
    'URU': 'URY',
    'PAK': 'PAK',
    'THA': 'THA',
    'MAS': 'MYS',  # Malaysia
    'SGP': 'SGP',
    'INA': 'IDN',  # Indonesia
    'PHI': 'PHL',  # Philippines
    'VIE': 'VNM',  # Vietnam
    'ISR': 'ISR',
    'IRQ': 'IRQ',
    'IRI': 'IRN',  # Iran
    'SAU': 'SAU',  # Saudi Arabia (Olympic: KSA)
    'KSA': 'SAU',  # Saudi Arabia
    'UAE': 'ARE',
    'KUW': 'KWT',  # Kuwait
    'QAT': 'QAT',
    'BAH': 'BHS',  # Bahamas
    'BRN': 'BHR',  # Bahrain
    'JOR': 'JOR',
    'TPE': 'TWN',  # Chinese Taipei
    'HKG': 'HKG',  # Hong Kong
    'LEB': 'LBN',  # Lebanon
    'SYR': 'SYR',
    
    # Historical/Special cases
    'ROC': 'RUS',  # Russian Olympic Committee (2020, 2022)
    'OAR': 'RUS',  # Olympic Athletes from Russia (2018)
    'URS': None,   # Soviet Union (1952-1988) - no direct modern equivalent
    'EUN': None,   # Unified Team (1992) - mix of former Soviet states
    'TCH': None,   # Czechoslovakia (until 1992)
    'YUG': None,   # Yugoslavia (until 1992)
    'GDR': 'DEU',  # East Germany (merged into Germany)
    'FRG': 'DEU',  # West Germany (merged into Germany)
    'EUA': 'DEU',  # United Team of Germany (1956-1964)
    
    # Caribbean
    'TRI': 'TTO',  # Trinidad and Tobago
    'BAR': 'BRB',  # Barbados
    'DOM': 'DOM',
    'HAI': 'HTI',  # Haiti
    'PUR': 'PRI',  # Puerto Rico
    
    # Africa
    'GHA': 'GHA',
    'ZIM': 'ZWE',  # Zimbabwe
    'UGA': 'UGA',
    'BOT': 'BWA',  # Botswana
    'NAM': 'NAM',
    'TAN': 'TZA',  # Tanzania
    'ZAM': 'ZMB',  # Zambia
    'SEN': 'SEN',
    'CIV': 'CIV',  # Ivory Coast
    'CMR': 'CMR',  # Cameroon
    'BUR': 'BFA',  # Burkina Faso
    'MLI': 'MLI',
    'NIG': 'NER',  # Niger
    'TOG': 'TGO',  # Togo
    'BEN': 'BEN',
    'GAB': 'GAB',
    'CGO': 'COG',  # Republic of Congo
    'COD': 'COD',  # Democratic Republic of Congo
    'ANG': 'AGO',  # Angola
    'MOZ': 'MOZ',  # Mozambique
    'MAD': 'MDG',  # Madagascar
    'MRI': 'MUS',  # Mauritius
    'SEY': 'SYC',  # Seychelles
    
    # Asia
    'PRK': 'PRK',  # North Korea
    'MGL': 'MNG',  # Mongolia
    'KAZ': 'KAZ',
    'UZB': 'UZB',
    'TKM': 'TKM',  # Turkmenistan
    'KGZ': 'KGZ',  # Kyrgyzstan
    'TJK': 'TJK',  # Tajikistan
    'AFG': 'AFG',
    'BAN': 'BGD',  # Bangladesh
    'SRI': 'LKA',  # Sri Lanka
    'NEP': 'NPL',  # Nepal
    'BHU': 'BTN',  # Bhutan
    'MYA': 'MMR',  # Myanmar
    'LAO': 'LAO',
    'CAM': 'KHM',  # Cambodia
    'BRU': 'BRN',  # Brunei
    'TLS': 'TLS',  # Timor-Leste
    
    # Central/South America
    'BOL': 'BOL',
    'PAR': 'PRY',  # Paraguay
    'GUY': 'GUY',
    'SUR': 'SUR',  # Suriname
    'GUA': 'GTM',  # Guatemala
    'HON': 'HND',  # Honduras
    'NCA': 'NIC',  # Nicaragua
    'CRC': 'CRI',  # Costa Rica
    'PAN': 'PAN',
    'ESA': 'SLV',  # El Salvador
    'BIZ': 'BLZ',  # Belize
    
    # Europe
    'SLO': 'SVN',  # Slovenia
    'CRO': 'HRV',  # Croatia
    'SRB': 'SRB',
    'BIH': 'BIH',  # Bosnia and Herzegovina
    'MKD': 'MKD',  # North Macedonia
    'MNE': 'MNE',  # Montenegro
    'ALB': 'ALB',
    'KOS': 'XKX',  # Kosovo (World Bank uses XKX)
    'BUL': 'BGR',  # Bulgaria
    'ROM': 'ROU',  # Romania
    'MDA': 'MDA',  # Moldova
    'GEO': 'GEO',
    'ARM': 'ARM',
    'AZE': 'AZE',
    'BLR': 'BLR',  # Belarus
    'LTU': 'LTU',
    'LAT': 'LVA',  # Latvia
    'EST': 'EST',
    'SVK': 'SVK',  # Slovakia
    'ISL': 'ISL',  # Iceland
    'LUX': 'LUX',
    'MLT': 'MLT',  # Malta
    'CYP': 'CYP',
    'AND': 'AND',  # Andorra
    'MON': 'MCO',  # Monaco
    'LIE': 'LIE',  # Liechtenstein
    'SMR': 'SMR',  # San Marino
    
    # Oceania
    'PNG': 'PNG',  # Papua New Guinea
    'FIJ': 'FJI',  # Fiji
    'SAM': 'WSM',  # Samoa
    'TON': 'TON',  # Tonga
    'SOL': 'SLB',  # Solomon Islands
    'VAN': 'VUT',  # Vanuatu
    'PLW': 'PLW',  # Palau
    'FSM': 'FSM',  # Micronesia
    'MHL': 'MHL',  # Marshall Islands
    'KIR': 'KIR',  # Kiribati
    'TUV': 'TUV',  # Tuvalu
    'NAU': 'NRU',  # Nauru
    'COK': 'COK',  # Cook Islands
    
    # Other
    'LBA': 'LBY',  # Libya
    'SUD': 'SDN',  # Sudan
    'SSD': 'SSD',  # South Sudan
    'ERI': 'ERI',  # Eritrea
    'DJI': 'DJI',  # Djibouti
    'SOM': 'SOM',  # Somalia
}

# Reverse mapping (World Bank to NOC) - useful for some operations
WB_TO_NOC = {v: k for k, v in NOC_TO_WB.items() if v is not None}

# Historical countries that no longer exist
HISTORICAL_COUNTRIES = {
    'URS': 'Soviet Union (1952-1988)',
    'EUN': 'Unified Team (1992)',
    'TCH': 'Czechoslovakia (until 1992)',
    'YUG': 'Yugoslavia (until 1992)',
    'GDR': 'East Germany (until 1990)',
    'FRG': 'West Germany (until 1990)',
    'EUA': 'United Team of Germany (1956-1964)',
}

def get_wb_code(noc_code):
    """
    Get World Bank country code from Olympic NOC code.
    
    Args:
        noc_code: Olympic NOC code (e.g., 'USA', 'GER', 'ROC')
    
    Returns:
        World Bank ISO3 code or None if not mappable
    """
    return NOC_TO_WB.get(noc_code)

def get_noc_code(wb_code):
    """
    Get Olympic NOC code from World Bank code.
    
    Args:
        wb_code: World Bank ISO3 code (e.g., 'USA', 'DEU')
    
    Returns:
        Olympic NOC code or None if not mappable
    """
    return WB_TO_NOC.get(wb_code)

def is_historical(noc_code):
    """Check if a NOC code represents a historical country."""
    return noc_code in HISTORICAL_COUNTRIES

if __name__ == "__main__":
    print("="*70)
    print("COUNTRY CODE MAPPING TEST")
    print("="*70)
    
    # Test some common mappings
    test_codes = ['USA', 'GER', 'NED', 'SUI', 'ROC', 'URS', 'GBR', 'CHN']
    
    print("\nOlympic NOC → World Bank Code:")
    for noc in test_codes:
        wb = get_wb_code(noc)
        if wb:
            print(f"  {noc:5} → {wb}")
        else:
            hist = HISTORICAL_COUNTRIES.get(noc, 'Unknown')
            print(f"  {noc:5} → (No mapping: {hist})")
    
    print(f"\n✓ Total mappings: {len([v for v in NOC_TO_WB.values() if v is not None])}")
    print(f"✓ Historical countries: {len(HISTORICAL_COUNTRIES)}")
    print("="*70)
