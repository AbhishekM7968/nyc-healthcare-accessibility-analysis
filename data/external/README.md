# External data and generated routing outputs

Large routing inputs and outputs are intentionally excluded from Git. This folder records what is required, where it comes from, and where it should be placed.

## Manifests

- [`gtfs/gtfs_locations.txt`](gtfs/gtfs_locations.txt) lists the MTA and regional GTFS archives, service periods, expected filenames, official publisher pages, and archived checksums.
- [`osm/osm_locations.txt`](osm/osm_locations.txt) documents the expected OpenStreetMap PBF, a public replacement source, and the archived checksum.
- [`routing_outputs.txt`](routing_outputs.txt) lists the large matrices and detailed-itinerary files produced by the routing scripts.

## Required routing downloads

For the current five-borough travel-time analysis, download:

- MTA subway static GTFS (`nyc_metro.zip`);
- all five borough bus feeds (`gtfs_bx.zip`, `gtfs_b.zip`, `gtfs_m.zip`,
  `gtfs_q.zip`, and `gtfs_si.zip`);
- the separate MTA Bus Company feed (`gtfs_busco.zip`);
- LIRR static GTFS (`gtfslirr.zip`) for the Queens configuration; and
- an OpenStreetMap PBF named `nyc.osm.pbf`.

Use the official MTA static GTFS download page linked in
[`gtfs/gtfs_locations.txt`](gtfs/gtfs_locations.txt). The MTA Bus Company feed
is separate from the borough feeds and should not be omitted: it covers B100,
B103, Bx23, express-bus services, and various Queens routes. NICE and Suffolk
County feeds are not part of the current five-borough configuration.

## Placement

The current routing scripts expect the required GTFS ZIP files and
the GTFS files under `data/external/local_inputs/gtfs/` and `nyc.osm.pbf` under
`data/external/local_inputs/osm/`. The three-nearest-hospital
candidate table is committed at
`gis/layers/routing_inputs/nyc_3_nearest_hospitals_unique.csv`.

These inputs are not downloaded automatically because feed versions affect the results. For close reproduction, use files matching the recorded checksums. For a new analysis, record the download date, service period, and checksum of every replacement.

Do not commit API keys, GTFS archives, OSM extracts, or large routing outputs. The root `.gitignore` excludes their common file patterns.

## Coordinate reference system

The QGIS candidate export stores origin and destination coordinate attributes
in EPSG:3857 (Web Mercator), which explains values in the millions. The routing
script explicitly reprojects both point sets to EPSG:4326 before sending them
to `r5py`. Selected OD outputs therefore contain longitude/latitude fields and
include `coordinate_crs = EPSG:4326`.
