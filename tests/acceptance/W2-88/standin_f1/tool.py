"""A stand-in ``codebase-memory-mcp`` for the S25 and S28 cases (``test_w2_88_f1_codegraph.py``, ``test_w2_88_s28_pieces.py``).

The case copies this file as ``codebase-memory-mcp`` into a folder that is first on the child's ``PATH`` (the first line becomes a
``#!`` line naming the python that runs the suite). ``gov.codeintel`` meets it three ways, all answered:

* ``codebase-memory-mcp config set ui_enabled false``: exit 0.
* ``codebase-memory-mcp cli --quiet --json <tool> <json arguments>`` (``index_repository``, ``list_projects``): one JSON envelope
  ``{"isError": false, "content": [{"type": "text", "text": "<json>"}]}`` on stdout, exit 0. ``index_repository`` keeps the folder it was
  given in ``$CBM_CACHE_DIR/staged.json`` and writes a small file beside it (the graph's bytes).
* ``codebase-memory-mcp`` with no argument: the MCP stdio server (``initialize``, ``notifications/initialized``, ``tools/call``), one JSON
  line in, one JSON line out, ``query_graph`` among the tools; it exits 0 when its input closes, as the real server does.

Run 8b (DEC-1185, S28; the run 8b interface items 13, 14, 20 and 23, the lead's probes of the real tool on redis): ``query_graph`` is a small
Cypher reader over a generated graph and behaves as the real tool was seen to:

* **Sound:** ``count(r)``, ``count(n)``, counts grouped by ``type(r)`` or by a node's ``label``; ``MATCH (n:<Label>) RETURN n.file_path``
  (any node property: ``qualified_name``, ``name``, ``label``, ``file_path``); typed matches ``-[r:T]->``; source and target labels
  ``(a:<Label>)``; the equality filter ``WHERE v.file_path = "<path>"`` (and ``v.label = "<L>"``), ``AND``-joined;
  ``coalesce(v.file_path, "") = ""``; ``id(r)`` as a column (unique per link, stable while the link's file is unchanged);
  ``DISTINCT``; ``ORDER BY`` on returned columns or aliases; the tool's own paging by ``offset`` and ``max_rows``.
* **Refused** (``isError: true``): any query whose result exceeds 100,000 rows, before the tool's paging, with the real tool's text
  ``result exceeded 100k rows — use narrower filters or add LIMIT``; ``IN`` and ``STARTS WITH``; a function in ``WHERE`` other than
  ``coalesce, substring, replace, left, right`` (``unsupported function 'type' in WHERE (supported: coalesce, substring, replace, left,
  right)``); a count grouped by a file path; a pattern, condition or return item it does not know.
* **Not sound:** a string comparison in ``WHERE`` (``>``, ``<``, ``>=``, ``<=``) answers **0 rows**, silently; ``SKIP``/``LIMIT`` answers
  short (two thirds of the rows asked, as run 8's probe saw); **the size cut**: a piece the plan names (``cut``) answers fewer rows than its
  count, with ``has_more`` false.

The graph (generated rows, never a real index), from the staged files and the plan (``W2_88_F1_PLAN``, a JSON file; absent, the defaults):

* a ``Project`` node and a ``Branch`` node, whose ``file_path`` is ``{}`` (not a string, as on redis); a ``Folder`` node per folder of the
  staged files (its path the folder's); a ``File`` node per staged file; ``functions`` (default 2) ``Function`` nodes per ``.c``/``.h``
  file (``labels`` adds nodes of other labels per code file, e.g. ``{"Method": 3}``); ``builtins`` ``Class`` nodes whose path is
  ``<python-builtins>``.
* links: ``Project -HAS_BRANCH-> Branch``; ``Branch -CONTAINS_FILE->`` each root file and ``-CONTAINS_FOLDER->`` each top folder; ``Folder
  -CONTAINS_FILE->`` its files and ``-CONTAINS_FOLDER->`` its subfolders; ``File -DEFINES->`` each of its code nodes; and, per code file,
  ``links[<path>]`` (else ``default_links``, ``{"CALLS": 1}``) links by type from its code nodes to code nodes (each source, type and
  target once); ``builtin_links`` (``{"BUILTIN_USAGE": 12}``, a type of its own so a case's type totals are its plan's) out of the ``<python-builtins>`` nodes.
* ``cut``: a list of ``{"piece": ..., "by": n}``: ``file`` (a links read filtered by a source file, untyped), ``file-type`` (the same with
  ``"type"``), ``list`` (``MATCH (n:<label>) RETURN ...file_path``, unfiltered), ``folder`` (a ``CONTAINS_FILE`` read filtered by a
  Folder's path), ``label-links`` (a links read by source label, unfiltered): that read answers ``by`` rows fewer than its count.
* ``named`` and ``calls`` (run 8b item 25, R8-2 (a): a link's end moving to another file): ``named`` ``{"<path>": ["foo", ...]}`` adds a
  ``Function`` node per name in that code file, its qualified name ``code.<path's module>.<name>`` (``code.src.server.foo``), so a
  function moved to another file, or renamed, is a node of a new qualified name; ``calls`` ``[{"key", "file", "source", "type",
  "target"}]`` adds a link from the named node ``source`` of ``file`` to the named node ``target`` wherever it is defined, its ``id(r)``
  from ``key`` alone, so it keeps its ``id(r)`` while its target moves. Named nodes get their ``DEFINES`` link and no other generated link.
* ``read``: ``ok`` or ``locked`` (a links read, a query returning ``id(r)``, ``type(r)`` or a qualified name over a link match, not a
  count, answers ``isError: true``, ``database is locked``); ``counts``: ``ok`` or ``fail`` (every count query answers that error).
* ``W2_88_F1_LOG``: every ``query_graph`` call is appended as a JSON line ``{"query", "offset", "max_rows", "rows": the result's size
  before paging or "error", "error", "served": the rows of this answer, "links": true for a links read, "file": the source file the
  equality filter names, "type": the typed match's type, "ids": the id(r) values served}``.
"""

