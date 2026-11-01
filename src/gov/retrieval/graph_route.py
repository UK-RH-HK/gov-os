"""The record route of a plain question: the records it names become start ids of the closure (W2-92; DEC-957, CAP-13).

``start_ids`` finds in a question the ids of records (``DEC-n``, ``CAP-n``, a ticket's id), a W2 id resolved to its
ticket, and record titles, so that the record closure joins the fusion without ``--ticket`` or ``--id``. Only ids and
titles the record store holds become start ids: a question that names no record gives none, and today's bundle. A
title is found whole, by word, in any case. Everything is sorted. It only reads.
"""

from __future__ import annotations

import re
from pathlib import Path

TOKEN = re.compile(r"[A-Za-z0-9]+(?:[-.][A-Za-z0-9]+)*")
W2_ID = re.compile(r"W2-[0-9]+[a-z]?")
TASK = "task"
# A ticket's W2 id stands in its frontmatter, never in the store (the ticket schema's wbs_id and external-ref).
_WBS = re.compile(r"^(?:wbs_id|external-ref):\s*['\"]?(W2-[0-9]+[a-z]?)['\"]?\s*$", re.MULTILINE)


def _wbs_ids(root: Path, known: list[dict]) -> dict[str, str]:
    """``W2 id -> ticket id`` of every ticket of the store whose file names one."""
    tickets = {}
    for record in sorted(known, key=lambda record: record["id"]):
        if record["type"] != TASK:
            continue
        try:
            text = (root / record["path"]).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        front = text[4:text.find("\n---", 4)] if text.startswith("---\n") else ""
        for wbs in sorted(set(_WBS.findall(front))):
            tickets.setdefault(wbs, record["id"])
    return tickets


def _named(query: str) -> set[str]:
    """Every run of hyphen-joined parts of the question's words: ``W2-92-tests`` names ``W2-92`` too."""
    named = set()
    for token in TOKEN.findall(query):
        parts = token.split("-")
        named |= {"-".join(parts[i:j]) for i in range(len(parts)) for j in range(i + 2, len(parts) + 1)}
    return named


def start_ids(root: Path, query: str, known: list[dict]) -> list[str]:
    """The ids of the records ``query`` names by id, W2 id or title, among the records ``known`` (the store's)."""
    ids, named = {record["id"] for record in known}, _named(query)
    found = named & ids
    w2 = {token for token in named - ids if W2_ID.fullmatch(token)}
    if w2:
        tickets = _wbs_ids(Path(root), known)
        found |= {tickets[token] for token in w2 if token in tickets}
    words = " ".join(query.split()).casefold()
    for record in known:
        title = " ".join((record.get("title") or "").split()).casefold()
        if title and re.search(rf"(?<!\w){re.escape(title)}(?!\w)", words):
            found.add(record["id"])
    return sorted(found)
