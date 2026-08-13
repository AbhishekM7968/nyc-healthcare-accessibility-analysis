# Local routing inputs

This folder is the expected local location for large, version-sensitive routing
inputs. Its contents are ignored by Git.

```text
local_inputs/
├── gtfs/
│   ├── nyc_metro.zip
│   ├── gtfs_bx.zip
│   ├── gtfs_b.zip
│   ├── gtfs_m.zip
│   ├── gtfs_q.zip
│   ├── gtfs_si.zip
│   ├── gtfs_busco.zip
│   ├── gtfslirr.zip
│   └── extracted/        # optional inspection copies; not used by r5py
└── osm/
    └── nyc.osm.pbf
```

Download sources, service periods, checksums, and replacement cautions are
documented in the sibling [`gtfs/`](../gtfs/) and [`osm/`](../osm/) manifests.
The routing scripts read the ZIP archives directly; extracting them is not
required.
