# Raster Metadata Observations



## Implementation check



I inspected the metadata of all available EEA PM2.5 GeoTIFF files in `data_raw`.



## Main finding



The annual raster files use the same coordinate reference system, EPSG:3035 / ETRS89-LAEA Europe, but they do not all have the same shape, coverage, data type, or no-data definition.



## Observed raster groups



### Earlier files

Several earlier files have the shape:



- 4037 x 3890



This includes years such as 2007, 2008, 2010, 2011, 2012, 2013, and 2015.



### Later files

Several later files have the shape:



- 4037 x 4680



This includes years such as 2016, 2017, 2019, 2020, 2021, and 2022.



### Special cases

- 2014 has a different shape, data type, and no explicit no-data value.

- 2018 and 2023 have larger raster shapes.

- 2024 has a slightly different height compared to other later files.



## Consequence for analysis



Full-map comparison across all years would be misleading because the spatial coverage is not identical.



For fair long-term comparison, the analysis should use:



- overlapping valid raster cells,

- or a standardized study area,

- or resampled/aligned raster grids.



## Next preprocessing step



The next implementation step is to align the rasters and calculate change only for the shared valid area.

