"""Install the pinned public ZIP directory needed by full-grid acquisition.

Only metadata is copied. No raw field, executable, credentials, or network
session is bundled. A differing pre-existing inventory is never overwritten.
"""
from pathlib import Path
import argparse
import json
from experiments.volume3d.prepare import ROOT, sha256

INVENTORY = Path(__file__).with_name('inputs') / 'tangaroa_archive_inventory.json'
DEFAULT_DATA = ROOT / 'data/real/Tangaroa-FAU'


def install(data_directory=DEFAULT_DATA):
    source = json.loads(INVENTORY.read_text())
    volumes = sorted((r for r in source['members'] if r['name'].endswith('.am')),
                     key=lambda r: float(Path(r['name']).stem.split('tangaroa-')[-1]))
    if len(volumes) != 201 or any(
            abs(float(Path(r['name']).stem.split('tangaroa-')[-1]) - i * .01) > 1e-12
            for i, r in enumerate(volumes)):
        raise ValueError('pinned inventory must identify all 201 original volumes')
    destination = Path(data_directory) / 'archive_inventory.json'
    if destination.exists():
        if sha256(destination) != sha256(INVENTORY):
            raise ValueError(f'Existing inventory differs; inspect it before replacing: {destination}')
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix('.json.part')
        temporary.write_bytes(INVENTORY.read_bytes())
        temporary.replace(destination)
    print(f'Pinned Tangaroa archive inventory ready: {destination}')
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-directory', type=Path, default=DEFAULT_DATA)
    install(parser.parse_args().data_directory)
