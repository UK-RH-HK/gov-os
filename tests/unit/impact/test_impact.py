"""Builder tests for ``gov impact`` (W2-37).

Regression evidence only (DEC-136). They cover what the acceptance tests cannot run inside a worker's sandbox
(P-W2-38): the code side, with the code index's functions replaced (the codebase-memory binary is not run), so the
id mapping of G-16, the deletable-class join of G-24 and a stale code index are held here too; and the parsing of the
stated change and the radius reading. Every store is built in a temporary repository; nothing is indexed.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import codeintel, impact, store  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402
from gov.impact import readings  # noqa: E402

# helper <- apply <- entry and the test; helper <- orphan; named_only alone
CALLS = {"apply": ["helper"], "entry": ["apply"], "test_apply": ["apply"], "orphan": ["helper"], "helper": [],
         "named_only": []}
PATHS = {name: "tests/test_flow.py" if name.startswith("test_") else "app/flow.py" for name in CALLS}
RECORDS = {"DEC-001": "decision\nconstrains: [SPEC-001, apply]", "SPEC-001": "specification",
           "DEC-002": "decision\ndepends_on: [DEC-001]",
           "DEC-051": "decision\nconstrains: [named_only]", "DEC-050": "decision"}


@pytest.fixture()
def root(tmp_path, monkeypatch):
    """A temporary repository with its store, a staged copy of its code, and a code index answering from CALLS."""
    git = ["git", "-C", str(tmp_path), "-c", "user.name=unit", "-c", "user.email=unit@example.invalid"]
    subprocess.run([*git, "init", "-q"], check=True)
    (tmp_path / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    for record, rest in RECORDS.items():
        (tmp_path / f"{record}.md").write_text(f"---\nid: {record}\nstatus: ACTIVE\ntype: {rest}\n---\n",
                                               encoding="utf-8")
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "flow.py").write_text("# the code\n", encoding="utf-8")
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "fixture"], check=True)
    store.load(tmp_path)
    staged = codeintel.home(tmp_path).parent / "files"
    for rel in (".gitignore", "app/flow.py", *(f"{record}.md" for record in RECORDS)):
        (staged / rel).parent.mkdir(parents=True, exist_ok=True)
        (staged / rel).write_bytes((tmp_path / rel).read_bytes())
    entries = lambda names: [{"name": name, "path": PATHS[name], "label": "Function"} for name in names]  # noqa: E731
    monkeypatch.setattr(codeintel, "definitions", lambda _root, name: entries([name] if name in CALLS else []))
    monkeypatch.setattr(codeintel, "callees", lambda _root, name: entries(CALLS.get(name, [])))
    monkeypatch.setattr(codeintel, "callers", lambda _root, name: entries(
        [caller for caller, called in CALLS.items() if name in called]))
    monkeypatch.setattr(codeintel, "dead_code", lambda _root: entries(
        [name for name in CALLS if not any(name in called for called in CALLS.values())]))
    return tmp_path


def where(found, wanted):
    return [(kind, item["graph"]) for kind in readings.KINDS for item in found["affected"][kind] if item["id"] == wanted]


def test_a_record_edge_to_a_symbol_joins_the_code_graph(root):
    found = impact.assess(root, ["DEC-001"], {})
    assert found["graphs"] == {"record": "ok", "code": "ok"}
    assert where(found, "apply") == [("code", "code")] and where(found, "SPEC-001") == [("specifications", "record")]
    assert where(found, "helper") == where(found, "entry") == [("code", "code")]
    assert where(found, "test_apply") == [("tests", "code")]
    assert found["complete"] is (not found["gaps"])


def test_a_symbol_reaches_the_records_that_name_it(root):
    found = impact.assess(root, ["named_only"], {})
    assert where(found, "DEC-051") == [("decisions", "record")]
    assert found["change"][0]["deletable"] is False  # dead code to the code graph, but a record names it


def test_the_deletable_join(root):
    assert impact.assess(root, ["orphan"], {})["change"][0]["deletable"] is True
    assert impact.assess(root, ["helper"], {})["change"][0]["deletable"] is False
    solo = impact.assess(root, ["DEC-050"], {})
    assert solo["change"][0]["deletable"] is True and solo["radius"] == "R0"


def test_a_code_index_older_than_the_working_tree_is_stale_and_never_complete(root):
    (root / "app" / "flow.py").write_text("# the code, changed\n", encoding="utf-8")
    found = impact.assess(root, ["orphan"], {})
    assert found["graphs"]["code"].startswith("stale") and found["complete"] is False
    assert found["change"][0]["deletable"] is False  # dead code, but read from a stale index


def test_without_a_code_index_the_symbol_is_a_gap(root):
    import shutil

    shutil.rmtree(codeintel.home(root).parent / "files")
    found = impact.assess(root, ["DEC-001"], {})
    assert found["graphs"]["code"].startswith("missing") and found["complete"] is False
    assert {"id": "apply", "reason": "CODE_GRAPH_MISSING"} in found["gaps"]
    with pytest.raises(GovError) as refused:
        impact.assess(root, ["helper"], {})
    assert refused.value.code == "IMPACT_CHANGE_UNKNOWN" and "code graph" in refused.value.message


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=unit", "-c", "user.email=unit@example.invalid",
                           *args], check=True, capture_output=True, text=True).stdout


@pytest.mark.parametrize("state", ["record-added", "record-edited", "older-commit"])
def test_a_record_graph_that_differs_from_the_tree_is_stale(root, state):
    """The first review's F1: an uncommitted record, an uncommitted edit, a HEAD older than the store's."""
    if state == "record-added":
        (root / "DEC-003.md").write_text("---\nid: DEC-003\nstatus: ACTIVE\ntype: decision\n---\n", encoding="utf-8")
    elif state == "record-edited":
        (root / "DEC-002.md").write_text("---\nid: DEC-002\nstatus: ACTIVE\ntype: decision\n---\n", encoding="utf-8")
    else:
        (root / "DEC-003.md").write_text("---\nid: DEC-003\nstatus: ACTIVE\ntype: decision\n---\n", encoding="utf-8")
        git(root, "add", "DEC-003.md")
        git(root, "commit", "-q", "-m", "a later record")
        store.load(root)
        git(root, "checkout", "-q", "HEAD~1")
    found = impact.assess(root, ["DEC-001"], {})
    assert found["graphs"]["record"].startswith("stale") and found["complete"] is False
    assert impact.assess(root, ["DEC-050"], {})["change"][0]["deletable"] is False


def test_a_markdown_file_without_frontmatter_leaves_the_record_graph_current(root):
    (root / "NOTES.md").write_text("# notes\n", encoding="utf-8")
    assert impact.assess(root, ["DEC-001"], {})["graphs"]["record"] == "ok"


def test_a_name_with_one_called_definition_is_not_dead(root, monkeypatch):
    """The first review's F6: two definitions share ``orphan``; one is dead, the other is called."""
    twice = [{"name": "orphan", "path": "app/flow.py", "label": "Function"},
             {"name": "orphan", "path": "app/other.py", "label": "Function"}]
    monkeypatch.setattr(codeintel, "definitions", lambda _root, name: twice if name == "orphan" else [])
    assert impact.assess(root, ["orphan"], {})["change"][0]["deletable"] is False


