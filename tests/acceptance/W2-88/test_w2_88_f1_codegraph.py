"""Run 7, S25 (F-1, DEC-1178 (3)(b)): redis's code graph. A9 names the cause where the code graph is over the tool's cap.

The smoke run's finding F-1 (``experiments/W2-88/smoke-run.md``): A9 on a copy of redis (C, vendored ``deps/``) refused ``FABRIC_INCOMPLETE``
(``codegraph: RuntimeError: codebase-memory-mcp query_graph failed (exit code 0)``) after the rebuild had marked its code-index store done.
The lead's probe: ``codebase-memory-mcp``'s ``query_graph`` refuses a query whose result exceeds 100,000 rows, before its own paging, with
``isError: true`` and the text ``result exceeded 100k rows ...``; redis's graph has 41,086 nodes and 143,008 edges, and ``gov.codeintel`` reads all
edges in one query. The cause is in ``src/gov/codeintel/__init__.py``, outside the ticket's paths (a package for the CTO). The interface
(the lead's statement, DEC-1052, DEC-136; the ticket's S25, "or, if the cause is outside them, A9 refuses with a code and text that name it"):

* when A9's read of the code graph fails, A9 asks the tool for the graph's node and edge counts (count queries, one row each). Where either
  count exceeds the cap of 100,000 rows A9 refuses ``CODEGRAPH_TOO_LARGE``: the message names the tool (``codebase-memory-mcp``), its cap of
  100,000 rows per query, the node and edge counts, and that gov's code-graph read takes the whole graph in one query (``gov.codeintel``);
  ``details`` hold ``nodes``, ``edges``, ``cap`` (100000) and ``tool``;
* any other failure of the read keeps ``FABRIC_INCOMPLETE`` naming the store and the error text; a failed read is never a pass and never
  0 nodes and edges; a graph under the cap is read and checked as today.

The seam: the tool's answers. ``standin_f1/tool.py`` is copied as ``codebase-memory-mcp`` into a folder first on the child's ``PATH`` and
answers the protocol ``gov.codeintel`` speaks (``config``, ``cli ... index_repository|list_projects``, the stdio server's ``query_graph``);
its settings (the counts it answers, what the whole-graph read of the edges does, whether the count queries answer) are the case's. The
plant is a C repository with a vendored folder (``src/``, ``deps/<lib>/``), code intelligence called for in its path map, the suite's chain
A0 to A8 run once per module and forked per case (the suite's A9 cases).

Run 8 (DEC-1183, the owner's package 2 (a); run 8 interface items 7-10): ``gov.codeintel`` reads the graph in pages by type, each under the
tool's cap: the counts first (edges by type, nodes by label), then each edge type with its typed match and each label with its label match,
never by ``SKIP``/``LIMIT``; the rows read for each type and label equal its count, else the read refuses. The stand-in now behaves as the
lead's probe found the real tool does (``standin_f1/tool.py``: count queries in full, the typed and label matches in full, any result over
100,000 rows refused with the real tool's text, ``SKIP``/``LIMIT`` answered short), its graph generated from ``W2_88_F1_TYPES`` and
``W2_88_F1_LABELS``. So:

* (a) a graph over 100,000 edges (or nodes) whose every type and label is within the cap: A9 completes, its record's code graph counts
  the planted totals (this replaces run 7's case that expected ``CODEGRAPH_TOO_LARGE`` for redis's figures: Rewrite-Reason DEC-1183,
  package 2 (a));
* (b) one edge type (or label) over 100,000: ``CODEGRAPH_TOO_LARGE`` naming the tool, the cap, the type (or label) and its count,
  ``details.kind`` the type (or label);
* (c) a typed (or label) read that answers fewer rows than its count: ``FABRIC_INCOMPLETE`` naming the store, the type (or label) and both
  figures.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

import w2_88_support as W

TOOL = "codebase-memory-mcp"
CAP = 100_000
STANDIN = W.HERE / "standin_f1" / "tool.py"
CODE = "CODEGRAPH_TOO_LARGE"
C_FILES = {
    "src/server.c": "#include \"server.h\"\n\nint serve(int port) {\n    return port + start();\n}\n\nint start(void) {\n    return 1;\n}\n",
    "src/server.h": "int serve(int port);\nint start(void);\n",
    "src/util.c": "#include \"server.h\"\n\nint helper(int n) {\n    return serve(n) * 2;\n}\n",
    "deps/lua/src/lapi.c": "/* Vendored from lua 5.1, kept as published. */\nint lua_gettop(void) {\n    return 0;\n}\n",
    "deps/lua/src/lauxlib.c": "/* Vendored from lua 5.1, kept as published. */\nint luaL_error(void) {\n    return 1;\n}\n",
    "deps/hiredis/hiredis.c": "/* Vendored from hiredis, kept as published. */\nint redisConnect(void) {\n    return 2;\n}\n",
    "deps/README.md": "# deps\n\nThe vendored libraries of the harbour's server, kept as published.\n",
}


def make_tool(folder: Path) -> Path:
    """The stand-in as a program named ``codebase-memory-mcp`` in ``folder`` (a ``#!`` line for the suite's python first)."""
    folder.mkdir(parents=True, exist_ok=True)
    program = folder / TOOL
    program.write_text(f"#!{sys.executable}\n" + STANDIN.read_text(encoding="utf-8"), encoding="utf-8")
    program.chmod(0o755)
    return folder


def c_path_map() -> str:
    document = yaml.safe_load(W.path_map_text(W.adoption_namespaces()))
    paths = document["namespaces"]["harbour"]["paths"]
    document["namespaces"]["harbour"]["paths"] = [*paths, "src/**", "deps/**"]
    document["capabilities"]["code_intelligence"] = {"enabled": True, "languages": ["c"]}
    return yaml.safe_dump(document, sort_keys=False)


@pytest.fixture(scope="module")
def c_world(tmp_path_factory, embedder):
    """The planted C repository through A8 with the stand-in tool on PATH (made once, forked per case)."""
    base = tmp_path_factory.mktemp("f1-world")
    box = W.make_box(base)
    tool = make_tool(Path(base) / "tools-cbm")
    extra = {**C_FILES, W.S124.PATH_MAP_REL: c_path_map()}
    project = W.plant_adoption(box, "harbour", extra=extra)
    adoption = W.Adoption(project, box, embedder.host, tools=(tool,),
                          extra_env={"CODEINTEL_DAEMON_BASE": str(Path(base) / "cbm"), "W2_88_F1_NODES": "", "W2_88_F1_EDGES": ""})
    failed = adoption.chain("A8")
    world = SimpleNamespace(box=box, project=project, adoption=adoption, chain_failed=failed, tool=tool)
    try:
        yield world
    finally:
        shutil.rmtree(base, ignore_errors=True)


def a9_with(world, name: str, **settings):
    """A fork of the planted repository at A8 with the stand-in's settings (``W2_88_F1_*``), A9 run once; ``(adoption, run, log)``."""
    assert world.chain_failed is None, f"the planted C repository did not reach A8: {world.chain_failed.describe()}"
    adoption = W.fork(world, name)
    log = Path(world.box.base) / f"{name}-queries.log"
    environment = {f"W2_88_F1_{key.upper()}": str(value) for key, value in settings.items()}
    adoption.extra_env.update(environment)
    adoption.extra_env["W2_88_F1_LOG"] = str(log)
    start = W.head(adoption.project)
    run = adoption.a9(Path(world.box.base) / f"{name}-out")
    W.assert_offered(run, "A9")
    return adoption, run, log, start


def queries(log: Path) -> list:
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.is_file() else []


def digits(text: str) -> str:
    """The text with the commas of 41,086 (and the spaces some write for thousands) taken out of numbers."""
    return re.sub(r"(?<=\d)[, _ ](?=\d{3}\b)", "", text)


def assert_nothing_left(adoption, start: str, run) -> None:
    """A refused A9 passed nothing: no ok on stdout, no A9 record, HEAD unmoved, A9's copies taken back."""
    project = adoption.project
    assert not run.prints_ok, f"A9 printed ok\n{run.describe()}"
    assert '"ok": true' not in run.stdout.replace('":true', '": true'), f"A9's output says ok: true\n{run.describe()}"
    assert W.head(project) == start, "A9 moved HEAD though it was refused"
    names = [n for n in W.git(project, "ls-files", "governance/adoption").splitlines() if "/A9" in n]
    assert not names, f"A9 committed a record ({names}) though it was refused: a record that names no 0-node pass is not one"
    left = [target for target, _source in W.copy_plan() if (project / target).exists()]
    assert not left, f"A9 was refused and left its copies in the tree: {left[:4]}"
    assert W.git(project, "status", "--porcelain", "--untracked-files=all").strip() == "", "the tree is not clean after A9's refusal"


# ------------------------------------------------------------------------------------------------------------
# Run 8 (package 2 (a)): a graph over the cap whose every type and label is within it is read by type; A9 completes
# ------------------------------------------------------------------------------------------------------------

def spec(parts: dict) -> str:
    """``{"USAGE": 60000}`` as the stand-in's setting ``USAGE=60000``."""
    return ",".join(f"{name}={count}" for name, count in parts.items())


# redis's figures (the lead's probe, run 8 item 7): 41,086 nodes over labels, 142,983 edges over 20 types, the largest USAGE 40,849.
REDIS_TYPES = {"USAGE": 40849, "CALLS": 29000, "IMPORTS": 15000, "READS": 12000, "WRITES": 10000, "REFERENCES": 8000, "RETURNS": 6000,
               "TAKES": 5000, "INCLUDES": 4000, "CASTS": 3000, "ASSIGNS": 2500, "EXPANDS": 2000, "OVERRIDES": 1500, "INHERITS": 1200,
               "IMPLEMENTS": 1000, "THROWS": 800, "TESTS": 600, "CONFIGURES": 400, "MEMBER_OF": 134}
REDIS_LABELS = {"Function": 20000, "Variable": 9000, "Field": 6000, "Macro": 4000, "Struct": 2086}

WITHIN_THE_CAP = [
    pytest.param(REDIS_LABELS, REDIS_TYPES, id="redis-figures-edges-over-the-cap"),
    pytest.param({"Function": 60000, "Variable": 45000}, {"USAGE": 60000, "CALLS": 50000, "IMPORTS": 40000}, id="nodes-and-edges-over-the-cap"),
    pytest.param({"Function": 30000}, {"USAGE": 100_000, "CALLS": 5000}, id="one-type-exactly-at-the-cap"),
]


@pytest.mark.parametrize("labels,types", WITHIN_THE_CAP)
def test_s25_a_graph_over_the_cap_whose_every_type_and_label_is_within_it_is_read_whole_and_a9_completes(c_world, labels, types):
    """success-S25 (run 8 items 8-10, DEC-1183 package 2 (a); revises run 7's case that expected ``CODEGRAPH_TOO_LARGE`` for redis's figures,
    Rewrite-Reason: DEC-1183, package 2 (a)): the stand-in's planted graph (generated rows: every node's file a staged file, every edge unique)
    is over the tool's cap of 100,000 rows in edges (redis's figures: 41,086 nodes, 142,983 edges in 19 types, the largest 40,849), in nodes and
    edges (105,000 nodes in two labels, 150,000 edges in three types), or has one type of exactly 100,000 (the cap is exceeded, not reached).
    Any one query whose result exceeds 100,000 rows is refused as the real tool refuses it; ``SKIP``/``LIMIT`` answers short. A9 completes (exit
    0, ok) and its record's code graph holds the planted totals of nodes and edges; A9 asked no ``SKIP``/``LIMIT`` query and no query of its
    was refused for the cap."""
    nodes, edges = sum(labels.values()), sum(types.values())
    assert edges > CAP or nodes > CAP, "the plant: the graph is not over the cap"
    assert max([*labels.values(), *types.values()]) <= CAP, "the plant: a type or label is over the cap"
    adoption, run, log, _start = a9_with(c_world, f"f1-within-{nodes}-{edges}", labels=spec(labels), types=spec(types))
    assert CODE not in W.error_text(run), f"A9 is refused {CODE} for a graph whose every type and label is within the cap\n{run.describe()}"
    W.assert_ok(run, f"A9 on a code graph of {nodes} nodes and {edges} edges, every type and label within the cap")
    assert run.returncode == 0, f"A9 exited {run.returncode}\n{run.describe()}"
    store = (W.a9_record(adoption.project, run).get("stores") or {}).get("codegraph") or {}
    assert store.get("nodes") == nodes and store.get("edges") == edges, (
        f"the record's code graph holds {store.get('nodes')} nodes and {store.get('edges')} edges, the planted graph {nodes} and {edges}: {store!r}")
    asked = queries(log)
    paged = [q["query"] for q in asked if re.search(r"\b(SKIP|LIMIT)\b", q["query"], re.I)]
    assert not paged, f"A9's read paged by SKIP/LIMIT (not a sound page: the tool answers it short): {paged[:3]}"
    refused = [q["query"] for q in asked if q.get("rows") == "error"]
    assert not refused, f"a query of A9's read was refused by the tool (over its cap): {refused[:3]}"


# ------------------------------------------------------------------------------------------------------------
# Run 8: a type or label over the cap is refused by name; a read that ends short is refused
# ------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("labels,types,kind,count", [
    pytest.param({"Function": 30000}, {"USAGE": 100_001, "CALLS": 20000}, "USAGE", 100_001, id="an-edge-type-one-over"),
    pytest.param({"Method": 100_001, "Function": 2000}, {"CALLS": 50000, "USAGE": 10000}, "Method", 100_001, id="a-node-label-one-over"),
])
def test_s25_a_type_or_label_over_the_cap_is_refused_codegraph_too_large_naming_it_and_its_count(c_world, labels, types, kind, count):
    """success-S25 (run 8 item 9): one edge type (or node label) of 100,001 rows cannot be read under the cap by type. A9 is refused
    ``CODEGRAPH_TOO_LARGE``: the message names ``codebase-memory-mcp``, the cap of 100,000, the type (or label) and its count (100,001);
    ``details`` hold ``nodes`` and ``edges`` (the planted totals), ``cap`` (100000), ``tool`` and ``kind`` (the type or label). Never ok, never
    0 nodes and edges; no record; HEAD unmoved; A9's copies taken back."""
    nodes, edges = sum(labels.values()), sum(types.values())
    adoption, run, _log, start = a9_with(c_world, f"f1-over-{kind}", labels=spec(labels), types=spec(types))
    W.assert_refused(run, CODE, f"A9 on a code graph whose {kind} holds {count} rows")
    error = run.error
    message = digits(str(error.get("message", "")))
    assert TOOL in message, f"the message does not name the tool {TOOL!r}: {message!r}"
    assert "100000" in message, f"the message does not name the tool's cap of 100,000 rows: {message!r}"
    assert kind in message, f"the message does not name the type or label over the cap ({kind}): {message!r}"
    assert str(count) in message, f"the message does not name {kind}'s count ({count}): {message!r}"
    details = error.get("details") or {}
    assert details.get("kind") == kind, f"details.kind is {details.get('kind')!r}, expected {kind!r}: {details!r}"
    assert details.get("nodes") == nodes and details.get("edges") == edges, f"details.nodes/edges, expected {nodes}/{edges}: {details!r}"
    assert details.get("cap") == CAP and details.get("tool") == TOOL, f"details.cap/tool: {details!r}"
    assert_nothing_left(adoption, start, run)


