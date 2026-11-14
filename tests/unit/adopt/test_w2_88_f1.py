"""W2-88 S25 (F-1): redis's code graph. ``codebase-memory-mcp`` refuses a query whose answer is over 100,000 rows; run 8
(package 2 (a), the owner's answer to be recorded as DEC-1183): ``gov.codeintel`` reads the graph by edge type and node
label under that cap, so A9 on a graph like redis's completes, its record holding the tool's counts; a type or label
over the cap is refused ``CODEGRAPH_TOO_LARGE`` by name, a read short of its count ``FABRIC_INCOMPLETE``.

Regression evidence only (DEC-136). The seam is the tool's answers: a stand-in ``codebase-memory-mcp`` first on ``PATH``
that speaks the MCP stdio protocol (``initialize``, ``tools/call`` of ``query_graph``) and answers as the real tool does
over its cap (``isError: true``, ``result exceeded 100k rows``), or counts of its own.
"""
from __future__ import annotations

import json
import os
import sys

import pytest
import yaml

from gov import codeintel
from gov.adopt import fabric
from gov.cli.errors import GovError

from .test_w2_88_fabric import planted, stand_ins  # noqa: F401  (stand_ins is a fixture)
from .test_w2_88_run4 import run_a9, stage_code_files, tree_status

# The lead's probe of ~/gov-os-runs/W2-88/redis (run 8): 41,086 nodes, 142,983 edges in 20 types, the largest 40,849.
REDIS_TYPES = {"USAGE": 40_849, "CALLS": 40_549, "DEFINES": 39_905, "WRITES": 12_427, "IMPORTS": 9_253}
REDIS = {"nodes": 41_086, "edges": 142_983, "types": REDIS_TYPES}
CAP_TEXT = "result exceeded 100k rows — use narrower filters or add LIMIT"
NODE = ["main.py::main", "main", "Function", "main.py"]

TOOL = '''#!%s
import json, re, sys
from pathlib import Path

CAP = 100_000
config = json.loads((Path(__file__).resolve().parent / "stand-in.json").read_text())
if sys.argv[1:2] == ["config"]:
    sys.exit(0)
TYPES = config.get("types") or {"CALLS": config["edges"]}
LABELS = config.get("labels") or {"Function": config["nodes"]}
SHORT = config.get("short", {})


def made(kind, count, node):
    count -= SHORT.get(kind, 0)
    return [[f"{kind}.{i}", f"n{i}", kind, f"gone{i}.c"] if node else [f"a{i}", kind, f"b{i}"] for i in range(count)]


def answer(query):
    if config.get("counts") == "fail" and "count(" in query:
        return None
    if query == "MATCH (n) RETURN count(n)":
        return [[str(config["nodes"])]]
    if query == "MATCH (a)-[r]->(b) RETURN count(r)":
        return [[str(config["edges"])]]
    if query == "MATCH (a)-[r]->(b) RETURN type(r), count(r)":
        return [[kind, str(count)] for kind, count in TYPES.items()]
    if query == "MATCH (n) RETURN n.label, count(n)":
        return [[label, str(count)] for label, count in LABELS.items()]
    typed = re.search(r"\\[r:(\\w+)\\]", query)
    labelled = re.search(r"MATCH \\(n:(\\w+)\\)", query)
    if typed:
        rows = made(typed.group(1), TYPES.get(typed.group(1), 0), False)
    elif labelled:
        rows = made(labelled.group(1), LABELS.get(labelled.group(1), 0), True)
    elif config.get("whole") == "fail":
        return None
    elif "RETURN n.qualified_name" in query:
        rows = config["rows"]["nodes"] if config["nodes"] == len(config["rows"]["nodes"]) else \\
            [row for label, count in LABELS.items() for row in made(label, count, True)]
    else:
        rows = config["rows"]["edges"] if config["edges"] == len(config["rows"]["edges"]) else \\
            [row for kind, count in TYPES.items() for row in made(kind, count, False)]
    return None if len(rows) > CAP else rows


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
        rows = answer(arguments.get("query", ""))
        if rows is None:
            result = {"content": [{"type": "text", "text": %r}], "isError": True}
        else:
            at, most = arguments.get("offset", 0), arguments.get("max_rows", 1000)
            text = json.dumps({"rows": rows[at:at + most], "has_more": at + most < len(rows)})
            result = {"content": [{"type": "text", "text": text}], "isError": False}
    print(json.dumps({"jsonrpc": "2.0", "id": message["id"], "result": result}), flush=True)
''' % (sys.executable, CAP_TEXT)


@pytest.fixture()
def tool(tmp_path, monkeypatch):
    """Plant the stand-in tool first on ``PATH``; its answers are the config the test sets."""
    bin_dir = tmp_path / "tool-bin"
    bin_dir.mkdir()
    place = bin_dir / codeintel.TOOL
    place.write_text(TOOL)
    place.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")

    def answers(**config):
        (bin_dir / "stand-in.json").write_text(json.dumps({"rows": {"nodes": [NODE], "edges": []}, **config}))

    return answers


