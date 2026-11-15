"""S25 (F-1, DEC-1178) and S28 (DEC-1185): redis's code graph, read in bounded pieces by source file for any repository size.

Run 7 (S25): the smoke run's finding F-1 (``experiments/W2-88/smoke-run.md``): A9 on a copy of redis refused ``FABRIC_INCOMPLETE``
(``codegraph: RuntimeError: codebase-memory-mcp query_graph failed (exit code 0)``): the tool's ``query_graph`` refuses a query whose result
exceeds 100,000 rows, before its own paging. Run 8 (DEC-1183, package 2 (a)) read the graph by edge type and refused a type over 100,000.

Run 8b (DEC-1185, the owner's change of package 2; S28 and its failure line; the run 8b interface items 13-24, which replace run 8's items
8-10): ``gov.codeintel`` reads the links in pieces by source path, because the tool cannot page soundly by a key (a string comparison in
``WHERE`` answers 0 rows, ``type()``/``id()`` in ``WHERE`` are refused, ``IN`` and ``STARTS WITH`` are refused, answers are cut by size
silently with ``has_more`` false, ``SKIP``/``LIMIT`` is unsound). (i) the total by ``type(r), count(r)``; (ii) the source paths from each
label's path list (each counted first and checked; the File list, if cut or over the cap, read per Folder and Branch by ``CONTAINS_FILE``);
(iii) per path its count, then its links (``id(r)`` among the columns); a file over 100,000 links or read short is read again by link type
within the file; a (file, type) piece over 100,000 is ``CODEGRAPH_TOO_LARGE`` (naming the file, the type and its count; ``details.kind``,
``details.file``), one read short ``FABRIC_INCOMPLETE`` (naming ``codegraph``, the file, the type and both figures); (iv) labels with no
string path (``Project``, ``Branch``) by source label. Each link once; the pieces' counts sum to the total. A refresh reads again only the
links of files whose content changed since the last good read. A single link type over 100,000 is read.

The seam: the tool's answers. ``standin_f1/tool.py`` is copied as ``codebase-memory-mcp`` into a folder first on the child's ``PATH``; it is a
small Cypher reader over a generated graph that answers and refuses as items 13-14 say the real tool does (its docstring). Its graph comes from
the staged files and the case's plan (``W2_88_F1_PLAN``); it logs every query (``W2_88_F1_LOG``: the rows served, the ``id(r)`` values, the
source file filtered on) and writes the planted totals beside the log. The plant is a C repository with a vendored folder (``src/``,
``deps/<lib>/``), code intelligence called for, the suite's chain A0 to A8 run once per module and forked per case.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
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
INCOMPLETE = "FABRIC_INCOMPLETE"
ERROR_CAP = "result exceeded 100k rows"
C_FILES = {
    "src/server.c": "#include \"server.h\"\n\nint serve(int port) {\n    return port + start();\n}\n\nint start(void) {\n    return 1;\n}\n",
    "src/server.h": "int serve(int port);\nint start(void);\n",
    "src/util.c": "#include \"server.h\"\n\nint helper(int n) {\n    return serve(n) * 2;\n}\n",
    "deps/lua/src/lapi.c": "/* Vendored from lua 5.1, kept as published. */\nint lua_gettop(void) {\n    return 0;\n}\n",
    "deps/lua/src/lauxlib.c": "/* Vendored from lua 5.1, kept as published. */\nint luaL_error(void) {\n    return 1;\n}\n",
    "deps/hiredis/hiredis.c": "/* Vendored from hiredis, kept as published. */\nint redisConnect(void) {\n    return 2;\n}\n",
    "deps/README.md": "# deps\n\nThe vendored libraries of the harbour's server, kept as published.\n",
}
CODE_FILES = sorted(rel for rel in C_FILES if rel.endswith((".c", ".h")))


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
                          extra_env={"CODEINTEL_DAEMON_BASE": str(Path(base) / "cbm")})
    failed = adoption.chain("A8")
    world = SimpleNamespace(box=box, project=project, adoption=adoption, chain_failed=failed, tool=tool)
    try:
        yield world
    finally:
        shutil.rmtree(base, ignore_errors=True)


def fork(world, name: str):
    assert world.chain_failed is None, f"the planted C repository did not reach A8: {world.chain_failed.describe()}"
    return W.fork(world, name)


def run_a9(world, adoption, name: str, plan: dict | None = None):
    """A9 once on ``adoption`` with the stand-in's plan; ``(run, log, start)``; the log is this run's alone."""
    base = Path(world.box.base)
    log = base / f"{name}-queries.log"
    for stale in (log, Path(str(log) + ".graph.json")):
        stale.unlink(missing_ok=True)
    where = base / f"{name}-plan.json"
    where.write_text(json.dumps(plan or {}), encoding="utf-8")
    adoption.extra_env.update({"W2_88_F1_PLAN": str(where), "W2_88_F1_LOG": str(log)})
    start = W.head(adoption.project)
    run = adoption.a9(base / f"{name}-out")
    W.assert_offered(run, "A9")
    return run, log, start


def a9_with(world, name: str, plan: dict | None = None):
    """A fork of the planted repository at A8, A9 run once with the plan; ``(adoption, run, log, start)``."""
    adoption = fork(world, name)
    run, log, start = run_a9(world, adoption, name, plan)
    return adoption, run, log, start


def queries(log: Path) -> list:
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.is_file() else []


def planted(log: Path) -> dict:
    """The graph the stand-in answered with: ``{"nodes", "links", "by_type", "files"}``."""
    where = Path(str(log) + ".graph.json")
    assert where.is_file(), f"the stand-in wrote no graph summary beside {log.name}: A9 never asked the tool"
    return json.loads(where.read_text(encoding="utf-8"))


def digits(text: str) -> str:
    """The text with the commas of 41,086 (and the spaces some write for thousands) taken out of numbers."""
    return re.sub(r"(?<=\d)[, _ ](?=\d{3}\b)", "", text)


def codegraph(adoption, run) -> dict:
    return (W.a9_record(adoption.project, run).get("stores") or {}).get("codegraph") or {}


def find_key(value, key: str):
    """The first value under ``key`` anywhere in a nested record (None where there is none)."""
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for item in value.values():
            found = find_key(item, key)
            if found is not None:
                return found
    if isinstance(value, list):
        for item in value:
            found = find_key(item, key)
            if found is not None:
                return found
    return None


def a9_records(project) -> list:
    return [n for n in W.git(project, "ls-files", "governance/adoption").splitlines() if "/A9" in n]


def last_good(project) -> dict:
    """What a good A9 left before a later run: its record and its copies, ``{path: bytes}``, and the record's last commit."""
    paths = [*a9_records(project), *(target for target, _source in W.copy_plan() if (project / target).exists())]
    commit = W.git(project, "log", "-1", "--format=%H", "--", "governance/adoption").strip()
    return {"files": {rel: (project / rel).read_bytes() for rel in paths}, "record_commit": commit}