import functools
import hashlib
import json
import os
import re
import sys
from pathlib import Path

CAP = 100_000
ERROR_CAP = "result exceeded 100k rows — use narrower filters or add LIMIT"
ERROR_LOCKED = "database is locked"
WHERE_FUNCTIONS = ("coalesce", "substring", "replace", "left", "right")
SHORT_SHARE = 0.66
CODE_SUFFIXES = (".c", ".h")
BUILTINS = "<python-builtins>"
PROPS = ("qualified_name", "name", "label", "file_path")


class Refused(Exception):
    pass


def cache() -> Path:
    folder = Path(os.environ.get("CBM_CACHE_DIR") or ".")
    folder.mkdir(parents=True, exist_ok=True)
    return folder


@functools.lru_cache(maxsize=None)
def plan() -> dict:
    where = os.environ.get("W2_88_F1_PLAN", "").strip()
    return json.loads(Path(where).read_text(encoding="utf-8")) if where and Path(where).is_file() else {}


def staged() -> tuple:
    """``(folder, [rel...])``: the folder the tool indexed and its files, sorted."""
    note = cache() / "staged.json"
    if not note.is_file():
        return None, []
    folder = Path(json.loads(note.read_text(encoding="utf-8"))["repo_path"])
    return folder, sorted(p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file())


def link_id(*parts) -> int:
    return int(hashlib.sha1("\0".join(str(p) for p in parts).encode()).hexdigest()[:13], 16)


