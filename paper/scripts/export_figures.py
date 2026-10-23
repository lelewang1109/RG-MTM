"""Export canonical PPT masters with real Arial regular/bold fonts.
Usage: export_figures.py 2,4 | Fig2,Supplement_Storms_Detail | all
Does not rebuild scientific data. Run sync_figure_catalog.py afterward.
"""
from pathlib import Path
import subprocess,sys,json,os,shutil
R=Path(__file__).resolve().parents[1]
BIN=Path('/Users/lele/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override')
reg=json.loads((R/'FIGURE_INDEX.json').read_text())
arg=sys.argv[1] if len(sys.argv)>1 else 'all'
stems=([f['stem']for f in reg['figures']]+[f['stem']for f in reg.get('supplementary_figures',[])])if arg=='all' else [('Fig'+s if s.isdigit()else s.removesuffix('.pptx'))for s in arg.split(',')]
files=[R/'figures_ppt'/(s+'.pptx')for s in stems]
assert all(p.exists()for p in files),files
stage=R/'.build/arial_export';fonts=stage/'fonts';fonts.mkdir(parents=True,exist_ok=True)
for name in ['Arial.ttf','Arial Bold.ttf']:
 source=Path('/System/Library/Fonts/Supplemental')/name
 if not source.exists():raise FileNotFoundError('Real Arial font required for a consistent export: '+str(source))
 # Copy bytes only: macOS system-font flags cannot be applied to workspace files.
 shutil.copyfile(source,fonts/name)
cache=stage/'cache';cache.mkdir(exist_ok=True)
config=stage/'fonts.conf';config.write_text(f'<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig><dir>{fonts}</dir><cachedir>{cache}</cachedir><alias><family>sans-serif</family><prefer><family>Arial</family></prefer></alias></fontconfig>')
env=dict(os.environ,FONTCONFIG_FILE=str(config),SAL_FONTPATH=str(fonts))
profile='-env:UserInstallation='+(stage/'lo-profile').as_uri()
for target in ['pdf','svg:impress_svg_Export']:
 subprocess.run([str(BIN/'soffice'),profile,'--headless','--convert-to',target,'--outdir',str(R/'figures_export'),*map(str,files)],check=True,env=env)
for stem in stems:
 p=R/'figures_export'/(stem+'.pdf')
 subprocess.run([str(BIN/'pdftoppm'),'-singlefile','-r','200','-png',str(p),str(p.with_suffix(''))],check=True)
 assert p.with_suffix('.svg').exists()
print('Exported with real Arial:',', '.join(stems))