def assert_nothing_left(adoption, start: str, run) -> None:
    """A refused A9 passed nothing: no ok on stdout, no A9 record, HEAD unmoved, A9's copies taken back."""
    project = adoption.project
    assert not run.prints_ok, f"A9 printed ok\n{run.describe()}"
    assert '"ok": true' not in run.stdout.replace('":true', '": true'), f"A9's output says ok: true\n{run.describe()}"
    assert W.head(project) == start, "A9 moved HEAD though it was refused"
    names = a9_records(project)
    assert not names, f"A9 committed a record ({names}) though it was refused: a record that names no 0-node pass is not one"
    left = [target for target, _source in W.copy_plan() if (project / target).exists()]
    assert not left, f"A9 was refused and left its copies in the tree: {left[:4]}"
    assert W.git(project, "status", "--porcelain", "--untracked-files=all").strip() == "", "the tree is not clean after A9's refusal"


def assert_last_good_kept(adoption, start: str, run, good: dict) -> None:
    """A refused A9 after a good one passed nothing: no ok on stdout, HEAD unmoved, the good run's A9 record as it wrote it (its bytes
    unchanged, no new record commit), the good run's copies as they were and no other copy left, the tree clean."""
    project = adoption.project
    assert not run.prints_ok, f"A9 printed ok\n{run.describe()}"
    assert '"ok": true' not in run.stdout.replace('":true', '": true'), f"A9's output says ok: true\n{run.describe()}"
    assert W.head(project) == start, "A9 moved HEAD though it was refused"
    records = a9_records(project)
    kept = [rel for rel in good["files"] if "/A9" in rel and rel.startswith("governance/adoption")]
    assert kept, "the plant: the good first A9 left no A9 record under governance/adoption/"
    assert records == kept, f"the refused A9 changed the A9 records: {records} after it, {kept} after the good run"
    commit = W.git(project, "log", "-1", "--format=%H", "--", "governance/adoption").strip()
    assert commit == good["record_commit"], f"the refused A9 committed under governance/adoption/ ({commit}, the good run's {good['record_commit']})"
    changed = [rel for rel, data in good["files"].items() if not (project / rel).is_file() or (project / rel).read_bytes() != data]
    assert not changed, f"the refused A9 changed what the good A9 left (its record or its copies): {changed[:4]}"
    left = [target for target, _source in W.copy_plan() if (project / target).exists() and target not in good["files"]]
    assert not left, f"A9 was refused and left copies in the tree the good run had not: {left[:4]}"
    assert W.git(project, "status", "--porcelain", "--untracked-files=all").strip() == "", "the tree is not clean after A9's refusal"


def assert_read_whole(adoption, run, log, what: str) -> dict:
    """A9 completed; its record's code graph holds the planted nodes and links; no query answered over 100,000 rows or was refused for
    the cap; the links read sum to the total, each ``id(r)`` once (no link read twice, none missed). The planted graph is returned."""
    assert CODE not in W.error_text(run), f"{what}: A9 is refused {CODE} for a graph the pieces can read\n{run.describe()}"
    W.assert_ok(run, what)
    assert run.returncode == 0, f"{what}: A9 exited {run.returncode}\n{run.describe()}"
    graph = planted(log)
    store = codegraph(adoption, run)
    assert store.get("nodes") == graph["nodes"] and store.get("edges") == graph["links"], (
        f"{what}: the record's code graph holds {store.get('nodes')} nodes and {store.get('edges')} links, the planted graph "
        f"{graph['nodes']} and {graph['links']}: {store!r}")
    asked = queries(log)
    over = [q["query"] for q in asked if isinstance(q.get("rows"), int) and q["rows"] > CAP]
    assert not over, f"{what}: a query answered more than 100,000 rows: {over[:3]}"
    capped = [q["query"] for q in asked if ERROR_CAP in str(q.get("error", ""))]
    assert not capped, f"{what}: the tool refused a query of A9's read for its cap of 100,000 rows: {capped[:3]}"
    return graph


def assert_each_link_once(log, graph: dict, what: str) -> None:
    """The links reads served each planted link exactly once (by rows served and by ``id(r)``)."""
    reads = [q for q in queries(log) if q.get("links")]
    served = sum(q.get("served", 0) for q in reads)
    ids = [identity for q in reads for identity in q.get("ids", [])]
    assert served == graph["links"], (
        f"{what}: the links reads served {served} rows for a graph of {graph['links']} links (a link read twice or missed)")
    assert len(ids) == len(set(ids)) == graph["links"], (
        f"{what}: {len(ids)} id(r) values served, {len(set(ids))} distinct, for {graph['links']} links (each link exactly once)")


