"""B4 OI-5 (routed to I1/BR-AR-0009): ``embed_and_store`` now commits PER BATCH, not once at the end, so a killed
rebuild resumes instead of losing everything since the last full commit. This proves the resumed result is
byte-identical to an uninterrupted build: killing after the first batch, resuming with a second call over the
FULL row set (which is exactly what a real restart does -- the same ``_eligible_chunk_rows`` query, re-run), must
give the same final vector-table digest as one uninterrupted call over the full set on a fresh store.

New test file (tests/semantic/test_vectors.py, the existing one, is unmodified)."""
import sqlite3

from govbridge.semantic import vectors


def _fake_embed_factory(calls):
    def fake_embed(texts, mode="passage", dimensions=None, pin_id=None, **kw):
        calls.append(list(texts))
        # a small, deterministic function of the text itself, so distinct texts get distinct (but reproducible)
        # vectors -- good enough to prove commit/resume identity without a real model
        return {"vectors": [[float(len(t) % 7), float(sum(map(ord, t)) % 11)] for t in texts], "dim": 2}
    return fake_embed


class FakePin:
    dimensions = 2


def _rows(n: int) -> list:
    return [(f"c{i}", f"sha{i}", f"chunk text number {i}") for i in range(n)]


class _CountingConnection(sqlite3.Connection):
    """A plain sqlite3.Connection subclass that counts real commits -- sqlite3.Connection does not allow
    monkeypatching ``commit`` on an instance directly (it is a read-only slot), so a subclass is the clean way to
    observe commit boundaries without changing what a commit actually does."""
    commits = 0

    def commit(self):
        self.__class__.commits += 1
        super().commit()


def test_commit_happens_after_every_batch_not_only_at_the_end(monkeypatch):
    """A batch boundary is a real, observable commit point: one commit for the reuse pass, plus one per embedding
    batch -- never a single commit only at the very end (B4 OI-5)."""
    calls = []
    monkeypatch.setattr("govbridge.semantic.vectors.runner.embed", _fake_embed_factory(calls))

    conn = sqlite3.connect(":memory:", factory=_CountingConnection)
    vectors.create_table(conn)
    rows = _rows(6)  # 6 distinct texts

    _CountingConnection.commits = 0
    # batch_texts=2 -> 3 batches of 2 unique texts each (every row here has a unique text_sha256)
    vectors.embed_and_store(conn, rows, FakePin(), "pinA", batch_texts=2)
    # one commit after the reuse pass, plus one per batch (3 batches of 2) = 4
    assert conn.commits == 4
    assert vectors.count_for_pin(conn, "pinA") == 6


def test_resumed_build_equals_uninterrupted_build(monkeypatch):
    """Kill after the first batch (only some rows committed); resume with a second, independent call over the
    FULL row set on the SAME store (exactly what a real restart does). The result must equal one uninterrupted
    call over the full set on a fresh store -- same digest, same row count, no duplicate model calls for the
    already-committed rows."""
    rows = _rows(9)

    # --- uninterrupted reference build, on a fresh store ---------------------------------------------------
    calls_uninterrupted = []
    monkeypatch.setattr("govbridge.semantic.vectors.runner.embed", _fake_embed_factory(calls_uninterrupted))
    conn_ref = sqlite3.connect(":memory:")
    vectors.create_table(conn_ref)
    stats_ref = vectors.embed_and_store(conn_ref, rows, FakePin(), "pinA", batch_texts=3)
    digest_ref = vectors.digest_for_pin(conn_ref, "pinA")
    assert stats_ref["chunks_embedded"] == 9
    assert len(calls_uninterrupted) == 3  # 9 rows / batch_texts=3 -> 3 model calls

    # --- interrupted-then-resumed build, on its own store --------------------------------------------------
    calls_resumed = []
    monkeypatch.setattr("govbridge.semantic.vectors.runner.embed", _fake_embed_factory(calls_resumed))
    conn_live = sqlite3.connect(":memory:")
    vectors.create_table(conn_live)

    # "killed" after only the first batch: call embed_and_store on a PREFIX of the rows only
    vectors.embed_and_store(conn_live, rows[:3], FakePin(), "pinA", batch_texts=3)
    assert vectors.count_for_pin(conn_live, "pinA") == 3
    assert len(calls_resumed) == 1

    # "resume": a real restart re-runs the SAME eligible-rows query, i.e. the full set again
    stats_resumed = vectors.embed_and_store(conn_live, rows, FakePin(), "pinA", batch_texts=3)
    digest_resumed = vectors.digest_for_pin(conn_live, "pinA")

    assert digest_resumed == digest_ref
    assert vectors.count_for_pin(conn_live, "pinA") == 9
    # the first 3 (already committed before the "kill") were reused on resume, never re-embedded
    assert stats_resumed["chunks_reused"] == 3
    assert stats_resumed["chunks_embedded"] == 6
    # total real model calls across the whole kill+resume sequence: 1 (pre-kill) + 2 (resume's remaining batches)
    assert len(calls_resumed) == 1 + 2
