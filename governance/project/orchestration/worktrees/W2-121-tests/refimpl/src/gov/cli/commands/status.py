"""``gov status`` (W1-07): a read command. The convention of a command module is in ``gov.cli.main``."""

from __future__ import annotations

from pathlib import Path


def run(root: Path, args, config: dict) -> dict:
    return {"root": str(root), "config_files": sorted(config)}
