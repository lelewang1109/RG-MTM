"""Validate current nine-input submission and frozen legacy evidence separately."""
from pathlib import Path
import argparse, subprocess, sys
ROOT = Path(__file__).resolve().parents[2]
def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--require-complete-run', action='store_true', help='Check the historical 30-stage run; current tables are reanalysis, not new runs')
    a = p.parse_args()
    cmd = [sys.executable, str(Path(__file__).with_name('validate_legacy.py'))]
    if a.require_complete_run: cmd.append('--require-complete-run')
    subprocess.run(cmd, check=True)
    subprocess.run([sys.executable, str(ROOT / 'tools/build_submission20261023.py'), '--check'], check=True)
if __name__ == '__main__': main()
