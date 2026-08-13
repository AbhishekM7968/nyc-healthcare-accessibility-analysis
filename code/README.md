# Code

This folder contains the scripts used to build datasets, calculate transit accessibility, run statistical models, perform spatial analysis, and generate figures.

## Structure

- `data_collection/` downloads ACS demographic variables.
- `preprocessing/` cleans demographic data, adds tract variables and population density, merges accessibility scores, and builds the final regression-ready dataset.
- `routing/` contains the `r5py` travel-time matrix, fastest-valid OD selection, and detailed-itinerary workflows. `routing_map_point_to_point.py` is a test/debug script rather than part of the main pipeline.
- `regression/` contains citywide and borough OLS models, quantile regression, GAM analysis, VIF checks, and Moran’s I diagnostics for model residuals.
- `spatial_analysis/` contains the Getis-Ord Gi* hotspot analysis.
- `visualization/` contains scripts for final charts and the figure runner.

The EWM calculations are retained in [`../notebooks/ewm/`](../notebooks/ewm/) because they were developed and checked interactively.

## Running the code

Create the Python environment from the repository root:

```bash
conda env create -f environment.yml
conda activate nyc-healthcare-access
```

The Conda environment includes Python, the geospatial stack, `r5py`, JupyterLab, and OpenJDK 21. A pip alternative is available in `requirements.txt`, but Java must then be installed separately for routing.

The R package list and one-time installation instructions are in [`R_REQUIREMENTS.md`](R_REQUIREMENTS.md). QGIS is required to open the project under `gis/project/`.

Before running an analysis stage, check the repository:

```bash
python code/validate_repository.py
```

The pipeline launcher provides a single entry point for the scripted stages that can be run from the committed repository:

```bash
python code/run_pipeline.py --list
python code/run_pipeline.py validate
python code/run_pipeline.py safe --dry-run
```

`safe` builds the final dataset, validates it, and regenerates the standard charts. Routing, EWM notebooks, GIS preparation, and model estimation remain explicit stages because they require external inputs, manual decisions, or separate software.

Scripts use repository-relative paths where possible. Consult [`../docs/workflow.md`](../docs/workflow.md) before rerunning the analysis.

### Travel-time analysis

The current travel-time workflow is:

```bash
python code/routing/routing_algorithm_time_matrix.py \
  --borough queens \
  --departure 2026-07-08T08:00:00

python code/routing/select_fastest_od_pairs.py
```

Repeat the matrix command for `bronx`, `brooklyn`, `manhattan`, and
`staten_island` before running the selection script. The routing script uses
the citywide candidate table at
`gis/layers/routing_inputs/nyc_3_nearest_hospitals_unique.csv`, converts its
QGIS coordinates from EPSG:3857 to EPSG:4326, and evaluates three candidate
hospitals per block group. The selection script retains the fastest valid
candidate and writes compact, shareable outputs under
`generated_outputs/routing/selected_od_pairs/`.

The optional next stage uses one of those selected files:

```bash
python code/routing/routing_algorithm_itineraries.py \
  --borough queens \
  --departure 2026-07-08T08:00:00
```

Download and placement instructions for every GTFS archive and the OSM network
are in [`../data/external/README.md`](../data/external/README.md).

## Census API key

`data_collection/download_acs_demographics.py` reads the Census API key from the `CENSUS_API_KEY` environment variable. Keep the key out of source files and local `.env` files out of Git.

On macOS or Linux, set the key only in the terminal session used to run the script:

```bash
export CENSUS_API_KEY="your_new_key"
python code/data_collection/download_acs_demographics.py
```

If a key has ever been committed or pushed, replace it before running the script again.
