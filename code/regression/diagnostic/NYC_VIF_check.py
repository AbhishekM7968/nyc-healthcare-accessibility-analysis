import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = PROJECT_ROOT / "results" / "summary"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Load files
# -----------------------------
demo_file = PROJECT_ROOT / "data/processed/intermediate/nyc_demographics_clean_with_density.csv"
ewm_file = PROJECT_ROOT / "data/processed/main/NEW_YORK_CITY_ALL_results_CORRECT.csv"

demo = pd.read_csv(
    demo_file,
    dtype={
        "GEOID_TEXT": str,
        "GEOID": str,
        "TRACT_GEOID": str
    }
)

ewm = pd.read_csv(
    ewm_file,
    dtype={
        "GEOID_TEXT": str
    }
)

print("Demographics rows:", len(demo))
print("EWM rows:", len(ewm))

# -----------------------------
# Clean GEOIDs
# -----------------------------
demo["GEOID_TEXT"] = demo["GEOID_TEXT"].str.strip()
ewm["GEOID_TEXT"] = ewm["GEOID_TEXT"].str.strip()

# -----------------------------
# Keep EWM score
# -----------------------------
ewm_keep = ewm[
    [
        "GEOID_TEXT",
        "ewm_accessibility_score"
    ]
].copy()

ewm_keep = ewm_keep.drop_duplicates(
    subset="GEOID_TEXT",
    keep="first"
)

# -----------------------------
# Merge all NYC rows
# -----------------------------
merged = demo.merge(
    ewm_keep,
    on="GEOID_TEXT",
    how="inner",
    validate="one_to_one"
)

print("Merged NYC rows:", len(merged))

if "borough" in merged.columns:
    print(
        "Boroughs included:",
        sorted(merged["borough"].dropna().unique())
    )

# -----------------------------
# Full model predictors
# -----------------------------
x_cols = [
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

# -----------------------------
# Convert predictors to numeric
# -----------------------------
for col in x_cols:
    merged[col] = pd.to_numeric(
        merged[col],
        errors="coerce"
    )

# -----------------------------
# Keep complete predictor rows
# -----------------------------
vif_data = merged.dropna(
    subset=x_cols
).copy()

print("Rows used for VIF:", len(vif_data))

# Check for variables with no variation
constant_columns = [
    col
    for col in x_cols
    if vif_data[col].nunique() <= 1
]

if constant_columns:
    print(
        "Removed variables with no variation:",
        constant_columns
    )

x_cols_for_vif = [
    col
    for col in x_cols
    if col not in constant_columns
]

X = vif_data[x_cols_for_vif].copy()

# Add intercept
X_with_const = sm.add_constant(
    X,
    has_constant="add"
)

# -----------------------------
# Calculate VIF
# -----------------------------
vif_rows = []

for i, col in enumerate(X_with_const.columns):
    vif_value = variance_inflation_factor(
        X_with_const.values,
        i
    )

    vif_rows.append({
        "variable": col,
        "vif": vif_value
    })

vif_table = pd.DataFrame(vif_rows)

# Remove intercept from interpretation table
vif_table_no_const = vif_table[
    vif_table["variable"] != "const"
].copy()

# Sort highest VIF first
vif_table_no_const = vif_table_no_const.sort_values(
    "vif",
    ascending=False
).reset_index(drop=True)

# Add basic interpretation
def interpret_vif(vif):
    if vif >= 10:
        return "High multicollinearity"
    elif vif >= 5:
        return "Moderate multicollinearity"
    else:
        return "Acceptable"

vif_table_no_const["interpretation"] = (
    vif_table_no_const["vif"].apply(interpret_vif)
)

print("\nNYC-wide VIF table:")
print(vif_table_no_const.to_string(index=False))

# -----------------------------
# Save output
# -----------------------------
vif_output = RESULTS_DIR / "nyc_wide_vif_table.csv"
vif_table_no_const.to_csv(vif_output, index=False)

print("\nSaved:")
print(vif_output)
