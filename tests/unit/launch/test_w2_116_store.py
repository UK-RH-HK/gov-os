"""Builder tests for the integration store a launched session searches (W2-116 S3, F1; DEC-963, DEC-1087 (3)).

Regression evidence only (MR-3). ``gov launch``'s settings carry ``GOV_STORE``, the configured link, for every worker
role; a plain ``gov retrieve`` answers from it and never from the working tree. No session is started and no model,
embedder or reranker is asked: the retrieval itself is a stand-in that records the folder it was given.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from gov.cli.errors import GovError
from gov.cli.main import main
from gov.launch import launcher, store
from gov.retrieval import retrieve as retrieval

ROLES = ("engineer", "independent-test-designer", "independent-auditor", "product-spec")


def _project(root: Path, rebuild: str | None) -> Path:
    files = {".tickets/DAEO-t95.md": "---\nid: DAEO-t95\nwbs_id: W2-95\nstatus: in_progress\nrole: engineer\n---\n",
             "governance/project/path-map.yaml": "namespaces: {}\n"}
    if rebuild is not None:
        files["governance/project/rebuild.yaml"] = rebuild
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    return root


@pytest.fixture(autouse=True)
def _no_session_store(monkeypatch):
    monkeypatch.delenv(store.ENV, raising=False)
    monkeypatch.delenv("GOV_ROLE", raising=False)
    monkeypatch.delenv("GOV_TICKET", raising=False)


@pytest.fixture()
def asked(monkeypatch):
    """The retrieval's stand-in: the folders it was asked to answer from."""
    folders = []

    def answer(root, query, **_):
        folders.append(Path(root))
        return {"evidence": []}

    monkeypatch.setattr(retrieval, "retrieve", answer)
    monkeypatch.setattr(retrieval, "role_filter", lambda root, role: None)
    return folders


# The launch ------------------------------------------------------------------------------------------------------

def test_every_worker_session_gets_the_configured_link(tmp_path):
    link = tmp_path / "stores" / "store"
    root = _project(tmp_path / "project", f"embed_headers: true\nintegration_store: {link}\n")
    for role in ROLES:
        env = launcher.build_settings(root, role, "DAEO-t95")["env"]
        assert env[store.ENV] == str(link), role  # the link itself, followed at each search
        assert env["GOV_ROLE"] == role and env["GOV_TICKET"] == "DAEO-t95"


@pytest.mark.parametrize("rebuild", [None, "embed_headers: true\n", ""])
def test_no_place_configured_sets_no_variable(tmp_path, rebuild):
    root = _project(tmp_path / "project", rebuild)
    assert store.ENV not in launcher.build_settings(root, "independent-test-designer", "DAEO-t95")["env"]


@pytest.mark.parametrize("rebuild", ["integration_store: relative/store\n", "integration_store: [a]\n", "- a\n",
                                     "integration_store: [\n"])
def test_a_place_that_cannot_be_used_refuses_the_launch(tmp_path, rebuild):
    root = _project(tmp_path / "project", rebuild)
    with pytest.raises(GovError) as raised:
        launcher.build_settings(root, "engineer", "DAEO-t95")
    assert raised.value.code == "LAUNCH_REFUSED"


# The search ------------------------------------------------------------------------------------------------------

def test_a_plain_retrieve_in_a_launched_session_answers_from_the_integration_store(tmp_path, monkeypatch, asked):
    link = tmp_path / "stores" / "store"
    worktree = _project(tmp_path / "W2-95", f"integration_store: {link}\n")
    env = launcher.build_settings(worktree, "independent-test-designer", "DAEO-t95")["env"]
    monkeypatch.setenv(store.ENV, env[store.ENV])
    monkeypatch.chdir(worktree)
    assert main(["retrieve", "--json", "how is the store refreshed"]) == 0
    assert asked == [link]  # never the worktree the session runs in


def test_a_root_given_wins_and_a_direct_call_keeps_its_root(tmp_path, monkeypatch, asked):
    from gov.retrieve import command

    monkeypatch.setenv(store.ENV, str(tmp_path / "store"))
    assert main(["retrieve", "--json", "--root", str(tmp_path), "a question"]) == 0
    command.run(tmp_path / "given", type("Args", (), {"query": "a question", "ids": [], "ticket": None,
                                                      "continuation": None, "radius": 0, "batch_size": None,
                                                      "bundle_budget": None, "role": None})(), {})
    assert asked == [tmp_path, tmp_path / "given"]


def test_without_the_variable_a_plain_retrieve_answers_from_the_working_tree(tmp_path, monkeypatch, asked):
    monkeypatch.chdir(tmp_path)
    assert main(["retrieve", "--json", "a question"]) == 0
    assert asked == [tmp_path]


def test_a_variable_that_is_no_absolute_path_is_refused(tmp_path, monkeypatch, asked, capsys):
    monkeypatch.setenv(store.ENV, "relative/store")
    monkeypatch.chdir(tmp_path)
    assert main(["retrieve", "--json", "a question"]) == 1
    assert json.loads(capsys.readouterr().out)["error"]["code"] == "STORE_ROOT_INVALID" and asked == []


def test_nothing_at_the_place_is_store_missing_and_never_the_working_tree_store(tmp_path, monkeypatch, capsys):
    """F1: the worktree holds a store of its own; the search does not fall back to it."""
    worktree = tmp_path / "W2-95"
    (worktree / ".gov-runtime").mkdir(parents=True)
    (worktree / ".gov-runtime" / "store.db").write_bytes(b"the worktree's own store, never to be read")
    monkeypatch.setenv(store.ENV, str(tmp_path / "nothing-here"))
    monkeypatch.chdir(worktree)
    assert main(["retrieve", "--json", "a question"]) == 1
    error = json.loads(capsys.readouterr().out)["error"]
    assert error["code"] == "STORE_MISSING" and str(tmp_path / "nothing-here") in error["message"]
