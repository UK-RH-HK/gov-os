"""``classes``: the auditor's five class counts into ``FIGURES.json`` (Interface items 1 and 10; S6).

Reads ``runs/<A>/miss-classes.json`` (the launch script's delivered copy of the auditor's ``classes.json``,
``{"<id>": {"class", "reason"}}``). Its ids must be exactly ``misses.jsonl``'s and every class one of the five, else
``MS-CLASSES``. Only the five counts reach ``FIGURES.json``; no reason is copied (F1).
"""

from __future__ import annotations

import json

from gov.memaudit import figures as figs
from gov.memaudit import layout
from gov.memaudit.common import read_json


def run(sets_root, audit, *, emit) -> str:
    """``ok`` or ``refused`` (``MS-NOFIGURES``, ``MS-CLASSES``)."""
    p = layout.paths(sets_root, audit)
    run_dir = p["run"]
    figures = read_json(run_dir / "FIGURES.json")
    if not isinstance(figures, dict):
        emit("MS-NOFIGURES")
        return "refused"
    try:
        lines = (run_dir / "misses.jsonl").read_text(encoding="utf-8").splitlines()
        ids = {json.loads(x)["id"] for x in lines if x.strip()}
    except (OSError, ValueError, KeyError, TypeError):
        emit("MS-CLASSES")
        return "refused"
    doc = read_json(run_dir / "miss-classes.json")
    if doc is None and not ids and not (run_dir / "miss-classes.json").exists():
        doc = {}
    if not isinstance(doc, dict) or set(doc) != ids or not all(
            isinstance(v, dict) and v.get("class") in figs.CLASSES for v in doc.values()):
        emit("MS-CLASSES")
        return "refused"
    counts = {c: sum(1 for v in doc.values() if v["class"] == c) for c in figs.CLASSES}
    figures["classes"] = counts
    figs.write_figures(run_dir, figures)
    emit("CLASSES " + "; ".join(f"{c} {n}" for c, n in counts.items()))
    return "ok"
