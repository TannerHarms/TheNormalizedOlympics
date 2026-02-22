"""
Scrape complete Olympic dataset from Olympedia.org.

For every held Summer and Winter Olympics edition, this script:
1. Fetches the list of participating countries (/editions/{id}/countries)
2. Fetches each country's results page (/countries/{NOC}/editions/{id})
3. Parses: Total_Athletes, Individual_Medalists, medal tallies, awarded counts
4. Caches raw HTML to disk for reproducibility
5. Outputs: data/olympedia_summer.csv and data/olympedia_winter.csv

Usage:
    python scripts/scrape_olympedia.py                    # scrape everything
    python scripts/scrape_olympedia.py --season winter    # winter only
    python scripts/scrape_olympedia.py --season summer    # summer only
    python scripts/scrape_olympedia.py --edition 62       # one edition only
    python scripts/scrape_olympedia.py --dry-run          # show plan, don't fetch
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CACHE_DIR = DATA_DIR / "olympedia_cache"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Research project"
}

REQUEST_DELAY = 5.0  # seconds between requests
MAX_RETRIES = 5
RETRY_BACKOFF = 30   # seconds for first retry; doubles each attempt

# Complete mapping of Olympedia edition IDs → (year, city, season)
# Only actually-held games are included.
EDITIONS = {
    # ---- Summer Olympics ----
    1:  (1896, "Athens",          "Summer"),
    2:  (1900, "Paris",           "Summer"),
    3:  (1904, "St. Louis",      "Summer"),
    5:  (1908, "London",         "Summer"),
    6:  (1912, "Stockholm",      "Summer"),
    7:  (1920, "Antwerp",        "Summer"),
    8:  (1924, "Paris",          "Summer"),
    9:  (1928, "Amsterdam",      "Summer"),
    10: (1932, "Los Angeles",    "Summer"),
    11: (1936, "Berlin",         "Summer"),
    12: (1948, "London",         "Summer"),
    13: (1952, "Helsinki",       "Summer"),
    14: (1956, "Melbourne",      "Summer"),
    15: (1960, "Rome",           "Summer"),
    16: (1964, "Tokyo",          "Summer"),
    17: (1968, "Mexico City",    "Summer"),
    18: (1972, "Munich",         "Summer"),
    19: (1976, "Montreal",       "Summer"),
    20: (1980, "Moscow",         "Summer"),
    21: (1984, "Los Angeles",    "Summer"),
    22: (1988, "Seoul",          "Summer"),
    23: (1992, "Barcelona",      "Summer"),
    24: (1996, "Atlanta",        "Summer"),
    25: (2000, "Sydney",         "Summer"),
    26: (2004, "Athens",         "Summer"),
    53: (2008, "Beijing",        "Summer"),
    54: (2012, "London",         "Summer"),
    59: (2016, "Rio de Janeiro", "Summer"),
    61: (2020, "Tokyo",          "Summer"),
    63: (2024, "Paris",          "Summer"),
    # ---- Winter Olympics ----
    29: (1924, "Chamonix",       "Winter"),
    30: (1928, "St. Moritz",     "Winter"),
    31: (1932, "Lake Placid",    "Winter"),
    32: (1936, "Garmisch",       "Winter"),
    33: (1948, "St. Moritz",     "Winter"),
    34: (1952, "Oslo",           "Winter"),
    35: (1956, "Cortina",        "Winter"),
    36: (1960, "Squaw Valley",   "Winter"),
    37: (1964, "Innsbruck",      "Winter"),
    38: (1968, "Grenoble",       "Winter"),
    39: (1972, "Sapporo",        "Winter"),
    40: (1976, "Innsbruck",      "Winter"),
    41: (1980, "Lake Placid",    "Winter"),
    42: (1984, "Sarajevo",       "Winter"),
    43: (1988, "Calgary",        "Winter"),
    44: (1992, "Albertville",    "Winter"),
    45: (1994, "Lillehammer",    "Winter"),
    46: (1998, "Nagano",         "Winter"),
    47: (2002, "Salt Lake City", "Winter"),
    49: (2006, "Turin",          "Winter"),
    57: (2010, "Vancouver",      "Winter"),
    58: (2014, "Sochi",          "Winter"),
    60: (2018, "PyeongChang",    "Winter"),
    62: (2022, "Beijing",        "Winter"),
    72: (2026, "Milano-Cortina", "Winter"),
}

# ---------------------------------------------------------------------------
# HTTP helpers with caching
# ---------------------------------------------------------------------------

_session = requests.Session()
_session.headers.update(HEADERS)
_last_request_time = 0.0


def _rate_limit():
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < REQUEST_DELAY:
        time.sleep(REQUEST_DELAY - elapsed)
    _last_request_time = time.time()


def fetch(url: str, cache_path: Path) -> str:
    """Fetch a URL, using disk cache if available.  Retries on 429/5xx."""
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")

    for attempt in range(MAX_RETRIES):
        _rate_limit()
        try:
            resp = _session.get(url, timeout=60)
            if resp.status_code == 429:
                wait = RETRY_BACKOFF * (2 ** attempt)
                print(f"      429 rate-limited, waiting {wait}s (attempt {attempt+1}/{MAX_RETRIES})")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            html = resp.text
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(html, encoding="utf-8")
            return html
        except requests.ConnectionError as e:
            wait = RETRY_BACKOFF * (2 ** attempt)
            print(f"      Connection error, retrying in {wait}s: {e}")
            time.sleep(wait)
            continue

    # Final attempt
    _rate_limit()
    resp = _session.get(url, timeout=60)
    resp.raise_for_status()
    html = resp.text
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(html, encoding="utf-8")
    return html


def fetch_countries_for_edition(edition_id: int) -> list[str]:
    """Return sorted list of NOC codes for an edition."""
    cache = CACHE_DIR / f"editions/{edition_id}_countries.html"
    url = f"https://www.olympedia.org/editions/{edition_id}/countries"
    html = fetch(url, cache)
    nocs = sorted(set(re.findall(r'href="/countries/([A-Z]{3})"', html)))
    return nocs


def fetch_country_edition(noc: str, edition_id: int) -> str:
    """Return HTML for a country's results at an edition."""
    cache = CACHE_DIR / f"countries/{edition_id}_{noc}.html"
    url = f"https://www.olympedia.org/countries/{noc}/editions/{edition_id}"
    return fetch(url, cache)


