import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from pathlib import Path

# --------------------------------------------------
# Load and clean data
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]
file = PROJECT_ROOT / "data/processed/main/final_regression_ready_dataset.csv"
output_file = PROJECT_ROOT / "figures/main/nyc_population_percentiles.png"

population_col = "total_population"
accessibility_col = "ewm_accessibility_score"

df = pd.read_csv(
    file,
    dtype={"GEOID_TEXT": str}
)

df[population_col] = pd.to_numeric(
    df[population_col],
    errors="coerce"
)

df[accessibility_col] = pd.to_numeric(
    df[accessibility_col],
    errors="coerce"
)

df = df.dropna(
    subset=[
        population_col,
        accessibility_col
    ]
)

# --------------------------------------------------
# Create accessibility percentile groups
# --------------------------------------------------

df["accessibility_percentile"] = (
    df[accessibility_col]
    .rank(pct=True)
    .mul(100)
)

bins = list(range(0, 101, 10))

labels = [
    "0–10",
    "10–20",
    "20–30",
    "30–40",
    "40–50",
    "50–60",
    "60–70",
    "70–80",
    "80–90",
    "90–100"
]

df["accessibility_percentile_bin"] = pd.cut(
    df["accessibility_percentile"],
    bins=bins,
    labels=labels,
    include_lowest=True
)

# --------------------------------------------------
# Calculate population share
# --------------------------------------------------

total_population = df[population_col].sum()

graph_data = (
    df.groupby(
        "accessibility_percentile_bin",
        observed=False
    )[population_col]
    .sum()
    .reindex(labels)
    .reset_index()
)

graph_data["percent_population"] = (
    graph_data[population_col] / total_population
) * 100

# --------------------------------------------------
# Chart styling
# --------------------------------------------------

font_name = "Arial"

plt.rcParams.update({
    "font.family": font_name,
    "font.weight": "normal",
    "axes.titleweight": "bold",
    "axes.labelweight": "normal",
    "axes.labelcolor": "#222222",
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "text.color": "#222222"
})

fig, ax = plt.subplots(
    figsize=(11, 5.8),
    layout="constrained"
)

# Solid white background for consistent presentation and export.
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

x_values = (
    graph_data["accessibility_percentile_bin"]
    .astype(str)
)

y_values = graph_data["percent_population"]

bars = ax.bar(
    x_values,
    y_values,
    width=0.58,
    color="#666666",
    edgecolor="#3F3F3F",
    linewidth=0.5,
    zorder=3
)

# --------------------------------------------------
# Reference line
# --------------------------------------------------

ax.axhline(
    y=10,
    color="#555555",
    linewidth=0.9,
    linestyle=(0, (4, 4)),
    zorder=2
)

ax.text(
    1.0,
    1.015,
    "Expected share: 10%",
    transform=ax.transAxes,
    ha="right",
    va="bottom",
    fontsize=10.5,
    fontfamily=font_name,
    color="#555555"
)

# --------------------------------------------------
# Title and subtitle
# --------------------------------------------------

ax.set_title(
    "NYC Population Across Accessibility Percentiles",
    fontsize=19,
    fontfamily=font_name,
    fontweight="bold",
    loc="left",
    pad=22
)

ax.text(
    0,
    1.01,
    "Population share within each EWM accessibility percentile group",
    transform=ax.transAxes,
    fontsize=11.5,
    fontfamily=font_name,
    color="#666666",
    va="bottom"
)

# --------------------------------------------------
# Axes
# --------------------------------------------------

ax.set_xlabel(
    "Accessibility percentile group",
    fontsize=13,
    fontfamily=font_name,
    fontweight="bold",
    labelpad=12
)

ax.set_ylabel(
    "Share of NYC population (%)",
    fontsize=13,
    fontfamily=font_name,
    fontweight="bold",
    labelpad=12
)

ax.tick_params(
    axis="x",
    labelsize=11.5,
    length=0,
    pad=8
)

ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))

ax.tick_params(
    axis="y",
    labelsize=11.5,
    length=0,
    pad=6
)

for label in ax.get_xticklabels():
    label.set_fontfamily(font_name)
    label.set_fontweight("bold")

for label in ax.get_yticklabels():
    label.set_fontfamily(font_name)
    label.set_fontweight("bold")

# --------------------------------------------------
# Gridlines and borders
# --------------------------------------------------

ax.grid(
    axis="y",
    color="#CCCCCC",
    linewidth=0.6,
    zorder=0
)

ax.grid(
    axis="x",
    visible=False
)

for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)

ax.spines["bottom"].set_color("#8A8A8A")
ax.spines["bottom"].set_linewidth(0.6)

# --------------------------------------------------
# Percentage labels
# --------------------------------------------------

for bar in bars:
    height = bar.get_height()

    if height < 9.95:
        label_y = height - 0.08
        vertical_alignment = "top"
        label_color = "white"
    else:
        label_y = height + 0.12
        vertical_alignment = "bottom"
        label_color = "#222222"

    ax.text(
        bar.get_x() + bar.get_width() / 2,
        label_y,
        f"{height:.1f}%",
        ha="center",
        va=vertical_alignment,
        fontsize=10.8,
        fontfamily=font_name,
        fontweight="bold",
        color=label_color,
        zorder=5
    )

# --------------------------------------------------
# Save transparent version
# --------------------------------------------------

fig.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight",
    facecolor="white",
    transparent=False
)

plt.show()