@pytest.mark.parametrize("labels,types,short,counted", [
    pytest.param({"Function": 20000}, {"USAGE": 50000, "CALLS": 40000, "IMPORTS": 30000}, ("CALLS", 7), 40000, id="an-edge-type-read-short"),
    pytest.param({"Function": 60000, "Variable": 45000}, {"CALLS": 20000}, ("Variable", 7), 45000, id="a-node-label-read-short"),
])
def test_s25_a_typed_read_that_answers_fewer_rows_than_its_count_is_refused_fabric_incomplete(c_world, labels, types, short, counted):
    """success-S25 (run 8 item 9, never a silent partial count): a graph over the cap (so it is read by type or label), whose typed match of
    ``CALLS`` (or label match of ``Variable``) answers 7 rows fewer than its count. A9 is refused ``FABRIC_INCOMPLETE`` naming the store
    (``codegraph``), the type (or label) and both figures (its count and the rows read); never ``CODEGRAPH_TOO_LARGE``; never ok; no record;
    HEAD unmoved; A9's copies taken back."""
    kind, fewer = short
    adoption, run, _log, start = a9_with(c_world, f"f1-short-{kind}", labels=spec(labels), types=spec(types), short=f"{kind}={fewer}")
    W.assert_refused(run, "FABRIC_INCOMPLETE", f"A9 where the read of {kind} ends {fewer} rows short of its count")
    text = digits(W.error_text(run))
    assert "codegraph" in text, f"the refusal does not name the store (codegraph): {text!r}"
    assert kind in text, f"the refusal does not name the type or label read short ({kind}): {text!r}"
    assert str(counted) in text and str(counted - fewer) in text, f"the refusal does not name both figures ({counted} counted, {counted - fewer} read): {text!r}"
    assert CODE not in text, f"the refusal is {CODE} for a read that ended short: {text!r}"
    assert_nothing_left(adoption, start, run)


