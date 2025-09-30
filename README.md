# US Ownership Map

A fast, accurate web map showing US public land ownership (federal, state, local, tribal) on satellite imagery.

## Features

- **Satellite basemap**: USGS National Map imagery
- **Public land boundaries**: PAD-US (Protected Areas Database)
- **Two-tier vector tiles**: Fast at low zoom, detailed at high zoom
- **Interactive**: Click parcels for ownership details
- **No paid services**: 100% open data and free tile endpoints

## Project Structure

```
us-ownership/
├── server/          # FastAPI tile server
├── etl/             # Data processing scripts
├── web/             # React + MapLibre frontend
└── data/            # PAD-US data and MBTiles output
```

## Prerequisites

**System dependencies:**
- Python 3.11+
- Node.js 18+
- GDAL 3.4+ (ogr2ogr)
- tippecanoe 2.42+

**Install tippecanoe:**
```bash
# macOS
brew install tippecanoe

# Ubuntu/Debian
sudo apt-get install tippecanoe

# Or build from source: https://github.com/felt/tippecanoe
```

**Install GDAL:**
```bash
# macOS
brew install gdal

# Ubuntu/Debian
sudo apt-get install gdal-bin python3-gdal

# Windows
# Use OSGeo4W: https://trac.osgeo.org/osgeo4w/
```

## Setup

### 1. Install Python dependencies

```bash
cd server
pip install -r requirements.txt
```

### 2. Install Node dependencies

```bash
cd web
npm install
```

## Build Data Pipeline

### Step 1: Download PAD-US

```bash
bash etl/padus_download.sh
```

Downloads ~5GB PAD-US dataset to `data/padus/`

### Step 2: Prepare data

```bash
python etl/padus_prepare.py
```

Normalizes PAD-US attributes and outputs:
- `data/padus/padus_clean.ndjson` (all features)
- `data/padus/padus_dissolved.geojson` (dissolved by owner_class)

### Step 3: Build vector tiles

```bash
bash etl/build_tiles.sh
```

Generates `data/tiles/ownership.mbtiles` (~800MB) with:
- **padus_low** layer (z4-z9): Dissolved boundaries
- **padus_hi** layer (z10-z14): Original features

**Build time:** ~10-30 minutes depending on hardware

## Run Application

### Start tile server

```bash
cd server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Server runs at `http://localhost:8000`

**Endpoints:**
- `GET /health` - Health check
- `GET /tiles/ownership/{z}/{x}/{y}.pbf` - Vector tiles

### Start web app

```bash
cd web
npm run dev
```

App runs at `http://localhost:5173`

## Performance

- **Tile sizes**: <75KB at z≤8, <200KB at z≤10
- **Load time**: <2s on national view (typical laptop)
- **Zoom range**: z3-z16
- **Caching**: Immutable tiles cached for 1 year

## Data Sources

| Layer | Source | License |
|-------|--------|---------|
| Satellite imagery | USGS National Map | Public Domain |
| Public land boundaries | PAD-US 3.0 | Public Domain |

**PAD-US date:** September 2023 (update `ASOF_DATE` in `etl/padus_prepare.py`)

## Color Legend

- **Federal** (blue): BLM, USFS, NPS, FWS, DOD, etc.
- **State** (green): State parks, forests, wildlife areas
- **Local** (purple): County, city, regional parks
- **Tribal** (orange): Tribal lands
- **Other Public** (cyan): NGO, joint management

## Architecture

### ETL Pipeline

1. **Download**: PAD-US GeoPackage from ScienceBase
2. **Normalize**: Extract 5 fields (owner_class, owner_name, unit_name, source, asof)
3. **Dissolve**: Union by owner_class for low zooms
4. **Tile**: tippecanoe with two-tier zoom strategy

### Tile Server

- **FastAPI** serves MBTiles via SQLite read-only connection
- **Y-flip**: Converts XYZ → TMS for MBTiles compatibility
- **Headers**: Gzip + immutable caching

### Frontend

- **MapLibre GL JS 3.x**: Vector + raster rendering
- **React 18**: UI components
- **Two layers**:
  - `padus_low` (z4-z9): Solid outlines, no fill
  - `padus_hi` (z10-z14): Dashed outlines + transparent fill

## Scaling & Optimization

**To reduce tile size:**
- Increase `--simplification` in tippecanoe
- Add `--drop-smallest-as-needed`
- Reduce max zoom to z12

**To add more data:**
- Add new source to `style.json`
- Create separate MBTiles for each dataset
- Mount new tile endpoint in FastAPI

## Future Enhancements (Out of Scope)

- Private parcel boundaries (requires commercial data)
- Property owner search
- Wells, pipelines, trails
- 3D terrain
- Mobile apps

## Troubleshooting

**"MBTiles file not found"**
- Run `bash etl/build_tiles.sh` first
- Check `data/tiles/ownership.mbtiles` exists

**"tippecanoe: command not found"**
- Install tippecanoe (see Prerequisites)

**Tiles not loading in browser**
- Verify server running: `curl http://localhost:8000/health`
- Check CORS in browser console
- Confirm tile path in `web/src/map/style.json`

**Slow performance**
- Reduce max zoom in `build_tiles.sh`
- Increase simplification tolerance
- Check tile sizes: `sqlite3 data/tiles/ownership.mbtiles "SELECT zoom_level, COUNT(*), AVG(LENGTH(tile_data)) FROM tiles GROUP BY zoom_level"`

## License

MIT License - See LICENSE file

**Data licenses:**
- USGS Imagery: Public Domain
- PAD-US: Public Domain (CC0)

## Credits

Built using:
- [MapLibre GL JS](https://maplibre.org/)
- [tippecanoe](https://github.com/felt/tippecanoe)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)

Data from:
- [USGS National Map](https://www.usgs.gov/programs/national-geospatial-program/national-map)
- [PAD-US](https://www.usgs.gov/programs/gap-analysis-project/science/pad-us-data-overview)