# ---------------------------------------------------------------------------
# HTML Parsing
# ---------------------------------------------------------------------------

def parse_country_page(html: str, noc: str) -> dict:
    """
    Parse an Olympedia country/edition page and return:
      Total_Athletes, Individual_Medalists,
      Gold, Silver, Bronze, Total,
      Gold_Medalists, Silver_Medalists, Bronze_Medalists,
      Gold_Awarded, Silver_Awarded, Bronze_Awarded,
      Total_Medals_Awarded

    HTML structure on Olympedia country/edition pages:
      - Sport header:  <tr><td colspan="4"><h2>Sport</h2></td></tr>
      - Individual:    <tr><td>event</td><td>athlete</td><td>pos</td><td>medal?</td></tr>
      - Continuation:  <tr><td></td><td>athlete</td><td>pos</td><td>medal?</td></tr>
      - Team result:   <tr><td>event</td><td>Country</td><td>pos</td><td>medal?</td></tr>
      - Team members:  <tr><td></td><td colspan="3">athletes •-separated</td></tr>

    NOTE: BeautifulSoup nests the team-member <tr> inside the team-result <tr>
    (because the source HTML lacks explicit </tr>).  The outer row therefore
    contains BOTH the medal span AND the athlete links.  We must detect this
    by checking for an event link FIRST, before the colspan-3 shortcut.
    """
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table", class_="table")
    if table is None:
        return _empty_result()

    all_athletes: set[str] = set()
    gold_medalists: set[str] = set()
    silver_medalists: set[str] = set()
    bronze_medalists: set[str] = set()
    gold_awarded = 0
    silver_awarded = 0
    bronze_awarded = 0
    country_gold = 0
    country_silver = 0
    country_bronze = 0

    rows = table.find_all("tr")
    pending_team_medal: str | None = None   # "Gold" / "Silver" / "Bronze"

    def _assign_medal(medal: str, athlete_ids: list[str]):
        """Add medal credit to each athlete."""
        nonlocal gold_awarded, silver_awarded, bronze_awarded
        for aid in athlete_ids:
            if medal == "Gold":
                gold_medalists.add(aid)
                gold_awarded += 1
            elif medal == "Silver":
                silver_medalists.add(aid)
                silver_awarded += 1
            elif medal == "Bronze":
                bronze_medalists.add(aid)
                bronze_awarded += 1

    def _count_country_medal(medal: str):
        nonlocal country_gold, country_silver, country_bronze
        if medal == "Gold":
            country_gold += 1
        elif medal == "Silver":
            country_silver += 1
        elif medal == "Bronze":
            country_bronze += 1

    for row in rows:
        tds = row.find_all("td")
        if not tds:
            continue

        # --- Sport header row (colspan=4 with <h2>) ---
        if tds[0].get("colspan") and tds[0].find("h2"):
            pending_team_medal = None
            continue

        # --- Extract features ---
        event_link = tds[0].find("a", href=re.compile(r"/results/"))
        medal_span = row.find("span", class_=re.compile(r"^(Gold|Silver|Bronze)$"))
        medal_type = medal_span.get("class")[0] if medal_span else None
        has_colspan3 = any(td.get("colspan") == "3" for td in tds)

        athlete_links = row.find_all("a", href=re.compile(r"/athletes/\d+"))
        athlete_ids = []
        for a in athlete_links:
            m = re.search(r"/athletes/(\d+)", a["href"])
            if m:
                athlete_ids.append(m.group(1))
        # De-duplicate while preserving order (same athlete link may appear
        # twice if BS4 nesting causes the nested <tr> athletes to also be
        # found in the parent).
        seen = set()
        unique_ids = []
        for aid in athlete_ids:
            if aid not in seen:
                seen.add(aid)
                unique_ids.append(aid)
        athlete_ids = unique_ids
        all_athletes.update(athlete_ids)

        # --- Decision tree ---
        if event_link:
            # PRIMARY ROW — new event entry
            pending_team_medal = None

            if medal_type:
                # 1 medal for the country tally
                _count_country_medal(medal_type)

                if athlete_ids:
                    # Athletes found (individual event, or team event where
                    # BS4 nested the member row inside this one).
                    _assign_medal(medal_type, athlete_ids)
                else:
                    # Team event header with no embedded athletes —
                    # expect a separate team-member row next.
                    pending_team_medal = medal_type
            # else: event row with no medal — just athletes counted above.

        elif medal_type:
            # CONTINUATION ROW WITH ITS OWN MEDAL — a second result for the
            # same country in the same event (e.g. Germany's 2nd bobsled
            # winning Silver while the 1st won Gold).
            _count_country_medal(medal_type)
            pending_team_medal = None

            if athlete_ids:
                _assign_medal(medal_type, athlete_ids)
            else:
                # Team continuation with medal but no embedded athletes;
                # next row should supply the team members.
                pending_team_medal = medal_type

        elif has_colspan3:
            # CONTINUATION — team-member row (no event link, no medal,
            # has colspan=3).  Inherits medal from pending state.
            if pending_team_medal and athlete_ids:
                _assign_medal(pending_team_medal, athlete_ids)
            pending_team_medal = None

        # else: non-medal continuation row (e.g., 4th-place finisher
        #       in a multi-athlete event). No action beyond athlete counting.

    country_total = country_gold + country_silver + country_bronze
    total_medals_awarded = gold_awarded + silver_awarded + bronze_awarded
    individual_medalists = gold_medalists | silver_medalists | bronze_medalists

    return {
        "Total_Athletes": len(all_athletes),
        "Individual_Medalists": len(individual_medalists),
        "Gold": country_gold,
        "Silver": country_silver,
        "Bronze": country_bronze,
        "Total": country_total,
        "Gold_Medalists": len(gold_medalists),
        "Silver_Medalists": len(silver_medalists),
        "Bronze_Medalists": len(bronze_medalists),
        "Total_Medals_Awarded": total_medals_awarded,
        "Gold_Awarded": gold_awarded,
        "Silver_Awarded": silver_awarded,
        "Bronze_Awarded": bronze_awarded,
    }


