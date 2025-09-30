#!/usr/bin/env python3
"""
PAD-US Data Preparation Script
Normalizes PAD-US attributes and outputs clean GeoJSON NDJSON
"""

import json
import sys
from pathlib import Path
from datetime import datetime

try:
    from osgeo import ogr, osr
    import shapely
    from shapely.geometry import shape, mapping
    from shapely.validation import make_valid
except ImportError:
    print("ERROR: Missing dependencies. Install with:")
    print("  pip install gdal shapely")
    sys.exit(1)

# Configuration
PADUS_GPKG = Path("data/padus/PADUS3_0Geopackage/PADUS3_0_Designations.gpkg")
OUTPUT_CLEAN = Path("data/padus/padus_clean.ndjson")
OUTPUT_DISSOLVED = Path("data/padus/padus_dissolved.geojson")
ASOF_DATE = "2023-09-01"  # Update based on PAD-US release date


def map_owner_class(owner_type, manager_type):
    """Map PAD-US owner/manager type to normalized owner_class."""
    owner = str(owner_type).upper()
    manager = str(manager_type).upper()

    # Federal
    if any(x in owner for x in ['FED', 'FEDERAL']) or \
       any(x in manager for x in ['FED', 'FEDERAL', 'BLM', 'USFS', 'NPS', 'FWS', 'DOD', 'BOR']):
        return 'federal'

    # State
    if 'STATE' in owner or 'STATE' in manager:
        return 'state'

    # Local (county, city, regional)
    if any(x in owner for x in ['LOCAL', 'COUNTY', 'CITY', 'MUNICIPAL', 'REGIONAL']) or \
       any(x in manager for x in ['LOCAL', 'COUNTY', 'CITY', 'MUNICIPAL', 'REGIONAL']):
        return 'local'

    # Tribal
    if any(x in owner for x in ['TRIB', 'NATIVE']) or \
       any(x in manager for x in ['TRIB', 'NATIVE']):
        return 'tribal'

    # Other public (NGO, Joint, etc.)
    if any(x in owner for x in ['NGO', 'JOINT', 'PRIVATE']) or \
       any(x in manager for x in ['NGO', 'JOINT']):
        return 'other_public'

    return None


def extract_owner_name(feature, owner_class):
    """Extract simplified owner name."""
    props = feature.GetFieldDefNames()

    # Try different field names
    for field in ['Mang_Name', 'Manager_Name', 'Own_Name', 'Owner_Name', 'Mang_Type', 'Owner_Type']:
        if field in props:
            val = feature.GetField(field)
            if val:
                return str(val)[:100]  # Truncate to 100 chars

    return owner_class.replace('_', ' ').title()


def extract_unit_name(feature):
    """Extract unit/park/forest name."""
    props = feature.GetFieldDefNames()

    for field in ['Unit_Nm', 'Unit_Name', 'Loc_Nm', 'Location_Name']:
        if field in props:
            val = feature.GetField(field)
            if val:
                return str(val)[:100]

    return ''


def process_features():
    """Process PAD-US features and write normalized output."""

    if not PADUS_GPKG.exists():
        print(f"ERROR: PAD-US file not found: {PADUS_GPKG}")
        print("Run padus_download.sh first")
        sys.exit(1)

    # Open PAD-US dataset
    ds = ogr.Open(str(PADUS_GPKG))
    if not ds:
        print(f"ERROR: Could not open {PADUS_GPKG}")
        sys.exit(1)

    layer = ds.GetLayer(0)
    print(f"Processing {layer.GetFeatureCount()} features from PAD-US...")

    # Setup output
    OUTPUT_CLEAN.parent.mkdir(parents=True, exist_ok=True)

    features_by_class = {
        'federal': [],
        'state': [],
        'local': [],
        'tribal': [],
        'other_public': []
    }

    count = 0
    skipped = 0

    with open(OUTPUT_CLEAN, 'w') as f:
        for feature in layer:
            # Get owner type fields
            owner_type = feature.GetField('Own_Type') if 'Own_Type' in feature.GetFieldDefNames() else None
            manager_type = feature.GetField('Mang_Type') if 'Mang_Type' in feature.GetFieldDefNames() else None

            owner_class = map_owner_class(owner_type, manager_type)

            if not owner_class:
                skipped += 1
                continue

            # Get geometry
            geom = feature.GetGeometryRef()
            if not geom:
                skipped += 1
                continue

            # Convert to GeoJSON
            geom_json = json.loads(geom.ExportToJson())

            # Validate and fix geometry
            try:
                shp = shape(geom_json)
                if not shp.is_valid:
                    shp = make_valid(shp)
                geom_json = mapping(shp)
            except Exception as e:
                print(f"Warning: Could not validate geometry: {e}")
                skipped += 1
                continue

            # Build normalized feature
            clean_feature = {
                'type': 'Feature',
                'geometry': geom_json,
                'properties': {
                    'owner_class': owner_class,
                    'owner_name': extract_owner_name(feature, owner_class),
                    'unit_name': extract_unit_name(feature),
                    'source': 'PAD-US',
                    'asof': ASOF_DATE
                }
            }

            # Write NDJSON
            f.write(json.dumps(clean_feature) + '\n')

            # Collect for dissolve
            features_by_class[owner_class].append(clean_feature)

            count += 1
            if count % 10000 == 0:
                print(f"  Processed {count:,} features...")

    print(f"✓ Wrote {count:,} features to {OUTPUT_CLEAN}")
    print(f"  Skipped {skipped:,} features (no valid owner_class or geometry)")

    return features_by_class


def dissolve_by_class(features_by_class):
    """Dissolve features by owner_class for low-zoom layer."""
    print("\nDissolving features by owner_class for low-zoom tiles...")

    dissolved_features = []

    for owner_class, features in features_by_class.items():
        if not features:
            continue

        print(f"  Dissolving {len(features):,} {owner_class} features...")

        # Union all geometries for this class
        geometries = []
        for feat in features:
            try:
                shp = shape(feat['geometry'])
                if shp.is_valid and not shp.is_empty:
                    geometries.append(shp)
            except:
                continue

        if not geometries:
            continue

        # Union (this can be slow for large datasets)
        try:
            from shapely.ops import unary_union
            dissolved = unary_union(geometries)

            dissolved_feature = {
                'type': 'Feature',
                'geometry': mapping(dissolved),
                'properties': {
                    'owner_class': owner_class,
                    'owner_name': owner_class.replace('_', ' ').title(),
                    'unit_name': '',
                    'source': 'PAD-US',
                    'asof': ASOF_DATE
                }
            }

            dissolved_features.append(dissolved_feature)
            print(f"    ✓ Dissolved to 1 feature")

        except Exception as e:
            print(f"    Warning: Could not dissolve {owner_class}: {e}")

    # Write dissolved GeoJSON
    dissolved_collection = {
        'type': 'FeatureCollection',
        'features': dissolved_features
    }

    with open(OUTPUT_DISSOLVED, 'w') as f:
        json.dump(dissolved_collection, f)

    print(f"✓ Wrote {len(dissolved_features)} dissolved features to {OUTPUT_DISSOLVED}")


if __name__ == '__main__':
    print("PAD-US Data Preparation")
    print("=" * 60)

    features_by_class = process_features()
    dissolve_by_class(features_by_class)

    print("\n✓ Preparation complete!")
    print(f"  Clean features: {OUTPUT_CLEAN}")
    print(f"  Dissolved features: {OUTPUT_DISSOLVED}")
    print("\nNext step: Run etl/build_tiles.sh")