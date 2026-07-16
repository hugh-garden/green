import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ALLOW_ORIGINS, GEO_LAYERS

app = FastAPI(title="green")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["*"],
)


# retrieve geospatial info for map rendering
@app.get("/api/geo/{layer_name}")
def get_geo_layer(layer_name: str) -> dict:
    path = GEO_LAYERS.get(layer_name)
    if path is None:
        raise HTTPException(status_code=404, detail=f"Unknown layer: {layer_name}")
    return json.loads(path.read_text())
