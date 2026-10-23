"""Validate the complete research export authorized on 2026-10-23.

The paper, editable sources and figures now live in ../../paper rather than a
code-local private alias. Release-only archives remain outside Git.
"""
from pathlib import Path
import runpy
if __name__=='__main__':
    runpy.run_path(str(Path(__file__).resolve().parents[2]/'tools/verify_release.py'),run_name='__main__')
