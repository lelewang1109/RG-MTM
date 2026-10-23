"""Rebuild the two genuine-hourly Figure1 variants in supplementary_variants.
Default: reuse saved experiment results. --recompute reruns this authorized experiment.
"""
from pathlib import Path
import subprocess,sys,shutil,json,hashlib,os
R=Path(__file__).resolve().parents[1];S=R/'scripts';B=R/'.build/fig1_december'
RT=Path('/Users/lele/.cache/codex-runtimes/codex-primary-runtime/dependencies');NODE=RT/'node/bin/node';BIN=RT/'bin/override'
def run(*args):subprocess.run(list(map(str,args)),check=True,cwd=R.parent)
if '--recompute' in sys.argv:
 run(sys.executable,S/'run_fig1_december_xaxis.py')
 run(sys.executable,S/'solve_fig1_december_xaxis.py')
 run(sys.executable,S/'solve_fig1_december_xaxis.py','--data-direction')
 run(sys.executable,S/'validate_fig1_direction_data.py')
run(sys.executable,S/'prepare_fig1_direction_comparison.py')
run(sys.executable,S/'prepare_fig1_local_panel.py')
for stem in ['Fig1_XAxis','Fig1_DataDirection']:
 run(NODE,S/'build_fig1_direction_comparison.mjs',stem)
 run(sys.executable,S/'patch_fig1_direction_images.py',stem)
 (B/'final'/(stem+'.pptx')).unlink(missing_ok=True)
 run(NODE,S/'finalize_fig1_direction_comparison.mjs',stem)
run(sys.executable,S/'publish_fig1_direction_comparison.py')
