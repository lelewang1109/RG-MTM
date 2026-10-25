"""Verify saved evidence against exact, reversible historical source snapshots.

Old numerical runs retain their original source hashes. A registered rename is
accepted only if the current file matches its recorded post-rename hash and its
reverse edits reconstruct the exact old bytes. This is not evidence of a new run.
"""
from pathlib import Path
import hashlib
import json


def evidence_path(root, relative_path):
    """Resolve old experimental-asset paths without publishing manuscripts."""
    root = Path(root)
    relative_path = Path(relative_path)
    if relative_path.parts and relative_path.parts[0] == "paper":
        relocated = root / "results/legacy_publication" / Path(*relative_path.parts[1:])
        if relocated.is_file():
            return relocated
    return root / relative_path


def historical_source_bytes(root,relative_path):
    """Restore the pre-3-D source snapshot with exact hash and edit checks.

    This validates a historical source snapshot, not a rerun with current code
    and not a claim of numerical equivalence between different source versions.
    """
    root=Path(root);path=root/relative_path;current=path.read_bytes()
    # Newer registered edits are reversed before the earlier 3-D snapshot.
    # Each step requires exact before/after hashes; this never asserts that an
    # old numerical run was repeated with the current source.
    for name in ['unified_model_extension_20261026.json',
                 'submission_selection_20261023.json',
                 'baseline_preset_correction_20261019.json',
                 'volume3d_extension_20261017.json']:
        ledger=root/'provenance'/name
        if not ledger.exists():continue
        record=json.loads(ledger.read_text())['sources'].get(str(relative_path))
        if record is None:continue
        if hashlib.sha256(current).hexdigest()!=record['after_sha256']:
            raise ValueError(f'Source changed after registered snapshot {name}: {relative_path}')
        restored=current
        for start,end,original in reversed(record['reverse_edits']):
            restored=restored[:start]+original.encode('utf-8')+restored[end:]
        if hashlib.sha256(restored).hexdigest()!=record['before_sha256']:
            raise ValueError(f'Invalid historical source snapshot {name}: {relative_path}')
        current=restored
    return current



def verify_saved_file(root, relative_path, expected):
    root = Path(root)
    path = evidence_path(root, relative_path)
    if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected:
        return "unchanged"
    if path.is_file() and hashlib.sha256(historical_source_bytes(root,str(relative_path))).hexdigest()==expected:
        return "verified historical source snapshot"
    manifest = root / "provenance/rgmtm_rename_20261016.json"
    record = json.loads(manifest.read_text())["sources"].get(str(relative_path))
    if not record or record["before_sha256"] != expected:
        raise ValueError(f"Unregistered evidence/source mismatch: {relative_path}")
    current = historical_source_bytes(root,record['after_path'])
    if hashlib.sha256(current).hexdigest() != record["after_sha256"]:
        raise ValueError(f"Source changed after registered rename: {relative_path}")
    restored = current
    for start, end, original in reversed(record["reverse_edits"]):
        restored = restored[:start] + original.encode("utf-8") + restored[end:]
    if hashlib.sha256(restored).hexdigest() != expected:
        raise ValueError(f"Invalid reversible rename record: {relative_path}")
    return "verified pre-rename source"
