"""Compile into a temporary directory; update the one canonical delivery PDF."""
from pathlib import Path
import os,shutil,subprocess,tempfile
base=Path(__file__).resolve().parent
binary=shutil.which('tectonic')
if not binary:
 candidates=sorted((Path.home()/'.cache/codex-tools').glob('tectonic-*/tectonic'))
 if not candidates:raise SystemExit('Tectonic is not installed or on PATH.')
 binary=str(candidates[-1])
with tempfile.TemporaryDirectory(prefix='anchormtm-build-') as tmp:
 subprocess.run([binary,'-X','compile','--outdir',tmp,'method_anchor_figures_updated_en.tex'],cwd=base/'drafts',check=True)
 target=base/'最新论文与三张PPT/AnchorMTM_最新论文.pdf'
 target.parent.mkdir(exist_ok=True)
 staged=target.with_suffix('.tmp.pdf');shutil.copy2(Path(tmp)/'method_anchor_figures_updated_en.pdf',staged);os.replace(staged,target)
print(target)
