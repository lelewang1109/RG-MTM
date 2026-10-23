"""Independent full-array verification of the corrected three-frame input audit.

Decode original Amira bytes directly, without calling the preparation reader or
audit computation. This verifies pre-TTK scalar inputs, not paper tree layouts.
"""
from pathlib import Path
import hashlib
import json
import re
import zlib
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data/real/Tangaroa-FAU'
OUT=ROOT/'results/volume3d/tangaroa-input-audit-20261018'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify(directory=OUT):
    directory=Path(directory);audit=json.loads((directory/'input_audit.json').read_text())
    hashes=json.loads((directory/'artifact_hashes.json').read_text())
    for name,expected in hashes.items():assert digest(directory/name)==expected,name
    assert digest(Path(__file__).with_name('audit_tangaroa.py'))==audit['audit_source_sha256']
    assert not audit['ttk_simplification_applied'] and not audit['complete_201_frame_rgmtm_reproduction']
    records=[]
    for row in audit['records']:
        path=DATA/row['filename'];raw=path.read_bytes()
        assert digest(path)==row['source_sha256'] and zlib.crc32(raw)==row['source_crc32']
        header,payload=raw.split(b'\n@1',1)
        if payload.startswith(b'\r\n'):payload=payload[2:]
        elif payload.startswith(b'\n'):payload=payload[1:]
        else:raise ValueError('missing line terminator after Amira data marker')
        assert b'BINARY-LITTLE-ENDIAN' in header and b'float[3]' in header
        dimensions=tuple(map(int,re.search(rb'define Lattice (\d+) (\d+) (\d+)',header).groups()))
        assert dimensions==(300,180,120) and len(payload)==np.prod(dimensions)*3*4
        v=np.frombuffer(payload,dtype='<f4').reshape(120,180,300,3)
        u,w,z=[v[...,i].astype(np.float64) for i in range(3)]
        speed=np.sqrt(u*u+w*w+z*z).astype(np.float32)
        corrected=speed.copy();corrected[speed<1e-6]=1;corrected[corrected>2]=2
        prepared=DATA/f"paper_protocol_speed_index_{row['paper_index']:03d}.npz"
        assert digest(prepared)==row['corrected_input_sha256']
        with np.load(prepared) as cache:
            assert str(cache['tree_kind'])=='join'
            assert not cache['ttk_simplification_applied'] and not cache['spatial_smoothing_applied'] and not cache['spatial_resampling_applied']
            np.testing.assert_array_equal(cache['field'],corrected)
            np.testing.assert_array_equal(cache['bounds_xyz'],[-.35,.65,-.3,.3,-.5,-.3])
        assert hashlib.sha256(corrected.tobytes()).hexdigest()==row['corrected_field_sha256']
        assert int((speed<1e-6).sum())==row['masked_samples_main']
        assert int((speed>2).sum())==row['clipped_high_samples']
        records.append(dict(paper_index=row['paper_index'],max_absolute_difference=0.,samples=int(corrected.size)))
    result=dict(status='passed',scope='three original-resolution pre-TTK scalar inputs; not a complete paper reproduction',
        independent_decoder=True,records=records,artifact_manifest_sha256=digest(directory/'artifact_hashes.json'),
        verification_source_sha256=digest(__file__))
    (directory/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));return result


if __name__=='__main__':verify()
