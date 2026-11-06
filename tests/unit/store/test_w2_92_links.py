"""Builder tests for W2-92 S7 (DEC-1072 (1)): the links the repository states, kept at the load.

Regression evidence only (DEC-136). A planted repository in a temporary folder: a register whose entries supersede,
amend and stand under one another, a ticket, a checkpoint, a close record and a plan. Each kind the census ranks 1 to
4 becomes a typed row of ``stated_links``; a supersession that names ids alone is SUPERSEDES, one of a part AMENDS;
only links between records are kept, none that ``edges`` holds; the digest and every reader of ``edges`` are unchanged.
On this repository's register, ``register_statements`` gives the census's own statements one for one.
"""
from __future__ import annotations

import collections
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import records, store  # noqa: E402
from gov.rebuild import seed  # noqa: E402
from gov.store import loader  # noqa: E402

REGISTER = "docs/DECISION_REGISTER.md"
REGISTER_TEXT = """\
# Register

| Version | Change |
|---|---|
| 0.2 | DEC-108 (the second rule; supersedes DEC-110) |

### DEC-101 — The harbour rule
- **Status:** ACCEPTED
- **Decision:** The pier is kept dry; its cap is 4 boats.

### DEC-102 — The pier's cap
- **Status:** ACCEPTED · **Under:** DEC-101 (amended here), DEC-107
- **Changes:** DEC-101 (its cap of 4 boats)
- **Decision:** The cap is 6 boats.

### DEC-103 — The new mooring rule
- **Status:** ACCEPTED · **Under:** DEC-101
- **Replaces:** DEC-104's mooring line (item 1)
- **Refines:** DEC-107

### DEC-104 — Mooring
- **Status:** ACCEPTED
- **Decision:** (1) Moor at the east line. (2) Moor in pairs.

### DEC-105 — The ferry
- **Status:** ACCEPTED
- **Changed by:** withdrawn by DEC-106

### DEC-106 — No ferry
- **Status:** ACCEPTED
- **Decision:** The ferry ends. DEC-107's lamp is amended by DEC-106.

### DEC-107 — The lamp
- **Status:** ACCEPTED
- **Decision:** A lamp at the pier's end.

### DEC-108 — The second rule
- **Status:** ACCEPTED · **Supersedes:** DEC-109

### DEC-109 — The first rule
- **Status:** SUPERSEDED

### DEC-110 — An older rule
- **Status:** ACCEPTED

### DEC-111 — A proposal
- **Status:** PROPOSED
- **Decision:** The pier gets a crane.
"""
FILES = {
    REGISTER: REGISTER_TEXT,
    "governance/project/path-map.yaml": f"decision_register: {REGISTER}\n",
    ".tickets/DAEO-aaaa.md": "---\nid: DAEO-aaaa\ntype: task\nstatus: open\nwbs_id: W2-5\n"
                             "sources: [DEC-101, CAP-01, DEC-999, MR-3]\n"
                             "closes: ['DEC-104 (item 1)', W2-H001]\ndepends_on: [DAEO-bbbb]\n---\n# x\n",
    ".tickets/DAEO-bbbb.md": "---\nid: DAEO-bbbb\ntype: task\nstatus: closed\n---\n# y\n",
    "docs/contract/CAP-01.md": "---\nid: CAP-01\ntype: capability\nstatus: ACTIVE\n---\n",
    "docs/checkpoints/CP-1.md": "---\nid: CP-1\ntype: checkpoint\nstatus: ACTIVE\ntask: W2-5\n---\n",
    "docs/close/CL-1.md": "---\nid: CL-1\ntype: close\nstatus: ACTIVE\ntask: DAEO-aaaa\n"
                          "decisions_applied: [DEC-101]\nrequirements_implemented: [DEC-101, engineer]\n---\n",
    "docs/plan/PLAN.md": "---\nid: PLAN-1\ntype: plan\nstatus: ACTIVE\ndecisions: [DEC-102, DEC-103]\n---\n",
}
EXPECTED = {
    ("CITES", "DAEO-aaaa", "DEC-101", "sources"), ("CITES", "DAEO-aaaa", "CAP-01", "sources"),
    ("CITES", "DAEO-aaaa", "DEC-104", "closes"),
    ("CITES", "CL-1", "DEC-101", "decisions_applied"),
    ("CITES", "PLAN-1", "DEC-102", "decisions"), ("CITES", "PLAN-1", "DEC-103", "decisions"),
    ("OF_TASK", "CP-1", "DAEO-aaaa", "task"), ("OF_TASK", "CL-1", "DAEO-aaaa", "task"),
    ("UNDER", "DEC-102", "DEC-101", "**Under:**"), ("UNDER", "DEC-102", "DEC-107", "**Under:**"),
    ("UNDER", "DEC-103", "DEC-101", "**Under:**"),
    ("AMENDS", "DEC-102", "DEC-101", "(amended here)"),  # and **Changes:**: one row, its first form
    ("AMENDS", "DEC-103", "DEC-104", "**Replaces:**"),  # a part replaced: AMENDS, never SUPERSEDES
    ("AMENDS", "DEC-106", "DEC-107", "text: amended by"),  # free text: "DEC-107's lamp is amended by DEC-106"
    ("AMENDS", "DEC-108", "DEC-110", "change log: supersedes"),
    ("SUPERSEDES", "DEC-106", "DEC-105", "**Changed by:** withdrawn by"),  # ids alone: the whole
}


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), "-c", "user.name=unit", "-c", "user.email=unit@example.invalid", *args],
                   check=True, capture_output=True)