def _empty_result() -> dict:
    return {
        "Total_Athletes": 0,
        "Individual_Medalists": 0,
        "Gold": 0, "Silver": 0, "Bronze": 0, "Total": 0,
        "Gold_Medalists": 0, "Silver_Medalists": 0, "Bronze_Medalists": 0,
        "Total_Medals_Awarded": 0,
        "Gold_Awarded": 0, "Silver_Awarded": 0, "Bronze_Awarded": 0,
    }


# ---------------------------------------------------------------------------
# Medal-table cross-check from edition overview
# ---------------------------------------------------------------------------

def fetch_edition_medal_table(edition_id: int) -> dict[str, tuple[int, int, int, int]]:
    """
    Fetch the edition overview page and return medal table as
    {NOC: (Gold, Silver, Bronze, Total)}.
    """
    cache = CACHE_DIR / f"editions/{edition_id}_overview.html"
    url = f"https://www.olympedia.org/editions/{edition_id}"
    html = fetch(url, cache)
    soup = BeautifulSoup(html, "html.parser")

    medal_table: dict[str, tuple[int, int, int, int]] = {}

    # Find Medal table section - look for header
    h2s = soup.find_all("h2", string=re.compile(r"Medal table", re.I))
    if not h2s:
        return medal_table

    # The table follows the h2
    table = h2s[0].find_next("table")
    if table is None:
        return medal_table

    for row in table.find_all("tr"):
        tds = row.find_all("td")
        if len(tds) < 5:
            continue
        # Find NOC link
        noc_link = row.find("a", href=re.compile(r"/countries/[A-Z]{3}"))
        if not noc_link:
            continue
        noc = re.search(r"/countries/([A-Z]{3})", noc_link["href"]).group(1)
        try:
            g = int(tds[-4].get_text(strip=True))
            s = int(tds[-3].get_text(strip=True))
            b = int(tds[-2].get_text(strip=True))
            t = int(tds[-1].get_text(strip=True))
            medal_table[noc] = (g, s, b, t)
        except (ValueError, IndexError):
            continue

    return medal_table


