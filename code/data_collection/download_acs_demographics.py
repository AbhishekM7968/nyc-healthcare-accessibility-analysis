import os

import requests
import pandas as pd
from functools import reduce
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "acs" / "nyc_block_group_demographics.csv"

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

ACS_VARIABLES = [
    # Vehicle access
    "B25044_001E",  # total occupied housing units
    "B25044_003E",  # owner occupied: no vehicle available
    "B25044_009E",  # renter occupied: no vehicle available

   

    # Public transit commute
    "B08301_001E",  # total workers 16 years and over
    "B08301_010E",  # public transportation, excluding taxicab

    # Total population and age
    "B01001_001E",  # total population

    # Under 18
    "B01001_003E", "B01001_004E", "B01001_005E", "B01001_006E",  # male under 18
    "B01001_027E", "B01001_028E", "B01001_029E", "B01001_030E",  # female under 18

    # Age 65+
    "B01001_020E", "B01001_021E", "B01001_022E",
    "B01001_023E", "B01001_024E", "B01001_025E",
    "B01001_044E", "B01001_045E", "B01001_046E",
    "B01001_047E", "B01001_048E", "B01001_049E",

    # Race and ethnicity
    "B03002_001E",  # total population
    "B03002_003E",  # non-Hispanic white alone
    "B03002_004E",  # non-Hispanic Black alone
    "B03002_006E",  # non-Hispanic Asian alone
    "B03002_012E",  # Hispanic or Latino

    # Limited English-speaking households
    "C16002_001E",  # total households
    "C16002_004E",  # Spanish limited English-speaking household
    "C16002_007E",  # other Indo-European limited English-speaking household
    "C16002_010E",  # Asian/Pacific Island limited English-speaking household
    "C16002_013E",  # other languages limited English-speaking household
]


