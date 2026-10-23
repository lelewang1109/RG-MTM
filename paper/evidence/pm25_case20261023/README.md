# PM2.5 source-linked case

Figure 13 reads the unchanged full-year 2000 experiment. It adds visual analysis, not another dataset or new accuracy population.

- Annual input: 366 dated 10:30 fields, same 102–114°E / 28–38°N region, 49×49 analysis grid and 100 km smoothing.
- Selection: 34 frames have a strongest three-feature witness above 2% L; five have three common tracks over at least three consecutive dates. Closest to their median witness obstruction selects July 14, frame195. Motion scores and achieved gains do not enter selection.
- Source views: July12–16; local map: July10–20. A153/B146/C152 are processed-field extrema, not independently validated pollutant plumes.
- On July14, maximum displayed-anchor error is P14.8809% L / R20 0.8373% L. Measured NMLE is1.119210%; the local window reaches3.332004%. NMLE uses the fixed annual processed scalar range147.885866 µg/m³, not a displayed colour range.
- The annual map uses0–165 µg/m³. All local supplied/processed fields and both local maps share0–100 µg/m³. No per-date scaling; no AQI categories.
- Case scalar arrays and original profiles are unchanged. P/R local display reconstruction uses the same41 display samples per original date and preserves every saved frame exactly. Intermediate columns are display samples only.
- The annual motion scores remain P42/95 and R20 47/95. This local example supplies a mechanism, not an annual performance claim or independent physical-episode validation.

Authoring: `../../scripts/prepare_pm25_case.py`, native scene to PPT with `../../scripts/submission_cases_build.mjs`. Independent checks: `../../scripts/verify_pm25_case.py`. `case.json` contains all candidate frames, marker coordinates, source hashes and precise measurements. `case_arrays.npz` contains compact source/analysis arrays. Geographic context is a frozen Natural Earth China province subset, with its source hash recorded separately in data/geo/pm25_context/source.json.