def a9(tmp_path, monkeypatch):
    stage_code_files(monkeypatch)
    codeintel._graph.cache_clear()
    root = planted(tmp_path)
    return root, lambda: run_a9(root, tmp_path / "out", with_code_graph=True)


def head(root, result):
    return yaml.safe_load((root / result["record"]).read_text().split("---\n")[1])


def assert_nothing_written(root):
    assert tree_status(root) == "" and not (root / ".claude").exists()
    assert not (root / "governance/adoption").exists()


def test_a_graph_like_rediss_over_the_cap_with_every_type_under_completes_with_the_tools_counts(tmp_path, monkeypatch,
                                                                                               stand_ins, tool):
    tool(**REDIS)
    root, run = a9(tmp_path, monkeypatch)
    result = run()
    assert result["ok"] is True
    graph = head(root, result)["stores"]["codegraph"]
    assert graph["nodes"] == 41_086 and graph["edges"] == 142_983 and "built" not in graph


def test_a_type_at_the_cap_is_read(tmp_path, monkeypatch, stand_ins, tool):
    tool(nodes=5, edges=100_000 + 7, types={"USAGE": 100_000, "CALLS": 7})
    root, run = a9(tmp_path, monkeypatch)
    assert head(root, run())["stores"]["codegraph"]["edges"] == 100_007


def test_a_type_over_the_cap_is_refused_codegraph_too_large_by_name(tmp_path, monkeypatch, stand_ins, tool):
    types = {**REDIS_TYPES, "USAGE": 100_001}
    tool(nodes=41_086, edges=sum(types.values()), types=types)
    root, run = a9(tmp_path, monkeypatch)
    with pytest.raises(GovError) as raised:
        run()
    err = raised.value
    assert err.code == "CODEGRAPH_TOO_LARGE"
    assert err.details == {"nodes": 41_086, "edges": sum(types.values()), "cap": 100_000, "tool": "codebase-memory-mcp",
                           "kind": "USAGE"}
    for said in ("codebase-memory-mcp", "100000", "USAGE", "100001", "edge type"):
        assert said in err.message, said
    assert_nothing_written(root)  # a refusal after A9's copies undoes them


def test_a_label_over_the_cap_is_refused_by_name(tmp_path, monkeypatch, stand_ins, tool):
    tool(nodes=150_000, edges=10, labels={"Function": 120_000, "File": 30_000})
    root, run = a9(tmp_path, monkeypatch)
    with pytest.raises(GovError) as raised:
        run()
    assert raised.value.code == "CODEGRAPH_TOO_LARGE" and raised.value.details["kind"] == "Function"
    assert raised.value.details["nodes"] == 150_000 and "node label Function has 120000" in raised.value.message


def test_a_typed_read_short_of_its_count_is_fabric_incomplete_with_both_figures(tmp_path, monkeypatch, stand_ins, tool):
    tool(**REDIS, short={"CALLS": 3})
    root, run = a9(tmp_path, monkeypatch)
    with pytest.raises(GovError) as raised:
        run()
    err = raised.value
    assert err.code == "FABRIC_INCOMPLETE" and "codegraph" in err.details["not_built"]
    for said in ("codegraph", "CALLS", "40549", "40546"):
        assert said in err.message, said
    assert_nothing_written(root)


def test_another_failure_of_the_read_keeps_fabric_incomplete_naming_the_store_and_the_error(tmp_path, monkeypatch,
                                                                                            stand_ins, tool):
    tool(nodes=50, edges=70, whole="fail")  # a graph under the cap that the tool still fails to answer
    root, run = a9(tmp_path, monkeypatch)
    with pytest.raises(GovError) as raised:
        run()
    err = raised.value
    assert err.code == "FABRIC_INCOMPLETE" and "codegraph" in err.details["not_built"]
    assert "codegraph" in err.message and "query_graph failed" in err.message and "RuntimeError" in err.message
    assert_nothing_written(root)


def test_a_tool_that_cannot_count_refuses_and_never_records_zero(tmp_path, monkeypatch, stand_ins, tool):
    tool(**REDIS, counts="fail")
    root, run = a9(tmp_path, monkeypatch)
    with pytest.raises(GovError) as raised:
        run()
    assert raised.value.code == "FABRIC_INCOMPLETE" and "query_graph failed" in raised.value.message
    assert_nothing_written(root)


def test_a_graph_under_the_cap_is_read_and_checked_as_today(tmp_path, monkeypatch, stand_ins, tool):
    tool(nodes=1, edges=0)
    root, run = a9(tmp_path, monkeypatch)
    result = run()
    graph = head(root, result)["stores"]["codegraph"]
    assert result["ok"] is True
    assert graph["nodes"] == 1 and graph["edges"] == 0
    assert graph["indexed"] == ["main.py"]


def test_the_refusal_is_made_from_the_reads_own_error():
    exc = codeintel.GraphTooLarge("edge type", "USAGE", 100_001, 41_086, 160_001)
    err = fabric.too_large(exc)
    assert err.code == "CODEGRAPH_TOO_LARGE" and err.details["kind"] == "USAGE" and "USAGE" in err.message
