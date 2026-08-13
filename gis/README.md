# GIS

This folder contains the QGIS project and spatial layers used to map hospital accessibility, inspect routing inputs, and present the EWM and hotspot results.

## Structure

- `project/` contains the active `nyc_healthcare_accessibility.qgz` project.
  `project/travel_time_analysis/` contains the separately preserved travel-time
  mapping project, and earlier versions remain under `project/archive/`.
- `layers/block_groups/` contains the NYC census block-group geometry used as the main spatial unit.
- `layers/boundaries/` contains borough boundary data.
- `layers/centroids/` contains borough block-group centroids and a 6,587-point
  citywide centroid layer used as routing origins.
- `layers/hospitals/` contains the original 66-record citywide hospital layer,
  borough subsets, and the 61-unique-facility layer used for routing.
- `layers/transit/lines/` and `layers/transit/stops/` contain transit layers used for map context and validation.
- `layers/routing_inputs/nyc_3_nearest_hospitals_unique.csv` is the portable
  three-candidate-per-origin table consumed by the current routing script. Its
  coordinate attributes are EPSG:3857 and are converted in Python before routing.
- `layers/routing_inputs/source_layers/` stores the local QGIS GeoPackages used
  to create that portable CSV. These working layers are excluded from Git.
- `layers/generated_outputs/` retains two legacy QGIS layers required by the
  untouched travel-time project.
- `layers/final_outputs/ewm/` contains final accessibility layers.
- `layers/final_outputs/hotspots/` contains the Getis-Ord Gi* hotspot and cold-spot shapefile.

Shapefile components (`.shp`, `.shx`, `.dbf`, `.prj`, and `.cpg` when available) must remain together. Do not move or rename layers without also updating their paths in the QGIS project.

The transit layers in this folder support mapping; routing itself uses GTFS and OpenStreetMap inputs documented under [`../data/external/`](../data/external/). Final exported maps belong in [`../figures/maps/`](../figures/maps/), not in this folder.

The bus visualization layers contain 1,189 route-shape features and 14,157 stop
points. They are for map context only; `r5py` reads the original static GTFS ZIP
archives rather than these GeoPackages.
