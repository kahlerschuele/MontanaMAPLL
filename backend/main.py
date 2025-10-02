"""
FastAPI Tile Server
Main application entry point
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import settings
from tiles import get_ownership_tile
import json
from pathlib import Path
from production_db import get_well_production
from eia_api import get_all_montana_data, format_eia_data_for_display
from ais_stream import ais_manager
import asyncio

app = FastAPI(
    title="US Ownership Tile Server",
    description="Serves PAD-US vector tiles and GeoJSON data",
    version="1.0.1"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Start AIS stream manager on application startup"""
    asyncio.create_task(ais_manager.start())


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Montana Property & Energy Map API",
        "version": "1.1.0",
        "endpoints": {
            "health": "/health",
            "tiles": "/tiles/ownership/{z}/{x}/{y}.pbf",
            "ownership_data": "/data/ownership.geojson",
            "parcels_data": "/data/parcels.geojson",
            "well_production": "/api/well-production/{api_number}",
            "eia_montana": "/api/eia/montana-data",
            "ais_websocket": "/ws/ais",
            "tiger_counties": "/data/tiger/counties.geojson",
            "tiger_tracts": "/data/tiger/tracts.geojson",
            "tiger_blockgroups": "/data/tiger/blockgroups.geojson",
            "tiger_places": "/data/tiger/places.geojson",
            "tiger_zipcodes": "/data/tiger/zipcodes.geojson"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/tiles/ownership/{z}/{x}/{y}.pbf")
async def tiles_endpoint(z: int, x: int, y: int):
    """
    Serve ownership vector tiles.

    Args:
        z: Zoom level (4-14)
        x: Tile column
        y: Tile row

    Returns:
        Vector tile (gzipped protobuf)
    """
    return await get_ownership_tile(z, x, y)


@app.get("/data/ownership.geojson")
async def get_ownership_geojson():
    """
    Serve complete ownership data as GeoJSON.
    For simple rendering without vector tiles.
    """
    # Path is relative to backend/ directory, go up one level to project root
    geojson_path = Path(__file__).parent.parent / "data" / "padus" / "padus_clean.ndjson"

    # Resolve to absolute path to debug
    geojson_path = geojson_path.resolve()

    if not geojson_path.exists():
        raise HTTPException(status_code=404, detail=f"GeoJSON not found at {geojson_path}")

    # Load all features
    features = []
    with open(geojson_path, 'r') as f:
        for line in f:
            if line.strip():
                features.append(json.loads(line))

    return {
        "type": "FeatureCollection",
        "features": features
    }


@app.get("/data/parcels.geojson")
async def get_parcels_geojson():
    """
    Serve test parcel data as GeoJSON.
    """
    # Path is relative to backend/ directory, go up one level to project root
    parcels_path = Path(__file__).parent.parent / "data" / "parcels" / "test_parcels.geojson"

    # Resolve to absolute path to debug
    parcels_path = parcels_path.resolve()

    if not parcels_path.exists():
        raise HTTPException(status_code=404, detail=f"Parcel data not found at {parcels_path}")

    with open(parcels_path, 'r') as f:
        return json.load(f)


@app.get("/api/well-production/{api_number}")
async def get_well_production_endpoint(api_number: str):
    """
    Fetch production data for a specific well by API number.

    Args:
        api_number: Well API number (e.g., "25001050000000")

    Returns:
        Production data including barrels per day, cumulative totals, and monthly history
    """
    if not api_number:
        raise HTTPException(status_code=400, detail="API number is required")

    # Fetch production data from local database
    production_data = get_well_production(api_number)

    if production_data is None:
        raise HTTPException(
            status_code=404,
            detail=f"No production data found for API number {api_number}. "
                   f"Have you imported the production data? See PRODUCTION_DATA_SETUP.md"
        )

    return production_data


@app.get("/api/eia/montana-data")
async def get_montana_eia_data():
    """
    Fetch all EIA data categories for Montana

    Returns:
        Dictionary with crude oil production, reserves, drilling activity, etc.
    """
    data = await get_all_montana_data()

    # Format each category for display
    formatted_data = {}
    for category, raw_data in data.items():
        if raw_data:
            formatted_data[category] = format_eia_data_for_display(raw_data)
        else:
            formatted_data[category] = []

    return formatted_data


@app.get("/data/tiger/montana_state.geojson")
async def get_montana_state():
    """Serve Montana state boundary from TIGER/Line"""
    tiger_path = Path(__file__).parent.parent / "data" / "tiger" / "montana_state.geojson"
    if not tiger_path.exists():
        raise HTTPException(status_code=404, detail=f"State boundary not found at {tiger_path}")
    with open(tiger_path, 'r') as f:
        return json.load(f)


@app.get("/data/tiger/counties.geojson")
async def get_tiger_counties():
    """Serve Montana counties from TIGER/Line"""
    tiger_path = Path(__file__).parent.parent / "data" / "tiger" / "counties.geojson"
    if not tiger_path.exists():
        raise HTTPException(status_code=404, detail=f"Counties data not found at {tiger_path}")
    with open(tiger_path, 'r') as f:
        return json.load(f)


@app.get("/data/tiger/tracts.geojson")
async def get_tiger_tracts():
    """Serve Montana census tracts from TIGER/Line"""
    tiger_path = Path(__file__).parent.parent / "data" / "tiger" / "tracts.geojson"
    if not tiger_path.exists():
        raise HTTPException(status_code=404, detail=f"Tracts data not found at {tiger_path}")
    with open(tiger_path, 'r') as f:
        return json.load(f)


@app.get("/data/tiger/blockgroups.geojson")
async def get_tiger_blockgroups():
    """Serve Montana census block groups from TIGER/Line"""
    tiger_path = Path(__file__).parent.parent / "data" / "tiger" / "blockgroups.geojson"
    if not tiger_path.exists():
        raise HTTPException(status_code=404, detail=f"Block groups data not found at {tiger_path}")
    with open(tiger_path, 'r') as f:
        return json.load(f)


@app.get("/data/tiger/places.geojson")
async def get_tiger_places():
    """Serve Montana incorporated places from TIGER/Line"""
    tiger_path = Path(__file__).parent.parent / "data" / "tiger" / "places.geojson"
    if not tiger_path.exists():
        raise HTTPException(status_code=404, detail=f"Places data not found at {tiger_path}")
    with open(tiger_path, 'r') as f:
        return json.load(f)


@app.get("/data/tiger/zipcodes.geojson")
async def get_tiger_zipcodes():
    """Serve Montana ZIP Code Tabulation Areas from TIGER/Line"""
    tiger_path = Path(__file__).parent.parent / "data" / "tiger" / "zipcodes.geojson"
    if not tiger_path.exists():
        raise HTTPException(status_code=404, detail=f"ZIP codes data not found at {tiger_path}")
    with open(tiger_path, 'r') as f:
        return json.load(f)


@app.websocket("/ws/ais")
async def websocket_ais_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for AIS vessel tracking data

    Connects clients to the AIS stream and broadcasts vessel positions
    """
    await ais_manager.add_client(websocket)

    try:
        while True:
            # Keep connection alive and handle client messages if needed
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ais_manager.remove_client(websocket)
