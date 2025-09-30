#!/usr/bin/env python3
"""Check what layers are in a vector tile"""
import sqlite3
import gzip
import sys

mbtiles_path = sys.argv[1] if len(sys.argv) > 1 else 'data/tiles/ownership.mbtiles'

conn = sqlite3.connect(mbtiles_path)

# Get a sample tile
sample = conn.execute('SELECT tile_data FROM tiles LIMIT 1').fetchone()

if sample:
    tile_data = sample[0]

    # Check if it's gzipped (starts with 1f 8b)
    if tile_data[:2] == b'\x1f\x8b':
        print("Tile is gzipped")
        try:
            decompressed = gzip.decompress(tile_data)
            print(f"Decompressed size: {len(decompressed)} bytes")
            # Try to detect layer names (this is hacky, proper parsing needs protobuf)
            text = decompressed.decode('latin-1', errors='ignore')
            if 'padus' in text:
                print("Found 'padus' in tile data")
            print("\nFirst 500 bytes (as text):")
            print(repr(decompressed[:500]))
        except Exception as e:
            print(f"Error decompressing: {e}")
    else:
        print("Tile is not gzipped")
        print(f"First 100 bytes: {tile_data[:100]}")
else:
    print("No tiles found!")

# Check metadata for layer info
print("\n" + "=" * 60)
print("METADATA json field (if exists):")
print("=" * 60)
result = conn.execute("SELECT value FROM metadata WHERE name='json'").fetchone()
if result:
    print(result[0][:500])
else:
    print("No 'json' metadata found")

conn.close()