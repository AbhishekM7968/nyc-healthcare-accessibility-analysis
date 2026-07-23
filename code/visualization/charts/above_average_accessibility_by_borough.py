import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from pathlib import Path

# -----------------------------
# Load combined file
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[3]
file = PROJECT_ROOT / "data/processed/main/final_regression_ready_dataset.csv"
output_file = PROJECT_ROOT / "figures/main/nyc_accessibility_distribution.png"

df = pd.read_csv(file, dtype={"GEOID_TEXT": str})

# Make sure columns are numeric
df["ewm_accessibility_score"] = pd.to_numeric(df["ewm_accessibility_score"], errors="coerce")
df["total_population"] = pd.to_numeric(df["total_population"], errors="coerce")

df = df.dropna(subset=["ewm_accessibility_score", "total_population", "borough"])

# -----------------------------
# Find average accessibility score
# -----------------------------
average_accessibility = df["ewm_accessibility_score"].mean()

# -----------------------------
# Keep only above-average accessibility block groups
# -----------------------------
above_average = df[df["ewm_accessibility_score"] > average_accessibility].copy()

# -----------------------------
# Group by borough
# -----------------------------
borough_distribution = (
    above_average.groupby("borough")["total_population"]
    .sum()
    .reset_index()
)

# -----------------------------
# Calculate percent distribution
# -----------------------------
total_above_average_population = borough_distribution["total_population"].sum()

borough_distribution["percent_of_above_average_population"] = (
    borough_distribution["total_population"] / total_above_average_population
) * 100

# Sort from highest to lowest
borough_distribution = borough_distribution.sort_values(
    "percent_of_above_average_population",
    ascending=False
)

print("Average accessibility score:", average_accessibility)
print("Total population in above-average accessibility areas:", total_above_average_population)
print(borough_distribution)
print(sum(borough_distribution["percent_of_above_average_population"]))  # Should be 100%

# -----------------------------
# Create polished graph
# -----------------------------
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "axes.titleweight": "bold",
    "axes.labelweight": "bold",
})

plt.figure(figsize=(10, 6), facecolor="white")

bars = plt.bar(
    borough_distribution["borough"],
    borough_distribution["percent_of_above_average_population"],
    color="#35698F",
    edgecolor="#17324D",
    linewidth=0.7
)

plt.title("Distribution of NYC Residents in Above-Average Accessibility Areas", pad=15)
plt.xlabel("Borough")
plt.ylabel("Share of above-average population (%)")
plt.gca().yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))

plt.xticks(rotation=30, ha="right")
plt.ylim(0, max(borough_distribution["percent_of_above_average_population"]) + 5)

# Add value labels above bars
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.5,
        f"{height:.1f}%",
        ha="center",
        va="bottom",
        fontsize=9
    )

plt.figtext(
    0.5,
    -0.03,
    "This chart shows where NYC residents living in above-average accessibility block groups are located, not each borough's own accessibility rate.",
    ha="center",
    fontsize=9
)

plt.tight_layout()

output_file.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(output_file, dpi=300, bbox_inches="tight", facecolor="white")
plt.show()
