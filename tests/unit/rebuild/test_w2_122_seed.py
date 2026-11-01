"""Builder tests for ``gov rebuild --seed`` and the failed rebuild without its semantic store (W2-122; DEC-1014,
DEC-1015 item 4).

Regression evidence only (MR-3). Each tree is a temporary git repository; the secrets filter lets every file through,
the embedding endpoint is an in-process stand-in (``semantic._ask``, never the shared server: ``OLLAMA_HOST`` points
at a closed port) and the code-graph tool is a stand-in that builds its home anew, as the tool does.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import subprocess

import pytest

from gov import codeintel
from gov.cli.errors import GovError
from gov.rebuild import seed
from gov.rebuild.command import add_arguments, run
from gov.retrieval import lexical, ollama, semantic

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
PATH_MAP = "namespaces:\n  all: {paths: ['**'], embedding_policy: embedded}\n"
FILES = {".gitignore": ".gov-runtime/\n", "governance/project/path-map.yaml": PATH_MAP,
         "docs/pear.md": "pear trees\n", "docs/plum.md": "plum trees\n", "docs/fig.md": "fig trees\n"}
CONFIG = {"path-map.yaml": {"namespaces": {"all": {"paths": ["**"], "embedding_policy": "embedded"}}}}
STORE = ".gov-runtime/store.db"
CHUNKS = 6  # the tree's files, one chunk each: every file is embedded


def _commit(root, files):
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    for args in (["add", "-A"], ["commit", "-q", "-m", "a change"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env={**_ENV, "HOME": str(root)})


def _repo(path, files):
    path.mkdir()
    subprocess.run(["git", "-C", str(path), "init", "-q", "-b", "main"], check=True, capture_output=True, env=_ENV)
    _commit(path, files)
    return path


def _args(*given):
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    return parser.parse_args(list(given))


def _vectors(root):
    connection = sqlite3.connect(root / STORE)
    try:
        return dict(connection.execute("SELECT chunk_id, embedding FROM semantic_vector"))
    finally:
        connection.close()


@pytest.fixture()
def endpoint(monkeypatch):
    """The embedding endpoint's stand-in: the texts it was asked to embed, its model's digest, and whether it fails."""
    state = {"sent": [], "digest": "ac6da0dfba84" + "0" * 52, "fails": False}

    def ask(path, body=None, host=None):
        if path == "/api/tags":
            return {"models": [{"name": semantic.MODEL, "digest": state["digest"]}]}
        if state["fails"]:
            return None
        state["sent"] += body["input"]
        return {"embeddings": [[float(len(text)), float(sum(map(ord, text)))] for text in body["input"]]}

    def build_home(root):  # the code-graph tool builds its home anew, as ``codeintel.index`` does
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
def base(tmp_path, endpoint):
    """A warm base: a tree rebuilt in full, so it holds its stores and their record."""
    root = _repo(tmp_path / "base", FILES)
    run(root, _args(), CONFIG)
    (root / codeintel.BASE_REL / "home" / "notes.txt").write_text("the tool's own file\n")
    del endpoint["sent"][:]
    return root


@pytest.fixture()
def tree(tmp_path):
    """A tree like the base, with one file changed and one added."""
    return _repo(tmp_path / "tree", {**FILES, "docs/plum.md": "plum orchards\n", "docs/quince.md": "quince trees\n"})


def test_a_full_rebuild_records_its_code_embedder_and_schema(base, endpoint):
    record = json.loads((base / seed.RECORD_REL).read_text())
    assert record["code"] == seed.code_fingerprint() and record["schema"] == seed.schema_version()
    assert record["embedder"] == {"model": semantic.MODEL, "revision": endpoint["digest"]}


def test_a_seeded_rebuild_embeds_only_what_differs_and_equals_a_cold_one(base, tree, endpoint):
    seeded = run(tree, _args("--seed", str(base)), CONFIG)
    assert seeded["seed"]["status"] == "seeded" and seeded["seed"]["base"] == str(base.resolve())
    assert sorted(endpoint["sent"]) == ["plum orchards\n", "quince trees\n"]
    assert (tree / codeintel.BASE_REL / "home" / "code.db").is_file()  # the tree's own home, built anew
    digests, vectors = (seeded["digest"], lexical.digest(tree)), _vectors(tree)
    shutil.rmtree(tree / ".gov-runtime")
    cold = run(tree, _args(), CONFIG)
    assert "seed" not in cold
    assert (cold["digest"], lexical.digest(tree)) == digests
    assert _vectors(tree) == vectors and len(vectors) == CHUNKS


def test_the_code_graph_home_is_copied_into_the_tree_own_home(base, tree):
    answer = seed.seed(tree, str(base), True)  # the copy alone, before any stage
    home = tree / codeintel.BASE_REL / "home"
    assert answer["copied"] == [STORE, f"{codeintel.BASE_REL}/home"]
    assert not home.is_symlink() and (home / "notes.txt").read_text() == "the tool's own file\n"
    assert (home / "code.db").stat().st_ino != (base / codeintel.BASE_REL / "home" / "code.db").stat().st_ino
    assert not (tree / codeintel.BASE_REL / "files").exists()


def test_the_base_is_only_read(base, tree):
    before = {path: path.read_bytes() for path in (base / ".gov-runtime").rglob("*") if path.is_file()}
    run(tree, _args("--seed", str(base)), CONFIG)
    assert {path: path.read_bytes() for path in (base / ".gov-runtime").rglob("*") if path.is_file()} == before


@pytest.mark.parametrize("field, words", [("code", "code fingerprint"), ("schema", "schema"),
                                          ("embedder", "embedder model"), (None, "no readable record")])
def test_a_base_that_differs_is_refused_named_and_the_rebuild_runs_cold(base, tree, endpoint, field, words):
    record_path = base / seed.RECORD_REL
    record = json.loads(record_path.read_text())
    if field is None:
        record_path.unlink()
    else:
        record[field] = {"model": semantic.MODEL, "revision": "another"} if field == "embedder" else "sha256:other"
        record_path.write_text(json.dumps(record))
    result = run(tree, _args("--seed", str(base)), CONFIG)
    assert result["seed"]["status"] == "refused" and words in result["seed"]["reason"]
    if field is None:
        assert str(base) in result["seed"]["reason"]
    assert len(endpoint["sent"]) == CHUNKS  # every chunk embedded: nothing of the base was used
    assert not (tree / ".gov-runtime" / "rebuild" / "seed.tmp").exists()


def test_an_endpoint_now_reporting_another_revision_refuses_the_base(base, tree, endpoint):
    endpoint["digest"] = "b" * 64
    result = run(tree, _args("--seed", str(base)), CONFIG)
    assert result["seed"]["status"] == "refused" and "embedder model" in result["seed"]["reason"]
    assert set(map(tuple, json.loads((tree / seed.RECORD_REL).read_text())["embedder"].items())) == \
        {("model", semantic.MODEL), ("revision", "b" * 64)}


def test_a_link_to_the_base_is_followed_once(base, tree, tmp_path):
    (tmp_path / "link").symlink_to(base)
    result = run(tree, _args("--seed", str(tmp_path / "link")), CONFIG)
    assert result["seed"]["status"] == "seeded" and result["seed"]["base"] == str(base.resolve())


def test_the_configured_base_is_read_and_a_project_without_one_rebuilds_cold(base, tree, tmp_path):
    settings = tree / "governance" / "project" / "rebuild.yaml"
    answer = run(tree, _args("--seed"), CONFIG)["seed"]
    assert answer["status"] == "none" and "integration_store" in answer["reason"] and answer["base"] is None
    settings.write_text(f"integration_store: {tmp_path / 'nowhere'}\n")
    answer = run(tree, _args("--seed"), CONFIG)["seed"]
    assert answer["status"] == "none" and "no warm base" in answer["reason"]
    assert str(tmp_path / "nowhere") in answer["reason"]  # the configured path, named
    settings.write_text(f"integration_store: {base}\n")
    assert run(tree, _args("--seed"), CONFIG)["seed"]["status"] == "seeded"
    settings.write_text(f"integration_store: {tree}\n")
    answer = run(tree, _args("--seed"), CONFIG)["seed"]
    assert answer["status"] == "none" and str(tree) in answer["reason"]  # itself: nothing to seed from


def test_a_folder_given_that_holds_no_base_is_named_as_given_and_as_resolved(tree, endpoint, tmp_path):
    (tmp_path / "empty").mkdir()
    (tmp_path / "link").symlink_to(tmp_path / "empty")
    answer = run(tree, _args("--seed", str(tmp_path / "link")), CONFIG)["seed"]
    assert answer["status"] == "none" and answer["base"] == str((tmp_path / "empty").resolve())
    assert str(tmp_path / "link") in answer["reason"] and answer["base"] in answer["reason"]


def test_a_seed_without_embeddings_keeps_no_vector_and_asks_no_endpoint(base, tree, endpoint, monkeypatch):
    monkeypatch.setattr(semantic, "_ask", lambda *a, **k: pytest.fail("the endpoint was asked"))
    result = run(tree, _args("--no-embeddings", "--seed", str(base)), CONFIG)
    assert result["seed"]["status"] == "seeded"
    connection = sqlite3.connect(tree / STORE)
    names = {name for (name,) in connection.execute("SELECT name FROM sqlite_master")}
    connection.close()
    assert not names & {"semantic_vector", "semantic_manifest"}
    assert not (tree / seed.RECORD_REL).exists()  # no full rebuild: no warm base


@pytest.mark.parametrize("seeded", [False, True])
def test_a_semantic_store_asked_for_and_not_recreated_fails_the_rebuild(base, tree, endpoint, seeded):
    endpoint["fails"] = True
    with pytest.raises(GovError) as raised:
        run(tree, _args(*(("--seed", str(base)) if seeded else ())), CONFIG)
    assert raised.value.code == "REBUILD_FAILED" and raised.value.details["store"] == "semantic"
    assert raised.value.details["reason"] == semantic.NO_EMBEDDING
    assert not (tree / seed.RECORD_REL).exists()
    assert run(tree, _args("--no-embeddings"), CONFIG)["stores"]["semantic"]["requested"] is False

