"""A stand-in ``codebase-memory-mcp`` for run 7's S25 cases (``test_w2_88_f1_codegraph.py``): the tool's answers, planted.

The case copies this file as ``codebase-memory-mcp`` into a folder that is first on the child's ``PATH`` (the first line becomes a
``#!`` line naming the python that runs the suite). ``gov.codeintel`` meets it three ways, all answered:

* ``codebase-memory-mcp config set ui_enabled false``: exit 0.
* ``codebase-memory-mcp cli --quiet --json <tool> <json arguments>`` (``index_repository``, ``list_projects``): one JSON envelope
  ``{"isError": false, "content": [{"type": "text", "text": "<json>"}]}`` on stdout, exit 0. ``index_repository`` keeps the folder it was
  given in ``$CBM_CACHE_DIR/staged.json`` and writes a small file beside it (the graph's bytes).
* ``codebase-memory-mcp`` with no argument: the MCP stdio server (``initialize``, ``notifications/initialized``, ``tools/call``), one JSON
  line in, one JSON line out, ``query_graph`` among the tools; it exits 0 when its input closes, as the real server does.

The graph it answers with is made from the files of the staged folder: each ``.c`` or ``.h`` file holds two ``Function`` nodes, and the
nodes are joined by ``CALLS`` edges in a chain. The settings are environment variables (the case's own):

* ``W2_88_F1_NODES`` and ``W2_88_F1_EDGES``: the counts a count query answers (``MATCH (n) RETURN count(n)``, ``MATCH (a)-[r]->(b) RETURN
  count(r)``: any query holding ``count(``; one holding ``-[`` or ``->`` counts the edges, any other the nodes). Unset: the size of the graph
  made from the staged files.
* ``W2_88_F1_READ``: what the whole-graph read of the edges (a query with no ``count(`` that holds ``-[`` or ``->``) does. ``ok`` (the
  default): answers the edges, paged by ``offset`` and ``max_rows``. ``cap``: answers as the real tool does over its cap, before any paging,
  ``isError: true`` with the text ``result exceeded 100k rows - use narrower filters or add LIMIT``. ``locked``: ``isError: true`` with
  the text ``database is locked`` (a failure that is not the cap).
* ``W2_88_F1_COUNTS``: ``ok`` (the default) or ``fail`` (a count query answers ``isError: true``, ``database is locked``).
* ``W2_88_F1_LOG``: a file to which every ``query_graph`` query is appended as a JSON line (``{"query": ..., "args": {...}}``).
"""

import json
import os
import sys
from pathlib import Path

CAP = 100_000
ERROR_CAP = "result exceeded 100k rows — use narrower filters or add LIMIT"
ERROR_LOCKED = "database is locked"


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


def graph():
    files = staged_files()
    nodes, edges = [], []
    for number, rel in enumerate(files):
        for part in (0, 1):
            name = f"fn_{number}_{part}"
            nodes.append([f"code.{name}", name, "Function", rel])
    for number in range(len(nodes) - 1):
        edges.append([nodes[number][0], "CALLS", nodes[number + 1][0]])
    return nodes, edges


def text_envelope(payload=None, error=None) -> dict:
    if error is not None:
        return {"isError": True, "content": [{"type": "text", "text": error}]}
    return {"isError": False, "content": [{"type": "text", "text": json.dumps(payload)}]}


def query_graph(args: dict) -> dict:
    query = str(args.get("query", ""))
    log = os.environ.get("W2_88_F1_LOG")
    if log:
        with open(log, "a", encoding="utf-8") as handle:
            handle.write(json.dumps({"query": query, "args": {k: v for k, v in args.items() if k != "query"}}) + "\n")
    nodes, edges = graph()
    about_edges = "-[" in query or "->" in query
    if "count(" in query:
        if os.environ.get("W2_88_F1_COUNTS", "ok") == "fail":
            return text_envelope(error=ERROR_LOCKED)
        given = os.environ.get("W2_88_F1_EDGES" if about_edges else "W2_88_F1_NODES")
        number = int(given) if given else len(edges if about_edges else nodes)
        return text_envelope({"columns": ["count"], "rows": [[number]], "total": 1, "has_more": False})
    rows = edges if about_edges else nodes
    if about_edges:
        mode = os.environ.get("W2_88_F1_READ", "ok")
        if mode == "cap":
            return text_envelope(error=ERROR_CAP)
        if mode == "locked":
            return text_envelope(error=ERROR_LOCKED)
    offset, limit = int(args.get("offset") or 0), int(args.get("max_rows") or CAP)
    page = rows[offset:offset + limit]
    return text_envelope({"columns": [], "rows": page, "total": len(rows), "has_more": offset + len(page) < len(rows)})


def call(tool: str, args: dict) -> dict:
    if tool == "index_repository":
        (cache() / "staged.json").write_text(json.dumps({"repo_path": args["repo_path"]}), encoding="utf-8")
        (cache() / "code.db").write_bytes(b"stand-in graph\n" * 64)
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
            result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "stand-in", "version": "0"}}
        elif method == "tools/call":
            params = message.get("params") or {}
            result = call(params.get("name", ""), params.get("arguments") or {})
        else:
            result = {}
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": identity, "result": result}) + "\n")
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
