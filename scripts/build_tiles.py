#!/usr/bin/env python3
"""
Build MBTiles from GeoJSON - Python alternative to tippecanoe
Simple vector tile generation for testing
"""

import json
import sqlite3
import gzip
from pathlib import Path
import math

def lon_to_tile_x(lon, zoom):
    """Convert longitude to tile X coordinate."""
    return int((lon + 180.0) / 360.0 * (1 << zoom))

def lat_to_tile_y(lat, zoom):
    """Convert latitude to tile Y coordinate."""
    lat_rad = math.radians(lat)
    return int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * (1 << zoom))

def create_tile_feature(feature, tile_extent=4096):
    """
    Convert GeoJSON feature to a simplified vector tile feature.
    This is a basic implementation - tippecanoe does much more sophisticated work.
    """
    return feature  # Simplified - just pass through for now

def create_mbtiles(geojson_files, output_path, zoom_range=(4, 14)):
    """
    Create MBTiles from GeoJSON files.
    This is a simplified implementation for testing.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove existing file
    if output_path.exists():
        output_path.unlink()

    # Create SQLite database
    conn = sqlite3.connect(str(output_path))
    cursor = conn.cursor()

    # Create MBTiles schema
    cursor.execute('''
        CREATE TABLE metadata (
            name TEXT,
            value TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE tiles (
            zoom_level INTEGER,
            tile_column INTEGER,
            tile_row INTEGER,
            tile_data BLOB
        )
    ''')

    cursor.execute('CREATE UNIQUE INDEX tile_index ON tiles (zoom_level, tile_column, tile_row)')

    # Add metadata
    metadata = {
        'name': 'US Ownership',
        'format': 'pbf',
        'type': 'overlay',
        'version': '1.0',
        'description': 'US Public Land Ownership',
        'minzoom': str(zoom_range[0]),
        'maxzoom': str(zoom_range[1]),
        'bounds': '-180,-85.0511,180,85.0511',
        'center': '-98.5795,39.8283,4',
    }

    for name, value in metadata.items():
        cursor.execute('INSERT INTO metadata VALUES (?, ?)', (name, value))

    # For this simplified version, we'll create one tile per feature
    # Real tippecanoe does sophisticated spatial indexing and tiling

    print("Creating simplified vector tiles...")
    print("NOTE: This is a basic implementation for testing.")
    print("For production, use tippecanoe on Linux/Mac or WSL.")
    print()

    total_tiles = 0

    for geojson_file, layer_name, zoom_levels in geojson_files:
        if not Path(geojson_file).exists():
            print(f"Warning: {geojson_file} not found, skipping")
            continue

        print(f"Processing {layer_name} (z{zoom_levels[0]}-{zoom_levels[1]})...")

        # Load features
        features = []
        if geojson_file.endswith('.ndjson'):
            with open(geojson_file, 'r') as f:
                for line in f:
                    if line.strip():
                        features.append(json.loads(line))
        else:
            with open(geojson_file, 'r') as f:
                data = json.load(f)
                features = data.get('features', [])

        # Create tiles for each zoom level
        for zoom in range(zoom_levels[0], zoom_levels[1] + 1):
            # Group features by tile
            tiles_dict = {}

            for feature in features:
                # Get feature bounds (simplified - just use first coordinate)
                coords = feature['geometry']['coordinates']
                if feature['geometry']['type'] == 'Polygon':
                    first_coord = coords[0][0]
                else:
                    first_coord = coords[0]

                lon, lat = first_coord[0], first_coord[1]

                # Calculate tile coordinates
                tx = lon_to_tile_x(lon, zoom)
                ty = lat_to_tile_y(lat, zoom)

                tile_key = (zoom, tx, ty)
                if tile_key not in tiles_dict:
                    tiles_dict[tile_key] = []

                tiles_dict[tile_key].append(feature)

            # Create vector tiles
            for (z, x, y), tile_features in tiles_dict.items():
                # Create simplified vector tile (GeoJSON for now, not real MVT)
                # Real implementation would use mapbox-vector-tile library
                tile_data = {
                    'type': 'FeatureCollection',
                    'features': tile_features
                }

                # Convert to JSON and gzip
                tile_json = json.dumps(tile_data).encode('utf-8')
                tile_gzipped = gzip.compress(tile_json)

                # Calculate TMS y (flip y coordinate)
                tms_y = (1 << z) - 1 - y

                # Insert tile
                try:
                    cursor.execute(
                        'INSERT INTO tiles (zoom_level, tile_column, tile_row, tile_data) VALUES (?, ?, ?, ?)',
                        (z, x, tms_y, tile_gzipped)
                    )
                    total_tiles += 1
                except sqlite3.IntegrityError:
                    # Tile already exists (duplicate), skip
                    pass

            print(f"  z{zoom}: {len(tiles_dict)} tiles")

    conn.commit()
    conn.close()

    print(f"\nCreated {output_path}")
    print(f"Total tiles: {total_tiles}")

    # Show file size
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"Size: {size_mb:.2f} MB")

    print("\n" + "="*60)
    print("NOTE: Using simplified tile format (GeoJSON, not MVT)")
    print("="*60)
    print("This works for testing but is not optimized.")
    print("For production, install tippecanoe:")
    print("  - WSL: sudo apt-get install tippecanoe")
    print("  - Mac: brew install tippecanoe")
    print("  - Or use Docker")
    print("="*60)

if __name__ == '__main__':
    print("Building vector tiles...")
    print()

    geojson_files = [
        ('data/padus/padus_dissolved.geojson', 'padus_low', (4, 9)),
        ('data/padus/padus_clean.ndjson', 'padus_hi', (10, 14)),
    ]

    output_path = 'data/tiles/ownership.mbtiles'

    create_mbtiles(geojson_files, output_path)

    print("\nNext step: cd server && uvicorn main:app --reload")