@functools.lru_cache(maxsize=None)
def graph():
    """``(nodes, links)``: a node ``{"qualified_name", "name", "label", "file_path"}``; a link ``(id, source, type, target)`` (indexes)."""
    folder, files = staged()
    settings = plan()
    nodes, links = [], []

    def node(label, name, path):
        nodes.append({"qualified_name": f"code.{name}", "name": name.rsplit(".", 1)[-1], "label": label, "file_path": path})
        return len(nodes) - 1

    def link(source, kind, target, *key):
        links.append((link_id(*key), source, kind, target))

    project = node("Project", "code", {})
    branch = node("Branch", "code.main", {})
    link(project, "HAS_BRANCH", branch, "project", "branch")
    folders = sorted({str(Path(rel).parents[i].as_posix()) for rel in files for i in range(len(Path(rel).parents) - 1)})
    at = {name: node("Folder", f"folder.{name}", name) for name in folders}
    for name in folders:
        parent = str(Path(name).parent.as_posix())
        link(at[parent] if parent in at else branch, "CONTAINS_FOLDER", at[name], "folder", name)
    file_node = {}
    for rel in files:
        file_node[rel] = node("File", f"file.{rel}", rel)
        parent = str(Path(rel).parent.as_posix())
        link(at[parent] if parent in at else branch, "CONTAINS_FILE", file_node[rel], "contains", rel)
    code_files = [rel for rel in files if rel.endswith(CODE_SUFFIXES)]
    extra_labels = {"Function": int(settings.get("functions", 2)), **{k: int(v) for k, v in (settings.get("labels") or {}).items()}}
    named = settings.get("named") or {}
    by_file, targets, named_at = {}, [], {}
    for number, rel in enumerate(code_files):
        own = []
        for label, count in extra_labels.items():
            for index in range(count):
                own.append(node(label, f"{label.lower()}_{number}_{index}", rel))
        by_file[rel] = own
        targets += own
        module = rel.rsplit(".", 1)[0].replace("/", ".")
        own_named = []
        for name in named.get(rel, []):
            named_at[(rel, name)] = node("Function", f"{module}.{name}", rel)
            own_named.append(named_at[(rel, name)])
        digest = hashlib.sha1((folder / rel).read_bytes()).hexdigest() if folder else ""
        for index, target in enumerate(own + own_named):
            link(file_node[rel], "DEFINES", target, "defines", rel, digest, index)
    builtin_nodes = [node("Class", f"builtins.class_{i}", BUILTINS) for i in range(int(settings.get("builtins", 3)))]
    targets = targets or builtin_nodes
    default = settings.get("default_links", {"CALLS": 1})

    def spread(sources, spec, key, digest):
        for kind, count in spec.items():
            for ordinal in range(int(count)):
                source = sources[ordinal % len(sources)]
                target = targets[(ordinal // len(sources)) % len(targets)]
                link(source, kind, target, key, digest, kind, ordinal)

    for rel in code_files:
        digest = hashlib.sha1((folder / rel).read_bytes()).hexdigest() if folder else ""
        spread(by_file[rel], (settings.get("links") or {}).get(rel, default), rel, digest)
    defined = {name: index for (_rel, name), index in sorted(named_at.items())}
    for item in settings.get("calls") or []:
        source, target = named_at.get((item["file"], item["source"])), defined.get(item["target"])
        if source is not None and target is not None:
            link(source, item.get("type", "CALLS"), target, "call", item["key"])
    if builtin_nodes:
        spread(builtin_nodes, settings.get("builtin_links", {"BUILTIN_USAGE": 12}), BUILTINS, "")
    return nodes, links


@functools.lru_cache(maxsize=None)
def by_source_path() -> dict:
    nodes, links = graph()
    index = {}
    for item in links:
        path = nodes[item[1]]["file_path"]
        if isinstance(path, str):
            index.setdefault(path, []).append(item)
    return index


# --- the reader --------------------------------------------------------------------------------------------------------

NODE = r"\(\s*(\w*)\s*(?::\s*`?(\w+)`?)?\s*\)"
EDGE = NODE + r"\s*-\s*\[\s*(\w*)\s*(?::\s*`?(\w+)`?)?\s*\]\s*->\s*" + NODE


def split_top(text: str) -> list:
    parts, depth, current = [], 0, ""
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if char == "," and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += char
    parts.append(current)
    return [p.strip() for p in parts if p.strip()]


def parse(query: str) -> dict:
    text = " ".join(query.split())
    found = re.match(r"(?i)^MATCH\s+(.+?)(?:\s+WHERE\s+(.+?))?\s+RETURN\s+(.+)$", text)
    if not found:
        raise Refused(f"unsupported query: {text[:80]}")
    pattern, where, tail = found.group(1).strip(), found.group(2), found.group(3)
    edge = re.fullmatch(EDGE, pattern)
    single = re.fullmatch(NODE, pattern)
    if edge:
        shape = {"edge": True, "a": edge.group(1) or "_a", "la": edge.group(2), "r": edge.group(3) or "_r", "type": edge.group(4),
                 "b": edge.group(5) or "_b", "lb": edge.group(6)}
    elif single:
        shape = {"edge": False, "n": single.group(1) or "_n", "ln": single.group(2)}
    else:
        raise Refused(f"unsupported pattern: {pattern[:80]}")
    skip = re.search(r"(?i)\bSKIP\s+(\d+)", tail)
    limit = re.search(r"(?i)\bLIMIT\s+(\d+)", tail)
    order = re.search(r"(?i)\bORDER\s+BY\s+(.+?)(?=\s+SKIP\b|\s+LIMIT\b|$)", tail)
    clause = re.split(r"(?i)\s+(?:ORDER\s+BY|SKIP|LIMIT)\b", tail, maxsplit=1)[0].strip()
    distinct = bool(re.match(r"(?i)^DISTINCT\s+", clause))
    clause = re.sub(r"(?i)^DISTINCT\s+", "", clause)
    items = []
    for raw in split_top(clause):
        alias = re.search(r"(?i)\s+AS\s+(\w+)\s*$", raw)
        expression = raw[:alias.start()].strip() if alias else raw.strip()
        items.append((expression, alias.group(1) if alias else expression))
    shape.update(where=where, items=items, distinct=distinct, skip=int(skip.group(1)) if skip else None,
                 limit=int(limit.group(1)) if limit else None, order=order.group(1) if order else None)
    shape["conditions"], shape["zero"] = conditions(where)
    return shape


def conditions(where):
    """``([(var, prop, value)], zero)``: the equality conditions; ``zero`` for a string comparison (answered with no rows)."""
    if not where:
        return [], False
    if re.search(r"(?i)\bIN\b", where):
        raise Refused("unsupported operator 'IN' in WHERE")
    if re.search(r"(?i)\bSTARTS\s+WITH\b", where):
        raise Refused("unsupported operator 'STARTS WITH' in WHERE")
    for name in re.findall(r"(\w+)\s*\(", where):
        if name.lower() not in WHERE_FUNCTIONS:
            raise Refused(f"unsupported function '{name}' in WHERE (supported: {', '.join(WHERE_FUNCTIONS)})")
    found, zero = [], False
    for part in re.split(r"(?i)\s+AND\s+", where.strip()):
        part = part.strip().strip("()").strip() if part.strip().startswith("(") and part.strip().endswith(")") and "coalesce" not in part else part.strip()
        literal = r"(?:\"([^\"]*)\"|'([^']*)')"
        equal = re.fullmatch(r"(\w+)\.(\w+)\s*=\s*" + literal, part)
        empty = re.fullmatch(r"(?i)coalesce\(\s*(\w+)\.(\w+)\s*,\s*(?:\"\"|'')\s*\)\s*=\s*(?:\"\"|'')", part)
        compare = re.fullmatch(r"(\w+)\.(\w+)\s*(?:>=|<=|>|<)\s*" + literal, part)
        if equal:
            found.append((equal.group(1), equal.group(2), equal.group(3) if equal.group(3) is not None else equal.group(4)))
        elif empty:
            found.append((empty.group(1), empty.group(2), ""))
        elif compare:
            zero = True
        else:
            raise Refused(f"unsupported condition in WHERE: {part[:80]}")
    return found, zero


def holds(value, wanted: str) -> bool:
    if wanted == "":
        return value is None or value == ""
    return isinstance(value, str) and value == wanted


def bindings(shape: dict):
    nodes, links = graph()
    if not shape["edge"]:
        for index, item in enumerate(nodes):
            if shape["ln"] and item["label"] != shape["ln"]:
                continue
            if all(holds(item.get(prop), value) for var, prop, value in shape["conditions"] if var == shape["n"]):
                yield {shape["n"]: item}
        return
    source_path = next((value for var, prop, value in shape["conditions"] if var == shape["a"] and prop == "file_path" and value), None)
    pool = by_source_path().get(source_path, []) if source_path is not None else links
    for identity, source, kind, target in pool:
        if shape["type"] and kind != shape["type"]:
            continue
        a, b = nodes[source], nodes[target]
        if shape["la"] and a["label"] != shape["la"]:
            continue
        if shape["lb"] and b["label"] != shape["lb"]:
            continue
        values = {shape["a"]: a, shape["b"]: b}
        if all(holds(values[var].get(prop), value) if var in values else False for var, prop, value in shape["conditions"]):
            yield {shape["a"]: a, shape["b"]: b, shape["r"]: {"id": identity, "type": kind}}


def value_of(expression: str, binding: dict, shape: dict):
    low = expression.replace(" ", "")
    call = re.fullmatch(r"(?i)(id|type|labels)\((\w+)\)", low)
    if call:
        name, var = call.group(1).lower(), call.group(2)
        if var not in binding:
            raise Refused(f"unknown variable {var}")
        if name == "id":
            return binding[var]["id"]
        if name == "type":
            return binding[var]["type"]
        return [binding[var]["label"]]
    prop = re.fullmatch(r"(\w+)\.(\w+)", low)
    if prop and prop.group(1) in binding and prop.group(2) in PROPS:
        return binding[prop.group(1)][prop.group(2)]
    raise Refused(f"unsupported return item: {expression[:60]}")


def is_count(expression: str) -> bool:
    return bool(re.fullmatch(r"(?i)count\(\s*(?:DISTINCT\s+)?[\w*.]+\s*\)", expression.strip()))


def links_read(shape: dict) -> bool:
    """A read of links (not a count, not a path list over a link match)."""
    if not shape["edge"] or any(is_count(e) for e, _ in shape["items"]):
        return False
    for expression, _alias in shape["items"]:
        low = expression.replace(" ", "").lower()
        if low.startswith(("id(", "type(")) or low in (f"{shape['a']}.qualified_name".lower(), f"{shape['b']}.qualified_name".lower()):
            return True
    return False


def evaluate(shape: dict) -> list:
    items = shape["items"]
    if shape["zero"]:
        source = []
    else:
        source = bindings(shape)
    if any(is_count(e) for e, _ in items):
        keys = [e for e, _ in items if not is_count(e)]
        if any(k.replace(" ", "").lower().endswith(".file_path") for k in keys):
            raise Refused("unsupported aggregation: a count grouped by file_path")
        groups = {}
        for binding in source:
            key = tuple(json.dumps(value_of(k, binding, shape)) for k in keys)
            groups[key] = groups.get(key, 0) + 1
        if not keys:
            return [[groups.get((), 0) if e and is_count(e) else None for e, _ in items]]
        rows = []
        for key, number in groups.items():
            values = iter(json.loads(part) for part in key)
            rows.append([number if is_count(e) else next(values) for e, _ in items])
        return rows
    rows = [[value_of(e, binding, shape) for e, _ in items] for binding in source]
    if shape["distinct"]:
        seen, unique = set(), []
        for row in rows:
            mark = json.dumps(row, sort_keys=True)
            if mark not in seen:
                seen.add(mark)
                unique.append(row)
        rows = unique
    if shape["order"]:
        names = [alias for _e, alias in items]
        exprs = [e for e, _a in items]
        positions = []
        for part in split_top(shape["order"]):
            key = re.sub(r"(?i)\s+(ASC|DESC)$", "", part.strip())
            if key in names:
                positions.append(names.index(key))
            elif key in exprs:
                positions.append(exprs.index(key))
            else:
                raise Refused(f"unsupported ORDER BY key: {key[:60]}")
        rows.sort(key=lambda row: [json.dumps(row[p], sort_keys=True) for p in positions])
    return rows


def piece(shape: dict) -> dict:
    """What the query is, for the plan's cuts and the log."""
    if shape["edge"]:
        file = next((value for var, prop, value in shape["conditions"] if var == shape["a"] and prop == "file_path"), None)
        return {"edge": True, "file": file, "type": shape["type"], "source_label": shape["la"], "target_label": shape["lb"]}
    return {"edge": False, "label": shape["ln"], "filtered": bool(shape["conditions"])}


def cut_by(shape: dict, about: dict) -> int:
    counting = any(is_count(e) for e, _ in shape["items"])
    if counting:
        return 0
    returns_paths = all(e.replace(" ", "").lower().endswith((".file_path",)) for e, _ in shape["items"])
    for cut in plan().get("cut") or []:
        kind, by = cut.get("piece"), int(cut.get("by", 1))
        if kind == "file" and links_read(shape) and about["file"] == cut["file"] and not about["type"] and not about["source_label"]:
            return by
        if kind == "file-type" and links_read(shape) and about["file"] == cut["file"] and about["type"] == cut["type"]:
            return by
        if kind == "label-links" and links_read(shape) and about["file"] is None and about["source_label"] == cut["label"]:
            return by
        if kind == "list" and not about["edge"] and about["label"] == cut["label"] and not about["filtered"] and returns_paths:
            return by
        if kind == "folder" and about["edge"] and about["type"] == "CONTAINS_FILE" and about["file"] == cut["file"] and returns_paths:
            return by
    return 0


_ANSWERS = {}


def answer(query: str):
    """``(rows, shape)`` of a query before the tool's paging; raises ``Refused`` with the tool's text."""
    if query in _ANSWERS:
        return _ANSWERS[query]
    shape = parse(query)
    counting = any(is_count(e) for e, _ in shape["items"])
    if counting and plan().get("counts", "ok") == "fail":
        raise Refused(ERROR_LOCKED)
    if links_read(shape) and plan().get("read", "ok") == "locked":
        raise Refused(ERROR_LOCKED)
    rows = evaluate(shape)
    if shape["skip"] is not None or shape["limit"] is not None:
        start = shape["skip"] or 0
        asked = rows[start:start + shape["limit"]] if shape["limit"] is not None else rows[start:]
        rows = asked[:int(len(asked) * SHORT_SHARE)]
    if len(rows) > CAP:
        raise Refused(ERROR_CAP)
    fewer = cut_by(shape, piece(shape))
    if fewer:
        rows = rows[:max(0, len(rows) - fewer)]
    _ANSWERS[query] = (rows, shape)
    return rows, shape


def text_envelope(payload=None, error=None) -> dict:
    if error is not None:
        return {"isError": True, "content": [{"type": "text", "text": error}]}
    return {"isError": False, "content": [{"type": "text", "text": json.dumps(payload)}]}


def log(entry: dict) -> None:
    where = os.environ.get("W2_88_F1_LOG")
    if where:
        with open(where, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")


def summary() -> None:
    """The planted graph's totals, for the case to compare A9's record with: ``<W2_88_F1_LOG>.graph.json``."""
    where = os.environ.get("W2_88_F1_LOG")
    if not where:
        return
    nodes, links = graph()
    by_type = {}
    for _identity, _source, kind, _target in links:
        by_type[kind] = by_type.get(kind, 0) + 1
    _folder, files = staged()
    Path(where + ".graph.json").write_text(json.dumps({"nodes": len(nodes), "links": len(links), "by_type": by_type, "files": files}),
                                           encoding="utf-8")


_SUMMARISED = []


def query_graph(args: dict) -> dict:
    if not _SUMMARISED:
        _SUMMARISED.append(True)
        summary()
    query = str(args.get("query", ""))
    offset, limit = int(args.get("offset") or 0), int(args.get("max_rows") or CAP)
    entry = {"query": query, "offset": offset, "max_rows": limit}
    try:
        rows, shape = answer(query)
    except Refused as refusal:
        log(entry | {"rows": "error", "error": str(refusal), "served": 0})
        return text_envelope(error=str(refusal))
    page = rows[offset:offset + limit]
    about = piece(shape)
    entry |= {"rows": len(rows), "served": len(page), "links": links_read(shape), "file": about.get("file"), "type": about.get("type"),
              "source_label": about.get("source_label")}
    names = [e.replace(" ", "").lower() for e, _ in shape["items"]]
    if entry["links"] and "id(" + shape["r"].lower() + ")" in names:
        entry["ids"] = [row[names.index("id(" + shape["r"].lower() + ")")] for row in page]
    log(entry)
    columns = [alias for _e, alias in shape["items"]]
    return text_envelope({"columns": columns, "rows": page, "total": len(rows), "has_more": offset + len(page) < len(rows)})


def call(tool: str, args: dict) -> dict:
    if tool == "index_repository":
        (cache() / "staged.json").write_text(json.dumps({"repo_path": args["repo_path"]}), encoding="utf-8")
        (cache() / "code.db").write_bytes(b"stand-in graph\n" * 64)
        graph.cache_clear()
        by_source_path.cache_clear()
        _ANSWERS.clear()
        nodes, links = graph()
        summary()
        return text_envelope({"status": "indexed", "project": args.get("name", "code"), "nodes": len(nodes), "edges": len(links)})
    if tool == "list_projects":
        nodes, links = graph()
        return text_envelope({"projects": [{"name": "code", "nodes": len(nodes), "edges": len(links)}]})
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
