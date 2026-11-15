"""W2-88 S25 (F-1) and S28 (DEC-1185): redis's code graph. ``codebase-memory-mcp`` refuses a query whose answer is over
100,000 rows and cuts answers short by size; ``gov.codeintel`` reads the links in pieces by source file (by link type
inside a file cut or over the cap), so A9 on a graph like redis's, or one whose single link type is over 100,000,
completes, its record holding the tool's counts, the pieces read and the read's wall time; a (file, type) piece over
the cap is refused ``CODEGRAPH_TOO_LARGE`` by name, a piece short of its count ``FABRIC_INCOMPLETE``.

Regression evidence only (DEC-136). The seam is the tool's answers: the stand-in of
``tests/unit/codeintel/test_w2_88_standin_tool.py`` first on ``PATH``.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest
import yaml

from gov import codeintel
from gov.adopt import fabric
from gov.cli.errors import GovError

from .test_w2_88_fabric import planted, stand_ins  # noqa: F401  (stand_ins is a fixture)
from .test_w2_88_run4 import run_a9, stage_code_files, tree_status

_SPEC = importlib.util.spec_from_file_location(
    "w2_88_standin_tool", Path(__file__).resolve().parents[1] / "codeintel" / "test_w2_88_standin_tool.py")
standin = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(standin)


def graph_of(files: dict, **extra) -> dict:
    """Links out of ``files``; each path one File node and one Function node (``main.py``'s Function is its symbol)."""
    return {"files": files, "labels": {"File": {p: 1 for p in files}, "Function": {p: 1 for p in files}}, **extra}


# A graph like redis's in kind (run 8b, item 20), its one large type over 100,000 spread across files.
WIDE = {**{f"src/m{i:02}.c": {"USAGE": 3_000, "CALLS": 1_000} for i in range(40)}, "main.py": {"CALLS": 1}}


@pytest.fixture()
def tool(tmp_path, monkeypatch):
    """Plant the stand-in tool first on ``PATH``; its answers are the graph the test sets."""
    bin_dir = tmp_path / "tool-bin"
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")
    return lambda graph: standin.plant(bin_dir, graph)


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


def test_a_graph_whose_one_type_is_over_the_cap_completes_with_the_tools_counts_and_the_read(tmp_path, monkeypatch,
                                                                                             stand_ins, tool):
    tool(graph_of(WIDE))
    root, run = a9(tmp_path, monkeypatch)
    result = run()
    assert result["ok"] is True
    graph = head(root, result)["stores"]["codegraph"]
    assert graph["nodes"] == 82 and graph["edges"] == 160_001 and "built" not in graph  # USAGE alone 120,000
    assert graph["pieces_read"] == 41 and graph["pieces_from_record"] == 0 and graph["read_seconds"] >= 0


def test_a_file_and_type_piece_over_the_cap_is_refused_codegraph_too_large_by_name(tmp_path, monkeypatch, stand_ins,
                                                                                    tool):
    tool(graph_of({**WIDE, "src/huge.c": {"USAGE": 100_001}}))
    root, run = a9(tmp_path, monkeypatch)
    with pytest.raises(GovError) as raised:
        run()
    err = raised.value
    assert err.code == "CODEGRAPH_TOO_LARGE"
    assert err.details == {"nodes": 84, "edges": 260_002, "cap": 100_000, "tool": "codebase-memory-mcp",
                           "kind": "USAGE", "file": "src/huge.c"}
    for said in ("codebase-memory-mcp", "100000", "USAGE", "100001", "src/huge.c"):
        assert said in err.message, said
    assert_nothing_written(root)  # a refusal after A9's copies undoes them


def test_a_file_and_type_piece_short_of_its_count_is_fabric_incomplete_with_both_figures(tmp_path, monkeypatch,
                                                                                         stand_ins, tool):
    tool(graph_of(WIDE, cut={"links:src/m03.c": 10, "links:src/m03.c:CALLS": 997}))
    root, run = a9(tmp_path, monkeypatch)
    with pytest.raises(GovError) as raised:
        run()
    err = raised.value
    assert err.code == "FABRIC_INCOMPLETE" and "codegraph" in err.details["not_built"]
    for said in ("codegraph", "src/m03.c", "CALLS", "1000", "997"):
        assert said in err.message, said
    assert_nothing_written(root)


def test_another_failure_of_the_read_keeps_fabric_incomplete_naming_the_store_and_the_error(tmp_path, monkeypatch,
                                                                                            stand_ins, tool):
    tool(graph_of(WIDE, fail='WHERE a.file_path = "src/m07.c" RETURN count(r)'))
    root, run = a9(tmp_path, monkeypatch)
    with pytest.raises(GovError) as raised:
        run()
    err = raised.value
    assert err.code == "FABRIC_INCOMPLETE" and "codegraph" in err.details["not_built"]
    assert "codegraph" in err.message and "query_graph failed" in err.message and "boom" in err.message
    assert "RuntimeError" in err.message
    assert_nothing_written(root)


def test_a_tool_that_cannot_count_refuses_and_never_records_zero(tmp_path, monkeypatch, stand_ins, tool):
    tool(graph_of(WIDE, fail="count("))
    root, run = a9(tmp_path, monkeypatch)
    with pytest.raises(GovError) as raised:
        run()
    assert raised.value.code == "FABRIC_INCOMPLETE" and "query_graph failed" in raised.value.message
    assert_nothing_written(root)


def test_a_small_graph_is_read_and_checked(tmp_path, monkeypatch, stand_ins, tool):
    tool(graph_of({"main.py": {"CALLS": 1}}))
    root, run = a9(tmp_path, monkeypatch)
    result = run()
    graph = head(root, result)["stores"]["codegraph"]
    assert result["ok"] is True
    assert graph["nodes"] == 2 and graph["edges"] == 1
    assert graph["indexed"] == ["main.py"]


def test_the_refusal_is_made_from_the_reads_own_error():
    exc = codeintel.GraphTooLarge("link type", "USAGE", 100_001, 41_086, 160_001, file="src/module.c")
    err = fabric.too_large(exc)
    assert err.code == "CODEGRAPH_TOO_LARGE" and err.details["kind"] == "USAGE" and "USAGE" in err.message
    assert err.details["file"] == "src/module.c" and "src/module.c" in err.message
    plain = fabric.too_large(codeintel.GraphTooLarge("source label", "Branch", 100_001, 5, 100_001))
    assert "file" not in plain.details