def chunks(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def clean_numeric(series):
    nums = pd.to_numeric(series, errors="coerce")
    nums = nums.mask(nums < 0)
    return nums


def safe_divide(numerator, denominator):
    return numerator / denominator.replace({0: pd.NA})


def fetch_county_data(county_code, borough_name):
    print(f"Downloading {borough_name}...")

    county_frames = []

    for variable_chunk in chunks(ACS_VARIABLES, 35):
        params = {
            "get": ",".join(["NAME"] + variable_chunk),
            "for": "block group:*",
            "in": f"state:36 county:{county_code} tract:*",
            "key": API_KEY,
        }

        response = requests.get(BASE_URL, params=params)

        if response.status_code != 200:
            print(f"Error downloading {borough_name}")
            print(response.text)
            raise RuntimeError("Census API request failed.")

        data = response.json()
        header = data[0]
        rows = data[1:]

        df = pd.DataFrame(rows, columns=header)
        county_frames.append(df)

    join_keys = ["NAME", "state", "county", "tract", "block group"]

    county_df = reduce(
        lambda left, right: pd.merge(left, right, on=join_keys, how="outer"),
        county_frames
    )

    county_df["borough"] = borough_name
    return county_df


all_data = []

for county_code, borough_name in counties.items():
    county_df = fetch_county_data(county_code, borough_name)
    all_data.append(county_df)

combined = pd.concat(all_data, ignore_index=True)

# Create GEOID
combined["state"] = combined["state"].astype(str).str.zfill(2)
combined["county"] = combined["county"].astype(str).str.zfill(3)
combined["tract"] = combined["tract"].astype(str).str.zfill(6)
combined["block group"] = combined["block group"].astype(str).str.zfill(1)

combined["GEOID"] = (
    combined["state"]
    + combined["county"]
    + combined["tract"]
    + combined["block group"]
)

combined["GEOID_TEXT"] = combined["GEOID"].astype(str)

# Convert ACS columns to numbers
for col in ACS_VARIABLES:
    if col in combined.columns:
        combined[col] = clean_numeric(combined[col])

# -----------------------------
# Vehicle access
# -----------------------------
combined["total_households"] = combined["B25044_001E"]

combined["no_vehicle_households"] = (
    combined["B25044_003E"] + combined["B25044_009E"]
)

combined["no_vehicle_rate"] = safe_divide(
    combined["no_vehicle_households"],
    combined["total_households"]
)



# -----------------------------
# Public transit commute
# -----------------------------
combined["total_workers_16_plus"] = combined["B08301_001E"]
combined["public_transit_workers"] = combined["B08301_010E"]

combined["public_transit_commute_rate"] = safe_divide(
    combined["public_transit_workers"],
    combined["total_workers_16_plus"]
)

# -----------------------------
# Total population
# -----------------------------
combined["total_population"] = combined["B01001_001E"]

# -----------------------------
# Under 18
# -----------------------------
under_18_cols = [
    "B01001_003E", "B01001_004E", "B01001_005E", "B01001_006E",
    "B01001_027E", "B01001_028E", "B01001_029E", "B01001_030E",
]

combined["under_18_population"] = combined[under_18_cols].sum(axis=1, min_count=1)

combined["under_18_rate"] = safe_divide(
    combined["under_18_population"],
    combined["total_population"]
)

# -----------------------------
# Age 65+
# -----------------------------
age_65_cols = [
    "B01001_020E", "B01001_021E", "B01001_022E",
    "B01001_023E", "B01001_024E", "B01001_025E",
    "B01001_044E", "B01001_045E", "B01001_046E",
    "B01001_047E", "B01001_048E", "B01001_049E",
]

combined["age_65_plus_population"] = combined[age_65_cols].sum(axis=1, min_count=1)

combined["age_65_plus_rate"] = safe_divide(
    combined["age_65_plus_population"],
    combined["total_population"]
)

# -----------------------------
# Race / ethnicity
# -----------------------------
combined["race_ethnicity_total"] = combined["B03002_001E"]

combined["white_non_hispanic_population"] = combined["B03002_003E"]
combined["black_non_hispanic_population"] = combined["B03002_004E"]
combined["asian_non_hispanic_population"] = combined["B03002_006E"]
combined["hispanic_population"] = combined["B03002_012E"]

combined["white_non_hispanic_rate"] = safe_divide(
    combined["white_non_hispanic_population"],
    combined["race_ethnicity_total"]
)

combined["black_non_hispanic_rate"] = safe_divide(
    combined["black_non_hispanic_population"],
    combined["race_ethnicity_total"]
)

combined["asian_non_hispanic_rate"] = safe_divide(
    combined["asian_non_hispanic_population"],
    combined["race_ethnicity_total"]
)

combined["hispanic_rate"] = safe_divide(
    combined["hispanic_population"],
    combined["race_ethnicity_total"]
)

# -----------------------------
# Limited English-speaking households
# -----------------------------
limited_english_cols = [
    "C16002_004E",
    "C16002_007E",
    "C16002_010E",
    "C16002_013E",
]

combined["language_households_total"] = combined["C16002_001E"]

combined["limited_english_households"] = combined[limited_english_cols].sum(axis=1, min_count=1)

combined["limited_english_rate"] = safe_divide(
    combined["limited_english_households"],
    combined["language_households_total"]
)

# -----------------------------
# Final clean output
# -----------------------------
clean = combined[
    [
        "GEOID_TEXT",
        "GEOID",
        "NAME",
        "borough",

        "total_population",
        "total_households",
        "no_vehicle_households",
        "no_vehicle_rate",

        "total_workers_16_plus",
        "public_transit_workers",
        "public_transit_commute_rate",

        "under_18_population",
        "under_18_rate",

        "age_65_plus_population",
        "age_65_plus_rate",

        "white_non_hispanic_population",
        "white_non_hispanic_rate",
        "black_non_hispanic_population",
        "black_non_hispanic_rate",
        "asian_non_hispanic_population",
        "asian_non_hispanic_rate",
        "hispanic_population",
        "hispanic_rate",

        "limited_english_households",
        "limited_english_rate",
    ]
].copy()

# Remove empty/no-population rows
clean = clean[clean["total_population"] > 0]

clean["GEOID_TEXT"] = clean["GEOID_TEXT"].astype(str)
clean["GEOID"] = clean["GEOID"].astype(str)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
clean.to_csv(OUTPUT_FILE, index=False)

print("Done.")
print("Saved:", OUTPUT_FILE)
print(clean.head())
print("Rows:", len(clean))
print(clean["borough"].value_counts())

print("\nMissing values check:")
print(clean.isna().sum())
