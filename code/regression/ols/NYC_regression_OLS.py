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
# Clean GEOID fields
# -----------------------------
demo["GEOID_TEXT"] = demo["GEOID_TEXT"].str.strip()
ewm["GEOID_TEXT"] = ewm["GEOID_TEXT"].str.strip()

# -----------------------------
# Keep all NYC demographic rows
# -----------------------------
demo_nyc = demo.copy()

print("NYC demographic rows:", len(demo_nyc))

# -----------------------------
# Keep EWM score
# -----------------------------
ewm_keep = ewm[
    [
        "GEOID_TEXT",
        "ewm_accessibility_score"
    ]
].copy()

ewm_keep["ewm_accessibility_score"] = pd.to_numeric(
    ewm_keep["ewm_accessibility_score"],
    errors="coerce"
)

# Remove duplicate GEOIDs if any exist
ewm_keep = ewm_keep.drop_duplicates(
    subset="GEOID_TEXT",
    keep="first"
)

# -----------------------------
# Merge all NYC block groups
# -----------------------------
merged = demo_nyc.merge(
    ewm_keep,
    on="GEOID_TEXT",
    how="inner",
    validate="one_to_one"
)

print("Merged NYC rows:", len(merged))
print(
    "Boroughs included:",
    sorted(merged["borough"].dropna().unique())
)

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
# Convert regression columns
# to numeric
# -----------------------------
all_regression_columns = {
    y_col
}

for columns in model_sets.values():
    all_regression_columns.update(columns)

for column in all_regression_columns:
    merged[column] = pd.to_numeric(
        merged[column],
        errors="coerce"
    )

# -----------------------------
# Run NYC-wide models
# -----------------------------
all_results = []
model_summary_rows = []

for model_name, x_cols in model_sets.items():
    print("\n" + "=" * 70)
    print("Running NYC-wide model:", model_name)
    print("=" * 70)

    regression_data = merged.dropna(
        subset=[y_col] + x_cols
    ).copy()

    print("Rows used:", len(regression_data))

    if len(regression_data) == 0:
        print("No complete rows available. Model skipped.")
        continue

    Y = regression_data[y_col]
    X = regression_data[x_cols]

    X = sm.add_constant(
        X,
        has_constant="add"
    )

    model = sm.OLS(
        Y,
        X
    ).fit()

    print(model.summary())

    # Save model-level summary
    model_summary_rows.append({
        "model": model_name,
        "rows_used": len(regression_data),
        "r_squared": model.rsquared,
        "adjusted_r_squared": model.rsquared_adj,
        "aic": model.aic,
        "bic": model.bic,
        "f_statistic": model.fvalue,
        "f_p_value": model.f_pvalue
    })

    # Save coefficient results
    confidence_intervals = model.conf_int()

    for variable in model.params.index:
        all_results.append({
            "model": model_name,
            "variable": variable,
            "coefficient": model.params[variable],
            "standard_error": model.bse[variable],
            "t_value": model.tvalues[variable],
            "p_value": model.pvalues[variable],
            "confidence_interval_low": confidence_intervals.loc[
                variable, 0
            ],
            "confidence_interval_high": confidence_intervals.loc[
                variable, 1
            ],
            "significance": significance_stars(
                model.pvalues[variable]
            )
        })

# -----------------------------
# Save outputs
# -----------------------------
results_table = pd.DataFrame(all_results)
summary_table = pd.DataFrame(model_summary_rows)

results_table.to_csv(
    RESULTS_DIR / "nyc_wide_ols_coefficient_results.csv",
    index=False
)

summary_table.to_csv(
    RESULTS_DIR / "nyc_wide_ols_model_summary.csv",
    index=False
)

merged.to_csv(
    PROJECT_ROOT / "data/processed/intermediate/nyc_wide_merged_regression_data.csv",
    index=False
)

print("\nSaved files:")
print(RESULTS_DIR / "nyc_wide_ols_coefficient_results.csv")
print(RESULTS_DIR / "nyc_wide_ols_model_summary.csv")
print(PROJECT_ROOT / "data/processed/intermediate/nyc_wide_merged_regression_data.csv")

print("\nNYC-wide model summary:")
print(summary_table)
