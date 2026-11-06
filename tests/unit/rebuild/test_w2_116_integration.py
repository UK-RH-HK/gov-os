"""Builder tests for ``gov rebuild --integration <branch>``, the seed's ``behind`` note, and a re-index that never
empties the semantic index (W2-116 S1, S4, S5, F2, F3; DEC-963, DEC-983, DEC-1014, DEC-1087 (3)).

Regression evidence only (MR-3). The project is a temporary git repository on a branch ``integrate``; the store's two
halves are worktrees of it beside the configured link. The secrets filter lets every file through, the embedding
endpoint is an in-process stand-in (``semantic._ask``, never the shared server: ``OLLAMA_HOST`` points at a closed
port) and the code-graph tool a stand-in that builds its home anew. No GPU, no model, never the real store.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import shutil
import sqlite3
import subprocess
import threading
import time

import pytest

from gov import codeintel
from gov.cli.errors import GovError
from gov.config.loader import load_config
from gov.rebuild import integration, seed
from gov.rebuild.command import add_arguments, run
from gov.retrieval import lexical, ollama, semantic

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
PATH_MAP = "namespaces:\n  all: {paths: ['**'], embedding_policy: embedded}\n"
STORE = ".gov-runtime/store.db"
BRANCH = "integrate"


def _git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True,
                          env={**_ENV, "HOME": str(root)}).stdout.strip()


def _commit(root, files):
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "a change")
    return _git(root, "rev-parse", "HEAD")


def _args(*given):
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    return parser.parse_args(list(given))


def _snapshot(folder):
    """Every file of a half's stores, by its bytes."""
    return {path: path.read_bytes() for path in (folder / ".gov-runtime").rglob("*") if path.is_file()}


def _count(root, table):
    connection = sqlite3.connect(root / STORE)
    try:
        return connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
    finally:
        connection.close()


@pytest.fixture()
def endpoint(monkeypatch):
    """The embedding endpoint's stand-in: the texts it was asked to embed, and whether it fails."""
    state = {"sent": [], "digest": "ac6da0dfba84" + "0" * 52, "fails": False}

    def ask(path, body=None, host=None):
        if path == "/api/tags":
            return {"models": [{"name": semantic.MODEL, "digest": state["digest"]}]}
        if path == "/api/ps":
            return {"models": [{"name": semantic.MODEL, "model": semantic.MODEL, "size": 1, "size_vram": 1}]}
        if state["fails"]:
            return None
        state["sent"] += body["input"]
        return {"embeddings": [[float(len(text)), float(sum(map(ord, text)))] for text in body["input"]]}

    def build_home(root):
        base = root.resolve() / codeintel.BASE_REL
        if base.exists():
            shutil.rmtree(base)
        (base / "home").mkdir(parents=True)
        sqlite3.connect(base / "home" / "code.db").close()

    monkeypatch.setenv("OLLAMA_HOST", "127.0.0.1:9")
    monkeypatch.setenv("GOV_QUERY_OLLAMA_HOST", "127.0.0.1:9")
    monkeypatch.setenv("GOV_SECRETS_CACHE", "")
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "_ask", ask)
    monkeypatch.setattr(semantic, "_ready", lambda connection, ensure=None: None)
    monkeypatch.setattr(ollama, "ensure_available", lambda **_: {"available": True})
    monkeypatch.setattr(codeintel, "index", build_home)
    return state


@pytest.fixture()
def project(tmp_path, endpoint):
    """The project: a repository on ``integrate`` whose rebuild.yaml names the link ``stores/store``."""
    root = tmp_path / "project"
    root.mkdir()
    _git(root, "init", "-q", "-b", BRANCH)
    link = tmp_path / "stores" / "store"
    _commit(root, {".gitignore": ".gov-runtime/\n", "governance/project/path-map.yaml": PATH_MAP,
                   "governance/project/rebuild.yaml": f"integration_store: {link}\n",
                   "docs/pear.md": "pear trees\n", "docs/plum.md": "plum trees\n", "docs/fig.md": "fig trees\n"})
    (tmp_path / "stores").mkdir()
    return root


def _link(project):
    return integration.place(project)


def _refresh(project):
    return run(project, _args("--integration", BRANCH), {})


