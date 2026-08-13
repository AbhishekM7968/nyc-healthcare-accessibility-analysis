"""Select the fastest valid hospital candidate from each borough TTM.

The travel-time matrices retain all three candidate hospitals per census block
group. This script selects the minimum non-missing travel time for the detailed
itinerary stage and records every unavailable candidate in a separate audit
file. Missing travel times are never imputed or converted to zero.
"""

from pathlib import Path

import geopandas as gpd
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANDIDATES_FILE = (
    PROJECT_ROOT
    / "gis/layers/routing_inputs/nyc_3_nearest_hospitals_unique.csv"
)
OUTPUT_DIRECTORY = PROJECT_ROOT / "generated_outputs/routing/selected_od_pairs"
AUDIT_OUTPUT = OUTPUT_DIRECTORY / "UNAVAILABLE_OD_CANDIDATES_AUDIT.csv"
MASTER_OUTPUT = OUTPUT_DIRECTORY / "ALL_BLOCK_GROUP_OD_SELECTION_STATUS.csv"

FILES = {
    "queens": {
        "matrix": "generated_outputs/routing/matrices/current/QUEENS_3_OD_TTM_CITYWIDE_TRANSIT.csv",
        "output": "QUEENS_FASTEST_VALID_OD_PAIRS.csv",
    },
    "bronx": {
        "matrix": "generated_outputs/routing/matrices/current/BRONX_3_OD_TTM_CITYWIDE_TRANSIT.csv",
        "output": "BRONX_FASTEST_VALID_OD_PAIRS.csv",
    },
    "brooklyn": {
        "matrix": "generated_outputs/routing/matrices/current/BROOKLYN_3_OD_TTM_CITYWIDE_TRANSIT.csv",
        "output": "BROOKLYN_FASTEST_VALID_OD_PAIRS.csv",
    },
    "manhattan": {
        "matrix": "generated_outputs/routing/matrices/current/MANHATTAN_3_OD_TTM_CITYWIDE_TRANSIT.csv",
        "output": "MANHATTAN_FASTEST_VALID_OD_PAIRS.csv",
    },
    "staten_island": {
        "matrix": "generated_outputs/routing/matrices/current/STATEN_ISLAND_3_OD_TTM_CITYWIDE_TRANSIT.csv",
        "output": "STATEN_ISLAND_FASTEST_VALID_OD_PAIRS.csv",
    },
}

REQUIRED_MATRIX_COLUMNS = {
    "GEOID",
    "candidate_fid",
    "hospital_facility_id",
    "hospital_facility_name",
    "nearest_rank",
    "travel_time",
    "routing_departure",
    "departure_window_minutes",
}
REQUIRED_CANDIDATE_COLUMNS = {
    "GEOID",
    "fid",
    "feature_x",
    "feature_y",
    "nearest_x",
    "nearest_y",
}

UNRESOLVED_NOTES = {
    "360050019041": "South Brother Island; no matched ACS demographic record",
    "360050019042": "North Brother Island; no matched ACS demographic record",
    "360050110001": "Ferry Point Park; no matched ACS demographic record",
    "360050516021": "Hart Island; no matched ACS demographic record",
    "360610001001": "Liberty Island; ferry-dependent and no matched ACS demographic record",
    "360610005001": "Governors Island; ferry-dependent and no matched ACS demographic record",
    "360850181003": (
        "Populated Todt Hill origin; no route after 180-minute, walking, and "
        "automatic-snapping diagnostics"
    ),
}


