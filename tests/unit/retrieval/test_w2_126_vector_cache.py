"""Builder tests for the machine-wide vector cache (W2-126; DEC-1032, DEC-1039).

Regression evidence only (DEC-136). The endpoint is a stand-in (``_ask``) and ``sqlite_vec`` a Python function, as in
``tests/unit/semantic/test_semantic.py``; every cache sits in the test's own folder (``GOV_VECTOR_CACHE_DIR``), so no
test reads or writes the user's own cache.
"""
from __future__ import annotations

import multiprocessing
import os
import sqlite3
import stat
import struct
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import lexical, ollama, semantic, vector_cache  # noqa: E402
from gov.store import STORE_REL  # noqa: E402

DIGEST, OTHER = "ac6da0dfba84" + "0" * 52, "5e" + "1" * 62
_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
FILES = {".gitignore": ".gov-runtime/\n",
         "governance/project/path-map.yaml": "namespaces:\n  open: {paths: ['open/**'], embedding_policy: embedded}\n",
         **{f"open/note{n:02}.md": f"note number {n} about pears\n" for n in range(40)}}


def blob(*numbers) -> bytes:
    return struct.pack(f"{len(numbers)}f", *numbers)


@pytest.fixture(autouse=True)
def own_cache(tmp_path, monkeypatch):
    monkeypatch.setenv(vector_cache.DIR_SETTING, str(tmp_path / "cache"))
    monkeypatch.delenv(vector_cache.BOUND_SETTING, raising=False)
    return tmp_path / "cache" / vector_cache.FILE


def _repo(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "-C", str(root), "init", "-q", "-b", "main"], check=True, capture_output=True, env=_ENV)
    for rel, text in FILES.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    for args in (["add", "-A"], ["commit", "-q", "-m", "c"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env={**_ENV, "HOME": str(root)})
    return root


@pytest.fixture()
def endpoint(monkeypatch):
    """The stand-in endpoint: the texts sent, and the digest its model list reports."""
    state = {"sent": [], "digest": DIGEST}

    def ask(path, body=None, host=None):
        if path == "/api/tags":
            return {"models": [{"name": semantic.MODEL, "digest": state["digest"]}]}
        if path == "/api/ps":
            return {"models": [{"name": semantic.MODEL, "size": 1, "size_vram": 1}]}
        state["sent"] += body["input"]
        return {"embeddings": [[float(len(text)), float(sum(map(ord, text)) % 97), 0.25] for text in body["input"]]}

    def ready(connection, ensure=None):
        connection.create_function("vec_distance_cosine", 2, lambda a, b: float(a != b))

    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "_ask", ask)
    monkeypatch.setattr(semantic, "_ready", ready)
    monkeypatch.setenv(ollama.QUERY_HOST_SETTING, "127.0.0.1:1")
    return state


def _vectors(root: Path) -> list:
    with sqlite3.connect(root / STORE_REL) as connection:
        return connection.execute("SELECT chunk_id, embedding FROM semantic_vector ORDER BY chunk_id").fetchall()


def test_a_second_tree_sends_nothing_and_its_store_is_the_same(tmp_path, endpoint):
    first = semantic.refresh(_repo(tmp_path / "a"))
    assert first["available"] and first["vector_cache"] == {"hits": 0, "misses": 40, "skipped": None}
    assert len(endpoint["sent"]) == 40
    endpoint["sent"].clear()
    second = semantic.refresh(_repo(tmp_path / "b"))
    assert second["vector_cache"] == {"hits": 40, "misses": 0, "skipped": None} and endpoint["sent"] == []
    assert _vectors(tmp_path / "a") == _vectors(tmp_path / "b")


def test_an_all_cached_store_equals_one_built_without_the_cache(tmp_path, endpoint, monkeypatch):
    semantic.refresh(_repo(tmp_path / "warm"))
    semantic.refresh(_repo(tmp_path / "cached"))
    monkeypatch.setenv(vector_cache.DIR_SETTING, str(tmp_path / "fresh-cache"))
    semantic.refresh(_repo(tmp_path / "cold"))
    assert _vectors(tmp_path / "cached") == _vectors(tmp_path / "cold")