def links_reads_of(log, file: str) -> list:
    return [q for q in queries(log) if q.get("links") and q.get("file") == file]


def code_links(per_file: dict, functions: int = 200) -> dict:
    """A plan: ``per_file`` links by type for some code files (the rest one ``CALLS`` each), ``functions`` code nodes per file."""
    return {"functions": functions, "links": per_file}


# ------------------------------------------------------------------------------------------------------------
# S28 (a), (b): one link type of 250,000 links; one source file of 120,000 links: read whole
# ------------------------------------------------------------------------------------------------------------

TYPE_OF_250K = {"src/server.c": {"USAGE": 90_000}, "src/util.c": {"USAGE": 80_000}, "deps/lua/src/lapi.c": {"USAGE": 50_000},
                "deps/hiredis/hiredis.c": {"USAGE": 30_000}}
FILE_OF_120K = {"src/server.c": {"USAGE": 70_000, "CALLS": 50_000}, "src/util.c": {"CALLS": 3_000}}


def test_s28_a_one_link_type_of_250000_links_spread_over_files_is_read_whole(c_world):
    """success-S28 (a), S28's failure (a single type over 100,000 refused; a link read twice or missed; a page over 100,000): one link
    type, ``USAGE``, of 250,000 links spread over four source files (90,000, 80,000, 50,000 and 30,000, each under 100,000). A9 completes
    (exit 0, ok); its record's code graph holds the planted nodes and links; no query answered more than 100,000 rows; the links reads served
    each link once (rows served and distinct ``id(r)`` equal to the total); the record gives the read's wall time (``read_seconds``)."""
    adoption, run, log, _start = a9_with(c_world, "s28-a", code_links(TYPE_OF_250K))
    graph = assert_read_whole(adoption, run, log, "A9 on a graph with one link type of 250,000 links")
    assert graph["by_type"].get("USAGE") == 250_000, f"the plant: USAGE holds {graph['by_type'].get('USAGE')} links"
    assert_each_link_once(log, graph, "one type of 250,000")
    seconds = find_key(W.a9_record(adoption.project, run), "read_seconds")
    assert isinstance(seconds, (int, float)) and seconds >= 0, f"the A9 record gives no read_seconds for the code graph's read: {seconds!r}"


def test_s28_b_one_source_file_of_120000_links_is_read_whole_by_type_within_the_file(c_world):
    """success-S28 (b): one source file, ``src/server.c``, of 120,000 links and more (``USAGE`` 70,000, ``CALLS`` 50,000, its ``DEFINES``),
    each type under 100,000. A9 completes with the planted totals, no query over 100,000 rows, each link once; the file's links were read by
    type within the file (a typed read filtered on ``src/server.c``)."""
    adoption, run, log, _start = a9_with(c_world, "s28-b", code_links(FILE_OF_120K))
    graph = assert_read_whole(adoption, run, log, "A9 on a graph with one source file of 120,000 links")
    assert_each_link_once(log, graph, "one file of 120,000")
    typed = {q.get("type") for q in links_reads_of(log, "src/server.c") if q.get("served")}
    assert {"USAGE", "CALLS"} <= typed, f"src/server.c's links were not read by type within the file: typed reads {sorted(t or '' for t in typed)}"


# ------------------------------------------------------------------------------------------------------------
# S28 (c), (d): a (file, type) piece over the cap is refused by name; a short file read is read again by type; a short typed read refused
# ------------------------------------------------------------------------------------------------------------

def test_s28_c_a_file_and_type_piece_over_100000_links_is_refused_codegraph_too_large_naming_the_file_the_type_and_its_count(c_world):
    """success-S28 (c) (a graph the tool cannot page soundly refuses by name): ``src/server.c`` holds 100,001 ``USAGE`` links, one (file,
    type) piece over the cap. A9 is refused ``CODEGRAPH_TOO_LARGE``: the message names the tool, the cap (100,000), the file, the type and
    its count (100,001); ``details.kind`` is ``USAGE``, ``details.file`` ``src/server.c``, ``details.cap`` 100000; never ok, never 0 nodes and
    links; no record; HEAD unmoved."""
    adoption, run, _log, start = a9_with(c_world, "s28-c", code_links({"src/server.c": {"USAGE": 100_001, "CALLS": 1_000}}))
    W.assert_refused(run, CODE, "A9 where src/server.c holds 100,001 USAGE links")
    message = digits(str(run.error.get("message", "")))
    for part, what in ((TOOL, "the tool"), ("100000", "the cap"), ("src/server.c", "the file"), ("USAGE", "the type"), ("100001", "its count")):
        assert part in message, f"the message does not name {what} ({part}): {message!r}"
    details = run.error.get("details") or {}
    assert details.get("kind") == "USAGE" and details.get("file") == "src/server.c", f"details.kind/file: {details!r}"
    assert details.get("cap") == CAP and details.get("tool") == TOOL, f"details.cap/tool: {details!r}"
    assert (details.get("nodes") or 0) > 0 and (details.get("edges") or 0) > 0, f"details hold 0 nodes or links: {details!r}"
    assert_nothing_left(adoption, start, run)


FILE_50K = {"src/server.c": {"USAGE": 30_000, "CALLS": 20_000}}


def test_s28_d_a_file_read_cut_short_whose_typed_reads_are_whole_is_read_again_by_type_and_a9_completes(c_world):
    """success-S28 (d), the size cut (item 16): ``src/server.c`` (50,200 links: ``USAGE`` 30,000, ``CALLS`` 20,000, ``DEFINES``) answers its
    links read 5,000 rows short of its count with ``has_more`` false; its typed reads are whole. A9 completes with the planted totals (the
    reader read the file again by type), no query over 100,000 rows."""
    plan = code_links(FILE_50K) | {"cut": [{"piece": "file", "file": "src/server.c", "by": 5_000}]}
    adoption, run, log, _start = a9_with(c_world, "s28-d-file", plan)
    assert_read_whole(adoption, run, log, "A9 where src/server.c's links read is cut 5,000 rows short")
    typed = {q.get("type") for q in links_reads_of(log, "src/server.c") if q.get("type")}
    assert {"USAGE", "CALLS"} <= typed, f"the cut file was not read again by type: typed reads of src/server.c {sorted(typed)}"


