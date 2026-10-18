"""Export only input/build metadata from a completed local full-grid run."""
from pathlib import Path
import argparse,json,shutil
from experiments.volume3d.prepare import ROOT,sha256

OUT=ROOT/'results/volume3d/tangaroa-paper-p10-full201'
DATA=ROOT/'data/real/Tangaroa-FAU/paper_full_201'


def export(directory=OUT):
    out=Path(directory);manifest=json.loads((out/'manifest.json').read_text())
    verification=json.loads((out/'verification.json').read_text())
    if verification['status']!='passed' or verification['manifest_sha256']!=sha256(out/'manifest.json'):
        raise ValueError('export requires the independently verified numerical manifest')
    files={DATA/'input_protocol.json':('preparation_protocol.json',manifest['source_preparation_protocol_sha256']),
           DATA/'ttk_p10/protocol.json':('tree_protocol.json',manifest['tree_protocol_sha256']),
           DATA/'source_manifest.json':('source_manifest.json',None),
           ROOT/'tmp/volume3d/native-build-manifest.json':('native_build.json',None)}
    for record in manifest['input_trees']:
        name=f"frame_{record['index']:03d}.manifest.json"
        files[DATA/'ttk_p10'/name]=(name,record['manifest_sha256'])
    for source,(_,expected) in files.items():
        if expected is not None and sha256(source)!=expected:raise ValueError(f'Input metadata differs: {source}')
    destination=out/'input_evidence';destination.mkdir(exist_ok=True)
    for source,(name,_) in files.items():shutil.copyfile(source,destination/name)
    print(f'Exported {len(files)} metadata files; no raw field or executable: {destination}')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path,nargs='?',default=OUT)
    export(parser.parse_args().directory)
