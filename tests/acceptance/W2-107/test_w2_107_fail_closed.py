"""W2-107: a cache that cannot be used is a miss: every text is scanned, the verdicts are right, nothing raises or hangs.

KPI success 4 (a cache that cannot be opened, is corrupt, has the wrong form or is locked counts as a miss; a write that
fails is ignored); failure 3 (a corrupt, missing or locked cache that stops a rebuild or answers clean). Each pass is a
process of its own (as a rebuild is), stopped as hanging after ``support.CHILD_TIMEOUT_S``. ``full`` is what the pass
costs with no cache; ``findings`` what its texts that hold a secret cost, the rest being answered from a cache that works.
"""

from __future__ import annotations

import os
import sqlite3

import pytest

import w2_107_support as support
from gov import secrets

pytestmark = support.needs_tools

FILES = {
    "docs/alpha.md": "W2-107: the alpha page, ordinary text.\n",
    "docs/beta.md": "W2-107: the beta page, ordinary text.\n",
}
LOCKED_EXTRA_S = 120  # how much longer than a pass without a cache a pass may take while the cache is held locked


@pytest.fixture()
def scene(project, engine):
    """Two clean files and one holding the secret; one clean name and one holding it; the costs of a pass."""
    rels = support.put(project, FILES)
    secret = support.put(project, {"docs/planted.md": f"The value is {support.planted()} today.\n"})
    names = ["docs/an-ordinary-name.md", f"docs/{support.planted()}/page.md"]
    off = support.child_env(engine, "")
    run, full = support.counted(engine, lambda: support.run_child(project, rels + secret, names, off))
    assert run.error is None and run.indexable == rels and run.names == [False, True], "premise: the verdicts"
    assert run.gov == secrets.__file__, "the child runs the same gov as this run (DEC-732)"
    findings = support.counted(engine, lambda: support.run_child(project, secret, names[1:], off))[1]
    assert 1 <= findings < full, "premise: the texts holding the secret cost less than the whole pass"
    return {"root": project, "paths": rels + secret, "names": names, "kept": rels, "full": full,
            "findings": findings, "seconds": run.seconds}


def judge(scene, engine, cache, label):
    """One pass in a child process: the verdicts are right and nothing raised; returns (scan calls, seconds)."""
    env = support.child_env(engine, cache)
    run, calls = support.counted(engine, lambda: support.run_child(scene["root"], scene["paths"], scene["names"], env))
    assert run.error is None, f"{label}: the filter raised {run.error} for a cache it cannot use"
    assert run.indexable == scene["kept"] and run.names == [False, True], f"{label}: the verdicts are right"
    return calls, run.seconds


def a_working_cache_answers(scene, engine, cache, label):
    """With the damage gone, the cache works: a first pass scans every text and the next is answered from it."""
    assert judge(scene, engine, cache, f"{label}, first pass")[0] == scene["full"]
    assert judge(scene, engine, cache, f"{label}, second pass")[0] == scene["findings"], \
        f"{label}: a cache that works answers the clean texts"


def test_a_cache_file_of_garbage_bytes_is_a_miss_until_removed_and_is_never_replaced(scene, engine, cache):
    garbage = b"W2-107: this is no database.\n" * 64 + bytes(range(256)) * 16
    cache.write_bytes(garbage)
    for number in range(2):
        assert judge(scene, engine, cache, f"garbage, pass {number + 1}")[0] == scene["full"], "every text is scanned"
    assert cache.read_bytes() == garbage, "the filter never replaces the damaged file"
    cache.unlink()
    a_working_cache_answers(scene, engine, cache, "the garbage removed")


def test_an_empty_cache_file_neither_stops_the_scan_nor_answers_wrong(scene, engine, cache):
    """Whether an empty file then becomes a cache is left open (package P-W2-107-TD-1): both passes must be right."""
    cache.write_bytes(b"")
    inode = cache.stat().st_ino
    assert judge(scene, engine, cache, "empty, pass 1")[0] == scene["full"], "every text is scanned"
    judge(scene, engine, cache, "empty, pass 2")
    assert cache.exists() and cache.stat().st_ino == inode, "the filter never deletes or replaces the file"


def test_a_sqlite_file_of_another_form_is_a_miss_until_removed_and_is_never_replaced(scene, engine, cache):
    foreign = sqlite3.connect(cache)
    try:
        foreign.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)")
        foreign.execute("INSERT INTO notes (body) VALUES ('W2-107: another program owns this file')")
        foreign.commit()
    finally:
        foreign.close()
    for number in range(2):
        assert judge(scene, engine, cache, f"another form, pass {number + 1}")[0] == scene["full"], \
            "every text is scanned"
    foreign = sqlite3.connect(f"file:{cache}?mode=ro", uri=True)
    try:
        assert foreign.execute("SELECT body FROM notes").fetchall() == [("W2-107: another program owns this file",)], \
            "the other program's file is kept as it was"
    finally:
        foreign.close()
    cache.unlink()
    a_working_cache_answers(scene, engine, cache, "the file of another form removed")


def test_a_cache_held_locked_by_another_connection_is_a_miss_after_a_short_wait(scene, engine, cache):
    a_working_cache_answers(scene, engine, cache, "before the lock")
    holder = sqlite3.connect(cache, isolation_level=None)
    try:
        holder.execute("PRAGMA locking_mode=EXCLUSIVE")
        holder.execute("BEGIN EXCLUSIVE")
        holder.execute("CREATE TABLE w2_107_lock_holder (x)")  # a write: the lock is now held against every reader
        calls, seconds = judge(scene, engine, cache, "locked")
        assert calls == scene["full"], "every text is scanned while the cache is locked"
        assert seconds <= scene["seconds"] + LOCKED_EXTRA_S, "the lock is waited out only a short while"
    finally:
        holder.execute("ROLLBACK")
        holder.close()
    assert judge(scene, engine, cache, "the lock released")[0] == scene["findings"], \
        "after the lock, the cache still answers what it held"


def test_a_cache_place_that_cannot_be_written_is_a_miss_and_nothing_is_made(scene, engine, tmp_path):
    folder = tmp_path / "read-only"
    folder.mkdir()
    cache = folder / support.CACHE_NAME
    folder.chmod(0o555)
    try:
        if os.access(folder, os.W_OK):
            pytest.skip("this user writes in a folder of mode 555 (root): the case cannot be built")
        for number in range(2):
            assert judge(scene, engine, cache, f"read-only, pass {number + 1}")[0] == scene["full"], \
                "every text is scanned"
        assert list(folder.iterdir()) == [], "nothing is made in a place that cannot be written"
    finally:
        folder.chmod(0o755)