@pytest.mark.parametrize("counts,expected", [
    pytest.param((100_001, 10), True, id="nodes-one-over"),
    pytest.param((10, 100_001), True, id="edges-one-over"),
    pytest.param((100_000, 100_000), False, id="both-exactly-at-the-cap"),
    pytest.param((1_200, 3_400), False, id="both-well-under"),
])
def test_s25_either_count_over_the_cap_makes_it_codegraph_too_large_and_at_the_cap_it_does_not(c_world, counts, expected):
    """success-S25 (the edges of the rule): the read fails for a reason that is not the cap (``database is locked``) and the counts are 100,001 nodes
    (or edges) against 10: ``CODEGRAPH_TOO_LARGE`` with ``details.nodes`` and ``details.edges`` the counts; at exactly 100,000 each, or well under,
    the read failed for another reason and A9 keeps ``FABRIC_INCOMPLETE`` (the cap is exceeded, not reached)."""
    nodes, edges = counts
    adoption, run, _log, start = a9_with(c_world, f"f1-edge-{nodes}-{edges}", nodes=nodes, edges=edges, read="locked")
    if expected:
        W.assert_refused(run, CODE, f"A9 with {nodes} nodes and {edges} edges")
        details = run.error.get("details") or {}
        assert details.get("nodes") == nodes and details.get("edges") == edges and details.get("cap") == CAP, f"details: {details!r}"
    else:
        W.assert_refused(run, "FABRIC_INCOMPLETE", f"A9 with {nodes} nodes and {edges} edges and a read that failed")
        assert CODE not in W.error_text(run), f"the refusal names {CODE} for counts that do not exceed the cap\n{run.describe()}"
    assert_nothing_left(adoption, start, run)


