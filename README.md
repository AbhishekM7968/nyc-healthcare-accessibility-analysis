# NYC Healthcare Accessibility

This repository contains a research workflow for measuring access to hospitals by public transit across New York City. The project examines how transit travel conditions and neighborhood demographics relate to healthcare accessibility at the census block-group level and across the five boroughs.

## Research goal
This project evaluates public transit accessibility to healthcare facilities in New York City using a multi-criteria accessibility index constructed with the Entropy Weight Method (EWM).

The goal is to identify geographic and demographic differences in access to hospital care by public transit. The analysis combines hospital locations, transit schedules, street-network data, accessibility indicators, spatial statistics, and regression models.

## Method overview

- Hospital facilities are represented by 66 filtered hospital points.
- MTA GTFS feeds and OpenStreetMap data provide the transit and street networks.
- `r5py` calculates travel-time matrices and detailed transit itineraries between block-group origins and nearby hospitals.
- The Entropy Weight Method (EWM) combines travel time, distance, walking, waiting, and transfer indicators into an accessibility index.
- QGIS and spatial-analysis code support accessibility mapping and Getis-Ord Gi* hotspot analysis.
- OLS, quantile regression, and generalized additive models (GAMs) examine relationships between accessibility and demographic conditions.

## Repository structure

| Folder | Contents |
|---|---|
| [`code/`](code/) | Data collection, preprocessing, routing, regression, spatial-analysis, and visualization scripts |
| [`data/`](data/) | Raw inputs, processed datasets, and references to large external data |
| [`docs/`](docs/) | Methodology, data-source notes, workflow documentation, and research decisions |
| [`figures/`](figures/) | Final charts, maps, and model figures |
| [`gis/`](gis/) | QGIS project files and organized spatial layers |
| [`notebooks/`](notebooks/) | Citywide and borough EWM calculations |
| [`results/`](results/) | Final regression tables and a short findings summary |
| [`paper/`](paper/) | Reserved location for manuscript files |
| [`presentation/`](presentation/) | Reserved location for presentation materials |

Start with [`docs/workflow.md`](docs/workflow.md) for the full analysis sequence and [`docs/methodology.md`](docs/methodology.md) for methodological details.

## Reproducibility notes

Large GTFS, OpenStreetMap, and routing-output files are not stored in GitHub. Their expected sources and original locations are documented under `data/external/`. Python, R, Java, QGIS, and Jupyter are required for different parts of the workflow; individual folder READMEs describe the relevant requirements.

The final SRA paper and presentation are not included because they were created using program resources. The `paper/` and `presentation/` directories are retained only as reserved locations if those materials can be shared later.
