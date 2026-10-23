"""Build current submission tables and checked snapshots from saved numerical evidence.
Historical six-sequence build is experiments/publication2027/build_legacy.py.
"""
from pathlib import Path
import runpy
ROOT = Path(__file__).resolve().parents[1]
if __name__ == '__main__':
    runpy.run_path(str(ROOT / 'tools/build_submission20261023.py'), run_name='__main__')
