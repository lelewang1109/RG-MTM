"""Regenerate the current Figure 1 from frozen data, preserving the other figures.
The former six-figure reconstruction was retired because it restored an obsolete
Figure 1. Its scientific layer helpers remain available for targeted maintenance.
"""
from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parents[1]
for script in [R/'scripts/regenerate_fig1.py',R/'scripts/select_manuscript_teaser.py',R/'scripts/package_delivery.py']:
 subprocess.run([sys.executable,str(script)],check=True)
print('Current Figure 1 regenerated. Recompile the manuscript if its PNG changed.')
