"""W2-32 S10 (DEC-1065 (1), DEC-1031): no CPU fallback for embeddings. ``ensure_*`` check health only and start
nothing; only an explicit restart starts a server; a vector computed on the CPU is refused, never cached or stored;
a rebuild refuses to embed on the CPU. Regression evidence only (DEC-136): nothing is started (``subprocess.Popen``
is replaced by a recorder), and the endpoint is a stand-in.
"""
from __future__ import annotations

import sqlite3
import struct
import subprocess
import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.config import models  # noqa: E402
from gov.retrieval import lexical, ollama, semantic, vector_cache  # noqa: E402
from gov.store import STORE_REL  # noqa: E402

PINNED = models.DEFAULT_REVISION + "0" * 52
_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
FILES = {".gitignore": ".gov-runtime/\n",
         "governance/project/path-map.yaml": "namespaces:\n  open: {paths: ['open/**'], embedding_policy: embedded}\n",
         "open/pear.md": "pear trees\n", "open/plum.md": "plum trees\n"}


@pytest.fixture()
def no_start(monkeypatch, tmp_path):
    """Every ``Popen`` recorded, never run; an executable that would be found; nothing answers."""
    started = []
    recorder = types.SimpleNamespace(Popen=lambda *args, **kwargs: started.append(args), DEVNULL=subprocess.DEVNULL,
                                     SubprocessError=subprocess.SubprocessError)
    monkeypatch.setattr(ollama, "subprocess", recorder)  # ollama's own name only: git still runs
    monkeypatch.setattr(ollama, "_healthy", lambda url, deadline: False)
    binary = tmp_path / "ollama"
    binary.write_text("#!/bin/sh\n")
    binary.chmod(0o755)
    return started, {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path), "GOV_OLLAMA_BIN": str(binary)}


@pytest.mark.parametrize("check", [ollama.ensure_available, ollama.ensure_query_available])
def test_a_health_check_starts_nothing_and_names_the_embedder_unavailable(no_start, check, capsys):
    started, env = no_start
    result = check(timeout_s=0.2, env=env)
    assert started == [] and result["started"] is False and result["available"] is False
    assert ollama.UNAVAILABLE == "EMBEDDER_UNAVAILABLE" and result["state"] == "FACET_UNAVAILABLE"
    assert result["warning"].startswith("EMBEDDER_UNAVAILABLE") and "FTS-only" in result["warning"]
    assert capsys.readouterr().err.count(ollama.WARNING) == 1


@pytest.mark.parametrize("check", [ollama.ensure_available, ollama.ensure_query_available])
def test_an_answering_embedder_is_available_and_nothing_is_started(no_start, monkeypatch, check):
    started, env = no_start
    monkeypatch.setattr(ollama, "_healthy", lambda url, deadline: True)
    assert check(timeout_s=0.2, env=env)["available"] is True and started == []


@pytest.mark.parametrize("server", ["shared", "query"])
def test_only_an_explicit_restart_asks_for_a_start(monkeypatch, tmp_path, server):
    asked = []
    monkeypatch.setattr(ollama, "probe", lambda server, env=None: {"state": "down"})
    for name in ("ensure_available", "ensure_query_available"):
        monkeypatch.setattr(ollama, name, lambda name=name, **kwargs: asked.append((name, kwargs))
                            or {"available": False, "started": False, "state": "FACET_UNAVAILABLE"})
    ollama.safe_restart(server, env={"HOME": str(tmp_path), "PATH": "/usr/bin:/bin"})
    assert len(asked) == 1 and asked[0][1]["start"] is True


# --- the semantic route ---------------------------------------------------------------------------------------------

def _distance(left, right):
    count = len(left) // 4
    return sum(abs(a - b) for a, b in zip(struct.unpack(f"{count}f", left), struct.unpack(f"{count}f", right)))


@pytest.fixture()
def project(tmp_path, monkeypatch):
    """A repository; the endpoint's stand-in reports the model on the device ``endpoint[host]`` names."""
    endpoint = {"sent": [], "shared": "gpu", "query": "gpu"}
    monkeypatch.setenv(ollama.QUERY_HOST_SETTING, "query:1")
    monkeypatch.setenv("GOV_VECTOR_CACHE_DIR", str(tmp_path / "machine-cache"))

    def ask(path, body=None, host=None):
        device = endpoint["query" if host == "query:1" else "shared"]
        if path == "/api/tags":
            return {"models": [{"name": semantic.MODEL, "digest": PINNED}]}
        if path == "/api/ps":
            return {"models": [{"name": semantic.MODEL, "size": 4, "size_vram": 4 if device == "gpu" else 0}]}
        endpoint["sent"] += body["input"]
        return {"embeddings": [[float("pear" in text), float("plum" in text)] for text in body["input"]]}

    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "_ask", ask)
    monkeypatch.setattr(semantic, "_ready", lambda connection, ensure=None:
                        connection.create_function("vec_distance_cosine", 2, _distance))
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "-C", str(root), "init", "-q", "-b", "main"], check=True, capture_output=True, env=_ENV)
    for rel, text in FILES.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    for args in (["add", "-A"], ["commit", "-q", "-m", "c"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                       env={**_ENV, "HOME": str(root)})
    return root, endpoint


def _stored(root):
    connection = sqlite3.connect(root / STORE_REL)
    try:
        return connection.execute("SELECT count(*) FROM semantic_vector").fetchone()[0]
    finally:
        connection.close()


def test_a_rebuild_on_the_cpu_stores_and_caches_nothing_and_is_named(project):
    root, endpoint = project
    endpoint["shared"] = "cpu"
    report = semantic.refresh(root)
    assert (report["available"], report["error"]) == (False, "EMBEDDER_ON_CPU")
    assert report["reason"].startswith("EMBEDDER_ON_CPU")
    assert _stored(root) == 0
    texts = ["pear trees\n", "plum trees\n"]
    assert vector_cache.Cache(semantic.MODEL, PINNED).get(texts) == [None, None]  # nothing put in the cache
    assert semantic.search(root, "pear", refresh=False)["available"] is False
    endpoint["shared"] = "gpu"
    assert semantic.refresh(root)["available"] is True and _stored(root) == 2


def test_a_question_s_vector_from_the_cpu_is_refused_and_not_cached(project):
    root, endpoint = project
    assert semantic.refresh(root)["available"] is True
    endpoint["query"] = "cpu"
    answer = semantic.search(root, "where is the pear", refresh=False)
    assert answer["available"] is False and answer["hits"] == [] and answer["error"] == "EMBEDDER_ON_CPU"
    assert not (root / semantic.QUERY_VECTORS_REL).exists()
    assert vector_cache.Cache(semantic.MODEL, PINNED).get([semantic.INSTRUCTION + "where is the pear"]) == [None]
    endpoint["query"] = "gpu"
    assert semantic.search(root, "where is the pear", refresh=False)["hits"][0]["path"] == "open/pear.md"


def test_an_unreachable_query_embedder_is_named_and_nothing_is_started(project, no_start, monkeypatch):
    root, _ = project
    started, _ = no_start
    assert semantic.refresh(root)["available"] is True
    monkeypatch.setattr(semantic, "_ready", lambda connection, ensure=None: None if ensure is None or
                        ensure()["available"] else ollama.WARNING)  # the real health check, no extension needed
    answer = semantic.search(root, "pear", refresh=False)
    assert answer["available"] is False and answer["reason"].startswith("EMBEDDER_UNAVAILABLE")
    assert started == []


def test_the_gpu_is_the_only_device():
    assert semantic.DEVICES == ("gpu",)
