"""Compatibility entry point: current figure numbering is defined by FIGURE_INDEX.json."""
from pathlib import Path
import subprocess,sys
subprocess.run([sys.executable,str(Path(__file__).with_name('sync_figure_catalog.py'))],check=True)
