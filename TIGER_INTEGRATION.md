# Census TIGER Data Integration - Complete

## Overview
Successfully integrated US Census Bureau TIGER/Line 2023 data into the Montana Property Map, adding demographic and administrative boundary layers.

## Data Integrated

### 1. Counties (56 features, 371 KB)
- All Montana counties
- Includes FIPS codes, names, land/water area
- Purple boundaries (#4B0082)

### 2. Census Tracts (319 features, 1.1 MB)
- Statistical subdivisions for demographic analysis
- Used for detailed population and economic data
- Red boundaries (#FF6B6B)

### 3. Block Groups (900 features, 1.8 MB)
- Finest-grained demographic areas
- ~1,000-3,000 people per block group
- Cyan boundaries (#4ECDC4)

### 4. Places (497 features, 556 KB)
- Incorporated cities and Census Designated Places
- Includes towns, cities, and unincorporated communities
- Yellow boundaries (#F7DC6F)

## Files Added

### Scripts
- `scripts/download_tiger_simple.py` - Downloads and converts TIGER data using geopandas
- Automatically filters to Montana where needed
- Simplifies geometries to reduce file sizes

### Data Files
```
data/tiger/
├── counties.geojson      (371 KB)
├── tracts.geojson        (1.1 MB)
├── blockgroups.geojson   (1.8 MB)
└── places.geojson        (556 KB)
```

### Backend Endpoints
Added to `backend/main.py`:
- `GET /data/tiger/counties.geojson`
- `GET /data/tiger/tracts.geojson`
- `GET /data/tiger/blockgroups.geojson`
- `GET /data/tiger/places.geojson`

### Frontend Features
Updated `frontend/public/map.html`:
- Added TIGER boundary layers with toggleable visibility
- Color-coded by boundary type
- Click boundaries to see details (GEOID, area, FIPS codes)
- Legend checkboxes for each layer type
- Layers load on map startup but hidden by default

## Usage

### Viewing TIGER Boundaries
1. Open the map at http://localhost:5176/map.html
2. Look for "Census Boundaries" section in the legend (top-right)
3. Check the boxes to toggle layers:
   - ☐ Counties (56)
   - ☐ Census Tracts (319)
   - ☐ Block Groups (900)
   - ☐ Places (497)

### Clicking Boundaries
Click any boundary to see a popup with:
- Name
- GEOID (Census Geographic Identifier)
- State and County FIPS codes
- Land area in square miles
- Water area in square miles

## Analysis Capabilities Enabled

### 1. Property Analysis by Area
- Identify which census tract a parcel belongs to
- Compare property values across different tracts/counties
- Analyze parcel density by block group

### 2. Energy Production by Region
- See which counties have the most oil/gas wells
- Analyze production concentration by census tract
- Identify demographic areas near drilling activity

### 3. Water Rights Distribution
- Map water rights allocation across counties
- Compare agricultural vs residential water use by tract
- Identify high-density irrigation areas

### 4. Investment Screening
- Find underdeveloped areas in high-value census tracts
- Identify growth corridors using place boundaries
- Compare rural vs urban property characteristics

## Technical Details

### Data Source
- **US Census Bureau TIGER/Line 2023 Cartographic Boundary Files**
- URL: https://www2.census.gov/geo/tiger/GENZ2023/shp/
- These are simplified (500k) versions optimized for web mapping
- Already generalized, smaller than full TIGER/Line files

### Processing
- Downloaded as shapefiles
- Converted to GeoJSON using geopandas
- Geometries simplified with 0.001-degree tolerance
- Montana-only filtering for nationwide datasets (counties)

### Rendering
- MapLibre GL JS vector layers
- Fill + line rendering for each boundary type
- Semi-transparent fills to see underlying satellite imagery
- Colored outlines for clear delineation
- Hidden by default to avoid clutter

## Performance
- Total TIGER data: ~3.8 MB (compressed ~1.2 MB with gzip)
- Loads asynchronously on map initialization
- No impact on initial page load
- Click events only on visible layers
- Boundaries cached by browser after first load

## Future Enhancements

### Demographics Integration
Could add American Community Survey (ACS) data via Census API:
- Population by tract
- Median household income
- Age distribution
- Housing statistics
- Employment data

### Analysis Tools
- Buffer zones around boundaries
- Spatial queries (e.g., "wells within 1 mile of residential tracts")
- Statistical overlays (choropleth maps by income/population)
- Export boundary + property data as CSV

### Additional TIGER Layers
Not yet integrated but could add:
- Roads (primary, secondary, local)
- Railways
- ZIP Code Tabulation Areas (ZCTAs)
- School districts
- Tribal boundaries (detailed)

## Maintenance

### Updating TIGER Data
Run annually when Census releases new TIGER/Line files:
```bash
cd scripts
python download_tiger_simple.py
```

This will download the latest TIGER boundaries for Montana.

### Backend Restart Required
After downloading new data, restart the backend:
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

## Data Attribution
**Source**: U.S. Census Bureau TIGER/Line Shapefiles 2023
**License**: Public Domain (U.S. Government Work)
**URL**: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
