"""The fault rule's parts (Interface item 12; S4, F3): when a retrieval was not answered as declared, what a measure's
text output holds, and when an attempt is whole. Pure functions over text and kept files; nothing here searches.

``degraded`` is ``f80lib.degraded`` of the fresh 80, on a kept output's ``result``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

UNRESOLVED_IDS = "UNRESOLVED_IDS"  # gov.closure.UNRESOLVED_ALONE
KEPT = re.compile(r"[0-9]{5,}\.json")
QUESTION = re.compile(r"(\S+) \((\w+)\): hit@5 (yes|no) \(first gold rank (\d+|-)\), in the bundle (yes|no); "
                      r"full evidence (yes|no)\b")
CALLS = re.compile(r"; (\d+) calls?(?:;|$)")


def degraded(result) -> str | None:
    """Why a retrieval was not answered as declared, or None: no bundle; a route (lexical or semantic) missing or not
    available; a non-empty bundle not reranked by the shared service (``rerank.by`` other than ``service``); the
    pool's rerank fallen back. The empty UNRESOLVED_IDS bundle (the stated gap, which carries no rerank) is none."""
    if not isinstance(result, dict) or not isinstance(result.get("evidence"), list):
        return "no bundle"
    if result.get("stopping_reason") == UNRESOLVED_IDS and not result["evidence"]:
        return None
    facets = result.get("facets") if isinstance(result.get("facets"), dict) else {}
    for route in ("lexical", "semantic"):
        f = facets.get(route)
        if not isinstance(f, dict):
            return f"route {route} missing"
        if not f.get("available"):
            return f"route {route} unavailable"
    if result["evidence"]:
        rerank = result.get("rerank")
        by = rerank.get("by") if isinstance(rerank, dict) else None
        if by != "service":
            return f"reranker {by}"
    if isinstance(result.get("pool"), dict) and result["pool"].get("fallback"):
        return "pool fallback"
    return None


def result_of(text) -> dict | None:
    """The ``result`` of one retriever output (``gov retrieve --json``), or None when it holds none."""
    try:
        doc = json.loads(text)
        result = doc["result"]
    except (ValueError, KeyError, TypeError):
        return None
    return result if isinstance(result, dict) else None


def answered(rc: int, text) -> tuple[bool, str | None]:
    """Whether one search was answered as declared, and the word of the ``ready`` event for why not (None, ``exit``,
    ``no bundle``, ``route``, ``reranker``, ``pool``)."""
    if rc != 0:
        return False, "exit"
    result = result_of(text)
    try:
        failed = json.loads(text).get("ok") is False
    except (ValueError, AttributeError):
        failed = False
    if result is None or failed:
        return False, "no bundle"
    why = degraded(result)
    if why is None:
        return True, None
    if why.startswith("route"):
        return False, "route"
    if why.startswith("reranker"):
        return False, "reranker"
    if why.startswith("pool"):
        return False, "pool"
    return False, "no bundle"


def kept_files(folder) -> list[Path]:
    """The kept outputs of a run folder (``kept/00001.json`` ...) in call order."""
    where = Path(folder) / "kept"
    if not where.is_dir():
        return []
    return sorted((f for f in where.iterdir() if KEPT.fullmatch(f.name) and f.is_file()), key=lambda f: int(f.stem))


def kept_result(file) -> dict | None:
    try:
        return result_of(Path(file).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return None


def parse(text: str) -> dict:
    """What a measure's text output holds: ``families`` (its first ``families:`` line, or None), ``questions`` (one
    dict per question line, in order: id, part, hit5, rank, bundle, full, calls) and ``total`` (a total line)."""
    families, questions, total = None, [], False
    for line in text.splitlines():
        if line.startswith("families:") and families is None:
            families = line
        elif line.startswith("total:"):
            total = True
        else:
            m = QUESTION.match(line)
            if m:
                c = CALLS.search(line)
                questions.append({"id": m[1], "part": m[2], "hit5": m[3] == "yes",
                                  "rank": None if m[4] == "-" else int(m[4]), "bundle": m[5] == "yes",
                                  "full": m[6] == "yes", "calls": int(c[1]) if c else 0})
    return {"families": families, "questions": questions, "total": total}


def read_parsed(folder) -> dict:
    try:
        text = (Path(folder) / "measure.txt").read_text(encoding="utf-8", errors="replace")
    except OSError:
        text = ""
    return parse(text)


def not_whole(folder, n: int, families, part: str = "hidden") -> str | None:
    """None when the run folder's output is whole, else the first cause (``whole`` or ``degraded``): its question
    lines number ``n`` and are all of ``part``; it has a total line and a ``families:`` line (equal to ``families``
    when that is given); the kept files number the sum of its calls; and no kept output is degraded."""
    parsed = read_parsed(folder)
    qs = parsed["questions"]
    kept = kept_files(folder)
    if (len(qs) != n or any(q["part"] != part for q in qs) or not parsed["total"] or parsed["families"] is None
            or (families is not None and parsed["families"] != families) or len(kept) != sum(q["calls"] for q in qs)):
        return "whole"
    if any(degraded(kept_result(f)) for f in kept):
        return "degraded"
    return None
