# MontanaMAPLL

Interactive map showing Montana property boundaries with detailed parcel information on high-quality satellite imagery.

## Features

- **Real Montana cadastral data**: Official parcel boundaries from Montana State Library MSDI Framework
- **High-quality satellite basemap**: Esri World Imagery (no API key required)
- **Detailed property information**: Owner name, acreage, assessed values, legal description, land use breakdown
- **Interactive parcels**: Click any property to see full details
- **Dynamic loading**: Fetches parcels on-demand as you pan around Montana
- **White property lines**: Clean onX-style visualization with black casing
- **100% free data**: No paid services or API keys required

## Quick Start

### Option 1: Standalone HTML (Easiest)

Open `frontend/public/map.html` in any modern web browser - no setup required!

Or serve it locally:
```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5174/map.html`

### Option 2: Full Development Setup

**1. Backend (FastAPI)**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

**2. Frontend (React + Vite)**
```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5174`

## Project Structure

```
montana-map/
├── frontend/
│   ├── public/
│   │   ├── map.html                    # Standalone working map (use this!)
│   │   └── montana_parcels_WORKING.html # Backup version
│   ├── src/                            # React components
│   └── package.json
├── backend/
│   ├── main.py                         # FastAPI server
│   └── requirements.txt
├── data/
│   └── parcels/                        # Sample parcel data
└── scripts/                            # Data fetching scripts
```

## How It Works

The map uses the **Montana State Library MSDI Parcels** service to fetch real parcel data:

- **Data source**: `https://gisservicemt.gov/arcgis/rest/services/MSDI_Framework/Parcels/MapServer`
- **Update frequency**: Monthly from Montana Department of Revenue
- **Coverage**: All 56 Montana counties
- **Parcel limit**: 2,000 parcels per view (dynamically loaded)

When you zoom to level 13+, the map queries the API for parcels in your current view and displays:
- Parcel ID
- Owner name and mailing address
- Property address
- Total acres and property type
- Assessment values (total, land, building)
- Tax year
- Legal description (Township/Range/Section)
- Land use breakdown (irrigated, grazing, forest, crop acres)
- County name

## Data Fields

All parcel data comes from Montana's cadastral database. Click any parcel to see:

| Field | Description |
|-------|-------------|
| PARCELID | Unique parcel identifier |
| OwnerName | Property owner name |
| OwnerAddress | Owner mailing address (street, city, state, zip) |
| AddressLine1/2 | Property situs address |
| GISAcres | Total parcel acreage |
| PropType | Property type/classification |
| TotalValue | Total assessed value |
| TotalLandValue | Land-only assessed value |
| TotalBuildingValue | Improvement/building value |
| TaxYear | Assessment year |
| Township/Range/Section | Legal description (PLSS) |
| LegalDescriptionShort | Short legal description |
| Subdivision | Subdivision name (if applicable) |
| IrrigatedAcres | Irrigated land acreage |
| GrazingAcres | Grazing land acreage |
| ForestAcres | Forest land acreage |
| ContinuousCropAcres | Cropland acreage |
| CountyName | Montana county |

## Tech Stack

**Frontend:**
- MapLibre GL JS 3.6.2 (vector map rendering)
- Vanilla JavaScript (standalone map)
- React 18 + TypeScript (development version)
- Vite (build tool)

**Backend:**
- FastAPI (Python)
- CORS-enabled for local development

**Data:**
- Montana State Library MSDI Framework (live API)
- Esri World Imagery (satellite basemap)

## Performance

- Parcels only load when zoomed to level 13+
- Maximum 2,000 parcels per viewport
- Data fetched on-demand (no large downloads)
- Works across all of Montana

## Future Enhancements

- Historical tax data
- Property sales history
- Zoning information
- Public land overlay (PAD-US)
- Search by owner name or parcel ID
- Export parcel data to CSV/GeoJSON
- Mobile optimization

## License

MIT License

**Data licenses:**
- Montana Cadastral Data: Public Domain (Montana State Library)
- Esri World Imagery: Free for non-commercial use

## Credits

Built using:
- [MapLibre GL JS](https://maplibre.org/)
- [Montana State Library MSDI Framework](https://msl.mt.gov/geoinfo/msdi/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)

Data from:
- [Montana State Library - Cadastral](https://msl.mt.gov/geoinfo/msdi/cadastral/)
- [Esri World Imagery](https://www.esri.com/en-us/arcgis/products/data/data-portfolio/world-imagery)

🤖 Built with [Claude Code](https://claude.com/claude-code)