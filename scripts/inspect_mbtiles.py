#!/usr/bin/env python3
"""Quick script to inspect MBTiles"""
import sqlite3
import sys

mbtiles_path = sys.argv[1] if len(sys.argv) > 1 else 'data/tiles/ownership.mbtiles'

conn = sqlite3.connect(mbtiles_path)

print(f"Inspecting: {mbtiles_path}\n")
print("=" * 60)
print("METADATA:")
print("=" * 60)
for row in conn.execute('SELECT name, value FROM metadata'):
    value = row[1][:200] if len(row[1]) > 200 else row[1]
    print(f"  {row[0]}: {value}")

print("\n" + "=" * 60)
print("TILES BY ZOOM LEVEL:")
print("=" * 60)
for row in conn.execute('SELECT zoom_level, COUNT(*) FROM tiles GROUP BY zoom_level ORDER BY zoom_level'):
    print(f"  z{row[0]}: {row[1]} tiles")

print("\n" + "=" * 60)
print("SAMPLE TILE:")
print("=" * 60)
sample = conn.execute('SELECT zoom_level, tile_column, tile_row, length(tile_data) FROM tiles LIMIT 1').fetchone()
if sample:
    print(f"  z{sample[0]}/{sample[1]}/{sample[2]}: {sample[3]} bytes")
else:
    print("  No tiles found!")

conn.close()