def load_candidate_coordinates() -> pd.DataFrame:
    """Load candidate coordinates and convert QGIS EPSG:3857 fields to WGS84."""
    candidates = pd.read_csv(
        CANDIDATES_FILE,
        dtype={"GEOID": "string"},
        low_memory=False,
    )
    missing = REQUIRED_CANDIDATE_COLUMNS.difference(candidates.columns)
    if missing:
        raise ValueError(f"{CANDIDATES_FILE.name} is missing columns: {sorted(missing)}")

    numeric_columns = ["fid", "feature_x", "feature_y", "nearest_x", "nearest_y"]
    for column in numeric_columns:
        candidates[column] = pd.to_numeric(candidates[column], errors="raise")

    origins = gpd.GeoSeries(
        gpd.points_from_xy(candidates["feature_x"], candidates["feature_y"]),
        crs="EPSG:3857",
    ).to_crs("EPSG:4326")
    destinations = gpd.GeoSeries(
        gpd.points_from_xy(candidates["nearest_x"], candidates["nearest_y"]),
        crs="EPSG:3857",
    ).to_crs("EPSG:4326")
    candidates["centroid_x"] = origins.x.to_numpy()
    candidates["centroid_y"] = origins.y.to_numpy()
    candidates["destination_x"] = destinations.x.to_numpy()
    candidates["destination_y"] = destinations.y.to_numpy()

    coordinate_columns = [
        "GEOID",
        "fid",
        "centroid_x",
        "centroid_y",
        "destination_x",
        "destination_y",
    ]
    coordinates = candidates[coordinate_columns].copy()
    if coordinates.duplicated(["GEOID", "fid"]).any():
        raise ValueError("Candidate source has duplicate GEOID/fid coordinate keys")
    return coordinates


