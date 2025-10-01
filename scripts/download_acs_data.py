#!/usr/bin/env python3
"""
Download US Census ACS (American Community Survey) data for Montana
Enriches TIGER tract data with demographics
"""

import urllib.request
import json
import geopandas as gpd
from pathlib import Path

# Montana FIPS
MONTANA_FIPS = "30"
YEAR = "2022"  # Latest 5-year ACS
DATASET = "acs5"

# ACS API endpoint
ACS_BASE = f"https://api.census.gov/data/{YEAR}/acs/{DATASET}"

# Variables to download (Census variable codes)
# See: https://api.census.gov/data/2022/acs/acs5/variables.html
ACS_VARIABLES = {
    # Demographics
    "B01003_001E": "total_population",
    "B01002_001E": "median_age",

    # Race/Ethnicity
    "B02001_002E": "white_alone",
    "B02001_003E": "black_alone",
    "B02001_004E": "native_american_alone",
    "B02001_005E": "asian_alone",
    "B03003_003E": "hispanic_latino",

    # Housing
    "B25001_001E": "total_housing_units",
    "B25002_002E": "occupied_housing_units",
    "B25002_003E": "vacant_housing_units",
    "B25077_001E": "median_home_value",
    "B25064_001E": "median_gross_rent",

    # Economics
    "B19013_001E": "median_household_income",
    "B19301_001E": "per_capita_income",
    "B17001_002E": "poverty_count",

    # Education
    "B15003_022E": "bachelors_degree",
    "B15003_023E": "masters_degree",
    "B15003_025E": "doctorate_degree",

    # Employment
    "B23025_003E": "in_labor_force",
    "B23025_004E": "employed",
    "B23025_005E": "unemployed"
}

def download_acs_data(geography, geo_filter):
    """
    Download ACS data from Census API

    Args:
        geography: "tract" or "block group"
        geo_filter: Geographic filter (e.g., "state:30")
    """
    var_list = ",".join(ACS_VARIABLES.keys())

    url = f"{ACS_BASE}?get=NAME,{var_list}&for={geography}:*&in={geo_filter}"

    print(f"Fetching ACS data for {geography}...")
    print(f"URL: {url[:100]}...")

    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
    except Exception as e:
        print(f"ERROR: Failed to fetch ACS data: {e}")
        return None

    # Parse response
    headers = data[0]
    rows = data[1:]

    print(f"Downloaded {len(rows)} records")

    # Convert to dictionary format
    records = []
    for row in rows:
        record = {}
        for i, header in enumerate(headers):
            value = row[i]

            # Build GEOID
            if header == "state":
                record["state_fips"] = value
            elif header == "county":
                record["county_fips"] = value
            elif header == "tract":
                record["tract_fips"] = value
            elif header == "block group":
                record["bg_fips"] = value
            elif header == "NAME":
                record["name"] = value
            elif header in ACS_VARIABLES:
                # Rename to friendly name and convert to number
                friendly_name = ACS_VARIABLES[header]
                try:
                    record[friendly_name] = int(value) if value and value != "-666666666" else None
                except ValueError:
                    record[friendly_name] = None

        # Build GEOID (standard Census identifier)
        if "state_fips" in record and "county_fips" in record and "tract_fips" in record:
            geoid = record["state_fips"] + record["county_fips"] + record["tract_fips"]
            if "bg_fips" in record:
                geoid += record["bg_fips"]
            record["GEOID"] = geoid

        records.append(record)

    return records

def enrich_geojson(geojson_path, acs_records, output_path):
    """Join ACS data to GeoJSON by GEOID"""

    print(f"\nLoading {geojson_path.name}...")
    gdf = gpd.read_file(geojson_path)
    print(f"Features: {len(gdf)}")

    # Convert ACS records to dict by GEOID
    acs_dict = {r["GEOID"]: r for r in acs_records if "GEOID" in r}
    print(f"ACS records with GEOID: {len(acs_dict)}")

    # Add ACS columns to GeoDataFrame
    for col in ACS_VARIABLES.values():
        gdf[col] = None

    # Join by GEOID
    matched = 0
    for idx, row in gdf.iterrows():
        geoid = row.get("GEOID")
        if geoid and geoid in acs_dict:
            acs_data = acs_dict[geoid]
            for col in ACS_VARIABLES.values():
                if col in acs_data:
                    gdf.at[idx, col] = acs_data[col]
            matched += 1

    print(f"Matched {matched}/{len(gdf)} features with ACS data")

    # Calculate derived fields (handle division by zero)
    if "total_population" in gdf.columns and "poverty_count" in gdf.columns:
        gdf["poverty_rate"] = gdf.apply(
            lambda row: round(row["poverty_count"] / row["total_population"] * 100, 2)
            if row["total_population"] and row["total_population"] > 0 else None,
            axis=1
        )

    if "unemployed" in gdf.columns and "in_labor_force" in gdf.columns:
        gdf["unemployment_rate"] = gdf.apply(
            lambda row: round(row["unemployed"] / row["in_labor_force"] * 100, 2)
            if row["in_labor_force"] and row["in_labor_force"] > 0 else None,
            axis=1
        )

    # Save enriched GeoJSON
    print(f"Saving enriched data to {output_path.name}...")
    gdf.to_file(output_path, driver='GeoJSON')

    file_size = output_path.stat().st_size / 1024
    print(f"SUCCESS: {file_size:.1f} KB")

    return gdf

def main():
    project_root = Path(__file__).parent.parent
    tiger_dir = project_root / "data" / "tiger"

    print("=" * 60)
    print("ACS Data Download and Enrichment for Montana")
    print("=" * 60)
    print(f"Year: {YEAR}")
    print(f"Dataset: {DATASET}")
    print(f"Variables: {len(ACS_VARIABLES)}")

    # Download ACS data for census tracts
    print("\n" + "=" * 60)
    print("CENSUS TRACTS")
    print("=" * 60)

    tract_acs = download_acs_data("tract", f"state:{MONTANA_FIPS}")

    if tract_acs:
        # Enrich tract GeoJSON
        tract_geojson = tiger_dir / "mt_tracts.geojson"
        if tract_geojson.exists():
            enriched_tracts = tiger_dir / "mt_tracts_acs.geojson"
            enrich_geojson(tract_geojson, tract_acs, enriched_tracts)
        else:
            print(f"WARNING: {tract_geojson.name} not found")
            print("Run download_tiger_montana.py first")

    # Download ACS data for block groups
    print("\n" + "=" * 60)
    print("BLOCK GROUPS")
    print("=" * 60)

    bg_acs = download_acs_data("block group", f"state:{MONTANA_FIPS}")

    if bg_acs:
        # Enrich block group GeoJSON
        bg_geojson = tiger_dir / "mt_blockgroups.geojson"
        if bg_geojson.exists():
            enriched_bg = tiger_dir / "mt_blockgroups_acs.geojson"
            enrich_geojson(bg_geojson, bg_acs, enriched_bg)
        else:
            print(f"WARNING: {bg_geojson.name} not found")
            print("Run download_tiger_montana.py first")

    # Summary
    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print("\nEnriched files:")
    for filename in ["mt_tracts_acs.geojson", "mt_blockgroups_acs.geojson"]:
        path = tiger_dir / filename
        if path.exists():
            size = path.stat().st_size / 1024
            print(f"  ✓ {filename} ({size:.1f} KB)")

    print("\nNext steps:")
    print("1. Update frontend to load enriched GeoJSON files")
    print("2. Add choropleth styling based on ACS variables")
    print("3. Add tooltips showing demographic data")

if __name__ == "__main__":
    main()
