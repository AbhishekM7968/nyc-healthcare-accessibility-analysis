# Routing outputs

## Structure

- `matrices/current/` contains the five current borough candidate matrices.
- `matrices/archive/` contains superseded Queens comparison runs.
- `selected_od_pairs/` contains the compact final selections committed to Git.
- `diagnostics/` contains small connectivity and snapping tests.
- `itineraries/` is reserved for detailed itinerary outputs from the next stage.

The matrix, diagnostic, and itinerary folders are intentionally ignored by Git
because they can be regenerated and may grow substantially when routing
parameters change. Their expected filenames are documented in
[`../../data/external/routing_outputs.txt`](../../data/external/routing_outputs.txt).

The `selected_od_pairs/` subfolder is committed because it contains the compact
one-origin-per-block-group products used for mapping and downstream itinerary
analysis.
