"""Create a trend-continuation scenario for PM2.5 hotspot cells in 2024.

This is a descriptive scenario, not an official forecast. All annual rasters are
aligned to the 2024 EEA raster grid before cell-level comparisons are made.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from rasterio.warp import Resampling, reproject


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data_raw"
SUMMARY_CSV = ROOT / "data_processed/current_hotspot_projection_summary.csv"
MAP_PNG = ROOT / "figures/current_hotspot_projection_categories.png"
BAR_PNG = ROOT / "figures/current_hotspot_projection_summary.png"

THRESHOLD = 10.0
MIN_ALL_YEARS = 10
RECENT_START = 2015
MIN_RECENT_YEARS = 5
VALID_MIN = 0.0
VALID_MAX = 100.0

RASTERS = {
    2007: "EEA_1kmgrid_2007_pm25_avg.tif",
    2008: "EEA_1kmgrid_2008_pm25_avg.tif",
    2010: "EEA_1kmgrid_2010_pm25_avg.tif",
    2011: "EEA_1kmgrid_2011_pm25_avg.tif",
    2012: "EEA_1kmgrid_2012_pm25_avg.tif",
    2013: "EEA_1kmgrid_2013_pm25_avg.tif",
    2014: "EEA_1kmgrid_2014_pm25_avg.tif",
    2015: "EEA_1kmgrid_2015_pm25_avg.tif",
    2016: "EEA_1kmgrid_2016_pm25_avg.tif",
    2017: "EEA_1kmgrid_2017_pm25_avg.tif",
    2018: "pm25_avg_18.tif",
    2019: "pm25_avg19.tif",
    2020: "EEA_1kmgrid_2020_pm25_avg.tif",
    2021: "EEA_1kmgrid_2021_pm25_avg.tif",
    2022: "pm25_avg_22.tif",
    2023: "pm25_avg_23.tif",
    2024: "pm25_avg24_int.tif",
}

CATEGORY_ORDER = [
    "Projected below 10 by 2030",
    "Projected below 10 by 2035",
    "Improving, but not below 10 by 2035",
    "Stable or worsening",
    "Insufficient data",
]

CATEGORY_COLORS = {
    "Projected below 10 by 2030": "#238b45",
    "Projected below 10 by 2035": "#2b8cbe",
    "Improving, but not below 10 by 2035": "#f28e2b",
    "Stable or worsening": "#c43c39",
    "Insufficient data": "#6b7280",
}


def valid_values(data):
    """Return the project-wide validity mask used for every aligned raster."""
    return np.isfinite(data) & (data > VALID_MIN) & (data < VALID_MAX)


def aligned_array(path, reference):
    """Read one raster on the exact 2024 grid while preserving its valid mask."""
    destination = np.full(reference["shape"], np.nan, dtype="float32")
    with rasterio.open(path) as src:
        source = src.read(1, masked=True).astype("float32").filled(np.nan)
        source[~valid_values(source)] = np.nan
        reproject(
            source=source,
            destination=destination,
            src_transform=src.transform,
            src_crs=src.crs,
            src_nodata=np.nan,
            dst_transform=reference["transform"],
            dst_crs=reference["crs"],
            dst_nodata=np.nan,
            resampling=Resampling.nearest,
            init_dest_nodata=True,
        )
    destination[~valid_values(destination)] = np.nan
    return destination


def calculate_scenario():
    reference_path = DATA_DIR / RASTERS[2024]
    with rasterio.open(reference_path) as src:
        reference = {
            "shape": (src.height, src.width),
            "transform": src.transform,
            "crs": src.crs,
            "bounds": src.bounds,
        }
        values_2024 = src.read(1, masked=True).astype("float32").filled(np.nan)

    values_2024[~valid_values(values_2024)] = np.nan
    comparable_2024 = np.isfinite(values_2024)
    hotspot_mask = comparable_2024 & (values_2024 > THRESHOLD)
    hotspot_flat = np.flatnonzero(hotspot_mask.ravel())
    hotspot_2024 = values_2024.ravel()[hotspot_flat].astype("float64")
    n_hotspots = hotspot_flat.size

    valid_count = np.zeros(n_hotspots, dtype="uint8")
    recent_count = np.zeros(n_hotspots, dtype="uint8")
    sum_x = np.zeros(n_hotspots, dtype="float64")
    sum_y = np.zeros(n_hotspots, dtype="float64")
    sum_xx = np.zeros(n_hotspots, dtype="float64")
    sum_xy = np.zeros(n_hotspots, dtype="float64")

    for year, filename in RASTERS.items():
        print(f"Aligning and processing {year}: {filename}")
        if year == 2024:
            aligned = values_2024
        else:
            aligned = aligned_array(DATA_DIR / filename, reference)

        hotspot_values = aligned.ravel()[hotspot_flat].astype("float64")
        valid = np.isfinite(hotspot_values)
        valid_count += valid

        if year >= RECENT_START:
            x = float(year - RECENT_START)
            recent_count += valid
            sum_x[valid] += x
            sum_y[valid] += hotspot_values[valid]
            sum_xx[valid] += x * x
            sum_xy[valid] += x * hotspot_values[valid]

    sufficient = (valid_count >= MIN_ALL_YEARS) & (recent_count >= MIN_RECENT_YEARS)
    denominator = recent_count.astype("float64") * sum_xx - sum_x * sum_x
    sufficient &= denominator > 0

    slope = np.full(n_hotspots, np.nan, dtype="float64")
    slope[sufficient] = (
        recent_count[sufficient] * sum_xy[sufficient]
        - sum_x[sufficient] * sum_y[sufficient]
    ) / denominator[sufficient]

    crossing_year = np.full(n_hotspots, np.nan, dtype="float64")
    improving = sufficient & (slope < 0)
    crossing_year[improving] = 2024 + (THRESHOLD - hotspot_2024[improving]) / slope[improving]

    category_code = np.full(n_hotspots, 5, dtype="uint8")
    category_code[sufficient & (slope >= 0)] = 4
    category_code[improving & (crossing_year > 2035)] = 3
    category_code[improving & (crossing_year > 2030) & (crossing_year <= 2035)] = 2
    category_code[improving & (crossing_year <= 2030)] = 1

    # 0 is comparable non-hotspot; 1-5 follow CATEGORY_ORDER.
    map_codes = np.full(reference["shape"], np.nan, dtype="float32")
    map_codes[comparable_2024] = 0
    map_codes.ravel()[hotspot_flat] = category_code

    return reference, map_codes, category_code, slope, crossing_year


def create_summary(category_code, slope, crossing_year):
    total = category_code.size
    records = []
    for code, label in enumerate(CATEGORY_ORDER, start=1):
        selected = category_code == code
        count = int(selected.sum())
        slopes = slope[selected & np.isfinite(slope)]
        crossings = crossing_year[selected & np.isfinite(crossing_year)]
        records.append(
            {
                "classification": label,
                "cell_count": count,
                "percentage_of_current_hotspot_cells": 100 * count / total if total else 0,
                "median_recent_slope": float(np.median(slopes)) if slopes.size else np.nan,
                "median_projected_crossing_year": (
                    float(np.median(crossings)) if crossings.size else np.nan
                ),
            }
        )
    return pd.DataFrame(records)


def plot_map(map_codes):
    colors = ["#dedede"] + [CATEGORY_COLORS[label] for label in CATEGORY_ORDER]
    cmap = ListedColormap(colors)
    masked = np.ma.masked_invalid(map_codes)

    fig, ax = plt.subplots(figsize=(11, 9), facecolor="white")
    ax.imshow(masked, cmap=cmap, vmin=-0.5, vmax=5.5, interpolation="nearest")
    ax.set_title(
        "If recent trends continue, when could 2024 hotspots fall below 10 µg/m³?",
        loc="left",
        fontsize=15,
        fontweight="bold",
        pad=14,
    )
    ax.text(
        0,
        1.005,
        "Cell-level scenario based on annual EEA rasters; this is not an official forecast",
        transform=ax.transAxes,
        fontsize=10,
        color="#4b5563",
        va="bottom",
    )
    legend = [Patch(facecolor="#dedede", label="Comparable 2024 non-hotspot cell")]
    legend.extend(
        Patch(facecolor=CATEGORY_COLORS[label], label=label) for label in CATEGORY_ORDER
    )
    ax.legend(
        handles=legend,
        loc="lower left",
        frameon=True,
        framealpha=0.96,
        fontsize=9,
        title="2024 hotspot scenario",
        title_fontsize=9,
    )
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(MAP_PNG, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_summary(summary):
    labels = summary["classification"].tolist()
    shares = summary["percentage_of_current_hotspot_cells"].to_numpy()
    colors = [CATEGORY_COLORS[label] for label in labels]

    fig, ax = plt.subplots(figsize=(11, 6.5), facecolor="white")
    bars = ax.barh(labels[::-1], shares[::-1], color=colors[::-1], height=0.66)
    ax.bar_label(bars, labels=[f"{value:.1f}%" for value in shares[::-1]], padding=5, fontsize=10)
    ax.set_xlim(0, max(100, float(shares.max()) * 1.12))
    ax.set_xlabel("Share of cells above 10 µg/m³ in 2024")
    ax.set_title(
        "How quickly could current PM2.5 hotspots improve?",
        loc="left",
        fontsize=15,
        fontweight="bold",
        pad=14,
    )
    ax.text(
        0,
        1.01,
        "Trend-continuation scenario using recent annual observations, 2015–2024",
        transform=ax.transAxes,
        fontsize=10,
        color="#4b5563",
        va="bottom",
    )
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", color="#e5e7eb", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    fig.tight_layout()
    fig.savefig(BAR_PNG, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    missing = [str(DATA_DIR / name) for name in RASTERS.values() if not (DATA_DIR / name).exists()]
    if missing:
        raise FileNotFoundError("Missing input raster(s): " + ", ".join(missing))

    SUMMARY_CSV.parent.mkdir(parents=True, exist_ok=True)
    MAP_PNG.parent.mkdir(parents=True, exist_ok=True)

    _, map_codes, category_code, slope, crossing_year = calculate_scenario()
    summary = create_summary(category_code, slope, crossing_year)
    summary.to_csv(SUMMARY_CSV, index=False, float_format="%.3f")
    plot_map(map_codes)
    plot_summary(summary)

    total = len(category_code)
    by_2030 = int((category_code == 1).sum())
    by_2035 = int(np.isin(category_code, [1, 2]).sum())
    stable = int((category_code == 4).sum())
    print("\nScenario summary")
    print(f"Total current hotspot cells: {total:,}")
    print(f"Share projected below 10 by 2030: {100 * by_2030 / total:.1f}%")
    print(f"Share projected below 10 by 2035 (cumulative): {100 * by_2035 / total:.1f}%")
    print(f"Share stable or worsening: {100 * stable / total:.1f}%")
    print(f"Saved: {SUMMARY_CSV.relative_to(ROOT)}")
    print(f"Saved: {MAP_PNG.relative_to(ROOT)}")
    print(f"Saved: {BAR_PNG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
