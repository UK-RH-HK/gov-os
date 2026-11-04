"""W2-32, DEC-1068 M3: the reverse ``depends_on`` edge in the closure, behind ``closure_reverse_depends_on`` in
``rebuild.yaml`` (absent: off, today's index and answers). Regression evidence only (DEC-136): no model is started
(the semantic route is a stand-in with no hit). Each store is in a temporary git repository.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import store  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402
from gov.config import loader  # noqa: E402
from gov.retrieval import lexical, reverse_edges, semantic  # noqa: E402
from gov.retrieval import retrieve as retrieving  # noqa: E402
from gov.store import STORE_REL  # noqa: E402

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
needs_gitleaks = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")
BODY = "".join(f"Line {n:02d} of the ticket's notes, kept long so that it holds several chunks.\n" for n in range(60))


def _ticket(record_id: str, depends: str = "") -> str:
    return f"---\nid: {record_id}\ntype: task\nstatus: open\ntitle: Ticket {record_id}\n{depends}---\n# {record_id}\n" \
           + BODY


TICKETS = {
    "T-1": _ticket("T-1"),  # the start record: its own chunks come first in today's closure route
    "T-2": _ticket("T-2", "deps: [T-1]\ndepends_on:\n- T-1\n"),  # a list item under the key
    "T-3": _ticket("T-3", "depends_on: [T-9, T-1]\n"),  # an inline list
    "T-4": _ticket("T-4", "depends_on:\n- T-2\n"),  # depends on T-2, not on T-1
    "T-9": _ticket("T-9"),
    "T-10": _ticket("T-10", "depends_on:\n- T-9\n"),  # names T-1 nowhere: T-10 is no T-1
}


def _git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env={**_ENV, "HOME": str(root)})


def _settings(root: Path, text: str | None) -> None:
    path = root / "governance/project/rebuild.yaml"
    if text is None:
        path.unlink(missing_ok=True)
    else:
        path.write_text(text)


# --- the stating line's exact form -----------------------------------------------------------------------------------

@pytest.mark.parametrize("text, target, line", [
    (TICKETS["T-2"], "T-1", 8),  # the item under depends_on, not the deps line above it
    (TICKETS["T-3"], "T-1", 6),  # the inline value's own line
    (TICKETS["T-3"], "T-9", 6),
    (TICKETS["T-4"], "T-1", None),
    (TICKETS["T-10"], "T-1", None),  # T-10 does not name T-1
    ("---\nid: X\ndepends_on:\n  - A-1\n  - B-2\nstatus: open\n---\n- B-2\n", "B-2", 5),  # indented items
    ("---\nid: X\ndepends_on:\n- A-1\nlinks:\n- B-2\n---\n", "B-2", None),  # another key's item
    ("no front matter\ndepends_on: [B-2]\n", "B-2", None),
    ("---\nid: X\n---\ndepends_on: [B-2]\n", "B-2", None),  # after the front matter
])
def test_the_stating_line_is_the_depends_on_value_s_line_naming_the_target(text, target, line):
    assert reverse_edges.stating_line(text, target) == line


# --- the setting -----------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("text, on", [(None, False), ("file_level_index: true\n", False),
                                      ("closure_reverse_depends_on: false\n", False),
                                      ("closure_reverse_depends_on: true\n", True)])
def test_the_setting_is_off_unless_written_true(tmp_path, text, on):
    (tmp_path / "governance/project").mkdir(parents=True)
    _settings(tmp_path, text)
    assert reverse_edges.on(tmp_path) is on


@pytest.mark.parametrize("value", ["yes", "1", "'true'", "on"])
def test_any_other_value_is_refused_by_the_loader_naming_the_key(tmp_path, value):
    (tmp_path / "governance/project").mkdir(parents=True)
    _settings(tmp_path, f"closure_reverse_depends_on: {value}\n")
    for read in (loader.load_config, reverse_edges.on):
        with pytest.raises(GovError) as raised:
            read(tmp_path)
        assert raised.value.code == "CONFIG_INVALID"
        assert raised.value.details == {"file": "governance/project/rebuild.yaml", "key": "closure_reverse_depends_on"}


def test_this_repository_does_not_switch_it_on():
    assert reverse_edges.on(REPO) is False


# --- the index and the closure route ---------------------------------------------------------------------------------

@pytest.fixture()
def project(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    (root / "governance/project").mkdir(parents=True)
    (root / ".gitignore").write_text(".gov-runtime/\n")
    (root / "governance/project/path-map.yaml").write_text("namespaces:\n  all: {paths: ['**']}\n")
    (root / ".tickets").mkdir()
    for record_id, text in TICKETS.items():
        (root / f".tickets/{record_id}.md").write_text(text)
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "c")
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "search", lambda *_a, **_k: {"available": True, "reason": None, "hits": []})
    lexical.refresh(root)
    store.load(root)
    return root


def _table(root: Path):
    connection = sqlite3.connect(root / STORE_REL)
    try:
        names = {name for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        rows = sorted(connection.execute("SELECT * FROM closure_reverse_edge")) \
            if "closure_reverse_edge" in names else None
        recipe = dict(connection.execute("SELECT key, value FROM index_recipe")) if "index_recipe" in names else {}
    finally:
        connection.close()
    return rows, recipe


def test_off_the_rebuild_s_index_is_today_s(project):
    assert reverse_edges.refresh(project) is None
    assert _table(project) == (None, {})


def test_on_each_depends_on_edge_is_kept_with_its_stating_line(project):
    _settings(project, "closure_reverse_depends_on: true\n")
    assert reverse_edges.refresh(project) == {"status": "recreated", "edges": 5, "stated": 5}
    rows, recipe = _table(project)
    assert rows == [("T-1", "T-2", ".tickets/T-2.md", 8), ("T-1", "T-3", ".tickets/T-3.md", 6),
                    ("T-2", "T-4", ".tickets/T-4.md", 7), ("T-9", "T-10", ".tickets/T-10.md", 7),
                    ("T-9", "T-3", ".tickets/T-3.md", 6)]
    assert recipe == {"closure_reverse_depends_on": "true"}
    _settings(project, None)  # switched off: the next rebuild drops it
    assert reverse_edges.refresh(project) is None and _table(project) == (None, {})


def _closure_route(root: Path, monkeypatch) -> tuple[list[str], dict]:
    seen = {}
    original = retrieving.rrf
    monkeypatch.setattr(retrieving, "rrf", lambda routes: seen.update(routes) or original(routes))
    bundle = retrieving.retrieve(root, "Which tickets depend on T-1?", reranker=lambda: None)
    chunks = {c["chunk_id"]: c for c in lexical.chunks(root)}
    return [f"{chunks[h['chunk_id']]['path']}:{h['start_line']}" for h in seen[retrieving.CLOSURE]], bundle


@needs_gitleaks
def test_off_the_closure_route_is_today_s(project, monkeypatch):
    route, bundle = _closure_route(project, monkeypatch)
    assert route[0].startswith(".tickets/T-1.md")  # the start record's own chunks first, the dependents' after
    assert reverse_edges.FACET_KEY not in bundle["facets"][retrieving.CLOSURE]


@needs_gitleaks
def test_on_the_dependents_stating_chunks_come_first_in_the_closure_route(project, monkeypatch):
    off, _ = _closure_route(project, monkeypatch)
    _settings(project, "closure_reverse_depends_on: true\n")
    reverse_edges.refresh(project)
    on, bundle = _closure_route(project, monkeypatch)
    assert on[:2] == [".tickets/T-2.md:1", ".tickets/T-3.md:1"]  # the chunks holding lines 8 and 6, by the dependent
    assert sorted(on) == sorted(off)  # the same chunks, the stating ones moved ahead
    assert reverse_edges.FACET_KEY not in bundle["facets"][retrieving.CLOSURE]
    assert not any(path.startswith((".tickets/T-4.md", ".tickets/T-10.md")) for path in on[:2])


@needs_gitleaks
def test_switched_on_without_a_rebuild_the_route_is_today_s_and_named_stale(project, monkeypatch):
    off, _ = _closure_route(project, monkeypatch)
    _settings(project, "closure_reverse_depends_on: true\n")
    on, bundle = _closure_route(project, monkeypatch)
    assert on == off and bundle["facets"][retrieving.CLOSURE][reverse_edges.FACET_KEY] == reverse_edges.STALE


@needs_gitleaks
def test_gov_rebuild_builds_the_index_only_with_the_setting_on(project, tmp_path, monkeypatch, capsys):
    from gov.cli import main as cli
    monkeypatch.setenv("GOV_REBUILD_LOCK", str(tmp_path / "rebuild.lock"))

    def rebuild():
        cli.main(["rebuild", "--no-embeddings", "--json", "--root", str(project)])
        return json.loads(capsys.readouterr().out.strip().splitlines()[-1])

    off = rebuild()
    assert off["ok"] is True and reverse_edges.RECIPE_KEY not in off["result"]["stores"]
    assert _table(project) == (None, {})
    _settings(project, "closure_reverse_depends_on: true\n")
    on = rebuild()
    assert on["result"]["stores"][reverse_edges.RECIPE_KEY] == {"status": "recreated", "edges": 5, "stated": 5}
    assert len(_table(project)[0]) == 5
    assert on["result"]["digest"] == off["result"]["digest"]  # the record store's digest is unchanged
