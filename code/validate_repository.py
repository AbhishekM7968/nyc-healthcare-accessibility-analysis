"""Run lightweight integrity checks on the committed research repository.

The checks use only the Python standard library. They do not recalculate model
results, modify data, or require the large external routing inputs.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

FINAL_DATA = PROJECT_ROOT / "data/processed/main/final_regression_ready_dataset.csv"
EWM_DATA = PROJECT_ROOT / "data/processed/main/NEW_YORK_CITY_ALL_results_CORRECT.csv"
BOROUGH_DIR = PROJECT_ROOT / "data/processed/borough"

EXPECTED_BOROUGHS = {
    "bronx",
    "brooklyn",
    "manhattan",
    "queens",
    "staten island",
}

FINAL_REQUIRED_COLUMNS = {
    "GEOID_TEXT",
    "GEOID",
    "borough",
    "total_population",
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
    "ewm_accessibility_score",
}

EWM_REQUIRED_COLUMNS = {
    "GEOID_TEXT",
    "total_distance",
    "walking_distance",
    "transfers",
    "travel_time_total",
    "walking_time",
    "wait_time_total",
    "ewm_accessibility_score",
}

REQUIRED_PATHS = [
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "requirements.txt",
    PROJECT_ROOT / "environment.yml",
    PROJECT_ROOT / "docs/methodology.md",
    PROJECT_ROOT / "docs/data_sources.md",
    PROJECT_ROOT / "docs/workflow.md",
    PROJECT_ROOT / "gis/project/nyc_healthcare_accessibility.qgz",
    PROJECT_ROOT / "figures/maps/citywide/nyc_ewm_map.png",
    PROJECT_ROOT / "figures/maps/citywide/hotspots_map.png",
    PROJECT_ROOT / "figures/main/nyc_population_percentiles.png",
    PROJECT_ROOT / "results/tables/nyc/nyc_ols_results.html",
    PROJECT_ROOT / "results/tables/nyc/nyc_quantile_results.html",
    PROJECT_ROOT / "data/external/gtfs/gtfs_locations.txt",
    PROJECT_ROOT / "data/external/osm/osm_locations.txt",
]

SHAPEFILE_BASES = [
    PROJECT_ROOT / "data/processed/spatial/correct_nyc_ewm",
    PROJECT_ROOT / "data/processed/spatial/CORRECT_NYC_Hotspots_Shapefile",
    PROJECT_ROOT / "gis/layers/final_outputs/ewm/correct_nyc_ewm",
    PROJECT_ROOT
    / "gis/layers/final_outputs/hotspots/CORRECT_NYC_Hotspots_Shapefile",
    PROJECT_ROOT / "gis/layers/boundaries/nybb",
]


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.passes: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if condition:
            self.passes.append(message)
        else:
            self.errors.append(message)

    def warn(self, condition: bool, message: str) -> None:
        if not condition:
            self.warnings.append(message)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        return list(reader.fieldnames or []), list(reader)


def check_paths(report: Report) -> None:
    missing = [path.relative_to(PROJECT_ROOT) for path in REQUIRED_PATHS if not path.exists()]
    report.require(not missing, f"Required repository files exist ({len(REQUIRED_PATHS)} checked)")
    if missing:
        report.errors.append(f"Missing required paths: {missing}")


def check_main_data(report: Report) -> tuple[set[str], int]:
    if not FINAL_DATA.exists():
        report.errors.append(f"Missing final dataset: {FINAL_DATA.relative_to(PROJECT_ROOT)}")
        return set(), 0

    header, rows = read_csv(FINAL_DATA)
    missing_columns = FINAL_REQUIRED_COLUMNS.difference(header)
    report.require(not missing_columns, "Final dataset contains the required analysis columns")
    if missing_columns:
        report.errors.append(f"Final dataset missing columns: {sorted(missing_columns)}")

    geoids = [row.get("GEOID_TEXT", "").strip() for row in rows]
    report.require(bool(rows), "Final dataset is not empty")
    report.require(len(geoids) == len(set(geoids)), "Final dataset GEOID_TEXT values are unique")

    boroughs = {row.get("borough", "").strip().lower() for row in rows}
    report.require(boroughs == EXPECTED_BOROUGHS, "Final dataset contains all five NYC boroughs")

    required_values = FINAL_REQUIRED_COLUMNS.intersection(header)
    missing_cells = sum(
        not row.get(column, "").strip() for row in rows for column in required_values
    )
    report.require(missing_cells == 0, "Final dataset has no blank required values")

    report.warn(
        len(rows) == 6_347,
        f"Final dataset row count is {len(rows)} rather than the documented 6,347",
    )
    return set(geoids), len(rows)


def check_ewm_data(report: Report) -> None:
    if not EWM_DATA.exists():
        report.errors.append(f"Missing EWM dataset: {EWM_DATA.relative_to(PROJECT_ROOT)}")
        return

    header, rows = read_csv(EWM_DATA)
    missing_columns = EWM_REQUIRED_COLUMNS.difference(header)
    report.require(not missing_columns, "Citywide EWM data contain all six indicators and the score")
    if missing_columns:
        report.errors.append(f"EWM dataset missing columns: {sorted(missing_columns)}")

    geoids = [row.get("GEOID_TEXT", "").strip() for row in rows]
    report.require(len(geoids) == len(set(geoids)), "Citywide EWM GEOID_TEXT values are unique")
    report.warn(
        len(rows) == 6_569,
        f"Citywide EWM row count is {len(rows)} rather than the documented 6,569",
    )


def check_borough_data(report: Report, final_geoids: set[str], final_count: int) -> None:
    total_rows = 0
    combined_geoids: set[str] = set()

    for slug in ["bronx", "brooklyn", "manhattan", "queens", "staten_island"]:
        path = BOROUGH_DIR / f"{slug}_regression_ready.csv"
        if not path.exists():
            report.errors.append(f"Missing borough dataset: {path.relative_to(PROJECT_ROOT)}")
            continue

        header, rows = read_csv(path)
        missing_columns = FINAL_REQUIRED_COLUMNS.difference(header)
        if missing_columns:
            report.errors.append(f"{path.name} missing columns: {sorted(missing_columns)}")

        expected_name = slug.replace("_", " ")
        values = {row.get("borough", "").strip().lower() for row in rows}
        report.require(values == {expected_name}, f"{path.name} contains only {expected_name.title()} rows")

        geoids = [row.get("GEOID_TEXT", "").strip() for row in rows]
        report.require(len(geoids) == len(set(geoids)), f"{path.name} GEOID_TEXT values are unique")
        total_rows += len(rows)
        combined_geoids.update(geoids)

    report.require(total_rows == final_count, "Borough dataset row counts sum to the citywide final dataset")
    report.require(combined_geoids == final_geoids, "Borough datasets contain the same GEOIDs as the final dataset")


def check_spatial_files(report: Report) -> None:
    for base in SHAPEFILE_BASES:
        missing = [
            base.with_suffix(extension).name
            for extension in [".shp", ".shx", ".dbf", ".prj"]
            if not base.with_suffix(extension).exists()
        ]
        report.require(
            not missing,
            f"Shapefile components complete: {base.relative_to(PROJECT_ROOT)}",
        )
        if missing:
            report.errors.append(
                f"{base.relative_to(PROJECT_ROOT)} missing components: {missing}"
            )


def check_notebooks(report: Report) -> None:
    notebooks = sorted((PROJECT_ROOT / "notebooks").rglob("*.ipynb"))
    report.require(len(notebooks) == 6, "Six EWM notebooks are present")

    invalid: list[str] = []
    for path in notebooks:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            invalid.append(str(path.relative_to(PROJECT_ROOT)))
    report.require(not invalid, "All notebooks contain valid JSON")
    if invalid:
        report.errors.append(f"Invalid notebooks: {invalid}")


def check_portability_and_secrets(report: Report) -> None:
    personal_path = re.compile(r"/Users/[^/]+/|[A-Za-z]:\\\\Users\\\\[^\\\\]+\\\\")
    literal_api_key = re.compile(
        r"(?i)(?:api[_-]?key|census_api_key)\s*=\s*['\"][^'\"]+['\"]"
    )
    allowed_suffixes = {".py", ".R", ".r", ".ipynb", ".yml", ".yaml"}

    personal_hits: list[str] = []
    secret_hits: list[str] = []
    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix not in allowed_suffixes:
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        relative = str(path.relative_to(PROJECT_ROOT))
        if personal_path.search(text):
            personal_hits.append(relative)
        if literal_api_key.search(text) and path.name != ".env.example":
            secret_hits.append(relative)

    report.require(not personal_hits, "No personal absolute paths appear in text-based project files")
    report.require(not secret_hits, "No literal API keys appear in text-based project files")
    if personal_hits:
        report.errors.append(f"Files containing personal absolute paths: {personal_hits}")
    if secret_hits:
        report.errors.append(f"Files containing possible literal API keys: {secret_hits}")


def print_report(report: Report) -> int:
    print("Repository validation")
    print("=====================")
    for message in report.passes:
        print(f"[PASS] {message}")
    for message in report.warnings:
        print(f"[WARN] {message}")
    for message in report.errors:
        print(f"[FAIL] {message}")

    print()
    print(
        f"{len(report.passes)} passed, "
        f"{len(report.warnings)} warning(s), "
        f"{len(report.errors)} failure(s)"
    )
    return 1 if report.errors else 0


def main() -> int:
    report = Report()
    check_paths(report)
    final_geoids, final_count = check_main_data(report)
    check_ewm_data(report)
    check_borough_data(report, final_geoids, final_count)
    check_spatial_files(report)
    check_notebooks(report)
    check_portability_and_secrets(report)
    return print_report(report)


if __name__ == "__main__":
    sys.exit(main())
