library(mgcv)
library(gratia)
library(ggplot2)

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
output_dir <- file.path(project_root, "figures", "models", "gam")
output_path <- file.path(output_dir, "gam_graphs_correct.png")

if (!file.exists(input_path)) {
    stop(paste("Required GAM input not found:", input_path))
}

df <- read.csv(input_path)

gam_model <- gam(
    CORRECT_NYC_ALL_INDEX_SCORES_ewm_accessibility_score_num ~
        s(public_transit_commute_rate) + s(no_vehicle_rate) + s(under_18_rate) +
        s(age_65_plus_rate) + s(limited_english_rate) + s(tract_poverty_rate) +
        s(tract_disability_rate) + s(tract_uninsured_rate) + s(black_non_hispanic_rate) +
        s(asian_non_hispanic_rate) + s(hispanic_rate) + s(population_density_per_sq_km),
    data = df
)

print(summary(gam_model))
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

# plot.gam() uses base graphics, so export through a PNG graphics device.
# A 4-by-3 layout accommodates all twelve smooth terms on one presentation page.
png(
    filename = output_path,
    width = 16,
    height = 12,
    units = "in",
    res = 300,
    bg = "white"
)
par(mfrow = c(4, 3), mar = c(4, 4, 2.5, 1), oma = c(0, 0, 3, 0))
plot(gam_model, pages = 1, shade = TRUE, shade.col = "lightblue")
mtext(
    "Figure 4: Generalized Additive Model Regression: New York City",
    side = 3,
    outer = TRUE,
    line = 1,
    font = 2,
    cex = 1.3
)
dev.off()

message("Saved GAM smooth plots to: ", normalizePath(output_path, mustWork = TRUE))
