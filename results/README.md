# Results

This folder contains the final statistical output tables and a concise summary of the main model findings.

## Structure

- `tables/citywide/` contains the final NYC OLS and quantile-regression HTML tables.
- `tables/boroughs/` contains the final OLS table for each borough.
- `summary/key_findings.txt` records the main observed patterns across the models.

The citywide and borough OLS models evaluate average relationships between demographic conditions and the accessibility index. Quantile regression examines whether those relationships differ across the accessibility distribution. The GAM analysis checks nonlinear relationships; its final visual output is stored in [`../figures/models/gam/`](../figures/models/gam/).

Model scripts are in [`../code/regression/`](../code/regression/), and the regression-ready inputs are in [`../data/processed/`](../data/processed/). These tables support the written interpretation and figures, but they should be read with the model specifications and limitations documented in [`../docs/methodology.md`](../docs/methodology.md).

Only final corrected outputs are included here. Prototype and duplicate tables are intentionally excluded.
