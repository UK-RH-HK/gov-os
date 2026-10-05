"""Builder tests for ``gov closure`` (W1-20).

Regression evidence only (DEC-136). They cover what the acceptance tests leave to the builder or cannot run
without the code tool: the stopping reason when several kinds of gap meet, the code side with the wrapper's
functions replaced (the codebase-memory binary is not run), a facet that fails and is not asked again, and a depth
below zero. Every store is built in a temporary repository (DEC-322); nothing is indexed.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import closure as closure_module, codeintel, store  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402
from gov.closure import closure  # noqa: E402

CALLS = {"top": ["mid"], "mid": ["leaf"], "side": ["leaf"], "leaf": []}  # top calls mid, mid and side call leaf
RECORDS = {"A-1": "depends_on: [A-2, GONE-1]", "A-2": "tests: [A-3]", "A-3": "validates: [GONE-2]", "B-1": ""}


@pytest.fixture()
def root(tmp_path, monkeypatch):
    """A temporary repository with its own store, and a code facet that answers from ``CALLS``."""
    git = ["git", "-C", str(tmp_path), "-c", "user.name=unit", "-c", "user.email=unit@example.invalid"]
    subprocess.run([*git, "init", "-q"], check=True)
    (tmp_path / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    for record, edges in RECORDS.items():
        (tmp_path / f"{record}.md").write_text(f"---\nid: {record}\ntype: decision\nstatus: ACTIVE\n{edges}\n---\n",
                                               encoding="utf-8")
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "fixture"], check=True)
    store.load(tmp_path)
    entries = lambda names: [{"name": name, "path": "flow.py", "label": "Function"} for name in names]  # noqa: E731
    monkeypatch.setattr(codeintel, "definitions", lambda _root, name: entries([name] if name in CALLS else []))
    monkeypatch.setattr(codeintel, "callees", lambda _root, name: entries(CALLS[name]))
    monkeypatch.setattr(codeintel, "callers", lambda _root, name: entries(k for k in CALLS if name in CALLS[k]))
    return tmp_path


def _ids(found, key="closure"):
    return [entry["id"] for entry in found[key]]


def test_records_and_symbols_in_one_closure_sorted_with_the_gap_beyond_the_depth(root):
    found = closure(root, ["mid", "A-2", "mid"], depth=1)
    assert found["start"] == ["A-2", "mid"] and found["depth"] == 1
    assert found["closure"] == [{"id": "A-1", "kind": "record"}, {"id": "A-2", "kind": "record"},
                                {"id": "A-3", "kind": "record"}, {"id": "leaf", "kind": "symbol"},
                                {"id": "mid", "kind": "symbol"}, {"id": "top", "kind": "symbol"}]
    beyond = ("GONE-1", "GONE-2", "side")
    assert found["gaps"] == [{"id": name, "reason": closure_module.DEPTH_LIMIT} for name in beyond]
    assert found["stopping_reason"] == closure_module.DEPTH_LIMIT and found["facets"] == {"code": "available"}
    assert list(found) == ["start", "depth", "stopping_reason", "closure", "gaps", "facets", "uncommitted"]


def test_the_stopping_reason_when_kinds_of_gap_meet(root):
    alone = closure(root, ["A-1", "nothing"], depth=9)  # unresolved ids alone: the constant, whatever it says
    assert {gap["reason"] for gap in alone["gaps"]} == {closure_module.UNRESOLVED}
    assert _ids(alone, "gaps") == ["GONE-1", "GONE-2", "nothing"]
    assert alone["stopping_reason"] == closure_module.UNRESOLVED_ALONE != closure_module.COMPLETE
    cut = closure(root, ["A-1"], depth=1)  # an unresolved id and one beyond the depth: the depth cut is stated
    assert cut["gaps"] == [{"id": "A-3", "reason": closure_module.DEPTH_LIMIT},
                           {"id": "GONE-1", "reason": closure_module.UNRESOLVED}]
    assert cut["stopping_reason"] == closure_module.DEPTH_LIMIT and cut["facets"] == {"code": "not_asked"}
    assert closure(root, ["B-1", "top"], depth=9)["stopping_reason"] == closure_module.COMPLETE


@pytest.mark.parametrize("error", [RuntimeError("no index"), FileNotFoundError("no binary")])
def test_a_code_facet_that_fails_is_stated_and_not_asked_again(root, monkeypatch, error):
    asked = []

    def callers(_root, name):
        asked.append(name)
        raise error
    monkeypatch.setattr(codeintel, "callers", callers)
    found = closure(root, ["A-1", "leaf", "side", "nothing"], depth=0)
    assert asked == ["leaf"] and found["facets"] == {"code": "unavailable"}
    assert found["closure"] == [{"id": "A-1", "kind": "record"}]
    assert [gap for gap in found["gaps"] if gap["reason"] == closure_module.FACET_UNAVAILABLE] == [
        {"id": name, "reason": closure_module.FACET_UNAVAILABLE} for name in ("leaf", "nothing", "side")]
    assert found["stopping_reason"] == closure_module.FACET_UNAVAILABLE  # before the depth cut of A-1's edges


def test_uncommitted_paths_are_sorted_and_a_depth_below_zero_is_refused(root):
    for name in ("z.md", "B-1.md"):
        (root / name).write_text("changed\n", encoding="utf-8")
    assert closure(root, ["B-1"], depth=0)["uncommitted"] == ["B-1.md", "z.md"]
    with pytest.raises(GovError):
        closure(root, ["B-1"], depth=-1)


def test_the_radius_gives_the_depth():
    assert [closure_module.depth_of_radius(radius) for radius in (0, 1, 2, 3, 4)] == [1, 1, 3, 8, 8]
