library(sf)
library(spdep)
library(dplyr)

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
    project_root, "data", "processed", "spatial", "correct_nyc_ewm.shp"
)
output_path <- file.path(project_root, "generated_outputs", "gis", "nyc_hotspots.shp")

bg <- st_read(input_path)

# ESRI Shapefile truncates long DBF column names. CORRECT__8 is the positionally
# matched numeric/rounded version of the final EWM accessibility score; CORRECT__7
# is the unrounded score. This mapping was verified against correct_nyc_ewm.csv.
accessibility_field <- "CORRECT__8"
if (!accessibility_field %in% names(bg)) {
    stop(paste("Missing expected accessibility field:", accessibility_field))
}
bg[[accessibility_field]] <- as.numeric(bg[[accessibility_field]])
bg <- bg %>% filter(!is.na(.data[[accessibility_field]]))

coords <- st_coordinates(st_centroid(bg))
knn <- knearneigh(coords, k = 8)
nb <- knn2nb(knn)
lw <- nb2listw(nb, style = "W")
print(moran.test(bg[[accessibility_field]], lw))

bg$GiZScore <- as.numeric(localG(bg[[accessibility_field]], lw))
bg$Hotspot <- case_when(
    bg$GiZScore >= 2.58 ~ "99% Hot Spot",
    bg$GiZScore >= 1.96 ~ "95% Hot Spot",
    bg$GiZScore >= 1.65 ~ "90% Hot Spot",
    bg$GiZScore <= -2.58 ~ "99% Cold Spot",
    bg$GiZScore <= -1.96 ~ "95% Cold Spot",
    bg$GiZScore <= -1.65 ~ "90% Cold Spot",
    TRUE ~ "Not Significant"
)
dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
st_write(bg, output_path, delete_layer = TRUE)
