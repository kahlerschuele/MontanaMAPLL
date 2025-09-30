#!/usr/bin/env python3
"""
Create sample ownership data for testing
This creates realistic sample polygons for US public lands
"""

import json
from pathlib import Path

# Sample features covering major US public lands
SAMPLE_FEATURES = [
    # Yellowstone National Park (Federal - NPS)
    {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-111.15, 44.95],
                [-109.85, 44.95],
                [-109.85, 44.13],
                [-111.15, 44.13],
                [-111.15, 44.95]
            ]]
        },
        "properties": {
            "owner_class": "federal",
            "owner_name": "National Park Service",
            "unit_name": "Yellowstone National Park",
            "source": "PAD-US",
            "asof": "2023-09-01"
        }
    },
    # BLM Land in Nevada (Federal - BLM)
    {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-117.5, 39.5],
                [-116.5, 39.5],
                [-116.5, 38.5],
                [-117.5, 38.5],
                [-117.5, 39.5]
            ]]
        },
        "properties": {
            "owner_class": "federal",
            "owner_name": "Bureau of Land Management",
            "unit_name": "Central Nevada BLM",
            "source": "PAD-US",
            "asof": "2023-09-01"
        }
    },
    # State Park in Colorado
    {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-105.6, 40.3],
                [-105.4, 40.3],
                [-105.4, 40.15],
                [-105.6, 40.15],
                [-105.6, 40.3]
            ]]
        },
        "properties": {
            "owner_class": "state",
            "owner_name": "Colorado Parks and Wildlife",
            "unit_name": "State Forest State Park",
            "source": "PAD-US",
            "asof": "2023-09-01"
        }
    },
    # Tribal Land - Navajo Nation
    {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-110.5, 36.5],
                [-109.0, 36.5],
                [-109.0, 35.5],
                [-110.5, 35.5],
                [-110.5, 36.5]
            ]]
        },
        "properties": {
            "owner_class": "tribal",
            "owner_name": "Navajo Nation",
            "unit_name": "Navajo Nation Reservation",
            "source": "PAD-US",
            "asof": "2023-09-01"
        }
    },
    # Local Park - California
    {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-122.5, 37.8],
                [-122.4, 37.8],
                [-122.4, 37.7],
                [-122.5, 37.7],
                [-122.5, 37.8]
            ]]
        },
        "properties": {
            "owner_class": "local",
            "owner_name": "East Bay Regional Park District",
            "unit_name": "Regional Park",
            "source": "PAD-US",
            "asof": "2023-09-01"
        }
    },
]

def create_sample_data():
    """Create sample data files for testing."""

    output_dir = Path("data/padus")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create NDJSON file (high-zoom layer)
    clean_file = output_dir / "padus_clean.ndjson"
    with open(clean_file, 'w') as f:
        for feature in SAMPLE_FEATURES:
            f.write(json.dumps(feature) + '\n')

    print(f"[OK] Created {clean_file} ({len(SAMPLE_FEATURES)} features)")

    # Create dissolved GeoJSON (low-zoom layer)
    # Group by owner_class
    dissolved_features = []
    classes = {}

    for feature in SAMPLE_FEATURES:
        owner_class = feature['properties']['owner_class']
        if owner_class not in classes:
            classes[owner_class] = {
                "type": "Feature",
                "geometry": feature['geometry'],  # Simplified - just use first feature
                "properties": {
                    "owner_class": owner_class,
                    "owner_name": owner_class.replace('_', ' ').title(),
                    "unit_name": "",
                    "source": "PAD-US",
                    "asof": "2023-09-01"
                }
            }

    dissolved_features = list(classes.values())

    dissolved_file = output_dir / "padus_dissolved.geojson"
    with open(dissolved_file, 'w') as f:
        json.dump({
            "type": "FeatureCollection",
            "features": dissolved_features
        }, f)

    print(f"[OK] Created {dissolved_file} ({len(dissolved_features)} dissolved features)")
    print("\n" + "="*60)
    print("NOTE: Using sample data for testing")
    print("="*60)
    print("This is a small sample dataset with 5 test polygons.")
    print("For production, download the full PAD-US dataset:")
    print("  https://www.sciencebase.gov/catalog/item/6596f0d1d34e176b9e694b3a")
    print("="*60)


if __name__ == '__main__':
    print("Creating sample PAD-US data...")
    create_sample_data()
    print("\nNext step: bash etl/build_tiles.sh")