# Methods and reproducibility

## Two stages of work

The original project was built in October–November 2026 using ArcGIS Pro/ArcPy, the ArcGIS API for Python, GDAL, NumPy and scripted web-map definitions. Its published maps include river-network references, watershed and land-cover context, reported oxygen values, CHIRPS rainfall, Hansen tree-cover loss and a StoryMaps village tour.

This portfolio edition was assembled on 24 November 2026 after the author lost ArcGIS Pro access. It contains a curated public-data collector from that project, new portable Python adapters, saved evidence inputs and original figures. It does not authenticate to ArcGIS, modify the StoryMap or reproduce every desktop layout. Retained inputs represent the saved project state, not a new field investigation or a fresh scientific verification of each news report.

## Evidence join and proportional symbols

The eight transcribed readings retain source URLs, publication dates, unknown sample times and uncertainty notes. Five records carry GeoNames IDs and can be associated with settlement references. Three descriptions refer to a canal and positions upstream/downstream, but lack coordinates and remain in the CSV/chart only. A source description naming a company is preserved as an attributed location description, not a finding of responsibility.

The left join keeps all nine settlement references. Four absent values remain null. Display names are normalized separately from original names. Filled circles show known values; hollow circles identify missing values in this source.

Circle diameter follows `28 × sqrt(value / 6.19)`. Squaring diameter is proportional to circle area, so area represents mg/L. The 28-point maximum is a display choice. Leaflet uses the same relative scale in pixel units; neither size is a geographic radius. Marker size does not indicate event extent.

## Rainfall

The saved preparation read CHIRPS v3 final daily rasters, rnl branch, over 35 days from 5 July through 8 August 2026. Five consecutive seven-day sums were formed with complete data. Approximately 0.05-degree grid cells intersecting the research watershed delineation were retained. The CSV contains 370 grid-cell centers and five totals. The portable map reconstructs their native square extents at ±0.025 degrees.

These are estimated grid-cell precipitation totals in millimetres. They are not local rain-gauge observations, stream discharge, pollutant load or proof of flow through a particular outlet. The map uses common thresholds across all weeks: ≤100, >100–200, >200–400 and >400 mm. Turn on one rainfall layer at a time; stacking them is not a valid temporal comparison.

## Historical tree-cover loss

The saved extraction used Hansen Global Forest Change v1.13, loss years 2001–2025, with baseline canopy ≥30% in 2000. The selected rectangle is [-88.90, 17.25, -88.30, 17.75] in longitude/latitude, distinct from the research watershed.

The original GDAL workflow polygonized loss-year pixels, grouped disconnected patches for display and estimated polygon areas using an ellipsoidal degree-area conversion at each polygon centroid. The archive summary reports 61,851 patches and 880 display groups. The figure simply redraws annual hectares from the saved statistics; it does not rerun that raster extraction. These approximate gross-loss hectares exclude regrowth and should not be relabeled as hectares of agricultural clearing. Pixel size is about 30 m, varying with latitude. No 2026 loss is represented.

## Coordinate systems and reference offsets

Bundled GeoJSON is WGS84 longitude/latitude. Optional nearest-distance calculations project to EPSG:32616. Historical river geometry is retrieved from the source service and may differ from modern imagery. Gazetteer references also vary in placement. Offsets are straight-line minimum distances, not river-route distances, bank access, exposure or sampling error. The optional distance analysis was run against the recovered local hydrography for release verification; a future download may differ.

## Verification scope

The evidence build and rendering scripts are run locally; tests assert eight records, five joined readings, four missing community values, three unlocated readings, source-value preservation and the area scaling relationship. Generated CSV/GeoJSON and the HTML map are inspected. These checks validate the transformations, not the accuracy of the original investigation or a causal explanation of the fish kill.

The standalone ArcPy adapter requires an active ArcGIS Pro licence and is syntax-checked only in this release. The network collector is archived code; live retrieval is optional. The public StoryMap is maintained separately, and may change after this repository snapshot.
