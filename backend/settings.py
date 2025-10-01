"""
Server Settings
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
MBTILES_PATH = BASE_DIR / "data" / "tiles" / "ownership.mbtiles"

# CORS
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    "http://127.0.0.1:5176",
    "http://127.0.0.1:3000",
]

# Cache
TILE_CACHE_MAX_AGE = 31536000  # 1 year in seconds