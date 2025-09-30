"""
Vector Tile Server
Serves MBTiles via HTTP endpoints
"""

import sqlite3
from pathlib import Path
from fastapi import HTTPException
from fastapi.responses import Response
import settings


class TileServer:
    def __init__(self, mbtiles_path: Path):
        self.mbtiles_path = mbtiles_path
        self._connection = None

    def _get_connection(self):
        """Get or create database connection."""
        if self._connection is None:
            if not self.mbtiles_path.exists():
                raise FileNotFoundError(f"MBTiles file not found: {self.mbtiles_path}")

            self._connection = sqlite3.connect(
                str(self.mbtiles_path),
                check_same_thread=False,
                uri=True
            )
        return self._connection

    def get_tile(self, z: int, x: int, y: int) -> bytes:
        """
        Retrieve a vector tile from MBTiles.

        Args:
            z: Zoom level
            x: Tile column
            y: Tile row (TMS scheme, flipped from XYZ)

        Returns:
            Tile data as bytes (gzipped protobuf)
        """
        # Flip Y coordinate (MBTiles uses TMS, web maps use XYZ)
        tile_row = (1 << z) - 1 - y

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?",
            (z, x, tile_row)
        )

        row = cursor.fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Tile not found")

        return row[0]


# Global tile server instance
tile_server = TileServer(settings.MBTILES_PATH)


async def get_ownership_tile(z: int, x: int, y: int):
    """
    FastAPI endpoint for ownership tiles.

    GET /tiles/ownership/{z}/{x}/{y}.pbf
    """
    try:
        tile_data = tile_server.get_tile(z, x, y)

        return Response(
            content=tile_data,
            media_type="application/x-protobuf",
            headers={
                "Content-Encoding": "gzip",
                "Cache-Control": f"public, max-age={settings.TILE_CACHE_MAX_AGE}, immutable",
                "Access-Control-Allow-Origin": "*",
            }
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tile: {str(e)}")