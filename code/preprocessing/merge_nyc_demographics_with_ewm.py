import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INTERMEDIATE_DIR = PROJECT_ROOT / "data" / "processed" / "intermediate"
MAIN_DATA_DIR = PROJECT_ROOT / "data" / "processed" / "main"

# -----------------------------
# Load files
# -----------------------------
demo_file = INTERMEDIATE_DIR / "nyc_demographics_clean_with_density.csv"
ewm_file = MAIN_DATA_DIR / "NEW_YORK_CITY_ALL_results_CORRECT.csv"
output_file = INTERMEDIATE_DIR / "nyc_demographics_with_ewm_accessibility.csv"

demo = pd.read_csv(demo_file, dtype={"GEOID_TEXT": str, "GEOID": str, "TRACT_GEOID": str})
ewm = pd.read_csv(ewm_file, dtype={"GEOID_TEXT": str})

print("Demographic rows:", len(demo))
print("EWM rows:", len(ewm))

# -----------------------------
# Keep only needed EWM columns
# -----------------------------
ewm_keep = ewm[[
    "GEOID_TEXT",
    "ewm_accessibility_score"
]].copy()

# -----------------------------
# Merge demographics + NYC accessibility
# -----------------------------
merged = demo.merge(
    ewm_keep,
    on="GEOID_TEXT",
    how="inner"
)

print("Merged rows:", len(merged))

# -----------------------------
# Save combined file
# -----------------------------
merged.to_csv(output_file, index=False)

print("Saved:", output_file)
print(merged.head())
