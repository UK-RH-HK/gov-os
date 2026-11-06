"""The record route of a plain question: the records it names become start ids of the closure (W2-92; DEC-957, CAP-13).

``start_ids`` finds in a question the ids of records (``DEC-n``, ``CAP-n``, a ticket's id), a W2 id resolved to its
ticket, and record titles, so that the record closure joins the fusion without ``--ticket`` or ``--id``. Only ids and
titles the record store holds become start ids: a question that names no record gives none, and today's bundle. A
title is a register entry's in the store, or the ``title`` of the frontmatter that declares the record; it is found
whole, by word, in any case. Everything is sorted. It only reads.

The frontmatter titles come from the store's ``record_titles``, parsed once at the load (S6, DEC-1065 (4)); only a
store built before that table is read file by file, with the C loader where PyYAML has it.

``follow`` is S8 (DEC-1072 (1)): one bounded hop over the store's stated links (``stated_links``) from what the record
route or the closure reached; ``changers`` gives, for S9, each decision's changers by the links and the edges.
"""

from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path

import yaml

from gov.cli.errors import GovError
from gov.store import loader
from gov.store.loader import TITLES_TABLE, connect

_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)  # the C parser: about 9x faster on ~840 frontmatters
TOKEN = re.compile(r"[A-Za-z0-9]+(?:[-.][A-Za-z0-9]+)*")
W2_ID = re.compile(r"W2-[0-9]+[a-z]?")
TASK = "task"
# A ticket's W2 id stands in its frontmatter, never in the store (the ticket schema's wbs_id and external-ref).
_WBS = re.compile(r"^(?:wbs_id|external-ref):\s*['\"]?(W2-[0-9]+[a-z]?)['\"]?\s*$", re.MULTILINE)
_FRONTS: dict[tuple, object] = {}  # (file, size, time) -> its parsed frontmatter