def test_a_revision_change_is_a_new_key_space(tmp_path, endpoint):
    semantic.refresh(_repo(tmp_path / "a"))
    endpoint["digest"], endpoint["sent"] = OTHER, []
    assert semantic.refresh(_repo(tmp_path / "b"))["vector_cache"]["hits"] == 0 and len(endpoint["sent"]) == 40


def test_a_question_is_embedded_once_across_trees_and_named_in_the_search(tmp_path, endpoint):
    a, b = _repo(tmp_path / "a"), _repo(tmp_path / "b")
    semantic.refresh(a)
    semantic.refresh(b)
    endpoint["sent"].clear()
    first = semantic.search(a, "where are the pears", refresh=False)
    assert first["available"] and first["vector_cache"] == {"hits": 0, "misses": 1, "skipped": None}
    assert endpoint["sent"] == [semantic.INSTRUCTION, semantic.INSTRUCTION + "where are the pears"]
    second = semantic.search(b, "where are the pears", refresh=False)
    assert second["vector_cache"] == {"hits": 1, "misses": 0, "skipped": None} and len(endpoint["sent"]) == 2
    assert first["hits"] == second["hits"]


def test_the_key_is_the_model_the_revision_and_the_exact_text(own_cache):
    cache = vector_cache.Cache("m", "r1")
    assert cache.get(["pear", "plum"]) == [None, None]
    cache.put(["pear", "plum"], [blob(1, 2), blob(3, 4)])
    assert vector_cache.Cache("m", "r1").get(["pear", "plum", "pear "]) == [blob(1, 2), blob(3, 4), None]
    assert vector_cache.Cache("m", "r2").get(["pear"]) == [None]
    assert vector_cache.Cache("n", "r1").get(["pear"]) == [None]
    no_key = vector_cache.Cache("m", None)
    assert no_key.get(["pear"]) == [None] and "no revision" in no_key.counts["skipped"]


def test_the_cache_is_one_file_of_mode_0600(own_cache):
    cache = vector_cache.Cache("m", "r")
    cache.get(["x"])
    cache.put(["x"], [blob(1)])
    assert vector_cache.Cache("m", "r").get(["x"]) == [blob(1)]
    assert [p.name for p in own_cache.parent.iterdir()] == [vector_cache.FILE]
    assert stat.S_IMODE(own_cache.stat().st_mode) == 0o600
    assert stat.S_IMODE(own_cache.parent.stat().st_mode) == 0o700


def test_the_default_place_is_the_users_cache_folder(tmp_path, monkeypatch):
    monkeypatch.delenv(vector_cache.DIR_SETTING)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "xdg"))
    assert vector_cache.location() == tmp_path / "xdg" / "gov-os" / "vector-cache" / vector_cache.FILE
    monkeypatch.delenv("XDG_CACHE_HOME")
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    assert vector_cache.location() == tmp_path / "home" / ".cache" / "gov-os" / "vector-cache" / vector_cache.FILE


def test_an_entry_whose_bytes_do_not_match_is_a_miss_and_is_replaced(own_cache):
    cache = vector_cache.Cache("m", "r")
    cache.get(["x"])
    cache.put(["x"], [blob(1, 2)])
    with sqlite3.connect(own_cache) as connection:
        connection.execute("UPDATE vector SET embedding = ?", (blob(1, 2)[:-1],))
    cache = vector_cache.Cache("m", "r")
    assert cache.get(["x"]) == [None] and cache.counts == {"hits": 0, "misses": 1, "skipped": None}
    cache.put(["x"], [blob(1, 2)])
    assert vector_cache.Cache("m", "r").get(["x"]) == [blob(1, 2)]


