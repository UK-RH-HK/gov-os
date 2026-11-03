"""Builder tests for ``gov retrieve``'s stated gap (W2-13; RETR-X-02, AR-9, DEC-900).

Regression evidence only (DEC-136). A question asked alone whose ids exist nowhere stops with ``UNRESOLVED_IDS``,
names each id as a gap and cites nothing; an id a file holds, or a question with ``--id``, is retrieved as before.
The store is built in a temporary repository (DEC-322); the semantic route is replaced, so no endpoint is asked.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import closure, store  # noqa: E402
from gov.retrieval import lexical, semantic  # noqa: E402
from gov.retrieval import retrieve as retrieve_module  # noqa: E402
from gov.retrieve import command  # noqa: E402

REAL_SEMANTIC_SEARCH = semantic.search

pytestmark = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")
MISSING = "-".join(("DEC", "9999"))


@pytest.fixture()
def root(tmp_path, monkeypatch):
    git = ["git", "-C", str(tmp_path), "-c", "user.name=unit", "-c", "user.email=unit@example.invalid"]
    subprocess.run([*git, "init", "-q"], check=True)
    (tmp_path / "governance/project").mkdir(parents=True)
    path_map = yaml.safe_load((REPO / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    path_map["namespaces"] = {"notes": {**next(iter(path_map["namespaces"].values())), "paths": ["**"]}}
    path_map.pop("decision_register", None)
    (tmp_path / "governance/project/path-map.yaml").write_text(yaml.safe_dump(path_map), encoding="utf-8")
    shutil.copy2(REPO / "template/.gitleaks.toml", tmp_path / ".gitleaks.toml")
    (tmp_path / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    for number in (1, 2, 3):
        (tmp_path / f"note{number}.md").write_text(f"# Note {number}\n\nWhat the harbour decides, pier {number}.\n",
                                                   encoding="utf-8")
    (tmp_path / "held.md").write_text(f"# Held\n\nSee {MISSING}9 and DEC-41 for the harbour.\n", encoding="utf-8")
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "fixture"], check=True)
    lexical.refresh(tmp_path)
    store.load(tmp_path)
    hits = [{"chunk_id": chunk["chunk_id"], "path": chunk["path"]} for chunk in lexical.chunks(tmp_path)]
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "reason": None,
                                                                       "hits": hits})
    monkeypatch.setattr(retrieve_module, "rerank", lambda _query, candidates, _reranker=None: candidates)  # no model
    monkeypatch.setattr(closure, "_symbol", lambda *_args: None)  # no code-graph tool is asked
    return tmp_path


def _ask(root, query, **more):
    args = argparse.Namespace(query=query, ticket=None, ids=[], radius=0, batch_size=None, bundle_budget=None,
                              continuation=None, **more)
    return command.run(root, args, {})


@pytest.mark.parametrize("query", [MISSING, f"What does {MISSING} decide?"])
def test_an_id_that_exists_nowhere_is_the_stated_gap(root, query):
    bundle = _ask(root, query)
    assert bundle["stopping_reason"] == "UNRESOLVED_IDS" and bundle["evidence"] == []
    assert bundle["gaps"] == [{"id": MISSING, "reason": "UNRESOLVED"}] and bundle["continuation"] is None
    assert bundle["facets"]["lexical"]["available"] is True and "semantic" in bundle["facets"]


def test_an_id_a_file_holds_is_answered_as_before(root):
    bundle = _ask(root, "What does DEC-41 decide?")
    assert bundle["stopping_reason"] != "UNRESOLVED_IDS" and bundle["evidence"]


def test_a_question_without_an_id_is_answered_as_before(root):
    assert _ask(root, "What does the harbour decide?")["evidence"]


def _given(root, query, ids=(), ticket=None):
    return command.run(root, argparse.Namespace(query=query, ticket=ticket, ids=list(ids), radius=0, batch_size=None,
                                                bundle_budget=None, continuation=None), {})


@pytest.mark.parametrize("ids, ticket", [([MISSING], None), ([], "RT-9999"), ([MISSING, "ADR-0404"], None)])
def test_ids_and_a_ticket_that_exist_nowhere_are_the_stated_gap(root, ids, ticket):
    bundle = _given(root, f"What does {MISSING} decide?", ids, ticket)
    assert bundle["stopping_reason"] == "UNRESOLVED_IDS" and bundle["evidence"] == []
    assert bundle["continuation"] is None and bundle["batches"] == [{"size": 0}]
    assert {gap["id"] for gap in bundle["gaps"]} == {MISSING, *ids, *([ticket] if ticket else [])}


@pytest.mark.parametrize("ids", [[MISSING, "DEC-41"], [MISSING, "resize"]], ids=["one-id-exists", "a-symbol-name"])
def test_an_id_that_exists_or_a_symbol_name_is_retrieved_as_before(root, ids):
    bundle = _given(root, f"What does {MISSING} decide?", ids)
    assert bundle["evidence"] and MISSING in {gap.get("id") for gap in bundle["gaps"]}


def test_a_store_that_is_no_database_is_a_governance_error_not_a_traceback(root, capsys, monkeypatch):
    from gov.cli.main import main

    # The real semantic route: it reads the store before it asks any endpoint, so it meets the same bad file. Since
    # W2-92 the record graph's fault is that route's alone, and the double would answer from a store that is none.
    monkeypatch.setattr(semantic, "search", REAL_SEMANTIC_SEARCH)
    (root / ".gov-runtime/store.db").write_bytes(b"this is no database" * 100)
    code = main(["retrieve", "--json", "--root", str(root), "pilot tide harbour"])
    out, err = capsys.readouterr()
    assert code == 1 and "Traceback" not in err and "STORE_UNREADABLE" in out, (code, out, err)


def test_a_stale_index_decides_nothing(root):
    (root / "note1.md").write_text("# Note 1\n\nChanged.\n", encoding="utf-8")
    assert command._nowhere(root, MISSING) is None
