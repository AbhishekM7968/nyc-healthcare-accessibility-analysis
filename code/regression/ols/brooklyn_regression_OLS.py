import pandas as pd
import statsmodels.api as sm
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = PROJECT_ROOT / "results" / "summary"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Load files
# -----------------------------
demo_file = PROJECT_ROOT / "data/processed/intermediate/nyc_demographics_clean_with_density.csv"
ewm_file = PROJECT_ROOT / "data/processed/borough/brooklyn_regression_ready.csv"

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
# Filter to Brooklyn
# -----------------------------
demo_borough = demo[demo["borough"] == "Brooklyn"].copy()

print("Brooklyn demographic rows:", len(demo_borough))

# -----------------------------
# Keep EWM score
# -----------------------------
ewm_keep = ewm[["GEOID_TEXT", "ewm_accessibility_score"]].copy()

# -----------------------------
# Merge
# -----------------------------
merged = demo_borough.merge(
    ewm_keep,
    on="GEOID_TEXT",
    how="inner"
)

print("Merged rows:", len(merged))

# -----------------------------
# Regression setup
# -----------------------------
y_col = "ewm_accessibility_score"

model_sets = {
    "model_1_transit_dependence": [
        "no_vehicle_rate",
        "public_transit_commute_rate",
    ],

    "model_2_vulnerability": [
        "under_18_rate",
        "age_65_plus_rate",
        "limited_english_rate",
        "tract_poverty_rate",
        "tract_disability_rate",
        "tract_uninsured_rate",
    ],

    "model_3_vulnerability_race": [
        "under_18_rate",
        "age_65_plus_rate",
        "limited_english_rate",
        "tract_poverty_rate",
        "tract_disability_rate",
        "tract_uninsured_rate",
        "black_non_hispanic_rate",
        "asian_non_hispanic_rate",
        "hispanic_rate",
    ],

    "model_4_full_with_density": [
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
    ],
}

# -----------------------------
# Significance stars
# -----------------------------
def significance_stars(p):
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    elif p < 0.1:
        return "."
    else:
        return ""

# -----------------------------
# Run models
# -----------------------------
all_results = []
model_summary_rows = []

for model_name, x_cols in model_sets.items():
    print("\n" + "=" * 70)
    print("Running:", model_name)
    print("=" * 70)

    regression_data = merged.dropna(subset=[y_col] + x_cols).copy()

    print("Rows used:", len(regression_data))

    Y = regression_data[y_col]
    X = regression_data[x_cols]
    X = sm.add_constant(X)

    model = sm.OLS(Y, X).fit()

    print(model.summary())

    # Save model-level summary
    model_summary_rows.append({
        "model": model_name,
        "rows_used": len(regression_data),
        "r_squared": model.rsquared,
        "adjusted_r_squared": model.rsquared_adj,
        "aic": model.aic,
        "bic": model.bic
    })

    # Save coefficient table
    for variable in model.params.index:
        all_results.append({
            "model": model_name,
            "variable": variable,
            "coefficient": model.params[variable],
            "p_value": model.pvalues[variable],
            "significance": significance_stars(model.pvalues[variable])
        })

# -----------------------------
# Save outputs
# -----------------------------
results_table = pd.DataFrame(all_results)
summary_table = pd.DataFrame(model_summary_rows)

results_table.to_csv(RESULTS_DIR / "brooklyn_model_tests_coefficients.csv", index=False)
summary_table.to_csv(RESULTS_DIR / "brooklyn_model_tests_summary.csv", index=False)
merged.to_csv(PROJECT_ROOT / "data/processed/borough/brooklyn_regression_ready.csv", index=False)

print("\nSaved files:")
print(RESULTS_DIR / "brooklyn_model_tests_coefficients.csv")
print(RESULTS_DIR / "brooklyn_model_tests_summary.csv")
print(PROJECT_ROOT / "data/processed/borough/brooklyn_regression_ready.csv")

print("\nModel summary:")
print(summary_table)
