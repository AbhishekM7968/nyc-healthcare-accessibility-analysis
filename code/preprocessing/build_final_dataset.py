"""Build the NYC regression-ready dataset from validated project inputs.

This pipeline starts from the tract-enriched block-group demographics table,
adds land area and population density, then merges the corrected NYC EWM score.
It does not recalculate ACS estimates, routing indicators, or EWM weights.
"""

from argparse import ArgumentParser
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ACS_DIR = PROJECT_ROOT / "data" / "raw" / "acs"
INTERMEDIATE_DIR = PROJECT_ROOT / "data" / "processed" / "intermediate"
MAIN_DATA_DIR = PROJECT_ROOT / "data" / "processed" / "main"

DEMOGRAPHICS_FILE = (
    INTERMEDIATE_DIR
    / "nyc_block_group_demographics_with_tract_vars.csv"
)
AREA_FILE = RAW_ACS_DIR / "NYC_BLOCK_GROUP_AREA.csv"
EWM_FILE = MAIN_DATA_DIR / "NEW_YORK_CITY_ALL_results_CORRECT.csv"
DEFAULT_OUTPUT_FILE = MAIN_DATA_DIR / "final_regression_ready_dataset.csv"

ID_COLUMNS = ["GEOID_TEXT", "GEOID", "TRACT_GEOID"]
REGRESSION_PREDICTORS = [
    "no_vehicle_rate",
    "public_transit_commute_rate",
    "under_18_rate",
    "age_65_plus_rate",
    "limited_english_rate",
    "tract_poverty_rate",
    "tract_disability_rate",
    "tract_uninsured_rate",
    "black_non_hispanic_rate",
    "asian_non_hispanic_rate",
    "hispanic_rate",
    "population_density_per_sq_km",
]
EWM_SCORE = "ewm_accessibility_score"


def require_columns(df: pd.DataFrame, columns: list[str], filename: Path) -> None:
    """Raise a clear error when an input does not match the expected schema."""
    missing = sorted(set(columns).difference(df.columns))
    if missing:
        raise ValueError(f"{filename.name} is missing required columns: {missing}")


def require_unique(df: pd.DataFrame, column: str, filename: Path) -> None:
    """Require one row per identifier before a one-to-one merge."""
    duplicate_count = int(df[column].duplicated().sum())
    if duplicate_count:
        raise ValueError(
            f"{filename.name} has {duplicate_count} duplicate {column} values"
        )


def clean_identifier(series: pd.Series) -> pd.Series:
    """Normalize identifier whitespace without converting IDs to numbers."""
    return series.astype("string").str.strip()


def load_and_clean_demographics() -> tuple[pd.DataFrame, int]:
    """Load demographics and remove rows missing required regression fields."""
    demographics = pd.read_csv(
        DEMOGRAPHICS_FILE,
        dtype={column: "string" for column in ID_COLUMNS},
    )
    required = [*ID_COLUMNS, "borough", "total_population", *REGRESSION_PREDICTORS[:-1]]
    require_columns(demographics, required, DEMOGRAPHICS_FILE)

    for column in ID_COLUMNS:
        demographics[column] = clean_identifier(demographics[column])
    require_unique(demographics, "GEOID_TEXT", DEMOGRAPHICS_FILE)
    require_unique(demographics, "GEOID", DEMOGRAPHICS_FILE)

    numeric_columns = ["total_population", *REGRESSION_PREDICTORS[:-1]]
    demographics[numeric_columns] = demographics[numeric_columns].apply(
        pd.to_numeric, errors="coerce"
    )

    rows_before = len(demographics)
    demographics = demographics.dropna(
        subset=REGRESSION_PREDICTORS[:-1]
    ).copy()
    removed_count = rows_before - len(demographics)
    return demographics, removed_count