# ---------------------------------------------------------------------------
# Main scraping loop
# ---------------------------------------------------------------------------

def scrape_edition(edition_id: int, year: int, city: str, season: str,
                   medal_table: dict | None = None) -> list[dict]:
    """Scrape all countries for one edition. Returns list of row dicts."""
    nocs = fetch_countries_for_edition(edition_id)
    print(f"    {len(nocs)} countries")

    rows = []
    for i, noc in enumerate(nocs, 1):
        try:
            html = fetch_country_edition(noc, edition_id)
            parsed = parse_country_page(html, noc)
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                # Country page doesn't exist for this edition
                parsed = _empty_result()
            else:
                print(f"      ERROR {noc}: {e}")
                parsed = _empty_result()
        except Exception as e:
            print(f"      ERROR {noc}: {e}")
            parsed = _empty_result()

        row = {"Year": year, "Country": noc, **parsed}
        rows.append(row)

        # Progress indicator every 20 countries
        if i % 20 == 0:
            cached = (CACHE_DIR / f"countries/{edition_id}_{noc}.html").exists()
            status = "cached" if cached else "fetched"
            print(f"      {i}/{len(nocs)} ({status})")

    # Cross-check medal tally against official table
    if medal_table:
        mismatches = []
        for noc, (eg, es, eb, et) in medal_table.items():
            country_rows = [r for r in rows if r["Country"] == noc]
            if not country_rows:
                mismatches.append(f"{noc}: not in our list")
                continue
            cr = country_rows[0]
            if (cr["Gold"], cr["Silver"], cr["Bronze"], cr["Total"]) != (eg, es, eb, et):
                mismatches.append(
                    f"{noc}: parsed={cr['Gold']}/{cr['Silver']}/{cr['Bronze']}/{cr['Total']} "
                    f"expected={eg}/{es}/{eb}/{et}"
                )
        if mismatches:
            print(f"    ⚠ Medal tally mismatches:")
            for m in mismatches[:10]:
                print(f"      {m}")
            if len(mismatches) > 10:
                print(f"      ... and {len(mismatches) - 10} more")
        else:
            print(f"    ✓ Medal tally matches official table")

    return rows


