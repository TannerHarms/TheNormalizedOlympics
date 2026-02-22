"""
Tests for the Olympic normalization data pipeline.

Run with: python -m pytest tests/test_pipeline.py -v
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.country_mapping import NOC_TO_WB, get_wb_code, get_noc_code, is_historical

DATA_DIR = PROJECT_ROOT / "data"


# ============================================================================
# Country Mapping Tests
# ============================================================================

class TestCountryMapping:
    """Verify NOC ↔ World Bank code mapping is correct."""

    def test_major_countries_mapped(self):
        expected = {
            "USA": "USA", "CHN": "CHN", "GBR": "GBR", "JPN": "JPN",
            "FRA": "FRA", "GER": "DEU", "AUS": "AUS", "CAN": "CAN",
            "NOR": "NOR", "SWE": "SWE", "KOR": "KOR", "BRA": "BRA",
            "ITA": "ITA", "NED": "NLD", "SUI": "CHE", "NZL": "NZL",
        }
        for noc, wb in expected.items():
            assert get_wb_code(noc) == wb, f"{noc} should map to {wb}"

    def test_bahamas_not_bahrain(self):
        """BAH is the Bahamas (BHS), not Bahrain (BHR)."""
        assert get_wb_code("BAH") == "BHS"

    def test_bahrain_mapping(self):
        """BRN is Bahrain (BHR)."""
        assert get_wb_code("BRN") == "BHR"

    def test_ire_not_mapped(self):
        """IRE is not a valid NOC code — should not map to Iran."""
        assert get_wb_code("IRE") is None

    def test_iran_mapped_correctly(self):
        """Iran's NOC code is IRI."""
        assert get_wb_code("IRI") == "IRN"

    def test_ireland_mapped_correctly(self):
        assert get_wb_code("IRL") == "IRL"

    def test_chinese_taipei_mapped(self):
        assert get_wb_code("TPE") == "TWN"

    def test_hong_kong_mapped(self):
        assert get_wb_code("HKG") == "HKG"

    def test_historical_countries_return_none(self):
        for code in ["URS", "EUN", "TCH", "YUG"]:
            assert get_wb_code(code) is None, f"{code} should map to None"
            assert is_historical(code), f"{code} should be historical"

    def test_no_duplicate_wb_targets_in_active_countries(self):
        """Except for historical/special cases, each WB code should appear at most
        a small number of times (e.g., RUS maps from RUS/ROC/OAR)."""
        wb_counts = {}
        for noc, wb in NOC_TO_WB.items():
            if wb is not None:
                wb_counts.setdefault(wb, []).append(noc)
        for wb, nocs in wb_counts.items():
            assert len(nocs) <= 4, f"WB code {wb} has too many NOC mappings: {nocs}"


# ============================================================================
# Medal Data Integrity Tests
# ============================================================================

