"""A stand-in ``codebase-memory-mcp`` for the S25 cases (``test_w2_88_f1_codegraph.py``): the tool's answers, planted.

The case copies this file as ``codebase-memory-mcp`` into a folder that is first on the child's ``PATH`` (the first line becomes a
``#!`` line naming the python that runs the suite). ``gov.codeintel`` meets it three ways, all answered:

* ``codebase-memory-mcp config set ui_enabled false``: exit 0.
* ``codebase-memory-mcp cli --quiet --json <tool> <json arguments>`` (``index_repository``, ``list_projects``): one JSON envelope
  ``{"isError": false, "content": [{"type": "text", "text": "<json>"}]}`` on stdout, exit 0. ``index_repository`` keeps the folder it was
  given in ``$CBM_CACHE_DIR/staged.json`` and writes a small file beside it (the graph's bytes).
* ``codebase-memory-mcp`` with no argument: the MCP stdio server (``initialize``, ``notifications/initialized``, ``tools/call``), one JSON
  line in, one JSON line out, ``query_graph`` among the tools; it exits 0 when its input closes, as the real server does.

Run 8 (DEC-1183, package 2 (a); the lead's probe of the real tool on redis, run 8 interface item 7): ``query_graph`` behaves as the real tool
was seen to:

* **Count queries** (any query holding ``count(``) answer in full: ``MATCH (a)-[r]->(b) RETURN type(r), count(r)`` one row per edge type;
  ``MATCH (n) RETURN n.label, count(n)`` one row per node label; ``count(r)`` / ``count(n)`` one row (the edges or nodes, of the type or label
  the match names if it names one).
* **The typed edge match** (``MATCH (a)-[r:TYPE]->(b) RETURN a.qualified_name, type(r), b.qualified_name``) and **the label node match**
  (``MATCH (n:Label) RETURN n.qualified_name, n.name, n.label, n.file_path``) answer every row of that type or label, paged by the tool's
  ``offset`` and ``max_rows``. With no type or label named, the whole edges or nodes.
* **The cap**: a query whose result would exceed 100,000 rows is refused before any paging, ``isError: true`` with the real tool's text
  ``result exceeded 100k rows — use narrower filters or add LIMIT``.
* **``SKIP``/``LIMIT`` is not a sound page**: a query with ``SKIP`` or ``LIMIT`` answers short (about two thirds of the rows asked, as the probe
  saw 32,943 rows for ``LIMIT 50000``), so a reader that pages by them gets a partial count.

The graph it answers with, by the settings (environment variables, the case's own):

* ``W2_88_F1_TYPES`` (``USAGE=60000,CALLS=50000``) and ``W2_88_F1_LABELS`` (``Function=60000,Variable=45000``): a generated graph of
  that many edges per type and nodes per label (labels default to ``Function=1000`` when only types are given). Every node's file is one of
  the staged ``.c``/``.h`` files; every edge is unique (no two share source, type and target). Unset: the graph made from the staged files
  (each ``.c`` or ``.h`` file two ``Function`` nodes, joined by ``CALLS`` edges in a chain).
* ``W2_88_F1_SHORT`` (``CALLS=7``): the typed match of that edge type (or the label match of that label) answers that many rows fewer than
  its count says (a read that ends short).
* ``W2_88_F1_NODES`` and ``W2_88_F1_EDGES`` (run 7): the totals the count queries answer in place of the graph's (grouped counts then answer
  one group, ``Function`` or ``CALLS``, holding the total).
* ``W2_88_F1_READ`` (run 7): what a read of edges that is not a count does. ``ok`` (the default): answers as above. ``cap``: refused with the
  cap's text whatever its size. ``locked``: ``isError: true`` with the text ``database is locked`` (a failure that is not the cap).
* ``W2_88_F1_COUNTS``: ``ok`` (the default) or ``fail`` (a count query answers ``isError: true``, ``database is locked``).
* ``W2_88_F1_LOG``: a file to which every ``query_graph`` query is appended as a JSON line (``{"query": ..., "args": {...}, "rows": n}``,
  ``rows`` the result's size before paging, or ``"error"``).
"""

import functools
import json
import os
import re
import sys
from pathlib import Path

CAP = 100_000
ERROR_CAP = "result exceeded 100k rows — use narrower filters or add LIMIT"
ERROR_LOCKED = "database is locked"
SHORT_SHARE = 0.66                 # the share of the rows asked a SKIP/LIMIT query answers (the probe: 32,943 of 50,000)
EDGE_COLUMNS = ("source", "type", "target")
NODE_COLUMNS = ("qualified_name", "name", "label", "file_path")