def add_population_density(demographics: pd.DataFrame) -> pd.DataFrame:
    """Join Census land area and calculate residents per square kilometre."""
    area = pd.read_csv(AREA_FILE, dtype={"GEOID": "string"})
    require_columns(area, ["GEOID", "ALAND"], AREA_FILE)
    area = area[["GEOID", "ALAND"]].copy()
    area["GEOID"] = clean_identifier(area["GEOID"])
    area["ALAND"] = pd.to_numeric(area["ALAND"], errors="coerce")
    require_unique(area, "GEOID", AREA_FILE)

    result = demographics.merge(area, on="GEOID", how="left", validate="one_to_one")
    invalid_area = result["ALAND"].isna() | result["ALAND"].le(0)
    if invalid_area.any():
        raise ValueError(
            f"Area join produced {int(invalid_area.sum())} missing/nonpositive ALAND values"
        )

    result["land_area_sq_km"] = result["ALAND"] / 1_000_000
    density = result["total_population"] / result["land_area_sq_km"]

    # Match the 10-significant-digit precision of the existing validated file.
    result["population_density_per_sq_km"] = density.map(
        lambda value: float(f"{value:.10g}")
    )
    return result


def merge_ewm(demographics: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Merge one corrected EWM accessibility score onto each block group."""
    ewm = pd.read_csv(EWM_FILE, dtype={"GEOID_TEXT": "string"})
    require_columns(ewm, ["GEOID_TEXT", EWM_SCORE], EWM_FILE)
    ewm = ewm[["GEOID_TEXT", EWM_SCORE]].copy()
    ewm["GEOID_TEXT"] = clean_identifier(ewm["GEOID_TEXT"])
    ewm[EWM_SCORE] = pd.to_numeric(ewm[EWM_SCORE], errors="coerce")

    if ewm[EWM_SCORE].isna().any():
        raise ValueError(
            f"{EWM_FILE.name} contains {int(ewm[EWM_SCORE].isna().sum())} invalid scores"
        )
    require_unique(ewm, "GEOID_TEXT", EWM_FILE)

    unmatched_count = int((~demographics["GEOID_TEXT"].isin(ewm["GEOID_TEXT"])).sum())
    final = demographics.merge(
        ewm,
        on="GEOID_TEXT",
        how="inner",
        validate="one_to_one",
    )
    return final, unmatched_count


def validate_final_dataset(final: pd.DataFrame) -> None:
    """Validate the regression-ready output before writing it."""
    require_unique(final, "GEOID_TEXT", DEFAULT_OUTPUT_FILE)
    required_complete = ["GEOID_TEXT", "borough", EWM_SCORE, *REGRESSION_PREDICTORS]
    require_columns(final, required_complete, DEFAULT_OUTPUT_FILE)

    missing = final[required_complete].isna().sum()
    missing = missing[missing.gt(0)]
    if not missing.empty:
        raise ValueError(f"Final dataset has missing required values: {missing.to_dict()}")
    if final.empty:
        raise ValueError("Final dataset is empty")


def build_final_dataset(output_file: Path) -> pd.DataFrame:
    """Run the complete semi-processed-input-to-final-dataset workflow."""
    for input_file in [DEMOGRAPHICS_FILE, AREA_FILE, EWM_FILE]:
        if not input_file.exists():
            raise FileNotFoundError(f"Required input not found: {input_file}")

    demographics, removed_missing = load_and_clean_demographics()
    demographics = add_population_density(demographics)
    final, unmatched_ewm = merge_ewm(demographics)
    validate_final_dataset(final)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    final.to_csv(output_file, index=False)

    print(f"Demographic rows removed for missing predictors: {removed_missing}")
    print(f"Clean demographic rows without a matching EWM score: {unmatched_ewm}")
    print(f"Final rows: {len(final)}")
    print(f"Final columns: {len(final.columns)}")
    print(f"Saved: {output_file}")
    return final


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_FILE,
        help=f"Output CSV (default: {DEFAULT_OUTPUT_FILE})",
    )
    args = parser.parse_args()
    output_file = args.output if args.output.is_absolute() else PROJECT_ROOT / args.output
    build_final_dataset(output_file)


if __name__ == "__main__":
    main()
