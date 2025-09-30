#!/usr/bin/env python3
"""
Fetch Montana Parcel Data from Montana Cadastral API
Downloads real parcel boundaries for all of Montana
"""

import requests
import json
import time
from pathlib import Path

# Montana Cadastral Parcel Service
# This is the official Montana state parcel data
MONTANA_CADASTRAL_URL = "https://svc.mt.gov/msl/mtcadastral/Map"
PARCEL_FEATURE_SERVER = "https://geoinfo.msl.mt.gov/arcgis/rest/services/Cadastral/MapServer/1"

def fetch_montana_county_parcels(county_name, output_file):
    """
    Fetch parcel data for a Montana county.

    Args:
        county_name: Name of Montana county (e.g., "Gallatin")
        output_file: Path to output NDJSON file
    """

    print(f"\n{'='*60}")
    print(f"Fetching parcels for {county_name} County, Montana")
    print(f"{'='*60}\n")

    # Query parameters for ESRI Feature Server
    params = {
        'where': f"COUNTY_NAME='{county_name.upper()}'",
        'outFields': 'PARCEL_ID,OWNER_NAME,SITUS_ADDRESS,ACRES,TAXABLE_VALUE,COUNTY_NAME',
        'returnGeometry': 'true',
        'outSR': '4326',  # WGS84
        'f': 'geojson',
        'resultOffset': 0,
        'resultRecordCount': 2000
    }

    all_features = []
    offset = 0

    while True:
        params['resultOffset'] = offset

        print(f"  Fetching records {offset} to {offset + 2000}...")

        try:
            response = requests.get(
                f"{PARCEL_FEATURE_SERVER}/query",
                params=params,
                timeout=60
            )

            if response.status_code != 200:
                print(f"  ERROR: HTTP {response.status_code}")
                break

            data = response.json()

            if 'features' not in data or len(data['features']) == 0:
                print(f"  DONE: No more features. Total: {len(all_features)}")
                break

            features = data['features']
            all_features.extend(features)

            print(f"  FETCHED: Got {len(features)} features (total: {len(all_features)})")

            # If we got less than the record count, we're done
            if len(features) < 2000:
                break

            offset += 2000
            time.sleep(0.5)  # Be nice to the server

        except Exception as e:
            print(f"  ERROR: {e}")
            break

    # Write to NDJSON
    if all_features:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            for feature in all_features:
                # Normalize properties
                props = feature.get('properties', {})
                normalized_feature = {
                    'type': 'Feature',
                    'geometry': feature['geometry'],
                    'properties': {
                        'parcel_id': props.get('PARCEL_ID', ''),
                        'owner_name': props.get('OWNER_NAME', ''),
                        'address': props.get('SITUS_ADDRESS', ''),
                        'acres': props.get('ACRES', 0),
                        'tax_value': props.get('TAXABLE_VALUE', 0),
                        'county': props.get('COUNTY_NAME', county_name.upper()),
                        'source': 'Montana Cadastral',
                        'state': 'MT'
                    }
                }
                f.write(json.dumps(normalized_feature) + '\n')

        print(f"\nSUCCESS: Wrote {len(all_features):,} features to {output_path}")

        # Calculate file size
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"   File size: {size_mb:.2f} MB")

        return len(all_features)

    return 0

def fetch_gallatin_county_sample():
    """
    Fetch a sample of Gallatin County parcels (Bozeman area)
    This is a quick test with real data
    """
    print("Fetching Gallatin County (Bozeman) parcel sample...")

    # Get just Bozeman area - smaller bounding box for testing
    bbox = "-111.2,45.5,-110.8,45.8"  # Bozeman area (corrected lat/lon)

    params = {
        'where': "COUNTY_NAME='GALLATIN'",
        'geometry': bbox,
        'geometryType': 'esriGeometryEnvelope',
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': 'PARCEL_ID,OWNER_NAME,SITUS_ADDRESS,ACRES,TAXABLE_VALUE',
        'returnGeometry': 'true',
        'outSR': '4326',
        'f': 'geojson',
        'resultRecordCount': 1000
    }

    try:
        response = requests.get(
            f"{PARCEL_FEATURE_SERVER}/query",
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            features = data.get('features', [])

            print(f"SUCCESS: Got {len(features)} parcels in Bozeman area")

            # Save sample
            output_path = Path('data/parcels/gallatin_sample.geojson')
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                json.dump(data, f)

            print(f"Saved to {output_path}")
            return len(features)
        else:
            print(f"ERROR: HTTP {response.status_code}")
            return 0

    except Exception as e:
        print(f"ERROR: {e}")
        return 0

if __name__ == '__main__':
    import sys

    print("Montana Cadastral Parcel Fetcher")
    print("=" * 60)

    # Test with Gallatin County (Bozeman area) first
    print("\nOption 1: Fetch sample (1000 parcels in Bozeman area)")
    print("Option 2: Fetch full Gallatin County")
    print("Option 3: Fetch all Montana counties")

    choice = sys.argv[1] if len(sys.argv) > 1 else '1'

    if choice == '1':
        # Quick sample for testing
        count = fetch_gallatin_county_sample()
        print(f"\n✅ Fetched {count} sample parcels")

    elif choice == '2':
        # Full Gallatin County
        count = fetch_montana_county_parcels('Gallatin', 'data/parcels/gallatin_county.ndjson')
        print(f"\n✅ Total: {count:,} parcels")

    elif choice == '3':
        # All Montana counties (this will take a while!)
        montana_counties = [
            'Gallatin', 'Yellowstone', 'Missoula', 'Flathead', 'Cascade',
            'Lewis and Clark', 'Ravalli', 'Silver Bow', 'Lake', 'Fergus'
            # Add more counties as needed
        ]

        total = 0
        for county in montana_counties:
            count = fetch_montana_county_parcels(
                county,
                f'data/parcels/{county.lower().replace(" ", "_")}_county.ndjson'
            )
            total += count
            time.sleep(1)

        print(f"\n✅ Total parcels: {total:,}")

    print("\nNext step: Update the frontend to load this data!")
    print("          python scripts/fetch_montana_parcels.py")