#!/usr/bin/env python3
"""
Create test parcel data for Bozeman, Montana area
Using realistic coordinates for a small neighborhood
"""

import json
from pathlib import Path

# Test parcels in Bozeman, Montana (downtown area)
# These are realistic parcel shapes for demonstration
TEST_PARCELS = [
    {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-111.0440, 45.6790],
                [-111.0430, 45.6790],
                [-111.0430, 45.6780],
                [-111.0440, 45.6780],
                [-111.0440, 45.6790]
            ]]
        },
        "properties": {
            "PARCELID": "R12345",
            "OWNERNAME": "SMITH, JOHN & JANE",
            "MAILADD": "123 MAIN ST",
            "MAILCITY": "BOZEMAN",
            "MAILSTATE": "MT",
            "MAILZIP": "59715",
            "ACRES": 0.25,
            "TAXVALUE": 425000
        }
    },
    {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-111.0430, 45.6790],
                [-111.0420, 45.6790],
                [-111.0420, 45.6780],
                [-111.0430, 45.6780],
                [-111.0430, 45.6790]
            ]]
        },
        "properties": {
            "PARCELID": "R12346",
            "OWNERNAME": "DOE FAMILY TRUST",
            "MAILADD": "125 MAIN ST",
            "MAILCITY": "BOZEMAN",
            "MAILSTATE": "MT",
            "MAILZIP": "59715",
            "ACRES": 0.23,
            "TAXVALUE": 398000
        }
    },
    {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-111.0420, 45.6790],
                [-111.0410, 45.6790],
                [-111.0410, 45.6780],
                [-111.0420, 45.6780],
                [-111.0420, 45.6790]
            ]]
        },
        "properties": {
            "PARCELID": "R12347",
            "OWNERNAME": "JOHNSON, MICHAEL R",
            "MAILADD": "127 MAIN ST",
            "MAILCITY": "BOZEMAN",
            "MAILSTATE": "MT",
            "MAILZIP": "59715",
            "ACRES": 0.28,
            "TAXVALUE": 445000
        }
    },
    {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-111.0440, 45.6780],
                [-111.0430, 45.6780],
                [-111.0430, 45.6770],
                [-111.0440, 45.6770],
                [-111.0440, 45.6780]
            ]]
        },
        "properties": {
            "PARCELID": "R12348",
            "OWNERNAME": "BROWN PROPERTIES LLC",
            "MAILADD": "PO BOX 456",
            "MAILCITY": "BOZEMAN",
            "MAILSTATE": "MT",
            "MAILZIP": "59715",
            "ACRES": 0.26,
            "TAXVALUE": 412000
        }
    },
    {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-111.0430, 45.6780],
                [-111.0420, 45.6780],
                [-111.0420, 45.6770],
                [-111.0430, 45.6770],
                [-111.0430, 45.6780]
            ]]
        },
        "properties": {
            "PARCELID": "R12349",
            "OWNERNAME": "WILSON, SARAH J",
            "MAILADD": "124 ELM ST",
            "MAILCITY": "BOZEMAN",
            "MAILSTATE": "MT",
            "MAILZIP": "59715",
            "ACRES": 0.24,
            "TAXVALUE": 389000
        }
    },
    {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-111.0420, 45.6780],
                [-111.0410, 45.6780],
                [-111.0410, 45.6770],
                [-111.0420, 45.6770],
                [-111.0420, 45.6780]
            ]]
        },
        "properties": {
            "PARCELID": "R12350",
            "OWNERNAME": "MARTINEZ FAMILY TRUST",
            "MAILADD": "126 ELM ST",
            "MAILCITY": "BOZEMAN",
            "MAILSTATE": "MT",
            "MAILZIP": "59715",
            "ACRES": 0.27,
            "TAXVALUE": 435000
        }
    }
]

def create_test_parcels():
    """Create test parcel GeoJSON file."""

    output_dir = Path("data/parcels")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "test_parcels.geojson"

    geojson = {
        "type": "FeatureCollection",
        "features": TEST_PARCELS
    }

    with open(output_file, 'w') as f:
        json.dump(geojson, f, indent=2)

    print("Test Parcel Data Created")
    print("=" * 60)
    print(f"Created {len(TEST_PARCELS)} test parcels")
    print(f"Location: Bozeman, Montana (downtown)")
    print(f"Saved to: {output_file}")
    print()
    print("To view these parcels:")
    print("1. Navigate to Bozeman, Montana")
    print("2. Zoom to coordinates: -111.0425, 45.6780")
    print("3. Zoom level: 16+")
    print()
    print("Next: Restart the server to load new data")

if __name__ == '__main__':
    create_test_parcels()