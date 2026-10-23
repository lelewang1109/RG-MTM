"""Index and verify saved public experiments; never rerun numerical experiments."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/latest"
DATASETS = ("era5", "wildfire", "olr", "pm25", "ring")


def snapshot():
    performance = json.loads((ROOT / "results/final_performance.json").read_text())
    images = json.loads((ROOT / "results/figures/manifest.json").read_text())
    control = json.loads((ROOT / "results/publication2027/bisector_control/bisector_highres_x_three_methods.json").read_text())
    frames = {name: performance[name]["frames"] for name in DATASETS}
    assert sum(frames.values()) == 278 # historical five-input runner
    historical_frames=dict(frames)
    frames["pm25"]=366 # current isolated annual replacement
    groups = {}
    for label, directory in (("core_code", "src/rgmtm"), ("analysis", "analysis"),
                             ("experiment_code", "experiments/publication2027")):
        groups[label] = sorted(p for p in (ROOT / directory).rglob("*.py") if "__pycache__" not in p.parts)
    for label, directory in (("legacy_frozen_results", "results/publication2027"),
                             ("current_submission", "results/submission20261023"),
                             ("annual_pm25", "results/pm25_2000"),
                             ("public_metrics", "results/public_metrics_20261016"),
                             ("current_figures", "results/figures")):
        groups[label] = sorted(p for p in (ROOT / directory).rglob("*")
                               if p.is_file() and p.suffix in {".json", ".csv", ".npz", ".png", ".svg", ".md"})
    groups['volume3d_code'] = sorted(p for p in (ROOT/'experiments/volume3d').rglob('*')
                                   if p.is_file() and '__pycache__' not in p.parts
                                   and (p.suffix in {'.py','.cpp','.json','.md'} or p.name=='CMakeLists.txt'))
    groups['volume3d_results'] = sorted(p for p in (ROOT/'results/volume3d').rglob('*')
                                      if p.is_file() and p.suffix in {'.json','.csv','.npz','.npy','.png','.svg','.pdf','.md'})
    for label, directory in (("additional_input_code", "experiments/paper1_suite"),
                             ("additional_input_results", "results/paper1_suite"),
                             ("baseline_audit", "results/baseline_audit_20261019"),
                             ("real_case_evidence", "results/real_case_studies")):
        groups[label] = sorted(p for p in (ROOT / directory).rglob('*')
                               if p.is_file() and '__pycache__' not in p.parts
                               and p.suffix in {'.py', '.cpp', '.json', '.csv', '.npz', '.npy', '.png', '.svg', '.pdf', '.md'})
    groups["primary_records"] = [ROOT / "results" / name for name in (
        "final_performance.json", "final_performance.csv", "eval_projection.json", "native_merge_errors.json",
        "filling.json", "pointcert.json", "protocol_olr.json", "protocol_pm25.json",
        *[f"replicate_{name}.json" for name in DATASETS], *[f"attainable_{name}.json" for name in DATASETS])]
    groups["evaluation_and_export_code"] = [ROOT / "tools" / name for name in (
        "evaluate_public_metrics.py", "check_public_metrics.py", "evaluate_reference_task_metrics.py",
        "build_rgmtm_figures.py", "verify_rgmtm_migration.py", "check_public_export.py",
        "build_latest_experiment_index.py", "build_submission20261023.py", "submission_annual_tables.py",
        "run_pm25_annual.py", "export_pm25_annual.py", "annual_reference_tasks.py")]
    files = {str(p.relative_to(ROOT)): dict(group=group, bytes=p.stat().st_size,
             sha256=hashlib.sha256(p.read_bytes()).hexdigest())
             for group, paths in groups.items() for p in paths}
    return dict(scope="Current nine-input submission; five planar temporal sequences. Annual PM2.5 is isolated from frozen January evidence; this index does not rerun experiments",
                datasets=list(DATASETS), frames=frames, historical_planar_frames=historical_frames, total_frames=sum(frames.values()),
                current_submission="results/submission20261023/manifest.json",
                current_population=dict(primary_datasets=9,temporal_sequences=7,temporal_frames=917,static_sections=22),
                bisector_control_frames=control["frames"], current_figure_groups=json.loads((ROOT.parent/"paper/FIGURE_INDEX.json").read_text())["main_figure_count"], historical_code_figure_groups=len(images["figures"]),
                volume3d_supplement=dict(official_tangaroa_frames=201,original_grid_xyz=[300,180,120],
                    synthetic_frames=[24,24],included_in_planar_614_frames=False, included_in_nine_input_comparison=True,
                    inventory='results/volume3d/README.md'),
                additional_inputs=dict(nucleon_static_planar_inputs=1,
                    benzene_reconstructed_static_planar_sections=21,
                    square_cylinder_volumetric_frames=102,
                    included_in_planar_614_frames=False, included_in_nine_input_comparison=True,
                    inventory='results/paper1_suite/README.md'),
                manuscript_figure_registry='../paper/FIGURE_INDEX.json',
                group_counts={name: len(paths) for name, paths in groups.items()}, files=files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check the committed manifest against current bytes")
    args = parser.parse_args()
    manifest = snapshot()
    path = OUT / "manifest.json"
    if args.check:
        if json.loads(path.read_text()) != manifest:
            raise SystemExit("Experiment snapshot changed; inspect the changes and rebuild the index before upload.")
        print(f"Latest experiment snapshot verified: {len(manifest['files'])} files, "
              f"{manifest['total_frames']} main frames, {manifest['current_figure_groups']} figure groups.")
    else:
        OUT.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        print(f"Indexed {len(manifest['files'])} saved experiment/code/figure files; no numerical experiment rerun.")


if __name__ == "__main__":
    main()
