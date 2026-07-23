# R setup

The regression and spatial-analysis scripts require R and the packages listed below. Package installation is a one-time setup step; the analysis scripts do not reinstall packages when they run.

## Required packages

| Analysis | Packages |
|---|---|
| Quantile regression | `quantreg`, `modelsummary` |
| Generalized additive model | `mgcv`, `gratia`, `ggplot2` |
| Hot spot analysis | `sf`, `spdep`, `dplyr` |

Install the packages from an R session:

```r
install.packages(c(
  "quantreg",
  "modelsummary",
  "mgcv",
  "gratia",
  "ggplot2",
  "sf",
  "spdep",
  "dplyr"
))
```

Verify the R installation:

```bash
R --version
which R
```

Run a script from the repository root, for example:

```bash
Rscript code/regression/GAM_r/gam_regression.R
```

The `sf` package may require system geospatial libraries on Linux. On macOS, installing R from CRAN and using current package binaries is usually the simplest approach.
