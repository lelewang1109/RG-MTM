# Reference direction in 3-D (2026-10-27)

The certified bounds need only the merge tree, the extremum positions and the
feature widths, so they apply to volumetric data unchanged. This experiment asks
how the choice of the one-dimensional reference affects them on the two
volumetric sequences (Tangaroa, Cylinder).

For 400 directions over the hemisphere (d and -d give the same bound), the
references are rebuilt exactly as the stored ones: projection of each extremum
onto d, canvas origin and length from the projection of the 8 domain corners.
The stored direction reproduces the saved references (asserted).

Per direction: mean order bound nu* (data resolution eps0 = 1e-7), mean NROE of
native TMTM and ST-MTM from their stored positions (one global flip per
sequence, chosen in their favour, so these values are slightly lower than in the
main table, which used the original orientation rule), and violations of the
bound. For the x, y, z axes, the stored direction and the direction with the
smallest bound: our exact width-aware order (NROE, attained displacement tau,
width-aware lower bound).

```sh
cd code
PYTHONPATH=src python experiments/reference_direction/run.py     # both datasets, a few minutes
```

Outputs: `results/reference_direction20261027/{tangaroa,cylinder}.json`.

New rendering of 3-D maps from these layouts needs the raw volumes and the
native TTK extraction, which are not part of the repository; it is not part of
this experiment.
