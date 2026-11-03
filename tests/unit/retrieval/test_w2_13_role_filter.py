"""Builder tests for search's role separation in ``gov retrieve`` (W2-13 S5; DEC-1065 (2)).

Regression evidence only (DEC-136). A temporary repository is indexed and loaded; the semantic route is a stand-in
that names the same chunks as the lexical one (no embedder runs). Every route's hits are filtered by the caller's
role paths, what is withheld is counted in the bundle, and no section or no role is today's bundle.
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

from gov import store  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402
from gov.retrieval import code_route, lexical, semantic  # noqa: E402
from gov.retrieval import retrieve as retrieve_module  # noqa: E402
from gov.retrieval.retrieve import retrieve  # noqa: E402
from gov.retrieve import command  # noqa: E402

pytestmark = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")
CASE = "tests/acceptance/W2-99/test_heron.py"
SECTION = {"engineer": {"reads_denied": ["{ticket_tests}"]},
           "independent-test-designer": {"reads_denied": ["{ticket_impl}"]}}


def _write_map(root: Path, role_paths) -> None:
    path_map = yaml.safe_load((REPO / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    path_map["namespaces"] = {"notes": {**next(iter(path_map["namespaces"].values())), "paths": ["**"]}}
    path_map.pop("decision_register", None)
    path_map.pop("role_paths", None)
    if role_paths is not None:
        path_map["role_paths"] = role_paths
    (root / "governance/project/path-map.yaml").write_text(yaml.safe_dump(path_map), encoding="utf-8")


def _build(tmp_path, monkeypatch, section):
    """An indexed repository: a note and the ticket W2-99's acceptance case, both about the heron ledger."""
    git = ["git", "-C", str(tmp_path), "-c", "user.name=unit", "-c", "user.email=unit@example.invalid"]
    subprocess.run([*git, "init", "-q"], check=True)
    (tmp_path / "governance/project").mkdir(parents=True)
    _write_map(tmp_path, section)
    shutil.copy2(REPO / "template/.gitleaks.toml", tmp_path / ".gitleaks.toml")
    (tmp_path / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    (tmp_path / ".tickets").mkdir()
    (tmp_path / ".tickets/DAEO-pier.md").write_text("---\nid: DAEO-pier\nwbs_id: W2-99\n---\n# The pier\n",
                                                     encoding="utf-8")
    (tmp_path / "note.md").write_text("# Note\n\nThe heron ledger of the pier.\n", encoding="utf-8")
    (tmp_path / CASE).parent.mkdir(parents=True)
    (tmp_path / CASE).write_text("def test_heron_ledger():\n    assert 'the heron ledger is kept'\n", encoding="utf-8")
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "fixture"], check=True)
    lexical.refresh(tmp_path)
    store.load(tmp_path)

    def stand_in(root, _query, **_kwargs):  # the semantic route names every chunk of both files
        hits = [c for c in lexical.chunks(root) if c["path"] in ("note.md", CASE)]
        return {"available": True, "reason": None, "hits": hits}
    monkeypatch.setattr(semantic, "search", stand_in)
    monkeypatch.setattr(code_route, "route", lambda *_args: None)
    monkeypatch.setattr(retrieve_module, "rerank", lambda _query, candidates, _reranker=None: candidates)  # no model
    monkeypatch.delenv("GOV_ROLE", raising=False)
    monkeypatch.delenv("GOV_TICKET", raising=False)
    return tmp_path


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    return _build(tmp_path, monkeypatch, SECTION)


@pytest.fixture()
def bare(tmp_path, monkeypatch):
    return _build(tmp_path, monkeypatch, None)


def _paths(bundle) -> set:
    return {item["path"] for item in bundle["evidence"]} | {gap.get("path") for gap in bundle["gaps"]} - {None}


def test_no_role_is_todays_bundle(repo):
    bundle = retrieve(repo, "heron ledger", reranker=lambda: None)
    assert CASE in _paths(bundle) and "note.md" in _paths(bundle)
    assert "role_filter" not in bundle