def process_borough(
    borough: str,
    config: dict[str, str],
    coordinates: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Select fastest valid rows and return unavailable-candidate audit rows."""
    matrix_path = PROJECT_ROOT / config["matrix"]
    matrix = pd.read_csv(matrix_path, dtype={"GEOID": "string"})
    missing = REQUIRED_MATRIX_COLUMNS.difference(matrix.columns)
    if missing:
        raise ValueError(f"{matrix_path.name} is missing columns: {sorted(missing)}")
    if matrix.duplicated(["GEOID", "candidate_fid"]).any():
        raise ValueError(f"{matrix_path.name} has duplicate GEOID/candidate_fid rows")

    matrix["candidate_fid"] = pd.to_numeric(matrix["candidate_fid"], errors="raise")
    matrix["travel_time"] = pd.to_numeric(matrix["travel_time"], errors="coerce")
    matrix["nearest_rank"] = pd.to_numeric(matrix["nearest_rank"], errors="raise")
    row_counts = matrix.groupby("GEOID").size()
    if not (row_counts == 3).all():
        invalid = row_counts[row_counts != 3].index[:10].tolist()
        raise ValueError(f"{matrix_path.name} does not have three rows for: {invalid}")

    matrix["valid_candidate_count"] = matrix.groupby("GEOID")["travel_time"].transform(
        lambda values: int(values.notna().sum())
    )
    matrix["unavailable_candidate_count"] = 3 - matrix["valid_candidate_count"]

    valid = matrix.loc[matrix["travel_time"].notna()].copy()
    selected = (
        valid.sort_values(
            ["GEOID", "travel_time", "nearest_rank", "hospital_facility_id"],
            kind="stable",
        )
        .groupby("GEOID", sort=False, as_index=False)
        .first()
    )
    selected = selected.merge(
        coordinates,
        left_on=["GEOID", "candidate_fid"],
        right_on=["GEOID", "fid"],
        how="left",
        validate="one_to_one",
    )
    coordinate_columns = ["centroid_x", "centroid_y", "destination_x", "destination_y"]
    if selected[coordinate_columns].isna().any().any():
        raise ValueError(f"Coordinate join failed for selected {borough} candidates")

    selected["borough"] = borough
    selected["selection_status"] = selected["valid_candidate_count"].map(
        {3: "fastest_valid_of_3", 2: "fastest_valid_of_2", 1: "only_valid_candidate"}
    )
    selected["coordinate_crs"] = "EPSG:4326"
    selected = selected.rename(
        columns={
            "destination_x": "nearest_x",
            "destination_y": "nearest_y",
            "travel_time": "selected_travel_time_minutes",
        }
    )

    output_columns = [
        "borough",
        "GEOID",
        "fid",
        "centroid_x",
        "centroid_y",
        "nearest_x",
        "nearest_y",
        "hospital_facility_id",
        "hospital_facility_name",
        "nearest_rank",
        "selected_travel_time_minutes",
        "valid_candidate_count",
        "unavailable_candidate_count",
        "selection_status",
        "routing_departure",
        "departure_window_minutes",
        "coordinate_crs",
    ]
    selected = selected[output_columns].sort_values("GEOID").reset_index(drop=True)

    unavailable = matrix.loc[matrix["travel_time"].isna()].copy()
    unavailable["borough"] = borough
    unavailable["origin_selection_possible"] = unavailable["valid_candidate_count"] > 0
    unavailable["review_note"] = unavailable["GEOID"].map(UNRESOLVED_NOTES).fillna(
        "Candidate route unavailable; fastest valid candidate retained"
    )
    audit_columns = [
        "borough",
        "GEOID",
        "candidate_fid",
        "hospital_facility_id",
        "hospital_facility_name",
        "nearest_rank",
        "travel_time",
        "valid_candidate_count",
        "unavailable_candidate_count",
        "origin_selection_possible",
        "routing_departure",
        "departure_window_minutes",
        "review_note",
    ]
    return selected, unavailable[audit_columns]


def main() -> None:
    required_files = [CANDIDATES_FILE, *(PROJECT_ROOT / item["matrix"] for item in FILES.values())]
    missing_files = [str(path) for path in required_files if not path.exists()]
    if missing_files:
        raise FileNotFoundError(f"Missing fastest-selection inputs: {missing_files}")

    coordinates = load_candidate_coordinates()
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    audits = []
    master_rows = []
    for borough, config in FILES.items():
        selected, unavailable = process_borough(borough, config, coordinates)
        output_path = OUTPUT_DIRECTORY / config["output"]
        selected.to_csv(output_path, index=False)
        audits.append(unavailable)
        selected_master = selected.copy()
        selected_master["eligible_for_detailed_itinerary"] = True
        selected_master["unresolved_category"] = pd.NA
        selected_master["review_note"] = pd.NA
        master_rows.append(selected_master)

        unresolved = unavailable.loc[~unavailable["origin_selection_possible"]].copy()
        if not unresolved.empty:
            unresolved = unresolved.drop_duplicates("GEOID").merge(
                coordinates.drop_duplicates("GEOID")[["GEOID", "centroid_x", "centroid_y"]],
                on="GEOID",
                how="left",
                validate="one_to_one",
            )
            unresolved_master = pd.DataFrame(
                {
                    "borough": borough,
                    "GEOID": unresolved["GEOID"],
                    "fid": pd.NA,
                    "centroid_x": unresolved["centroid_x"],
                    "centroid_y": unresolved["centroid_y"],
                    "nearest_x": pd.NA,
                    "nearest_y": pd.NA,
                    "hospital_facility_id": pd.NA,
                    "hospital_facility_name": pd.NA,
                    "nearest_rank": pd.NA,
                    "selected_travel_time_minutes": pd.NA,
                    "valid_candidate_count": 0,
                    "unavailable_candidate_count": 3,
                    "selection_status": "unresolved_no_valid_route",
                    "routing_departure": unresolved["routing_departure"],
                    "departure_window_minutes": unresolved["departure_window_minutes"],
                    "coordinate_crs": "EPSG:4326",
                    "eligible_for_detailed_itinerary": False,
                    "unresolved_category": unresolved["GEOID"].map(
                        lambda geoid: (
                            "populated_network_limitation"
                            if geoid == "360850181003"
                            else "non_demographic_special_geography"
                        )
                    ),
                    "review_note": unresolved["review_note"],
                }
            )
            master_rows.append(unresolved_master)
        print(f"Wrote {len(selected):,} selected {borough} OD pairs to {output_path}")

    audit = pd.concat(audits, ignore_index=True).sort_values(
        ["borough", "GEOID", "nearest_rank"]
    )
    audit.to_csv(AUDIT_OUTPUT, index=False)
    print(f"Wrote {len(audit):,} unavailable candidate rows to {AUDIT_OUTPUT}")

    master = pd.concat(master_rows, ignore_index=True, sort=False).sort_values(
        ["borough", "GEOID"]
    )
    if len(master) != 6_587 or master["GEOID"].nunique() != 6_587:
        raise ValueError(
            "Expected one master status row for each of 6,587 unique block groups; "
            f"found {len(master)} rows and {master['GEOID'].nunique()} unique GEOIDs"
        )
    master.to_csv(MASTER_OUTPUT, index=False)
    print(f"Wrote {len(master):,} block-group status rows to {MASTER_OUTPUT}")


if __name__ == "__main__":
    main()
