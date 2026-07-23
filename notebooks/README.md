# Notebooks

This folder contains the Jupyter notebooks used to calculate and validate Entropy Weight Method accessibility scores.

## EWM notebooks

The `ewm/` folder contains six notebooks: one citywide calculation and one calculation for each borough. They use NumPy and pandas to normalize the six routing indicators, calculate entropy-based weights, and produce composite accessibility scores.

Inputs are stored in:

```text
data/processed/intermediate/ewm_inputs/
```

Generated notebook outputs are stored in:

```text
data/processed/intermediate/ewm_outputs/
```

The notebooks are retained because they show the calculation and validation steps used during development. Final citywide EWM results used elsewhere in the repository are stored in `data/processed/main/`.

## Running the notebooks

Open the repository root in Jupyter, install `numpy`, `pandas`, and a Jupyter environment, then run the relevant notebook from top to bottom. Repository-relative paths are used so the notebooks do not depend on a specific user account or computer.

No routing, regression, or general exploratory notebooks are currently included because no additional notebook was both clearly documented and necessary to the final research workflow.