# ------------------------------------------------------------------------------------------------------------
# Another failure keeps today's refusal; a graph under the cap is read as today
# ------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("counts", ["answer", "fail"])
def test_s25_a_read_that_fails_for_another_reason_keeps_fabric_incomplete_with_the_error_text(c_world, counts):
    """success-S25 (any other failure keeps today's ``FABRIC_INCOMPLETE``): the whole-graph read fails with ``database is locked``; the counts are small
    (they answer) or the count queries fail too. A9 is refused ``FABRIC_INCOMPLETE`` naming the store (``codegraph``) and the error text
    (``query_graph failed``); never ``CODEGRAPH_TOO_LARGE``; never ok (a failed read is never a pass and never 0 nodes and edges)."""
    settings = {"nodes": 20, "edges": 40, "read": "locked"} | ({"counts": "fail"} if counts == "fail" else {})
    adoption, run, _log, start = a9_with(c_world, f"f1-other-{counts}", **settings)
    W.assert_refused(run, "FABRIC_INCOMPLETE", f"A9 where the code graph's read failed for a reason that is not the cap (counts {counts})")
    text = W.error_text(run)
    assert "codegraph" in text, f"the refusal does not name the store (codegraph): {text!r}"
    assert "query_graph failed" in text, f"the refusal does not carry the error text of the failed read: {text!r}"
    assert CODE not in text, f"the refusal is {CODE} for a read that failed for another reason: {text!r}"
    assert_nothing_left(adoption, start, run)


