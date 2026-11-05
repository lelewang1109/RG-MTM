# Cylinder central-tree figure (Q only)

Run `python make_figure.py` with NumPy and Matplotlib to regenerate PDF/PNG/SVG from the compact cache. Cache arrays contain Q only; there are no velocity-direction or vorticity attributes. The 3D meshes are native-grid Q=0.2/1 level sets of original frames 20, 50, 101. All three cameras and physical scales agree. Times cover the public 102-frame data, not the paper's unavailable 508-frame version.

S links the retained extremum of track 21 to its containing Q>=0.2 component at frame 50. The one-dimensional locator is padded. It is not a complete 3D-region footprint.

The temporal coordinate is centered-tree layout position in [-0.5,0.5], not physical X. This is an exploratory fixed-tree-order layout variant. Mean frame-balanced absolute X error is 28.1%, versus 1.9% for the previous streamwise configuration. The X cap is 56.21%; retained-leaf NMLEmax is 0 in all 102 frames, within the 1% cap. It does not establish the previous position-preservation advantage.

Phases I/II/III are qualitative reading guides, not estimated physical transition times. One sequential blue Q scale is used in all panels. Native Q values are retained; the color scale alone saturates above 1.

Dataset: https://tinoweinkauf.net/notes/squarecylinder.html . Source archive and method-layout hashes are in provenance.json. The original reference smoke-surface illustration is not reproduced.
