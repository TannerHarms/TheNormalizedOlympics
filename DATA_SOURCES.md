# Data Sources Documentation

All data sources used in the Olympic normalization analysis, with provenance, URLs, and coverage notes.

---

## Olympic Medal Data

### Kaggle: 120 Years of Olympic History
- **Source**: [120 years of Olympic history: athletes and results](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results)
- **Dataset**: athlete_events.csv
- **Coverage**: 1896–2016 (271,116 athlete records)
- **License**: CC0: Public Domain
- **Accessed**: February 2026
- **Processing**: Deduplicated to count one medal per event (team events counted once, not per athlete)

### Olympedia (2018–2026)
- **Source**: [Olympedia.org](https://www.olympedia.org/) — comprehensive Olympic encyclopedia
- **Coverage**: 2018 Winter (PyeongChang), 2020 Summer (Tokyo), 2022 Winter (Beijing), 2024 Summer (Paris), 2026 Winter (Milano-Cortina)
- **Method**: Direct scrape of per-country results pages (`/countries/{NOC}/editions/{id}`)
- **Validation**: Medal tallies cross-checked against Olympedia's official edition medal tables
- **Script**: `scripts/scrape_olympedia.py` with HTTP caching (`data/olympedia_cache/`)
- **License**: Data scraped for research/analysis purposes
- **Accessed**: February 2026
- **Metrics extracted per country**:
  - Total athletes sent
  - Individual medalists (unique athletes winning ≥1 medal)
  - Event-level medals (Gold, Silver, Bronze, Total — deduplicated for team events)
  - Athlete-level medals awarded (Gold_Awarded, Silver_Awarded, Bronze_Awarded, Total_Medals_Awarded)

---

## World Bank Open Data

- **Source**: [World Bank Data API](https://api.worldbank.org/v2/)
- **License**: Creative Commons Attribution 4.0 (CC-BY 4.0)
- **Coverage**: 1960–2024, 125 countries
- **Accessed**: February 2026

### Core Indicators (world_bank_data.csv)

| Indicator | Code | Units | Coverage |
|-----------|------|-------|----------|
| Population | SP.POP.TOTL | People | 99% |
| GDP (Current US$) | NY.GDP.MKTP.CD | US Dollars | 86% |
| GDP per Capita | NY.GDP.PCAP.CD | US$/person | 86% |

### Additional Indicators (additional_world_bank_data.csv)

| Indicator | Code | Units | Notes |
|-----------|------|-------|-------|
| Land Area | AG.LND.TOTL.K2 | km² | |
| Surface Area | AG.SRF.TOTL.K2 | km² | |
| Internet Users | IT.NET.USER.ZS | % of pop. | Available ~2000+ |
| Vehicles per 1000 | IS.VEH.NVEH.P3 | Per 1000 people | Very sparse |
| Healthcare Spending | SH.XPD.CHEX.PC.CD | US$/capita | Available ~2000+ |
| Healthcare % GDP | SH.XPD.CHEX.GD.ZS | % of GDP | |
| Life Expectancy | SP.DYN.LE00.IN | Years | |
| Labor Force | SL.TLF.TOTL.IN | People | |

---

## Human Development Index

- **Source**: [UNDP Human Development Reports](https://hdr.undp.org/)
- **Dataset**: HDI Complete Time Series
- **Coverage**: 1990–2021, 202 countries
- **License**: CC-BY 3.0 IGO
- **Scale**: 0.0–1.0 (higher = more developed)
- **Accessed**: February 2026

---

## Geographic Data (geographic_features.csv)

- **Source**: CIA World Factbook, Wikipedia
- **Type**: Static (no year dependency)
- **Coverage**: 85 countries

| Feature | Units | Source |
|---------|-------|--------|
| Coastline Length | km | CIA World Factbook |
| Average Elevation | meters | CIA World Factbook, Wikipedia |

**Note**: Landlocked countries have coastline = 0.

---

## Climate Data (climate_features.csv)

- **Source**: World Bank Climate Knowledge Portal, national weather services
- **Type**: Static averages
- **Coverage**: 53 countries

| Feature | Units | Notes |
|---------|-------|-------|
| Average Temperature | °C | Annual mean |
| Average Snowfall | cm/year | National average |
| Sunshine Days | days/year | Days with significant sunshine |

**Note**: Values are approximate national averages. Large countries (USA, Russia, China) have wide regional variation.

---

## Climate Zone Classification (climate_data.csv)

- **Source**: Manual classification based on latitude and geography
- **Coverage**: 183 countries
- **Zones**: Arctic (10), Continental (32), Temperate (28), Mediterranean (34), Tropical (79)
- **Used for**: Winter Sports Index (0–10 scale)

---

## Sports & Culture Data (sports_culture_data.csv)

- **Source**: UNESCO Institute for Statistics, manually compiled
- **Type**: 2024 snapshot
- **Coverage**: 54 countries

| Feature | Source | Notes |
|---------|--------|-------|
| Number of Universities | UNESCO, national statistics | Definition varies by country |
| Number of Ski Resorts | Ski resort databases | Includes small resorts |
| Professional Sports Stadiums | Manually compiled | 50K+ capacity |

---

## Consumption Data (consumption_data.csv)

- **Source**: International Coffee Organization, consumption surveys
- **Type**: 2024 snapshot
- **Coverage**: 37 countries

| Feature | Units | Source |
|---------|-------|--------|
| Coffee Consumption | kg per capita/year | Intl Coffee Organization |
| Cola Servings | servings per capita/year | Industry consumption data |

---

## Work Hours (work_hours_data.csv)

- **Source**: [OECD Data Explorer](https://data-explorer.oecd.org/) via SDMX API
- **API**: `sdmx.oecd.org/public/rest/data/OECD.ELS.SAE,DSD_HW@DF_AVG_ANN_HRS_WKD`
- **Indicator**: Average annual hours actually worked per worker
- **Type**: Time series (2000–2023)
- **Coverage**: 45 OECD/partner countries
- **Script**: `scripts/collect_work_hours_data.py`
- **Note**: Non-OECD Olympic nations (China, India, etc.) not included. Russia included.

---

## Global Peace Index (global_peace_index.csv)

- **Source**: [Vision of Humanity / Institute for Economics & Peace](https://www.visionofhumanity.org/)
- **Report**: GPI 2024
- **Type**: 2024 snapshot
- **Coverage**: 47 countries (subset of 163 ranked)
- **Scale**: 1.0–5.0 (lower = more peaceful)

---

## Refugee Data (refugee_data.csv)

- **Source**: [UNHCR Refugee Statistics](https://www.unhcr.org/refugee-statistics/)
- **Type**: 2023 snapshot
- **Coverage**: 66 countries

| Feature | Units | Description |
|---------|-------|-------------|
| Refugees Received | People | Total refugees/asylum seekers hosted |
| Refugees Produced | People | Total refugees/asylum seekers originating from country |

---

## Military Data (military_data.csv)

- **Source**: [World Bank Open Data](https://data.worldbank.org/) (originally sourced from SIPRI and IISS)
- **API**: `api.worldbank.org/v2`
- **Type**: Time series (2000–2023)
- **Coverage**: 122 countries
- **Script**: `scripts/collect_military_data.py`

| Feature | Indicator Code | Units | Years |
|---------|---------------|-------|-------|
| Military Expenditure | MS.MIL.XPND.CD | Current USD | 2000–2023 |
| Military Spending per Capita | Computed | USD/person | 2000–2023 |
| Armed Forces Personnel | MS.MIL.TOTL.P1 | People | 2000–2020 |
| Active Military Personnel | Computed | Thousands | 2000–2020 |

**Note**: Per-capita spending computed from total expenditure / population.

---

## Education Spending (education_spending.csv)

- **Source**: World Bank (SE.XPD.TOTL.GD.ZS)
- **Type**: Time series
- **Coverage**: 35% of records (sparse reporting)
- **Note**: ⚠️ Many countries don't report consistently. Use cautiously.

---

## Country Code Mapping

- **Source**: Manual mapping table (country_mapping.py)
- **Coverage**: 176 active Olympic NOC codes → World Bank ISO3 codes
- **Key mappings**: GER→DEU, NED→NLD, SUI→CHE, GRE→GRC, ROC→RUS

---

## Data Limitations

1. **Time-series vs. snapshot metrics**: Military spending, military personnel, and OECD work hours are now proper time-series matched by year. Refugees, peace index, and consumption data remain as snapshots applied to all Olympic years.
2. **Coverage gaps**: Smaller nations often lack data for niche metrics. Coverage ranges from 24% (ski resorts) to 99% (population).
3. **GDP not inflation-adjusted**: GDP is in current US dollars, not PPP or constant dollars.
4. **Historical countries**: Soviet Union, Yugoslavia, etc. are mapped to successor states using modern economic data.
5. **University/stadium definitions**: Vary by country — some count all higher education institutions, others only major universities.
6. **Climate averages**: Large countries have wide regional variation; values are national approximations.
7. **OECD work hours**: Only covers 45 OECD/partner countries; no data for China, India, most African nations.
8. **Refugee API limitation**: UNHCR and World Bank refugee indicators were tested for time-series conversion but failed (WB indicators archived, UNHCR API country filtering broken). Data remains as 2023 snapshot.

---

## Citation

**Olympic Medal Data:**
- Griffin, R. (2018). 120 years of Olympic history. Kaggle. https://www.kaggle.com/heesoo37/120-years-of-olympic-history-athletes-and-results
- Olympedia.org. (2026). Olympic results database. https://www.olympedia.org/ (direct scrape of 2018–2026 editions)

**Economic Data:**
- World Bank. (2024). World Development Indicators. https://data.worldbank.org/

**Human Development:**
- UNDP. (2022). Human Development Report 2021-22. https://hdr.undp.org/

**Military:**
- World Bank. (2024). Military expenditure (MS.MIL.XPND.CD) and Armed forces personnel (MS.MIL.TOTL.P1). https://data.worldbank.org/ (via API, data originally from SIPRI and IISS)

**Work Hours:**
- OECD. (2024). Average annual hours actually worked per worker. https://data-explorer.oecd.org/ (via SDMX API)

**Peace:**
- IEP. (2024). Global Peace Index. https://www.visionofhumanity.org/

**Refugees:**
- UNHCR. (2023). Refugee Statistics. https://www.unhcr.org/refugee-statistics/

---

*Last Updated: February 10, 2026*