def _fresh_vector_cache(monkeypatch, tmp_path, name):
    """A machine-wide vector cache of its own, empty: only the texts sent then show what the build embedded."""
    monkeypatch.setenv("GOV_VECTOR_CACHE_DIR", str(tmp_path / name))


# S1: the double buffer --------------------------------------------------------------------------------------------

def test_the_first_refresh_builds_one_half_and_points_the_link_at_it(project, endpoint):
    result = _refresh(project)
    link = _link(project)
    first, second = integration.halves(link)
    assert result["integration"]["status"] == "switched" and result["integration"]["previous"] is None
    assert link.is_symlink() and os.path.realpath(link) == str(first.resolve())
    assert _git(first, "rev-parse", "HEAD") == _git(project, "rev-parse", BRANCH)
    assert result["stores"]["semantic"]["status"] == "recreated" and not second.exists()
    assert (first / seed.RECORD_REL).is_file()  # complete: a warm base for the next refresh
    assert endpoint["sent"]


def test_at_an_unchanged_head_it_does_nothing(project, endpoint):
    _refresh(project)
    link = _link(project)
    before = _snapshot(integration.halves(link)[0])
    del endpoint["sent"][:]
    result = _refresh(project)
    assert result == {"integration": {"branch": BRANCH, "head": _git(project, "rev-parse", BRANCH), "link": str(link),
                                      "ready": str(integration.halves(link)[0].resolve()), "status": "unchanged"}}
    assert not endpoint["sent"] and not integration.halves(link)[1].exists()
    assert _snapshot(integration.halves(link)[0]) == before


def test_a_new_head_is_built_into_the_other_half_seeded_so_only_what_changed_is_embedded(project, endpoint,
                                                                                         monkeypatch, tmp_path):
    _refresh(project)
    link = _link(project)
    first, second = integration.halves(link)
    old = _git(project, "rev-parse", BRANCH)
    before = _snapshot(first)
    new = _commit(project, {"docs/plum.md": "plum orchards\n", "docs/quince.md": "quince trees\n"})
    _fresh_vector_cache(monkeypatch, tmp_path, "empty-vector-cache")
    del endpoint["sent"][:]
    result = _refresh(project)
    assert result["integration"]["status"] == "switched"
    assert os.path.realpath(link) == str(second.resolve()) and _git(second, "rev-parse", "HEAD") == new
    assert sorted(endpoint["sent"]) == ["plum orchards\n", "quince trees\n"]  # seeded from the ready half
    assert result["seed"]["status"] == "seeded" and result["seed"]["base"] == str(first.resolve())
    assert result["seed"]["base_head"] == old and old in result["seed"]["behind"] and "behind" in \
        result["seed"]["behind"]
    assert _snapshot(first) == before  # the ready half is only read
    # and a third head goes back into the first half, seeded from the second
    _commit(project, {"docs/fig.md": "fig orchards\n"})
    del endpoint["sent"][:]
    third = _refresh(project)
    assert os.path.realpath(link) == str(first.resolve()) and sorted(endpoint["sent"]) == ["fig orchards\n"]
    assert third["seed"]["base"] == str(second.resolve())


def test_the_seeded_half_equals_a_cold_build_of_the_same_head(project, endpoint, tmp_path):
    _refresh(project)
    _commit(project, {"docs/plum.md": "plum orchards\n"})
    result = _refresh(project)
    half = integration.halves(_link(project))[1]
    cold = tmp_path / "cold"
    _git(project, "worktree", "add", "-q", "--detach", str(cold), BRANCH)
    assert run(cold, _args(), load_config(cold))["digest"] == result["digest"]
    assert lexical.digest(cold) == lexical.digest(half)


# F2: a search during a build, and a build that fails or is killed --------------------------------------------------

def test_a_search_during_a_build_is_answered_from_the_ready_half(project, endpoint, monkeypatch):
    _refresh(project)
    link = _link(project)
    first = integration.halves(link)[0]
    _commit(project, {"docs/pear.md": "pear orchards\n"})
    real, seen = semantic.refresh, {}

    def during(root):
        seen["link"] = os.path.realpath(link)
        seen["answer"] = lexical.search(link, "pear", refresh=False)
        return real(root)

    monkeypatch.setattr(semantic, "refresh", during)
    _refresh(project)
    assert seen["link"] == str(first.resolve())
    assert seen["answer"]["available"] and any("pear trees" in hit["text"] for hit in seen["answer"]["hits"])
    assert not any("pear orchards" in hit["text"] for hit in seen["answer"]["hits"])


