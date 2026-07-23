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
ewm_file = PROJECT_ROOT / "data/processed/borough/queens_regression_ready.csv"

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

# -----------------------------
# Filter to Queens
# -----------------------------
demo_borough = demo[demo["borough"] == "Queens"].copy()

# -----------------------------
# Merge with EWM
# -----------------------------
ewm_keep = ewm[["GEOID_TEXT", "ewm_accessibility_score"]].copy()

merged = demo_borough.merge(
    ewm_keep,
    on="GEOID_TEXT",
    how="inner"
)

print("Merged rows:", len(merged))

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
# Drop rows with missing predictor values
# -----------------------------
vif_data = merged.dropna(subset=x_cols).copy()

X = vif_data[x_cols]

# Add constant for VIF calculation
X_with_const = sm.add_constant(X)

# -----------------------------
# Calculate VIF
# -----------------------------
vif_rows = []

for i, col in enumerate(X_with_const.columns):
    vif = variance_inflation_factor(X_with_const.values, i)

    vif_rows.append({
        "variable": col,
        "vif": vif
    })

vif_table = pd.DataFrame(vif_rows)

# Remove const from final interpretation table
vif_table_no_const = vif_table[vif_table["variable"] != "const"].copy()

# Sort highest VIF first
vif_table_no_const = vif_table_no_const.sort_values("vif", ascending=False)

print("\nVIF table:")
print(vif_table_no_const)

vif_output = RESULTS_DIR / "queens_vif_table.csv"
vif_table_no_const.to_csv(vif_output, index=False)

print("\nSaved:")
print(vif_output)
