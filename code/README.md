# Code

This folder contains the scripts used to build datasets, calculate transit accessibility, run statistical models, perform spatial analysis, and generate figures.

## Structure

- `data_collection/` downloads ACS demographic variables.
- `preprocessing/` cleans demographic data, adds tract variables and population density, merges accessibility scores, and builds the final regression-ready dataset.
- `routing/` contains the `r5py` travel-time matrix and detailed-itinerary workflows. `routing_map_point_to_point.py` is a test/debug script rather than part of the main pipeline.
- `regression/` contains citywide and borough OLS models, quantile regression, GAM analysis, VIF checks, and Moran’s I diagnostics for model residuals.
- `spatial_analysis/` contains the Getis-Ord Gi* hotspot analysis.
- `visualization/` contains scripts for final charts and the figure runner.

The EWM calculations are retained in [`../notebooks/ewm/`](../notebooks/ewm/) because they were developed and checked interactively.

## Software

The Python workflow uses packages including `pandas`, `geopandas`, `statsmodels`, and `r5py`. Routing also requires Java plus local GTFS and OpenStreetMap inputs. The R analyses use packages such as `mgcv`, `gratia`, `ggplot2`, `quantreg`, `modelsummary`, `sf`, `spdep`, and `dplyr`, depending on the script.

Scripts use repository-relative paths where possible. Run them within the repository structure shown in the root README, and consult [`../docs/workflow.md`](../docs/workflow.md) before rerunning the full pipeline.

## Census API key

`data_collection/download_acs_demographics.py` reads the Census API key from the `CENSUS_API_KEY` environment variable. Keep the key out of source files and local `.env` files out of Git.

On macOS or Linux, set the key only in the terminal session used to run the script:

```bash
export CENSUS_API_KEY="your_new_key"
python code/data_collection/download_acs_demographics.py
```

If a key has ever been committed or pushed, replace it before running the script again.
