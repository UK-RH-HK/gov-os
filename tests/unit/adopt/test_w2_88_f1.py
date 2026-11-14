"""W2-88 run 7, S25 (F-1): redis's code graph. ``codebase-memory-mcp`` refuses a query whose answer is over 100,000 rows,
and ``gov.codeintel`` reads the whole graph in one query (outside W2-88's paths); A9 names that cause, with
``CODEGRAPH_TOO_LARGE``, instead of ``FABRIC_INCOMPLETE`` with no reason.

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

REDIS = {"nodes": 41_086, "edges": 143_008}  # the lead's probe of ~/gov-os-runs/W2-88/redis, 2026-11-14
CAP_TEXT = "result exceeded 100k rows — use narrower filters or add LIMIT"
NODE = ["main.py::main", "main", "Function", "main.py"]

TOOL = '''#!%s
import json, sys
from pathlib import Path

CAP = 100_000
config = json.loads((Path(__file__).resolve().parent / "stand-in.json").read_text())
if sys.argv[1:2] == ["config"]:
    sys.exit(0)


def answer(query):
    if config.get("counts") == "fail" and "count(" in query:
        return None
    if "count(n)" in query:
        return [[config["nodes"]]]
    if "count(r)" in query:
        return [[config["edges"]]]
    whole, size = ("nodes", config["nodes"]) if "RETURN n.qualified_name" in query else ("edges", config["edges"])
    if size > CAP or config.get("whole") == "fail":
        return None
    return config["rows"][whole]


for line in sys.stdin:
    if not line.startswith("{"):
        continue
    message = json.loads(line)
    if "id" not in message:
        continue
    if message["method"] == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {}, "serverInfo": {"name": "stand-in", "version": "0"}}
    else:
        rows = answer(message["params"]["arguments"].get("query", ""))
        if rows is None:
            result = {"content": [{"type": "text", "text": %r}], "isError": True}
        else:
            result = {"content": [{"type": "text", "text": json.dumps({"rows": rows, "has_more": False})}], "isError": False}
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


def assert_nothing_written(root):
    assert tree_status(root) == "" and not (root / ".claude").exists()
    assert not (root / "governance/adoption").exists()


def test_a_graph_over_the_tools_cap_is_refused_codegraph_too_large_with_the_counts(tmp_path, monkeypatch, stand_ins, tool):
    tool(**REDIS)
    root, run = a9(tmp_path, monkeypatch)
    with pytest.raises(GovError) as raised:
        run()
    err = raised.value
    assert err.code == "CODEGRAPH_TOO_LARGE"
    assert err.details == {"nodes": 41_086, "edges": 143_008, "cap": 100_000, "tool": "codebase-memory-mcp"}
    for said in ("codebase-memory-mcp", "100000", "41086", "143008", "gov.codeintel", "one query"):
        assert said in err.message, said
    assert_nothing_written(root)  # a refusal after A9's copies undoes them


def test_either_count_over_the_cap_is_enough(tmp_path, monkeypatch, stand_ins, tool):
    tool(nodes=150_000, edges=10)
    root, run = a9(tmp_path, monkeypatch)
    with pytest.raises(GovError) as raised:
        run()
    assert raised.value.code == "CODEGRAPH_TOO_LARGE" and raised.value.details["nodes"] == 150_000
    assert raised.value.details["edges"] == 10


def test_the_boundary_is_over_the_cap_not_at_it(tmp_path, monkeypatch, tool):
    tool(nodes=100_000, edges=100_000)
    root = planted(tmp_path)
    fabric.refuse_too_large(root)  # at the cap: the read's own failure stands
    tool(nodes=100_001, edges=1)
    with pytest.raises(GovError) as raised:
        fabric.refuse_too_large(root)
    assert raised.value.code == "CODEGRAPH_TOO_LARGE"


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


def test_a_tool_that_cannot_count_leaves_the_reads_own_failure(tmp_path, monkeypatch, stand_ins, tool):
    tool(**REDIS, counts="fail")
    root, run = a9(tmp_path, monkeypatch)
    with pytest.raises(GovError) as raised:
        run()
    assert raised.value.code == "FABRIC_INCOMPLETE" and "query_graph failed" in raised.value.message
    assert fabric.graph_counts(root) is None


def test_a_graph_under_the_cap_is_read_and_checked_as_today(tmp_path, monkeypatch, stand_ins, tool):
    tool(nodes=1, edges=0)
    root, run = a9(tmp_path, monkeypatch)
    result = run()
    head = yaml.safe_load((root / result["record"]).read_text().split("---\n")[1])
    assert result["ok"] is True
    assert head["stores"]["codegraph"]["nodes"] == 1 and head["stores"]["codegraph"]["edges"] == 0
    assert head["stores"]["codegraph"]["indexed"] == ["main.py"]
