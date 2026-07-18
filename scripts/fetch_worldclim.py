# downloads worldclim climate rasters, converts to compressed numpy arrays, writes to data/

import io
import zipfile
from pathlib import Path

import numpy as np
import requests
import tifffile


# url spec, all 10 arc-minute (lowest available) resolution
BASE_URL = "https://geodata.ucdavis.edu/climate/worldclim/2_1/base"
LAYERS = {
    "elevation": f"{BASE_URL}/wc2.1_10m_elev.zip",
    "bioclim": f"{BASE_URL}/wc2.1_10m_bio.zip",
}

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "worldclim"

# keep only the bands we need: bio_1 = annual mean temp, bio_12 = annual precip
KEPT_FILES = {
    "elevation": {"wc2.1_10m_elev.tif": "elevation"},
    "bioclim": {
        "wc2.1_10m_bio_1.tif": "annual_mean_temp",
        "wc2.1_10m_bio_12.tif": "annual_precip",
    },
}

# global equirectangular grid every worldclim 10m raster shares: lon_min, lat_min, lon_max, lat_max
BOUNDS = np.array([-180.0, -90.0, 180.0, 90.0])


def download_zip(url: str) -> zipfile.ZipFile:
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(response.content))


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for layer_name, url in LAYERS.items():
        print(f"Downloading {layer_name} from {url}")
        zf = download_zip(url)

        for member_name, out_name in KEPT_FILES[layer_name].items():
            array = tifffile.imread(io.BytesIO(zf.read(member_name)))

            out_path = DATA_DIR / f"{out_name}.npz"
            np.savez_compressed(out_path, data=array, bounds=BOUNDS)
            size_kb = out_path.stat().st_size / 1024
            print(f"Wrote {out_path} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
