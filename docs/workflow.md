# Research workflow

The project combines scripted processing with several GIS preparation steps.
The diagram below shows the intended order and the repository location for each
stage.

```text
Raw Data
   ↓
Data Cleaning
   ↓
GIS Preparation
   ↓
Transit Routing
   ↓
Accessibility Indicators
   ↓
Entropy Weight Method
   ↓
Spatial Analysis
   ↓
Regression Analysis
   ↓
Figures and Results
```

## 1. Raw data

Inputs include ACS five-year estimates, NYS Department of Health hospital
records, MTA GTFS archives, an OpenStreetMap PBF extract, census block groups,
and borough boundaries.

- Small raw and source tables are under `data/raw/`.
- Large or frequently updated routing inputs are documented under
  `data/external/` and are not committed.
- Spatial source and working layers are under `gis/layers/`.

See [data_sources.md](data_sources.md) for dataset-level provenance.

## 2. Demographic collection and cleaning

`code/data_collection/download_acs_demographics.py` downloads 2024 ACS
five-year block-group estimates for the five NYC counties. It constructs the
block-group rates used in the analysis and removes zero-population rows.

`code/preprocessing/add_tract_missing_vars.py` downloads tract poverty,
disability, and insurance variables, calculates rates, and joins them to block
groups using tract GEOID.

`code/preprocessing/cleaning_for_regression.py` identifies records with missing
required predictors and creates a complete analysis subset.

`code/preprocessing/add_population_density.py` and
`code/preprocessing/build_final_dataset.py` add Census land area, calculate
population density, merge the corrected citywide EWM score, and validate the
final output.

Important files are organized as:

- `data/raw/acs/`: downloaded ACS and land-area inputs;
- `data/processed/intermediate/`: cleaned and merged intermediate tables; and
- `data/processed/main/final_regression_ready_dataset.csv`: final citywide
  regression dataset.

## 3. GIS preparation

QGIS was used to prepare block-group polygons, representative origin points,
hospital points, borough subsets, and map-ready spatial joins. The active
project is `gis/project/nyc_healthcare_accessibility.qgz`.

The repository does not contain code that fully reproduces the hospital filter,
the block-group representative points, or the nearest-hospital candidate list.
These are documented as GIS preparation steps rather than automated pipeline
steps.

The resulting portable candidate export is
`gis/layers/routing_inputs/nyc_3_nearest_hospitals_unique.csv`. It contains
three candidate rows for each of 6,587 block-group origins and references the
61 unique routing facilities.

## 4. Transit routing

Before running the routing scripts:

1. place `nyc.osm.pbf` under `data/external/local_inputs/osm/`;
2. place the required GTFS ZIP archives under `data/external/local_inputs/gtfs/`;
3. provide the configured borough OD candidate CSVs; and
4. install `r5py`, its Python geospatial dependencies, Java, and a compatible R5
   runtime.

The expected external filenames are listed in `data/external/gtfs/` and
`data/external/osm/`.

For each borough, run `code/routing/routing_algorithm_time_matrix.py` with
`--borough`, a GTFS-covered `--departure`, and (optionally) a departure window.
The script loads three hospital candidates per block-group origin, converts the
QGIS coordinate attributes from EPSG:3857 to EPSG:4326, and routes each
candidate using the same citywide subway and bus network. Queens also includes
LIRR.

Example:

```bash
python code/routing/routing_algorithm_time_matrix.py \
  --borough queens \
  --departure 2026-07-08T08:00:00
```

After all five matrices exist, run:

```bash
python code/routing/select_fastest_od_pairs.py
```

This keeps the fastest valid candidate for every routable origin, preserves
unavailable candidates in an audit table, and retains unresolved origins rather
than assigning zero travel time or silently dropping them. The citywide status
file contains one row per block group and is written under
`generated_outputs/routing/selected_od_pairs/`.

Set the same borough in
`code/routing/routing_algorithm_itineraries.py` and run it against the selected
OD table. Repeat both routing stages for all five boroughs. Large outputs are
written under `generated_outputs/routing/itineraries/` and are excluded from Git.

## 5. Accessibility indicators

The detailed itineraries are summarized to one record per origin with the six
final burden indicators:

- transfers;
- walking time;
- walking distance;
- total travel time;
- total distance; and
- waiting time.

The borough indicator inputs used by the EWM notebooks are stored in
`data/processed/intermediate/ewm_inputs/`. The repository does not currently
contain one consolidated script that converts raw detailed itinerary segments
into every final indicator table.

## 6. Entropy Weight Method

The six notebooks in `notebooks/ewm/` show the normalization, probability,
entropy, diversity, weight, and final score calculations. Each notebook writes
results and weights to `data/processed/intermediate/ewm_outputs/`.

The corrected citywide result selected for downstream analysis is
`data/processed/main/NEW_YORK_CITY_ALL_results_CORRECT.csv`. Borough-specific
regression-ready files are under `data/processed/borough/`.

## 7. Final dataset construction

Run:

```bash
python code/preprocessing/build_final_dataset.py
```

The script starts from the tract-enriched demographics table, joins block-group
land area, calculates population density, merges the corrected EWM score, checks
IDs and missing values, and writes:

```text
data/processed/main/final_regression_ready_dataset.csv
```

The validated file contains 6,347 block groups and 39 columns.

## 8. Spatial analysis

The EWM score is joined to block-group geometry for QGIS mapping. The preferred
layer is `gis/layers/final_outputs/ewm/nyc_ewm_accessibility.gpkg`.

Run the R hot spot script from the repository environment:

```bash
Rscript code/spatial_analysis/hotspot_analysis.R
```

It reports Moran's I, calculates local Gi* z-scores using eight nearest
neighbors, and writes the generated hot spot layer. The curated final spatial
files are kept under `data/processed/spatial/` and
`gis/layers/final_outputs/hotspots/`.

## 9. Regression and diagnostics

Regression code is grouped under `code/regression/`:

- `ols/`: citywide and borough OLS models;
- `quantile_r/`: 25th-, 50th-, and 75th-percentile regression;
- `GAM_r/`: nonlinear smooth effects; and
- `diagnostic/`: VIF checks and Moran's I residual diagnostics.

The final HTML tables are under `results/tables/`. The GAM graphic is under
`figures/models/gam/`.

The saved HTML tables should be treated as the record of reported results.
Some current scripts and older table-generation code do not use identical input
filenames or outcome transformations, so exact table regeneration should be
checked before publication.

## 10. Figures and results

Run the chart driver with:

```bash
python code/visualization/charts/run_all_figures.py
```

Final charts are stored in `figures/main/`, citywide map exports in
`figures/maps/citywide/`, and the GAM figure in `figures/models/gam/`. Regression
tables and the concise findings summary are stored in `results/`.

The borough map directory is currently empty; those maps remain a pending
deliverable.
