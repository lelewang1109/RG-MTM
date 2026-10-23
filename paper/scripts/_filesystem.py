"""File synchronization helpers for canonical assets linked into LaTeX."""
from pathlib import Path
import shutil


def copy_if_distinct(source, destination):
    """Copy only when source and destination refer to different local files."""
    source, destination = Path(source), Path(destination)
    if source.resolve() != destination.resolve():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    return destination
