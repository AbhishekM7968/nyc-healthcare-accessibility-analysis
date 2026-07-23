import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from matplotlib.colors import LinearSegmentedColormap, Normalize
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
output_file = PROJECT_ROOT / "figures/main/coldspot_population.png"

# --------------------------------------------------
# Reconstructed cold-spot data
# --------------------------------------------------

coldspot_data = pd.DataFrame({
    "borough": [
        "Manhattan",
        "Brooklyn",
        "Bronx",
        "Staten Island",
        "Queens"
    ],
    "percent_population_in_coldspots": [
        0.0,
        11.0,
        14.0,
        42.0,
        44.0
    ]
})

# Sort so the largest values appear at the top
coldspot_data = coldspot_data.sort_values(
    "percent_population_in_coldspots",
    ascending=True
)

# --------------------------------------------------
# Chart styling
# --------------------------------------------------

font_name = "Arial"

main_text_color = "#17324D"
secondary_text_color = "#5E6E7C"
grid_color = "#B8C4CE"
border_color = "#17324D"

plt.rcParams.update({
    "font.family": font_name,
    "font.weight": "normal",
    "axes.titleweight": "bold",
    "axes.labelweight": "bold",
    "axes.labelcolor": main_text_color,
    "xtick.color": main_text_color,
    "ytick.color": main_text_color,
    "text.color": main_text_color
})

fig, ax = plt.subplots(
    figsize=(10.5, 6.2),
    layout="constrained"
)

# Solid white background
fig.patch.set_facecolor("white")
fig.patch.set_alpha(1)

ax.set_facecolor("white")
ax.patch.set_alpha(1)

x_values = coldspot_data[
    "percent_population_in_coldspots"
]

y_values = coldspot_data["borough"]

# --------------------------------------------------
# Sequential professional blue palette
# Higher cold-spot exposure = darker blue
# --------------------------------------------------

professional_blues = LinearSegmentedColormap.from_list(
    "professional_blues",
    [
        "#C9DAE8",
        "#91B5CF",
        "#527FA2",
        "#1E4D70"
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
    edgecolor=border_color,
    linewidth=0.55,
    zorder=3
)

# --------------------------------------------------
# Title and subtitle
# --------------------------------------------------

ax.set_title(
    "Population Located in Accessibility Cold Spots",
    fontsize=19,
    fontfamily=font_name,
    fontweight="bold",
    loc="left",
    pad=22,
    color=main_text_color
)

ax.text(
    0,
    1.01,
    "Share of each borough’s population located in identified cold spots",
    transform=ax.transAxes,
    fontsize=11.5,
    fontfamily=font_name,
    color=secondary_text_color,
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
    labelpad=12,
    color=main_text_color
)

ax.set_ylabel("")

ax.set_xlim(0, 50)

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
    label.set_color(main_text_color)

for label in ax.get_yticklabels():
    label.set_fontfamily(font_name)
    label.set_fontweight("bold")
    label.set_color(main_text_color)

# --------------------------------------------------
# Gridlines and borders
# --------------------------------------------------

ax.grid(
    axis="x",
    color=grid_color,
    linewidth=0.6,
    alpha=0.75,
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

label_offset = 0.8

for bar, value in zip(bars, x_values):
    ax.text(
        value + label_offset,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.0f}%",
        ha="left",
        va="center",
        fontsize=11.5,
        fontfamily=font_name,
        fontweight="bold",
        color=main_text_color,
        clip_on=False,
        zorder=5
    )

# --------------------------------------------------
# Method note
# --------------------------------------------------

fig.text(
    0.5,
    -0.015,
    "Higher percentages indicate greater population exposure to accessibility cold spots.",
    ha="center",
    va="top",
    fontsize=10,
    fontfamily=font_name,
    color=secondary_text_color
)

# --------------------------------------------------
# Save transparent graph using the same filename
# --------------------------------------------------

fig.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight",
    transparent=False
)

plt.show()
