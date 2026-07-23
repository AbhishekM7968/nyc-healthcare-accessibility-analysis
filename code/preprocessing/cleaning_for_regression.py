import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INTERMEDIATE_DIR = PROJECT_ROOT / "data" / "processed" / "intermediate"

# -----------------------------
# Load the full demographics file
# -----------------------------
input_file = INTERMEDIATE_DIR / "nyc_block_group_demographics_with_tract_vars.csv"
removed_rows_file = INTERMEDIATE_DIR / "nyc_demographics_removed_rows_check.csv"
clean_output_file = INTERMEDIATE_DIR / "nyc_demographics_clean_for_analysis.csv"

df = pd.read_csv(
    input_file,
    dtype={
        "GEOID_TEXT": str,
        "GEOID": str,
        "TRACT_GEOID": str
    }
)

print("Original rows:", len(df))
print("Original columns:", len(df.columns))

# -----------------------------
# Columns we need complete for analysis/regression
# -----------------------------
needed_cols = [
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
]

# -----------------------------
# Check missing values before cleaning
# -----------------------------
print("\nMissing values before cleaning:")
print(df[needed_cols].isna().sum())

# -----------------------------
# Save rows that will be removed
# -----------------------------
removed_rows = df[df[needed_cols].isna().any(axis=1)].copy()

def find_missing_columns(row):
    missing = []

    for col in needed_cols:
        if pd.isna(row[col]):
            missing.append(col)

    return ", ".join(missing)

removed_rows["missing_reason"] = removed_rows.apply(find_missing_columns, axis=1)

removed_rows.to_csv(removed_rows_file, index=False)

# -----------------------------
# Create cleaned data
# -----------------------------
df_clean = df.dropna(subset=needed_cols).copy()

# -----------------------------
# Check missing values after cleaning
# -----------------------------
print("\nMissing values after cleaning:")
print(df_clean[needed_cols].isna().sum())

# -----------------------------
# Save cleaned file
# -----------------------------
df_clean.to_csv(clean_output_file, index=False)

print("\nCleaning complete.")
print("Rows removed:", len(df) - len(df_clean))
print("Rows kept:", len(df_clean))

print("\nSaved files:")
print(clean_output_file)
print(removed_rows_file)