@pytest.fixture()
def repo(tmp_path):
    _git(tmp_path, "init", "-q")
    (tmp_path / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    for rel, text in FILES.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "fixture")
    return tmp_path


def _links(root: Path) -> set[tuple]:
    connection = sqlite3.connect(root / store.STORE_REL)
    try:
        return set(connection.execute(f"SELECT type, source, target, via FROM {loader.LINKS_TABLE}"))
    finally:
        connection.close()


def test_each_kind_the_census_ranks_becomes_a_typed_link_between_records(repo):
    store.load(repo)
    found = _links(repo)
    assert found == EXPECTED
    assert collections.Counter(kind for kind, *_ in found) == {"CITES": 6, "UNDER": 3, "AMENDS": 4, "OF_TASK": 2,
                                                               "SUPERSEDES": 1}


def test_the_links_are_not_edges_so_the_closure_and_the_edge_readers_are_unchanged(repo):
    store.load(repo)
    assert records.edges(repo) == [{"type": "DEPENDS_ON", "source": "DAEO-aaaa", "target": "DAEO-bbbb"},
                                   {"type": "SUPERSEDES", "source": "DEC-108", "target": "DEC-109"}]
    # the edge the first line's Supersedes already gives is not stated twice
    assert not any(row[1:3] == ("DEC-108", "DEC-109") for row in _links(repo))


def test_a_partial_supersession_leaves_its_target_current_in_the_store(repo):
    store.load(repo)
    assert "DEC-104" in {record["id"] for record in records.records(repo, type="decision", status="ACCEPTED")}
    assert "DEC-104" not in {edge["target"] for edge in records.edges(repo, type="SUPERSEDES")}


def test_the_digest_leaves_the_links_out_and_the_schema_version_holds_them(repo, monkeypatch):
    digest = store.load(repo)["digest"]
    connection = sqlite3.connect(repo / store.STORE_REL)
    connection.execute(f"DELETE FROM {loader.LINKS_TABLE}")
    connection.commit()
    connection.close()
    assert store.digest(repo) == digest
    version = seed.schema_version()
    monkeypatch.delitem(loader._TABLES, loader.LINKS_TABLE)
    assert seed.schema_version() != version


def test_the_statements_carry_every_class_and_only_four_kinds_become_links(repo):
    entries, _ = loader.register_entries(REGISTER_TEXT)
    every = loader.register_statements(REGISTER_TEXT)
    assert loader.register_statements(REGISTER_TEXT, entries) == every  # the entries given or read: the same
    said = {(s["source"], s["target"], s["cls"], s["whole"]) for s in every}
    assert ("DEC-103", "DEC-104", "supersede", False) in said  # "Replaces: DEC-104's mooring line": a part
    assert ("DEC-106", "DEC-105", "supersede", True) in said
    assert ("DEC-103", "DEC-107", "refine", True) in said  # a refinement is a statement (gov links reads it) ...
    store.load(repo)
    assert not any(row[1:3] == ("DEC-103", "DEC-107") for row in _links(repo))  # ... but no link kind built here
    assert {s["where"] for s in every} == {"label", "text", "preamble"}


def _census_statements(root: Path, text: str) -> list[dict]:
    """The census's own register statements: its §1 code, run as it is written in its file."""
    source = (root / "docs/research/D4B-link-census.py").read_text(encoding="utf-8").split("\n")
    first = next(n for n, line in enumerate(source) if line.startswith("# ----") and "1. the register" in line)
    last = next(n for n, line in enumerate(source) if line.startswith("statements = uniq"))
    scope = {"ROOT": root, "loader": loader, "re": re, "collections": collections, "TEXT": text,
             "DEC": re.compile(r"\bDEC-(\d{3,})\b"), "ANY_ID": re.compile(r"\b(?:CAP-\d{2}|MR-\d+)\b")}
    code = "\n".join(source[first:last + 1])
    assert '(ROOT / "docs/DECISION_REGISTER.md").read_text()' in code  # the census reads the register so
    exec(code.replace('(ROOT / "docs/DECISION_REGISTER.md").read_text()', "TEXT"), scope)
    return scope["statements"] + scope["pre_statements"]


_NO_CENSUS = pytest.mark.skipif(not (REPO / "docs/research/D4B-link-census.py").is_file(),
                                reason="no census in this tree")


@_NO_CENSUS
def test_the_planted_registers_statements_are_the_censuss_one_for_one():
    census = _census_statements(REPO, REGISTER_TEXT)
    assert census and loader.register_statements(REGISTER_TEXT) == census


@_NO_CENSUS
def test_this_repositorys_register_statements_are_the_censuss_one_for_one():
    text = (REPO / REGISTER).read_text(encoding="utf-8")
    census = _census_statements(REPO, text)
    assert len(census) > 1000 and loader.register_statements(text) == census


def test_the_load_is_the_same_twice(repo):
    first = (store.load(repo)["digest"], _links(repo))
    assert (store.load(repo)["digest"], _links(repo)) == first
