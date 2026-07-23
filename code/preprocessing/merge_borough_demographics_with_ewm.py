import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INTERMEDIATE_DIR = PROJECT_ROOT / "data" / "processed" / "intermediate"
MAIN_DATA_DIR = PROJECT_ROOT / "data" / "processed" / "main"
BOROUGH_DATA_DIR = PROJECT_ROOT / "data" / "processed" / "borough"

# -----------------------------
# Load demographics
# -----------------------------
demo_file = INTERMEDIATE_DIR / "nyc_demographics_clean_with_density.csv"

demo = pd.read_csv(
    demo_file,
    dtype={
        "GEOID_TEXT": str,
        "GEOID": str,
        "TRACT_GEOID": str
    }
)

# -----------------------------
# Borough EWM files
# Change file names if yours are slightly different
# -----------------------------
ewm_file = MAIN_DATA_DIR / "NEW_YORK_CITY_ALL_results_CORRECT.csv"

# -----------------------------
# Merge each borough separately
# -----------------------------
for borough in ["Manhattan", "Bronx", "Queens", "Brooklyn", "Staten Island"]:
    print("\n" + "=" * 60)
    print("Processing:", borough)
    print("=" * 60)

    # Filter demographics to one borough
    demo_borough = demo[demo["borough"] == borough].copy()

    # Load EWM file
    ewm = pd.read_csv(
        ewm_file,
        dtype={"GEOID_TEXT": str}
    )

    # Keep only needed EWM columns
    ewm_keep = ewm[["GEOID_TEXT", "ewm_accessibility_score"]].copy()

    # Merge
    merged = demo_borough.merge(
        ewm_keep,
        on="GEOID_TEXT",
        how="inner"
    )

    print("Demographic rows:", len(demo_borough))
    print("EWM rows:", len(ewm))
    print("Merged rows:", len(merged))

    # Make clean output file name
    output_name = BOROUGH_DATA_DIR / (
        borough.lower().replace(" ", "_") + "_regression_ready.csv"
    )

    # Save
    output_name.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_name, index=False)

    print("Saved:", output_name)
