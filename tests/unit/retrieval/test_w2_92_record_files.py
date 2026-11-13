"""Builder tests: no record file is cited without a record graph (W2-92; DEC-1019 = P-W2-92-5 (a), DEC-1006).

Regression evidence only (DEC-136). Without the store's record graph no record can be judged current (DEC-329, G-19,
DEC-423), so a file whose front matter declares a record and the decision register are left out, each in ``dropped``
with the reason, and the closure facet says so; plain documents and code spans still answer. With the graph present
the record-file check is never made. Each case builds its store in a temporary repository from scratch.
"""
from __future__ import annotations

import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import codeintel, store  # noqa: E402
from gov.retrieval import code_route, lexical, semantic  # noqa: E402
from gov.retrieval import retrieve as retrieval  # noqa: E402

REGISTER = "docs/DECISION_REGISTER.md"
WORD = "fuse_scores"
FILES = {
    "records/decisions/DEC-010.md": "---\nid: DEC-010\ntype: decision\nstatus: ACCEPTED\n---\n# DEC-010\n\n"
                                    f"The old {WORD} rule.\n",  # its own status ACCEPTED, superseded by DEC-011
    "records/decisions/DEC-011.md": "---\nid: DEC-011\ntype: decision\nstatus: ACCEPTED\nsupersedes: [DEC-010]\n---\n"
                                    f"# DEC-011\n\nThe new {WORD} rule.\n",
    "records/decisions/DEC-012.md": "---\nid: DEC-012\ntype: decision\nstatus: SUPERSEDED\n---\n# DEC-012\n\n"
                                    f"A {WORD} rule given up.\n",
    "records/decisions/DEC-013.md": "---\nid: DEC-013\ntype: decision\nstatus: ACCEPTED\nsuperseded_by: [DEC-099]\n"
                                    f"---\n# DEC-013\n\nA {WORD} rule whose successor no record holds.\n",
    REGISTER: f"# Register\n\n### DEC-020: The register's rule\n**Status:** ACCEPTED\n\nThe {WORD} entry.\n",
    "note.md": f"# Note\n\nThe {WORD} ledger of the pier.\n",
    "src/fus.py": f"def {WORD}(a):\n    return a\n",
}
RECORD_FILES = ["docs/DECISION_REGISTER.md", "records/decisions/DEC-010.md", "records/decisions/DEC-011.md",
                "records/decisions/DEC-012.md", "records/decisions/DEC-013.md"]


def build(root: Path) -> Path:
    """A repository at ``root``, indexed and loaded, whose path map names the register."""
    git = ["git", "-C", str(root), "-c", "user.name=unit", "-c", "user.email=unit@example.invalid"]
    subprocess.run([*git, "init", "-q"], check=True)
    (root / "governance/project").mkdir(parents=True)
    path_map = yaml.safe_load((REPO / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    path_map["namespaces"] = {"notes": {**next(iter(path_map["namespaces"].values())), "paths": ["**"]}}
    path_map["decision_register"] = REGISTER
    (root / "governance/project/path-map.yaml").write_text(yaml.safe_dump(path_map), encoding="utf-8")
    shutil.copy2(REPO / "template/.gitleaks.toml", root / ".gitleaks.toml")
    (root / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    for rel, text in FILES.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "fixture"], check=True)
    lexical.refresh(root)
    store.load(root)
    (root / codeintel.BASE_REL / "home").mkdir(parents=True)
    (root / codeintel.BASE_REL / "files").mkdir()
    return root


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    monkeypatch.setattr(code_route, "_SESSIONS", {})  # no tool session kept from another test
    monkeypatch.setattr(code_route, "_spans", lambda _root, words: [("src/fus.py", 1, 2)] if WORD in words else [])
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "reason": None, "hits": []})
    return build(tmp_path)


def _break(repo, sql):
    connection = sqlite3.connect(repo / ".gov-runtime/store.db")
    connection.execute(sql)
    connection.commit()
    connection.close()


needs_gitleaks = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")


@needs_gitleaks
@pytest.mark.parametrize("sql, named", [("DROP TABLE records", "the record store is missing"),
                                        ("ALTER TABLE records RENAME COLUMN status TO state",
                                         "the record store is unreadable")])
def test_without_a_record_graph_no_record_file_is_cited(repo, sql, named):
    _break(repo, sql)
    bundle = retrieve_it(repo)
    assert sorted({item["path"] for item in bundle["evidence"]}) == ["note.md", "src/fus.py"]  # docs and code answer
    assert any("code" in item["routes"] for item in bundle["evidence"] if item["path"] == "src/fus.py")
    dropped = bundle["merge"]["dropped"]
    assert [item["path"] for item in dropped] == RECORD_FILES
    assert all(item["reason"] == retrieval.NO_RECORD_GRAPH for item in dropped)
    assert [item["id"] for item in dropped] == [REGISTER, "DEC-010", "DEC-011", "DEC-012", "DEC-013"]
    closure = bundle["facets"]["closure"]
    assert closure["available"] is False and named in closure["reason"]
    assert "record files are left out" in closure["reason"] and "currency cannot be judged" in closure["reason"]
    assert bundle["stopping_reason"] == "FACET_UNAVAILABLE"  # the route is named; the answer still comes
    assert bundle == retrieve_it(repo)  # the same answer twice


@needs_gitleaks
def test_with_a_record_graph_the_record_file_check_is_never_made(repo, monkeypatch):
    def refused(*_args):
        raise AssertionError("a record file was judged without need")

    monkeypatch.setattr(retrieval, "_declares_record", refused)
    monkeypatch.setattr(retrieval, "_named_register", refused)
    bundle = retrieve_it(repo)
    cited = {item["path"] for item in bundle["evidence"]}
    assert {"note.md", "src/fus.py", "records/decisions/DEC-011.md", REGISTER} <= cited  # the current ones
    assert [(item["path"], item["reason"]) for item in bundle["merge"]["dropped"]] == [
        ("records/decisions/DEC-010.md", "SUPERSEDED"), ("records/decisions/DEC-012.md", "SUPERSEDED"),
        ("records/decisions/DEC-013.md", "SUPERSEDED")]
    assert "closure" not in bundle["facets"] and bundle["stopping_reason"] == "SATURATED"  # as at the base
    named = retrieval.retrieve(repo, "DEC-011", reranker=lambda: None)  # a record named: the closure answers
    assert named["facets"]["closure"] == {"available": True, "reason": None}
    assert "records/decisions/DEC-011.md" in {item["path"] for item in named["evidence"]}


def retrieve_it(repo):
    return retrieval.retrieve(repo, WORD, reranker=lambda: None)