def test_s28_d_a_file_and_type_read_cut_short_is_refused_fabric_incomplete_naming_the_file_the_type_and_both_figures(c_world):
    """success-S28 (d), never a partial read (item 16): ``src/server.c``'s links read and its typed read of ``USAGE`` (30,000) are both cut
    short (by 5,000 and by 7). A9 is refused ``FABRIC_INCOMPLETE`` naming the store (``codegraph``), the file, the type and both figures
    (30,000 counted, 29,993 read); never ``CODEGRAPH_TOO_LARGE``; never ok; no record; HEAD unmoved."""
    plan = code_links(FILE_50K) | {"cut": [{"piece": "file", "file": "src/server.c", "by": 5_000},
                                            {"piece": "file-type", "file": "src/server.c", "type": "USAGE", "by": 7}]}
    adoption, run, _log, start = a9_with(c_world, "s28-d-type", plan)
    W.assert_refused(run, INCOMPLETE, "A9 where src/server.c's USAGE read ends 7 rows short of its count")
    text = digits(W.error_text(run))
    for part, what in (("codegraph", "the store"), ("src/server.c", "the file"), ("USAGE", "the type"), ("30000", "the count"),
                       ("29993", "the rows read")):
        assert part in text, f"the refusal does not name {what} ({part}): {text!r}"
    assert CODE not in text, f"the refusal is {CODE} for a read that ended short: {text!r}"
    assert_nothing_left(adoption, start, run)


# ------------------------------------------------------------------------------------------------------------
# S28 (e): the refresh reads again only the links of the files changed since the last good read
# ------------------------------------------------------------------------------------------------------------

REFRESH_BEFORE = {"src/server.c": {"USAGE": 4_000, "CALLS": 1_000}, "src/util.c": {"CALLS": 2_000}, "deps/lua/src/lapi.c": {"USAGE": 1_500},
                  "deps/lua/src/lauxlib.c": {"USAGE": 1_200}, "deps/hiredis/hiredis.c": {"CALLS": 900}, "src/server.h": {"USAGE": 300}}
CHANGED = ("deps/lua/src/lapi.c", "src/server.c", "src/util.c")
REFRESH_AFTER = REFRESH_BEFORE | {"src/server.c": {"USAGE": 4_500, "CALLS": 700}, "src/util.c": {"CALLS": 2_000, "USAGE": 250},
                                  "deps/lua/src/lapi.c": {"USAGE": 1_100}}


def change_three(adoption) -> None:
    """The three source files changed (a line appended to each) and committed: the tree is clean for the next A9."""
    for rel in CHANGED:
        path = adoption.project / rel
        path.write_text(path.read_text(encoding="utf-8") + "\nint changed_for_the_refresh(void) {\n    return 3;\n}\n", encoding="utf-8")
    W.commit_all(adoption.project, "three source files changed")


def assert_refreshed_only_the_changed(log, graph: dict, what: str) -> None:
    """No links read of the refresh takes an unchanged file's links: each is filtered on a changed file, on a path that is no file (a
    Folder's, ``<python-builtins>``), or by a source label with no string path (``Project``, ``Branch``); counts are free."""
    unchanged = [rel for rel in graph["files"] if rel not in CHANGED]
    reread = sorted({q["file"] for q in queries(log) if q.get("links") and q.get("file") in unchanged})
    assert not reread, f"{what}: the refresh asked the tool for the links of files that did not change: {reread}"
    wide = [q["query"] for q in queries(log) if q.get("links") and q.get("file") is None and q.get("source_label") not in ("Project", "Branch")]
    assert not wide, f"{what}: the refresh read links not filtered by a source path (so unchanged files' links again): {wide[:3]}"
    for rel in CHANGED:
        assert links_reads_of(log, rel), f"{what}: the refresh did not read the links of the changed file {rel}"


def test_s28_e_a_refresh_after_three_changed_files_reads_only_those_files_links(c_world):
    """success-S28 (e), S28's failure (a refresh that re-reads unchanged files' links): A9 once over a planted graph (six code files with
    links); then three source files change (their content and their links) and are committed; a second A9 (the refresh) asks the tool for
    the links of only those three files (counts may be asked; no links read filtered on an unchanged file), and its record's code graph holds
    the new graph's totals."""
    adoption = fork(c_world, "s28-e")
    run, log, _start = run_a9(c_world, adoption, "s28-e-1", code_links(REFRESH_BEFORE, functions=40))
    assert_read_whole(adoption, run, log, "the first A9 of the refresh case")
    change_three(adoption)
    run, log, _start = run_a9(c_world, adoption, "s28-e-2", code_links(REFRESH_AFTER, functions=40))
    graph = assert_read_whole(adoption, run, log, "the second A9 (the refresh) after three files changed")
    assert_refreshed_only_the_changed(log, graph, "the refresh")


