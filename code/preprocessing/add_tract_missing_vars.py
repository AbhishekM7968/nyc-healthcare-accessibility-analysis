import os

import requests
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ACS_DIR = PROJECT_ROOT / "data" / "raw" / "acs"
INTERMEDIATE_DIR = PROJECT_ROOT / "data" / "processed" / "intermediate"
TRACT_OUTPUT = RAW_ACS_DIR / "nyc_tract_missing_vars.csv"
BLOCK_GROUP_INPUT = RAW_ACS_DIR / "nyc_block_group_demographics.csv"
MERGED_OUTPUT = INTERMEDIATE_DIR / "nyc_block_group_demographics_with_tract_vars.csv"

API_KEY = os.environ.get("CENSUS_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "CENSUS_API_KEY is not set. Export it in your shell before running this script."
    )
BASE_URL = "https://api.census.gov/data/2024/acs/acs5"

counties = {
    "005": "Bronx",
    "047": "Brooklyn",
    "061": "Manhattan",
    "081": "Queens",
    "085": "Staten Island",
}

TRACT_VARIABLES = [
    "NAME",

    # Poverty
    "B17001_001E",  # poverty universe
    "B17001_002E",  # below poverty population

    # Disability
    "B18101_001E",  # disability universe
    "B18101_004E", "B18101_007E", "B18101_010E",
    "B18101_013E", "B18101_016E", "B18101_019E",
    "B18101_023E", "B18101_026E", "B18101_029E",
    "B18101_032E", "B18101_035E", "B18101_038E",

    # Health insurance
    "B27001_001E",  # insurance universe

    # Male uninsured
    "B27001_005E", "B27001_008E", "B27001_011E",
    "B27001_014E", "B27001_017E", "B27001_020E",
    "B27001_023E", "B27001_026E", "B27001_029E",

    # Female uninsured
    "B27001_033E", "B27001_036E", "B27001_039E",
    "B27001_042E", "B27001_045E", "B27001_048E",
    "B27001_051E", "B27001_054E", "B27001_057E",
]


def clean_numeric(series):
    nums = pd.to_numeric(series, errors="coerce")
    nums = nums.mask(nums < 0)
    return nums


def safe_divide(numerator, denominator):
    return numerator / denominator.replace({0: pd.NA})


all_tract_data = []

for county_code, borough_name in counties.items():
    print(f"Downloading tract data for {borough_name}...")

    params = {
        "get": ",".join(TRACT_VARIABLES),
        "for": "tract:*",
        "in": f"state:36 county:{county_code}",
        "key": API_KEY,
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        print(f"Error downloading {borough_name}")
        print(response.text)
        raise RuntimeError("Census API request failed.")

    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])
    df["borough"] = borough_name
    all_tract_data.append(df)

tracts = pd.concat(all_tract_data, ignore_index=True)

# Create tract GEOID
tracts["state"] = tracts["state"].astype(str).str.zfill(2)
tracts["county"] = tracts["county"].astype(str).str.zfill(3)
tracts["tract"] = tracts["tract"].astype(str).str.zfill(6)

tracts["TRACT_GEOID"] = tracts["state"] + tracts["county"] + tracts["tract"]

# Convert ACS columns to numbers
for col in TRACT_VARIABLES:
    if col != "NAME" and col in tracts.columns:
        tracts[col] = clean_numeric(tracts[col])

# -----------------------------
# Tract poverty
# -----------------------------
tracts["tract_poverty_universe"] = tracts["B17001_001E"]
tracts["tract_below_poverty_population"] = tracts["B17001_002E"]

tracts["tract_poverty_rate"] = safe_divide(
    tracts["tract_below_poverty_population"],
    tracts["tract_poverty_universe"]
)

# -----------------------------
# Tract disability
# -----------------------------
disability_cols = [
    "B18101_004E", "B18101_007E", "B18101_010E",
    "B18101_013E", "B18101_016E", "B18101_019E",
    "B18101_023E", "B18101_026E", "B18101_029E",
    "B18101_032E", "B18101_035E", "B18101_038E",
]

tracts["tract_disability_universe"] = tracts["B18101_001E"]
tracts["tract_disabled_population"] = tracts[disability_cols].sum(axis=1, min_count=1)

tracts["tract_disability_rate"] = safe_divide(
    tracts["tract_disabled_population"],
    tracts["tract_disability_universe"]
)

# -----------------------------
# Tract uninsured
# -----------------------------
uninsured_cols = [
    "B27001_005E", "B27001_008E", "B27001_011E",
    "B27001_014E", "B27001_017E", "B27001_020E",
    "B27001_023E", "B27001_026E", "B27001_029E",
    "B27001_033E", "B27001_036E", "B27001_039E",
    "B27001_042E", "B27001_045E", "B27001_048E",
    "B27001_051E", "B27001_054E", "B27001_057E",
]

tracts["tract_insurance_universe"] = tracts["B27001_001E"]
tracts["tract_uninsured_population"] = tracts[uninsured_cols].sum(axis=1, min_count=1)

tracts["tract_uninsured_rate"] = safe_divide(
    tracts["tract_uninsured_population"],
    tracts["tract_insurance_universe"]
)

# Keep clean tract columns
tract_clean = tracts[
    [
        "TRACT_GEOID",
        "borough",

        "tract_poverty_universe",
        "tract_below_poverty_population",
        "tract_poverty_rate",

        "tract_disability_universe",
        "tract_disabled_population",
        "tract_disability_rate",

        "tract_insurance_universe",
        "tract_uninsured_population",
        "tract_uninsured_rate",
    ]
].copy()

TRACT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
tract_clean.to_csv(TRACT_OUTPUT, index=False)

print("\nTract file created:")
print(TRACT_OUTPUT)

print("\nTract missing values:")
print(
    tract_clean[
        [
            "tract_poverty_rate",
            "tract_disability_rate",
            "tract_uninsured_rate",
        ]
    ].isna().sum()
)

# -----------------------------
# Merge tract variables into your block group demographics CSV
# -----------------------------
bg = pd.read_csv(
    BLOCK_GROUP_INPUT,
    dtype={
        "GEOID_TEXT": str,
        "GEOID": str,
    }
)

bg["TRACT_GEOID"] = bg["GEOID_TEXT"].str[:11]

merged = bg.merge(
    tract_clean.drop(columns=["borough"]),
    on="TRACT_GEOID",
    how="left"
)

MERGED_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
merged.to_csv(MERGED_OUTPUT, index=False)

print("\nMerged block group file created:")
print(MERGED_OUTPUT)

print("\nMerged missing values:")
print(
    merged[
        [
            "tract_poverty_rate",
            "tract_disability_rate",
            "tract_uninsured_rate",
        ]
    ].isna().sum()
)

print("\nFirst rows:")
print(merged.head())

print("\nRows:", len(merged))
