from pathlib import Path

# shared data directory, resolved relative to this file so cwd doesn't matter
DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "natural-earth"

# maps a layer name in the API route to its GeoJSON file on disk
GEO_LAYERS = {
    "countries": DATA_DIR / "countries.geojson",
    "coastline": DATA_DIR / "coastline.geojson",
    "ocean": DATA_DIR / "ocean.geojson",
}

# origins allowed to call the API — just the vite dev server for now
CORS_ALLOW_ORIGINS = ["http://localhost:5173"]
