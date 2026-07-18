from pathlib import Path

# shared data directory, resolved relative to this file so cwd doesn't matter
DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "natural-earth"

# maps a layer name in the API route to its GeoJSON file on disk
GEO_LAYERS = {
    "countries": DATA_DIR / "countries.geojson",
    "coastline": DATA_DIR / "coastline.geojson",
    "ocean": DATA_DIR / "ocean.geojson",
    "states": DATA_DIR / "states.geojson",
    "subunits": DATA_DIR / "subunits.geojson",
}

# worldclim raster data directory
CLIMATE_DIR = Path(__file__).resolve().parents[2] / "data" / "worldclim"

# maps a climate variable name to its compressed raster on disk
CLIMATE_LAYERS = {
    "annual_mean_temp": CLIMATE_DIR / "annual_mean_temp.npz",
    "annual_precip": CLIMATE_DIR / "annual_precip.npz",
    "elevation": CLIMATE_DIR / "elevation.npz",
}

# origins allowed to call the API — just the vite dev server for now
CORS_ALLOW_ORIGINS = ["http://localhost:5173"]
