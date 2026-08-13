# Data

This folder separates source data, analysis-ready datasets, intermediate products, and large external inputs used by the project.

## Structure

### `raw/`

- `acs/` contains ACS demographic extracts and the block-group area file used to calculate population density.
- `hospitals/` contains the filtered citywide hospital point layer.
- `transit/` documents transit inputs that are stored externally.

### `processed/`

- `main/` contains the final citywide regression-ready dataset and the final citywide EWM results.
- `borough/` contains one regression-ready dataset for each borough.
- `intermediate/` contains staged demographic files plus EWM notebook inputs and outputs.
- `spatial/` contains accessibility and hotspot layers used in GIS and spatial analysis.

The main regression dataset is `processed/main/final_regression_ready_dataset.csv`. The citywide accessibility scores are in `processed/main/NEW_YORK_CITY_ALL_results_CORRECT.csv`.

### `external/`

Large or reproducible files are not copied into the repository. The text manifests in this folder document GTFS feeds, the OpenStreetMap `.pbf` extract, and large routing outputs. These files must be obtained or regenerated before rerunning routing.

## Data content

The workflow combines ACS demographic variables, 66 hospital facilities, MTA transit data, OpenStreetMap network data, EWM accessibility outputs, and regression-ready merged tables. See [`../docs/data_sources.md`](../docs/data_sources.md) for sources and variable definitions.

Do not edit processed values manually. Changes should be made through the scripts in [`../code/`](../code/) so the final datasets remain reproducible.

Full routing matrices and detailed itineraries remain excluded because they are
large and reproducible. The compact fastest-valid OD selections are retained
under `../generated_outputs/routing/selected_od_pairs/`; these are the direct
inputs to travel-time mapping and the next itinerary stage.
