"""Zero-result canary runner (W1-22, CAP-17.c, CAP-55.a)."""
from __future__ import annotations

from pathlib import Path

import yaml

from gov.retrieval import lexical, semantic

_TEMPLATE = Path(__file__).resolve().parents[3] / "template" / "governance" / "kernel" / "canaries"
FACET_UNAVAILABLE = "FACET_UNAVAILABLE"
AVAILABLE = "AVAILABLE"
_SEARCHERS = {"lexical": lexical.search, "semantic": semantic.search}


def run_canaries(root: Path) -> dict:
    root = Path(root)
    results = {}
    for index, searcher in _SEARCHERS.items():
        decl = yaml.safe_load((_TEMPLATE / f"{index}.yaml").read_text(encoding="utf-8"))
        misses = []
        for canary in decl.get("canaries", []):
            answer = searcher(root, canary["query"], refresh=False)
            if not answer.get("available") or not answer.get("hits"):
                misses.append(canary["query"])
        passed = not misses
        results[index] = {"passed": passed,
                          "status": AVAILABLE if passed else FACET_UNAVAILABLE,
                          "misses": misses}
    return results
