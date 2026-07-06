import json
import os

import numpy as np
import rasterio
from rasterio.transform import xy
from rasterio.warp import Resampling, calculate_default_transform, reproject


OUTPUT_JSON = "prototype/pm25_interactive_samples.json"
OUTPUT_JS = "prototype/pm25_interactive_samples.js"
DST_CRS = "EPSG:4326"
SAMPLE_STEP = 55

RASTERS = {
    "2007": "data_raw/EEA_1kmgrid_2007_pm25_avg.tif",
    "2024": "data_raw/pm25_avg24_int.tif",
}


def reproject_to_wgs84(path):
    with rasterio.open(path) as src:
        transform, width, height = calculate_default_transform(
            src.crs,
            DST_CRS,
            src.width,
            src.height,
            *src.bounds,
        )

        data = np.empty((height, width), dtype="float32")
        data[:] = np.nan

        reproject(
            source=rasterio.band(src, 1),
            destination=data,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs=DST_CRS,
            resampling=Resampling.nearest,
            src_nodata=src.nodata,
            dst_nodata=np.nan,
        )

    data[(data <= 0) | (data >= 100)] = np.nan
    return data, transform


def value_at(data, transform, lat, lng):
    col, row = ~transform * (lng, lat)
    row = int(round(row))
    col = int(round(col))
    if row < 0 or col < 0 or row >= data.shape[0] or col >= data.shape[1]:
        return None

    value = data[row, col]
    if np.isnan(value):
        return None
    return round(float(value), 2)


def color_for(value):
    if value is None:
        return "#9aa6b2"
    if value < 5:
        return "#2c7bb6"
    if value < 8:
        return "#00a6a6"
    if value < 10:
        return "#8bc34a"
    if value < 15:
        return "#fdae61"
    if value < 20:
        return "#f46d43"
    return "#a50026"


def main():
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)

    data_2007, transform_2007 = reproject_to_wgs84(RASTERS["2007"])
    data_2024, transform_2024 = reproject_to_wgs84(RASTERS["2024"])

    points = []
    for row in range(SAMPLE_STEP // 2, data_2024.shape[0], SAMPLE_STEP):
        for col in range(SAMPLE_STEP // 2, data_2024.shape[1], SAMPLE_STEP):
            lng, lat = xy(transform_2024, row, col, offset="center")
            value_2024 = value_at(data_2024, transform_2024, lat, lng)
            value_2007 = value_at(data_2007, transform_2007, lat, lng)

            if value_2007 is None and value_2024 is None:
                continue

            if value_2007 is not None and value_2024 is not None:
                change = round(value_2024 - value_2007, 2)
            else:
                change = None

            points.append(
                {
                    "lat": round(float(lat), 4),
                    "lng": round(float(lng), 4),
                    "pm25_2007": value_2007,
                    "pm25_2024": value_2024,
                    "change": change,
                    "hotspot_2024": bool(value_2024 is not None and value_2024 >= 10),
                    "color_2007": color_for(value_2007),
                    "color_2024": color_for(value_2024),
                }
            )

    comparable = [p for p in points if p["pm25_2007"] is not None and p["pm25_2024"] is not None]
    hotspots = [p for p in points if p["hotspot_2024"]]

    payload = {
        "metadata": {
            "source": "Sampled from EEA PM2.5 GeoTIFF rasters in this repository",
            "years": [2007, 2024],
            "sample_step_pixels": SAMPLE_STEP,
            "point_count": len(points),
            "comparable_point_count": len(comparable),
            "hotspot_2024_point_count": len(hotspots),
            "note": "Sampled points are for interactive browser display. Full-resolution analysis remains in the Python raster outputs.",
        },
        "points": points,
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, separators=(",", ":"))

    with open(OUTPUT_JS, "w", encoding="utf-8") as f:
        f.write("window.PM25_INTERACTIVE_SAMPLES = ")
        json.dump(payload, f, separators=(",", ":"))
        f.write(";\n")

    print("Saved:", OUTPUT_JSON)
    print("Saved:", OUTPUT_JS)
    print("Points:", len(points))
    print("Comparable points:", len(comparable))
    print("2024 hotspots:", len(hotspots))


if __name__ == "__main__":
    main()
