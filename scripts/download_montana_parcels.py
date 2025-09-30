#!/usr/bin/env python3
"""
Download Montana Cadastral Parcel Data
Uses Montana's free ArcGIS REST API
"""

import json
import requests
from pathlib import Path
import time

# Montana Parcel Service
MONTANA_PARCELS_URL = "https://gisservicemt.gov/arcgis/rest/services/MSDI_Framework/Parcels/MapServer/0"

def get_parcel_count():
    """Get total count of parcels."""
    url = f"{MONTANA_PARCELS_URL}/query"
    params = {
        'where': '1=1',
        'returnCountOnly': 'true',
        'f': 'json'
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get('count', 0)

def download_parcels_batch(offset, limit=1000):
    """Download a batch of parcels."""
    url = f"{MONTANA_PARCELS_URL}/query"

    params = {
        'where': '1=1',
        'outFields': 'OBJECTID,PARCELID,OWNERNAME,MAILADD,MAILCITY,MAILSTATE,MAILZIP,ACRES,TAXVALUE',
        'geometryType': 'esriGeometryEnvelope',
        'spatialRel': 'esriSpatialRelIntersects',
        'outSR': '4326',  # WGS84
        'f': 'geojson',
        'resultOffset': offset,
        'resultRecordCount': limit
    }

    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error downloading batch at offset {offset}: {e}")
        return None

def download_montana_parcels(max_parcels=10000):
    """
    Download Montana parcels in batches.

    Args:
        max_parcels: Maximum number of parcels to download (use None for all)
    """
    output_dir = Path("data/parcels")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "montana_parcels.geojson"

    print("Montana Cadastral Parcel Download")
    print("=" * 60)

    # Get total count
    total_count = get_parcel_count()
    print(f"Total parcels in Montana: {total_count:,}")

    if max_parcels:
        total_count = min(total_count, max_parcels)
        print(f"Downloading first {total_count:,} parcels...")

    # Download in batches
    batch_size = 1000
    all_features = []

    for offset in range(0, total_count, batch_size):
        remaining = total_count - offset
        current_batch = min(batch_size, remaining)

        print(f"Downloading parcels {offset:,} to {offset + current_batch:,}...", end=" ")

        batch_data = download_parcels_batch(offset, current_batch)

        if batch_data and 'features' in batch_data:
            features = batch_data['features']
            all_features.extend(features)
            print(f"OK ({len(features)} parcels)")
        else:
            print("FAILED")
            break

        # Rate limiting
        time.sleep(0.5)

    # Write GeoJSON
    geojson = {
        'type': 'FeatureCollection',
        'features': all_features
    }

    with open(output_file, 'w') as f:
        json.dump(geojson, f)

    print(f"\n[OK] Downloaded {len(all_features):,} parcels")
    print(f"[OK] Saved to {output_file}")

    # Show file size
    size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"[OK] File size: {size_mb:.1f} MB")

    # Sample features
    if all_features:
        print("\nSample parcel:")
        sample = all_features[0]
        props = sample.get('properties', {})
        print(f"  Parcel ID: {props.get('PARCELID')}")
        print(f"  Owner: {props.get('OWNERNAME')}")
        print(f"  Acres: {props.get('ACRES')}")
        print(f"  Value: ${props.get('TAXVALUE', 0):,}")

if __name__ == '__main__':
    print("Starting Montana parcel download...")
    print("This will download property boundary data from Montana State GIS.")
    print()

    # Download first 10,000 parcels for testing (remove limit for full state)
    download_montana_parcels(max_parcels=10000)

    print("\n" + "="*60)
    print("Next step: Update server to serve parcel data")
    print("="*60)