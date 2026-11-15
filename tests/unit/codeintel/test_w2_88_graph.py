"""W2-88 run 8b, S28 (DEC-1185): the code graph is read in bounded pieces by source path, each link exactly once.

Regression evidence only (DEC-136). ``codebase-memory-mcp`` refuses a query whose whole answer is over 100,000 rows,
cuts an answer short by its size silently, and answers no sound keyset cursor (the run 8b interface, items 13-14).
``gov.codeintel._graph`` asks the total by type, the labels and their path lists (each counted first, the File list per
Folder where it is cut), then one piece a source path by equality, by link type inside a piece cut or over the cap;
every piece's rows equal its count, the pieces' ids are distinct and sum to the total; a file unchanged since the last
read is taken from the record. The seam is the tool's answers: the stand-in of ``test_w2_88_standin_tool``.
"""
from __future__ import annotations

import os
import subprocess

import pytest

from gov import codeintel

from .test_w2_88_standin_tool import CAP_TEXT, plant


@pytest.fixture()
def graph(tmp_path, monkeypatch):
    """A repository root and a stand-in tool first on ``PATH``; ``graph(config)`` plants its answers and returns a
    reader of the queries it was asked since."""
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    bin_dir = tmp_path / "tool-bin"
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")
    codeintel._graph.cache_clear()

    def planted(config):
        log = plant(bin_dir, config)
        codeintel._graph.cache_clear()
        return lambda: log.read_text().splitlines()

    yield root, planted
    codeintel._graph.cache_clear()


def files_graph(files: dict, **extra) -> dict:
    """A graph whose links come out of ``files`` (each path one File node and one Function node)."""
    return {"files": files, "labels": {"File": {p: 1 for p in files}, "Function": {p: 1 for p in files}}, **extra}


def link_queries(queries):
    return [q for q in queries if "WHERE a.file_path =" in q]


def test_one_link_type_of_250000_links_over_files_is_read_whole_each_link_once(graph):
    root, planted = graph
    files = {f"src/m{i:02}.c": {"USAGE": 5_000} for i in range(50)}
    asked = planted(files_graph(files))
    codeintel._graph(root)
    assert codeintel.counted(root) == (100, 250_000)
    queries = asked()
    assert "MATCH (a)-[r:USAGE]->(b) RETURN a.qualified_name, type(r), b.qualified_name" not in queries  # no type whole
    assert len([q for q in link_queries(queries) if q.endswith("count(r)")]) == 50  # one piece a file
    assert codeintel.read_stats(root)["pieces_read"] == 50 and codeintel.read_stats(root)["pieces_from_record"] == 0


def test_one_file_of_120000_links_in_two_types_is_read_by_type_inside_the_file(graph):
    root, planted = graph
    asked = planted(files_graph({"big.c": {"CALLS": 70_000, "USAGE": 50_000}, "small.c": {"CALLS": 3}}))
    codeintel._graph(root)
    assert codeintel.counted(root) == (4, 120_003)
    queries = asked()
    for kind in ("CALLS", "USAGE"):
        assert f'MATCH (a)-[r:{kind}]->(b) WHERE a.file_path = "big.c" RETURN {codeintel._LINK}' in queries
    assert f'MATCH (a)-[r]->(b) WHERE a.file_path = "big.c" RETURN {codeintel._LINK}' not in queries  # over the cap


def test_a_file_and_type_piece_over_the_cap_is_refused_by_name(graph):
    root, planted = graph
    planted(files_graph({"huge.c": {"CALLS": 100_001, "USAGE": 2}}))
    with pytest.raises(codeintel.GraphTooLarge) as raised:
        codeintel._graph(root)
    err = raised.value
    assert (err.kind, err.file, err.count, err.cap) == ("CALLS", "huge.c", 100_001, codeintel.CAP)
    assert "huge.c" in str(err) and "CALLS" in str(err) and "100001" in str(err) and codeintel.TOOL in str(err)
    assert codeintel.counted(root) is None


def test_a_file_the_tool_cuts_short_is_read_again_by_type(graph):
    root, planted = graph
    asked = planted(files_graph({"a.c": {"CALLS": 30, "USAGE": 20}, "b.c": {"CALLS": 4}}, cut={"links:a.c": 10}))
    codeintel._graph(root)
    assert codeintel.counted(root) == (4, 54)
    assert f'MATCH (a)-[r:USAGE]->(b) WHERE a.file_path = "a.c" RETURN {codeintel._LINK}' in asked()


