\# Interactive Story Prototype v2 Plan



\## Main message



Europe’s PM2.5 levels improved between 2007 and 2024, but remaining hotspots show that the improvement is uneven.



\## Core interaction



The central interaction should be a user-controlled transition from 2007 to 2024.



The reader should be able to drag a slider or use a transition control to see how PM2.5 levels changed over time.



\## Main visual sequence



1\. Explain PM2.5 and why it matters.

2\. Show Europe in 2007.

3\. Let the reader transition from 2007 to 2024.

4\. Reveal that overall PM2.5 decreased.

5\. Highlight remaining 2024 hotspots.

6\. Allow the reader to zoom into selected hotspot regions.

7\. Let the reader explore views and regions.



\## Required interactions



\- Year slider from 2007 to 2024.

\- Smooth transition between PM2.5 map layers.

\- Toggle for hotspot overlay.

\- Zoom and pan map.

\- Clickable hotspot regions.

\- Region-specific annotations.

\- Side text that changes with the selected year, layer, or region.



\## Visual layers needed



\- 2007 PM2.5 map layer.

\- 2024 PM2.5 map layer.

\- 2007–2024 change layer.

\- 2024 hotspot layer.

\- Later: selected region focus layers or annotations.



\## Why this is better than the current prototype



The current prototype has map interaction, but it does not yet show the actual PM2.5 raster maps inside the interactive map.



The next version should make the data itself interactive, not only the explanation.



\## Implementation strategy



First, create georeferenced image overlays from the raster outputs.



Then add them to a Leaflet map.



Then add a year slider and opacity transition between 2007 and 2024.



After that, add hotspot overlay and region annotations.



\## Important limitation



The raster files do not all have identical spatial coverage. The prototype should explain this clearly. The 2007 to 2024 transition should be described as a visual comparison first, while exact change calculations should use comparable raster areas.