def test_an_unindexed_file_is_stale_whatever_its_modification_time(root, monkeypatch):
    """The first review's F8: a file the index would copy now, with a modification time from before the index."""
    import os

    import gov.secrets

    monkeypatch.setattr(gov.secrets, "indexable", lambda _root, paths: list(paths))
    monkeypatch.setattr(gov.secrets, "path_holds_secret", lambda _root, rel: False)
    (root / "app" / "moved.py").write_text("# moved here\n", encoding="utf-8")
    os.utime(root / "app" / "moved.py", (946684800, 946684800))
    found = impact.assess(root, ["orphan"], {})
    assert found["graphs"]["code"].startswith("stale") and "app/moved.py" in found["graphs"]["code"]
    assert found["complete"] is False
    monkeypatch.setattr(gov.secrets, "indexable", lambda _root, paths: [])  # a file the filter leaves out
    assert impact.assess(root, ["orphan"], {})["graphs"]["code"] == "ok"


def test_the_written_cit_p_says_what_the_assessment_says_of_completeness(root):
    """The first review's F3."""
    import shutil

    import yaml

    shutil.rmtree(codeintel.home(root).parent / "files")
    found = impact.assess(root, ["DEC-001"], {}, out="CITP-901.md")
    text = (root / "CITP-901.md").read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---\n")[1])
    assert found["complete"] is False and front["complete"] is False
    assert front["graphs"] == found["graphs"] and front["gaps"] == found["gaps"] == found["proposal"]["gaps"]


@pytest.mark.parametrize("value", ["some_symbol", {"DEC-099": "done"}])
def test_an_execution_record_whose_kind_is_not_a_list_is_refused(root, value):
    """The first review's F2."""
    import yaml

    for rel, front in (("CITP-001.md", {"id": "CITP-001", "type": impact.CITP_TYPE, "affected": {"code": []}}),
                       ("CITE-001.md", {"id": "CITE-001", "type": impact.CITE_TYPE, "proposal": "CITP-001",
                                        "affected": {"code": value}})):
        (root / rel).write_text(f"---\n{yaml.safe_dump({'status': 'ACCEPTED', **front})}---\n", encoding="utf-8")
    git(root, "add", "CITP-001.md", "CITE-001.md")
    git(root, "commit", "-q", "-m", "the change's records")
    store.load(root)
    with pytest.raises(GovError) as refused:
        impact.compare(root, "CITE-001.md")
    assert refused.value.code == "IMPACT_AFFECTED_MALFORMED" and "code" in refused.value.message


@pytest.mark.parametrize("asked,ids", [("What's the impact of DEC-001?", ["DEC-001"]),
                                       ("what is the impact of `helper`", ["helper"]),
                                       ("DEC-001", ["DEC-001"])])
def test_the_stated_change(asked, ids):
    assert impact._stated([asked]) == ids


@pytest.mark.parametrize("asked", ["", "What's the impact?", "a b", "???"])
def test_a_malformed_change_is_refused(asked):
    with pytest.raises(GovError):
        impact._stated([asked])


def test_the_radius_reading():
    assert readings.radius(True, {"code"}) == 0
    assert [readings.radius(False, set(readings.KINDS[:n])) for n in range(6)] == [1, 1, 2, 2, 3, 3]
