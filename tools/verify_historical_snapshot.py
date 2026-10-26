"""Verify the frozen 2026-10-23 outputs without checking/rewriting active TeX.

The historical builder's --check also compares the current manuscript tables.
Those tables intentionally changed when ST-MTM comparisons were completed.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'code/tools'),str(ROOT/'code/src')]
import build_submission20261023 as historical

summary=historical.calculate()
assert summary==json.loads((historical.OUT/'unified_metrics.json').read_text())
manifest=json.loads((historical.OUT/'manifest.json').read_text())
assert historical.frozen_authoring_sha()==manifest['authoring_script_sha256']
for name,digest in manifest['generated_sha256'].items():
    path=historical.OUT/name
    assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==digest,name
for name,digest in manifest['source_sha256'].items():
    assert historical.sha(historical.ROOT/name)==digest,name
print(f'Historical snapshot verified: rebuilt numerical summary, {len(manifest["generated_sha256"])} frozen outputs and {len(manifest["source_sha256"])} source identities; active manuscript tables untouched.')
