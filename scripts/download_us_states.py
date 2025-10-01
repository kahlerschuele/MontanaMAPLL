#!/usr/bin/env python3
"""
Download US state boundaries from Census Bureau TIGER/Line
"""

import urllib.request
import zipfile
import geopandas as gpd
from pathlib import Path
import shutil

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "tiger"
FRONTEND_DATA_DIR = BASE_DIR / "frontend" / "public" / "data" / "tiger"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Census Bureau TIGER/Line URL for state boundaries (500k resolution - good for overview)
STATES_URL = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_state_500k.zip"

def download_states():
    """Download and process US state boundaries"""
    print("=" * 60)
    print("Downloading US State Boundaries")
    print("=" * 60)

    # Download zip file
    zip_path = DATA_DIR / "us_states.zip"
    print(f"\nDownloading from Census Bureau...")
    print(f"URL: {STATES_URL}")

    urllib.request.urlretrieve(STATES_URL, zip_path)
    print(f"[OK] Downloaded to {zip_path}")

    # Extract zip
    extract_dir = DATA_DIR / "us_states_temp"
    extract_dir.mkdir(exist_ok=True)

    print(f"\nExtracting...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"[OK] Extracted to {extract_dir}")

    # Find the shapefile
    shp_files = list(extract_dir.glob("*.shp"))
    if not shp_files:
        print("ERROR: No shapefile found in download")
        return

    shp_file = shp_files[0]
    print(f"\nReading shapefile: {shp_file.name}")

    # Read with geopandas
    gdf = gpd.read_file(shp_file)
    print(f"[OK] Loaded {len(gdf)} state/territory features")

    # Show what we have
    print(f"\nFields: {list(gdf.columns)}")
    print(f"\nFirst few states:")
    for idx, row in gdf.head(10).iterrows():
        print(f"  - {row['NAME']} ({row['STUSPS']})")

    # Filter to exclude territories if desired (optional)
    # Uncomment to only include 50 states + DC
    # state_fips = [str(i).zfill(2) for i in range(1, 57) if i not in [3, 7, 11, 14, 43, 52]]
    # gdf = gdf[gdf['STATEFP'].isin(state_fips)]
    # print(f"\n[OK] Filtered to {len(gdf)} US states (excluding territories)")

    # Save as GeoJSON
    output_file = DATA_DIR / "us_states.geojson"
    gdf.to_file(output_file, driver='GeoJSON')
    print(f"\n[OK] Saved to {output_file}")
    print(f"  File size: {output_file.stat().st_size / 1024:.1f} KB")

    # Also save to frontend
    frontend_output = FRONTEND_DATA_DIR / "us_states.geojson"
    gdf.to_file(frontend_output, driver='GeoJSON')
    print(f"[OK] Saved to {frontend_output}")

    # Clean up
    shutil.rmtree(extract_dir)
    zip_path.unlink()
    print(f"\n[OK] Cleaned up temporary files")

    print("\n" + "=" * 60)
    print("SUCCESS: US state boundaries ready")
    print("=" * 60)
    print(f"\nTotal states/territories: {len(gdf)}")
    print(f"Output: {output_file}")
    print(f"Frontend: {frontend_output}")

if __name__ == '__main__':
    download_states()
