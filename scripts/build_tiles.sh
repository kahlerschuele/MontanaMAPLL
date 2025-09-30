#!/usr/bin/env bash
set -euo pipefail

# Vector Tile Build Script
# Builds two-tier MBTiles from PAD-US data using tippecanoe

LOW=data/padus/padus_dissolved.geojson
HI=data/padus/padus_clean.ndjson
OUT=data/tiles/ownership.mbtiles

# Check inputs
if [[ ! -f "$LOW" ]]; then
  echo "ERROR: $LOW not found. Run padus_prepare.py first"
  exit 1
fi

if [[ ! -f "$HI" ]]; then
  echo "ERROR: $HI not found. Run padus_prepare.py first"
  exit 1
fi

# Check tippecanoe
if ! command -v tippecanoe &> /dev/null; then
  echo "ERROR: tippecanoe not found"
  echo "Install with: brew install tippecanoe  (macOS)"
  echo "            or build from: https://github.com/felt/tippecanoe"
  exit 1
fi

echo "Building vector tiles..."
echo "  Low-zoom layer (z4-z9): $LOW"
echo "  High-zoom layer (z10-z14): $HI"
echo "  Output: $OUT"
echo ""

# Remove existing output
rm -f "$OUT"

# Layer 1: low-zoom dissolved (z4-z9)
echo "Step 1/3: Building low-zoom layer (z4-z9)..."
tippecanoe \
  -o "$OUT" \
  -l padus_low \
  -Z4 -z9 \
  --no-feature-limit \
  --no-tile-size-limit \
  --simplification=4 \
  --detect-shared-borders \
  --coalesce \
  --coalesce-densest-as-needed \
  --drop-densest-as-needed \
  --extend-zooms-if-still-dropping \
  "$LOW"

echo "✓ Low-zoom layer complete"
echo ""

# Layer 2: high-zoom original features (z10-z14)
echo "Step 2/3: Building high-zoom layer (z10-z14)..."
tippecanoe \
  -o "$OUT" \
  --force \
  -l padus_hi \
  -Z10 -z14 \
  --no-feature-limit \
  --no-tile-size-limit \
  --simplification=1.5 \
  --detect-shared-borders \
  --coalesce-densest-as-needed \
  --extend-zooms-if-still-dropping \
  --accumulate-attribute=owner_class:string \
  --accumulate-attribute=owner_name:string \
  --accumulate-attribute=unit_name:string \
  --accumulate-attribute=source:string \
  --accumulate-attribute=asof:string \
  "$HI"

echo "✓ High-zoom layer complete"
echo ""

# Step 3: Optimize (optional, if tile-join available)
if command -v tile-join &> /dev/null; then
  echo "Step 3/3: Optimizing MBTiles..."
  tile-join -f -o "$OUT" "$OUT"
  echo "✓ Optimization complete"
else
  echo "Step 3/3: Skipping optimization (tile-join not found)"
fi

echo ""
echo "✓ Tile build complete!"
echo "  Output: $OUT"

# Show file size
if command -v du &> /dev/null; then
  SIZE=$(du -h "$OUT" | cut -f1)
  echo "  Size: $SIZE"
fi

echo ""
echo "Next step: Start the tile server (cd server && uvicorn main:app --reload)"