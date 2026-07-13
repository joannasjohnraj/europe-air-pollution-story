"""Investigate apparent 2007-2024 PM2.5 increases on the island of Ireland.

The analysis aligns the 2007 raster to the 2024 reference grid, applies a
documented geographic bounding box, and retains the largest contiguous
valid-data land component to isolate the main island.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch
from rasterio.windows import Window, from_bounds
from rasterio.warp import Resampling, reproject, transform, transform_bounds
from scipy.ndimage import distance_transform_edt, label


ROOT = Path(__file__).resolve().parents[1]
RASTER_2007 = ROOT / "data_raw/EEA_1kmgrid_2007_pm25_avg.tif"
RASTER_2024 = ROOT / "data_raw/pm25_avg24_int.tif"
SUMMARY_CSV = ROOT / "data_processed/ireland_pm25_change_summary.csv"
POSITIVE_CSV = ROOT / "data_processed/ireland_positive_change_cells.csv"
FIGURE_PNG = ROOT / "figures/ireland_pm25_change_detail.png"
METHOD_MD = ROOT / "docs/ireland_change_investigation.md"

# Approximate island-wide search box. Political jurisdictions are not merged:
# both the Republic of Ireland and Northern Ireland are explicitly in scope.
BBOX_WGS84 = (-10.75, 51.30, -5.35, 55.35)
SCOPE_DESCRIPTION = (
    "Main island of Ireland within 10.75°W–5.35°W and 51.30°N–55.35°N; "
    "includes the Republic of Ireland and Northern Ireland, excludes disconnected "
    "offshore valid-data components"
)
VALID_MIN = 0.0
VALID_MAX = 100.0
LITTLE_CHANGE = 0.5
CLUSTER_THRESHOLD = 0.5


def valid_values(data):
    return np.isfinite(data) & (data > VALID_MIN) & (data < VALID_MAX)


def reference_window():
    with rasterio.open(RASTER_2024) as src:
        projected_bounds = transform_bounds(
            "EPSG:4326", src.crs, *BBOX_WGS84, densify_pts=21
        )
        raw_window = from_bounds(*projected_bounds, transform=src.transform)
        raster_window = Window(0, 0, src.width, src.height)
        window = raw_window.round_offsets().round_lengths().intersection(raster_window)
        window = Window(
            int(window.col_off), int(window.row_off), int(window.width), int(window.height)
        )
        destination_transform = src.window_transform(window)
        values_2024 = src.read(1, window=window, masked=True).astype("float32").filled(np.nan)
        reference = {
            "crs": src.crs,
            "transform": destination_transform,
            "shape": values_2024.shape,
            "window": window,
        }
    values_2024[~valid_values(values_2024)] = np.nan
    return reference, values_2024


def align_2007(reference):
    values_2007 = np.full(reference["shape"], np.nan, dtype="float32")
    with rasterio.open(RASTER_2007) as src:
        reproject(
            source=rasterio.band(src, 1),
            destination=values_2007,
            src_transform=src.transform,
            src_crs=src.crs,
            src_nodata=src.nodata,
            dst_transform=reference["transform"],
            dst_crs=reference["crs"],
            dst_nodata=np.nan,
            resampling=Resampling.nearest,
            init_dest_nodata=True,
        )
    values_2007[~valid_values(values_2007)] = np.nan
    return values_2007


def cell_coordinates(reference):
    rows, cols = np.indices(reference["shape"])
    xs, ys = rasterio.transform.xy(
        reference["transform"], rows.ravel(), cols.ravel(), offset="center"
    )
    longitudes, latitudes = transform(
        reference["crs"], "EPSG:4326", list(xs), list(ys)
    )
    return (
        np.asarray(xs).reshape(reference["shape"]),
        np.asarray(ys).reshape(reference["shape"]),
        np.asarray(longitudes).reshape(reference["shape"]),
        np.asarray(latitudes).reshape(reference["shape"]),
    )


def main_island_mask(values_2007, values_2024, longitudes, latitudes):
    west, south, east, north = BBOX_WGS84
    in_bbox = (
        (longitudes >= west)
        & (longitudes <= east)
        & (latitudes >= south)
        & (latitudes <= north)
    )
    any_valid = in_bbox & (valid_values(values_2007) | valid_values(values_2024))
    components, component_count = label(any_valid, structure=np.ones((3, 3), dtype="uint8"))
    if component_count == 0:
        raise RuntimeError("No valid raster component found in the Ireland bounding box.")
    component_sizes = np.bincount(components.ravel())
    component_sizes[0] = 0
    main_component = int(np.argmax(component_sizes))
    return components == main_component


def strongest_cells(change, values_2007, values_2024, mask, latitudes, longitudes):
    positive_rows, positive_cols = np.where(mask & (change > 0))
    if positive_rows.size == 0:
        return pd.DataFrame(
            columns=["latitude", "longitude", "pm25_2007", "pm25_2024", "absolute_change"]
        )
    changes = change[positive_rows, positive_cols]
    order = np.argsort(changes)[::-1][:20]
    rows = positive_rows[order]
    cols = positive_cols[order]
    return pd.DataFrame(
        {
            "latitude": latitudes[rows, cols],
            "longitude": longitudes[rows, cols],
            "pm25_2007": values_2007[rows, cols],
            "pm25_2024": values_2024[rows, cols],
            "absolute_change": change[rows, cols],
        }
    ).round(4)


def cluster_diagnostics(change, comparable_mask):
    meaningful_increase = comparable_mask & (change > CLUSTER_THRESHOLD)
    components, count = label(
        meaningful_increase, structure=np.ones((3, 3), dtype="uint8")
    )
    if count == 0:
        return components, np.array([], dtype="int64"), 0
    sizes = np.bincount(components.ravel())[1:]
    return components, sizes, int(sizes.max())


def classify_pattern(increase_percentage, meaningful_count, largest_cluster, valid_count):
    meaningful_share = 100 * meaningful_count / valid_count if valid_count else 0
    largest_share = 100 * largest_cluster / valid_count if valid_count else 0
    if increase_percentage >= 50 and meaningful_share >= 20:
        return "widespread"
    if meaningful_count >= 25 and (largest_cluster >= 20 or largest_share >= 1):
        return "localised"
    if meaningful_count <= 20 or largest_cluster <= 3:
        return "isolated"
    return "uncertain"


def distinct_peaks(change, mask, count=3, minimum_distance_cells=25):
    rows, cols = np.where(mask & (change > CLUSTER_THRESHOLD))
    if rows.size == 0:
        return []
    order = np.argsort(change[rows, cols])[::-1]
    peaks = []
    for index in order:
        row, col = int(rows[index]), int(cols[index])
        if all((row - old_row) ** 2 + (col - old_col) ** 2 >= minimum_distance_cells**2
               for old_row, old_col in peaks):
            peaks.append((row, col))
        if len(peaks) == count:
            break
    return peaks


def create_figure(change, comparable_mask, reference, peak_cells):
    displayed = np.where(comparable_mask, change, np.nan)
    cmap = ListedColormap(["#2166ac", "#92c5de", "#f2f2f2", "#fdae61", "#b2182b"])
    cmap.set_bad("white", alpha=0)
    boundaries = [-100, -2, -LITTLE_CHANGE, LITTLE_CHANGE, 2, 100]
    norm = BoundaryNorm(boundaries, cmap.N)

    height, width = reference["shape"]
    transform_ref = reference["transform"]
    left, top = transform_ref * (0, 0)
    right, bottom = transform_ref * (width, height)

    fig, ax = plt.subplots(figsize=(9.5, 10), facecolor="white")
    ax.imshow(
        displayed,
        cmap=cmap,
        norm=norm,
        extent=[left, right, bottom, top],
        interpolation="nearest",
    )
    ax.set_title(
        "Where did mapped PM2.5 increase on the island of Ireland?",
        loc="left",
        fontsize=15,
        fontweight="bold",
        pad=16,
    )
    ax.text(
        0,
        1.005,
        "Comparable EEA raster cells, 2024 minus aligned 2007 values",
        transform=ax.transAxes,
        fontsize=10,
        color="#4b5563",
        va="bottom",
    )

    offsets = [(46, 36), (-135, 42), (46, -52)]
    for index, ((row, col), offset) in enumerate(zip(peak_cells, offsets), start=1):
        x, y = rasterio.transform.xy(transform_ref, row, col, offset="center")
        ax.scatter(x, y, s=28, facecolor="white", edgecolor="#7f1d1d", linewidth=1.2, zorder=4)
        ax.annotate(
            f"Local increase {index}\n+{change[row, col]:.1f} µg/m³",
            xy=(x, y),
            xytext=offset,
            textcoords="offset points",
            fontsize=9,
            color="#29384b",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#cbd5e1"),
            arrowprops=dict(arrowstyle="-", color="#687382", linewidth=0.9),
            zorder=5,
        )

    legend_items = [
        Patch(facecolor="#2166ac", label="Decrease greater than 2 µg/m³"),
        Patch(facecolor="#92c5de", label="Decrease of 0.5–2 µg/m³"),
        Patch(facecolor="#f2f2f2", edgecolor="#cbd5e1", label="Little change (±0.5 µg/m³)"),
        Patch(facecolor="#fdae61", label="Increase of 0.5–2 µg/m³"),
        Patch(facecolor="#b2182b", label="Increase greater than 2 µg/m³"),
    ]
    ax.legend(
        handles=legend_items,
        loc="lower left",
        frameon=True,
        framealpha=0.96,
        fontsize=9,
        title="Change in annual PM2.5",
        title_fontsize=9,
    )
    ax.set_aspect("equal")
    ax.axis("off")
    fig.text(
        0.5,
        0.025,
        "Scope: main island raster component; includes the Republic of Ireland and Northern Ireland.",
        ha="center",
        fontsize=9,
        color="#4b5563",
    )
    fig.tight_layout(rect=[0, 0.045, 1, 1])
    FIGURE_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_PNG, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def write_summary(metrics):
    rows = [
        ("valid_comparable_cells", metrics["valid_count"], "cells"),
        ("mean_pm25_2007", metrics["mean_2007"], "µg/m³"),
        ("mean_pm25_2024", metrics["mean_2024"], "µg/m³"),
        ("mean_change_2024_minus_2007", metrics["mean_change"], "µg/m³"),
        ("cells_increased", metrics["increased_count"], "cells"),
        ("cells_increased_percentage", metrics["increased_percentage"], "%"),
        ("cells_decreased", metrics["decreased_count"], "cells"),
        ("cells_decreased_percentage", metrics["decreased_percentage"], "%"),
        ("cells_unchanged", metrics["unchanged_count"], "cells"),
        ("cells_unchanged_percentage", metrics["unchanged_percentage"], "%"),
        ("maximum_positive_change", metrics["maximum_positive_change"], "µg/m³"),
        ("strongest_increase_latitude", metrics["strongest_latitude"], "decimal degrees"),
        ("strongest_increase_longitude", metrics["strongest_longitude"], "decimal degrees"),
        ("cells_with_increase_over_0_5", metrics["meaningful_count"], "cells"),
        ("cells_with_increase_over_0_5_percentage", metrics["meaningful_percentage"], "%"),
        ("contiguous_increase_clusters_over_0_5", metrics["cluster_count"], "clusters"),
        ("largest_contiguous_increase_cluster_over_0_5", metrics["largest_cluster"], "cells"),
        ("increasing_cells_above_10_in_2024", metrics["increasing_hotspot_count"], "cells"),
        ("noncomparable_cells_within_main_island_mask", metrics["noncomparable_count"], "cells"),
        ("strongest_20_cells_within_2km_of_valid_data_edge", metrics["top_near_edge"], "cells"),
        ("pattern_classification", metrics["classification"], "category"),
    ]
    output = pd.DataFrame(rows, columns=["metric", "value", "unit"])
    output["value"] = output["value"].map(
        lambda value: round(float(value), 4)
        if isinstance(value, (float, np.floating))
        else value
    )
    output["geographic_scope"] = SCOPE_DESCRIPTION
    SUMMARY_CSV.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(SUMMARY_CSV, index=False, float_format="%.4f")


def write_method(metrics):
    decision = {
        "widespread": "The increase is widespread enough to merit consideration in the main story.",
        "localised": "The increase is localised rather than island-wide. It is meaningful as a mapped exception, but is better suited to a brief annotation or secondary detail than a main story chapter.",
        "isolated": "The increase is limited to isolated cells and is not strong enough for the main story.",
        "uncertain": "The pattern is mixed or weak enough that its story relevance remains uncertain.",
    }[metrics["classification"]]

    edge_note = (
        "None of the 20 strongest increasing cells lies within approximately 2 km of the "
        "comparable-data edge, so the strongest increases do not show a direct edge signature."
        if metrics["top_near_edge"] == 0
        else f"{metrics['top_near_edge']} of the 20 strongest increasing cells lie within "
        "approximately 2 km of the comparable-data edge, so edge sensitivity remains relevant."
    )
    coverage_note = (
        f"Within the raster-derived main-island mask, {metrics['noncomparable_count']:,} cells had a "
        "valid value in only one of the two years and were excluded."
    )
    text = f"""# Investigation of apparent PM2.5 worsening in Ireland

