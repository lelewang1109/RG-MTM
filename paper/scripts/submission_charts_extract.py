"""Extract saved chart evidence for the 2026-10-23 submission revision.

Reads existing results only. No layout optimization or scientific reruns.
"""
from pathlib import Path
import csv
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT.parent / 'code'
STAGE = ROOT / '.build/research-charts-20261023'
STAGE.mkdir(parents=True, exist_ok=True)
DATASETS = [('era5', 'Storms 1999/2000'), ('wildfire', 'Wildfires 2019'),
            ('olr', 'OLR 2024'), ('pm25', 'PM2.5 Jan 2000'), ('ring', 'Ring')]
sources = {}

def read(p):
    sources[str(p.relative_to(ROOT.parent))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return json.loads(p.read_text())

frontiers = []
for key, label in DATASETS:
    j = read(CODE / f'results/attainable_{key}.json')
    for o in j['ours']:
        if not math.isfinite(o['cap']):
            o['cap'] = 'infinity'
    frontiers.append(dict(key=key, label=label, data=j))

def csvread(p):
    sources[str(p.relative_to(ROOT.parent))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return list(csv.DictReader(p.open()))

volume = []
for key, label, directory in [
    ('tangaroa', 'Tangaroa', CODE / 'results/volume3d/tangaroa-paper-p10-full201'),
    ('cylinder', 'Cylinder', CODE / 'results/paper1_suite/square-cylinder3d')]:
    rows = csvread(directory / 'comparison.csv')
    selected = [r for r in rows if r['method'].startswith('RG-MTM')]
    for row in selected:
        for k in ['NROE_mean', 'NMLE_mean', 'NMLE_max']:
            row[k] = float(row[k])
    if key == 'cylinder':
        motion = read(directory / 'motion.json')
        for row in selected:
            for truth, field in [('spatial', 'ME_3D'), ('projected', 'ME_projected')]:
                match = [m for m in motion if m['method'] == row['method'] and m['truth'] == truth]
                assert len(match) == 1
                row[field] = match[0]['error']
        exact = [m['error'] for m in motion if m['method'] == 'Exact x projection' and m['truth'] == 'spatial'][0]
        counts = {t: [m['clear_events'] for m in motion if m['truth'] == t][0] for t in ['spatial', 'projected']}
    else:
        for row in selected:
            row['ME_3D'] = float(row['ME_3D'])
            row['ME_projected'] = float(row['ME_projected'])
        exact = float([r for r in rows if r['method'] == 'Exact projection'][0]['ME_3D'])
        counts = {'spatial': int(rows[0]['clear_3D']), 'projected': int(rows[0]['clear_projected'])}
    assert len(selected) == 4
    volume.append(dict(key=key, label=label, frames=int(selected[0]['frames']), rows=selected,
                       exact_spatial=exact, counts=counts))

eval_records = read(CODE / 'results/eval_projection.json')
diagnostics = [dict(key=key, label=label, data=eval_records[key]) for key, label in DATASETS]
out = dict(scope='Saved-result chart extraction. No scientific optimization rerun.',
           datasets=[x[0] for x in DATASETS], frontiers=frontiers, volume=volume,
           diagnostics=diagnostics, sources=sources,
           figure5_semantics='F and Phi are frame means under a common maximum scalar budget. '
            'Working-point x coordinates are sequence maxima, y coordinates are mean tau. '
            'Open markers use LCA filling, filled markers use optimal filling of the same order. '
            'The implemented orders need not attain F at their global budget.',
           figure7_semantics='Four achieved settings P, R2, R20, R100. '
            'NROE is the frame mean. Scalar cost shows the mean and maximum NMLE. '
            'Motion error uses spatial and projected clear-event sets separately. '
            'Kappa is an eligibility threshold, not a bound on achieved NMLE.')
def finite_json(o):
    if isinstance(o, dict):
        return {k: finite_json(v) for k, v in o.items()}
    if isinstance(o, list):
        return [finite_json(v) for v in o]
    if isinstance(o, float) and not math.isfinite(o):
        return 'infinity' if o > 0 else 'undefined'
    return o

(STAGE / 'chart_evidence.json').write_text(json.dumps(finite_json(out), ensure_ascii=False, indent=2, allow_nan=False) + '\n')
print(STAGE / 'chart_evidence.json')
