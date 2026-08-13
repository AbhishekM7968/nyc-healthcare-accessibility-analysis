# Data sources

## Transit schedules

The routing workflow uses static General Transit Feed Specification (GTFS)
archives published through MTA developer resources. The configured files cover
NYC subway service, all five borough bus feeds, and the separate MTA Bus Company
feed; the Queens configuration also includes Long Island Rail Road service.

The archives are not committed because they are large and periodically updated.
`data/external/gtfs/gtfs_locations.txt` records the expected filenames, service
periods, official publisher pages, and SHA-256 checksums for the archived
project copies. Exact reproduction requires the feed versions matching those
checksums. A current download may produce different routes or travel times.

Users are responsible for reviewing the applicable transit-agency terms before
redistributing a feed. This repository records source locations and checksums
but does not relicense agency data.

The configured routing feeds are:

- `nyc_metro.zip`: MTA New York City Transit subway;
- `gtfs_m.zip`: Manhattan bus;
- `gtfs_b.zip`: Brooklyn bus;
- `gtfs_bx.zip`: Bronx bus;
- `gtfs_q.zip`: Queens bus;
- `gtfs_si.zip`: Staten Island bus; and
- `gtfs_busco.zip`: MTA Bus Company routes omitted from the borough NYCT feeds;
- `gtfslirr.zip`: Long Island Rail Road, used in the Queens configuration.

Nassau and Suffolk feeds are listed in the external manifest but are not used by
the current five-borough routing configuration.

## OpenStreetMap

R5 uses `nyc.osm.pbf` for the pedestrian and street network. The file is not
stored in Git. `data/external/osm/osm_locations.txt` documents the expected
repository location, the checksum of the archived project copy, and the
Geofabrik New York download as a reproducible replacement source.

OpenStreetMap data are available under the Open Database License. Maps and
derived products using OSM should retain appropriate OpenStreetMap attribution.

The original URL and clipping procedure for the NYC-specific archived extract
were not recorded. A newly downloaded statewide or NYC extract should therefore
be treated as a replacement rather than a byte-identical copy.

## Hospital facilities

Hospital points originate from the New York State Department of Health dataset
**Health Facility General Information**. The retained fields include facility
identifier, facility name and description, address, county, operator,
ownership, and facility coordinates.

The final citywide file is `data/raw/hospitals/nyc_hospitals.gpkg`, with a GIS
copy under `gis/layers/hospitals/`. It contains 66 records whose facility
description is Hospital. The borough subsets contain:

| Borough | Hospital points |
|---|---:|
| Bronx | 11 |
| Brooklyn | 16 |
| Manhattan | 24 |
| Queens | 11 |
| Staten Island | 4 |
| **NYC** | **66** |

For routing, co-located records sharing the same facility identifier were
reduced to 61 unique facilities in
`gis/layers/hospitals/nyc_hospitals_unique_facilities.gpkg`. This avoids sending
the same physical facility to the network multiple times while preserving the
66-record source layer for provenance.

The repository does not contain a Python or R script for hospital preparation.
Filtering and point-layer preparation were completed in GIS. The exact download
date, filter expression, treatment of co-located facilities, and duplicate-
review procedure were not recorded and remain a provenance limitation.

## American Community Survey

Demographic measures come from the U.S. Census Bureau 2024 American Community
Survey five-year estimates, downloaded through the Census API by scripts in
`code/data_collection/` and `code/preprocessing/`.

The Census API terms request attribution and prohibit implying Census Bureau
endorsement. The project uses Census data for research and does not claim such
endorsement.

### Block-group variables

| Measure | Construction |
|---|---|
| No Vehicle Rate | Households with no vehicle divided by occupied households |
| Public Transit Commute Rate | Workers commuting by public transportation, excluding taxicab, divided by workers age 16+ |
| Under 18 Rate | Population under 18 divided by total population |
| Over 65 Rate | Population age 65+ divided by total population |
| Limited English Rate | Limited-English-speaking households divided by language-reporting households |
| Black Non-Hispanic Rate | Black-alone, non-Hispanic population divided by race/ethnicity total |
| Asian Non-Hispanic Rate | Asian-alone, non-Hispanic population divided by race/ethnicity total |
| Hispanic Rate | Hispanic or Latino population divided by race/ethnicity total |
| Population Density | Total population divided by block-group land area in square kilometers |

The ACS table groups used include B25044, B08301, B01001, B03002, and C16002.
Block groups with no population are removed from the demographic download
output. Census `ALAND` is used to calculate population density.

### Tract variables

Some measures are only incorporated at tract level and joined to block groups
using the first 11 digits of the block-group GEOID:

| Measure | ACS table |
|---|---|
| Poverty Rate | B17001 |
| Disability Rate | B18101 |
| Uninsured Rate | B27001 |

Rows missing required regression predictors are excluded during dataset
construction. The final regression-ready dataset contains 6,347 block groups.

## Census and administrative geography

- `gis/layers/block_groups/nyc_block_groups.gpkg` contains the census
  block-group geometry used as the analysis geography.
- `gis/layers/boundaries/nybb.shp` contains the five borough boundaries.
- `gis/layers/centroids/` contains the five borough origin-point layers.

The block-group geometry is identified as U.S. Census geography in the project,
but the original TIGER/Line download URL and vintage are not preserved in the
repository. The original source and release date for `nybb` are also not
recorded. These should be added to a future data deposit.

## Derived transit and spatial layers

- `gis/layers/transit/lines/nyc_metro_lines.gpkg` and
  `gis/layers/transit/lines/nyc_bus_lines.gpkg` provide subway and bus context.
- `gis/layers/transit/stops/nyc_stops.gpkg` contains GTFS-derived subway stops,
  while `gis/layers/transit/stops/nyc_bus_stops.gpkg` contains bus stops.
- `gis/layers/final_outputs/ewm/` contains the mapped EWM accessibility result.
- `gis/layers/final_outputs/hotspots/` contains the final Gi* hot spot and cold
  spot layer.

These map layers do not replace the GTFS and OSM inputs used by R5. An available
LIRR stop layer was excluded because its coordinates were implausibly close to
zero.

## Primary analysis datasets

- `data/processed/main/NEW_YORK_CITY_ALL_results_CORRECT.csv`: corrected
  citywide EWM scores and routing indicators for 6,569 origins.
- `data/processed/main/final_regression_ready_dataset.csv`: demographic and EWM
  variables for 6,347 complete block groups.
- `data/processed/borough/`: borough regression-ready datasets.
- `data/processed/spatial/`: shapefile and tabular outputs used for mapping and
  hot spot analysis.

Large GTFS, OSM, detailed itinerary, and travel-time-matrix files are described
under `data/external/` rather than committed to the repository.