def test_s25_a_graph_under_the_cap_is_read_and_checked_as_today(c_world):
    """success-S25 (GUARD: green on the base): the stand-in answers every query, the graph is small (the chain's files make about a dozen nodes);
    A9 is not refused ``CODEGRAPH_TOO_LARGE``, no ``FABRIC_INCOMPLETE`` names the code graph, and A9 is ok with its record's code-graph store
    holding the graph's nodes and edges (a read graph is never 0 nodes and 0 edges)."""
    adoption, run, _log, _start = a9_with(c_world, "f1-small", read="ok")
    assert CODE not in W.error_text(run), f"A9 is refused {CODE} for a graph under the cap\n{run.describe()}"
    W.assert_ok(run, "A9 on a code graph under the tool's cap")
    record = W.a9_record(adoption.project, run)
    store = (record.get("stores") or {}).get("codegraph") or {}
    assert (store.get("nodes") or 0) > 0 and (store.get("edges") or 0) > 0, f"the record's code graph holds no nodes or edges: {store!r}"


# ------------------------------------------------------------------------------------------------------------
# The real tool on a copy of redis: the lead runs it outside the sandbox
# ------------------------------------------------------------------------------------------------------------

REDIS = Path.home() / "gov-os-runs" / "W2-88" / "redis"


