# Routing inputs

`nyc_3_nearest_hospitals_unique.csv` is the portable origin-destination
candidate table used by the travel-time matrix script. It contains three unique
hospital candidates for each of 6,587 census block-group origins.

The coordinate attributes in this QGIS export are EPSG:3857. The routing and
selection scripts convert them to EPSG:4326 before creating r5py points or
publishing selected OD tables.

`source_layers/` contains the larger QGIS GeoPackages from which the CSV was
exported. They are retained locally for provenance but ignored by Git because
the CSV is the reproducible code input.
