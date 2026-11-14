"""W2-88 run 8, package 2 (a) (the owner's answer to be recorded as DEC-1183): the code graph is read in pages by type.

Regression evidence only (DEC-136). ``codebase-memory-mcp`` refuses any query whose whole answer is over 100,000 rows,
before its own ``offset``/``max_rows`` paging; ``gov.codeintel._graph`` asks the counts first, reads a total under the
cap whole, else each edge type and each node label with its own match, and checks the rows read against each count.
``SKIP``/``LIMIT`` is no sound page (the lead's probe) and is never asked. The seam is the tool's answers: a stand-in
``codebase-memory-mcp`` first on ``PATH`` that speaks MCP over stdio and answers as the real tool does.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

from gov import codeintel

CAP_TEXT = "result exceeded 100k rows — use narrower filters or add LIMIT"

STAND_IN = '''#!%s
import json, re, sys
from pathlib import Path

CAP = 100_000
here = Path(__file__).resolve().parent
config = json.loads((here / "stand-in.json").read_text())
if sys.argv[1:2] == ["config"]:
    sys.exit(0)
EDGES, LABELS = config["edges"], config["labels"]
SHORT, REFUSE = config.get("short", {}), config.get("refuse", [])


def nodes(label):
    count = LABELS[label] - SHORT.get(label, 0)
    return [[f"{label}.{i}", f"n{i}", label, f"f{i %% 7}.c"] for i in range(count)]


def edges(kind):
    count = EDGES[kind] - SHORT.get(kind, 0)
    return [[f"a{i}", kind, f"b{i}"] for i in range(count)]


def answer(query):
    """Every row of the query's whole answer, or None where the tool refuses it."""
    whole = None
    if query == "MATCH (n) RETURN count(n)":
        return [[str(sum(LABELS.values()) + config.get("unlabelled", 0))]]
    if query == "MATCH (a)-[r]->(b) RETURN count(r)":
        return [[str(sum(EDGES.values()) + config.get("untyped", 0))]]
    if query == "MATCH (a)-[r]->(b) RETURN type(r), count(r)":
        return [[kind, str(count)] for kind, count in EDGES.items()]
    if query == "MATCH (n) RETURN n.label, count(n)":
        return [[label, str(count)] for label, count in LABELS.items()]
    typed = re.fullmatch(r"MATCH \\(a\\)-\\[r:(\\w+)\\]->\\(b\\) RETURN a.qualified_name, type\\(r\\), b.qualified_name", query)
    labelled = re.fullmatch(r"MATCH \\(n:(\\w+)\\) RETURN n.qualified_name, n.name, n.label, n.file_path", query)
    if typed:
        if typed.group(1) in REFUSE:
            return None
        whole = edges(typed.group(1)) if typed.group(1) in EDGES else []
    elif labelled:
        if labelled.group(1) in REFUSE:
            return None
        whole = nodes(labelled.group(1)) if labelled.group(1) in LABELS else []
    elif query.startswith("MATCH (a)-[r]->(b) RETURN a.qualified_name"):
        whole = [row for kind in EDGES for row in edges(kind)]
    elif query.startswith("MATCH (n) RETURN n.qualified_name"):
        whole = [row for label in LABELS for row in nodes(label)]
    if whole is None:
        return []
    if " LIMIT " in query or " SKIP " in query:  # no sound page: a short answer, as the lead's probe saw
        return whole[: len(whole) // 3]
    return None if len(whole) > CAP else whole


for line in sys.stdin:
    if not line.startswith("{"):
        continue
    message = json.loads(line)
    if "id" not in message:
        continue
    if message["method"] == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {}, "serverInfo": {"name": "stand-in", "version": "0"}}
    else:
        arguments = message["params"]["arguments"]
        query = arguments.get("query", "")
        with open(here / "queries.log", "a") as log:
            log.write(query + "\\n")
        rows = answer(query)
        if rows is None:
            result = {"content": [{"type": "text", "text": %r}], "isError": True}
        else:
            at, most = arguments.get("offset", 0), arguments.get("max_rows", 1000)
            page = rows[at:at + most]
            result = {"content": [{"type": "text", "text": json.dumps({"rows": page, "has_more": at + most < len(rows)})}],
                      "isError": False}
    print(json.dumps({"jsonrpc": "2.0", "id": message["id"], "result": result}), flush=True)
