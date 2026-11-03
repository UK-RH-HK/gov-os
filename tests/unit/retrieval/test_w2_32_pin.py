"""W2-32 S1, S2 (CAP-19.a, CAP-10.b; W2-M073, W2-L065): the embedder's pin in configuration, a full re-embed when
it changes, and a fail-closed, named refusal when it is unpinned or does not match.

Regression evidence only (DEC-136): no model is started. ``_ask`` and ``_ready`` are stand-ins, as in
``tests/unit/semantic/test_semantic.py``; every store is in a temporary git repository with the secret filter
replaced.
"""
from __future__ import annotations

import sqlite3
import struct
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.config import models  # noqa: E402
from gov.retrieval import learning, lexical, semantic  # noqa: E402
from gov.store import STORE_REL  # noqa: E402

PINNED = models.DEFAULT_REVISION + "0" * 52
OTHER = "5e" + "1" * 62
_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
PATH_MAP = "namespaces:\n  open: {paths: ['open/**', 'fixtures/**'], embedding_policy: embedded}\n"
FILES = {".gitignore": ".gov-runtime/\n", "governance/project/path-map.yaml": PATH_MAP,
         "open/pear.md": "pear trees\n", "open/plum.md": "plum trees\n"}


def _commit(root, files):
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    for args in (["add", "-A"], ["commit", "-q", "-m", "a change"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                       env={**_ENV, "HOME": str(root)})


def _pin(root, model=semantic.MODEL, revision=PINNED):
    line = f"embedder:\n  model: {model}\n" + ("" if revision is None else f"  revision: {revision!r}\n")
    (root / models.MODELS_REL).write_text(line, encoding="utf-8")


def _distance(left, right):
    count = len(left) // 4
    return sum(abs(a - b) for a, b in zip(struct.unpack(f"{count}f", left), struct.unpack(f"{count}f", right)))


@pytest.fixture()
def project(tmp_path, monkeypatch):
    """A repository, and the endpoint's stand-in: the models it lists with their digests, what it was asked."""
    endpoint = {"sent": [], "models": {semantic.MODEL: PINNED}, "query": None, "asked_for": []}

    def ask(path, body=None, host=None):
        listed = endpoint["models"] if host is None or endpoint["query"] is None else endpoint["query"]
        if path == "/api/tags":
            return {"models": [{"name": name, "digest": digest} for name, digest in listed.items()]}
        if path == "/api/ps":
            return {"models": [{"name": name, "size": 1, "size_vram": 1} for name in listed]}
        endpoint["asked_for"].append(body["model"])
        endpoint["sent"] += body["input"]
        return {"embeddings": [[float("pear" in text), float("plum" in text)] for text in body["input"]]}

    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "_ask", ask)
    monkeypatch.setattr(semantic, "_ready", lambda connection, ensure=None:
                        connection.create_function("vec_distance_cosine", 2, _distance))
    monkeypatch.setenv("GOV_VECTOR_CACHE_DIR", str(tmp_path / "machine-cache"))
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "-C", str(root), "init", "-q", "-b", "main"], check=True, capture_output=True, env=_ENV)
    _commit(root, FILES)
    return root, endpoint


# --- the pin as configured -----------------------------------------------------------------------------------------

def test_without_a_file_adr_0002_s_pin_holds(tmp_path):
    pin = models.embedder(tmp_path)
    assert (pin.model, pin.revision) == ("qwen3-embedding:0.6b", "ac6da0dfba84")
    assert pin.matches(PINNED) and pin.matches("sha256:" + PINNED) and not pin.matches(OTHER) and not pin.matches(None)


@pytest.mark.parametrize("revision", [OTHER, OTHER[:12], "sha256:" + OTHER])
def test_a_file_pins_the_model_and_a_digest_or_a_prefix_of_at_least_12(tmp_path, revision):
    (tmp_path / "governance/project").mkdir(parents=True)
    _pin(tmp_path, "nomic-embed-text:v1.5", revision)
    pin = models.embedder(tmp_path)
    assert pin.model == "nomic-embed-text:v1.5" and pin.matches(OTHER) and not pin.matches(PINNED)


