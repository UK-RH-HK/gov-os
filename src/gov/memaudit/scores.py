"""The arithmetic of the figures (Interface items 8 and 10; S2, S3, S6): the retrieval figures from a measure's own
question lines, the printed percentage and the exact 95 % interval. Counts and fixed words only.

``exact_interval`` is the Clopper-Pearson interval by bisection on the binomial tails, as ``f80lib.exact_interval`` of the
fresh 80 (the form of the FRESH-80-RESULT figures).
"""

from __future__ import annotations

import math
import os
from pathlib import Path

import yaml

APART = "nonexistent-id"


def pct(x: int, n: int) -> str:
    return f"{100 * x / n:.1f} %" if n else "-"


def _tail_ge(x, n, p):
    return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(x, n + 1))


def _tail_le(x, n, p):
    return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(0, x + 1))


def exact_interval(x: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """Clopper-Pearson, by bisection on the binomial tails."""
    a = (1 - level) / 2
    if n == 0:
        return 0.0, 1.0

    def solve(f, rising):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if (f(mid) < a) == rising:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    lower = 0.0 if x == 0 else solve(lambda p: _tail_ge(x, n, p), True)
    upper = 1.0 if x == n else solve(lambda p: _tail_le(x, n, p), False)
    return lower, upper


def apart_ids(hidden) -> set[str]:
    """The ids of the set's questions of category ``nonexistent-id`` (the files' own ``id``, else the file's stem)."""
    out = set()
    hidden = Path(hidden)
    if not hidden.is_dir():
        return out
    for e in sorted(os.scandir(hidden), key=lambda e: e.name):
        if not e.name.endswith(".yaml") or not e.is_file():
            continue
        try:
            data = yaml.safe_load(Path(e.path).read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, yaml.YAMLError):
            continue
        if isinstance(data, dict) and data.get("category") == APART:
            out.add(str(data.get("id", e.name[:-5])))
    return out


def retrieval(questions: list[dict], apart: set[str] = frozenset()) -> dict:
    """hit@5, hit@10, hit@20, MRR, gold in the first bundle and full evidence, over the measure's question lines
    (``fault.parse``) of the questions with a gold place: those not in ``apart``."""
    qs = [q for q in questions if q["id"] not in apart]
    n = len(qs)

    def at(k):
        return sum(1 for q in qs if q["rank"] is not None and q["rank"] <= k)
    return {"n": n, "hit5": at(5), "hit10": at(10), "hit20": at(20),
            "mrr": round(sum(1 / q["rank"] for q in qs if q["rank"]) / n, 4) if n else 0.0,
            "in_bundle": sum(1 for q in qs if q["bundle"]), "full": sum(1 for q in qs if q["full"])}


def retrieval_line(attempt: int, r: dict) -> str:
    return (f"RETRIEVAL attempt {attempt}: hit@5 {r['hit5']} of {r['n']} ({pct(r['hit5'], r['n'])}); "
            f"hit@10 {r['hit10']}; hit@20 {r['hit20']}; MRR {r['mrr']:.4f}; in the first bundle {r['in_bundle']}; "
            f"full evidence {r['full']}")
