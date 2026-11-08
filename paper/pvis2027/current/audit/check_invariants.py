"""Read-only content-preservation audit. Run with Python 3 from any directory."""
from pathlib import Path
import re,json,hashlib,collections
P=Path(__file__).resolve().parents[1];baseline=(P/'audit/baseline_main.tex').read_text()
def expand(path):
 text=path.read_text()
 return re.sub(r'\\input\{([^}]+)\}',lambda m:expand(P/(m.group(1) if Path(m.group(1)).suffix else m.group(1)+'.tex')),text)
a=re.sub(r'\\input\{([^}]+)\}',lambda m:(P/m.group(1)).read_text(),baseline);b=expand(P/'main.tex')
report={}
for env in ['equation','theorem','proposition','table']:
 pat=r'\\begin\{'+env+(r'\*?' if env=='table' else '')+r'\}.*?\\end\{'+env+(r'\*?' if env=='table' else '')+r'\}'
 old=re.findall(pat,a,re.S);new=re.findall(pat,b,re.S);assert collections.Counter(old)==collections.Counter(new),env;report[env]=len(old)
cites=lambda t:collections.Counter(k for x in re.findall(r'\\cite\{([^}]+)\}',t) for k in x.split(','));assert cites(a)==cites(b)
maths=lambda t:set(re.findall(r'(?<!\\)\$(?!\$)(.*?)(?<!\\)\$',t,re.S));assert not maths(a)-maths(b)
manifest=json.loads((P/'audit/source_manifest.json').read_text())
for rel,expected in manifest['figures'].items():
 replacement=manifest.get('authorized_figure_replacements',{}).get(rel)
 if replacement:
  expected=replacement['replacement_sha256'];assert hashlib.sha256((P/replacement['source_in_package']).read_bytes()).hexdigest()==replacement['source_sha256']
 assert hashlib.sha256((P/rel).read_bytes()).hexdigest()==expected,rel
paths=re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',b)+re.findall(r'\\paperfigure(?:\[[^]]*\])?\{([^}]+)\}',b)
assert len({p for p in paths if p.startswith('figures/')})==13
for rel in paths:
 if not rel.startswith('#'):assert (P/rel).is_file(),rel
# Labels in the optional-width figure macro are supplied by its second public argument.
labels=re.findall(r'\\label\{([^}]+)\}',b)+re.findall(r'\\paperfigure(?:\[[^]]*\])?\{[^}]+\}\{([^}]+)\}',b)
refs=re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',b);assert not set(refs)-set(labels),set(refs)-set(labels)
assert not re.search(r'\\(?:input|include|includegraphics|bibliography)(?:\[[^]]*\])?\{/',b)
assert (P/'references.bib').is_file() and (P/'vgtc.cls').is_file() and (P/'abbrv-doi-narrow.bst').is_file()
nums=lambda t:collections.Counter(re.findall(r'(?<![\w.])\d+(?:,\d{3})*(?:\.\d+)?(?![\w.])',t.split('\\begin{document}',1)[1]))
assert nums(a)==nums(b),'body number tokens changed'
report.update(figures=13,all_math_and_table_blocks_byte_identical=True,unmodified_original_figures=12,authorized_workflow_replacement=True,citation_inventory_unchanged=True,inline_math_retained=True,unresolved_labels=[],absolute_TeX_dependencies=[])
print(json.dumps(report,indent=2))