def test_s28_e_a_failed_refresh_leaves_the_last_good_record_and_the_next_refreshes_what_changed_since_it(c_world):
    """success-S28 (e), item 18 (the record is written only after a read that passes): A9 once (good); three files change; the second A9's
    read of the last changed file in the fixed order (``src/util.c``) is cut short in its links read and in its typed read, so A9 is refused
    ``FABRIC_INCOMPLETE``; a third A9 with the tool whole reads again the links of all three files changed since the first read (not only the
    one the failed read did not reach), none of an unchanged file, and holds the new graph's totals."""
    adoption = fork(c_world, "s28-e-fail")
    run, log, _start = run_a9(c_world, adoption, "s28-ef-1", code_links(REFRESH_BEFORE, functions=40))
    assert_read_whole(adoption, run, log, "the first A9")
    change_three(adoption)
    broken = code_links(REFRESH_AFTER, functions=40) | {"cut": [{"piece": "file", "file": "src/util.c", "by": 3},
                                                                 {"piece": "file-type", "file": "src/util.c", "type": "CALLS", "by": 3}]}
    good = last_good(adoption.project)
    run, _log, start = run_a9(c_world, adoption, "s28-ef-2", broken)
    W.assert_refused(run, INCOMPLETE, "the second A9, whose read of src/util.c ends short")
    assert_last_good_kept(adoption, start, run, good)
    run, log, _start = run_a9(c_world, adoption, "s28-ef-3", code_links(REFRESH_AFTER, functions=40))
    graph = assert_read_whole(adoption, run, log, "the third A9 after a failed refresh")
    assert_refreshed_only_the_changed(log, graph, "the refresh after a failed one")


# ------------------------------------------------------------------------------------------------------------
# S28 (h), R8-2 (a) (run 8b item 25): a held link whose end is gone makes the record stale: every link is read again
# ------------------------------------------------------------------------------------------------------------

CALLER = "src/util.c"
START_C = "/* The server's start-up helpers. */\nint start_extra(void) {\n    return 4;\n}\n"
FOO_C = "\nint foo(void) {\n    return 5;\n}\n"
CALL_KEY = "helper-calls-foo"
CALL_ID = int(hashlib.sha1(f"call\0{CALL_KEY}".encode()).hexdigest()[:13], 16)  # the stand-in's id(r) of the call, keyed alone


def foo_plan(where: str, name: str = "foo") -> dict:
    """The stand-in's plan: ``helper`` in ``src/util.c`` calls ``name`` defined in ``where``; the call keeps its ``id(r)`` (keyed alone)."""
    return {"named": {where: [name], CALLER: ["helper"]},
            "calls": [{"key": CALL_KEY, "file": CALLER, "source": "helper", "type": "CALLS", "target": name}]}


def served_ids(log) -> set:
    return {identity for q in queries(log) if q.get("links") for identity in q.get("ids", [])}


@pytest.mark.parametrize("change", ["move", "rename"])
def test_s28_h_a_refresh_after_a_target_moves_to_another_file_rereads_every_link(c_world, change):
    """success-S28 (h), run 8b item 25 (the CTO's R8-2 (a) on the narrow check), S28's failure (a refresh that gives a stale graph): ``helper``
    in ``src/util.c`` calls ``foo`` in ``src/server.c``; A9 once (no record: every link read); then ``foo`` moves to ``src/start.c`` (``move``)
    or is renamed ``foo_renamed`` in ``src/server.c`` (``rename``), committed; ``src/util.c`` unchanged, the node and link counts unchanged, the
    call keeping its ``id(r)``. The second A9 (the refresh) finds the record's link ``code.src.util.helper -> code.src.server.foo`` ends on a
    node no longer in the graph, so the record is stale: A9 completes with the planted totals, the links of the unchanged ``src/util.c`` are
    read again from the tool (not taken from the record), every planted link's ``id(r)`` is served in this read, and the A9 record notes
    ``record_stale`` true and ``pieces_from_record`` 0."""
    adoption = fork(c_world, f"s28-h-{change}")
    project = adoption.project
    (project / "src" / "start.c").write_text(START_C, encoding="utf-8")
    (project / "src" / "server.c").write_text(C_FILES["src/server.c"] + FOO_C, encoding="utf-8")
    W.commit_all(project, "src/start.c added; foo defined in src/server.c")
    run, log, _start = run_a9(c_world, adoption, f"s28-h-{change}-1", foo_plan("src/server.c"))
    first = assert_read_whole(adoption, run, log, "the first A9 of the moved-target case")
    call_ids = {identity for q in links_reads_of(log, CALLER) for identity in q.get("ids", [])}
    assert CALL_ID in call_ids, f"the plant: the first A9 did not read helper's call to foo (id {CALL_ID}) among {CALLER}'s links"
    if change == "move":
        (project / "src" / "server.c").write_text(C_FILES["src/server.c"], encoding="utf-8")
        (project / "src" / "start.c").write_text(START_C + FOO_C, encoding="utf-8")
        after = foo_plan("src/start.c")
    else:
        (project / "src" / "server.c").write_text(C_FILES["src/server.c"] + FOO_C.replace("foo", "foo_renamed"), encoding="utf-8")
        after = foo_plan("src/server.c", "foo_renamed")
    W.commit_all(project, f"foo {'moved to src/start.c' if change == 'move' else 'renamed foo_renamed'}; src/util.c unchanged")
    run, log, _start = run_a9(c_world, adoption, f"s28-h-{change}-2", after)
    what = f"the refresh after foo's {change}"
    graph = assert_read_whole(adoption, run, log, what)
    code_types = ("CALLS", "DEFINES")  # the code links; A9's own committed record adds a File node and its CONTAINS_FILE link between runs
    assert [graph["by_type"].get(t) for t in code_types] == [first["by_type"].get(t) for t in code_types], (
        f"the plant: the {change} changed the code links' counts {first['by_type']} -> {graph['by_type']}")
    assert links_reads_of(log, CALLER), (
        f"{what}: the refresh asked the tool for no links of the unchanged {CALLER}: it took them from the record, whose link to "
        f"code.src.server.foo ends on a node no longer in the graph (the record is stale; every link must be read again)")
    ids = served_ids(log)
    assert call_ids <= ids, f"{what}: the links of {CALLER} read in the first A9 (call's id(r) kept) were not served again: {sorted(call_ids - ids)}"
    assert len(ids) == graph["links"], (
        f"{what}: {len(ids)} distinct id(r) values served for {graph['links']} links: a stale record's refresh reads every link again")
    record = W.a9_record(adoption.project, run)
    stale, from_record = find_key(record, "record_stale"), find_key(record, "pieces_from_record")
    assert stale is True, f"{what}: the A9 record does not note record_stale true (found {stale!r})"
    assert from_record == 0, f"{what}: the A9 record's pieces_from_record is {from_record!r}, not 0, for a stale record"


