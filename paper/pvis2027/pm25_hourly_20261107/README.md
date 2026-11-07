# Hourly PM2.5 case — 2026-11-07

Current single-column figure: January 22 00:00–27 12:00, 2017, Beijing time (133 hourly samples, endpoints included). Source: ChinaVis2021 CAQRA hourly CSV archive, northern China 110–120 E / 32–41 N. The full analysis contains 744 hours. This case is exploratory and excluded from the formal four-input comparison.

High concentrations are maxima: extraction uses join(-PM2.5), equivalent to split(PM2.5); display restores positive µg/m³. Persistence is 5% of each frame range, separate from the 5% layout allowance. The displayed case uses the original spatially interpolated fields, without added spatial/temporal smoothing. Bilinear display interpolation does not add observed hours. Colors saturate above 400 µg/m³.

Main map and five snapshots have thin black borders, single-line timestamps and no trajectory/dot overlays. Two-slide PPTX retains the original wide image and current compact figure; images are embedded, not editable scientific plots.

Replot the exact compact figure with `python draw.py` (NumPy and Matplotlib). `figure_cache.npz` is a compact derived display cache, not the original nationwide data archive. Full source archives remain external. Summary files document continuous/raster budget and polarity checks.