def main():
    parser = argparse.ArgumentParser(description="Scrape Olympedia data")
    parser.add_argument("--season", choices=["summer", "winter"], default=None,
                        help="Scrape only summer or winter")
    parser.add_argument("--edition", type=int, default=None,
                        help="Scrape only a specific edition ID")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show plan without fetching")
    parser.add_argument("--skip-medal-check", action="store_true",
                        help="Skip fetching edition overview for medal cross-check")
    parser.add_argument("--min-year", type=int, default=None,
                        help="Only scrape editions from this year onward")
    parser.add_argument("--max-year", type=int, default=None,
                        help="Only scrape editions up to this year")
    args = parser.parse_args()

    # Filter editions
    editions_to_scrape = {}
    for eid, (year, city, season) in sorted(EDITIONS.items(), key=lambda x: (x[1][2], x[1][0])):
        if args.edition and eid != args.edition:
            continue
        if args.season and season.lower() != args.season:
            continue
        if args.min_year and year < args.min_year:
            continue
        if args.max_year and year > args.max_year:
            continue
        editions_to_scrape[eid] = (year, city, season)

    print(f"Olympedia Scraper — {len(editions_to_scrape)} editions to process")
    print(f"Cache directory: {CACHE_DIR}")
    print()

    if args.dry_run:
        for eid, (year, city, season) in sorted(editions_to_scrape.items(),
                                                  key=lambda x: (x[1][2], x[1][0])):
            print(f"  Edition {eid:>3}: {year} {season} - {city}")
        return

    # Scrape
    summer_rows = []
    winter_rows = []

    total_editions = len(editions_to_scrape)
    for idx, (eid, (year, city, season)) in enumerate(
        sorted(editions_to_scrape.items(), key=lambda x: (x[1][2], x[1][0])), 1
    ):
        print(f"[{idx}/{total_editions}] {year} {season} Olympics ({city}) — edition {eid}")

        # Optionally fetch medal table for cross-check
        medal_table = None
        if not args.skip_medal_check:
            try:
                medal_table = fetch_edition_medal_table(eid)
            except Exception as e:
                print(f"    Warning: could not fetch medal table: {e}")

        rows = scrape_edition(eid, year, city, season, medal_table)

        if season == "Summer":
            summer_rows.extend(rows)
        else:
            winter_rows.extend(rows)

        print()

    # Write CSVs
    _write_csv(summer_rows, DATA_DIR / "olympedia_summer.csv", "Summer")
    _write_csv(winter_rows, DATA_DIR / "olympedia_winter.csv", "Winter")

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    if summer_rows:
        print(f"  Summer: {len(summer_rows)} rows across "
              f"{len(set(r['Year'] for r in summer_rows))} editions")
    if winter_rows:
        print(f"  Winter: {len(winter_rows)} rows across "
              f"{len(set(r['Year'] for r in winter_rows))} editions")
    print(f"  Cache: {CACHE_DIR}")


COLUMNS = [
    "Year", "Country",
    "Gold", "Silver", "Bronze", "Total",
    "Total_Athletes", "Individual_Medalists",
    "Gold_Medalists", "Silver_Medalists", "Bronze_Medalists",
    "Total_Medals_Awarded", "Gold_Awarded", "Silver_Awarded", "Bronze_Awarded",
]


def _write_csv(rows: list[dict], path: Path, label: str):
    if not rows:
        print(f"  {label}: no data to write")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for row in sorted(rows, key=lambda r: (r["Year"], r["Country"])):
            writer.writerow({k: row.get(k, 0) for k in COLUMNS})
    print(f"  {label}: wrote {len(rows)} rows → {path}")


if __name__ == "__main__":
    main()