@pytest.mark.parametrize("revision", [None, "", "  ", "latest", OTHER[:11], 42])
def test_a_model_without_a_revision_is_unpinned_by_name(tmp_path, revision):
    (tmp_path / "governance/project").mkdir(parents=True)
    text = "embedder:\n  model: nomic-embed-text\n" + ("" if revision is None else f"  revision: {revision!r}\n")
    (tmp_path / models.MODELS_REL).write_text(text, encoding="utf-8")
    with pytest.raises(GovError) as raised:
        models.embedder(tmp_path)
    assert raised.value.code == "MODEL_UNPINNED" and "MODEL_UNPINNED" in raised.value.message


@pytest.mark.parametrize("text", ["[]\n", "reranker: {model: x, revision: abc}\n", "embedder: x\n",
                                  "embedder: {revision: " + OTHER + "}\n",
                                  "embedder: {model: m, revision: " + OTHER + ", tag: z}\n", "embedder: [\n"])
def test_any_other_fault_is_config_invalid(tmp_path, text):
    (tmp_path / "governance/project").mkdir(parents=True)
    (tmp_path / models.MODELS_REL).write_text(text, encoding="utf-8")
    with pytest.raises(GovError) as raised:
        models.embedder(tmp_path)
    assert raised.value.code == "CONFIG_INVALID"


# --- S1: a changed pin is a full re-embed ----------------------------------------------------------------------------

def test_a_changed_revision_in_configuration_embeds_every_chunk_again(project):
    root, endpoint = project
    assert semantic.refresh(root)["available"] is True
    endpoint["sent"].clear()
    assert semantic.refresh(root)["available"] is True and endpoint["sent"] == []  # the same pin: nothing again
    endpoint["models"][semantic.MODEL] = OTHER
    _pin(root, revision=OTHER[:12])
    assert semantic.refresh(root)["available"] is True
    assert sorted(endpoint["sent"]) == ["pear trees\n", "plum trees\n"]
    assert semantic.manifest(root)["embedder"] == {"model": semantic.MODEL, "revision": OTHER}
    assert semantic.search(root, "pear", refresh=False)["available"] is True


def test_another_model_in_configuration_is_asked_for_and_embeds_every_chunk_again(project):
    root, endpoint = project
    semantic.refresh(root)
    endpoint["sent"].clear(), endpoint["asked_for"].clear()
    endpoint["models"]["nomic-embed-text:v1.5"] = OTHER
    _pin(root, "nomic-embed-text:v1.5", OTHER)
    assert semantic.refresh(root)["available"] is True
    assert sorted(endpoint["sent"]) == ["pear trees\n", "plum trees\n"]
    assert set(endpoint["asked_for"]) == {"nomic-embed-text:v1.5"}
    assert semantic.manifest(root)["embedder"] == {"model": "nomic-embed-text:v1.5", "revision": OTHER}
    answer = semantic.search(root, "where is the pear", refresh=False)
    assert answer["available"] is True and answer["hits"][0]["path"] == "open/pear.md"
    assert endpoint["asked_for"][-1] == "nomic-embed-text:v1.5"


# --- S2: unpinned or mismatched fails closed, named -----------------------------------------------------------------

def test_an_unpinned_model_embeds_nothing_and_compares_nothing(project):
    root, endpoint = project
    semantic.refresh(root)
    before = semantic.manifest(root)
    endpoint["sent"].clear()
    _pin(root, "nomic-embed-text", None)
    report = semantic.refresh(root)
    assert (report["available"], report["error"]) == (False, "MODEL_UNPINNED") and "MODEL_UNPINNED" in report["reason"]
    assert endpoint["sent"] == [] and semantic.manifest(root) == before
    answer = semantic.search(root, "pear", refresh=False)
    assert answer["available"] is False and answer["hits"] == [] and "MODEL_UNPINNED" in answer["reason"]
    assert endpoint["sent"] == []