def test_the_engineer_never_gets_its_tickets_acceptance_tests_from_any_route(repo, monkeypatch):
    monkeypatch.setenv("GOV_ROLE", "engineer")
    monkeypatch.setenv("GOV_TICKET", "DAEO-pier")
    bundle = retrieve(repo, "heron ledger", reranker=lambda: None)
    assert CASE not in _paths(bundle) and "note.md" in _paths(bundle)
    assert all(CASE not in item["text"] for item in bundle["evidence"])
    shown = bundle["role_filter"]
    assert shown["roles"] == ["engineer"] and shown["ticket"] == "DAEO-pier" and "role_paths" in shown["rule"]
    assert shown["withheld"]["paths"] == 1 and shown["withheld"]["chunks"] >= 1  # lexical and semantic, once
    assert [(b["rule"], b["glob"], b["paths"]) for b in shown["by"]] == [
        ("{ticket_tests}", "tests/acceptance/W2-99/**", 1)]


def test_a_role_given_adds_the_filter_and_never_lifts_the_sessions(repo, monkeypatch):
    monkeypatch.setenv("GOV_TICKET", "DAEO-pier")
    assert CASE not in _paths(retrieve(repo, "heron ledger", reranker=lambda: None, role="engineer"))
    monkeypatch.setenv("GOV_ROLE", "engineer")
    bundle = retrieve(repo, "heron ledger", reranker=lambda: None, role="orchestrator")
    assert CASE not in _paths(bundle) and bundle["role_filter"]["roles"] == ["engineer"]


def test_another_ticket_or_a_role_the_section_does_not_name_is_not_filtered(repo, monkeypatch):
    monkeypatch.setenv("GOV_TICKET", "DAEO-pier")
    monkeypatch.setenv("GOV_ROLE", "orchestrator")
    assert "role_filter" not in retrieve(repo, "heron ledger", reranker=lambda: None)
    monkeypatch.setenv("GOV_ROLE", "engineer")
    monkeypatch.setenv("GOV_TICKET", "DAEO-other")
    assert CASE in _paths(retrieve(repo, "heron ledger", reranker=lambda: None))


def test_no_section_is_no_filter(bare, monkeypatch):
    monkeypatch.setenv("GOV_ROLE", "engineer")
    monkeypatch.setenv("GOV_TICKET", "DAEO-pier")
    bundle = retrieve(bare, "heron ledger", reranker=lambda: None)
    assert CASE in _paths(bundle) and "role_filter" not in bundle


def test_a_section_that_cannot_be_read_hands_nothing_out(repo, monkeypatch):
    _write_map(repo, None)
    with open(repo / "governance/project/path-map.yaml", "a", encoding="utf-8") as f:
        f.write("role_paths:\n  engineer: [\"{ticket_tests}\"]\n")
    monkeypatch.setenv("GOV_ROLE", "engineer")
    with pytest.raises(GovError) as raised:
        retrieve(repo, "heron ledger", reranker=lambda: None)
    assert raised.value.code == "ROLE_PATHS_UNREADABLE"


def _args(query, **given):
    base = {"query": query, "ids": [], "ticket": None, "radius": 0, "batch_size": None, "bundle_budget": None,
            "continuation": None, "role": None}
    return argparse.Namespace(**{**base, **given})


def test_gov_retrieve_takes_role_and_names_the_filter_on_the_stated_gap_too(repo, monkeypatch):
    monkeypatch.setenv("GOV_TICKET", "DAEO-pier")
    bundle = command.run(repo, _args("heron ledger", role="engineer"), {})
    assert CASE not in _paths(bundle) and bundle["role_filter"]["withheld"]["paths"] == 1
    gap = command.run(repo, _args("What did DEC-4242 say?", role="engineer"), {})
    assert gap["stopping_reason"] == "UNRESOLVED_IDS" and gap["evidence"] == []
    assert gap["role_filter"]["withheld"] == {"paths": 0, "chunks": 0}
    assert "role_filter" not in command.run(repo, _args("What did DEC-4242 say?"), {})


# -- gov context's supplementary block (gov.retrieval.supplementary) -----------------------------------------------

def _block_paths(block) -> set:
    return {item["path"] for item in block["supplementary"]} | {item["path"] for item in block["further_batch"]}


def test_the_supplementary_block_without_a_role_is_todays(repo):
    from gov.retrieval import supplementary
    block = supplementary.stack(repo, "The heron ledger", [], 5000)
    assert CASE in _block_paths(block) and "note.md" in _block_paths(block)
    assert "role_filter" not in block and all(entry["id"] != "role_filter" for entry in block["dropped"])