# ------------------------------------------------------------------------------------------------------------
# S28 (g): the File list larger than one answer (item 23): read per Folder and Branch; a cut Folder piece is refused by name
# ------------------------------------------------------------------------------------------------------------

def test_s28_g_a_file_list_cut_short_is_read_per_folder_and_branch_and_a9_completes(c_world):
    """success-S28 (g), the CTO's condition 1 (item 23): the stand-in cuts ``MATCH (n:File) RETURN n.file_path`` 2 rows short (``has_more``
    false); its graph holds Folder nodes whose paths are folders, a Branch node (path ``{}``) holding the root's files, and links out of
    Folders and the Branch, as on redis. A9 completes with the planted totals and asked the tool for File paths by ``CONTAINS_FILE``."""
    plan = code_links({"src/server.c": {"USAGE": 3_000}}, functions=20) | {"cut": [{"piece": "list", "label": "File", "by": 2}]}
    adoption, run, log, _start = a9_with(c_world, "s28-g", plan)
    assert_read_whole(adoption, run, log, "A9 where the File list is cut short")
    by_folder = [q["query"] for q in queries(log) if "CONTAINS_FILE" in q["query"] and q.get("rows") != "error"]
    assert by_folder, "A9 completed on a cut File list without reading the File paths per Folder and Branch (CONTAINS_FILE)"


def test_s28_g_a_folder_piece_also_cut_is_refused_by_name_never_a_partial_list(c_world):
    """success-S28 (g), item 23 (where no sound piece exists, refuse by name, never a partial list): the File list is cut and so is the
    ``CONTAINS_FILE`` piece of the folder ``deps/hiredis``. A9 is refused ``FABRIC_INCOMPLETE`` or ``CODEGRAPH_TOO_LARGE`` naming
    ``codegraph`` and the folder; never ok; no record; HEAD unmoved."""
    plan = code_links({"src/server.c": {"USAGE": 3_000}}, functions=20) | {
        "cut": [{"piece": "list", "label": "File", "by": 2}, {"piece": "folder", "file": "deps/hiredis", "by": 1}]}
    adoption, run, _log, start = a9_with(c_world, "s28-g-folder", plan)
    W.assert_offered(run, "A9")
    text = W.error_text(run)
    assert run.returncode != 0 and (INCOMPLETE in text or CODE in text), (
        f"A9 on a cut File list whose folder deps/hiredis's piece is also cut was not refused by name\n{run.describe()}")
    assert "codegraph" in text and "deps/hiredis" in text, f"the refusal does not name codegraph and the folder deps/hiredis: {text!r}"
    assert_nothing_left(adoption, start, run)


# ------------------------------------------------------------------------------------------------------------
# S28 (f): a reader that pages by a string cursor, IN, SKIP/LIMIT or a whole-graph read gets a partial or refused answer
# ------------------------------------------------------------------------------------------------------------

