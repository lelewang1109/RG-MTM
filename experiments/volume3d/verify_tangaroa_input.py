"""Independent official-source audit using physical-coordinate interpolation.

The preparer uses index-coordinate map_coordinates. Here parse source bytes
independently, derive speed and sample with RegularGridInterpolator instead.
"""
from pathlib import Path
import json
import re
import sys
import zlib
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.interpolate import RegularGridInterpolator
from experiments.volume3d.prepare import ROOT,sha256


def verify(directory):
    directory=Path(directory)
    meta=json.loads((directory/'input_protocol.json').read_text())
    assert meta['dataset']=='Tangaroa-FAU-speed'
    data=ROOT/'data/real/Tangaroa-FAU'
    prepared=data/'prepared_speed_12.npz'
    assert sha256(prepared)==meta['prepared_input_sha256']
    with np.load(directory/'processed_fields.npz',allow_pickle=False) as source:
        raw=source['raw'];coords=source['coords']
    errors=[]
    for t,record in enumerate(meta['source_records']):
        path=data/record['filename'];payload=path.read_bytes()
        assert len(payload)==record['bytes'] and zlib.crc32(payload)==record['crc32']
        assert sha256(path)==record['sha256']
        marker=re.search(rb'\n@1\r?\n',payload)
        assert marker and b'BINARY-LITTLE-ENDIAN' in payload[:marker.start()]
        shape=tuple(re.search(rb'define\s+Lattice\s+(\d+)\s+(\d+)\s+(\d+)',payload).groups())
        nx,ny,nz=map(int,shape);assert (nx,ny,nz)==(300,180,120)
        vector=np.frombuffer(payload,dtype='<f4',offset=marker.end(),count=nx*ny*nz*3).reshape(nz,ny,nx,3).astype(float)
        speed=np.sqrt(np.sum(vector*vector,axis=-1))
        assert np.isfinite(speed).all()
        np.testing.assert_allclose([speed.min(),speed.max()],[record['speed_min'],record['speed_max']],rtol=0,atol=1e-14)
        bounds=np.array(record['velocity_bounds_xyz']).reshape(3,2)
        physical_bounds=np.c_[coords.min(0),coords.max(0)]
        np.testing.assert_allclose(physical_bounds,bounds,rtol=0,atol=1e-14)
        sigma=np.array(meta['antialias_sigma_source_zyx'])
        factor=np.array(speed.shape)/np.array(raw.shape[1:])
        np.testing.assert_allclose(sigma,.5*np.sqrt(factor**2-1),rtol=0,atol=1e-14)
        smooth=gaussian_filter(speed,sigma,mode='reflect')
        xyz=[np.linspace(*b,n) for b,n in zip(bounds,[nx,ny,nz])]
        interpolator=RegularGridInterpolator(tuple(xyz[::-1]),smooth,bounds_error=True)
        expected=interpolator(coords[:,::-1]).reshape(raw.shape[1:])
        errors.append(float(abs(expected-raw[t]).max()))
        np.testing.assert_allclose(expected,raw[t],rtol=0,atol=2e-13)
    result=dict(status='passed',source_frames=len(errors),source_total_frames=meta['source_total_frames'],
        interpolation_max_absolute_difference=max(errors),
        checks=['every original Amira byte count, CRC32, SHA256','independent source binary parse and XYZ components',
                'source-grid speed before scalar filtering','source physical bounds and declared antialias scale',
                'physical-coordinate RegularGridInterpolator versus prepared index-coordinate interpolation'],
        audit_source_sha256=sha256(Path(__file__)),
        artifact_sha256={name:sha256(directory/name) for name in ['input_protocol.json','processed_fields.npz']})
    (directory/'input_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));return result


if __name__=='__main__':verify(Path(sys.argv[1]))
