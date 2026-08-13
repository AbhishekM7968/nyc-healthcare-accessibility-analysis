"""Create an r5py travel-time matrix for one New York City borough.

The input is one citywide CSV exported from ``nyc_3_nn_hosptals.gpkg``. The
script selects the configured borough, validates three unique hospital
candidates per block-group origin, converts the QGIS EPSG:3857 coordinate
attributes to EPSG:4326, and routes each candidate OD pair with r5py.
"""

from argparse import ArgumentParser
from datetime import datetime, timedelta
from pathlib import Path

import geopandas as gpd
import pandas as pd
from r5py import TransportNetwork, TravelTimeMatrix
from shapely.geometry import Point


# Select one of: queens, bronx, brooklyn, manhattan, staten_island. This default
# can be overridden with the --borough command-line option.
BOROUGH = "queens"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OSM_FILE = "data/external/local_inputs/osm/nyc.osm.pbf"
GTFS_DIRECTORY = "data/external/local_inputs/gtfs"
INPUT_CSV = "gis/layers/routing_inputs/nyc_3_nearest_hospitals_unique.csv"
INPUT_CRS = "EPSG:3857"
ROUTING_CRS = "EPSG:4326"

# Every borough run uses the complete citywide subway and bus network. MTA bus
# schedules are split across five borough feeds plus the MTA Bus Company feed;
# using all six prevents valid cross-borough and BusCo itineraries from being
# omitted. LIRR remains an explicit Queens-only addition below.
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
        "input": INPUT_CSV,
        "countyfp": "081",
        "output": "generated_outputs/routing/matrices/current/QUEENS_3_OD_TTM_CITYWIDE_TRANSIT.csv",
        "gtfs": CITYWIDE_TRANSIT_GTFS + ("gtfslirr.zip",),
    },
    "bronx": {
        "input": INPUT_CSV,
        "countyfp": "005",
        "output": "generated_outputs/routing/matrices/current/BRONX_3_OD_TTM_CITYWIDE_TRANSIT.csv",
        "gtfs": CITYWIDE_TRANSIT_GTFS,
    },
    "brooklyn": {
        "input": INPUT_CSV,
        "countyfp": "047",
        "output": "generated_outputs/routing/matrices/current/BROOKLYN_3_OD_TTM_CITYWIDE_TRANSIT.csv",
        "gtfs": CITYWIDE_TRANSIT_GTFS,
    },
    "manhattan": {
        "input": INPUT_CSV,
        "countyfp": "061",
        "output": "generated_outputs/routing/matrices/current/MANHATTAN_3_OD_TTM_CITYWIDE_TRANSIT.csv",
        "gtfs": CITYWIDE_TRANSIT_GTFS,
    },
    "staten_island": {
        "input": INPUT_CSV,
        "countyfp": "085",
        "output": "generated_outputs/routing/matrices/current/STATEN_ISLAND_3_OD_TTM_CITYWIDE_TRANSIT.csv",
        "gtfs": CITYWIDE_TRANSIT_GTFS,
    },
}

REQUIRED_COLUMNS = {
    "GEOID",
    "COUNTYFP",
    "fid",
    "feature_x",
    "feature_y",
    "nearest_x",
    "nearest_y",
    "nn_Facility ID",
    "nn_Facility Name",
    "n",
    "distance",
}


