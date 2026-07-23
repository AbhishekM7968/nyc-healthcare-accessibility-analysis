import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
output_file = PROJECT_ROOT / "figures/main/entropy_weights.png"

# --------------------------------------------------
# NYC entropy weights
# --------------------------------------------------

weights_data = pd.DataFrame({
    "indicator": [
        "Transfers",
        "Walking Time",
        "Walking Distance",
        "Total Travel Time",
        "Total Distance",
        "Wait Time"
    ],
    "weight": [
        0.441671,
        0.152778,
        0.150798,
        0.135570,
        0.066226,
        0.052956
    ]
})

weights_data["weight_percent"] = weights_data["weight"] * 100

# --------------------------------------------------
# Professional styling
# --------------------------------------------------

font_name = "Arial"

main_text_color = "#17324D"
secondary_text_color = "#5E6E7C"

# Professional sequential blue palette
colors = [
    "#173F5F",  # Transfers
    "#35698F",
    "#527FA2",
    "#739FC2",
    "#9DBBD2",
    "#C7DAE9"
]

plt.rcParams.update({
    "font.family": font_name,
    "font.weight": "normal",
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

# --------------------------------------------------
# Donut chart
# --------------------------------------------------

wedges, label_texts, percentage_labels = ax.pie(
    weights_data["weight_percent"],
    colors=colors,
    startangle=90,
    counterclock=False,
    labels=None,
    autopct=lambda value: f"{value:.1f}%",
    pctdistance=0.78,
    wedgeprops={
        "width": 0.44,
        "edgecolor": "white",
        "linewidth": 1.8
    },
    textprops={
        "fontsize": 11,
        "fontfamily": font_name,
        "fontweight": "bold"
    }
)
# Adjust percentage-label colors for readability
for index, label in enumerate(percentage_labels):
    if index <= 2:
        label.set_color("white")
    else:
        label.set_color(main_text_color)

# Center label
ax.text(
    0,
    0.08,
    "EWM",
    ha="center",
    va="center",
    fontsize=25,
    fontfamily=font_name,
    fontweight="bold",
    color=main_text_color
)

ax.text(
    0,
    -0.12,
    "Indicator\nWeights",
    ha="center",
    va="center",
    fontsize=11.5,
    fontfamily=font_name,
    color=secondary_text_color,
    linespacing=1.15
)

# --------------------------------------------------
# Title and subtitle
# --------------------------------------------------

ax.set_title(
    "Entropy Weights of Accessibility Indicators",
    fontsize=19,
    fontfamily=font_name,
    fontweight="bold",
    loc="left",
    pad=24,
    color=main_text_color
)

fig.text(
    0.5,
    0.89,
    "Relative contribution of each indicator to the final accessibility score",
    ha="center",
    va="center",
    fontsize=11.5,
    fontfamily=font_name,
    color=secondary_text_color
)

# --------------------------------------------------
# Legend
# --------------------------------------------------

legend_labels = [
    f"{indicator} — {weight:.1f}%"
    for indicator, weight in zip(
        weights_data["indicator"],
        weights_data["weight_percent"]
    )
]

legend = ax.legend(
    wedges,
    legend_labels,
    title="Accessibility indicator",
    loc="center left",
    bbox_to_anchor=(1.02, 0.5),
    frameon=False,
    fontsize=11,
    title_fontsize=11.5,
    labelspacing=1.15,
    handlelength=1.3,
    handletextpad=0.8
)

legend.get_title().set_fontfamily(font_name)
legend.get_title().set_fontweight("bold")
legend.get_title().set_color(main_text_color)

for text in legend.get_texts():
    text.set_fontfamily(font_name)
    text.set_color(main_text_color)

ax.set_aspect("equal")

# --------------------------------------------------
# Save transparent final graph
# --------------------------------------------------

fig.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight",
    transparent=False
)

plt.show()
