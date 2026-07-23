import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from matplotlib.colors import LinearSegmentedColormap, Normalize
from pathlib import Path

# --------------------------------------------------
# Load and clean data
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]
file = PROJECT_ROOT / "data/processed/main/final_regression_ready_dataset.csv"
output_file = PROJECT_ROOT / "figures/main/borough_above_average.png"

score_col = "ewm_accessibility_score"
population_col = "total_population"
borough_col = "borough"

df = pd.read_csv(
    file,
    dtype={"GEOID_TEXT": str}
)

df[score_col] = pd.to_numeric(
    df[score_col],
    errors="coerce"
)

df[population_col] = pd.to_numeric(
    df[population_col],
    errors="coerce"
)

df = df.dropna(
    subset=[
        score_col,
        population_col,
        borough_col
    ]
)

# --------------------------------------------------
# Calculate borough-level results
# --------------------------------------------------

average_accessibility = df[score_col].mean()

df["above_average_access"] = (
    df[score_col] > average_accessibility
)

borough_total_pop = (
    df.groupby(borough_col)[population_col]
    .sum()
    .rename("total_borough_population")
)

borough_above_avg_pop = (
    df.loc[df["above_average_access"]]
    .groupby(borough_col)[population_col]
    .sum()
    .rename("above_average_population")
)

borough_results = pd.concat(
    [
        borough_total_pop,
        borough_above_avg_pop
    ],
    axis=1
).fillna(0)

borough_results[
    "percent_borough_population_above_average"
] = (
    borough_results["above_average_population"]
    / borough_results["total_borough_population"]
) * 100

borough_results = (
    borough_results
    .reset_index()
    .sort_values(
        "percent_borough_population_above_average",
        ascending=True
    )
)

print(
    f"NYC average accessibility score: "
    f"{average_accessibility:.4f}"
)

print(borough_results)

# --------------------------------------------------
# Professional chart styling
# --------------------------------------------------

font_name = "Arial"

plt.rcParams.update({
    "font.family": font_name,
    "font.weight": "normal",
    "axes.titleweight": "bold",
    "axes.labelweight": "bold",
    "axes.labelcolor": "#17324D",
    "xtick.color": "#273746",
    "ytick.color": "#273746",
    "text.color": "#17324D"
})

fig, ax = plt.subplots(
    figsize=(10.5, 6.2),
    layout="constrained"
)

fig.patch.set_facecolor("white")
ax.set_facecolor("white")

x_values = borough_results[
    "percent_borough_population_above_average"
]

y_values = borough_results[borough_col]

# --------------------------------------------------
# Sequential blue color scale
# Higher percentages appear darker
# --------------------------------------------------

professional_blues = LinearSegmentedColormap.from_list(
    "professional_blues",
    [
        "#B9D2E7",
        "#739FC2",
        "#35698F",
        "#123B5D"
    ]
)

normalizer = Normalize(
    vmin=x_values.min(),
    vmax=x_values.max()
)

bar_colors = [
    professional_blues(normalizer(value))
    for value in x_values
]

bars = ax.barh(
    y_values,
    x_values,
    height=0.56,
    color=bar_colors,
    edgecolor="#17324D",
    linewidth=0.55,
    zorder=3
)

# --------------------------------------------------
# Title and subtitle
# --------------------------------------------------

ax.set_title(
    "Population with Above-Average Accessibility by Borough",
    fontsize=19,
    fontfamily=font_name,
    fontweight="bold",
    loc="left",
    pad=22,
    color="#17324D"
)

ax.text(
    0,
    1.01,
    "Share of each borough’s population living in block groups above the NYC-wide mean",
    transform=ax.transAxes,
    fontsize=11.5,
    fontfamily=font_name,
    color="#5E6E7C",
    va="bottom"
)

# --------------------------------------------------
# Axes
# --------------------------------------------------

ax.set_xlabel(
    "Share of borough population",
    fontsize=13,
    fontfamily=font_name,
    fontweight="bold",
    labelpad=12
)

ax.set_ylabel("")

maximum_value = x_values.max()

ax.set_xlim(
    0,
    min(
        100,
        maximum_value + max(8, maximum_value * 0.10)
    )
)

ax.xaxis.set_major_formatter(
    PercentFormatter(
        xmax=100,
        decimals=0
    )
)

ax.tick_params(
    axis="x",
    labelsize=11.5,
    length=0,
    pad=7
)

ax.tick_params(
    axis="y",
    labelsize=12.5,
    length=0,
    pad=8
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
    axis="x",
    color="#B8C4CE",
    linewidth=0.6,
    alpha=0.7,
    zorder=0
)

ax.grid(
    axis="y",
    visible=False
)

for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)

ax.spines["bottom"].set_color("#82909B")
ax.spines["bottom"].set_linewidth(0.6)

# --------------------------------------------------
# Percentage labels
# --------------------------------------------------

label_offset = max(
    1.0,
    maximum_value * 0.015
)

for bar, value in zip(bars, x_values):
    ax.text(
        value + label_offset,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.1f}%",
        ha="left",
        va="center",
        fontsize=11.5,
        fontfamily=font_name,
        fontweight="bold",
        color="#17324D",
        clip_on=False,
        zorder=5
    )

# --------------------------------------------------
# Method note
# --------------------------------------------------

fig.text(
    0.5,
    -0.015,
    "Above average is defined using the NYC-wide mean EWM accessibility score.",
    ha="center",
    va="top",
    fontsize=10.5,
    fontfamily=font_name,
    color="#5E6E7C"
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

