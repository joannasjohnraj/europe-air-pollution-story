# Investigation of apparent PM2.5 worsening in Ireland

## Question

Does the small area of apparent worsening visible in Ireland represent a widespread increase, a coherent local pattern, isolated cells, or a possible raster-edge or coverage artefact?

## Geographic scope

No Ireland administrative boundary file is available in this repository. The analysis therefore starts with an approximate WGS84 bounding box from **10.75°W to 5.35°W and 51.30°N to 55.35°N**. Within that box, it retains the largest contiguous component having valid data in either 2007 or 2024. This raster-derived component represents the main island and avoids including nearby disconnected Scottish land.

The scope includes both the **Republic of Ireland and Northern Ireland**. They are not treated as the same political jurisdiction; this is an island-wide spatial investigation. Disconnected offshore islands may be omitted because no official coastline or administrative boundary is used.

## Method

The 2024 EEA raster defines the comparison grid, including its EPSG:3035 coordinate reference system, 1 km cell size, transform and alignment. The 2007 raster is aligned to that grid with nearest-neighbour resampling. Source nodata masks are preserved, and non-finite values, values at or below zero, and values at or above 100 µg/m³ are treated as invalid, consistently with the existing project processing.

Only cells valid in both years and inside the main-island component are compared. Change is calculated as **2024 minus 2007**, so positive values indicate an increase. Counts of increasing and decreasing cells use zero as the dividing point. For mapping and cluster diagnostics, changes within ±0.5 µg/m³ are shown as little change, and contiguous increases greater than 0.5 µg/m³ are assessed with eight-cell neighbourhood connectivity.

## Results

- Valid comparable cells: **86,424**
- Mean PM2.5 in 2007: **6.20 µg/m³**
- Mean PM2.5 in 2024: **5.21 µg/m³**
- Mean change: **-0.99 µg/m³**
- Increasing cells: **4,088 (4.7%)**
- Decreasing cells: **82,336 (95.3%)**
- Maximum positive change: **+3.50 µg/m³** at approximately **53.3438°N, 7.0489°W**
- Cells increasing by more than 0.5 µg/m³: **1,355**
- Share increasing by more than 0.5 µg/m³: **1.6%**
- Contiguous clusters above that increase threshold: **282**
- Largest contiguous cluster above that increase threshold: **158 cells**
- Increasing cells that are above 10 µg/m³ in 2024: **0**

The diagnostic classification is **localised**. The increase is localised rather than island-wide. It is meaningful as a mapped exception, but is better suited to a brief annotation or secondary detail than a main story chapter.

## Coverage and interpolation concerns

Within the raster-derived main-island mask, 0 cells had a valid value in only one of the two years and were excluded. None of the 20 strongest increasing cells lies within approximately 2 km of the comparable-data edge, so the strongest increases do not show a direct edge signature. This provides no clear evidence that the central increase cluster is caused by changing valid-data coverage. Nearest-neighbour alignment avoids smoothing the source surfaces, but it preserves block-like patterns in the inputs, and the EEA rasters are themselves modelled and interpolated products. Small local differences can reflect changes in input observations or model behaviour as well as changes in mapped concentration.

The bounding box and raster-component mask are approximations rather than an official Ireland boundary. Results should therefore be described as applying to comparable cells on the raster-derived main island, not as official national statistics for either jurisdiction.

## Story recommendation

The increase is localised rather than island-wide. It is meaningful as a mapped exception, but is better suited to a brief annotation or secondary detail than a main story chapter. It should not be presented as evidence of a cause. If mentioned, the wording should emphasise that this is a mapped local exception within a much larger pattern of decline and that interpolation and year-to-year source-surface differences limit interpretation.

## Reproduction

Run from the repository root:

```bash
python scripts/investigate_ireland_pm25_change.py
```
