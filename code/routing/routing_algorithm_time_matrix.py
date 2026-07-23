"""Create an r5py travel-time matrix for one New York City borough.

Change only ``BOROUGH`` to select a borough. Each configured input contains
approximately three candidate hospitals per census block-group origin.
"""

from argparse import ArgumentParser
from pathlib import Path

import geopandas as gpd
import pandas as pd
from r5py import TransportNetwork, TravelTimeMatrix
from shapely.geometry import Point


# Select one of: queens, bronx, brooklyn, manhattan, staten_island.
BOROUGH = "queens"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OSM_FILE = "nyc.osm.pbf"

FILES = {
    "queens": {
        "input": "QUEENS_i_hate_ts.csv",
        "output": "generated_outputs/routing/QUEENS_3_OD_TTM.csv",
        "gtfs": ["nyc_metro.zip", "gtfs_m.zip", "gtfs_q.zip", "gtfslirr.zip"],
    },
    "bronx": {
        "input": "BX_POTENTIAL_OD_PAIRS_JOINED.csv",
        "output": "generated_outputs/routing/BX_6300_TTM.csv",
        "gtfs": ["nyc_metro.zip", "gtfs_bx.zip"],
    },
    "brooklyn": {
        "input": "BROOKLYN_6300_OD_PAIRS.csv",
        "output": "generated_outputs/routing/B_6300_TRAVEL_TIME_MATRIX.csv",
        "gtfs": ["nyc_metro.zip", "gtfs_b.zip"],
    },
    "manhattan": {
        "input": "M_joined_back.csv",
        "output": "generated_outputs/routing/M_TIME_TRAVEL_MATRIX.csv",
        "gtfs": ["nyc_metro.zip", "gtfs_m.zip"],
    },
    "staten_island": {
        "input": "staten_island_od_pairs.csv",
        "output": "generated_outputs/routing/redo_travel_times_si.csv",
        "gtfs": ["nyc_metro.zip", "gtfs_si.zip"],
    },
}

REQUIRED_COLUMNS = {
    "GEOID",
    "fid",
    "centroid_x",
    "centroid_y",
    "nearest_x",
    "nearest_y",
}


def main(limit: int | None = None) -> None:
    if BOROUGH not in FILES:
        valid = ", ".join(FILES)
        raise ValueError(f"Unknown BOROUGH {BOROUGH!r}. Choose one of: {valid}")
    config = FILES[BOROUGH]
    input_path = PROJECT_ROOT / config["input"]
    output_path = PROJECT_ROOT / config["output"]
    osm_path = PROJECT_ROOT / OSM_FILE
    gtfs_paths = [PROJECT_ROOT / filename for filename in config["gtfs"]]

    # Check and load the selected borough's OD-candidate table.
    required_files = [input_path, osm_path, *gtfs_paths]
    missing_files = [str(path) for path in required_files if not path.exists()]
    if missing_files:
        raise FileNotFoundError(f"Missing routing inputs: {missing_files}")

    df = pd.read_csv(input_path, nrows=limit)
    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        raise ValueError(f"{input_path.name} is missing columns: {sorted(missing_columns)}")

    # Build the r5py network from the NYC OSM extract and applicable GTFS feeds.
    transport_network = TransportNetwork(osm_path, gtfs_paths)

    # Route each census block-group origin to one candidate hospital destination.
    results = []
    for _, row in df.iterrows():
        origins = gpd.GeoDataFrame(
            {"id": [f"o_{row['GEOID']}"]},
            geometry=[Point(row["centroid_x"], row["centroid_y"])],
            crs="EPSG:4326",
        )
        destinations = gpd.GeoDataFrame(
            {"id": [f"d_{row['fid']}"]},
            geometry=[Point(row["nearest_x"], row["nearest_y"])],
            crs="EPSG:4326",
        )
        results.append(TravelTimeMatrix(transport_network, origins, destinations))

    # Save the same r5py travel-time-matrix columns produced by the original code.
    details = pd.concat(results, ignore_index=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    details.to_csv(output_path, index=False)
    print(f"Wrote {len(details)} {BOROUGH} rows to {output_path}")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--limit", type=int, help="Process only the first N OD candidates")
    args = parser.parse_args()
    main(args.limit)
