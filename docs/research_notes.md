# Research notes

This file records decisions that affect interpretation or reproducibility. It
is not a substitute for the final paper's limitations section.

## Why use the Entropy Weight Method?

The accessibility outcome combines six measures with different units. EWM
provides a reproducible way to derive weights from the observed information in
each indicator rather than assigning equal weights or relying on researcher
judgment.

The tradeoff is that variation determines weight. A variable can receive a high
weight because it differs strongly across observations, not because travelers
consider it especially burdensome. EWM weights should therefore be interpreted
as statistical weights, not behavioral preference estimates.

## Why use census block groups?

Block groups offer more local spatial detail than census tracts and are small
enough to show within-borough differences in transit access. They also provide a
stable GEOID for joining geometry, origins, EWM results, and ACS estimates.

Some ACS measures were incorporated at tract level because the selected data
were not used at block-group resolution. Every block group in a tract therefore
shares the same poverty, disability, and uninsured rate. ACS estimates also
carry sampling uncertainty that is not modeled in the regressions.

## Why calculate citywide and borough EWM scores?

The citywide EWM uses one set of weights across all five boroughs and supports
NYC-wide comparison. Borough calculations show how accessibility varies within
each borough when weights reflect its own distribution.

Because weights depend on the sample, borough EWM scores are not automatically
comparable to one another. Citywide results are used for the main cross-borough
maps and regression dataset; borough results are supplementary and useful for
within-borough analysis.

## Why not route a full OD matrix?

A full matrix would connect every block-group origin to all 66 hospitals. It
would substantially increase the number of R5 calculations and the size of the
detailed itinerary outputs. The project instead starts from approximately three
nearby hospital candidates for each origin.

This choice makes borough-scale routing manageable but excludes farther
hospitals before transit travel time is evaluated. A geographically farther
hospital with a faster or simpler transit connection can therefore be missed.

## Why three nearest hospitals?

Three candidates provide limited destination choice while keeping the routing
task feasible. The time-matrix stage is used to compare the candidates, and a
selected or fastest OD record is passed to the detailed-itinerary stage.

The exact GIS procedure used to construct the three-nearest candidate tables and
the exact code used to select the fastest candidate are not present in the
repository. This step should be scripted before the routing analysis is rerun.

## Indicator decisions

The final citywide EWM uses transfers, walking time, walking distance, total
travel time, total distance, and waiting time. All are treated as cost
indicators.

Fare is not included in the final citywide result. An earlier Queens notebook
contains a fare criterion, while the other final indicator tables do not use it
consistently. Fare also depends on transfer rules, fare products, reduced-fare
eligibility, and free-transfer assumptions that are not represented in the
current routing workflow. It should only be added after one consistent fare
model is defined for every borough.

## Limitations

### Computational constraints

The reduced hospital candidate set and borough-by-borough processing were used
to keep routing time and output size manageable. Detailed itinerary and matrix
files are not stored in Git. Reproduction therefore requires the external
inputs and enough memory, processing time, and Java/R5 compatibility.

### Hospital choice

The method assumes that access to a nearby or fastest candidate hospital is an
appropriate accessibility measure. Actual patients may choose facilities based
on specialty, insurance network, referral, perceived quality, language access,
capacity, or prior relationships. These factors are not modeled.

The final 66-point hospital layer represents facilities labeled as hospitals in
the retained NYS Department of Health data. The exact filtering and duplicate-
review procedure was completed in GIS and was not saved as code.

### EWM indicator selection

EWM is sensitive to the included criteria, their measurement quality, and the
sample used to calculate weights. The index does not include service quality,
reliability, crowding, accessibility for disabled riders, hospital capacity, or
care specialization.

### Transit schedules and departure assumptions

Routing results depend on the exact GTFS versions, OSM extract, R5/r5py version,
Java version, departure date and time, and mode parameters. The GTFS manifest
records archived feed dates and checksums, but the current routing scripts do
not explicitly set or document the departure date/time or full mode
configuration. Exact reruns may therefore differ from the archived results.

Static GTFS represents scheduled service rather than observed delays,
cancellations, crowding, or temporary disruptions.

### Walking and origin representation

Pedestrian access depends on OSM network completeness and routing assumptions.
One representative point stands in for all residents of a block group, so
within-block-group variation is not measured. Manhattan points were created
with QGIS Point on Surface, while the other boroughs use Census internal points.

### Spatial inference

Gi* results depend on the eight-nearest-neighbor definition and selected
z-score thresholds. Regression residual spatial dependence and multicollinearity
are checked separately, but the reported regressions remain observational and
should not be interpreted causally.

## Items to document before publication

- archive the exact NYC OSM extract at a permanent URL;
- record the hospital dataset download date and GIS filter expression;
- script the nearest-hospital and fastest-candidate selection steps;
- record the routing departure date, time window, transport modes, and software
  versions;
- reconcile current regression scripts with the saved HTML table generation;
- record the original source and vintage of the block-group and borough
  boundary files; and
- generate the five pending borough map exports with consistent classes and
  layout.

