"""Launch the reproducible scripted stages of the research workflow.

This command does not automate the manual QGIS preparation, large r5py routing
runs, fastest-OD selection, itinerary-to-indicator reduction, or EWM notebooks.
Those stages require external inputs or research decisions documented in
docs/workflow.md.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

STAGES: dict[str, list[list[str]]] = {
    "validate": [
        [sys.executable, "code/validate_repository.py"],
    ],
    "build-final-data": [
        [sys.executable, "code/preprocessing/build_final_dataset.py"],
        [sys.executable, "code/validate_repository.py"],
    ],
    "figures": [
        [sys.executable, "code/visualization/charts/run_all_figures.py"],
    ],
    "safe": [
        [sys.executable, "code/preprocessing/build_final_dataset.py"],
        [sys.executable, "code/validate_repository.py"],
        [sys.executable, "code/visualization/charts/run_all_figures.py"],
    ],
}

DESCRIPTIONS = {
    "validate": "Check structure, schemas, identifiers, notebooks, spatial sidecars, and secrets.",
    "build-final-data": "Rebuild the final regression dataset from committed intermediate inputs, then validate it.",
    "figures": "Regenerate the standard charts under figures/main/.",
    "safe": "Build the final dataset, validate the repository, and regenerate standard charts.",
}


def display_command(command: list[str]) -> str:
    shown = ["python" if part == sys.executable else part for part in command]
    return " ".join(shown)


def list_stages() -> None:
    print("Available stages")
    print("================")
    for name, description in DESCRIPTIONS.items():
        print(f"{name:18} {description}")
    print()
    print("Excluded from this launcher: GIS preparation, r5py routing, OD reduction,")
    print("itinerary indicator construction, EWM notebooks, and statistical models.")
    print("See docs/workflow.md for the complete research sequence.")


def run_stage(stage: str, dry_run: bool) -> None:
    print(f"Stage: {stage}")
    for command in STAGES[stage]:
        print(f"  $ {display_command(command)}")
        if not dry_run:
            subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", nargs="?", choices=STAGES)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without running them.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List stages and explain what remains outside the launcher.",
    )
    args = parser.parse_args()

    if args.list:
        list_stages()
        return
    if not args.stage:
        parser.error("choose a stage or use --list")

    run_stage(args.stage, args.dry_run)


if __name__ == "__main__":
    main()
