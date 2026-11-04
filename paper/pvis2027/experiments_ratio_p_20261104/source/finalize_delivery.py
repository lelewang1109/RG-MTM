"""Check assembled delivery and fingerprint outputs without rerunning experiments."""
from pathlib import Path
import csv, datetime, hashlib, json

O = Path(__file__).resolve().parents[1]
W = O.parents[2]
P = O.parent


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def rows(name):
    with (O / name).open() as f:
        return list(csv.DictReader(f))


def main():
    params = rows('anchor_parameters.csv')
    assert len(params) == 4
    assert all(0 < float(x['epsilon_Balanced']) <= .1 and
               float(x['actual_NMLEmax']) <= float(x['epsilon_Balanced']) + 1e-12
               for x in params)
    comparison = rows('comparison_final.csv')
    assert len(comparison) == len({(x['Dataset'], x['Method']) for x in comparison}) == 16
    assert all(x['TD'] != 'N/A' for x in comparison)
    runtime = rows('anchor_runtime.csv')
    assert len(runtime) == 8 and all(x['success'] == 'True' and
        0 < float(x['t_opt']) <= float(x['t_total']) and int(x['repeats']) == 1
        for x in runtime)
    v = json.loads((O / 'verification.json').read_text())
    assert v['all_passed'] and all(x['profile_minimum_count_mismatch_frames'] == 0
                                 for x in v['records'])
    core = json.loads((O / 'config/core_sha256.json').read_text())
    assert all(sha(W / p) == h for p, h in core.items())
    assert not any(x in (O / 'paper_build.log').read_text() for x in
                   ['Overfull', 'Undefined control sequence', 'undefined references'])
    assert '\\rowcolor' not in (O / 'tables/anchor_parameter_settings.tex').read_text()
    assert (O / 'tables/quantitative_comparison.tex').read_text().count('$t_{\\rm opt}$') == 2
    files = {p for p in O.iterdir() if p.is_file() and p.name != 'DELIVERY_MANIFEST.json'}
    for folder in ['source', 'config', 'tables']:
        files.update(p for p in (O / folder).rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts)
    for ds in ['Gaussian', 'Ring', 'Wildfires', 'Storms']:
        root = O / 'results' / ds
        files.update([root / 'input_audit.json', root / 'selection.json'])
        for folder in ['Exact', 'Balanced', 'baseline_npe', 'selection', 'preparation']:
            files.update(p for p in (root / folder).rglob('*') if p.is_file()
                         and (p.parent == root / folder or folder != 'preparation')
                         and p.suffix in ['.json', '.csv', '.npz', '.npy'])
    files.update([P / 'drafts/method_anchor_figures_updated_en.tex',
                  P / '最新论文与三张PPT/AnchorMTM_最新论文.pdf',
                  P / '最新论文与三张PPT.zip', P / 'README.md'])
    manifest = dict(created=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        selection_rule_version=3, all_40_positive_validation_candidates_legal=True,
        all_8_anchor_runs_legal=True, all_8_displayed_baseline_NPE_computed=True,
        core_sources_unchanged=True, table_rankings_verified=True,
        table_presentation='All TD values visible; four-method SNS/TW/NPE numeric ranking; '
                           'TD ranked by displayed numbers with author-unit caveat; separate optimization/total columns; white parameters',
        source_limitations='Reconstructed processed inputs; author TD units unconfirmed; '
                           'TW coverage64/64,1/40,4/32,11/744; one timing repeat; p numbers interpreted as range fractions',
        files=[dict(path=str(p.relative_to(W)), bytes=p.stat().st_size, sha256=sha(p))
               for p in sorted(files)])
    (O / 'DELIVERY_MANIFEST.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print('Delivery checked:', len(comparison), 'comparison rows,', len(runtime),
          'runtimes,', len(files), 'artifact hashes')


if __name__ == '__main__':
    main()
