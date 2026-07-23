"""Generate all final project figures in one run."""

from __future__ import annotations

import os
import runpy
import sys
import traceback
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import matplotlib

matplotlib.use("Agg")

import matplotlib.figure
import matplotlib.pyplot as plt


SCRIPT_DIR = Path(__file__).resolve().parent
CHARTS_DIR = SCRIPT_DIR
REPOSITORY_ROOT = SCRIPT_DIR.parents[2]
OUTPUT_DIR = REPOSITORY_ROOT / "figures" / "main"

FIGURES = (
    (
        "coldspot chart",
        "coldspot_population_by_borough.py",
        "coldspot_population.png",
    ),
    (
        "accessibility percentiles",
        "nyc_population_accessibility_percentiles.py",
        "nyc_population_percentiles.png",
    ),
    (
        "entropy weights",
        "entropy_weights_graph.py",
        "entropy_weights.png",
    ),
    (
        "above-average accessibility",
        "above_average_accessibility_by_borough.py",
        "nyc_accessibility_distribution.png",
    ),
    (
        "borough percent above average",
        "percent_each_borough_above_average_access.py",
        "borough_above_average.png",
    ),
)

PROFESSIONAL_STYLE = {
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.facecolor": "white",
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 12,
    "axes.titlesize": 16,
    "axes.titleweight": "bold",
    "axes.labelsize": 13,
    "axes.labelweight": "bold",
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 11,
    "figure.titlesize": 18,
    "figure.titleweight": "bold",
    "axes.prop_cycle": matplotlib.cycler(color=["#1F4E79", "#4F81BD"]),
}


def apply_final_style(figure: matplotlib.figure.Figure) -> None:
    """Apply shared presentation styling without changing plotted data."""
    figure.set_facecolor("white")

    for axis in figure.axes:
        axis.set_facecolor("white")
        axis.xaxis.label.set_fontweight("bold")
        axis.yaxis.label.set_fontweight("bold")
        axis.title.set_fontweight("bold")

        for label in axis.get_xticklabels() + axis.get_yticklabels():
            label.set_fontfamily("sans-serif")

        legend = axis.get_legend()
        if legend is not None:
            for text in legend.get_texts():
                text.set_fontfamily("sans-serif")

    try:
        figure.tight_layout()
    except (ValueError, RuntimeError):
        pass


@contextmanager
def redirect_figure_output(output_path: Path) -> Iterator[None]:
    """Redirect a chart script's save operation to the final output path."""
    original_figure_savefig = matplotlib.figure.Figure.savefig
    original_pyplot_savefig = plt.savefig
    original_show = plt.show

    def save_figure(
        figure: matplotlib.figure.Figure,
        *_args: object,
        **kwargs: object,
    ) -> None:
        apply_final_style(figure)
        kwargs.update(
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
            transparent=False,
        )
        original_figure_savefig(figure, output_path, **kwargs)

    def save_current_figure(*_args: object, **kwargs: object) -> None:
        save_figure(plt.gcf(), **kwargs)

    matplotlib.figure.Figure.savefig = save_figure
    plt.savefig = save_current_figure
    plt.show = lambda *_args, **_kwargs: None

    try:
        yield
    finally:
        matplotlib.figure.Figure.savefig = original_figure_savefig
        plt.savefig = original_pyplot_savefig
        plt.show = original_show


def run_chart(description: str, script_name: str, output_name: str) -> None:
    """Execute one chart script and save its figure to the final directory."""
    script_path = CHARTS_DIR / script_name
    output_path = OUTPUT_DIR / output_name

    if not script_path.is_file():
        raise FileNotFoundError(f"Chart script not found: {script_path}")

    output_path.unlink(missing_ok=True)
    previous_directory = Path.cwd()

    try:
        os.chdir(CHARTS_DIR)
        with plt.rc_context(PROFESSIONAL_STYLE):
            with redirect_figure_output(output_path):
                runpy.run_path(str(script_path), run_name="__main__")

        if not output_path.is_file():
            raise RuntimeError(
                f"{script_name} completed but did not save {output_name}"
            )

        print(f"Saved: {output_path}")
    finally:
        os.chdir(previous_directory)
        plt.close("all")


def main() -> None:
    """Generate every final chart while allowing individual failures."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    charts_path = str(CHARTS_DIR)
    if charts_path not in sys.path:
        sys.path.insert(0, charts_path)

    successful = 0
    failed = 0

    for description, script_name, output_name in FIGURES:
        print(f"Generating {description}...")
        try:
            run_chart(description, script_name, output_name)
            successful += 1
        except Exception as error:
            failed += 1
            print(f"Failed to generate {description}: {error}")
            traceback.print_exc()
        finally:
            plt.close("all")

    print(f"Figure generation complete: {successful} succeeded, {failed} failed.")


if __name__ == "__main__":
    main()