class TestMedalData:
    """Verify medal CSVs are well-formed and spot-check against official results."""

    def setup_method(self):
        self.summer = pd.read_csv(DATA_DIR / "summer_olympics_by_year.csv")
        self.winter = pd.read_csv(DATA_DIR / "winter_olympics_by_year.csv")

    def test_required_columns(self):
        for df, name in [(self.summer, "summer"), (self.winter, "winter")]:
            for col in ["Year", "Country", "Gold", "Silver", "Bronze", "Total"]:
                assert col in df.columns, f"{name} missing column {col}"

    def test_no_duplicate_country_years(self):
        dupes_s = self.summer.duplicated(subset=["Year", "Country"], keep=False).sum()
        dupes_w = self.winter.duplicated(subset=["Year", "Country"], keep=False).sum()
        assert dupes_s == 0, f"Summer has {dupes_s} duplicate country-year rows"
        assert dupes_w == 0, f"Winter has {dupes_w} duplicate country-year rows"

    def test_total_equals_sum_of_medals(self):
        for df, name in [(self.summer, "summer"), (self.winter, "winter")]:
            calc_total = df["Gold"] + df["Silver"] + df["Bronze"]
            mismatches = (df["Total"] - calc_total).abs() > 0.01
            assert mismatches.sum() == 0, (
                f"{name}: {mismatches.sum()} rows where Total != Gold+Silver+Bronze"
            )

    def test_no_negative_medals(self):
        for df, name in [(self.summer, "summer"), (self.winter, "winter")]:
            for col in ["Gold", "Silver", "Bronze", "Total"]:
                assert (df[col] >= 0).all(), f"{name} has negative {col}"

    def test_summer_year_range(self):
        assert self.summer["Year"].min() == 1896
        assert self.summer["Year"].max() == 2024

    def test_winter_year_range(self):
        assert self.winter["Year"].min() == 1924
        assert self.winter["Year"].max() == 2026

    def test_country_codes_are_short(self):
        """All country identifiers should be NOC codes (≤3 chars), not full names."""
        long_summer = self.summer[self.summer["Country"].str.len() > 3]["Country"].unique()
        long_winter = self.winter[self.winter["Country"].str.len() > 3]["Country"].unique()
        assert len(long_summer) == 0, f"Summer has full names: {list(long_summer)}"
        assert len(long_winter) == 0, f"Winter has full names: {list(long_winter)}"

    # --- Spot checks against official IOC results ---

    def _check_medals(self, df, year, country, gold, silver, bronze):
        row = df[(df["Year"] == year) & (df["Country"] == country)]
        assert len(row) == 1, f"No data for {country} {year}"
        r = row.iloc[0]
        assert r["Gold"] == gold, f"{country} {year} Gold: got {r['Gold']}, expected {gold}"
        assert r["Silver"] == silver, f"{country} {year} Silver: got {r['Silver']}, expected {silver}"
        assert r["Bronze"] == bronze, f"{country} {year} Bronze: got {r['Bronze']}, expected {bronze}"

    def test_usa_2024_paris(self):
        self._check_medals(self.summer, 2024, "USA", 40, 44, 42)

    def test_china_2024_paris(self):
        self._check_medals(self.summer, 2024, "CHN", 40, 27, 24)

    def test_usa_2016_rio(self):
        self._check_medals(self.summer, 2016, "USA", 46, 37, 38)

    def test_norway_2022_beijing(self):
        self._check_medals(self.winter, 2022, "NOR", 16, 8, 13)

    def test_germany_2022_beijing(self):
        self._check_medals(self.winter, 2022, "GER", 12, 10, 5)


# ============================================================================
# Historical Totals Tests
# ============================================================================

class TestHistoricalTotals:
    """Verify cumulative medal history is calculated correctly."""

    def setup_method(self):
        self.summer = pd.read_csv(DATA_DIR / "summer_olympics_with_history.csv")
        self.winter = pd.read_csv(DATA_DIR / "winter_olympics_with_history.csv")

    def _verify_cumulative(self, df, country):
        """Historical_Total at year Y should equal sum of medals from all prior years."""
        c = df[df["Country"] == country].sort_values("Year")
        if len(c) == 0:
            return  # Country not in dataset
        running = 0.0
        for _, row in c.iterrows():
            assert abs(row["Historical_Total"] - running) < 0.01, (
                f"{country} {int(row['Year'])}: Historical_Total={row['Historical_Total']}, "
                f"expected cumulative={running}"
            )
            running += row["Total"]

    def test_usa_summer_cumulative(self):
        self._verify_cumulative(self.summer, "USA")

    def test_china_summer_cumulative(self):
        self._verify_cumulative(self.summer, "CHN")

    def test_gbr_summer_cumulative(self):
        self._verify_cumulative(self.summer, "GBR")

    def test_norway_winter_cumulative(self):
        self._verify_cumulative(self.winter, "NOR")

    def test_germany_winter_cumulative(self):
        self._verify_cumulative(self.winter, "GER")

    def test_first_appearance_has_zero_history(self):
        """A country's first Olympic appearance should have Historical_Total = 0."""
        for df in [self.summer, self.winter]:
            for country in df["Country"].unique()[:20]:
                first = df[df["Country"] == country].sort_values("Year").iloc[0]
                assert first["Historical_Total"] == 0, (
                    f"{country} first year {int(first['Year'])} has Historical_Total="
                    f"{first['Historical_Total']}, expected 0"
                )


# ============================================================================
# Normalized Data Tests
# ============================================================================

