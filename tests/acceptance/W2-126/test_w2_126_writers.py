"""KPI 3 (and F1, F3): concurrent rebuilds and searches share the cache without a corrupt entry, a lost write read as
a vector, or a lock held across an embedding request; an unreadable or locked cache is skipped, named, never a
failure."""

from __future__ import annotations

import fcntl
import os
import time

import pytest

import w2_126_support as S

WRITERS = 4
QUESTIONS = ("when are the quince trees pruned", "what does the beekeeper smoke")


def own_file(n):
    return {f"notes/own-{n}.md": f"# Own {n}\n\nTree {n} keeps ledger number {n * 7919} in the drawer.\n"}


def test_concurrent_rebuilds_and_searches_serve_only_right_vectors(box, stand_in, tmp_path):
    stand_in.delay_s = 0.05   # widens the overlap of the writers
    trees = [S.plant(tmp_path / f"tree-{n}", extra=own_file(n)) for n in range(WRITERS)]
    running = [box.start(tree, [S.refresh(), S.search(QUESTIONS[n % 2]), S.query(QUESTIONS[(n + 1) % 2])])
               for n, tree in enumerate(trees)]
    for process in running:
        built, searched, _ = box.finish(process)
        assert built["available"] and searched["available"], (built.get("reason"), searched.get("reason"))

    extra = {rel: text for n in range(WRITERS) for rel, text in own_file(n).items()}
    reference = S.plant(tmp_path / "reference", extra=extra)
    box.build(reference, box.env(cache_dir=tmp_path / "empty-cache"))
    returned = {question: {vector for text, vector, _ in stand_in.records if text.endswith(question)}
                for question in QUESTIONS}   # the stand-in is deterministic: one vector per question
    stand_in.reset()
    served = S.plant(tmp_path / "served", extra=extra)
    asked = box.run(served, [S.refresh(), *[S.query(question) for question in QUESTIONS]])
    assert stand_in.texts() == [], "texts every writer stored were sent again: a write was lost"
    assert S.store_vectors(served) == S.store_vectors(reference), "the cache served a wrong or corrupt vector"
    for question, answer in zip(QUESTIONS, asked[1:]):
        assert len(returned[question]) == 1, f"the set-up: {question!r} was not embedded by a writer"
        assert answer["vector"] == next(iter(returned[question])).hex(), f"a wrong vector for {question!r}"


def test_no_lock_is_held_across_an_embedding_request(box, stand_in, tmp_path):
    stand_in.hold = "HELD-OPEN-MARK"
    held = S.plant(tmp_path / "held", extra={"notes/held.md": "# Held\n\nHELD-OPEN-MARK is kept open.\n"})
    other = S.plant(tmp_path / "other", corpus={"notes/kiln.md": "# Kiln\n\nThe kiln is fired on Thursdays.\n"})
    first = box.start(held, [S.refresh()])
    try:
        assert stand_in.held.wait(timeout=120), "the held text never reached the embedder (the case's set-up)"
        began = time.monotonic()
        built, searched = box.run(other, [S.refresh(), S.search("when is the kiln fired")], timeout=90)
        assert first.poll() is None and not stand_in.released.is_set(), "the held request ended early"
        assert built["available"] and searched["available"], (built.get("reason"), searched.get("reason"))
        assert S.counts(built)["skipped"] is None and S.counts(searched)["skipped"] is None, \
            f"the cache was skipped while another process's request was open: {S.counts(built)}"
        assert time.monotonic() - began < 90
    finally:
        stand_in.release()
    box.finish(first)
    stand_in.reset()
    box.build(S.clone(other, tmp_path / "other-again"))
    assert stand_in.texts() == [], "what was stored while a request was open is not in the cache"


class Locked:
    """Holds every kind of whole-file lock on ``path`` (``flock`` and a POSIX record lock to the end of any
    file), so whatever lock the cache takes, it is taken already."""

    def __init__(self, path):
        self.handle = os.open(path, os.O_RDWR)
        fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.lockf(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB, 0, 0)

    def close(self):
        os.close(self.handle)


@pytest.mark.parametrize("state", ["unreadable", "locked", "garbage"])
def test_an_unusable_cache_is_skipped_and_named(box, stand_in, tmp_path, state):
    first = S.plant(tmp_path / "first")
    box.build(first)
    expected, sent = S.store_vectors(first), len(stand_in.texts())
    entry = S.cache_entry(box)
    lock = None
    if state == "unreadable":
        if os.geteuid() == 0:
            pytest.skip("root reads a file of mode 000")
        entry.chmod(0)
    elif state == "locked":
        lock = Locked(entry)
    else:
        entry.write_bytes(b"this is not a vector cache\n" * 200)
    try:
        stand_in.reset()
        second = S.clone(first, tmp_path / "second")
        built, searched = box.run(second, [S.refresh(), S.search("when does the beekeeper lift the frames")])
    finally:
        if lock:
            lock.close()
        if entry.exists():
            entry.chmod(0o600)
    assert built["available"] and searched["available"], (built.get("reason"), searched.get("reason"))
    assert len(stand_in.texts()) >= sent, "the texts were not embedded when the cache could not be used"
    assert S.store_vectors(second) == expected
    if state != "garbage":   # a garbage file may be replaced instead: the KPI names no choice
        for result in (built, searched):
            assert S.counts(result)["skipped"], f"the {state} cache was skipped unnamed: {S.counts(result)}"