def test_a_file_and_type_piece_the_tool_cuts_short_is_refused_with_both_figures(graph):
    root, planted = graph
    planted(files_graph({"a.c": {"CALLS": 30, "USAGE": 20}}, cut={"links:a.c": 10, "links:a.c:CALLS": 25}))
    with pytest.raises(codeintel.GraphShort) as raised:
        codeintel._graph(root)
    err = raised.value
    assert (err.kind, err.file, err.counted, err.read) == ("CALLS", "a.c", 30, 25)
    assert "a.c" in str(err) and "30" in str(err) and "25" in str(err)


def test_a_link_no_piece_holds_is_refused_naming_the_total_and_the_sum(graph):
    root, planted = graph
    config = files_graph({"a.c": {"CALLS": 3}})
    config["files"]["ghost.c"] = {"CALLS": 2}  # links out of a path no label lists: no piece reads them
    planted(config)
    with pytest.raises(codeintel.GraphShort) as raised:
        codeintel._graph(root)
    assert raised.value.counted == 5 and raised.value.read == 3 and "5" in str(raised.value)


def stage(root, files):
    for rel in files:
        place = root / codeintel.BASE_REL / "files" / rel
        place.parent.mkdir(parents=True, exist_ok=True)
        place.write_text(f"int {rel.replace('/', '_').replace('.', '_')};\n")


def test_a_refresh_after_three_changed_files_reads_the_links_of_those_three_only(graph):
    root, planted = graph
    files = {f"src/f{i}.c": {"CALLS": 5, "USAGE": 2} for i in range(10)}
    stage(root, files)
    planted(files_graph(files))
    codeintel._graph(root)
    assert codeintel.record_path(root).is_file()
    changed = ["src/f1.c", "src/f4.c", "src/f7.c"]
    for rel in changed:
        (root / codeintel.BASE_REL / "files" / rel).write_text("int changed;\n")
    asked = planted(files_graph(files))
    codeintel._graph(root)
    asked_paths = {q.split('"')[1] for q in link_queries(asked())}
    assert asked_paths == set(changed)
    assert codeintel.counted(root) == (20, 70)
    assert codeintel.read_stats(root)["pieces_from_record"] == 7
    assert "MATCH (a)-[r]->(b) RETURN type(r), count(r)" in asked()  # the total is asked every time


def test_a_failed_refresh_keeps_the_last_good_record(graph):
    root, planted = graph
    files = {f"f{i}.c": {"CALLS": 5} for i in range(4)}
    stage(root, files)
    planted(files_graph(files))
    codeintel._graph(root)
    good = codeintel.record_path(root).read_bytes()
    (root / codeintel.BASE_REL / "files" / "f2.c").write_text("int changed;\n")
    planted(files_graph(files, cut={"links:f2.c": 1, "links:f2.c:CALLS": 1}))
    with pytest.raises(codeintel.GraphShort):
        codeintel._graph(root)
    assert codeintel.record_path(root).read_bytes() == good


def test_a_stale_record_is_read_again_whole_never_refused(graph):
    root, planted = graph
    files = {f"f{i}.c": {"CALLS": 5} for i in range(4)}
    stage(root, files)
    planted(files_graph(files))
    codeintel._graph(root)
    files["f0.c"] = {"CALLS": 6}  # an unchanged file whose links the tool now counts otherwise
    planted(files_graph(files))
    codeintel._graph(root)
    assert codeintel.counted(root) == (8, 21)


def call_graph(callee: str, home: str, ids: tuple = ("r1", "r2", "r3", "r4")) -> dict:
    """``a.py``'s ``main`` calls ``callee``, defined in ``home``; the other of ``b.py``/``c.py`` holds ``spare``. Six
    nodes and four links whatever ``callee`` and ``home`` are, with the same ``id(r)`` values (R8-2's probe)."""
    other = "c.py" if home == "b.py" else "b.py"
    stem = {"b.py": "code.b", "c.py": "code.c"}
    return {"files": {}, "edges": {
        "a.py": [[ids[0], "code.a.main", "CALLS", callee], [ids[1], "file.a", "DEFINES", "code.a.main"]],
        home: [[ids[2], f"file.{home[0]}", "DEFINES", callee]],
        other: [[ids[3], f"file.{other[0]}", "DEFINES", f"{stem[other]}.spare"]]},
        "labels": {"File": {"a.py": ["file.a"], "b.py": ["file.b"], "c.py": ["file.c"]},
                   "Function": {"a.py": ["code.a.main"], home: [callee], other: [f"{stem[other]}.spare"]}}}


