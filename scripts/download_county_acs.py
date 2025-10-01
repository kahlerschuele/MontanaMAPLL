#!/usr/bin/env python3
"""
Download ACS demographic data for Montana counties and join to county GeoJSON
"""

import json
import urllib.request
import geopandas as gpd
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
TIGER_DIR = BASE_DIR / "data" / "tiger"
FRONTEND_TIGER_DIR = BASE_DIR / "frontend" / "public" / "data" / "tiger"

# ACS API configuration
ACS_BASE_URL = "https://api.census.gov/data/2022/acs/acs5"

# ACS variables to download (county level)
ACS_VARIABLES = {
    'B01003_001E': 'total_population',
    'B01002_001E': 'median_age',
    'B19013_001E': 'median_household_income',
    'B19301_001E': 'per_capita_income',
    'B25001_001E': 'total_housing_units',
    'B25003_002E': 'owner_occupied_housing',
    'B25003_003E': 'renter_occupied_housing',
    'B25077_001E': 'median_home_value',
    'B25064_001E': 'median_gross_rent',
    'B17001_002E': 'poverty_count',
    'B23025_002E': 'in_labor_force',
    'B23025_004E': 'employed',
    'B23025_005E': 'unemployed',
    'B02001_002E': 'white_alone',
    'B02001_003E': 'black_alone',
    'B02001_004E': 'native_american_alone',
    'B02001_005E': 'asian_alone',
    'B03003_003E': 'hispanic_or_latino',
    'B15003_022E': 'bachelors_degree',
    'B15003_023E': 'masters_degree',
    'B15003_025E': 'doctorate_degree'
}

def download_acs_county_data():
    """Download ACS data for all Montana counties"""
    print("Downloading ACS county data from Census API...")

    # Build API query
    var_list = ','.join(ACS_VARIABLES.keys())
    url = f"{ACS_BASE_URL}?get=NAME,{var_list}&for=county:*&in=state:30"

    print(f"Fetching: {url[:100]}...")

    # Download data
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())

    # Convert to dictionary with county FIPS as key
    headers = data[0]
    county_data = {}

    for row in data[1:]:
        row_dict = dict(zip(headers, row))

        # Build GEOID (state + county FIPS)
        geoid = row_dict['state'] + row_dict['county']

        # Map variable codes to readable names
        county_info = {
            'NAME': row_dict['NAME'],
            'GEOID': geoid
        }

        for var_code, var_name in ACS_VARIABLES.items():
            value = row_dict.get(var_code)
            # Convert to number, handle nulls and negatives (Census uses -666666666 for N/A)
            try:
                num_value = float(value) if value and float(value) > 0 else None
            except (ValueError, TypeError):
                num_value = None
            county_info[var_name] = num_value

        # Calculate derived metrics
        if county_info['total_population'] and county_info['poverty_count']:
            county_info['poverty_rate'] = round(
                (county_info['poverty_count'] / county_info['total_population']) * 100, 1
            )
        else:
            county_info['poverty_rate'] = None

        if county_info['in_labor_force'] and county_info['unemployed']:
            county_info['unemployment_rate'] = round(
                (county_info['unemployed'] / county_info['in_labor_force']) * 100, 1
            )
        else:
            county_info['unemployment_rate'] = None

        county_data[geoid] = county_info

    print(f"Downloaded data for {len(county_data)} Montana counties")
    return county_data

def join_to_counties(county_data):
    """Join ACS data to county GeoJSON"""
    print("Joining ACS data to county boundaries...")

    # Read county GeoJSON
    county_file = TIGER_DIR / "mt_counties.geojson"
    gdf = gpd.read_file(county_file)

    print(f"Loaded {len(gdf)} county features")

    # Join ACS data
    for idx, row in gdf.iterrows():
        geoid = row['GEOID']
        if geoid in county_data:
            acs_info = county_data[geoid]
            # Add all ACS fields to the GeoDataFrame
            for key, value in acs_info.items():
                if key not in ['GEOID', 'NAME']:  # Skip duplicates
                    gdf.at[idx, key] = value

    # Save to both locations
    output_file = TIGER_DIR / "mt_counties_acs.geojson"
    gdf.to_file(output_file, driver='GeoJSON')
    print(f"Saved: {output_file}")

    # Also save to frontend
    frontend_output = FRONTEND_TIGER_DIR / "mt_counties_acs.geojson"
    frontend_output.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(frontend_output, driver='GeoJSON')
    print(f"Saved: {frontend_output}")

    # Print sample
    print("\nSample county data:")
    sample = gdf.iloc[0]
    print(f"  County: {sample['NAME']}")
    print(f"  Population: {sample.get('total_population', 'N/A')}")
    print(f"  Median Income: ${sample.get('median_household_income', 'N/A')}")
    print(f"  Median Age: {sample.get('median_age', 'N/A')}")

if __name__ == '__main__':
    print("=" * 60)
    print("Montana County ACS Data Download")
    print("=" * 60)

    # Download ACS data
    county_data = download_acs_county_data()

    # Join to GeoJSON
    join_to_counties(county_data)

    print("\nDone! County demographics ready.")
    print(f"Output: {TIGER_DIR / 'mt_counties_acs.geojson'}")
