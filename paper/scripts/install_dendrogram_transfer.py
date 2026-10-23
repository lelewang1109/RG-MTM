"""Package the retained row-ordering figure and records without rerunning it."""
from pathlib import Path
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[1]
D = R.parent / 'code/results'
L = R / 'manuscript/latex'
dest = L / 'evidence/dendrogram_transfer'
dest.mkdir(parents=True, exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
files = ['dendrogram_demo.pdf', 'dendrogram_demo.json', 'generality.json']
original = {n: sha(D / n) for n in files}
for name in files:
    shutil.copy2(D / name, dest / name)
shutil.copy2(D / 'dendrogram_demo.pdf', L / 'figures/Fig7.pdf')
shutil.copy2(D / 'dendrogram_demo.pdf', R / 'figures_export/Fig7.pdf')
for name in ['generality.py', 'theory.py']:
    shutil.copy2(D.parent / 'analysis' / name, dest / name)
s = json.loads((D / 'dendrogram_demo.json').read_text())
g = json.loads((D / 'generality.json').read_text())
assert s['n'] == g['n'] == 1024
assert abs(s['ref_max_share'] * s['n'] - g['tau_free_rows']) < 1e-10
tau, free = s['tau_star_share'] * s['n'], g['tau_free_rows']
report = dict(
    source_records=original,
    source_figure='code/results/dendrogram_demo.pdf',
    source_figure_palette='Blues (archived PDF; screenshot uses a different palette)',
    original_records_unmodified=all(sha(D / n) == original[n] for n in files),
    experiment_rerun=False, figures_redrawn=False,
    manuscript_figure_number=7, manuscript_section='6.4',
    leaf_count=s['n'], observations_per_leaf=30,
    normalization='1024-row canvas height; maxima over cells',
    olo_max_percent=s['olo_max_share'] * 100,
    hierarchy_saved_endpoint_percent=s['tau_star_share'] * 100,
    hierarchy_tolerance_rows=0.25,
    hierarchy_optimum_percent_bracket=[(tau - .25) / s['n'] * 100, tau / s['n'] * 100],
    free_packing_percent=s['ref_max_share'] * 100,
    additional_hierarchy_cost_pp=(tau - free) / s['n'] * 100,
    main_suite_pooling=False,
    role='Positional certification for a clustering tree; scalar-barrier claims remain in merge-tree experiments.',
)
(R / 'checks/dendrogram_transfer_20261020.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