def write_staged(root, files: dict) -> None:
    for rel, text in files.items():
        place = root / codeintel.BASE_REL / "files" / rel
        place.parent.mkdir(parents=True, exist_ok=True)
        place.write_text(text)


def test_a_callee_moved_to_another_file_makes_the_record_stale_and_every_link_is_read_again(graph):
    """R8-2 (a), item 25: ``foo`` moves from ``b.py`` to ``c.py``, ``a.py`` unchanged, the counts unchanged."""
    root, planted = graph
    write_staged(root, {"a.py": "foo()\n", "b.py": "def foo(): ...\n", "c.py": "def spare(): ...\n"})
    planted(call_graph("code.b.foo", "b.py"))
    _nodes, users = codeintel._graph(root)
    assert users["code.b.foo"] == [("code.a.main", "CALLS")]
    write_staged(root, {"b.py": "def spare(): ...\n", "c.py": "def foo(): ...\n"})  # a.py's digest unchanged
    asked = planted(call_graph("code.c.foo", "c.py"))
    nodes, users = codeintel._graph(root)
    assert users.get("code.c.foo") == [("code.a.main", "CALLS")]
    assert "code.b.foo" not in users and "code.b.foo" not in nodes
    stats = codeintel.read_stats(root)
    assert stats["pieces_from_record"] == 0 and stats["record_stale"] is True and stats["stale_links"] == 1
    assert codeintel.counted(root) == (6, 4)
    assert {q.split('"')[1] for q in link_queries(asked())} == {"a.py", "b.py", "c.py"}  # every piece read again
    rewritten = codeintel.record_path(root).read_text()
    assert "code.c.foo" in rewritten and "code.b.foo" not in rewritten  # rewritten after the read that passed


def test_a_renamed_callee_makes_the_record_stale_and_the_caller_of_the_new_name_is_read(graph):
    root, planted = graph
    write_staged(root, {"a.py": "foo()\n", "b.py": "def foo(): ...\n", "c.py": "def spare(): ...\n"})
    planted(call_graph("code.b.foo", "b.py"))
    codeintel._graph(root)
    write_staged(root, {"b.py": "def bar(): ...\n"})
    planted(call_graph("code.b.bar", "b.py"))
    _nodes, users = codeintel._graph(root)
    assert users.get("code.b.bar") == [("code.a.main", "CALLS")] and "code.b.foo" not in users
    assert codeintel.read_stats(root)["record_stale"] is True
    assert codeintel.read_stats(root)["pieces_from_record"] == 0


def test_a_refresh_whose_held_links_all_keep_their_ends_reads_only_the_changed_files(graph):
    root, planted = graph
    write_staged(root, {"a.py": "foo()\n", "b.py": "def foo(): ...\n", "c.py": "def spare(): ...\n"})
    planted(call_graph("code.b.foo", "b.py"))
    codeintel._graph(root)
    write_staged(root, {"c.py": "def spare(): return 1\n"})  # only c.py changed; every end a.py holds still exists
    asked = planted(call_graph("code.b.foo", "b.py"))
    _nodes, users = codeintel._graph(root)
    assert {q.split('"')[1] for q in link_queries(asked())} == {"c.py"}
    stats = codeintel.read_stats(root)
    assert stats["pieces_from_record"] == 2 and stats["record_stale"] is False and stats["stale_links"] == 0
    assert users["code.b.foo"] == [("code.a.main", "CALLS")]


FOLDERS = {"src":[f"src/s{i}.c" for i in range(20)], "lib": [f"lib/l{i}.c" for i in range(8)]}
ROOT_FILES = ["main.c", "util.c"]


def folder_graph(**extra) -> dict:
    every = [f for fs in FOLDERS.values() for f in fs] + ROOT_FILES
    return {"files": {**{f: {"CALLS": 2} for f in every}, **{d: {"CONTAINS_FILE": len(fs)} for d, fs in FOLDERS.items()}},
            "bare": {"Branch": {"CONTAINS_FILE": len(ROOT_FILES), "CONTAINS_FOLDER": 2}},
            "labels": {"File": {f: 1 for f in every}, "Folder": {d: 1 for d in FOLDERS}, "Branch": {"{}": 1}},
            "holders": {"Folder": FOLDERS, "Branch": {"{}": ROOT_FILES}}, **extra}