def test_the_supplementary_block_withholds_the_engineers_tests_and_names_it_in_dropped(repo, monkeypatch):
    from gov.retrieval import supplementary
    monkeypatch.setenv("GOV_ROLE", "engineer")
    monkeypatch.setenv("GOV_TICKET", "DAEO-pier")
    block = supplementary.stack(repo, "The heron ledger", [], 5000)
    assert CASE not in _block_paths(block) and "note.md" in _block_paths(block)
    assert all(CASE not in item["text"] for item in block["supplementary"])
    assert block["role_filter"]["withheld"]["paths"] == 1
    named = [entry for entry in block["dropped"] if entry["id"] == "role_filter"]
    assert len(named) == 1 and "1 paths" in named[0]["reason"] and "{ticket_tests}" in named[0]["reason"]


def test_a_supplementary_block_whose_role_paths_cannot_be_read_is_empty_and_says_why(repo, monkeypatch):
    from gov import context
    with open(repo / "governance/project/path-map.yaml", "a", encoding="utf-8") as f:
        f.write("role_paths:\n  engineer: [\"{ticket_tests}\"]\n")  # a second, malformed section
    monkeypatch.setenv("GOV_ROLE", "engineer")
    block = context._try_supplementary(repo, "The heron ledger", [], 5000, set(), set())
    assert block["supplementary"] == [] and block["further_batch"] == []
    assert block["dropped"][0]["id"] == "supplementary" and "role_paths" in block["dropped"][0]["reason"]


# -- gov context --role: the role given reaches the supplementary block (the CTO's red, 2026-11-03) ---------------

_CTX_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t.invalid", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
_CTX_CASE = "tests/acceptance/W2-99/test_quokka.py"
_CTX_FILES = {
    ".gitignore": ".gov-runtime/\n",
    "governance/project/path-map.yaml": yaml.safe_dump({"decision_register": "docs/DECISION_REGISTER.md",
                                                       "role_paths": SECTION}),
    "docs/DECISION_REGISTER.md": "# Register\n\n### DEC-101 — The decision\n- **Status:** ACCEPTED\n\nIts text.\n",
    ".tickets/TK-1.md": ("---\nid: TK-1\nwbs_id: W2-99\ntype: task\nstatus: open\ntitle: zebra ticket\n"
                         "sources: [DEC-101]\nkpis:\n  success:\n  - the quokka line holds\n---\n# TK-1\n"),
    "notes/quokka.md": "# Planted\n\nthe quokka is found here\n",
    _CTX_CASE: "def test_quokka():\n    assert 'the quokka line holds'\n",
}


@pytest.fixture()
def project(tmp_path, monkeypatch):
    """A gov context project whose ticket W2-99 has an acceptance case and a note, both about the quokka."""
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))  # no gitleaks needed
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True, capture_output=True,
                   env=_CTX_ENV)
    for rel, text in _CTX_FILES.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    for args in (["add", "-A"], ["commit", "-q", "-m", "fixture"]):
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True,
                       env={**_CTX_ENV, "HOME": str(tmp_path)})
    store.load(tmp_path)
    lexical.refresh(tmp_path)
    monkeypatch.delenv("GOV_ROLE", raising=False)
    monkeypatch.setenv("GOV_TICKET", "TK-1")
    return tmp_path


def _packet_paths(packet) -> set:
    return {item["path"] for item in packet["supplementary"]} | {item["path"] for item in packet["further_batch"]}


def test_gov_context_with_role_given_withholds_the_engineers_tests_and_names_it(project, monkeypatch):
    from gov import context
    plain = context.context(project, "TK-1")
    assert _CTX_CASE in _packet_paths(plain) and all(e["id"] != "role_filter" for e in plain["dropped"])
    packet = context.context(project, "TK-1", role="engineer")  # gov context ... --role engineer, GOV_ROLE unset
    assert _CTX_CASE not in _packet_paths(packet) and "notes/quokka.md" in _packet_paths(packet)
    named = [entry for entry in packet["dropped"] if entry["id"] == "role_filter"]
    assert len(named) == 1 and "1 paths" in named[0]["reason"] and "engineer" in named[0]["reason"]
    monkeypatch.setenv("GOV_ROLE", "engineer")  # a role given never lifts the session's
    assert _CTX_CASE not in _packet_paths(context.context(project, "TK-1", role="orchestrator"))
