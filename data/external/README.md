# External data and generated routing outputs

Large routing inputs and outputs are intentionally excluded from Git. This folder records what is required, where it comes from, and where it should be placed.

## Manifests

- [`gtfs/gtfs_locations.txt`](gtfs/gtfs_locations.txt) lists the MTA and regional GTFS archives, service periods, expected filenames, official publisher pages, and archived checksums.
- [`osm/osm_locations.txt`](osm/osm_locations.txt) documents the expected OpenStreetMap PBF, a public replacement source, and the archived checksum.
- [`routing_outputs.txt`](routing_outputs.txt) lists the large matrices and detailed-itinerary files produced by the routing scripts.

## Placement

The current routing scripts expect the required GTFS ZIP files and `nyc.osm.pbf` directly under the repository root. They also expect borough-specific OD candidate tables named in the scripts’ `FILES` dictionaries.

These inputs are not downloaded automatically because feed versions affect the results. For close reproduction, use files matching the recorded checksums. For a new analysis, record the download date, service period, and checksum of every replacement.

Do not commit API keys, GTFS archives, OSM extracts, or large routing outputs. The root `.gitignore` excludes their common file patterns.
