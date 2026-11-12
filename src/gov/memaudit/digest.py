"""The ``figures`` reader (item 6) and the digest block's twelve lines (item 7).

``figures`` is the one place the driver's figures come from a file under the sets root, and it runs as a child: it prints
one JSON line of numbers and fixed words. The digest is built from that line, the launch counts, git and the driver's own
counts, so it holds ids, counts and repository paths only (F2).
"""

from __future__ import annotations

import json

from gov.memaudit import layout
from gov.memaudit.common import read_json

CLASSES = ("gold_wrong", "question_ambiguous", "out_of_scope", "retrieval_miss", "answer_wrong")
NOT = "not reached"


def _pick(doc, *keys):
    for k in keys:
        doc = doc.get(k) if isinstance(doc, dict) else None
    return doc


def figures(sets_root, audit, emit) -> str:
    """One JSON line from ``FIGURES.json`` and ``DROPS.json``; a missing file gives ``null`` for its keys."""
    run = layout.paths(sets_root, audit)["run"]
    fig, drops = read_json(run / "FIGURES.json"), read_json(run / "DROPS.json")
    verdict = _pick(fig, "verdict")
    line = {
        "audit": audit,
        "n": _pick(fig, "n"),
        "n_gold": _pick(fig, "n_gold"),
        "verdict": {k: verdict.get(k) for k in ("right", "wrong", "passes", "interval_exact")}
        if isinstance(verdict, dict) else None,
        "bar": _pick(fig, "bar"),
        "hit5": _pick(fig, "beside", "hit5"),
        "in_bundle": _pick(fig, "beside", "in_bundle"),
        "by_rank": _pick(fig, "misses", "by_rank"),
        "by_namespace": _pick(fig, "misses", "by_namespace"),
        "classes": _pick(fig, "classes"),
        "pool": _pick(fig, "pool"),
        "usd": _pick(fig, "spend", "usd"),
        "kept": _pick(drops, "kept"),
        "dropped": _pick(drops, "dropped"),
        "by_code": _pick(drops, "by_code"),
    }
    emit(json.dumps(line, sort_keys=True))
    return "ok"


def _word(value) -> str:
    return "none" if value is None else str(value)


def lines(st: dict) -> list[str]:
    """The twelve lines of the block from the run's state ``st`` (see ``driver``): a figure not reached prints its word
    followed by ``not reached``."""
    f = st.get("figures") or {}
    v, bar, rank, ns = f.get("verdict"), f.get("bar"), f.get("by_rank"), f.get("by_namespace")
    classes, pool, drops = f.get("classes"), f.get("pool"), f.get("by_code")
    out = [f"AUDIT {st['audit']} commit {st['commit'][:12]}", f"MODE {st['mode']} reason {st['reason']}"]
    if v and bar and f.get("n") is not None and v.get("interval_exact"):
        lo, hi = v["interval_exact"]
        out.append(f"VERDICT right {v['right']} of {f['n']}; wrong {v['wrong']}; exact {100 * lo:.1f} to {100 * hi:.1f} %; "
                   f"bar {bar['need_right']} right, {bar['max_wrong']} wrong: {'passes' if v['passes'] else 'misses'}")
    else:
        out.append(f"VERDICT {NOT}")
    out.append(f"HIT5 {f['hit5']} of {f['n_gold']}; first bundle {f['in_bundle']}"
               if f.get("hit5") is not None and f.get("n_gold") is not None and f.get("in_bundle") is not None
               else f"HIT5 {NOT}")
    if classes and rank and ns:
        out.append("MISSES class " + " ".join(f"{c} {classes[c]}" for c in CLASSES)
                   + f"; rank 1-5 {rank['rank_1_5']} 6-20 {rank['rank_6_20']} none {rank['not_in_20']}"
                   + f"; namespace embedded {ns['embedded']} keyword_only {ns['keyword_only']}")
    else:
        out.append(f"MISSES {NOT}")
    if isinstance(pool, dict) and pool.get("n") is not None:
        out.append(f"POOL hit5 {pool['hit5']} of {pool['n']} last {_word(pool.get('last_hit5'))}; "
                   f"full {pool['full']} last {_word(pool.get('last_full'))}; "
                   f"regression {'yes' if pool.get('regression') else 'no'}")
    else:
        out.append(f"POOL {NOT}")
    paths = st.get("retrieval", [])
    out.append(f"RETRIEVAL changed {len(paths)}" + (": " + " ".join(paths) if paths else ""))
    if f.get("kept") is not None and f.get("dropped") is not None:
        codes = "".join(f"; {c} {n}" if i == 0 else f" {c} {n}" for i, (c, n) in enumerate(sorted((drops or {}).items())))
        out.append(f"QUESTIONS kept {f['kept']} dropped {f['dropped']}{codes}")
    else:
        out.append(f"QUESTIONS {NOT}")
    cost = st.get("cost") or {}
    out.append("COST " + " ".join(f"{k} {x:.2f}" for k, x in cost.items()) + f" total {sum(cost.values()):.2f}"
               if cost else f"COST {NOT}")
    out.append(f"NEXT due {st['next']} {st['next_mode']}")
    if st.get("refused"):
        out.append(f"REFUSED {st['refused']}")
    elif st.get("stop"):
        out.append(f"STOP {st['stop']['step']} exit {st['stop']['exit']}")
    else:
        out.append("STOP none")
    stop = st.get("stop")
    out.append(f"OWNER stopped after USED at {stop['step']} exit {stop['exit']}: the set is not run again"
               if stop and stop.get("used") else "OWNER none")
    return out
