#!/usr/bin/env bash
set -euo pipefail

# PAD-US Download Script
# Downloads the latest PAD-US national dataset

PADUS_DIR="data/padus"
PADUS_URL="https://www.sciencebase.gov/catalog/file/get/6596f0d1d34e176b9e694b3a"

echo "Downloading PAD-US dataset..."
echo "This may take several minutes (file is ~5GB)"

mkdir -p "$PADUS_DIR"

# Download PAD-US GeoPackage (latest version)
curl -L -o "$PADUS_DIR/PADUS3_0_Geopackage.zip" \
  "https://www.sciencebase.gov/catalog/file/get/6596f0d1d34e176b9e694b3a?f=__disk__d0%2F56%2F96%2Fd05696f0d34e176b9e694b3a"

echo "Extracting..."
cd "$PADUS_DIR"
unzip -o PADUS3_0_Geopackage.zip

echo "Download complete. PAD-US data ready in $PADUS_DIR"