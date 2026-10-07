"""``gov rebuild`` (W1-27): an act command that recreates every derived store under ``.gov-runtime/``.

Two rebuilds from the same commit give the same digest. Needs only git.
"""

from __future__ import annotations

import time
from pathlib import Path

ACT_PATHS = (".gov-runtime/**",)
CLASS = "act"
HELP = "rebuild derived state"
EXIT_CODES = {}


def run(root: Path, args, config: dict) -> dict:
    from gov.retrieval.lexical import refresh as lexical_refresh
    from gov.store import load as store_load

    store_result = store_load(root)

    t0 = time.monotonic()
    lexical_refresh(root)
    lex_s = round(time.monotonic() - t0, 1)

    stores: dict = {}
    stores["lexical"] = {"status": "recreated", "time_s": lex_s}

    try:
        from gov.retrieval.semantic import refresh as semantic_refresh

        sem = semantic_refresh(root)
        if sem.get("available"):
            stores["semantic"] = {"status": "recreated"}
        else:
            stores["semantic"] = {
                "status": "not_recreated",
                "reason": sem.get("reason", "unknown"),
            }
    except Exception as exc:
        stores["semantic"] = {"status": "not_recreated", "reason": str(exc)}

    try:
        from gov.codeintel import index as codeintel_index

        try:
            codeintel_index(root)
            stores["codeintel"] = {"status": "recreated"}
        except Exception as exc:
            stores["codeintel"] = {
                "status": "not_recreated",
                "reason": str(exc),
            }
    except ImportError as exc:
        stores["codeintel"] = {
            "status": "not_recreated",
            "reason": str(exc),
        }

    return {
        "digest": store_result["digest"],
        "store": store_result,
        "stores": stores,
    }