def ask_standin(tmp: Path, plan: dict, asked: list) -> list:
    """The stand-in over stdio on a staged folder of the C files: ``[(query, error or None, total, rows)]``."""
    staged = tmp / "files"
    for rel, text in C_FILES.items():
        (staged / rel).parent.mkdir(parents=True, exist_ok=True)
        (staged / rel).write_text(text, encoding="utf-8")
    (tmp / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
    env = dict(os.environ, CBM_CACHE_DIR=str(tmp / "home"), W2_88_F1_PLAN=str(tmp / "plan.json"))
    env.pop("W2_88_F1_LOG", None)
    subprocess.run([sys.executable, str(STANDIN), "cli", "--json", "index_repository", json.dumps({"repo_path": str(staged)})],
                   env=env, check=True, capture_output=True)
    server = subprocess.Popen([sys.executable, str(STANDIN)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, env=env)
    answers = []
    try:
        for number, query in enumerate(asked, 1):
            message = {"jsonrpc": "2.0", "id": number, "method": "tools/call",
                       "params": {"name": "query_graph", "arguments": {"query": query, "max_rows": 50_000, "offset": 0}}}
            server.stdin.write(json.dumps(message) + "\n")
            server.stdin.flush()
            result = json.loads(server.stdout.readline())["result"]
            text = result["content"][0]["text"]
            if result["isError"]:
                answers.append((query, text, None, None))
            else:
                body = json.loads(text)
                answers.append((query, None, body["total"], body["rows"]))
    finally:
        server.stdin.close()
        server.wait(30)
    return answers


def test_s28_f_guard_a_cursor_in_skip_limit_or_whole_graph_reader_gets_a_partial_or_refused_answer(tmp_path):
    """S28's failure (a page over 100,000; a link missed), GUARD (green on the base by design: it holds the stand-in to items 13-14, so the
    cases above cannot pass by an unsound reader): on the 250,000-link plant, the whole-graph links read and the whole-type read are refused
    for the cap; a string cursor ``WHERE a.file_path > "..."`` answers 0 rows; ``IN`` and ``STARTS WITH`` are refused; ``type(r)`` and
    ``id(r)`` in ``WHERE`` are refused with the real tool's text; a count grouped by file is refused; ``SKIP``/``LIMIT`` answers fewer rows
    than asked; the equality filter answers rows equal to its count."""
    links = "RETURN id(r), a.qualified_name, type(r), b.qualified_name"
    asked = [f"MATCH (a)-[r]->(b) {links}", f"MATCH (a)-[r:USAGE]->(b) {links}",
             f'MATCH (a)-[r]->(b) WHERE a.file_path > "deps/m" {links}',
             f'MATCH (a)-[r]->(b) WHERE a.file_path IN ["src/util.c"] {links}',
             f'MATCH (a)-[r]->(b) WHERE a.file_path STARTS WITH "src/" {links}',
             f'MATCH (a)-[r]->(b) WHERE type(r) = "USAGE" {links}', f"MATCH (a)-[r]->(b) WHERE id(r) > 5 {links}",
             "MATCH (a)-[r]->(b) RETURN a.file_path, count(r)", f"MATCH (a)-[r:USAGE]->(b) {links} SKIP 0 LIMIT 50000",
             'MATCH (a)-[r]->(b) WHERE a.file_path = "src/util.c" RETURN count(r)', f'MATCH (a)-[r]->(b) WHERE a.file_path = "src/util.c" {links}']
    got = ask_standin(tmp_path, code_links(TYPE_OF_250K), asked)
    whole, typed, cursor, inlist, starts, by_type, by_id, grouped, paged, count, rows = got
    assert ERROR_CAP in (whole[1] or "") and ERROR_CAP in (typed[1] or ""), f"a read over 100,000 rows was answered: {whole[1]!r}, {typed[1]!r}"
    assert cursor[1] is None and cursor[2] == 0, f"a string cursor answered {cursor[2]} rows (the real tool answers 0, silently)"
    assert inlist[1] and starts[1], "IN or STARTS WITH was answered"
    assert "unsupported function 'type' in WHERE" in (by_type[1] or "") and "unsupported function 'id' in WHERE" in (by_id[1] or ""), (
        f"type()/id() in WHERE were not refused with the real tool's text: {by_type[1]!r}, {by_id[1]!r}")
    assert grouped[1], "a count grouped by file was answered"
    assert paged[1] is None and paged[2] < 50_000, f"SKIP/LIMIT answered {paged[2]} of the 50,000 rows asked (it must answer short)"
    assert count[1] is None and rows[1] is None and rows[2] == count[3][0][0] == 80_000 + 200, (
        f"the equality filter's rows ({rows[2]}) do not equal its count ({count[3]})")


# ------------------------------------------------------------------------------------------------------------
# S25 revised to S28 (Rewrite-Reason: DEC-1185): a graph over the cap is read in pieces; a single type or label over the cap is read
# ------------------------------------------------------------------------------------------------------------

# redis's figures (run 8b item 20): 142,983 links; the largest file 4,995 links in the real graph, here spread over six code files.
REDIS_LINKS = {"src/server.c": {"USAGE": 25_000, "CALLS": 15_000, "READS": 6_000}, "src/util.c": {"USAGE": 15_849, "CALLS": 10_000},
               "deps/lua/src/lapi.c": {"CALLS": 12_000, "WRITES": 10_000}, "deps/lua/src/lauxlib.c": {"REFERENCES": 8_000, "RETURNS": 6_000},
               "deps/hiredis/hiredis.c": {"TAKES": 5_000, "INCLUDES": 4_000, "CASTS": 3_000}, "src/server.h": {"USAGE": 2_000, "MEMBER_OF": 134}}
WITHIN_THE_CAP = [
    pytest.param(REDIS_LINKS, id="redis-figures-edges-over-the-cap"),
    pytest.param({"src/server.c": {"USAGE": 60_000}, "src/util.c": {"USAGE": 40_000, "CALLS": 50_000}}, id="one-type-exactly-at-the-cap"),
]


@pytest.mark.parametrize("links", WITHIN_THE_CAP)
def test_s25_a_graph_over_the_cap_whose_every_type_and_label_is_within_it_is_read_whole_and_a9_completes(c_world, links):
    """success-S25 and success-S28 (revised in run 8b, Rewrite-Reason: DEC-1185: the plant is now spread over source files and the read is
    by source file): a graph over the tool's cap in links (redis-like: about 143,000 links in 11 types over six code files; or a type of
    exactly 100,000 over two files). A9 completes (exit 0, ok), its record holds the planted totals, no query over 100,000 rows, none refused
    for the cap, each link once; A9 asked no ``SKIP``/``LIMIT`` query."""
    adoption, run, log, _start = a9_with(c_world, f"f1-within-{sum(sum(v.values()) for v in links.values())}", code_links(links))
    graph = assert_read_whole(adoption, run, log, "A9 on a code graph over the cap in links")
    assert graph["links"] > CAP, "the plant: the graph is not over the cap"
    assert_each_link_once(log, graph, "a graph over the cap")
    paged = [q["query"] for q in queries(log) if re.search(r"\b(SKIP|LIMIT)\b", q["query"], re.I)]
    assert not paged, f"A9's read paged by SKIP/LIMIT (not a sound page: the tool answers it short): {paged[:3]}"


@pytest.mark.parametrize("plan,what", [
    pytest.param(code_links({"src/server.c": {"USAGE": 60_000}, "src/util.c": {"USAGE": 40_001, "CALLS": 2_000}}), "USAGE of 100,001 links",
                 id="an-edge-type-one-over"),
    pytest.param({"functions": 2, "labels": {"Method": 16_667}, "links": {"src/server.c": {"CALLS": 20_000}}}, "Method of 100,002 nodes",
                 id="a-node-label-one-over"),
])
def test_s28_a_single_type_or_label_over_the_cap_spread_over_files_is_read_and_a9_completes(c_world, plan, what):
    """success-S28 (a single link type over 100,000 is read; items 17 and 23), S28's failure (a graph the paging can read refused); revises
    run 8's case that refused a type or label over the cap (Rewrite-Reason: DEC-1185): one link type of 100,001 links spread over two
    files, or one node label (``Method``) of 100,002 nodes spread over the six code files whose paths are File paths (its path list is not
    needed: the File pieces sum to the total). A9 completes with the planted totals, no query over 100,000 rows, each link once."""
    adoption, run, log, _start = a9_with(c_world, f"s28-over-{what.split()[0]}", plan)
    graph = assert_read_whole(adoption, run, log, f"A9 on a graph with {what}")
    assert_each_link_once(log, graph, what)


# ------------------------------------------------------------------------------------------------------------
# Another failure keeps FABRIC_INCOMPLETE with the tool's error text; a graph under the cap is read as today
# ------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("plan", [
    pytest.param({"read": "locked"}, id="answer"),
    pytest.param({"read": "locked", "counts": "fail"}, id="fail"),
    pytest.param(code_links({"src/server.c": {"USAGE": 70_000}, "src/util.c": {"USAGE": 50_000}}) | {"read": "locked"},
                 id="answer-links-over-the-cap"),
])
def test_s25_a_read_that_fails_for_another_reason_keeps_fabric_incomplete_with_the_error_text(c_world, plan):
    """success-S25 (revised in run 8b, Rewrite-Reason: DEC-1185; the stand-in's counts and rows now agree, and run 7's case "either count over
    the cap makes it CODEGRAPH_TOO_LARGE" is folded in: under S28 a total over the cap is read in pieces, never refused for its size): every
    links read fails with ``database is locked`` (the counts answer, or fail too; the graph small, or 120,000 links over two files). A9 is
    refused ``FABRIC_INCOMPLETE`` naming the store (``codegraph``) and the tool's error text; never ``CODEGRAPH_TOO_LARGE``; never ok."""
    name = "f1-other-" + ("fail" if plan.get("counts") == "fail" else "answer") + ("-big" if plan.get("links") else "")
    adoption, run, _log, start = a9_with(c_world, name, plan)
    W.assert_refused(run, INCOMPLETE, "A9 where the code graph's read failed for a reason that is not the cap")
    text = W.error_text(run)
    assert "codegraph" in text, f"the refusal does not name the store (codegraph): {text!r}"
    assert "database is locked" in text, f"the refusal does not carry the tool's error text (database is locked): {text!r}"
    assert CODE not in text, f"the refusal is {CODE} for a read that failed for another reason: {text!r}"
    assert_nothing_left(adoption, start, run)


