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

## Implementation Progress – Interactive Prototype and Persistent Hotspots  
**Date:** 19 June 2026

This week, I extended the project from static raster outputs toward a first interactive visual data story prototype.

Completed work:
- Calculated cleaned yearly mean PM2.5 values for all available raster years from 2007 to 2024, excluding 2009 because it is not available in the dataset.
- Created a time-series chart showing the long-term PM2.5 trend across available years.
- Created a persistent hotspot analysis by counting how often comparable raster cells were above 10 µg/m³ across the available years.
- Created a categorical persistent-hotspot map showing areas that exceeded the threshold in 40–60%, 60–80%, and 80–100% of valid years.
- Built a first interactive HTML prototype in `prototype/index.html`.
- Connected the main story stages to the current analysis outputs: overview, intermediate-year trend, change map, 2024 hotspots, persistent hotspots, and planned reader exploration.

Current interpretation:
The analysis shows that PM2.5 levels decreased strongly across Europe over time, but remaining pollution is spatially uneven. The persistent-hotspot map helps shift the story from a single-year view to the question of which areas repeatedly remain above the threshold.

Current limitation:
The raster files do not all have identical spatial coverage. Therefore, direct change and persistence analyses are based on comparable raster areas and should be described carefully. The current values are raster-cell based and not population-weighted exposure estimates.

Next steps:
- Improve the interactive prototype so it becomes more than a clickable slideshow.
- Add clearer annotations and explanatory text inside the story.
- Develop reader-driven exploration, such as switching between years or views.
- Continue refining the final story structure for the presentation and report.


## Implementation Progress – Scrollytelling Website Refinement  
**Date:** 07 July 2026

This week, I responded to feedback that the project should feel more like a data story and less like a collection of maps.

### Completed

- Redesigned the website into a scrollytelling structure.
- Added clearer narrative flow: introduction, PM2.5 explanation, sources, baseline, transition, trend, hotspots, regional focus, and reader exploration.
- Improved the 2007 to 2024 interactive transition using sampled PM2.5 values.
- Added slower Play animation so the transition is easier to follow.
- Refined the interactive explorer map with year scrubbing, hover values, and cleaner sampled-point visualization.
- Removed visually distracting raster overlays from the explorer map.
- Improved educational text so the website explains PM2.5, hotspots, and uneven improvement more clearly.
- Unified the visual language and improved layout consistency.

### Current Focus

The project now focuses on the main message:

> Europe’s PM2.5 levels improved, but the improvement is uneven and important hotspots remain.

### Next Steps

- Add exact official EEA, WHO, and EU citations.
- Improve remaining map visuals and legends.
- Refine final text for an environmental audience.
- Continue polishing the scrollytelling experience for the final presentation.

# Final Development Progress
**Date:** 13 July 2026

The project has moved from an interactive prototype to a complete visual data story for final submission.

## Storytelling

- Redesigned the website as a complete scrollytelling experience with a clear question-and-answer structure.
- Added a narrative introduction that establishes the central story of broad improvement and continuing spatial inequality.
- Added **From monitoring stations to a map of Europe** to explain how station observations become EEA raster maps.
- Added **Europe in 2007** as the visual and narrative baseline for the analysis.
- Redesigned **Has Europe improved?** as a clear 2007–2024 comparison with project-derived summary values.
- Added **Why did Europe become cleaner?** to connect the observed change with cleaner technologies, emission controls, and European policy.
- Added the hotspot trend-continuation scenario to examine what could happen if recent trends continued unchanged.
- Added the Ireland local exception as a cautious, visually subordinate example of uneven change.
- Improved transitions so each section answers one question and leads naturally to the next.

## Data Analysis

The final project includes:

- metadata inspection for all available annual EEA GeoTIFF rasters;
- raster alignment and preservation of valid-data masks;
- comparable-area overlap analysis for 2007 and 2024;
- cleaned yearly PM2.5 raster-cell summaries;
- 2024 and persistent hotspot detection;
- a recent-trend continuation scenario for current hotspot cells;
- a focused investigation of local change in Ireland; and
- an enriched browser-ready sampling dataset with annual values and derived metrics.

The reusable preprocessing and analysis scripts are fully documented in `scripts/`, with supporting methodological notes in `docs/`.

## Interactive Features

- Scroll-led storytelling with staged visual and textual reveals.
- Annotated maps that identify important regions and guide interpretation.
- A responsive Leaflet explorer with year scrubbing, playback, map modes, pan, and zoom.
- A click-to-inspect panel for individual sampled raster locations.
- An annual sparkline showing PM2.5 values and the 10 µg/m³ threshold.
- Automatic, data-based interpretation for each selected location.
- Responsive layouts for desktop and smaller screens.
- Constant-size sampled points, with PM2.5 magnitude communicated through colour rather than bubble area.

## Audience Feedback

**Feedback:** “The story should teach the reader.”

**Response:** Added concise educational sections explaining PM2.5, measurement and mapping methods, pollution sources, health relevance, and European policy.

**Feedback:** “The maps should guide the audience.”

**Response:** Added regional annotations, guided findings, clearer legends, and stronger narrative transitions between visualizations.

**Feedback:** “Increase interactivity.”

**Response:** Built an enriched interactive explorer with annual values, year controls, location profiles, sparklines, threshold history, and trend-continuation information.

**Feedback:** “Explain preprocessing.”

**Response:** Added reproducible scripts and methodological documentation describing raster metadata, alignment, comparable areas, missing data, sampling, and analysis limitations.

## Current Status

The project is functionally complete and has entered the final polishing phase before submission.

Remaining work consists of:

- final visual polish;
- consistency review;
- presentation preparation; and
- final report.
