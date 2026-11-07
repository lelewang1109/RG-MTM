# Hourly PM2.5 case — 2026-11-07

Current single-column figure: January 22 00:00–27 12:00, 2017, Beijing time (133 hourly samples, endpoints included). Source: ChinaVis2021 CAQRA hourly CSV archive, northern China 110–120 E / 32–41 N. The full analysis contains 744 hours. This exploratory case is added to the results and parameter tables as a fixed 5% configuration, distinct from validation-selected Balanced on the original four inputs.

High concentrations are maxima: extraction uses join(-PM2.5), equivalent to split(PM2.5); display restores positive µg/m³. Persistence is 5% of each frame range, separate from the 5% layout allowance. The displayed case uses the original spatially interpolated fields, without added spatial/temporal smoothing. Bilinear display interpolation does not add observed hours. Colors saturate above 400 µg/m³.

Main map and five snapshots have thin black borders, single-line timestamps and no trajectory/dot overlays. Two-slide PPTX retains the original wide image and current compact figure; images are embedded, not editable scientific plots.

Replot the exact compact figure with `python draw.py` (NumPy and Matplotlib). `figure_cache.npz` is a compact derived display cache, not the original nationwide data archive. Full source archives remain external. Summary files document continuous/raster budget and polarity checks.

PM2.5 metrics are recomputed on all 744 shared-input frames: Balanced (fixed 5% case budget) has best SNS (0.1636) and NPE (0.0468); Exact has second NPE (0.1390). Hilbert has best TW (0.8887). Local ST-MTM uses the declared Storms preset with start frame 0; no author PM2.5 baseline scores are claimed. Uncached one-thread remeasurement gives optimization 199.975 s and full pipeline 231.177 s; scientific metrics exactly match the original run. Stage times are recorded in timing.json.