## Question

Does the small area of apparent worsening visible in Ireland represent a widespread increase, a coherent local pattern, isolated cells, or a possible raster-edge or coverage artefact?

## Geographic scope

No Ireland administrative boundary file is available in this repository. The analysis therefore starts with an approximate WGS84 bounding box from **10.75°W to 5.35°W and 51.30°N to 55.35°N**. Within that box, it retains the largest contiguous component having valid data in either 2007 or 2024. This raster-derived component represents the main island and avoids including nearby disconnected Scottish land.

The scope includes both the **Republic of Ireland and Northern Ireland**. They are not treated as the same political jurisdiction; this is an island-wide spatial investigation. Disconnected offshore islands may be omitted because no official coastline or administrative boundary is used.

## Method

The 2024 EEA raster defines the comparison grid, including its EPSG:3035 coordinate reference system, 1 km cell size, transform and alignment. The 2007 raster is aligned to that grid with nearest-neighbour resampling. Source nodata masks are preserved, and non-finite values, values at or below zero, and values at or above 100 µg/m³ are treated as invalid, consistently with the existing project processing.

Only cells valid in both years and inside the main-island component are compared. Change is calculated as **2024 minus 2007**, so positive values indicate an increase. Counts of increasing and decreasing cells use zero as the dividing point. For mapping and cluster diagnostics, changes within ±0.5 µg/m³ are shown as little change, and contiguous increases greater than 0.5 µg/m³ are assessed with eight-cell neighbourhood connectivity.

