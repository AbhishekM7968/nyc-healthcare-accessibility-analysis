# GAM figures

`gam_effects.png` is the clean repository name for the historical
`gam_graphs_correct.png` export. `gam_relationships.png` is the accompanying GAM
relationship export.

The historical images have crowded or clipped panel labels and should be
regenerated before final publication. The corrected script uses a 4-by-3 base-R
graphics layout and a 300-DPI PNG device:

```bash
Rscript code/regression/GAM_r/gam_regression.R
```

It writes `gam_graphs_correct.png` in this directory. After visually verifying
all twelve smooth panels, replace `gam_effects.png` with that verified export.
Do not use `ggsave()` for `plot.gam()` output because those plots use base R
graphics.