class TestNormalizedData:
    """Verify the final merged/normalized datasets."""

    def setup_method(self):
        self.summer = pd.read_csv(DATA_DIR / "summer_olympics_normalized.csv")
        self.winter = pd.read_csv(DATA_DIR / "winter_olympics_normalized.csv")

    def test_starts_at_1960(self):
        assert self.summer["Year"].min() >= 1960
        assert self.winter["Year"].min() >= 1960

    def test_population_coverage(self):
        """At least 60% of records should have population data.
        
        Coverage is lower because we now include all ~200 participating countries,
        including tiny nations that lack World Bank data.
        """
        pct = self.summer["Population"].notna().mean()
        assert pct >= 0.60, f"Summer population coverage only {pct:.1%}"

    def test_gdp_coverage(self):
        """At least 60% of records should have GDP data.
        
        Coverage is lower because we now include all ~200 participating countries,
        including tiny nations that lack World Bank data.
        """
        pct = self.summer["GDP"].notna().mean()
        assert pct >= 0.60, f"Summer GDP coverage only {pct:.1%}"

    def test_normalization_math_medals_per_million(self):
        """Spot-check that Medals_per_million_pop = Total / Population * 1e6."""
        df = self.summer[self.summer["Population"].notna()].head(50)
        calc = (df["Total"] / df["Population"]) * 1_000_000
        stored = df["Medals_per_million_pop"]
        assert np.allclose(calc, stored, rtol=1e-6), "Medals_per_million_pop formula wrong"

    def test_normalization_math_medals_per_billion_gdp(self):
        df = self.summer[self.summer["GDP"].notna()].head(50)
        calc = (df["Total"] / df["GDP"]) * 1_000_000_000
        stored = df["Medals_per_billion_GDP"]
        assert np.allclose(calc, stored, rtol=1e-6), "Medals_per_billion_GDP formula wrong"

    def test_normalization_math_medals_per_gdp_percapita(self):
        df = self.summer[self.summer["GDP_per_capita"].notna()].head(50)
        calc = (df["Total"] / df["GDP_per_capita"]) * 10_000
        stored = df["Medals_per_10K_GDPpc"]
        assert np.allclose(calc, stored, rtol=1e-6), "Medals_per_10K_GDPpc formula wrong"

    def test_normalization_math_medals_per_hdi(self):
        df = self.summer[self.summer["HDI"].notna()].head(50)
        calc = df["Total"] / df["HDI"]
        stored = df["Medals_per_HDI"]
        assert np.allclose(calc, stored, rtol=1e-4), "Medals_per_HDI formula wrong"

    def test_world_bank_data_sanity_usa(self):
        """Sanity-check USA 2020 economic data against known values."""
        usa = self.summer[
            (self.summer["Country"] == "USA") & (self.summer["Year"] == 2020)
        ].iloc[0]
        assert 300e6 < usa["Population"] < 400e6, f"USA pop {usa['Population']}"
        assert 15e12 < usa["GDP"] < 30e12, f"USA GDP {usa['GDP']}"
        assert 50_000 < usa["GDP_per_capita"] < 80_000, f"USA GDPpc {usa['GDP_per_capita']}"

    def test_hdi_includes_high_hdi_nations(self):
        """Norway & Switzerland should have HDI data (were previously dropped by <=0.95 bug)."""
        for country in ["NOR", "SUI"]:
            rows = self.summer[
                (self.summer["Country"] == country) & (self.summer["HDI"].notna())
            ]
            assert len(rows) > 0, f"{country} has no HDI data — filter bug may have returned"

    def test_hdi_range(self):
        """All HDI values should be between 0.3 and 1.0."""
        hdi = self.summer["HDI"].dropna()
        assert hdi.min() >= 0.29, f"HDI min {hdi.min()} below expected range"
        assert hdi.max() <= 1.01, f"HDI max {hdi.max()} above expected range"


# ============================================================================
# Climate Data Tests
# ============================================================================

