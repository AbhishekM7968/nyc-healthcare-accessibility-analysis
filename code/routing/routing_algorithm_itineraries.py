"""Create detailed r5py itineraries for one New York City borough.

Each configured input is the fastest-valid hospital table produced by
``select_fastest_od_pairs.py`` after the time-matrix stage.
"""

from argparse import ArgumentParser
from datetime import datetime, timedelta
from pathlib import Path

import geopandas as gpd
import pandas as pd
from r5py import DetailedItineraries, TransportNetwork
from shapely.geometry import Point


# Select one of: queens, bronx, brooklyn, manhattan, staten_island.
BOROUGH = "queens"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OSM_FILE = "data/external/local_inputs/osm/nyc.osm.pbf"
GTFS_DIRECTORY = "data/external/local_inputs/gtfs"

CITYWIDE_TRANSIT_GTFS = (
    "nyc_metro.zip",
    "gtfs_bx.zip",
    "gtfs_b.zip",
    "gtfs_m.zip",
    "gtfs_q.zip",
    "gtfs_si.zip",
    "gtfs_busco.zip",
)

FILES = {
    "queens": {
        "input": "generated_outputs/routing/selected_od_pairs/QUEENS_FASTEST_VALID_OD_PAIRS.csv",
        "output": "generated_outputs/routing/itineraries/QUEENS_ITINERARIES_V1.csv",
        "gtfs": CITYWIDE_TRANSIT_GTFS + ("gtfslirr.zip",),
    },
    "bronx": {
        "input": "generated_outputs/routing/selected_od_pairs/BRONX_FASTEST_VALID_OD_PAIRS.csv",
        "output": "generated_outputs/routing/itineraries/BX_ITINERARIES_V1.csv",
        "gtfs": CITYWIDE_TRANSIT_GTFS,
    },
    "brooklyn": {
        "input": "generated_outputs/routing/selected_od_pairs/BROOKLYN_FASTEST_VALID_OD_PAIRS.csv",
        "output": "generated_outputs/routing/itineraries/B_2100_ITINERARIES.csv",
        "gtfs": CITYWIDE_TRANSIT_GTFS,
    },
    "manhattan": {
        "input": "generated_outputs/routing/selected_od_pairs/MANHATTAN_FASTEST_VALID_OD_PAIRS.csv",
        "output": "generated_outputs/routing/itineraries/M_1200_ITINERARIES.csv",
        "gtfs": CITYWIDE_TRANSIT_GTFS,
    },
    "staten_island": {
        "input": "generated_outputs/routing/selected_od_pairs/STATEN_ISLAND_FASTEST_VALID_OD_PAIRS.csv",
        "output": "generated_outputs/routing/itineraries/SI_ITINERARIES.csv",
        "gtfs": CITYWIDE_TRANSIT_GTFS,
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


def main(
    departure: datetime,
    limit: int | None = None,
    borough: str = BOROUGH,
    departure_window_minutes: int = 10,
) -> None:
    if borough not in FILES:
        valid = ", ".join(FILES)
        raise ValueError(f"Unknown borough {borough!r}. Choose one of: {valid}")
    config = FILES[borough]
    input_path = PROJECT_ROOT / config["input"]
    output_path = PROJECT_ROOT / config["output"]
    osm_path = PROJECT_ROOT / OSM_FILE
    gtfs_paths = [PROJECT_ROOT / GTFS_DIRECTORY / filename for filename in config["gtfs"]]

    # Check and load the selected borough's fastest/selected OD-pair table.
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

    # Calculate detailed itinerary segments for every selected OD pair.
    details_list = []
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
        details = DetailedItineraries(
            transport_network,
            origins,
            destinations,
            departure=departure,
            departure_time_window=timedelta(minutes=departure_window_minutes),
            transport_modes=["TRANSIT"],
        )
        details["GEOID"] = str(row["GEOID"])
        details["candidate_fid"] = int(row["fid"])
        details["hospital_facility_id"] = row["hospital_facility_id"]
        details["hospital_facility_name"] = row["hospital_facility_name"]
        details["routing_departure"] = departure.isoformat()
        details["departure_window_minutes"] = departure_window_minutes
        details_list.append(details)

    # Preserve the original r5py detailed-itinerary output structure.
    details = pd.concat(details_list, ignore_index=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    details.to_csv(output_path, index=False)
    print(f"Wrote {len(details)} {borough} rows to {output_path}")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--borough", choices=FILES, default=BOROUGH)
    parser.add_argument(
        "--departure",
        required=True,
        type=datetime.fromisoformat,
        help="GTFS-covered departure in ISO format, for example 2026-07-08T08:00:00",
    )
    parser.add_argument(
        "--departure-window-minutes",
        type=int,
        default=10,
        help="Minutes after departure over which transit connections are sampled",
    )
    parser.add_argument("--limit", type=int, help="Process only the first N selected OD pairs")
    args = parser.parse_args()
    if args.departure_window_minutes < 1:
        parser.error("--departure-window-minutes must be positive")
    main(args.departure, args.limit, args.borough, args.departure_window_minutes)
