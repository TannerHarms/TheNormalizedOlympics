# Data Sources Documentation

This document lists all data sources used in the Olympic normalization analysis, with links and access dates.

## Olympic Medal Data

### Kaggle: 120 Years of Olympic History
- **Source**: [120 years of Olympic history: athletes and results](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results)
- **Dataset**: athlete_events.csv
- **Coverage**: 1896-2016 (271,116 athlete records)
- **License**: CC0: Public Domain
- **Accessed**: February 2026
- **Description**: Athlete-level data including name, country, event, and medal results
- **Processing**: Deduplicated to count one medal per event (team events counted once, not per athlete)

### Wikipedia Medal Tables
- **Source**: Wikipedia medal count tables for recent Olympics
- **URLs**:
  - [2018 Winter Olympics](https://en.wikipedia.org/wiki/2018_Winter_Olympics_medal_table)
  - [2020 Summer Olympics](https://en.wikipedia.org/wiki/2020_Summer_Olympics_medal_table) (held in 2021)
  - [2022 Winter Olympics](https://en.wikipedia.org/wiki/2022_Winter_Olympics_medal_table)
  - [2024 Summer Olympics](https://en.wikipedia.org/wiki/2024_Summer_Olympics_medal_table)
- **Coverage**: 2018-2024 (185 Summer + 59 Winter records)
- **License**: Creative Commons
- **Accessed**: February 2026
- **Processing**: Scraped using BeautifulSoup4, cleaned Unicode artifacts and footnotes

---

## Economic & Demographic Data

### World Bank Open Data
- **Source**: [World Bank Data API](https://api.worldbank.org/v2/)
- **Documentation**: https://datahelpdesk.worldbank.org/knowledgebase/topics/125589
- **Coverage**: 1960-2024, 125 countries
- **License**: Creative Commons Attribution 4.0 (CC-BY 4.0)
- **Accessed**: February 2026

#### Indicators Used:

**1. Population (Total)**
- **Indicator Code**: SP.POP.TOTL
- **URL**: https://data.worldbank.org/indicator/SP.POP.TOTL
- **Coverage**: 8,060 / 8,125 records (99.2%)
- **Units**: Number of people

**2. GDP (Current US$)**
- **Indicator Code**: NY.GDP.MKTP.CD
- **URL**: https://data.worldbank.org/indicator/NY.GDP.MKTP.CD
- **Coverage**: 7,005 / 8,125 records (86.2%)
- **Units**: Current US dollars
- **Note**: Not adjusted for inflation

**3. GDP per Capita (Current US$)**
- **Indicator Code**: NY.GDP.PCAP.CD
- **URL**: https://data.worldbank.org/indicator/NY.GDP.PCAP.CD
- **Coverage**: 7,005 / 8,125 records (86.2%)
- **Units**: Current US dollars per person

**4. Government Expenditure on Education (% of GDP)**
- **Indicator Code**: SE.XPD.TOTL.GD.ZS
- **URL**: https://data.worldbank.org/indicator/SE.XPD.TOTL.GD.ZS
- **Coverage**: 2,840 / 8,125 records (35.0%)
- **Units**: Percentage of GDP
- **Note**: ⚠️ **Sparse data** - many countries don't report consistently
- **Available for**: 99 / 125 countries
- **Date Range**: 1970-2024 (sparse)
- **Missing data for**: Australia, Japan, Egypt, Kenya, Kazakhstan, Latvia, Luxembourg, and others

---

## Human Development Data

### UNDP Human Development Reports
- **Source**: [United Nations Development Programme](https://hdr.undp.org/)
- **Dataset**: Human Development Index (HDI) Complete Time Series
- **Direct Link**: https://hdr.undp.org/sites/default/files/2021-22_HDR/HDR21-22_Composite_indices_complete_time_series.csv
- **Coverage**: 1990-2021, 202 countries, 16,546 records
- **License**: Creative Commons Attribution 3.0 IGO
- **Accessed**: February 2026
- **Description**: Composite index measuring life expectancy, education, and per capita income
- **Scale**: 0.0 to 1.0 (higher is better)

**HDI Components:**
- Life expectancy at birth
- Expected years of schooling  
- Mean years of schooling
- GNI per capita (PPP)

---

## Climate Data

### Climate Zone Classification
- **Source**: Manual classification based on geographical knowledge
- **Methodology**: Countries classified into 5 climate zones based on latitude and typical winter conditions
- **Coverage**: 183 countries
- **Accessed**: February 2026

**Climate Zones:**
1. **Arctic/Subarctic** (10 countries)
   - Examples: Norway, Sweden, Finland, Canada, Russia
   - Winter Sports Index: 10/10 (excellent conditions)
   - Avg. Temperature: -5°C

2. **Continental** (32 countries)
   - Examples: USA, Austria, Switzerland, Germany, Japan
   - Winter Sports Index: 7/10 (good conditions)
   - Avg. Temperature: 5°C

3. **Temperate** (28 countries)
   - Examples: UK, Australia, New Zealand, Argentina
   - Winter Sports Index: 4/10 (moderate conditions)
   - Avg. Temperature: 12°C

4. **Mediterranean/Subtropical** (34 countries)
   - Examples: Spain, Greece, Morocco, India
   - Winter Sports Index: 2/10 (limited conditions)
   - Avg. Temperature: 18°C

5. **Tropical** (79 countries)
   - Examples: Brazil, Nigeria, Kenya, Jamaica
   - Winter Sports Index: 0/10 (no winter conditions)
   - Avg. Temperature: 26°C

**Note**: This is a simplified classification. Some large countries (USA, Russia, China) have multiple climate zones; classification represents predominant conditions where population is concentrated.

---

## Country Code Mappings

### Olympic NOC Codes to World Bank ISO3
- **Source**: Manual mapping table
- **Coverage**: 176 active Olympic NOC codes mapped to World Bank ISO3 codes
- **Historical Countries**: 7 (EUN, TCH, URS, YUG, etc.)
- **Purpose**: Join Olympic data with World Bank indicators

**Key Mappings:**
- GER → DEU (Germany)
- NED → NLD (Netherlands)
- SUI → CHE (Switzerland)
- GRE → GRC (Greece)
- ROC → RUS (Russian Olympic Committee)

**References:**
- [Olympic Country Codes](https://en.wikipedia.org/wiki/List_of_IOC_country_codes)
- [World Bank Country Codes](https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups)

---

## Data Limitations & Notes

### Coverage Issues

**Pre-1960 Olympics:**
- World Bank data only goes back to 1960
- Analysis limited to Olympics from 1960 onwards:
  - Summer: 1960-2024 (16 Olympics)
  - Winter: 1960-2022 (16 Olympics)
- Earlier Olympics (1896-1956 Summer, 1924-1956 Winter) excluded from normalized analysis

**Education Spending:**
- ⚠️ Only 35% data coverage (2,840 / 8,125 possible records)
- Major gaps for: Australia, Japan, Egypt, Kenya, Kazakhstan, Latvia, Luxembourg, and others
- Data collection inconsistent across countries and time periods
- **Use cautiously** - results may not be representative
- Many developed countries (Australia, Japan) have no reported data

**HDI Data:**
- Only available from 1990 onwards (not 1960)
- Limits analysis of early Olympic periods (1960-1988)
- Some duplicate/revision data in raw UNDP file

**Historical Countries:**
- Soviet Union (URS), Yugoslavia (YUG), Czechoslovakia (TCH), East Germany (GDR), etc.
- Not included in modern normalization data
- Historical medals attributed to successor states where appropriate

### Data Quality

**Medal Count Verification:**
- Kaggle data independently verified against official IOC records
- Critical bug fixed: Team events initially counted each athlete as separate medal
- Now correctly counts one medal per event
- Spot-checked: USA 2016 Rio (46 gold, 121 total ✓), Norway 2022 Beijing (16 gold, 37 total ✓)

**Economic Data:**
- GDP in current US dollars (not adjusted for inflation/PPP)
- For time-series analysis, consider inflation adjustment
- Some countries have sparse GDP data (especially smaller nations, earlier years)

---

## Citation

If using this analysis or data compilation, please cite:

**Olympic Medal Data:**
- Kaggle Dataset: Griffin, R. (2018). 120 years of Olympic history: athletes and results. Kaggle. https://www.kaggle.com/heesoo37/120-years-of-olympic-history-athletes-and-results
- Wikipedia Contributors. (2026). Olympic medal tables. Wikipedia. https://en.wikipedia.org/wiki/

**World Bank Data:**
- World Bank. (2024). World Development Indicators. The World Bank Group. https://data.worldbank.org/

**UNDP HDI:**
- United Nations Development Programme. (2021/22). Human Development Report 2021-22. http://hdr.undp.org/

---

## Tools & Libraries

**Programming Language:** Python 3.12.2

**Key Libraries:**
- pandas 2.x - Data manipulation
- requests - API calls and web scraping
- beautifulsoup4 - HTML parsing
- matplotlib - Data visualization
- seaborn - Statistical graphics
- openpyxl - Excel file handling

**Environment:** Virtual environment (.venv)

---

## Last Updated

February 6, 2026
