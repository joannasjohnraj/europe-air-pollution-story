# Europe's Uneven Progress on PM2.5 (2007–2024)

Final interactive data story submitted for the **Data Journalism & Storytelling** course, SoSe 2026, at the University of Konstanz.

## Project Overview

This project examines annual PM2.5 air pollution across Europe from 2007 to 2024 using European Environment Agency (EEA) raster datasets. It combines reproducible geospatial analysis with a browser-based scrollytelling story to show both the continent's broad improvement and the important regional hotspots that remain.

The project describes mapped annual concentrations and spatial patterns. Its raster-cell summaries give each valid grid cell equal weight and should not be interpreted as population-weighted exposure.

## Story Focus

Europe's PM2.5 pollution has improved considerably since 2007, but the improvement is uneven and important regional hotspots remain.

The story moves from an explanation of how PM2.5 is measured and mapped to the 2007 baseline, the 2007–2024 comparison, long-term change, current and persistent hotspots, and a trend-continuation scenario. It ends with a reader-driven map for inspecting individual sampled locations through time.

## Research Questions

- How did mapped annual PM2.5 concentrations change across Europe between 2007 and 2024?
- Which areas remained above the 10 µg/m³ annual threshold in 2024?
- Where did elevated concentrations persist across multiple years?
- If recent trends simply continued, which current hotspot cells could fall below 10 µg/m³ by 2030 or 2035?
- What can individual sampled locations reveal about the uneven pace of change?

## Repository Structure

```text
data_raw/          Original annual EEA GeoTIFF rasters
data_processed/    Analysis summaries and derived tabular outputs
docs/              Method notes, raster observations, and storyboard documentation
figures/           Generated maps, comparisons, and charts used by the story
prototype/         Final interactive website, explorer, and browser-ready assets
scripts/           Reusable preprocessing, analysis, and figure-generation scripts
Final_Report(Joannas).pdf  Final submitted ACM-format report
README.md          Project overview and reproduction guide
```

The main story is [`prototype/index.html`](prototype/index.html), and the reader-driven explorer is [`prototype/explorer.html`](prototype/explorer.html).

## Data Source

- **Provider:** European Environment Agency (EEA)
- **Dataset type:** Annual mapped PM2.5 concentration surfaces for Europe
- **Format:** GeoTIFF raster
- **Nominal resolution:** 1 km × 1 km
- **Period represented in the repository:** 2007–2024

The repository contains every annual raster available to this project within that period. A 2009 raster was not available, so browser-ready annual series preserve that year as missing rather than estimating a value. The annual files differ in metadata, geographic coverage, and valid-data masks; those differences are handled explicitly before comparison.

Official source: [European Environment Agency](https://www.eea.europa.eu/)

## Data Preprocessing and Analysis Workflow

1. **Inspect annual GeoTIFFs.** Record dimensions, coordinate reference systems, transforms, resolution, extent, and valid-data coverage for the available annual rasters.
2. **Align comparable rasters.** Reproject comparison years to a common reference grid and preserve valid-data masks so changes are calculated only for comparable cells.
3. **Summarize yearly PM2.5.** Calculate cleaned raster-cell annual means for the long-term trend while retaining the distinction from population-weighted exposure.
4. **Compare 2007 and 2024.** Produce the side-by-side comparison and aligned overlap-change map used in the story.
5. **Detect 2024 hotspots.** Identify valid 2024 cells above 10 µg/m³.
6. **Assess persistence.** Count repeated exceedances across available years to distinguish persistent hotspots from one-year patterns.
7. **Build a trend-continuation scenario.** Fit recent cell-level trends for current hotspots and classify potential threshold crossing by 2030, by 2035, later, or not under an unchanged-trend assumption. This is a scenario, not a forecast.
8. **Investigate local change in Ireland.** Examine the small cluster of apparent worsening separately, document its limited geographic extent, and report interpolation and coverage cautions.
9. **Create browser-ready samples.** Sample every available annual raster at the existing explorer locations and export compact JavaScript and JSON files with annual values, changes, exceedance counts, recent slopes, and scenario categories.

Reusable code is in [`scripts/`](scripts/), derived tables are in [`data_processed/`](data_processed/), methodological documentation is in [`docs/`](docs/), and generated visual outputs are in [`figures/`](figures/).

## Interactive Data Story

The final story uses an editorial, scroll-led structure rather than presenting all maps at once. Each chapter introduces one question, provides concise context, and then reveals the relevant project output. The final chapter links to the full explorer for reader-directed investigation.

- Story entry point: [`prototype/index.html`](prototype/index.html)
- Interactive explorer: [`prototype/explorer.html`](prototype/explorer.html)

## Interactive Features

- Scroll-triggered narrative and educational animations
- Responsive editorial layouts and annotated maps
- Interactive Leaflet explorer with pan and zoom
- Year scrubber and animated playback across available annual values
- Concentration, hotspot, and 2007–2024 change modes
- Fixed-size sampled raster circles with colour encoding PM2.5 magnitude or change
- Hover details for the selected year
- Click-to-inspect location panel with annual metrics and threshold history
- Per-location 2007–2024 sparkline and trend-continuation category
- Guided regional navigation and responsive mobile presentation

## How to Run the Data Story

From the repository root, start a local web server:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/prototype/index.html
```

VS Code's **Live Server** extension can be used as an alternative by serving the repository root and opening `prototype/index.html`.

Opening the HTML file directly from the filesystem may not reliably load all local scripts, data files, images, or browser security-dependent assets. A local HTTP server is recommended.

## Reproducibility

The original GeoTIFF inputs remain in `data_raw/`. Analysis scripts use repository-relative inputs and write reusable outputs to `data_processed/`, `figures/`, `docs/`, or `prototype/` as appropriate.

The scripts are organized by output rather than wrapped in one destructive pipeline, allowing individual analyses to be inspected and rerun independently. In particular:

- `scripts/create_current_hotspot_projection.py` reproduces the current-hotspot trend-continuation scenario.
- `scripts/investigate_ireland_pm25_change.py` reproduces the Ireland local-change investigation.
- `scripts/create_enriched_interactive_samples.py` rebuilds the compact annual dataset used by the explorer.

Generated outputs should only be refreshed when the corresponding source rasters or methodology change. Methodological assumptions and limitations are documented alongside the analyses in `docs/`.

## Final Report

The submitted ACM-format project report is included in the repository root:

- `Final_Report(Joannas).pdf`

The report summarizes the project development process, narrative design decisions, implementation, evaluation, and conclusions for the Data Journalism & Storytelling course submission.

## Technologies Used

- Python
- Rasterio, NumPy, pandas, and Matplotlib
- HTML, CSS, and JavaScript
- Leaflet
- SVG and Canvas
- QGIS for supplementary geospatial inspection
- Git for version control

## Limitations

- The EEA datasets are modelled and interpolated raster surfaces rather than direct measurements at every location.
- Raster-cell summaries are not population-weighted exposure estimates.
- Annual rasters differ slightly in spatial coverage; comparisons therefore use aligned, comparable areas only.
- The 2009 annual raster was unavailable and is preserved as missing.
- The hotspot trend-continuation analysis is an exploratory scenario based on recent trends rather than a forecast.

## Final Project Status

This repository contains the completed interactive data story submitted for the **Data Journalism & Storytelling** course, SoSe 2026, University of Konstanz. It includes the final scrollytelling website, interactive location explorer, reproducible analysis scripts, processed outputs, generated figures, methodological documentation, and the final submitted ACM-format report.