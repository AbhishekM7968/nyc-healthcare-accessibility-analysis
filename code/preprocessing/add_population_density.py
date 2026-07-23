import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ACS_DIR = PROJECT_ROOT / "data" / "raw" / "acs"
INTERMEDIATE_DIR = PROJECT_ROOT / "data" / "processed" / "intermediate"

# -----------------------------
# Load files
# -----------------------------
demo_file = INTERMEDIATE_DIR / "nyc_demographics_clean_for_analysis.csv"
area_file = RAW_ACS_DIR / "NYC_BLOCK_GROUP_AREA.csv"
output_file = INTERMEDIATE_DIR / "nyc_demographics_clean_with_density.csv"

demo = pd.read_csv(
    demo_file,
    dtype={
        "GEOID_TEXT": str,
        "GEOID": str,
        "TRACT_GEOID": str
    }
)

area = pd.read_csv(
    area_file,
    dtype={
        "GEOID": str
    }
)

print("Demographic rows:", len(demo))
print("Area rows:", len(area))

print("\nArea columns:")
print(area.columns.tolist())

# -----------------------------
# Keep only GEOID and ALAND
# -----------------------------
area_clean = area[["GEOID", "ALAND"]].copy()

area_clean["ALAND"] = pd.to_numeric(area_clean["ALAND"], errors="coerce")

# -----------------------------
# Merge area into demographics
# -----------------------------
merged = demo.merge(
    area_clean,
    on="GEOID",
    how="left"
)

print("\nRows after merge:", len(merged))
print("Missing ALAND:", merged["ALAND"].isna().sum())

# -----------------------------
# Calculate population density
# -----------------------------
merged["land_area_sq_km"] = merged["ALAND"] / 1_000_000

merged["population_density_per_sq_km"] = (
    merged["total_population"] / merged["land_area_sq_km"]
)

# Remove impossible density values from zero land area
merged.loc[merged["ALAND"] <= 0, "population_density_per_sq_km"] = pd.NA

# -----------------------------
# Check result
# -----------------------------
print("\nPopulation density summary:")
print(merged["population_density_per_sq_km"].describe())

print("\nMissing density:")
print(merged["population_density_per_sq_km"].isna().sum())

# -----------------------------
# Save new file
# -----------------------------
merged.to_csv(output_file, index=False)

print("\nSaved:")
print(output_file)