@pytest.mark.parametrize("how", ["endpoint fails", "model-less", "stage raises"])
def test_a_failed_build_never_moves_the_link_and_leaves_the_ready_half_as_it_was(project, endpoint, monkeypatch, how):
    _refresh(project)
    link = _link(project)
    first, second = integration.halves(link)
    before = _snapshot(first)
    _commit(project, {"docs/plum.md": "plum orchards\n"})
    if how == "endpoint fails":
        endpoint["fails"] = True
    elif how == "model-less":
        monkeypatch.setattr(semantic, "_ready", lambda connection, ensure=None: ollama.WARNING)
    else:
        monkeypatch.setattr(lexical, "refresh", lambda root: (_ for _ in ()).throw(RuntimeError("disk full")))
    with pytest.raises(GovError) as raised:
        _refresh(project)
    assert raised.value.code == "REBUILD_FAILED" and str(first) in raised.value.message
    assert os.path.realpath(link) == str(first.resolve()) and _snapshot(first) == before
    assert not (second / seed.RECORD_REL).exists()  # the half left behind is no warm base
    if how != "stage raises":  # N-2: the build ran; its semantic store was not recreated, so it is not switched to
        assert raised.value.details["stores"]["semantic"]["status"] == "not_recreated"


def test_a_build_killed_half_way_leaves_the_link_and_the_next_refresh_seeds_over_it(project, endpoint, monkeypatch):
    _refresh(project)
    link = _link(project)
    first, second = integration.halves(link)
    new = _commit(project, {"docs/plum.md": "plum orchards\n"})
    real = semantic.refresh

    def killed(root):
        raise KeyboardInterrupt  # the process stopped between the lexical stage and the switch

    monkeypatch.setattr(semantic, "refresh", killed)
    with pytest.raises(KeyboardInterrupt):
        _refresh(project)
    assert os.path.realpath(link) == str(first.resolve())
    assert lexical.search(link, "plum", refresh=False)["available"]  # the ready half still answers
    monkeypatch.setattr(semantic, "refresh", real)
    del endpoint["sent"][:]
    result = _refresh(project)
    assert result["integration"]["status"] == "switched" and os.path.realpath(link) == str(second.resolve())
    assert result["seed"]["status"] == "seeded" and _git(second, "rev-parse", "HEAD") == new


def test_the_running_code_changed_at_the_same_head_builds_again(project, endpoint, monkeypatch):
    """The store always matches the code that searches it: a record of other code is not unchanged."""
    _refresh(project)
    monkeypatch.setattr(seed, "code_fingerprint", lambda: "sha256:other code")
    result = _refresh(project)
    assert result["integration"]["status"] == "switched"
    assert result["seed"]["status"] == "refused" and "code fingerprint" in result["seed"]["reason"]


# Refusals --------------------------------------------------------------------------------------------------------

def test_a_link_that_is_a_folder_is_refused_and_left(project):
    link = _link(project)
    link.mkdir()
    (link / "kept.txt").write_text("mine\n")
    with pytest.raises(GovError, match="not a symbolic link"):
        _refresh(project)
    assert (link / "kept.txt").read_text() == "mine\n" and not integration.halves(link)[0].exists()


def test_a_half_that_is_a_foreign_folder_is_refused_and_left(project):
    first = integration.halves(_link(project))[0]
    first.mkdir()
    (first / "kept.txt").write_text("mine\n")
    with pytest.raises(GovError, match="not a worktree"):
        _refresh(project)
    assert (first / "kept.txt").read_text() == "mine\n" and not os.path.lexists(_link(project))


def test_a_half_of_another_repository_is_refused(project, tmp_path):
    other = tmp_path / "other"
    other.mkdir()
    _git(other, "init", "-q")
    _commit(other, {"a.md": "a\n"})
    first = integration.halves(_link(project))[0]
    _git(other, "worktree", "add", "-q", "--detach", str(first))
    with pytest.raises(GovError, match="another repository"):
        _refresh(project)


