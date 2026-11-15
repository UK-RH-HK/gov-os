"""W2-88 run 8b (S28): a stand-in ``codebase-memory-mcp`` that answers as the lead's probes found the real tool does.

Not a test module: ``main()`` is the server a test plants first on ``PATH`` (``plant``). It speaks MCP over stdio and
answers ``query_graph`` from the graph in ``stand-in.json`` beside the planted binary, as items 13-14 of the run 8b
interface say the real tool does: it refuses a query whose whole answer is over 100,000 rows (before its own paging);
it refuses ``IN [...]``, ``STARTS WITH`` and a function in ``WHERE`` other than ``coalesce``; it answers a string
``>`` in ``WHERE`` with 0 rows, silently; it cuts a named answer short, silently (``cut``). Every query is logged.

The graph: ``files`` {source path: {link type: links}}; ``bare`` {label: {link type: links}} (links out of nodes with no
string path); ``labels`` {label: {path: nodes}} (the path ``{}`` stands for a node whose path is no string);
``holders`` {label: {holder path: [file paths]}} (``CONTAINS_FILE``; holder path ``{}`` for a bare holder); ``cut``
{answer: rows} with answers named ``links:<path>``, ``links:<path>:<type>``, ``list:<label>``, ``holder:<path>``,
``nodes:<label>``; ``fail``: a text whose query the tool fails with ``boom``.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

CAP = 100_000
CAP_TEXT = "result exceeded 100k rows — use narrower filters or add LIMIT"
LINK = "id(r), a.qualified_name, type(r), b.qualified_name"
NODE = "n.qualified_name, n.name, n.label, n.file_path"
ALLOWED = {"coalesce", "substring", "replace", "left", "right"}


def plant(bin_dir: Path, graph: dict) -> Path:
    """Plant the stand-in first on a ``PATH`` folder ``bin_dir`` with ``graph``; return its query log."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    place = bin_dir / "codebase-memory-mcp"
    place.write_text(f"#!{sys.executable}\nimport os, runpy\nos.environ['W2_88_STAND_IN'] = {str(bin_dir)!r}\n"
                     f"runpy.run_path({str(Path(__file__))!r}, run_name='__main__')\n")
    place.chmod(0o755)
    (bin_dir / "stand-in.json").write_text(json.dumps(graph))
    log = bin_dir / "queries.log"
    log.write_text("")
    return log


