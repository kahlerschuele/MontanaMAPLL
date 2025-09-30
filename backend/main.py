"""
FastAPI Tile Server
Main application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import settings
from tiles import get_ownership_tile
import json
from pathlib import Path

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


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "US Ownership Tile Server",
        "version": "1.0.1",
        "endpoints": {
            "health": "/health",
            "tiles": "/tiles/ownership/{z}/{x}/{y}.pbf",
            "ownership_data": "/data/ownership.geojson",
            "parcels_data": "/data/parcels.geojson"
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