''' % (sys.executable, CAP_TEXT)

LABELS = {"Function": 30_000, "Variable": 12_000, "File": 900, "Macro": 4_000}
UNDER = {"CALLS": 45_000, "USAGE": 44_000, "DEFINES": 39_000, "IMPORTS": 2_000}  # 130,000 edges, every type under


@pytest.fixture()
def graph(tmp_path, monkeypatch):
    """A repository root and a stand-in tool first on ``PATH``; ``graph(**config)`` plants its answers and returns a
    reader of the queries it was asked."""
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    bin_dir = tmp_path / "tool-bin"
    bin_dir.mkdir()
    place = bin_dir / codeintel.TOOL
    place.write_text(STAND_IN)
    place.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")
    codeintel._graph.cache_clear()

    def plant(**config):
        (bin_dir / "stand-in.json").write_text(json.dumps({"labels": LABELS, "edges": UNDER, **config}))
        (bin_dir / "queries.log").write_text("")
        return lambda: (bin_dir / "queries.log").read_text().splitlines()

    yield root, plant
    codeintel._graph.cache_clear()


def test_a_graph_over_the_cap_whose_every_type_is_under_is_read_whole_by_type(graph):
    root, plant = graph
    asked = plant()
    nodes, users = codeintel._graph(root)
    assert codeintel.counted(root) == (sum(LABELS.values()), sum(UNDER.values()))  # 46,900 and 130,000
    queries = asked()
    for kind in UNDER:
        assert f"MATCH (a)-[r:{kind}]->(b) RETURN a.qualified_name, type(r), b.qualified_name" in queries
    assert "MATCH (a)-[r]->(b) RETURN a.qualified_name, type(r), b.qualified_name" not in queries  # over the cap whole
    assert "MATCH (n) RETURN n.qualified_name, n.name, n.label, n.file_path" in queries  # nodes under the cap: whole


def test_no_query_asks_skip_or_limit(graph):
    root, plant = graph
    asked = plant(labels={"Function": 60_000, "Variable": 50_000})  # nodes over the cap too: read by label
    codeintel._graph(root)
    queries = asked()
    assert queries and not any(" SKIP " in query or " LIMIT " in query for query in queries)
    for label in ("Function", "Variable"):
        assert f"MATCH (n:{label}) RETURN n.qualified_name, n.name, n.label, n.file_path" in queries
    assert codeintel.counted(root) == (110_000, sum(UNDER.values()))


def test_a_type_over_the_cap_is_refused_by_name_with_its_count(graph):
    root, plant = graph
    plant(edges={**UNDER, "USAGE": 100_001})
    with pytest.raises(codeintel.GraphTooLarge) as raised:
        codeintel._graph(root)
    err = raised.value
    assert (err.kind, err.count, err.cap) == ("USAGE", 100_001, codeintel.CAP) and err.what == "edge type"
    assert (err.nodes, err.edges) == (sum(LABELS.values()), sum(UNDER.values()) - 44_000 + 100_001)
    assert "USAGE" in str(err) and "100001" in str(err) and codeintel.TOOL in str(err)
    assert codeintel.counted(root) is None  # nothing read is a count


def test_a_label_over_the_cap_is_refused_by_name(graph):
    root, plant = graph
    plant(labels={**LABELS, "Function": 120_000})
    with pytest.raises(codeintel.GraphTooLarge) as raised:
        codeintel._graph(root)
    assert raised.value.kind == "Function" and raised.value.count == 120_000 and raised.value.what == "node label"


def test_a_typed_page_the_tool_still_refuses_is_refused_by_name(graph):
    root, plant = graph
    plant(refuse=["CALLS"])
    with pytest.raises(codeintel.GraphTooLarge) as raised:
        codeintel._graph(root)
    assert raised.value.kind == "CALLS" and raised.value.count == 45_000 and raised.value.refused is True


def test_a_typed_read_short_of_its_count_refuses_with_both_figures(graph):
    root, plant = graph
    plant(short={"DEFINES": 7})
    with pytest.raises(codeintel.GraphShort) as raised:
        codeintel._graph(root)
    err = raised.value
    assert (err.kind, err.counted, err.read) == ("DEFINES", 39_000, 38_993)
    assert "DEFINES" in str(err) and "39000" in str(err) and "38993" in str(err)


def test_type_counts_short_of_the_total_refuse(graph):
    root, plant = graph
    plant(untyped=5)  # five edges the counts by type do not hold: reading by type would miss them
    with pytest.raises(codeintel.GraphShort) as raised:
        codeintel._graph(root)
    assert raised.value.counted == sum(UNDER.values()) + 5 and raised.value.read == sum(UNDER.values())


def test_a_whole_read_short_of_its_count_refuses(graph):
    root, plant = graph
    plant(edges={"CALLS": 10, "USAGE": 20}, short={"USAGE": 1})  # under the cap: read whole, 29 rows of 30
    with pytest.raises(codeintel.GraphShort) as raised:
        codeintel._graph(root)
    assert raised.value.counted == 30 and raised.value.read == 29


def test_a_graph_under_the_cap_is_read_whole_as_today(graph):
    root, plant = graph
    asked = plant(labels={"Function": 3}, edges={"CALLS": 2})
    codeintel._graph(root)
    assert codeintel.counted(root) == (3, 2)
    assert "MATCH (a)-[r]->(b) RETURN a.qualified_name, type(r), b.qualified_name" in asked()


def test_a_tool_that_answers_no_count_is_read_whole_as_before_and_gives_no_count(tmp_path, monkeypatch):
    nodes = [["m.f", "f", "Function", "m.py"]]
    edges = [["m.f", "CALLS", "m.f"]]
    asked = []
    monkeypatch.setattr(codeintel, "_rows", lambda _s, query: asked.append(query) or (edges if "type(r)" in query else nodes))
    codeintel._graph.cache_clear()
    root = tmp_path / "plain"
    codeintel._graph(root)
    assert codeintel.counted(root) is None
    assert asked[-2:] == [codeintel._NODES, codeintel._EDGES]
    codeintel._graph.cache_clear()


def test_a_tool_error_keeps_the_tools_text(graph):
    root, plant = graph
    plant(refuse=["CALLS"])
    with codeintel._Session(root) as session:
        with pytest.raises(RuntimeError) as raised:
            session.tool("query_graph", project=codeintel.PROJECT, format="json", max_rows=10,
                         query="MATCH (a)-[r:CALLS]->(b) RETURN a.qualified_name, type(r), b.qualified_name")
    assert "query_graph failed" in str(raised.value) and "exceeded 100k rows" in str(raised.value)