def test_no_place_configured_an_unknown_branch_and_other_flags_are_refused(project):
    with pytest.raises(GovError, match="not known"):
        run(project, _args("--integration", "nowhere"), {})
    for flags in (("--seed",), ("--no-embeddings",)):
        with pytest.raises(GovError, match="takes no"):
            run(project, _args("--integration", BRANCH, *flags), {})
    (project / "governance/project/rebuild.yaml").write_text("embed_headers: false\n")
    with pytest.raises(GovError, match="names no integration_store"):
        _refresh(project)
    (project / "governance/project/rebuild.yaml").write_text("integration_store: relative/store\n")
    with pytest.raises(GovError, match="absolute path"):
        _refresh(project)


def test_a_held_lock_is_waited_for(project, endpoint, capfd):
    link = _link(project)
    holder = os.open(link.with_name(link.name + ".lock"), os.O_RDWR | os.O_CREAT)
    fcntl.flock(holder, fcntl.LOCK_EX)
    outcome = {}
    worker = threading.Thread(target=lambda: outcome.update(result=_refresh(project)))
    worker.start()
    try:
        time.sleep(1.0)
        assert worker.is_alive() and not os.path.lexists(link)
    finally:
        fcntl.flock(holder, fcntl.LOCK_UN)
        os.close(holder)
    worker.join(120)
    assert outcome["result"]["integration"]["status"] == "switched"
    assert "waiting for the integration store's lock" in capfd.readouterr().err


# S4: the seed names a base behind the head ------------------------------------------------------------------------

def test_a_seed_at_the_head_does_not_say_behind(project, endpoint, tmp_path):
    run(project, _args(), load_config(project))
    tree = tmp_path / "tree"
    _git(project, "worktree", "add", "-q", "--detach", str(tree), BRANCH)
    result = run(tree, _args("--seed", str(project)), load_config(tree))
    assert result["seed"]["status"] == "seeded"
    assert "behind" not in json.dumps(result) and "base_head" not in result["seed"]


def test_a_seed_from_a_base_behind_names_its_head_and_how_far(project, endpoint, tmp_path):
    run(project, _args(), load_config(project))
    old = _git(project, "rev-parse", "HEAD")
    tree = tmp_path / "tree"
    _git(project, "worktree", "add", "-q", "-b", "ahead", str(tree), BRANCH)
    _commit(tree, {"docs/plum.md": "plum orchards\n"})
    _commit(tree, {"docs/fig.md": "fig orchards\n"})
    result = run(tree, _args("--seed", str(project)), load_config(tree))
    assert result["seed"]["base_head"] == old
    assert f"built at {old}, behind this tree's head" in result["seed"]["behind"] and "by 2 commit" in \
        result["seed"]["behind"]


# S5, F3: a re-index never empties the semantic index ---------------------------------------------------------------

def test_a_model_less_reindex_keeps_the_vectors_and_reports_the_facet_unavailable(project, endpoint, monkeypatch):
    run(project, _args(), load_config(project))
    vectors = _count(project, "semantic_vector")
    _commit(project, {"docs/plum.md": "plum orchards\n"})
    monkeypatch.setattr(semantic, "_ready", lambda connection, ensure=None: ollama.WARNING)
    monkeypatch.setattr(semantic, "_ask", lambda *a, **k: pytest.fail("the endpoint was asked"))
    result = run(project, _args(), load_config(project))
    assert result["stores"]["semantic"] == {"status": "not_recreated", "reason": ollama.WARNING}
    assert _count(project, "semantic_vector") == vectors > 0
    assert semantic.search(project, "plum", refresh=False)["available"] is False


def test_a_failed_reindex_leaves_the_previous_index_and_reports_it(project, endpoint, monkeypatch):
    run(project, _args(), load_config(project))
    chunks, vectors = _count(project, "lexical_chunk"), _count(project, "semantic_vector")
    _commit(project, {"docs/plum.md": "plum orchards\n"})
    monkeypatch.setattr(lexical, "refresh", lambda root: (_ for _ in ()).throw(RuntimeError("disk full")))
    with pytest.raises(GovError) as raised:
        run(project, _args(), load_config(project))
    assert raised.value.code == "REBUILD_FAILED" and "disk full" in raised.value.message
    assert (_count(project, "lexical_chunk"), _count(project, "semantic_vector")) == (chunks, vectors)
    assert vectors > 0