def test_a_file_list_cut_by_the_size_cut_is_read_per_folder_and_branch(graph):
    root, planted = graph
    asked = planted(folder_graph(cut={"list:File": 10}))
    codeintel._graph(root)
    assert codeintel.counted(root) == (33, 30 * 2 + 28 + 4)
    queries = asked()
    assert 'MATCH (f:Folder)-[r:CONTAINS_FILE]->(n:File) WHERE f.file_path = "src" RETURN count(n)' in queries
    assert "MATCH (b:Branch)-[r:CONTAINS_FILE]->(n:File) RETURN n.file_path" in queries
    assert "MATCH (a:Branch)-[r]->(b) RETURN count(r)" in queries  # a label with no string path: one piece
    assert len([q for q in link_queries(queries) if q.endswith("count(r)")]) == 32  # 30 files and 2 folders


def test_a_folder_piece_of_the_file_list_cut_is_refused_by_name(graph):
    root, planted = graph
    planted(folder_graph(cut={"list:File": 10, "holder:src": 3}))
    with pytest.raises(codeintel.GraphShort) as raised:
        codeintel._graph(root)
    assert raised.value.kind == "src" and raised.value.counted == 20 and raised.value.read == 3


def test_the_folder_list_cut_while_the_file_list_is_cut_is_refused_by_name(graph):
    root, planted = graph
    planted(folder_graph(cut={"list:File": 10, "list:Folder": 1}))
    with pytest.raises(codeintel.GraphShort) as raised:
        codeintel._graph(root)
    assert raised.value.kind == "Folder" and "Folder" in str(raised.value)


def test_a_node_label_the_tool_cuts_is_read_by_path(graph):
    root, planted = graph
    asked = planted(files_graph({"a.c": {"CALLS": 1}, "b.c": {"CALLS": 1}}, cut={"nodes:Function": 1}))
    codeintel._graph(root)
    assert codeintel.counted(root) == (4, 2)
    assert 'MATCH (n:Function) WHERE n.file_path = "b.c" RETURN n.qualified_name, n.name, n.label, n.file_path' \
        in asked()


def test_no_query_asks_an_unsound_form(graph):
    root, planted = graph
    asked = planted(folder_graph(cut={"list:File": 10, "links:src/s1.c": 1}))
    codeintel._graph(root)
    for query in asked():
        assert not any(form in query for form in (" SKIP ", " LIMIT ", " IN ", "STARTS WITH", " > ", "ORDER BY")), query
        assert "WHERE" not in query or "id(" not in query.split("WHERE")[1].split("RETURN")[0]


def test_a_read_that_fails_for_another_reason_keeps_the_tools_text(graph):
    root, planted = graph
    planted(files_graph({"a.c": {"CALLS": 1}}, fail='WHERE a.file_path = "a.c" RETURN count(r)'))
    with pytest.raises(RuntimeError) as raised:
        codeintel._graph(root)
    assert "query_graph failed" in str(raised.value) and "boom" in str(raised.value)
    assert not isinstance(raised.value, (codeintel.GraphShort, codeintel.GraphTooLarge))


def test_the_symbols_and_their_users_come_from_the_pieces(graph):
    root, planted = graph
    stage(root, ["a.c"])
    planted(files_graph({"a.c": {"CALLS": 1}}))
    nodes, users = codeintel._graph(root)
    assert set(nodes) == {"Function:a.c:0"}  # a File node is a place, not a symbol
    assert codeintel.read_stats(root)["read_seconds"] >= 0


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
    root, planted = graph
    planted(files_graph({"a.c": {"CALLS": 100_001}}))
    with codeintel._Session(root) as session:
        with pytest.raises(RuntimeError) as raised:
            session.tool("query_graph", project=codeintel.PROJECT, format="json", max_rows=10,
                         query=f'MATCH (a)-[r]->(b) WHERE a.file_path = "a.c" RETURN {codeintel._LINK}')
    assert "query_graph failed" in str(raised.value) and CAP_TEXT.split(" —")[0] in str(raised.value)
