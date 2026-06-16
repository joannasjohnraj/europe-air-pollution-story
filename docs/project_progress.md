# Project Progress

## Date

9 June 2026

## Current Status

### Completed

* Selected project topic: PM2.5 air pollution in Europe
* Reviewed existing journalism and related visual stories
* Completed Narrative Structure assignment
* Completed Transition & Order assignment
* Completed Narrative Patterns assignment
* Collected European Environment Agency PM2.5 dataset
* Downloaded annual PM2.5 raster data (2007–2024, except 2009)
* Organized project repository structure

### Key Feedback Received

* The story should go beyond the known observation that air quality is unequally distributed in Europe.
* The audience should learn something new.
* Story pieces need to be defined in detail, not only as high-level stages.
* Existing visual stories should be used as inspiration, not copied.

### Current Direction

Investigate long-term PM2.5 changes across Europe and identify:

* regions with the greatest improvement,
* regions with the least improvement,
* persistent pollution hotspots.

### Next Steps

* Explore raster data structure
* Generate first visualizations from TIFF files
* Define detailed story pieces
* Refine the central story question
* Begin interactive prototype development


## Implementation Progress – Week of 16 June

This week, the project moved further from story planning into implementation and raster analysis.

### Completed

- Inspected metadata of all available EEA PM2.5 GeoTIFF files.
- Found that the annual raster files use the same projection but do not all have the same shape or spatial coverage.
- Documented this issue in `docs/raster_metadata_observations.md`.
- Created an overlap-based PM2.5 change map for 2007 to 2024.
- Created a first 2024 hotspot map using the threshold PM2.5 > 10 µg/m³.
- Updated GitLab with new implementation figures.

### Initial Findings

- Full-map comparison across years is not reliable without preprocessing because raster coverage differs.
- In the overlapping valid area, mean PM2.5 decreased from about 11.17 µg/m³ in 2007 to about 6.73 µg/m³ in 2024.
- The average change in the overlapping valid area is about -4.44 µg/m³.
- In 2024, about 20.7% of valid raster cells are above 10 µg/m³.
- Remaining hotspot areas are visible in regions such as Northern Italy, Poland, the Balkans, Turkey, and parts of Southeastern Europe.

### Next Steps

- Standardize or align raster files before using the full time series.
- Include intermediate years in the analysis.
- Identify persistent hotspots across multiple years.
- Improve map styling and annotations.
- Connect the analysis outputs to the interactive visual story prototype.