@pytest.mark.parametrize("how", ["garbage", "unreadable", "a folder"])
def test_an_unusable_cache_is_skipped_and_named_never_a_failure(tmp_path, endpoint, own_cache, how):
    own_cache.parent.mkdir(parents=True)
    if how == "a folder":
        own_cache.mkdir()
    else:
        own_cache.write_bytes(os.urandom(8192))
        if how == "unreadable":
            own_cache.chmod(0)
    if how == "unreadable" and os.access(own_cache, os.R_OK):
        pytest.skip("the file stays readable to this user")
    report = semantic.refresh(_repo(tmp_path / "a"))
    counts = report["vector_cache"]
    assert report["available"] and (counts["hits"], counts["misses"]) == (0, 40) and len(endpoint["sent"]) == 40
    assert str(own_cache) in counts["skipped"] and "could not be read" in counts["skipped"]


def test_a_locked_cache_is_skipped_quickly_for_the_rest_of_the_run(tmp_path, endpoint, own_cache, monkeypatch):
    monkeypatch.setattr(vector_cache, "BUSY_S", 0.2)
    vector_cache.Cache("m", "r").get(["x"])
    holder = sqlite3.connect(own_cache, isolation_level=None)
    holder.execute("PRAGMA locking_mode = EXCLUSIVE")
    holder.execute("BEGIN EXCLUSIVE")
    try:
        started = time.monotonic()
        report = semantic.refresh(_repo(tmp_path / "a"))
        assert time.monotonic() - started < 10
    finally:
        holder.execute("ROLLBACK")
        holder.close()
    counts = report["vector_cache"]
    assert report["available"] and counts["misses"] == 40 and len(endpoint["sent"]) == 40
    assert "locked" in counts["skipped"]


def test_the_bound_evicts_the_least_recently_used_first(own_cache, monkeypatch):
    big = blob(*[0.5] * 1024)
    cache = vector_cache.Cache("m", "r")
    texts = [f"t{n}" for n in range(30)]
    cache.get(texts)
    cache.put(texts, [big] * 30)
    full = own_cache.stat().st_size
    monkeypatch.setenv(vector_cache.BOUND_SETTING, str(full))
    vector_cache.Cache("m", "r").get(["t0"])  # t0 used again: t1 is now the least recently used
    more = [f"u{n}" for n in range(5)]
    cache = vector_cache.Cache("m", "r")
    cache.get(more)
    cache.put(more, [big] * 5)
    with sqlite3.connect(own_cache) as connection:
        size = connection.execute("PRAGMA page_count").fetchone()[0] * connection.execute(
            "PRAGMA page_size").fetchone()[0]
    assert size <= full
    found = vector_cache.Cache("m", "r").get(["t0", "t1", *more])
    assert found[0] == big and found[1] is None and found[2:] == [big] * 5


def _writer(folder: str, n: int) -> None:
    os.environ[vector_cache.DIR_SETTING] = folder
    for round_ in range(20):
        texts = [f"text {k}" for k in range(round_ * 5, round_ * 5 + 10)]
        cache = vector_cache.Cache("m", "r")
        found = cache.get(texts)
        for text, vector in zip(texts, found):
            assert vector is None or vector == blob(float(len(text)), float(text.split()[1]))
        misses = [t for t, v in zip(texts, found) if v is None]
        cache.put(misses, [blob(float(len(t)), float(t.split()[1])) for t in misses])


def test_concurrent_writers_never_corrupt_or_serve_a_wrong_vector(own_cache):
    context = multiprocessing.get_context("spawn")
    workers = [context.Process(target=_writer, args=(str(own_cache.parent), n)) for n in range(6)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(120)
    assert [worker.exitcode for worker in workers] == [0] * 6
    with sqlite3.connect(own_cache) as connection:
        assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)
    texts = [f"text {k}" for k in range(105)]
    assert vector_cache.Cache("m", "r").get(texts) == [blob(float(len(t)), float(t.split()[1])) for t in texts]
