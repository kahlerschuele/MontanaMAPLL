#!/usr/bin/env python3
"""
Download US Census TIGER/Line boundaries for Montana
Simplified approach with minimal dependencies
"""

import urllib.request
import zipfile
import geopandas as gpd
from pathlib import Path
import sys

# Montana FIPS code
MONTANA_FIPS = "30"
YEAR = "2023"

# Census URLs
TIGER_BASE = f"https://www2.census.gov/geo/tiger/GENZ{YEAR}/shp"

# Layers to download (name, URL pattern, filter)
LAYERS = [
    {
        "name": "counties",
        "url": f"{TIGER_BASE}/cb_{YEAR}_us_county_500k.zip",
        "filter_col": "STATEFP",
        "simplify": 0.001
    },
    {
        "name": "places",
        "url": f"{TIGER_BASE}/cb_{YEAR}_us_place_500k.zip",
        "filter_col": "STATEFP",
        "simplify": 0.001
    },
    {
        "name": "tracts",
        "url": f"{TIGER_BASE}/cb_{YEAR}_{MONTANA_FIPS}_tract_500k.zip",
        "filter_col": None,  # Already Montana-specific
        "simplify": 0.0005
    },
    {
        "name": "blockgroups",
        "url": f"{TIGER_BASE}/cb_{YEAR}_{MONTANA_FIPS}_bg_500k.zip",
        "filter_col": None,  # Already Montana-specific
        "simplify": 0.0003
    },
    {
        "name": "zcta",
        "url": f"{TIGER_BASE}/cb_{YEAR}_us_zcta520_500k.zip",
        "filter_col": None,  # Will clip by geometry
        "simplify": 0.001
    }
]

def download_and_process_layer(layer_config, montana_bounds, output_dir):
    """Download and process a single TIGER layer"""
    name = layer_config["name"]
    url = layer_config["url"]
    filter_col = layer_config["filter_col"]
    simplify = layer_config["simplify"]

    print(f"\n{'='*60}")
    print(f"Processing: {name}")
    print(f"URL: {url}")

    # Download
    zip_path = output_dir / f"{name}_temp.zip"
    print(f"Downloading...")
    try:
        urllib.request.urlretrieve(url, zip_path)
    except Exception as e:
        print(f"ERROR downloading {name}: {e}")
        return False

    # Extract
    extract_dir = output_dir / f"{name}_temp"
    extract_dir.mkdir(exist_ok=True)
    print(f"Extracting...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    # Find shapefile
    shp_files = list(extract_dir.glob("*.shp"))
    if not shp_files:
        print(f"ERROR: No shapefile found for {name}")
        zip_path.unlink()
        return False

    shp_path = shp_files[0]
    print(f"Reading {shp_path.name}...")

    # Load data
    gdf = gpd.read_file(shp_path)
    print(f"Loaded {len(gdf)} features")

    # Filter to Montana if needed
    if filter_col and filter_col in gdf.columns:
        gdf = gdf[gdf[filter_col] == MONTANA_FIPS]
        print(f"Filtered to Montana: {len(gdf)} features")

    # Clip to Montana bounds (for national datasets like ZCTA)
    if montana_bounds is not None and len(gdf) > 1000:
        gdf = gdf.to_crs(4326)
        gdf = gpd.clip(gdf, montana_bounds)
        print(f"Clipped to Montana bounds: {len(gdf)} features")

    # Ensure WGS84
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs(4326)

    # Simplify geometry
    if simplify:
        print(f"Simplifying (tolerance={simplify})...")
        gdf['geometry'] = gdf['geometry'].simplify(tolerance=simplify, preserve_topology=True)

    # Save as GeoJSON
    output_path = output_dir / f"mt_{name}.geojson"
    gdf.to_file(output_path, driver='GeoJSON')

    file_size = output_path.stat().st_size / 1024
    print(f"SUCCESS: Saved {output_path.name}")
    print(f"Features: {len(gdf)}, Size: {file_size:.1f} KB")

    # Cleanup
    zip_path.unlink()
    import shutil
    shutil.rmtree(extract_dir)

    return True

def main():
    # Setup paths
    project_root = Path(__file__).parent.parent
    tiger_dir = project_root / "data" / "tiger"
    tiger_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("TIGER/Line Data Download for Montana")
    print("=" * 60)
    print(f"Year: {YEAR}")
    print(f"State FIPS: {MONTANA_FIPS}")
    print(f"Output directory: {tiger_dir}")

    # Load Montana state boundary for clipping
    state_path = tiger_dir / "montana_state.geojson"
    if state_path.exists():
        print(f"\nLoading Montana boundary from {state_path.name}...")
        montana_gdf = gpd.read_file(state_path)
        montana_bounds = montana_gdf.geometry.unary_union
    else:
        print("\nWARNING: Montana state boundary not found, skipping spatial clip")
        montana_bounds = None

    # Process each layer
    success_count = 0
    for layer in LAYERS:
        if download_and_process_layer(layer, montana_bounds, tiger_dir):
            success_count += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"COMPLETE: {success_count}/{len(LAYERS)} layers processed")
    print(f"{'='*60}")
    print("\nGenerated files:")
    for layer in LAYERS:
        path = tiger_dir / f"mt_{layer['name']}.geojson"
        if path.exists():
            size = path.stat().st_size / 1024
            print(f"  ✓ {path.name} ({size:.1f} KB)")

    print("\nNext steps:")
    print("1. Update frontend to add these layers to the map")
    print("2. Run ACS enrichment script to add demographic data")

if __name__ == "__main__":
    main()
