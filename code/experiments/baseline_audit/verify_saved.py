"""Check frozen baseline-audit bindings without recomputing numerical layouts."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'src'),str(ROOT/'analysis')]
from rgmtm.baselines.tmtm import PAPER_PRESETS
from provenance import verify_saved_file
from real_case_studies import read,write,sha
OUT=ROOT/'results/baseline_audit_20261019'

def verify():
 report=read(OUT/'algorithm_audit.json')
 for path,digest in report['source_sha256'].items():assert sha(ROOT/path)==digest,path
 assert sha(ROOT/'experiments/baseline_audit/official_core_fixture.cpp')==report['official_harness_sha256']
 inputs={}
 for name,d in report['datasets'].items():
  assert not d['TMTM_official_core']['mismatches']
  assert d['TMTM_all_leaf_pair_merge_error_max']==0
  assert d['STMTM']['actual_raster_all_leaf_pair_merge_error_max']==0
  assert not d['STMTM']['topology_signature_failed_frames']
  metadata=read(ROOT/f'results/real_case_studies/evidence/{name}.json');path=ROOT/metadata['source'];assert sha(path)==metadata['source_sha256'];inputs[metadata['source']]=sha(path)
 for key in ['0.15','0.5','2','10']:assert PAPER_PRESETS['tangaroa-'+key].tree_kind=='join'
 old=read(ROOT/'provenance/rgmtm_rename_20261016.json');count=0
 for p,digest in old['protected_result_sha256'].items():assert sha(ROOT/p)==digest;count+=1
 for p,record in old['sources'].items():verify_saved_file(ROOT,p,record['before_sha256'])
 record=dict(status='passed',input_sha256=inputs,algorithm_report_sha256=sha(OUT/'algorithm_audit.json'),
   preserved_original_numeric_files=count,source_snapshots='exactly reversible; no result rerun implied',
   metadata_correction='all four Tangaroa generic presets use join; active full201 was already join',
   report_sha256={n:sha(OUT/n)for n in ['REPORT_zh.md','preset_correction.json']})
 write(OUT/'validation.json',record);print(json.dumps(record,indent=2))
 return record
if __name__=='__main__':verify()
