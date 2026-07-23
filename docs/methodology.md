# Methodology

## Study design

The study uses NYC census block groups as the primary unit of analysis. Block
groups provide finer spatial detail than census tracts while still supporting
the demographic measures needed for the equity analysis. The five boroughs are
analyzed together and separately because transit service, hospital density, and
urban form differ substantially across the city.

The outcome is relative access to hospitals by scheduled public transit. Each
block group is represented by a point used as a routing origin. Hospital
facilities are represented by geocoded point locations and used as candidate
destinations. The final citywide hospital layer contains 66 facilities.

Four borough point layers use Census internal-point coordinates. Manhattan uses
a QGIS Point on Surface layer. Both methods place the point inside its polygon,
but they are not identical geometric definitions.

## Transit accessibility workflow

### Network inputs

The routing network combines:

- static MTA GTFS feeds for subway and applicable borough bus service;
- an OpenStreetMap PBF extract for the pedestrian and street network; and
- Long Island Rail Road GTFS in the configured Queens workflow.

The files are loaded with `r5py.TransportNetwork`. The external files are too
large and change too frequently to keep in Git; their expected filenames,
service dates, and archived checksums are documented under `data/external/`.

### Origins and destinations

Origins are block-group representative points in EPSG:4326. The OD tables use
the fields `centroid_x` and `centroid_y` for origins and `nearest_x` and
`nearest_y` for hospitals. The routing scripts describe each borough input as
containing approximately three candidate hospitals per origin.

This is a reduced candidate design, not a full block-group-by-hospital matrix.
The candidate list was prepared before the current routing scripts. The
repository does not contain a standalone script that reproduces the nearest-
hospital selection, so that preparation step remains partly GIS-based.

### Time matrix and itinerary selection

`code/routing/routing_algorithm_time_matrix.py` calculates an R5 travel-time
matrix for the candidate OD records. After that stage, each borough has a
reduced selected or fastest OD table. The selection is intended to retain the
fastest reachable hospital among the nearby candidates. The exact reduction
operation is not automated in the current repository and should be documented
if it is rerun.

`code/routing/routing_algorithm_itineraries.py` uses the reduced OD tables to
extract detailed itineraries. Those itineraries provide the components used in
the accessibility index:

- transfers;
- walking time;
- walking distance;
- total travel time;
- total distance; and
- waiting time.

The detailed itinerary and matrix outputs are excluded from Git because they
are large. Their expected output names are listed in
`data/external/routing_outputs.txt`.

## Entropy Weight Method

### Rationale

The six routing measures are expressed in different units and do not contribute
equally to the observed differences between origins. EWM was selected as a
data-driven alternative to assigning weights through researcher judgment. A
criterion receives more weight when it contains more information, represented
by greater differentiation across observations.

This does not mean that EWM estimates travelers' preferences. It weights
statistical variation, not perceived burden or clinical importance.

### Cost indicators and normalization

All six final indicators are cost indicators: a lower raw value indicates a
less burdensome trip. Each criterion is converted so that a higher normalized
value indicates better accessibility:

```text
r_ij = (max_j - x_ij) / (max_j - min_j)
```

The normalized values are converted to within-column proportions:

```text
p_ij = r_ij / sum_i(r_ij)
```

The notebooks replace zero proportions with a small positive value before
taking logarithms. For criterion `j`, entropy is calculated as:

```text
e_j = -k * sum_i(p_ij * ln(p_ij)), where k = 1 / ln(n)
```

Diversity and the final criterion weight are:

```text
d_j = 1 - e_j
w_j = d_j / sum_j(d_j)
```

The accessibility index for each origin is the weighted sum of its normalized
criteria:

```text
EWM_i = sum_j(w_j * r_ij)
```

The resulting score is relative to the observations and criteria used in that
EWM run. Higher values indicate lower overall transit burden and therefore
better relative hospital accessibility.

### Citywide and borough calculations

The notebooks under `notebooks/ewm/` calculate one citywide index and five
borough indexes. The citywide calculation provides a common weighting basis for
cross-borough comparisons. Borough calculations show within-borough variation
and allow indicator weights to respond to each borough's distribution.

Because EWM weights depend on the input sample, a borough-specific score should
not be treated as numerically interchangeable with a citywide score. The final
NYC regression and citywide maps use the corrected citywide EWM results in
`data/processed/main/NEW_YORK_CITY_ALL_results_CORRECT.csv`.

## Spatial analysis

The EWM scores are joined to census block-group polygons for mapping in QGIS.
The preferred GIS layer is
`gis/layers/final_outputs/ewm/nyc_ewm_accessibility.gpkg`, where the numeric score
is named `EWM_SCORE`. The active QGIS project maps the score with five Equal
Count (Quantile) classes. Population summaries also compare accessibility
percentile groups.

The hot spot workflow is implemented in
`code/spatial_analysis/hotspot_analysis.R`. It:

1. removes polygons without a numeric accessibility score;
2. calculates polygon centroids for the neighbor operation;
3. constructs an eight-nearest-neighbor spatial graph;
4. row-standardizes the spatial weights;
5. reports global Moran's I for the accessibility score; and
6. calculates local Getis-Ord Gi* z-scores.

Gi* results are classified at absolute z-score thresholds of 1.65, 1.96, and
2.58, corresponding to the reported 90%, 95%, and 99% hot spot or cold spot
categories. These categories identify spatial clustering, not causal effects.

## Regression analysis

The regression analysis relates the EWM accessibility outcome to measures of
transit dependence, demographic vulnerability, race and ethnicity, and
population density. The predictors are:

- no-vehicle household rate;
- public-transit commute rate;
- population under 18 rate;
- population age 65 and over rate;
- limited-English household rate;
- tract poverty rate;
- tract disability rate;
- tract uninsured rate;
- Black non-Hispanic population rate;
- Asian non-Hispanic population rate;
- Hispanic population rate; and
- population density per square kilometer.

### Ordinary least squares

OLS estimates average conditional associations between accessibility and the
predictors. The saved tables use four nested specifications: transit dependence,
vulnerability, vulnerability plus race and ethnicity, and the full model with
transit dependence and population density. Citywide and borough models are
reported separately. The saved NYC table labels the dependent variable as the
log EWM score; the borough tables use the EWM score.

### Quantile regression

Quantile regression tests whether associations differ between lower-, middle-,
and higher-accessibility block groups. The R script models the log EWM score at
the 25th, 50th, and 75th percentiles and reports bootstrapped standard errors.
This is useful when an average OLS coefficient hides distributional differences.

### Generalized additive model

The GAM uses smooth functions for all twelve demographic predictors and models
the numeric EWM score directly. Its purpose is to inspect nonlinear patterns
without forcing each relationship to follow a straight line. The fitted smooths
are exported to `figures/models/gam/`.

These models are observational. Their coefficients and smooths describe
associations and do not establish that demographic composition causes transit
accessibility.