@pytest.mark.real
@pytest.mark.skipif(not REDIS.is_dir(), reason="no copy of redis under ~/gov-os-runs/W2-88/ on this machine")
def test_s25_real_redis_copy_a9_is_ok_or_names_the_cause(box, host):
    """success-S25 (the real tool; the lead runs it outside the sandbox; not run by the whole-folder runs: its name holds ``real``): A9 on a fresh
    copy of ``~/gov-os-runs/W2-88/redis`` (W2-88b's, at A8's commit) made in tmp, with the real ``codebase-memory-mcp`` on PATH. Exit 0, or
    the refusal ``CODEGRAPH_TOO_LARGE`` naming 41,086 and 143,008 (the graph is the same one); never ``FABRIC_INCOMPLETE`` with ``exit code 0``."""
    copy = Path(box.base) / "redis"
    shutil.copytree(REDIS, copy, symlinks=True)
    adoption = W.Adoption(copy, box, host, code_graph=True)
    run = adoption.a9(Path(box.base) / "redis-out")
    if run.returncode == 0:
        assert run.prints_ok, run.describe()
        return
    W.assert_refused(run, CODE, "A9 on the copy of redis")
    assert "exit code 0" not in W.error_text(run), run.describe()
    details = run.error.get("details") or {}
    assert details.get("nodes", 0) > 0 and details.get("edges", 0) > 0, f"details: {details!r}"