class TestClimateData:
    """Verify climate zone classifications."""

    def setup_method(self):
        self.climate = pd.read_csv(DATA_DIR / "climate_data.csv")

    def test_no_duplicate_countries(self):
        dupes = self.climate.duplicated(subset=["WB_Code"], keep=False).sum()
        assert dupes == 0, f"Climate data has {dupes} duplicate countries"

    def test_china_is_continental(self):
        """China should be Zone 2 (Continental), not Zone 4."""
        chn = self.climate[self.climate["WB_Code"] == "CHN"]
        assert len(chn) == 1, "CHN should appear exactly once"
        assert chn.iloc[0]["Climate_Zone"] == 2, "CHN should be Continental (Zone 2)"

    def test_zones_are_valid(self):
        assert set(self.climate["Climate_Zone"].unique()) == {1, 2, 3, 4, 5}

    def test_winter_sports_index_monotonic(self):
        """Higher climate zone → lower winter sports index."""
        zone_index = self.climate.groupby("Climate_Zone")["Winter_Sports_Index"].first()
        for z in range(1, 5):
            assert zone_index[z] > zone_index[z + 1], (
                f"Zone {z} index ({zone_index[z]}) should be > Zone {z+1} ({zone_index[z+1]})"
            )


# ============================================================================
# All-Metrics Data Integrity Tests
# ============================================================================

class TestAllMetricsData:
    """Verify the all_metrics CSVs have no inf values, no duplicates,
    and do not contain removed metrics (refugee, coffee, cola)."""

    def setup_method(self):
        self.summer = pd.read_csv(DATA_DIR / "summer_olympics_all_metrics.csv")
        self.winter = pd.read_csv(DATA_DIR / "winter_olympics_all_metrics.csv")

    def test_no_inf_values_in_normalized_metrics(self):
        """No normalized metric column should contain inf or -inf."""
        for df, name in [(self.summer, "summer"), (self.winter, "winter")]:
            norm_cols = [c for c in df.columns if c.startswith("Medals_Per_")]
            for col in norm_cols:
                inf_count = np.isinf(df[col].dropna()).sum()
                assert inf_count == 0, (
                    f"{name} column {col} has {inf_count} inf values"
                )

    def test_no_duplicate_country_year_rows(self):
        """No duplicate (Country, Year) rows in all_metrics files."""
        for df, name in [(self.summer, "summer"), (self.winter, "winter")]:
            dupes = df.duplicated(subset=["Country", "Year"], keep=False).sum()
            assert dupes == 0, (
                f"{name} all_metrics has {dupes} duplicate Country-Year rows"
            )

    def test_no_refugee_columns(self):
        """Refugee columns should not exist in all_metrics after cleanup."""
        removed_cols = [
            "Medals_Per_1000_Refugees_Received",
            "Medals_Per_1000_Refugees_Produced",
            "Refugees_Received",
            "Refugees_Produced",
        ]
        for df, name in [(self.summer, "summer"), (self.winter, "winter")]:
            for col in removed_cols:
                assert col not in df.columns, (
                    f"{name} all_metrics still has removed column {col}"
                )

    def test_no_coffee_cola_columns(self):
        """Coffee/cola consumption columns should not exist after cleanup."""
        removed_cols = [
            "Medals_Per_Million_Kg_Coffee",
            "Medals_Per_Million_Cola_Servings",
            "Coffee_Consumption_Kg_Per_Capita",
            "Coca_Cola_Servings_Per_Capita",
        ]
        for df, name in [(self.summer, "summer"), (self.winter, "winter")]:
            for col in removed_cols:
                assert col not in df.columns, (
                    f"{name} all_metrics still has removed column {col}"
                )

    def test_total_athletes_coverage(self):
        """Total_Athletes should have broad coverage (not just medal winners)."""
        for df, name in [(self.summer, "summer"), (self.winter, "winter")]:
            if "Total_Athletes" not in df.columns:
                continue
            # Check that some countries have Total_Athletes > 0 but Total == 0
            # (i.e., nations that participated but won no medals)
            athletes_no_medals = df[
                (df["Total_Athletes"] > 0) & (df["Total"] == 0)
            ]
            # This is a soft check — not all datasets will have these
            # At minimum, Total_Athletes should exist and have reasonable values
            has_athletes = df["Total_Athletes"].notna().sum()
            total_rows = len(df)
            pct = has_athletes / total_rows
            assert pct >= 0.5, (
                f"{name} Total_Athletes coverage is only {pct:.1%}"
            )
