"""Builder tests for the semantic route (W1-19).

Regression evidence only (DEC-136). ``sqlite_vec`` and Ollama are absent on this machine (DEC-384), so the path
that stores and compares vectors is run here against stand-ins: ``_ready`` gives the connection a Python function
named ``vec_distance_cosine``, and ``_ask`` answers as the endpoint would. This shows the bookkeeping (which chunks
are embedded, the manifest, staleness), not the extension or the model. Every store is in a temporary git
repository (DEC-322), with the secret filter replaced, so no test needs gitleaks.
"""
from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import lexical, semantic  # noqa: E402

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
PATH_MAP = """namespaces:
  open: {paths: ['open/**'], embedding_policy: embedded}
  closed: {paths: ['closed/**'], embedding_policy: not embedded}
  odd: {paths: ['odd/**'], embedding_policy: embedded on request}
  bare: {paths: ['bare/**']}
  both: {paths: ['open/shared/**'], embedding_policy: not embedded}
"""
FILES = {".gitignore": ".gov-runtime/\n", "governance/project/path-map.yaml": PATH_MAP,
         "open/pear.md": "pear trees\n", "open/plum.md": "plum trees\n", "open/shared/fig.md": "fig trees\n",
         "closed/vault.md": "cobalt ledger\n", "odd/attic.md": "saffron register\n", "bare/cellar.md": "indigo roster\n",
         "elsewhere/none.md": "no namespace\n"}


def _commit(root, files):
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    for args in (["add", "-A"], ["commit", "-q", "-m", "a change"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env={**_ENV, "HOME": str(root)})


def _distance(left, right):
    count = len(left) // 4
    return sum(abs(a - b) for a, b in zip(struct.unpack(f"{count}f", left), struct.unpack(f"{count}f", right)))


@pytest.fixture()
def project(tmp_path, monkeypatch):
    """A repository with one file in each reading of ``embedding_policy``, and the endpoint's stand-in: the texts it
    was asked to embed, and the digest its model list reports."""
    endpoint = {"sent": [], "digest": "ac6da0dfba84" + "0" * 52}

    def ask(path, body=None):
        if path == "/api/tags":
            return {"models": [{"name": semantic.MODEL, "digest": endpoint["digest"]}]}
        endpoint["sent"] += body["input"]
        return {"embeddings": [[float("pear" in text), float("plum" in text)] for text in body["input"]]}

    def ready(connection):
        connection.create_function("vec_distance_cosine", 2, _distance)

    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "_ask", ask)
    monkeypatch.setattr(semantic, "_ready", ready)
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True, capture_output=True, env=_ENV)
    _commit(tmp_path, FILES)
    return tmp_path, endpoint


def test_only_a_file_whose_every_namespace_says_embedded_is_sent_and_found(project):
    root, endpoint = project
    assert semantic.refresh(root)["available"] is True
    assert sorted(endpoint["sent"]) == ["pear trees\n", "plum trees\n"]
    answer = semantic.search(root, "where is the pear", refresh=False)
    assert answer["available"] is True and [hit["path"] for hit in answer["hits"]] == ["open/pear.md", "open/plum.md"]
    assert endpoint["sent"][-1] == semantic.INSTRUCTION + "where is the pear"
    record = lexical.chunks(root, "open/pear.md")[0]
    assert {key: answer["hits"][0][key] for key in record} == record


def test_a_refresh_embeds_only_what_has_no_vector_and_drops_what_is_no_longer_embedded(project):
    root, endpoint = project
    semantic.refresh(root)
    del endpoint["sent"][:]
    _commit(root, {"open/quince.md": "quince trees\n",
                   "governance/project/path-map.yaml": PATH_MAP.replace("['open/**']", "['open/q*', 'open/pear.md']")})
    assert semantic.search(root, "pear", refresh=False)["reason"] == "stale"
    assert semantic.refresh(root)["available"] is True
    assert endpoint["sent"] == ["quince trees\n"]
    assert {hit["path"] for hit in semantic.search(root, "pear", refresh=False)["hits"]} == \
        {"open/pear.md", "open/quince.md"}


def test_the_manifest_follows_the_model_list_and_another_embedder_builds_the_vectors_again(project):
    root, endpoint = project
    assert semantic.manifest(root) is None
    semantic.refresh(root)
    assert semantic.manifest(root)["embedder"] == {"model": semantic.MODEL, "revision": endpoint["digest"]}
    endpoint["digest"] = "5e" + "1" * 62
    del endpoint["sent"][:]
    semantic.refresh(root)
    assert semantic.manifest(root)["embedder"]["revision"] == endpoint["digest"]
    assert sorted(endpoint["sent"]) == ["pear trees\n", "plum trees\n"]


def test_nothing_is_sent_or_stored_when_the_model_is_not_in_the_model_list(project):
    root, endpoint = project
    endpoint["digest"] = None
    report = semantic.refresh(root)
    assert (report["available"], report["state"], report["reason"]) == (False, "FACET_UNAVAILABLE", semantic.NO_MODEL)
    assert endpoint["sent"] == [] and semantic.manifest(root) is None
