"""Render, publish and record the two verified single-slide experimental figures."""
from _filesystem import copy_if_distinct
from pathlib import Path
import subprocess,shutil,os,json,hashlib,sys
R=Path(__file__).resolve().parents[1];V=R/'supplementary_variants';B=R/'.build/fig1_december';O=B/'render';O.mkdir(exist_ok=True)
RT=Path('/Users/lele/.cache/codex-runtimes/codex-primary-runtime/dependencies');BIN=RT/'bin/override'
fonts=B/'fonts';fonts.mkdir(exist_ok=True);cache=B/'fontcache';cache.mkdir(exist_ok=True)
for name in ['Arial.ttf','Arial Bold.ttf']:shutil.copyfile(Path('/System/Library/Fonts/Supplemental')/name,fonts/name)
config=B/'fonts.conf';config.write_text(f'<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig><dir>{fonts}</dir><cachedir>{cache}</cachedir></fontconfig>')
env=dict(os.environ,FONTCONFIG_FILE=str(config),SAL_FONTPATH=str(fonts))
profile='-env:UserInstallation='+(B/'lo_arial').as_uri()
filter='pdf:impress_pdf_Export:{"ReduceImageResolution":{"type":"boolean","value":"false"},"UseLosslessCompression":{"type":"boolean","value":"true"}}'
manifest={}
for stem in (sys.argv[1:] or ['Fig1_XAxis','Fig1_DataDirection']):
 subprocess.run([str(BIN/'soffice'),profile,'--headless','--convert-to',filter,'--outdir',str(O),str(B/'final'/(stem+'.pptx'))],check=True,env=env)
 for dpi,suffix in [(400,''),(150,'_preview')]:
  subprocess.run([str(BIN/'pdftoppm'),'-singlefile','-r',str(dpi),'-png',str(O/(stem+'.pdf')),str(O/(stem+suffix))],check=True)
 for src,dst in [(B/'final'/(stem+'.pptx'),V/'figures_ppt'/(stem+'.pptx')),(O/(stem+'.pdf'),V/'figures_export'/(stem+'.pdf')),(O/(stem+'.png'),V/'figures_export'/(stem+'.png'))]:
  copy_if_distinct(src,dst);manifest[str(dst.relative_to(R))]=dict(bytes=dst.stat().st_size,sha256=hashlib.sha256(dst.read_bytes()).hexdigest())
(R/'checks/fig1_direction_comparison_delivery.json').write_text(json.dumps(dict(date='2026-10-22',files=manifest,original_main_figures_not_overwritten=True,source='ERA5 actual hourly observations',frames=744),indent=2)+'\n')
print('Both experimental variants published to supplementary_variants/.')
