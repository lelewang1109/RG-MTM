"""Regenerate the selected744-hour data-direction Figure1 from saved results."""
from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parents[1]
for name in ['regenerate_fig1_direction_comparison.py','install_selected_fig1.py','select_manuscript_teaser.py','package_delivery.py']:
 subprocess.run([sys.executable,str(R/'scripts'/name)],check=True)
print('Selected data-direction Figure1 updated; recompile the manuscript after scientific changes.')