def test_s25_a_graph_under_the_cap_is_read_and_checked_as_today(c_world):
    """success-S25 (GUARD: green on the base): the stand-in answers every query, the graph is small (the chain's files: two functions per
    code file); A9 is not refused ``CODEGRAPH_TOO_LARGE``, and A9 is ok with its record's code-graph store holding the graph's nodes and
    links (a read graph is never 0 nodes and 0 links)."""
    adoption, run, log, _start = a9_with(c_world, "f1-small")
    assert CODE not in W.error_text(run), f"A9 is refused {CODE} for a graph under the cap\n{run.describe()}"
    W.assert_ok(run, "A9 on a code graph under the tool's cap")
    store = codegraph(adoption, run)
    assert (store.get("nodes") or 0) > 0 and (store.get("edges") or 0) > 0, f"the record's code graph holds no nodes or edges: {store!r}"


# ------------------------------------------------------------------------------------------------------------
# The real tool on a copy of redis: the lead runs it outside the sandbox
# ------------------------------------------------------------------------------------------------------------

REDIS = Path.home() / "gov-os-runs" / "W2-88" / "redis"
REDIS_A9_TIMEOUT_S = 2400   # run 8b (Rewrite-Reason: DEC-1185): under S28 A9 on redis completes, in 8 to 15 minutes (W2-124's 240 s cut it)


@pytest.mark.real
@pytest.mark.skipif(not REDIS.is_dir(), reason="no copy of redis under ~/gov-os-runs/W2-88/ on this machine")
def test_s25_real_redis_copy_a9_is_ok_or_names_the_cause(box, host):
    """success-S25 (the real tool; the lead runs it outside the sandbox; not run by the whole-folder runs: its name holds ``real``; revised in
    run 8b, Rewrite-Reason: DEC-1185: A9's limit is 2,400 s, not W2-124's 240 s, since under S28 A9 on redis completes, in 8 to 15 minutes): A9
    on a fresh copy of ``~/gov-os-runs/W2-88/redis`` (W2-88b's, at its latest adoption commit) made in tmp, with the real ``codebase-memory-mcp``
    on PATH. Exit 0, or the refusal ``CODEGRAPH_TOO_LARGE`` naming 41,086 and 143,008 (the graph is the same one); never ``FABRIC_INCOMPLETE``
    with ``exit code 0``."""
    copy = Path(box.base) / "redis"
    shutil.copytree(REDIS, copy, symlinks=True)
    adoption = W.Adoption(copy, box, host, code_graph=True)
    # adoption.a9's own call (the same arguments and session), with a limit that fits a completing A9 on redis
    run = W.S124.gov(copy, adoption.env(), "adopt", "--lite", "--stage", "A9", "--out", str(Path(box.base) / "redis-out"), "--json",
                     "--session", W.S124.ADOPTER, timeout=REDIS_A9_TIMEOUT_S)
    assert run.returncode is not None, f"A9 on the copy of redis did not end within {REDIS_A9_TIMEOUT_S} s\n{run.describe()}"
    if run.returncode == 0:
        assert run.prints_ok, run.describe()
        return
    W.assert_refused(run, CODE, "A9 on the copy of redis")
    assert "exit code 0" not in W.error_text(run), run.describe()
    details = run.error.get("details") or {}
    assert details.get("nodes", 0) > 0 and details.get("edges", 0) > 0, f"details: {details!r}"
