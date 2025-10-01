#!/usr/bin/env python3
"""
Download Montana state boundary from Census TIGER
"""

import urllib.request
import zipfile
import geopandas as gpd
from pathlib import Path

TIGER_STATE_URL = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_state_500k.zip"
MONTANA_FIPS = "30"

project_root = Path(__file__).parent.parent
tiger_dir = project_root / "data" / "tiger"
tiger_dir.mkdir(exist_ok=True)

print("Downloading Montana state boundary...")
print(f"URL: {TIGER_STATE_URL}")

# Download
zip_path = tiger_dir / "states.zip"
urllib.request.urlretrieve(TIGER_STATE_URL, zip_path)
print("Downloaded")

# Extract
extract_dir = tiger_dir / "states_temp"
extract_dir.mkdir(exist_ok=True)
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)
print("Extracted")

# Find shapefile
shp_files = list(extract_dir.glob("*.shp"))
if not shp_files:
    print("ERROR: No shapefile found")
    exit(1)

shp_path = shp_files[0]
print(f"Reading {shp_path.name}...")

# Load and filter to Montana
gdf = gpd.read_file(shp_path)
montana = gdf[gdf['STATEFP'] == MONTANA_FIPS]

if len(montana) == 0:
    print("ERROR: Montana not found in data")
    exit(1)

# Simplify geometry
montana['geometry'] = montana['geometry'].simplify(tolerance=0.01, preserve_topology=True)

# Save as GeoJSON
output_path = tiger_dir / "montana_state.geojson"
montana.to_file(output_path, driver='GeoJSON')

print(f"SUCCESS: Montana state boundary saved to {output_path}")
print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")

# Cleanup
zip_path.unlink()
import shutil
shutil.rmtree(extract_dir)
