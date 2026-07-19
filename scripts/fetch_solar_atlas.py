# downloads global solar atlas annual GHI raster, downsamples to a small grid, writes to data/
#
# the source geotiff decodes to ~29GB (50000x144000px, 9 arc-sec resolution) so this reads and
# downsamples it tile by tile instead of ever materializing the full array in memory

import tempfile
import zipfile
from pathlib import Path

import numpy as np
import requests
import tifffile


URL = "https://api.globalsolaratlas.info/download/World/World_GHI_GISdata_LTAy_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF.zip"

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "solar-atlas"

# matches worldclim's 10 arc-minute grid so every climate layer samples the same way
GLOBAL_SHAPE = (1080, 2160)
GLOBAL_BOUNDS = np.array([-180.0, -90.0, 180.0, 90.0])

# shared with climate.py's nodata convention (anything <= -30000 is treated as missing)
NODATA_SENTINEL = -99999.0


def download_zip(url: str, out_path: Path) -> None:
    response = requests.get(url, timeout=300, stream=True)
    response.raise_for_status()
    total_bytes = int(response.headers.get("content-length", 0))

    downloaded_bytes = 0
    next_report_pct = 10
    with open(out_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            f.write(chunk)
            downloaded_bytes += len(chunk)
            if total_bytes and downloaded_bytes / total_bytes * 100 >= next_report_pct:
                print(f"  {downloaded_bytes / 1024 / 1024:.0f} / {total_bytes / 1024 / 1024:.0f} MB")
                next_report_pct += 10


# streams just the geotiff entry out of the zip to disk (it's ~2.8GB, too big to hold in memory)
def extract_tif(zip_path: Path, extract_dir: Path) -> Path:
    with zipfile.ZipFile(zip_path) as zf:
        tif_name = next(n for n in zf.namelist() if n.endswith(".tif"))
        zf.extract(tif_name, extract_dir)
    return extract_dir / tif_name


# true geographic extent of the raster, read from its geotiff tags (this dataset excludes the poles)
def read_bounds(page: tifffile.TiffPage) -> np.ndarray:
    scale = page.tags["ModelPixelScaleTag"].value
    tiepoint = page.tags["ModelTiepointTag"].value
    lon_origin, lat_origin = tiepoint[3], tiepoint[4]
    dx, dy = scale[0], scale[1]
    rows, cols = page.shape[:2]
    return np.array([lon_origin, lat_origin - dy * rows, lon_origin + dx * cols, lat_origin])


# scatter-adds one decoded tile into the (small) sum/count accumulators covering its output region
def accumulate_tile(
    sums: np.ndarray,
    counts: np.ndarray,
    tile: np.ndarray,
    row_off: int,
    col_off: int,
    row_scale: float,
    col_scale: float,
) -> None:
    tile = tile.reshape(tile.shape[-3], tile.shape[-2])
    valid = ~np.isnan(tile)
    if not valid.any():
        return

    out_rows = np.clip(((row_off + np.arange(tile.shape[0])) * row_scale).astype(np.int64), 0, sums.shape[0] - 1)
    out_cols = np.clip(((col_off + np.arange(tile.shape[1])) * col_scale).astype(np.int64), 0, sums.shape[1] - 1)

    r0, r1 = int(out_rows.min()), int(out_rows.max()) + 1
    c0, c1 = int(out_cols.min()), int(out_cols.max()) + 1
    local_h, local_w = r1 - r0, c1 - c0

    rr, cc = np.meshgrid(out_rows - r0, out_cols - c0, indexing="ij")
    linear = (rr[valid] * local_w + cc[valid]).astype(np.int64)
    values = tile[valid]

    sums[r0:r1, c0:c1] += np.bincount(linear, weights=values, minlength=local_h * local_w).reshape(local_h, local_w)
    counts[r0:r1, c0:c1] += np.bincount(linear, minlength=local_h * local_w).reshape(local_h, local_w)


# reads bounds + shape from tags (cheap), then walks tiles one at a time, downsampling as it goes
def downsample_geotiff(tif_path: Path) -> tuple[np.ndarray, tuple[int, int, int, int]]:
    with tifffile.TiffFile(tif_path) as tif:
        page = tif.pages[0]
        bounds = read_bounds(page)
        full_rows, full_cols = page.shape[:2]

        deg_per_row = 180 / GLOBAL_SHAPE[0]
        deg_per_col = 360 / GLOBAL_SHAPE[1]
        row_start = int((90 - bounds[3]) / deg_per_row)
        row_end = int((90 - bounds[1]) / deg_per_row)
        col_start = int((bounds[0] + 180) / deg_per_col)
        col_end = int((bounds[2] + 180) / deg_per_col)
        sub_shape = (row_end - row_start, col_end - col_start)

        row_scale = sub_shape[0] / full_rows
        col_scale = sub_shape[1] / full_cols

        sums = np.zeros(sub_shape, dtype=np.float64)
        counts = np.zeros(sub_shape, dtype=np.int64)

        total_tiles = page.chunked[0] * page.chunked[1]
        print(f"Processing {total_tiles} tiles")
        for i, (segment, position, _shape) in enumerate(page.segments()):
            if segment is not None:
                accumulate_tile(sums, counts, segment, position[2], position[3], row_scale, col_scale)
            if (i + 1) % 5000 == 0:
                print(f"  {i + 1} / {total_tiles} tiles")

    with np.errstate(invalid="ignore"):
        downsampled = sums / counts

    return downsampled, (row_start, row_end, col_start, col_end)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # scratch dir lives next to data/ (real disk) rather than the default /tmp (tmpfs, i.e. ram)
    with tempfile.TemporaryDirectory(dir=DATA_DIR.parent) as tmp:
        tmp_path = Path(tmp)
        zip_path = tmp_path / "ghi_world.zip"

        print(f"Downloading GHI from {URL}")
        download_zip(URL, zip_path)

        print("Extracting geotiff")
        tif_path = extract_tif(zip_path, tmp_path)

        print("Downsampling (tile by tile, to keep memory low)")
        downsampled, (row_start, row_end, col_start, col_end) = downsample_geotiff(tif_path)

    canvas = np.full(GLOBAL_SHAPE, NODATA_SENTINEL, dtype=np.float32)
    canvas[row_start:row_end, col_start:col_end] = np.nan_to_num(downsampled, nan=NODATA_SENTINEL)

    out_path = DATA_DIR / "ghi_annual.npz"
    np.savez_compressed(out_path, data=canvas, bounds=GLOBAL_BOUNDS)
    size_kb = out_path.stat().st_size / 1024
    print(f"Wrote {out_path} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