def test_an_endpoint_off_the_pin_embeds_nothing(project):
    root, endpoint = project
    endpoint["models"][semantic.MODEL] = OTHER
    report = semantic.refresh(root)
    assert (report["available"], report["error"]) == (False, "MODEL_MISMATCH") and "MODEL_MISMATCH" in report["reason"]
    assert endpoint["sent"] == [] and semantic.manifest(root) is None


def test_vectors_of_another_pin_are_not_compared_until_rebuilt(project):
    root, endpoint = project
    semantic.refresh(root)
    endpoint["sent"].clear()
    _pin(root, revision=OTHER)  # configured, not yet rebuilt
    answer = semantic.search(root, "pear", refresh=False)
    assert answer["available"] is False and answer["hits"] == [] and answer["reason"].startswith("MODEL_MISMATCH")
    assert endpoint["sent"] == []  # the question was not embedded either
    _pin(root, "nomic-embed-text:v1.5", PINNED)
    assert "MODEL_MISMATCH" in semantic.search(root, "pear", refresh=False)["reason"]


def test_a_query_embedder_at_another_revision_gives_no_vector(project):
    root, endpoint = project
    semantic.refresh(root)
    endpoint["sent"].clear()
    endpoint["query"] = {semantic.MODEL: OTHER}
    answer = semantic.search(root, "pear", refresh=False)
    assert answer["available"] is False and answer["hits"] == [] and "MODEL_MISMATCH" in answer["reason"]
    assert endpoint["sent"] == []
    endpoint["query"] = {}  # the query embedder lists no revision at all: not confirmed, not compared
    assert "MODEL_MISMATCH" in semantic.search(root, "pear", refresh=False)["reason"]
    endpoint["query"] = {semantic.MODEL: PINNED}
    assert semantic.search(root, "pear", refresh=False)["available"] is True


def test_a_pinned_model_the_endpoint_does_not_list_is_named(project):
    root, endpoint = project
    endpoint["models"].clear()
    report = semantic.refresh(root)
    assert report["available"] is False and report["reason"] == semantic.NO_MODEL
    assert report["reason"].startswith("MODEL_NOT_LISTED") and semantic.MODEL in report["reason"]


# --- W2-L065: the cut ---------------------------------------------------------------------------------------------

def test_the_manifest_holds_the_cut_and_a_store_built_before_it_is_stale(project, tmp_path, monkeypatch):
    root, endpoint = project
    semantic.refresh(root)
    assert semantic.manifest(root)["embed_chars"] == 512 == semantic.EMBED_CHARS
    connection = sqlite3.connect(root / STORE_REL)
    connection.execute("DROP TABLE semantic_pin")  # the store as every store built before W2-32 is
    connection.commit()
    connection.close()
    assert semantic.manifest(root)["embed_chars"] is None
    assert semantic.search(root, "pear", refresh=False)["reason"] == "stale"
    endpoint["sent"].clear()
    monkeypatch.setenv("GOV_VECTOR_CACHE_DIR", str(tmp_path / "fresh-cache"))  # else W2-126's cache serves them
    assert semantic.refresh(root)["available"] is True
    assert sorted(endpoint["sent"]) == ["pear trees\n", "plum trees\n"]  # every chunk embedded again
    assert semantic.search(root, "pear", refresh=False)["available"] is True


# --- S3's held-out cases are never embedded ---------------------------------------------------------------------

def test_the_learning_loop_s_folder_is_never_embedded(project):
    root, endpoint = project
    _commit(root, {f"{learning.CASES_REL}/MQ-1.yaml": "question: pear?\n", "fixtures/other.md": "fig trees\n"})
    semantic.refresh(root)
    assert sorted(endpoint["sent"]) == ["fig trees\n", "pear trees\n", "plum trees\n"]
