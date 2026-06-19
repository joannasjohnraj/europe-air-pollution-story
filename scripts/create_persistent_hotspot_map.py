import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.windows import Window
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

files = [
    ("data_raw/EEA_1kmgrid_2007_pm25_avg.tif", 2007),
    ("data_raw/EEA_1kmgrid_2008_pm25_avg.tif", 2008),
    ("data_raw/EEA_1kmgrid_2010_pm25_avg.tif", 2010),
    ("data_raw/EEA_1kmgrid_2011_pm25_avg.tif", 2011),
    ("data_raw/EEA_1kmgrid_2012_pm25_avg.tif", 2012),
    ("data_raw/EEA_1kmgrid_2013_pm25_avg.tif", 2013),
    ("data_raw/EEA_1kmgrid_2014_pm25_avg.tif", 2014),
    ("data_raw/EEA_1kmgrid_2015_pm25_avg.tif", 2015),
    ("data_raw/EEA_1kmgrid_2016_pm25_avg.tif", 2016),
    ("data_raw/EEA_1kmgrid_2017_pm25_avg.tif", 2017),
    ("data_raw/pm25_avg_18.tif", 2018),
    ("data_raw/pm25_avg19.tif", 2019),
    ("data_raw/EEA_1kmgrid_2020_pm25_avg.tif", 2020),
    ("data_raw/EEA_1kmgrid_2021_pm25_avg.tif", 2021),
    ("data_raw/pm25_avg_22.tif", 2022),
    ("data_raw/pm25_avg_23.tif", 2023),
    ("data_raw/pm25_avg24_int.tif", 2024),
]

# Shared comparison grid based on the older common extent
h = 4037
w = 3890

hotspot_count = np.zeros((h, w), dtype="float32")
valid_count = np.zeros((h, w), dtype="float32")

for fp, year in files:
    print(f"Processing {year}...")

    src = rasterio.open(fp)
    hh = min(h, src.height)
    ww = min(w, src.width)

    arr = src.read(1, window=Window(0, 0, ww, hh)).astype("float32")

    if src.nodata is not None:
        arr[arr == src.nodata] = np.nan

    # Remove invalid / unrealistic values
    arr[(arr <= 0) | (arr >= 100)] = np.nan

    data = np.full((h, w), np.nan, dtype="float32")
    data[:hh, :ww] = arr

    valid = np.isfinite(data)
    valid_count[valid] += 1
    hotspot_count[(data > 10) & valid] += 1

persistent = np.full((h, w), np.nan, dtype="float32")
mask = valid_count >= 10
persistent[mask] = hotspot_count[mask] / valid_count[mask]

print("Years used:", len(files))
print("Cells with >=10 valid years:", np.isfinite(persistent).sum())
print("Mean persistence:", np.nanmean(persistent))

# Build categorical persistence classes
# 0 = comparable area but not persistent
# 1 = 40–60%
# 2 = 60–80%
# 3 = 80–100%
classes = np.full((h, w), np.nan, dtype="float32")
classes[np.isfinite(persistent)] = 0
classes[(persistent >= 0.4) & (persistent < 0.6)] = 1
classes[(persistent >= 0.6) & (persistent < 0.8)] = 2
classes[persistent >= 0.8] = 3

print("Cells 40–60%:", np.sum(classes == 1))
print("Cells 60–80%:", np.sum(classes == 2))
print("Cells 80–100%:", np.sum(classes == 3))

# Colors: light gray background + purple categories
cmap = ListedColormap([
    "#E6E6E6",  # comparable area
    "#C7B9E8",  # 40–60
    "#8C6BB1",  # 60–80
    "#4B0082",  # 80–100
])

plt.figure(figsize=(9, 7))
plt.imshow(classes, cmap=cmap, vmin=0, vmax=3)

plt.title(
    "Persistent PM2.5 Hotspots Across Available Years",
    fontsize=12,
    pad=10
)

legend_items = [
    Patch(facecolor="#E6E6E6", label="Comparable area"),
    Patch(facecolor="#C7B9E8", label="Above 10 µg/m³ in 40–60% of valid years"),
    Patch(facecolor="#8C6BB1", label="Above 10 µg/m³ in 60–80% of valid years"),
    Patch(facecolor="#4B0082", label="Above 10 µg/m³ in 80–100% of valid years"),
]

plt.legend(
    handles=legend_items,
    loc="upper left",
    bbox_to_anchor=(1.02, 1.0),
    frameon=True,
    fontsize=8
)

plt.axis("off")
plt.tight_layout()
plt.savefig(
    "figures/persistent_hotspots_threshold10_categorical.png",
    dpi=150,
    bbox_inches="tight"
)

print("Saved: figures/persistent_hotspots_threshold10_categorical.png")