## Results

- Valid comparable cells: **{metrics['valid_count']:,}**
- Mean PM2.5 in 2007: **{metrics['mean_2007']:.2f} µg/m³**
- Mean PM2.5 in 2024: **{metrics['mean_2024']:.2f} µg/m³**
- Mean change: **{metrics['mean_change']:+.2f} µg/m³**
- Increasing cells: **{metrics['increased_count']:,} ({metrics['increased_percentage']:.1f}%)**
- Decreasing cells: **{metrics['decreased_count']:,} ({metrics['decreased_percentage']:.1f}%)**
- Maximum positive change: **{metrics['maximum_positive_change']:+.2f} µg/m³** at approximately **{metrics['strongest_latitude']:.4f}°N, {abs(metrics['strongest_longitude']):.4f}°W**
- Cells increasing by more than 0.5 µg/m³: **{metrics['meaningful_count']:,}**
- Share increasing by more than 0.5 µg/m³: **{metrics['meaningful_percentage']:.1f}%**
- Contiguous clusters above that increase threshold: **{metrics['cluster_count']:,}**
- Largest contiguous cluster above that increase threshold: **{metrics['largest_cluster']:,} cells**
- Increasing cells that are above 10 µg/m³ in 2024: **{metrics['increasing_hotspot_count']:,}**

