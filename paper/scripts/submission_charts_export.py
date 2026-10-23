"""Export the staged native evidence charts with the existing Arial policy."""
from pathlib import Path
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / '.build/research-charts-20261023'
OUT = STAGE / 'output'
BIN = Path('/Users/lele/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override')
fonts = STAGE / 'fonts'
fonts.mkdir(exist_ok=True)
for name in ['Arial.ttf', 'Arial Bold.ttf']:
    shutil.copyfile(Path('/System/Library/Fonts/Supplemental') / name, fonts / name)
cache = STAGE / 'font-cache'
cache.mkdir(exist_ok=True)
config = STAGE / 'fonts.conf'
config.write_text(f'<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig><dir>{fonts}</dir><cachedir>{cache}</cachedir><alias><family>sans-serif</family><prefer><family>Arial</family></prefer></alias></fontconfig>')
env = dict(os.environ, FONTCONFIG_FILE=str(config), SAL_FONTPATH=str(fonts))
profile = '-env:UserInstallation=' + (STAGE / 'lo-profile').as_uri()
stems = ['Fig5', 'Fig7', 'rgmtm_motion_error_comparison', 'rgmtm_neighbourhood_preservation', 'rgmtm_motion_window_sensitivity']
files = [str(OUT / (s + '.pptx')) for s in stems]
assert all(Path(f).exists() for f in files)
for target in ['pdf', 'svg:impress_svg_Export']:
    subprocess.run([str(BIN / 'soffice'), profile, '--headless', '--convert-to', target, '--outdir', str(OUT), *files], check=True, env=env)
for stem in stems:
    subprocess.run([str(BIN / 'pdftoppm'), '-singlefile', '-r', '150', '-png', str(OUT / (stem + '.pdf')), str(OUT / stem)], check=True)
print('Staged exports:', ', '.join(stems))