def _front(root: Path, path: str) -> str:
    """The frontmatter text of the file at ``path``, empty when it has none or cannot be read."""
    try:
        text = (root / path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return text[4:text.find("\n---", 4)] if text.startswith("---\n") else ""


def _wbs_ids(root: Path, known: list[dict]) -> dict[str, str]:
    """``W2 id -> ticket id`` of every ticket of the store whose file names one."""
    tickets = {}
    for record in sorted(known, key=lambda record: record["id"]):
        if record["type"] == TASK:
            for wbs in sorted(set(_WBS.findall(_front(root, record["path"])))):
                tickets.setdefault(wbs, record["id"])
    return tickets


def _parsed(root: Path, path: str):
    """The parsed frontmatter of the file at ``path``, None when it cannot be read or parsed; parsed once a process
    while the file keeps its size and time (DEC-1006: every question reads every record's title)."""
    try:
        stat = (root / path).stat()
    except OSError:
        return None
    key = (os.path.abspath(root / path), stat.st_size, stat.st_mtime_ns)
    if key not in _FRONTS:
        try:
            _FRONTS[key] = yaml.load(_front(root, path), Loader=_LOADER)
        except yaml.YAMLError:
            _FRONTS[key] = None
    return _FRONTS[key]


def _titles(root: Path) -> dict[tuple[str, str], str] | None:
    """``(path, id) -> title`` of the store's records of files; None where the store has no such table (built before
    S6) or cannot be read, so the titles are read from the files as before."""
    try:
        connection = connect(root)
    except GovError:
        return None
    try:
        return {(path, rid): title for path, rid, title in connection.execute(
            f"SELECT path, id, title FROM {TITLES_TABLE}")}
    except sqlite3.Error:
        return None
    finally:
        connection.close()


def _title(root: Path, record: dict, titles: dict | None = None) -> str:
    """The record's title: a register entry's from the store, any other record's from its frontmatter, as the store
    keeps it in ``titles`` or, with none, as its file holds it."""
    if record.get("title"):
        return record["title"]
    if titles is not None:
        return titles.get((record["path"], record["id"]), "")
    front = _parsed(root, record["path"])
    if not isinstance(front, dict) or front.get("id") != record["id"] or not isinstance(front.get("title"), str):
        return ""
    return front["title"]


# S8 (DEC-1072 (1)): one hop over the stated links from the records the record route or the closure reached, so the
# records they state they are bound to join the closure route. The direction: a record to what it cites, stands under
# or records the work of (out); a decision to the decisions that change it (in: from the amended or superseded to its
# changer). The bound: at most FOLLOW_RECORDS records, each with at most its first FOLLOW_CHUNKS chunks, appended after
# today's closure chunks, so those keep their places in the fusion.
FOLLOW_RECORDS = 12
FOLLOW_CHUNKS = 2
OUT_LINKS = (loader.CITES, loader.UNDER, loader.OF_TASK)
CHANGE_LINKS = (loader.AMENDS, loader.SUPERSEDES)


def stated_links(root: Path) -> list[dict] | None:
    """The store's stated links (``loader.LINKS_TABLE``), sorted; None where the store holds no such table (built
    before them) or cannot be read."""
    try:
        connection = connect(root)
    except GovError:
        return None
    try:
        return [{"type": kind, "source": source, "target": target, "via": via}
                for kind, source, target, via in sorted(connection.execute(
                    f"SELECT type, source, target, via FROM {loader.LINKS_TABLE}"))]
    except sqlite3.Error:
        return None
    finally:
        connection.close()


def _natural(record_id: str) -> tuple:
    return tuple((0, int(part), "") if part.isdigit() else (1, 0, part) for part in re.split(r"(\d+)", record_id))


def changers(links: list[dict], edges: list[dict] = ()) -> dict[str, list[str]]:
    """``decision -> the decisions that change it``, newest first: every AMENDS and SUPERSEDES stated link to it, and
    every SUPERSEDES edge to it (``edges``, the store's)."""
    by: dict[str, set[str]] = {}
    for link in list(links) + [edge for edge in edges if edge["type"] == loader.SUPERSEDES]:
        if link["type"] in CHANGE_LINKS:
            by.setdefault(link["target"], set()).add(link["source"])
    return {target: sorted(sources, key=_natural, reverse=True) for target, sources in by.items()}


def follow(links: list[dict], start: list[str], reached: set[str], decisions: set[str]) -> dict:
    """One hop over ``links`` from ``reached`` (``start`` first): ``records``, the records it adds in order, at most
    FOLLOW_RECORDS; ``left``, how many more it found past the bound; ``changed_by``, each decision in reach (reached or
    added) that a link says is amended or superseded, with every decision that changes it, newest first.

    The order under the bound: the changers of the start records; what the start records cite, stand under or record
    the work of; the changers of what that added and of the other reached decisions; what the other reached records
    cite or stand under. Within each, by source and then by target, newest changer first. Deterministic."""
    out, changed_by = {}, changers(links)
    for link in links:
        if link["type"] in OUT_LINKS:
            out.setdefault(link["source"], set()).add(link["target"])
    first = sorted(set(start) & reached, key=_natural)
    rest = sorted(reached - set(first), key=_natural)

    def changed(ids):
        return [changer for rid in ids for changer in changed_by.get(rid, ())]

    def cited(ids):
        return [target for rid in ids for target in sorted(out.get(rid, ()), key=_natural)]

    hop, found = cited(first), []
    for rid in changed(first) + hop + changed(sorted(set(hop), key=_natural) + rest) + cited(rest):
        if rid not in reached and rid not in found:
            found.append(rid)
    added = found[:FOLLOW_RECORDS]
    reach = (reached | set(added)) & decisions
    return {"records": added, "left": len(found) - len(added),
            "changed_by": {rid: changed_by[rid] for rid in sorted(reach, key=_natural) if rid in changed_by}}


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
    titles = _titles(Path(root)) if known else None
    for record in known:
        title = " ".join(_title(Path(root), record, titles).split()).casefold()
        if title and title in words and re.search(rf"(?<!\w){re.escape(title)}(?!\w)", words):
            found.add(record["id"])
    return sorted(found)
