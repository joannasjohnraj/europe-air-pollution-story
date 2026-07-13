# Current PM2.5 hotspot trend-continuation scenario

## Research question

For raster cells where annual mean PM2.5 exceeded 10 µg/m³ in 2024, would a continuation of the recent cell-level trend bring concentrations below 10 µg/m³ by 2030 or 2035?

## Interpretation

This analysis is a simple trend-continuation scenario, not an official forecast. It describes what would happen if each current hotspot cell continued changing at its estimated recent linear rate. The results should not be read as predictions or policy commitments.

## Input data

The script uses all 17 annual EEA PM2.5 GeoTIFF rasters available in this repository: 2007, 2008, and 2010–2024. No 2009 raster is present in `data_raw`.

Current hotspots are cells with a valid 2024 annual mean greater than 10 µg/m³. The threshold is a scenario benchmark used by this project; the analysis does not imply that concentrations below it are risk-free.

## Raster alignment and masks

The 2024 GeoTIFF defines the comparison grid: its coordinate reference system, affine transform, 1 km cell size, width, and height. Every earlier raster is reprojected to this exact grid with nearest-neighbour resampling, which is appropriate here because the source and target grids represent the same type of cell-level annual concentration surface and should not be smoothed again during alignment.

Source nodata masks are converted to missing values before reprojection. Values that are non-finite, less than or equal to zero, or at least 100 µg/m³ are also treated as invalid, consistently with the existing project scripts. A cell-year is used only when its aligned value is valid.

## Coverage requirements

A 2024 hotspot cell must have:

- at least 10 valid observations across all available annual rasters; and
- at least five valid observations in the recent 2015–2024 period.

Cells failing either test are classified as `Insufficient data`. This prevents trends from being estimated from sparse or spatially inconsistent coverage.

## Recent trend and crossing year

For every sufficiently observed current hotspot cell, ordinary least squares estimates a linear slope from its valid annual values in 2015–2024. Recent years are used because they better represent the direction and pace immediately preceding 2024 than the full 2007–2024 history. The period contains nine available rasters.

For negative slopes, the scenario crossing year is calculated from the observed 2024 value and the fitted annual slope:

`crossing year = 2024 + (10 - PM2.5 in 2024) / recent slope`

Anchoring the extrapolation to the observed 2024 concentration ensures that the scenario starts from each cell's current hotspot level. Slopes are reported in µg/m³ per year.

## Categories

- **Projected below 10 by 2030:** negative recent slope and scenario crossing year no later than 2030.
- **Projected below 10 by 2035:** negative recent slope and scenario crossing year after 2030 but no later than 2035.
- **Improving, but not below 10 by 2035:** negative recent slope and scenario crossing year after 2035.
- **Stable or worsening:** recent slope is zero or positive.
- **Insufficient data:** fewer than 10 valid years overall, fewer than five valid recent years, or an unestimable trend.

The summary CSV reports each category's cell count, share of all 2024 hotspot cells, median recent slope, and median crossing year where a crossing year applies.

## Limitations

Linear extrapolation assumes a constant rate of change and cannot represent nonlinear responses, plateaus, abrupt reversals, or uncertainty around the fitted slope. Results are sensitive to annual variability and to the selected recent period. Adjacent raster cells are spatially related, so cell counts are not independent observations.

Future air quality may differ because policy, emissions, technology, weather, long-range transport, wildfire smoke, economic activity, and the EEA mapping methodology can change. The scenario therefore shows the implications of continuing recent mapped trends; it does not say what will happen or explain why individual areas change.

## Reproduction

From the repository root, run:

```bash
python scripts/create_current_hotspot_projection.py
```

The script writes the requested CSV and two PNG figures and prints the headline shares to the console.