def load_candidates(input_path: Path, countyfp: str, limit: int | None) -> pd.DataFrame:
    """Load, select, validate, and reproject one borough's candidate OD rows."""
    df = pd.read_csv(
        input_path,
        dtype={"GEOID": "string", "COUNTYFP": "string"},
    )
    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        raise ValueError(f"{input_path.name} is missing columns: {sorted(missing_columns)}")

    df["COUNTYFP"] = df["COUNTYFP"].str.zfill(3)
    df = df.loc[df["COUNTYFP"] == countyfp].copy()
    if df.empty:
        raise ValueError(f"{input_path.name} contains no rows for COUNTYFP {countyfp}")

    if limit is not None:
        if limit < 1:
            raise ValueError("--limit must be a positive integer")
        df = df.head(limit).copy()

    numeric_columns = [
        "fid",
        "feature_x",
        "feature_y",
        "nearest_x",
        "nearest_y",
        "nn_Facility ID",
        "n",
        "distance",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="raise")

    null_columns = [column for column in REQUIRED_COLUMNS if df[column].isna().any()]
    if null_columns:
        raise ValueError(f"{input_path.name} has nulls in required columns: {sorted(null_columns)}")

    # A full borough input must contain ranks 1-3 and three unique hospitals for
    # every origin. A --limit smoke test may intentionally stop mid-origin.
    if limit is None:
        grouped = df.groupby("GEOID", sort=False)
        row_counts = grouped.size()
        unique_hospitals = grouped["nn_Facility ID"].nunique()
        rank_sets = grouped["n"].agg(lambda values: set(values.astype(int)))
        invalid_origins = row_counts.index[
            (row_counts != 3)
            | (unique_hospitals != 3)
            | (rank_sets != {1, 2, 3})
        ]
        if len(invalid_origins):
            examples = invalid_origins[:10].tolist()
            raise ValueError(
                "Expected ranks 1-3 with three unique hospitals per GEOID; "
                f"invalid origins include: {examples}"
            )

    origin_points = gpd.GeoSeries(
        gpd.points_from_xy(df["feature_x"], df["feature_y"]),
        crs=INPUT_CRS,
    ).to_crs(ROUTING_CRS)
    destination_points = gpd.GeoSeries(
        gpd.points_from_xy(df["nearest_x"], df["nearest_y"]),
        crs=INPUT_CRS,
    ).to_crs(ROUTING_CRS)
    df["origin_lon"] = origin_points.x.to_numpy()
    df["origin_lat"] = origin_points.y.to_numpy()
    df["destination_lon"] = destination_points.x.to_numpy()
    df["destination_lat"] = destination_points.y.to_numpy()
    return df


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

    # Check and load the selected borough's OD-candidate table.
    required_files = [input_path, osm_path, *gtfs_paths]
    missing_files = [str(path) for path in required_files if not path.exists()]
    if missing_files:
        raise FileNotFoundError(f"Missing routing inputs: {missing_files}")

    df = load_candidates(input_path, config["countyfp"], limit)

    # Build the r5py network from the NYC OSM extract and applicable GTFS feeds.
    transport_network = TransportNetwork(osm_path, gtfs_paths)

    # Route each census block-group origin to one candidate hospital destination.
    results = []
    for _, row in df.iterrows():
        origins = gpd.GeoDataFrame(
            {"id": [f"o_{row['GEOID']}"]},
            geometry=[Point(row["origin_lon"], row["origin_lat"])],
            crs=ROUTING_CRS,
        )
        hospital_id = int(row["nn_Facility ID"])
        destinations = gpd.GeoDataFrame(
            {"id": [f"h_{hospital_id}"]},
            geometry=[Point(row["destination_lon"], row["destination_lat"])],
            crs=ROUTING_CRS,
        )
        matrix = TravelTimeMatrix(
            transport_network,
            origins,
            destinations,
            departure=departure,
            departure_time_window=timedelta(minutes=departure_window_minutes),
            transport_modes=["TRANSIT"],
        )
        matrix["GEOID"] = str(row["GEOID"])
        matrix["candidate_fid"] = int(row["fid"])
        matrix["hospital_facility_id"] = hospital_id
        matrix["hospital_facility_name"] = row["nn_Facility Name"]
        matrix["nearest_rank"] = int(row["n"])
        matrix["candidate_distance_3857"] = row["distance"]
        matrix["routing_departure"] = departure.isoformat()
        matrix["departure_window_minutes"] = departure_window_minutes
        results.append(matrix)

    # Save the r5py matrix plus auditable candidate and routing metadata.
    details = pd.concat(results, ignore_index=True)
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
    parser.add_argument("--limit", type=int, help="Process only the first N OD candidates")
    args = parser.parse_args()
    if args.departure_window_minutes < 1:
        parser.error("--departure-window-minutes must be positive")
    main(
        args.departure,
        args.limit,
        args.borough,
        args.departure_window_minutes,
    )
