import os

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.warp import Resampling, calculate_default_transform, reproject


OUTPUT_DIR = "prototype"
DST_CRS = "EPSG:4326"
VMIN = 0
VMAX = 25

OVERLAYS = {
    2007: "data_raw/EEA_1kmgrid_2007_pm25_avg.tif",
    2024: "data_raw/pm25_avg24_int.tif",
}


def reproject_to_leaflet(input_file):
    with rasterio.open(input_file) as src:
        transform, width, height = calculate_default_transform(
            src.crs,
            DST_CRS,
            src.width,
            src.height,
            *src.bounds,
        )

        destination = np.empty((height, width), dtype="float32")
        destination[:] = np.nan

        reproject(
            source=rasterio.band(src, 1),
            destination=destination,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs=DST_CRS,
            resampling=Resampling.nearest,
            src_nodata=src.nodata,
            dst_nodata=np.nan,
        )

    destination[(destination <= 0) | (destination >= 100)] = np.nan
    return destination, transform, width, height


def save_overlay(year, input_file):
    output_png = os.path.join(OUTPUT_DIR, f"pm25_{year}_overlay.png")
    output_bounds = os.path.join(OUTPUT_DIR, f"pm25_{year}_overlay_bounds.txt")

    data, transform, width, height = reproject_to_leaflet(input_file)

    cmap = plt.get_cmap("inferno").copy()
    cmap.set_bad(alpha=0)

    fig = plt.figure(figsize=(width / 200, height / 200), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(data, cmap=cmap, vmin=VMIN, vmax=VMAX, interpolation="nearest")
    ax.axis("off")

    fig.savefig(output_png, transparent=True, pad_inches=0)
    plt.close(fig)

    left = transform.c
    top = transform.f
    right = left + transform.a * width
    bottom = top + transform.e * height

    with open(output_bounds, "w", encoding="utf-8") as f:
        f.write(f"south={bottom}\n")
        f.write(f"west={left}\n")
        f.write(f"north={top}\n")
        f.write(f"east={right}\n")

    print("Saved:", output_png)
    print("Saved:", output_bounds)
    print("Leaflet bounds:", [[bottom, left], [top, right]])


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for year, input_file in OVERLAYS.items():
        save_overlay(year, input_file)


if __name__ == "__main__":
    main()
