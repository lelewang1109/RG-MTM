"""Check current figure identity; archived numerical audits remain in evidence and checks."""
from pathlib import Path
import subprocess,sys
subprocess.run([sys.executable,str(Path(__file__).with_name('check_figure_consistency.py'))],check=True)
