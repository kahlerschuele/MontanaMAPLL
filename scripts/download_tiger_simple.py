#!/usr/bin/env python3
"""
Download Montana TIGER data directly as GeoJSON from Census Cartographic Boundary Files
No GDAL required - pure Python approach
"""

import urllib.request
import zipfile
import json
from pathlib import Path

# Census Cartographic Boundary Files (2023) - already simplified, smaller files
# These are GeoJSON-ready and don't require ogr2ogr
TIGER_DATASETS = {
    "counties": "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip",
    "tracts": "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_30_tract_500k.zip",
    "blockgroups": "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_30_bg_500k.zip",
    "places": "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_30_place_500k.zip",
}

MONTANA_FIPS = "30"


def download_and_convert(url, output_dir, dataset_name, filter_montana=False):
    """Download shapefile and convert to GeoJSON using geopandas"""
    print(f"\nDownloading {dataset_name}...")
    print(f"  URL: {url}")

    zip_path = output_dir / f"{dataset_name}.zip"
    extract_dir = output_dir / dataset_name
    extract_dir.mkdir(exist_ok=True)

    # Download
    try:
        print("  Downloading...", end="", flush=True)
        urllib.request.urlretrieve(url, zip_path)
        print(" DONE")
    except Exception as e:
        print(f" FAILED: {e}")
        return False

    # Extract
    try:
        print("  Extracting...", end="", flush=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print(" DONE")
    except Exception as e:
        print(f" FAILED: {e}")
        return False
    finally:
        if zip_path.exists():
            zip_path.unlink()

    # Find shapefile
    shp_files = list(extract_dir.glob("*.shp"))
    if not shp_files:
        print("  ERROR: No .shp file found")
        return False

    shp_path = shp_files[0]
    geojson_path = output_dir / f"{dataset_name}.geojson"

    # Convert using geopandas
    try:
        import geopandas as gpd

        print("  Converting to GeoJSON...", end="", flush=True)
        gdf = gpd.read_file(shp_path)

        # Filter to Montana if needed
        if filter_montana and 'STATEFP' in gdf.columns:
            gdf = gdf[gdf['STATEFP'] == MONTANA_FIPS]

        # Simplify to reduce file size
        gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.001, preserve_topology=True)

        # Save as GeoJSON
        gdf.to_file(geojson_path, driver='GeoJSON')

        file_size = geojson_path.stat().st_size / 1024
        print(f" DONE ({len(gdf)} features, {file_size:.1f} KB)")
        return True

    except ImportError:
        print("\n  ERROR: geopandas not installed")
        print("  Install with: pip install geopandas")
        return False
    except Exception as e:
        print(f" FAILED: {e}")
        return False


def main():
    print("=" * 60)
    print("Montana TIGER Data Download (Simplified)")
    print("=" * 60)

    project_root = Path(__file__).parent.parent
    tiger_dir = project_root / "data" / "tiger"
    tiger_dir.mkdir(exist_ok=True)

    print(f"\nOutput directory: {tiger_dir}")

    success_count = 0
    for dataset_name, url in TIGER_DATASETS.items():
        filter_montana = dataset_name in ["counties"]
        if download_and_convert(url, tiger_dir, dataset_name, filter_montana):
            success_count += 1

    print("\n" + "=" * 60)
    print(f"Downloaded {success_count}/{len(TIGER_DATASETS)} datasets")
    print("=" * 60)

    if success_count > 0:
        print(f"\nData saved to: {tiger_dir}")
        print("\nNext steps:")
        print("1. Restart the backend server on port 8001")
        print("2. Refresh the map to see TIGER boundary layers")


if __name__ == "__main__":
    main()
