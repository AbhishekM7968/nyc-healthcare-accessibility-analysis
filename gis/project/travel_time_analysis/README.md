# Travel-time analysis QGIS project

`travel_time_analysis.qgz` is the QGIS project used to inspect and map the
fastest-valid hospital travel-time results.

The file was copied unchanged from:

```text
/Users/_abhishekm/QGIS/travel_time_analysis.qgz
```

Source and repository copies have the same SHA-256 checksum:

```text
1605735580995a479bbe841f0f0aae97fa5bf7a8006c0ed780db9306a006dd0e
```

## Main analysis table

The mapped travel-time values come from:

```text
generated_outputs/routing/selected_od_pairs/
└── ALL_BLOCK_GROUP_OD_SELECTION_STATUS.csv
```

The table contains one row for each of 6,587 block groups, including 6,580
fastest-valid routes and seven explicitly unresolved origins.

## Referenced GIS layers

The project uses existing repository layers for block groups, borough
boundaries, centroids, hospitals, subway and bus lines, and subway and bus
stops. It also references these legacy QGIS working layers:

```text
gis/layers/generated_outputs/
├── nyc_3_nearest_hospitals.gpkg
└── nyc_3_nn_hosptals.gpkg
```

## Portability note

The QGIS project was intentionally not edited during repository organization.
It therefore retains the relative paths saved when the source project lived in
`/Users/_abhishekm/QGIS/`, plus one local GPS destination path stored by QGIS.
The project file is preserved as an exact research artifact rather than claimed
to be fully portable.

If a collaborator opens the copied project and QGIS reports unavailable
layers, use **Repair Data Source** and point the first missing layer to the
matching file under `gis/layers/`. QGIS can usually resolve the remaining
layers from the same repository tree. Save any repaired portable version under
a new filename; do not overwrite this preserved copy.
