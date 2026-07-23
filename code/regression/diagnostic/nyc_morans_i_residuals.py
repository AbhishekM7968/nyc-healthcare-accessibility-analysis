import pandas as pd
import statsmodels.api as sm

from libpysal.weights import KNN
from esda.moran import Moran
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = PROJECT_ROOT / "results" / "summary"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Load full NYC regression file
# -----------------------------
file = PROJECT_ROOT / "data/processed/intermediate/NYC_regression_ready_data_67.csv"

df = pd.read_csv(file, dtype={"GEOID_TEXT": str})

print("Rows loaded:", len(df))
print("Columns:")
print(df.columns.tolist())

# -----------------------------
# Set dependent variable
# -----------------------------
y_col = "CORRECT_NYC_ALL_INDEX_SCORES_ewm_accessibility_score"

# -----------------------------
# Predictor variables
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
# Pick coordinate columns
# CHANGE THESE if your file uses different names
# -----------------------------
x_coord = "INTPTLON"
y_coord = "INTPTLAT"

# If your file uses x/y instead, use:
# x_coord = "x"
# y_coord = "y"

# -----------------------------
# Keep needed data
# -----------------------------
needed_cols = [y_col, "borough", x_coord, y_coord] + x_cols

df = df.dropna(subset=needed_cols).copy()

print("Rows used:", len(df))

# -----------------------------
# Create borough controls
# -----------------------------
borough_dummies = pd.get_dummies(
    df["borough"],
    prefix="borough",
    drop_first=True
)

# -----------------------------
# Regression setup
# -----------------------------
Y = pd.to_numeric(df[y_col], errors="coerce")
X = df[x_cols].apply(pd.to_numeric, errors="coerce")

X = pd.concat([X, borough_dummies], axis=1)
X = X.astype(float)
X = sm.add_constant(X)

# -----------------------------
# Run regression
# -----------------------------
model = sm.OLS(Y, X).fit(cov_type="HC3")

df["residuals"] = model.resid

print(model.summary())

# -----------------------------
# Create spatial weights using nearest neighbors
# -----------------------------
coords = list(zip(df[x_coord], df[y_coord]))

# k=8 means each block group is compared to its 8 nearest neighbors
w = KNN.from_array(coords, k=8)
w.transform = "r"

# -----------------------------
# Moran's I on regression residuals
# -----------------------------
moran = Moran(df["residuals"], w, permutations=999)

print("\nMoran's I results for regression residuals")
print("----------------------------------------")
print("Moran's I:", moran.I)
print("Expected I:", moran.EI)
print("p-value:", moran.p_sim)
print("z-score:", moran.z_sim)

# -----------------------------
# Save residuals
# -----------------------------
df[["GEOID_TEXT", "borough", "residuals"]].to_csv(
    RESULTS_DIR / "nyc_regression_residuals_for_morans_i.csv",
    index=False
)

print("\nSaved:", RESULTS_DIR / "nyc_regression_residuals_for_morans_i.csv")
