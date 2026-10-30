"""Zero-result canary runner (W1-22, CAP-17.c, CAP-55.a)."""
from __future__ import annotations

from pathlib import Path

import yaml

from gov.retrieval import lexical, semantic

# the declarations of the project under check, in either layout of its kernel (DEC-579), never the install path's (DEC-835)
_TEMPLATE = Path("template/governance/kernel/canaries")
_INSTALLED = Path("governance/kernel/canaries")
FACET_UNAVAILABLE = "FACET_UNAVAILABLE"
AVAILABLE = "AVAILABLE"
_SEARCHERS = {"lexical": lexical.search, "semantic": semantic.search}


def run_canaries(root: Path) -> dict:
    root = Path(root)
    results = {}
    for index, searcher in _SEARCHERS.items():
        try:
            found = [path for path in (root / _TEMPLATE / f"{index}.yaml", root / _INSTALLED / f"{index}.yaml")
                     if path.is_file()]
            decl = yaml.safe_load(found[0].read_text(encoding="utf-8"))
            if not isinstance(decl, dict):
                raise ValueError("malformed canary declaration")
        except Exception:
            results[index] = {"passed": False, "status": FACET_UNAVAILABLE,
                              "misses": [], "reason": "unreadable canary declaration"}
            continue
        canaries = decl.get("canaries") or []
        if not canaries:
            results[index] = {"passed": False, "status": FACET_UNAVAILABLE,
                              "misses": [], "reason": "empty canary declaration"}
            continue
        misses = []
        for canary in canaries:
            query = canary.get("query") if isinstance(canary, dict) else None
            if query is None:
                results[index] = {"passed": False, "status": FACET_UNAVAILABLE,
                                  "misses": misses, "reason": "canary entry has no query"}
                break
            try:
                answer = searcher(root, query, refresh=False)
            except Exception:
                misses.append(query)
                continue
            if not answer.get("available") or not answer.get("hits"):
                misses.append(query)
        else:
            passed = not misses
            results[index] = {"passed": passed,
                              "status": AVAILABLE if passed else FACET_UNAVAILABLE,
                              "misses": misses}
    return results
