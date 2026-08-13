# Generated outputs

This directory separates compact, reproducible products from computationally
expensive local intermediates. Large matrices and detailed itineraries remain
local and are documented under [`../data/external/`](../data/external/).

## Routing

`routing/selected_od_pairs/` contains the final products of the travel-time
matrix selection stage:

- `ALL_BLOCK_GROUP_OD_SELECTION_STATUS.csv` has one row for each of 6,587 NYC
  census block groups. It records the selected hospital, fastest valid travel
  time, routing status, and longitude/latitude coordinates. Seven origins with
  no valid candidate route are retained and clearly flagged.
- `*_FASTEST_VALID_OD_PAIRS.csv` contains one selected routable origin-hospital
  pair for each borough.
- `UNAVAILABLE_OD_CANDIDATES_AUDIT.csv` preserves candidate routes for which
  `r5py` returned no travel time.

All coordinate fields in these selected outputs are EPSG:4326. The original
QGIS candidate attributes were EPSG:3857 and are converted in
[`../code/routing/routing_algorithm_time_matrix.py`](../code/routing/routing_algorithm_time_matrix.py)
and independently reconstructed during fastest-pair selection.

Do not replace missing travel times with zero or remove unresolved origins.
See [`../docs/workflow.md`](../docs/workflow.md) for the complete routing order.
