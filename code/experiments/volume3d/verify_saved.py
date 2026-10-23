"""Verify published 3-D evidence bindings without raw data or numerical reruns.

This checks saved bytes and their provenance relationships. It does not repeat
the all-sample scientific validation performed by verify_paper.py.
"""
from pathlib import Path
import argparse,hashlib,json

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/volume3d/tangaroa-paper-p10-full201'


def digest(path):
    result=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):result.update(block)
    return result.hexdigest()


def read(path):return json.loads(Path(path).read_text())


def require(condition,message):
    if not condition:raise ValueError(message)


def check(path,expected):
    require(digest(path)==expected,f'SHA256 mismatch: {path}')


def verify(directory=OUT):
    out=Path(directory);manifest=read(out/'manifest.json');verification=read(out/'verification.json')
    require(manifest['indices']==list(range(201)),'expected all 201 frames')
    require(read(out/'status.json')==dict(status='complete_verified',frames=201),'run is not complete_verified')
    require(verification['status']=='passed' and verification['frames']==201,'independent audit is incomplete')
    check(out/'manifest.json',verification['manifest_sha256'])
    check(Path(__file__).with_name('verify_paper.py'),verification['verification_source_sha256'])
    for name,expected in manifest['source_sha256'].items():check(ROOT/name,expected)
    for name,expected in manifest['numerical_evidence_sha256'].items():check(out/name,expected)
    for name,expected in verification['independent_helper_sha256'].items():check(ROOT/name,expected)
    evidence=out/'input_evidence'
    check(evidence/'preparation_protocol.json',manifest['source_preparation_protocol_sha256'])
    check(evidence/'tree_protocol.json',manifest['tree_protocol_sha256'])
    preparation=read(evidence/'preparation_protocol.json');trees=read(evidence/'tree_protocol.json')
    check(ROOT/'experiments/volume3d/prepare_tangaroa_paper.py',preparation['prepare_source_sha256'])
    check(ROOT/'experiments/volume3d/inputs/tangaroa_archive_inventory.json',preparation['source_inventory_sha256'])
    check(ROOT/'experiments/volume3d/native/main.cpp',trees['native_source_sha256'])
    check(ROOT/'experiments/volume3d/paper_trees.py',trees['driver_source_sha256'])
    native=read(evidence/'native_build.json')
    require(native['binary_sha256']==trees['native_binary_sha256'],'native executable identity differs')
    require(native['source_archive_sha256']==trees['ttk_source_archive_sha256'],'TTK source archive identity differs')
    check(ROOT/'experiments/volume3d/native/CMakeLists.txt',native['cmake_source_sha256'])
    sources=read(evidence/'source_manifest.json')
    require(sources['protocol']==preparation,'source acquisition protocol differs')
    source_records={r['index']:r for r in sources['records']}
    require(sorted(source_records)==list(range(201)),'source metadata is incomplete')
    inventory=read(ROOT/'experiments/volume3d/inputs/tangaroa_archive_inventory.json')
    members={Path(r['name']).name:r for r in inventory['members'] if r['name'].endswith('.am')}
    for row in manifest['input_trees']:
        name=f"frame_{row['index']:03d}.manifest.json";check(evidence/name,row['manifest_sha256'])
        tree=read(evidence/name);source=source_records[row['index']];member=members[source['source_filename']]
        require(tree['input_sha256']==source['scalar_sha256'],'prepared scalar identity differs')
        require(tree['native_binary_sha256']==trees['native_binary_sha256'],'tree executable identity differs')
        require(source['source_crc32']==member['crc32'] and source['source_bytes']==member['size'],'source ZIP member differs')
    render=read(out/'render_manifest.json')
    check(Path(__file__).with_name('report_paper.py'),render['source_sha256'])
    for group in ['input_sha256','files']:
        for name,expected in render[group].items():check(out/name,expected)
    settings=ROOT/'results/volume3d/tangaroa-input-audit-20261018/author_settings.json'
    check(settings,render['author_rendering_settings_sha256'])
    visual=read(out/'paper_style/visual_manifest.json')
    check(Path(__file__).with_name('paper_style.py'),visual['source_sha256'])
    check(out/'manifest.json',visual['numerical_manifest_sha256'])
    check(out/'verification.json',visual['verification_sha256'])
    check(out/'frame_metrics.json',visual['frame_metrics_sha256'])
    check(settings,visual['author_settings_sha256'])
    camera=Path(__file__).with_name('inputs')/'tangaroa_closer_camera.json'
    check(camera,visual['camera_config_sha256'])
    require(read(camera)['source_sha256']==visual['camera_workspace_sha256'],'camera source identity differs')
    for name,expected in visual['files'].items():check(out/'paper_style'/name,expected)
    metrics=read(out/'metrics.json')
    require(len(metrics)==6 and all(r['frames']==201 for r in metrics),'method evidence is incomplete')
    for pilot in ['synthetic','synthetic-conflict','tangaroa','tangaroa-official']:
        pilot_file=ROOT/'results/volume3d'/pilot/'verification.json'
        if pilot in {'tangaroa','tangaroa-official'}:
            pilot_file=ROOT.parents[1]/'其他/归档/历史或排除结果/volume3d'/pilot/'verification.json'
        require(read(pilot_file)['status']=='passed',f'pilot audit: {pilot}')
    result=dict(status='passed',scope='published evidence bindings only; no raw-input or full-array numerical revalidation',
                original_grid_xyz=[300,180,120],frames=201,methods=[r['method'] for r in metrics],
                original_input_tree_identity_claimed=False,numerical_rerun=False)
    print(json.dumps(result,indent=2,ensure_ascii=False));return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path,nargs='?',default=OUT)
    verify(parser.parse_args().directory)
