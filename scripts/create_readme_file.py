#!/usr/bin/env python3
"""Create README.md for Montana Property Map"""

readme_content = """# Montana Property Map with Census TIGER Data

Interactive web mapping application for Montana with property parcels, US Census TIGER boundaries, ACS demographics, water rights, and oil/gas data.

## Features

- **US State Boundaries** - All 56 states and territories
- **Montana Counties** - 56 counties with demographic data
- **Census Tracts** - 319 tracts with income choropleth
- **City Labels** - 497 places with smart filtering
- **Property Parcels** - Montana cadastral data
- **Demographics** - Population, income, housing statistics
- **Water Rights** - DNRC integration
- **Oil/Gas Wells** - Production data

## Required Downloads

**You MUST run these scripts before using the map:**

```bash
# Download US state boundaries (8.2 MB)
python scripts/download_us_states.py

# Download Montana TIGER data
python scripts/download_tiger_montana.py

# Download census tract demographics
python scripts/download_acs_data.py

# Download county demographics
python scripts/download_county_acs.py
```

These scripts download from US Census Bureau and create GeoJSON files in `data/tiger/` and `frontend/public/data/tiger/`.

## Prerequisites

- Python 3.8+ with `geopandas`, `shapely`, `fastapi`, `uvicorn`, `httpx`
- Node.js 16+ with npm
- GDAL/OGR

```bash
# Install Python dependencies
pip install fastapi uvicorn[standard] python-dotenv geopandas shapely httpx

# Install frontend dependencies
cd frontend
npm install
```

## Backend Connections

The backend connects to public Montana GIS APIs (no keys needed):

- **DNRC Water Rights:** gis.dnrc.mt.gov/arcgis/rest/services/WRD/WRQS
- **DNRC Oil & Gas:** gis.dnrc.mt.gov/arcgis/rest/services/BOG/DataMiner
- **MT Parcels:** gisservicemt.gov/arcgis/rest/services/MSDI_Framework/Parcels
- **MT Hydrography:** gisservicemt.gov/arcgis/rest/services/MSDI_Framework/Hydrography

All are public ArcGIS REST services.

## Running the Application

**Start Backend:**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Start Frontend:**
```bash
cd frontend
npm run dev
```

Open http://localhost:5173 (or port shown by Vite)

## Map Controls

- **Zoom 0-6:** US states
- **Zoom 5-10:** Montana counties (click for demographics)
- **Zoom 8-14:** Census tracts (income choropleth, clickable)
- **Zoom 14+:** Property parcels (double-click for details)

## Technology

- **Frontend:** MapLibre GL JS, React, TypeScript, Vite
- **Backend:** FastAPI, GDAL/OGR
- **Data:** US Census TIGER/Line 2023, ACS 2022

## Credits

- Montana State Library - Cadastral data
- US Census Bureau - TIGER/ACS
- Montana DNRC - Water/Oil data
- Esri - Satellite basemap

---

Last Updated: October 2025
"""

# Write README
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)

print("README.md created successfully!")
