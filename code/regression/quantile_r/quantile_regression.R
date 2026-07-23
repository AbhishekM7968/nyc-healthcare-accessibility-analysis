library(quantreg)
library(modelsummary)

args <- commandArgs(trailingOnly = FALSE)
script_arg <- sub("^--file=", "", args[grep("^--file=", args)])
script_dir <- if (length(script_arg) > 0) dirname(normalizePath(script_arg[1])) else getwd()

find_project_root <- function(start_dir) {
    candidate <- normalizePath(start_dir, mustWork = TRUE)
    repeat {
        if (dir.exists(file.path(candidate, "code")) &&
            dir.exists(file.path(candidate, "data"))) {
            return(candidate)
        }
        parent <- dirname(candidate)
        if (identical(parent, candidate)) stop("Could not locate repository root")
        candidate <- parent
    }
}

project_root <- find_project_root(script_dir)
input_path <- file.path(
    project_root,
    "data", "processed", "intermediate", "NYC_regression_ready_data_67.csv"
)
if (!file.exists(input_path)) {
    stop(paste("Required quantile-regression input not found:", input_path))
}
df <- read.csv(input_path)
df$ln_ewm <- log(df$CORRECT_NYC_ALL_INDEX_SCORES_ewm_accessibility_score_num)

model_formula <- ln_ewm ~ no_vehicle_rate + public_transit_commute_rate + under_18_rate +
    age_65_plus_rate + limited_english_rate + tract_poverty_rate + tract_disability_rate +
    tract_uninsured_rate + black_non_hispanic_rate + asian_non_hispanic_rate +
    hispanic_rate + population_density_per_sq_km
q25 <- rq(model_formula, data = df, tau = 0.25)
q50 <- rq(model_formula, data = df, tau = 0.50)
q75 <- rq(model_formula, data = df, tau = 0.75)

print(summary(q25, se = "boot"))
print(summary(q50, se = "boot"))
print(summary(q75, se = "boot"))

output_dir <- file.path(project_root, "results", "tables")
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
modelsummary(
    list("25th Percentile" = q25, "Median" = q50, "75th Percentile" = q75),
    title = "Table 2: Quantile Regression Results: New York City - ln EWM score",
    coef_map = c(
        "no_vehicle_rate" = "No Vehicle Rate (%)",
        "public_transit_commute_rate" = "Public Transit Commute Rate (%)",
        "under_18_rate" = "Population Under 18 (%)", "age_65_plus_rate" = "Population Aged 65+ (%)",
        "limited_english_rate" = "Limited English Proficiency (%)",
        "tract_poverty_rate" = "Tract Poverty Rate (%)",
        "tract_disability_rate" = "Tract Disability Rate (%)",
        "tract_uninsured_rate" = "Tract Uninsured Rate (%)",
        "black_non_hispanic_rate" = "Black Non-Hispanic Rate (%)",
        "asian_non_hispanic_rate" = "Asian Non-Hispanic Rate (%)",
        "hispanic_rate" = "Hispanic Rate (%)", "population_density_per_sq_km" = "Population Density"
    ),
    stars = c("*" = .10, "**" = .05, "***" = .01),
    estimate = "{estimate}{stars}", statistic = "({std.error})",
    gof_omit = "AIC|BIC|Log|RMSE|IC",
    output = file.path(output_dir, "nyc_quantile_results.html")
)
