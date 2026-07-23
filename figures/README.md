# Figures

This folder contains final, presentation-quality charts and maps produced for the accessibility analysis.

## Structure

- `main/` contains the principal statistical and descriptive charts, including the accessibility distribution, population percentiles, borough above-average access, cold-spot population, and EWM indicator weights.
- `maps/citywide/` contains the final citywide EWM accessibility and hotspot maps.
- `maps/borough/` is reserved for final borough-specific map exports.
- `models/gam/` contains the exported GAM smooth-effect figure.

Chart-generation scripts are stored in [`../code/visualization/`](../code/visualization/), including `run_all_figures.py` for the standardized chart workflow. GIS map exports are produced from the QGIS project in [`../gis/project/`](../gis/project/).

Only final figures belong here; data tables, temporary plots, and routing outputs are stored elsewhere.