class Graph:
    def __init__(self, config: dict) -> None:
        self.files = config.get("files", {})
        self.bare = config.get("bare", {})
        self.labels = config.get("labels", {})
        self.holders = config.get("holders", {})
        self.cut = config.get("cut", {})
        self.fail = config.get("fail")

    def links(self, path: str, kind: str | None, by_label: bool = False) -> list[list]:
        groups = (self.bare if by_label else self.files).get(path, {})
        return [[f"{path}|{t}|{i}", f"{path}::s{i % 50}", t, f"tgt{i % 97}"]
                for t, n in sorted(groups.items()) if kind in (None, t) for i in range(n)]

    def types(self) -> dict[str, int]:
        found: dict[str, int] = {}
        for groups in [*self.files.values(), *self.bare.values()]:
            for kind, n in groups.items():
                found[kind] = found.get(kind, 0) + n
        return found

    def label_paths(self, label: str) -> list:
        return [({} if path == "{}" else path) for path, n in self.labels.get(label, {}).items() for _ in range(n)]

    def answer(self, query: str):
        """``(rows, None)``, or ``(None, error text)`` where the tool refuses."""
        if self.fail and self.fail in query:
            return None, "boom"
        if " IN " in query or "STARTS WITH" in query:
            return None, "unsupported operator in WHERE"
        where = query.split(" WHERE ", 1)[1].split(" RETURN ")[0] if " WHERE " in query else ""
        for name in re.findall(r"(\w+)\(", where):
            if name not in ALLOWED:
                return None, f"unsupported function '{name}' in WHERE"
        if re.search(r"\.file_path\s*[<>]", where):
            return [], None  # a string comparison answers 0 rows, silently
        rows, cut = self.rows(query)
        if rows is None:
            return None, f"unsupported query: {query}"
        if len(rows) > CAP:
            return None, CAP_TEXT
        if cut is not None and cut in self.cut:
            rows = rows[: self.cut[cut]]
        return rows, None

    def rows(self, query: str):
        def count(rows):
            return [[str(len(rows))]]

        if query == "MATCH (a)-[r]->(b) RETURN type(r), count(r)":
            return [[k, str(n)] for k, n in self.types().items()], None
        if query == "MATCH (a)-[r]->(b) RETURN count(r)":
            return [[str(sum(self.types().values()))]], None
        if query == "MATCH (n) RETURN n.label, count(n)":
            return [[label, str(sum(paths.values()))] for label, paths in self.labels.items()], None
        if query == "MATCH (a)-[r:CONTAINS_FILE]->(n:File) RETURN a.label, count(r)":
            return [[label, str(sum(len(files) for files in held.values()))] for label, held in self.holders.items()], None
        m = re.fullmatch(r'MATCH \(a\)-\[r(?::(\w+))?\]->\(b\) WHERE a\.file_path = "([^"]*)" RETURN (.+)', query)
        if m:
            kind, path, ret = m.groups()
            rows = self.links(path, kind)
            if ret == "count(r)":
                return count(rows), None
            if ret == "type(r), count(r)" and kind is None:
                return [[k, str(n)] for k, n in sorted(self.files.get(path, {}).items())], None
            if ret == LINK:
                return rows, f"links:{path}" + (f":{kind}" if kind else "")
            return None, None
        m = re.fullmatch(r"MATCH \(a:(\w+)\)-\[r(?::(\w+))?\]->\(b\) RETURN (.+)", query)
        if m:
            label, kind, ret = m.groups()
            rows = self.links(label, kind, by_label=True)
            return (count(rows), None) if ret == "count(r)" else ((rows, f"bare:{label}") if ret == LINK else (None, None))
        m = re.fullmatch(r'MATCH \(n:(\w+)\)(?: WHERE n\.file_path = "([^"]*)")? RETURN (.+)', query)
        if m:
            label, path, ret = m.groups()
            paths = [p for p in self.label_paths(label) if path is None or p == path]
            if ret == "count(n)":
                return count(paths), None
            if ret == "n.file_path":
                return [[p] for p in paths], f"list:{label}"
            if ret == NODE:
                return [[f"{label}:{p}:{i}", f"n{i}", label, p] for i, p in enumerate(paths)], \
                    (f"nodes:{label}" if path is None else f"nodes:{label}:{path}")
            return None, None
        m = re.fullmatch(r'MATCH \((f|b):(\w+)\)-\[r:CONTAINS_FILE\]->\(n:File\)(?: WHERE f\.file_path = "([^"]*)")? '
                         r"RETURN (count\(n\)|n\.file_path)", query)
        if m:
            alias, label, path, ret = m.groups()
            held = self.holders.get(label, {})
            if (alias == "f") != (path is not None):
                return None, None
            files = [f for key, fs in held.items() if path is None or key == path for f in fs]
            return (count(files), None) if ret == "count(n)" else ([[f] for f in files], f"holder:{path or label}")
        if query == "MATCH (a)-[r]->(b) RETURN a.qualified_name, type(r), b.qualified_name":
            return [row[1:] for path in self.files for row in self.links(path, None)], None
        return None, None


def main() -> None:
    here = Path(os.environ["W2_88_STAND_IN"])
    if sys.argv[1:2] == ["config"]:
        sys.exit(0)
    graph = Graph(json.loads((here / "stand-in.json").read_text()))
    for line in sys.stdin:
        if not line.startswith("{"):
            continue
        message = json.loads(line)
        if "id" not in message:
            continue
        if message["method"] == "initialize":
            result = {"protocolVersion": "2024-11-05", "capabilities": {}, "serverInfo": {"name": "stand-in"}}
        else:
            arguments = message["params"]["arguments"]
            query = arguments.get("query", "")
            with open(here / "queries.log", "a") as log:
                log.write(query + "\n")
            rows, error = graph.answer(query)
            if rows is None:
                result = {"content": [{"type": "text", "text": error}], "isError": True}
            else:
                at, most = arguments.get("offset", 0), arguments.get("max_rows", 1000)
                text = json.dumps({"rows": rows[at:at + most], "has_more": at + most < len(rows)})
                result = {"content": [{"type": "text", "text": text}], "isError": False}
        print(json.dumps({"jsonrpc": "2.0", "id": message["id"], "result": result}), flush=True)


if __name__ == "__main__":
    main()
