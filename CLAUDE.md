# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A web mapping application that displays US public land ownership (federal, state, local, tribal) on satellite imagery, with support for Montana property parcels. Built with FastAPI backend serving vector tiles and a React + MapLibre GL frontend.

## Quick Start Commands

### Development
```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install

# Start backend server (from backend/)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Start frontend dev server (from frontend/)
npm run dev

# Build frontend for production
npm run build

# Preview production build
npm run preview
```

### Data Pipeline
```bash
# Download PAD-US dataset (~5GB)
bash scripts/padus_download.sh

# Prepare and normalize PAD-US data
python scripts/padus_prepare.py

# Build vector tiles (requires tippecanoe on Linux/Mac/WSL)
bash scripts/build_tiles.sh

# Windows alternative (simplified Python-based tiles)
python scripts/build_tiles.py
```

## Architecture

### Backend (FastAPI)
- **backend/main.py** - FastAPI application with CORS, tile serving, and GeoJSON endpoints
- **backend/tiles.py** - TileServer class that serves MBTiles via SQLite with XYZ→TMS coordinate flipping
- **backend/settings.py** - Configuration (paths, CORS origins, cache settings)

**Key endpoints:**
- `GET /` - API info
- `GET /health` - Health check
- `GET /tiles/ownership/{z}/{x}/{y}.pbf` - Vector tiles (gzipped protobuf)
- `GET /data/ownership.geojson` - Full PAD-US dataset as GeoJSON
- `GET /data/parcels.geojson` - Montana test parcel data

### Frontend (React + MapLibre GL)
- **frontend/src/main.tsx** - React app entry point
- **frontend/src/map/OwnershipMap.tsx** - Main map component with satellite basemap, ownership layers, parcel layers, popups
- **frontend/src/ui/** - Legend and Attribution components
- **frontend/src/map/style.json** - MapLibre style configuration (if using vector tiles instead of GeoJSON)

**Technology stack:**
- MapLibre GL JS 3.x for vector + raster rendering
- React 18 with TypeScript
- Zustand for state management
- Vite for build tooling

### Data Pipeline (ETL)
- **scripts/padus_download.sh** - Downloads PAD-US GeoPackage from USGS ScienceBase
- **scripts/padus_prepare.py** - Normalizes PAD-US attributes, validates geometries, creates NDJSON and dissolved GeoJSON
  - Maps owner/manager types to 5 classes: federal, state, local, tribal, other_public
  - Outputs `data/padus/padus_clean.ndjson` (all features) and `data/padus/padus_dissolved.geojson` (dissolved by class)
- **scripts/build_tiles.sh** - Uses tippecanoe to create two-tier vector tiles (Linux/Mac/WSL)
- **scripts/build_tiles.py** - Python fallback for Windows (creates simplified GeoJSON tiles, not MVT)

### Data Structure
- **data/padus/** - PAD-US source data and processed outputs
- **data/tiles/** - MBTiles output (ownership.mbtiles)
- **data/parcels/** - Montana parcel test data

## Two-Tier Tile Strategy

The application uses a two-layer approach for performance:

1. **padus_low** (z4-z9): Dissolved geometries by owner_class, solid outlines, no fill
2. **padus_hi** (z10-z14): Original detailed features, dashed outlines + transparent fill

This reduces tile sizes at low zooms while maintaining detail at high zooms.

## Owner Classification

Five normalized classes derived from PAD-US Owner_Type and Manager_Type fields:

- **federal** (blue #1d4ed8): BLM, USFS, NPS, FWS, DOD, BOR, etc.
- **state** (green #059669): State parks, forests, wildlife areas
- **local** (purple #7c3aed): County, city, regional parks
- **tribal** (orange #b45309): Tribal lands
- **other_public** (cyan #0ea5e9): NGO, joint management

See `padus_prepare.py:map_owner_class()` for mapping logic.

## Coordinate Systems

- **MBTiles** uses TMS (Tile Map Service) scheme with origin at bottom-left
- **Web maps** use XYZ scheme with origin at top-left
- **tiles.py** flips Y coordinate: `tile_row = (1 << z) - 1 - y`

## Current Data Mode

The map currently loads full GeoJSON datasets via HTTP (`/data/ownership.geojson` and `/data/parcels.geojson`) rather than vector tiles. This simplifies development but doesn't scale well. To use vector tiles:

1. Build tiles using `build_tiles.sh` or `build_tiles.py`
2. Update `OwnershipMap.tsx` to use vector tile sources (see `style.json` for reference)
3. Ensure tile server is running

## Geometry Validation

All PAD-US geometries are validated and fixed using Shapely's `make_valid()` during the prepare step. Invalid geometries are logged and skipped.

## Dependencies

**Backend:**
- fastapi
- uvicorn[standard]
- python-dotenv

**Frontend:**
- maplibre-gl
- react, react-dom
- zustand
- vite, @vitejs/plugin-react
- typescript

**ETL (Linux/Mac):**
- GDAL/OGR (ogr2ogr)
- tippecanoe 2.42+
- Python: gdal, shapely

**ETL (Windows):**
- Python: gdal, shapely (tippecanoe not required for simplified build)

## Performance Notes

- Tile cache headers set to 1 year (`immutable`)
- Target tile sizes: <75KB at z≤8, <200KB at z≤10
- Zoom range: z3-z20 (map), z4-z14 (tiles)
- USGS satellite basemap from National Map (256px tiles)

## Testing Location

Default map center: Bozeman, Montana area (-111.0425, 45.6780) at z16 for testing Montana parcel data.