def cache() -> Path:
    folder = Path(os.environ.get("CBM_CACHE_DIR") or ".")
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def staged_files() -> list:
    note = cache() / "staged.json"
    if not note.is_file():
        return []
    folder = Path(json.loads(note.read_text(encoding="utf-8"))["repo_path"])
    return sorted(p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file() and p.suffix in (".c", ".h"))


def spec(name: str) -> list:
    """``A=1,B=2`` as ``[("A", 1), ("B", 2)]``."""
    text = os.environ.get(name, "").strip()
    return [(part.split("=")[0].strip(), int(part.split("=")[1])) for part in text.split(",") if "=" in part]


@functools.lru_cache(maxsize=None)
def graph():
    """``(nodes, edges)``: nodes ``[qualified_name, name, label, file_path]``, edges ``[source, type, target]``."""
    files = staged_files() or ["src/server.c"]
    types = spec("W2_88_F1_TYPES")
    if not types and not os.environ.get("W2_88_F1_LABELS", "").strip():
        nodes, edges = [], []
        for number, rel in enumerate(staged_files()):
            for part in (0, 1):
                name = f"fn_{number}_{part}"
                nodes.append([f"code.{name}", name, "Function", rel])
        for number in range(len(nodes) - 1):
            edges.append([nodes[number][0], "CALLS", nodes[number + 1][0]])
        return nodes, edges
    labels = spec("W2_88_F1_LABELS") or [("Function", 1000)]
    nodes = []
    for label, count in labels:
        for number in range(count):
            name = f"{label.lower()}_{number}"
            nodes.append([f"code.{name}", name, label, files[number % len(files)]])
    total, edges = len(nodes), []
    for kind, count in types:
        for number in range(count):
            source = number % total
            target = (source + 1 + number // total) % total
            edges.append([nodes[source][0], kind, nodes[target][0]])
    return nodes, edges


@functools.lru_cache(maxsize=None)
def grouped(about_edges: bool) -> dict:
    """The count per edge type or node label, as the count queries answer it."""
    nodes, edges = graph()
    given = os.environ.get("W2_88_F1_EDGES" if about_edges else "W2_88_F1_NODES", "").strip()
    if given:
        return {"CALLS" if about_edges else "Function": int(given)}
    counts = {}
    for row in edges if about_edges else nodes:
        key = row[1] if about_edges else row[2]
        counts[key] = counts.get(key, 0) + 1
    return counts


def text_envelope(payload=None, error=None) -> dict:
    if error is not None:
        return {"isError": True, "content": [{"type": "text", "text": error}]}
    return {"isError": False, "content": [{"type": "text", "text": json.dumps(payload)}]}


def returned(query: str) -> list:
    """The items of the query's ``RETURN`` clause (aliases, ``ORDER BY``, ``SKIP`` and ``LIMIT`` taken off)."""
    found = re.search(r"\breturn\b(.*)$", query, re.I | re.S)
    if not found:
        return []
    clause = re.split(r"\b(?:order\s+by|skip|limit)\b", found.group(1), maxsplit=1, flags=re.I)[0]
    items = [re.sub(r"\s+as\s+\w+\s*$", "", item.strip(), flags=re.I).strip() for item in clause.split(",")]
    return [item for item in items if item]


def named(query: str, about_edges: bool):
    """The edge type or node label the match names (``-[r:T]->``, ``(n:L)``, ``WHERE type(r) = 'T'``, ``WHERE n.label = 'L'``), or None."""
    if about_edges:
        found = (re.search(r"\[\s*\w*\s*:\s*`?(\w+)`?", query)
                 or re.search(r"type\(\s*\w+\s*\)\s*=\s*['\"](\w+)['\"]", query))
    else:
        found = (re.search(r"\(\s*\w*\s*:\s*`?(\w+)`?", query)
                 or re.search(r"\w+\.label\s*=\s*['\"](\w+)['\"]", query)
                 or re.search(r"['\"](\w+)['\"]\s+in\s+labels\(", query, re.I))
    return found.group(1) if found else None


def column(item: str, about_edges: bool, source_var: str):
    """The index in the row of a ``RETURN`` item, or None for one the stand-in does not know."""
    low = item.lower().replace(" ", "")
    if about_edges:
        if low.startswith("type("):
            return 1
        if low.endswith(".qualified_name") or low.endswith(".name"):
            return 0 if low.split(".")[0] == source_var.lower() else 2
        return None
    for index, field in enumerate(NODE_COLUMNS):
        if low.endswith("." + field):
            return index
    if low.startswith("labels("):
        return 2
    return None


_ANSWERS = {}


def result(query: str, about_edges: bool):
    """The rows a query's result holds before the tool's paging, or an error text."""
    if query in _ANSWERS:
        return _ANSWERS[query]
    nodes, edges = graph()
    kind = named(query, about_edges)
    position = 1 if about_edges else 2
    rows = [row for row in (edges if about_edges else nodes) if kind is None or row[position] == kind]
    short = dict(spec("W2_88_F1_SHORT"))
    if kind is not None and kind in short:
        rows = rows[:max(0, len(rows) - short[kind])]
    skip = re.search(r"\bskip\s+(\d+)", query, re.I)
    limit = re.search(r"\blimit\s+(\d+)", query, re.I)
    if skip or limit:
        start = int(skip.group(1)) if skip else 0
        asked = rows[start:start + int(limit.group(1))] if limit else rows[start:]
        rows = asked[:int(len(asked) * SHORT_SHARE)]
    if len(rows) > CAP:
        answer = ERROR_CAP
    else:
        source = re.search(r"\(\s*(\w+)", query)
        items = returned(query)
        columns = [column(item, about_edges, source.group(1) if source else "a") for item in items]
        standard = list(range(len(EDGE_COLUMNS if about_edges else NODE_COLUMNS)))
        if items and None not in columns and columns != standard:
            rows = [[row[index] for index in columns] for row in rows]
        answer = rows
    _ANSWERS[query] = answer
    return answer


def counted(query: str, about_edges: bool):
    counts = grouped(about_edges)
    kind = named(query, about_edges)
    if kind is not None:
        counts = {kind: counts.get(kind, 0)}
    items = returned(query)
    by_group = any(("type(" in item.lower() if about_edges else "label" in item.lower()) and "count(" not in item.lower() for item in items)
    if not by_group:
        return [[sum(counts.values())]]
    rows = []
    for key, number in counts.items():
        rows.append([number if "count(" in item.lower() else key for item in items])
    return rows


def log(query: str, args: dict, size) -> None:
    where = os.environ.get("W2_88_F1_LOG")
    if where:
        with open(where, "a", encoding="utf-8") as handle:
            handle.write(json.dumps({"query": query, "args": {k: v for k, v in args.items() if k != "query"}, "rows": size}) + "\n")


def query_graph(args: dict) -> dict:
    query = str(args.get("query", ""))
    about_edges = "-[" in query or "->" in query or "<-" in query
    if "count(" in query.lower():
        if os.environ.get("W2_88_F1_COUNTS", "ok") == "fail":
            log(query, args, "error")
            return text_envelope(error=ERROR_LOCKED)
        rows = counted(query, about_edges)
        log(query, args, len(rows))
        return text_envelope({"columns": returned(query), "rows": rows, "total": len(rows), "has_more": False})
    if about_edges:
        mode = os.environ.get("W2_88_F1_READ", "ok")
        if mode in ("cap", "locked"):
            log(query, args, "error")
            return text_envelope(error=ERROR_CAP if mode == "cap" else ERROR_LOCKED)
    rows = result(query, about_edges)
    if isinstance(rows, str):
        log(query, args, "error")
        return text_envelope(error=rows)
    offset, limit = int(args.get("offset") or 0), int(args.get("max_rows") or CAP)
    page = rows[offset:offset + limit]
    log(query, args, len(rows))
    return text_envelope({"columns": returned(query), "rows": page, "total": len(rows), "has_more": offset + len(page) < len(rows)})


def call(tool: str, args: dict) -> dict:
    if tool == "index_repository":
        (cache() / "staged.json").write_text(json.dumps({"repo_path": args["repo_path"]}), encoding="utf-8")
        (cache() / "code.db").write_bytes(b"stand-in graph\n" * 64)
        graph.cache_clear()
        grouped.cache_clear()
        nodes, edges = graph()
        return text_envelope({"status": "indexed", "project": args.get("name", "code"), "nodes": len(nodes), "edges": len(edges)})
    if tool == "list_projects":
        nodes, edges = graph()
        return text_envelope({"projects": [{"name": "code", "nodes": len(nodes), "edges": len(edges)}]})
    if tool == "query_graph":
        return query_graph(args)
    return text_envelope(error=f"unknown tool {tool}")


def serve() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line.startswith("{"):
            continue
        message = json.loads(line)
        method, identity = message.get("method", ""), message.get("id")
        if identity is None:
            continue
        if method == "initialize":
            result_ = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "stand-in", "version": "0"}}
        elif method == "tools/call":
            params = message.get("params") or {}
            result_ = call(params.get("name", ""), params.get("arguments") or {})
        else:
            result_ = {}
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": identity, "result": result_}) + "\n")
        sys.stdout.flush()
    return 0


def main(argv: list) -> int:
    if argv[:1] == ["config"]:
        return 0
    if argv[:1] == ["cli"]:
        rest = [a for a in argv[1:] if not a.startswith("--")]
        envelope = call(rest[0], json.loads(rest[1]) if len(rest) > 1 else {})
        sys.stdout.write(json.dumps(envelope) + "\n")
        return 0
    return serve()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
