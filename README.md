# Air Pollution in Europe — PM2.5 Data Story (2024)

## Project Overview
This project is a data journalism exploration of air pollution (PM2.5) across Europe.  
It investigates spatial inequality in air quality and how exposure varies across regions.

Using geospatial analysis, the project aims to reveal patterns of environmental inequality and highlight differences in population exposure to fine particulate matter.

---

## Story Focus
While air quality in Europe has improved over recent decades, PM2.5 exposure remains unevenly distributed.

The central narrative of this project is that environmental quality is strongly shaped by geography, with persistent regional disparities in pollution levels across Europe.

---

## Data Source
- Provider: European Environment Agency (EEA)  
- Dataset: PM2.5 European air quality data (2024, interpolated interim dataset)  
- Format: GeoTIFF raster (1 km grid resolution)  
- Publication date: June 2025  
- Coverage: Europe  

Official source:  
https://www.eea.europa.eu/

---

## Tools Used
- Python (raster processing, analysis, and chart generation)
- Rasterio / NumPy / Matplotlib (geospatial raster analysis and visualization)
- HTML / CSS / JavaScript (first interactive prototype)
- QGIS (geospatial inspection and visualization)
- GitLab (version control and project tracking)

---

## Visualization
- Raster heatmap of PM2.5 annual mean concentration across Europe
- Color scale interpretation:
  - Blue / Green → low pollution
  - Yellow / Orange → moderate pollution
  - Red → high pollution

---

## Research Questions
- How does PM2.5 exposure vary across European regions?
- Which regions consistently experience higher pollution levels?
- What spatial inequalities in air quality can be observed?

---

## Key Insight
Preliminary analysis suggests a clear spatial divide in PM2.5 exposure across Europe, with higher pollution levels concentrated in Central and Eastern regions compared to Northern Europe.

---

## Limitations
- Dataset is interpolated (combining monitoring data and model estimates)
- Health outcomes are not directly measured
- Spatial resolution is grid-based and not city-specific
- Temporal analysis is currently based on cleaned raster-cell means and should not yet be interpreted as population-weighted exposure
- Raster files do not all have identical spatial coverage, so direct comparisons are based on shared comparable areas

---

## Project Status

This project is being developed as part of the **Data Journalism & Storytelling** course (SoSe 2026) at the University of Konstanz.

Current progress includes:

- Interactive scrollytelling website structure.
- PM2.5 introduction and educational context.
- Interactive 2007–2024 transition map.
- Yearly PM2.5 trend analysis.
- 2007–2024 overlap change analysis.
- 2024 hotspot analysis.
- Persistent hotspot analysis.
- Interactive exploration map with year scrubbing and regional exploration.

The current focus is refining the visual design, educational content, interaction quality, and integrating official EEA, WHO, and EU information before the final presentation.