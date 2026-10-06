"""``gov rebuild`` (W1-27): an act command that recreates every derived store under ``.gov-runtime/``.

Two rebuilds from the same commit give the same digest. Needs only git.
"""

from __future__ import annotations

from pathlib import Path

ACT_PATHS = (".gov-runtime/**",)
CLASS = "act"
HELP = "rebuild derived state"
EXIT_CODES = {}


def run(root: Path, args, config: dict) -> dict:
    from gov.store import load as store_load

    runtime = root / ".gov-runtime"
    store_path = runtime / "store.db"
    if store_path.is_file():
        store_path.unlink()

    store_result = store_load(root)

    return {
        "digest": store_result["digest"],
        "store": store_result,
    }
