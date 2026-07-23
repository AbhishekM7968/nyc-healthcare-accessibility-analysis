# GIS

This folder contains the QGIS project and spatial layers used to map hospital accessibility, inspect routing inputs, and present the EWM and hotspot results.

## Structure

- `project/` contains the active `nyc_healthcare_accessibility.qgz` project. Earlier project versions are retained in `project/archive/`.
- `layers/block_groups/` contains the NYC census block-group geometry used as the main spatial unit.
- `layers/boundaries/` contains borough boundary data.
- `layers/centroids/` contains borough block-group centroids used as routing origins.
- `layers/hospitals/` contains the citywide hospital layer and borough subsets.
- `layers/transit/lines/` and `layers/transit/stops/` contain transit layers used for map context and validation.
- `layers/final_outputs/ewm/` contains final accessibility layers.
- `layers/final_outputs/hotspots/` contains the Getis-Ord Gi* hotspot and cold-spot shapefile.

Shapefile components (`.shp`, `.shx`, `.dbf`, `.prj`, and `.cpg` when available) must remain together. Do not move or rename layers without also updating their paths in the QGIS project.

The transit layers in this folder support mapping; routing itself uses GTFS and OpenStreetMap inputs documented under [`../data/external/`](../data/external/). Final exported maps belong in [`../figures/maps/`](../figures/maps/), not in this folder.
