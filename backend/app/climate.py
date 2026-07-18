import numpy as np

from .config import CLIMATE_LAYERS

# worldclim rasters mark missing data (ocean, no coverage) with a large negative sentinel
NODATA_THRESHOLD = -30000

_arrays: dict[str, np.ndarray] = {}


# lazily load and cache a layer's raster array
def _load(layer_name: str) -> np.ndarray:
    if layer_name not in _arrays:
        _arrays[layer_name] = np.load(CLIMATE_LAYERS[layer_name])["data"]
    return _arrays[layer_name]


# look up a raster value at a lon/lat, or none if there's no data there
def sample_layer(layer_name: str, lon: float, lat: float) -> float | None:
    array = _load(layer_name)
    rows, cols = array.shape
    row = min(rows - 1, max(0, int((90 - lat) / 180 * rows)))
    col = min(cols - 1, max(0, int((lon + 180) / 360 * cols)))
    value = float(array[row, col])
    return None if value <= NODATA_THRESHOLD else value


# sample every known climate layer at a coordinate
def sample_climate(lon: float, lat: float) -> dict[str, float | None]:
    return {layer_name: sample_layer(layer_name, lon, lat) for layer_name in CLIMATE_LAYERS}
