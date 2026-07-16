# downloads natural earth boundary data, strips it down, writes to data/

import io
import json
import zipfile
from pathlib import Path

import requests
import shapefile


# url spec
BASE_URL = "https://naciscdn.org/naturalearth/110m"
LAYERS = {
    "countries": f"{BASE_URL}/cultural/ne_110m_admin_0_countries.zip",
    "coastline": f"{BASE_URL}/physical/ne_110m_coastline.zip",
    "ocean": f"{BASE_URL}/physical/ne_110m_ocean.zip",
}

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "natural-earth"

# keep a tiny subset of columns
KEPT_PROPERTIES = {
    "countries": ["NAME", "ISO_A2", "ISO_A3", "CONTINENT"],
    "coastline": [],
    "ocean": [],
}


def download_zip(url: str) -> zipfile.ZipFile:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(response.content))


def shapefile_to_geojson(zf: zipfile.ZipFile, keep: list[str]) -> dict:
    shp_name = next(n for n in zf.namelist() if n.endswith(".shp"))
    stem = shp_name[: -len(".shp")]

    shp = io.BytesIO(zf.read(f"{stem}.shp"))
    dbf = io.BytesIO(zf.read(f"{stem}.dbf"))
    shx_name = f"{stem}.shx"
    shx = io.BytesIO(zf.read(shx_name)) if shx_name in zf.namelist() else None

    reader = shapefile.Reader(shp=shp, dbf=dbf, shx=shx)
    geojson = reader.__geo_interface__

    if keep:
        for feature in geojson["features"]:
            feature["properties"] = {
                k: feature["properties"][k] for k in keep
            }

    return geojson


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for layer_name, url in LAYERS.items():
        print(f"Downloading {layer_name} from {url}")
        zf = download_zip(url)

        print(f"Converting {layer_name} to GeoJSON")
        geojson = shapefile_to_geojson(zf, KEPT_PROPERTIES[layer_name])

        out_path = DATA_DIR / f"{layer_name}.geojson"
        out_path.write_text(json.dumps(geojson))
        size_kb = out_path.stat().st_size / 1024
        print(f"Wrote {out_path} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
