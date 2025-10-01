#!/usr/bin/env python3
"""
Download and process Montana TIGER/Line shapefiles from Census Bureau
Converts to GeoJSON for web mapping
"""

import urllib.request
import zipfile
import json
from pathlib import Path
import subprocess
import sys

# Census Bureau TIGER/Line 2023 base URL
TIGER_BASE_URL = "https://www2.census.gov/geo/tiger/TIGER2023"

# Montana FIPS code
MONTANA_FIPS = "30"

# TIGER datasets to download
TIGER_DATASETS = {
    "counties": f"{TIGER_BASE_URL}/COUNTY/tl_2023_us_county.zip",
    "tracts": f"{TIGER_BASE_URL}/TRACT/tl_2023_{MONTANA_FIPS}_tract.zip",
    "blockgroups": f"{TIGER_BASE_URL}/BG/tl_2023_{MONTANA_FIPS}_bg.zip",
    "places": f"{TIGER_BASE_URL}/PLACE/tl_2023_{MONTANA_FIPS}_place.zip",
    "zipcodes": f"{TIGER_BASE_URL}/ZCTA520/tl_2023_us_zcta520.zip",
}

def download_and_extract(url: str, output_dir: Path, dataset_name: str):
    """Download and extract a TIGER shapefile"""
    print(f"\n>> Downloading {dataset_name}...")
    print(f"   URL: {url}")

    zip_path = output_dir / f"{dataset_name}.zip"
    extract_dir = output_dir / dataset_name
    extract_dir.mkdir(exist_ok=True)

    # Download
    try:
        urllib.request.urlretrieve(url, zip_path)
        print(f"   ✓ Downloaded to {zip_path}")
    except Exception as e:
        print(f"   ✗ Download failed: {e}")
        return None

    # Extract
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print(f"   ✓ Extracted to {extract_dir}")

        # Find the .shp file
        shp_files = list(extract_dir.glob("*.shp"))
        if shp_files:
            return shp_files[0]
        else:
            print(f"   ✗ No .shp file found in {extract_dir}")
            return None
    except Exception as e:
        print(f"   ✗ Extraction failed: {e}")
        return None
    finally:
        # Clean up zip file
        if zip_path.exists():
            zip_path.unlink()


def shapefile_to_geojson(shp_path: Path, output_path: Path, filter_montana: bool = False):
    """Convert shapefile to GeoJSON using ogr2ogr"""
    print(f"\n>> Converting {shp_path.name} to GeoJSON...")

    try:
        cmd = ["ogr2ogr", "-f", "GeoJSON"]

        # Filter to Montana for nationwide datasets
        if filter_montana:
            cmd.extend(["-where", f"STATEFP='{MONTANA_FIPS}'"])

        # Simplify geometries to reduce file size
        cmd.extend(["-simplify", "0.0001"])

        # Output and input
        cmd.extend([str(output_path), str(shp_path)])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            # Get feature count
            with open(output_path, 'r') as f:
                data = json.load(f)
                feature_count = len(data.get('features', []))

            file_size = output_path.stat().st_size / 1024  # KB
            print(f"   ✓ Created {output_path.name} ({feature_count} features, {file_size:.1f} KB)")
            return True
        else:
            print(f"   ✗ ogr2ogr failed: {result.stderr}")
            return False

    except FileNotFoundError:
        print("   ✗ ogr2ogr not found. Install GDAL/OGR:")
        print("      Windows: https://www.gisinternals.com/release.php")
        print("      Mac: brew install gdal")
        print("      Linux: sudo apt-get install gdal-bin")
        return False
    except Exception as e:
        print(f"   ✗ Conversion failed: {e}")
        return False


def main():
    """Download and process all TIGER datasets"""
    print("=" * 60)
    print("Montana TIGER/Line Data Download & Conversion")
    print("=" * 60)

    # Setup directories
    project_root = Path(__file__).parent.parent
    tiger_dir = project_root / "data" / "tiger"
    tiger_dir.mkdir(exist_ok=True)

    print(f"\nOutput directory: {tiger_dir}")

    # Download and convert each dataset
    for dataset_name, url in TIGER_DATASETS.items():
        # Download and extract
        shp_path = download_and_extract(url, tiger_dir, dataset_name)

        if shp_path:
            # Convert to GeoJSON
            geojson_path = tiger_dir / f"{dataset_name}.geojson"

            # Filter nationwide datasets to Montana only
            filter_montana = dataset_name in ["counties", "zipcodes"]

            shapefile_to_geojson(shp_path, geojson_path, filter_montana)

    print("\n" + "=" * 60)
    print("TIGER data download complete!")
    print("=" * 60)
    print(f"\nData saved to: {tiger_dir}")
    print("\nNext steps:")
    print("1. Restart the backend server")
    print("2. Refresh the map to see new boundary layers")


if __name__ == "__main__":
    main()