The diagnostic classification is **{metrics['classification']}**. {decision}

## Coverage and interpolation concerns

{coverage_note} {edge_note} This provides no clear evidence that the central increase cluster is caused by changing valid-data coverage. Nearest-neighbour alignment avoids smoothing the source surfaces, but it preserves block-like patterns in the inputs, and the EEA rasters are themselves modelled and interpolated products. Small local differences can reflect changes in input observations or model behaviour as well as changes in mapped concentration.

The bounding box and raster-component mask are approximations rather than an official Ireland boundary. Results should therefore be described as applying to comparable cells on the raster-derived main island, not as official national statistics for either jurisdiction.

## Story recommendation

{decision} It should not be presented as evidence of a cause. If mentioned, the wording should emphasise that this is a mapped local exception within a much larger pattern of decline and that interpolation and year-to-year source-surface differences limit interpretation.

## Reproduction

Run from the repository root:

```bash
python scripts/investigate_ireland_pm25_change.py
```
"""
    METHOD_MD.parent.mkdir(parents=True, exist_ok=True)
    METHOD_MD.write_text(text, encoding="utf-8")


def main():
    for path in (RASTER_2007, RASTER_2024):
        if not path.exists():
            raise FileNotFoundError(path)

    reference, values_2024 = reference_window()
    values_2007 = align_2007(reference)
    xs, ys, longitudes, latitudes = cell_coordinates(reference)
    island_mask = main_island_mask(values_2007, values_2024, longitudes, latitudes)

    valid_2007 = valid_values(values_2007)
    valid_2024 = valid_values(values_2024)
    comparable = island_mask & valid_2007 & valid_2024
    change = np.full(reference["shape"], np.nan, dtype="float32")
    change[comparable] = values_2024[comparable] - values_2007[comparable]

    valid_count = int(comparable.sum())
    if valid_count == 0:
        raise RuntimeError("No comparable Ireland cells were found.")
    increased = comparable & (change > 0)
    decreased = comparable & (change < 0)
    unchanged = comparable & (change == 0)

    positive_cells = strongest_cells(
        change, values_2007, values_2024, comparable, latitudes, longitudes
    )
    positive_cells.to_csv(POSITIVE_CSV, index=False)

    components, cluster_sizes, largest_cluster = cluster_diagnostics(change, comparable)
    meaningful_count = int((comparable & (change > CLUSTER_THRESHOLD)).sum())
    increase_percentage = 100 * int(increased.sum()) / valid_count
    classification = classify_pattern(
        increase_percentage, meaningful_count, largest_cluster, valid_count
    )

    strongest_row, strongest_col = np.unravel_index(np.nanargmax(change), change.shape)
    edge_distance = distance_transform_edt(comparable)
    if positive_cells.empty:
        top_near_edge = 0
    else:
        top_rows = []
        top_cols = []
        for latitude, longitude in positive_cells[["latitude", "longitude"]].itertuples(index=False):
            distance = (latitudes - latitude) ** 2 + (longitudes - longitude) ** 2
            row, col = np.unravel_index(np.argmin(distance), distance.shape)
            top_rows.append(row)
            top_cols.append(col)
        top_near_edge = int(np.sum(edge_distance[top_rows, top_cols] <= 2))

    metrics = {
        "valid_count": valid_count,
        "mean_2007": float(np.mean(values_2007[comparable])),
        "mean_2024": float(np.mean(values_2024[comparable])),
        "mean_change": float(np.mean(change[comparable])),
        "increased_count": int(increased.sum()),
        "increased_percentage": increase_percentage,
        "decreased_count": int(decreased.sum()),
        "decreased_percentage": 100 * int(decreased.sum()) / valid_count,
        "unchanged_count": int(unchanged.sum()),
        "unchanged_percentage": 100 * int(unchanged.sum()) / valid_count,
        "maximum_positive_change": float(change[strongest_row, strongest_col]),
        "strongest_latitude": float(latitudes[strongest_row, strongest_col]),
        "strongest_longitude": float(longitudes[strongest_row, strongest_col]),
        "meaningful_count": meaningful_count,
        "meaningful_percentage": 100 * meaningful_count / valid_count,
        "cluster_count": int(cluster_sizes.size),
        "largest_cluster": largest_cluster,
        "increasing_hotspot_count": int((increased & (values_2024 > 10)).sum()),
        "noncomparable_count": int((island_mask & ~(valid_2007 & valid_2024)).sum()),
        "top_near_edge": top_near_edge,
        "classification": classification,
    }

    peak_cells = distinct_peaks(change, comparable)
    create_figure(change, comparable, reference, peak_cells)
    write_summary(metrics)
    write_method(metrics)

    print("\nIreland PM2.5 change investigation")
    print(f"Mean change (2024 minus 2007): {metrics['mean_change']:+.2f} ug/m3")
    print(f"Share of comparable cells increasing: {metrics['increased_percentage']:.1f}%")
    print(f"Largest increase: {metrics['maximum_positive_change']:+.2f} ug/m3")
    print(f"Conclusion: {metrics['classification']}")
    print(f"Saved: {SUMMARY_CSV.relative_to(ROOT)}")
    print(f"Saved: {POSITIVE_CSV.relative_to(ROOT)}")
    print(f"Saved: {FIGURE_PNG.relative_to(ROOT)}")
    print(f"Saved: {METHOD_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
