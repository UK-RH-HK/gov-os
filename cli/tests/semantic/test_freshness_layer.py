"""End-to-end: govbridge.core.freshness rebuild, with the "semantic" layer builder registered
(import govbridge.semantic), against a real (if tiny) Git fixture repo and the REAL, committed
config/embed-profile.yaml + config/model-pin.yaml + the real ONNX adapter. This is the in-worktree analogue of
this node's acceptance check 3 (`$PY -m govbridge.core.freshness rebuild --layer semantic`), run here on a
hermetic fixture instead of the full corpus so it stays fast.

NOTE on process-global registration: govbridge.core.freshness/manifest's register_* calls are process-global
(Python module state), by the design their own docstrings describe for B2-B5. Importing govbridge.semantic here
means a BARE freshness.run() (no --layer) in this same pytest process now also runs the "semantic" builder --
this file always uses a bare call deliberately (see the module-level comment above _run_full_build) so the
"semantic" builder has real core-built chunk data to embed. This is flagged as an open issue in this run's typed
report: govbridge.core.freshness has no per-run isolation of the layer registry, so running tests/core and
tests/semantic together in ONE pytest session pulls "semantic" into tests/core's own bare freshness.run() calls
too. It does not appear to break any of tests/core's assertions (they use loose bounds, not exact chunk counts,
around any bare rebuild), but this node's own acceptance command runs tests/semantic in isolation
(`pytest tests/semantic -q`), which never collects tests/core in the same process.
"""
from govbridge.core import freshness, telemetry
from govbridge.semantic import vectors

# `built` is defined in tests/semantic/conftest.py so test_search.py can share it.


def test_vector_status_built_and_rows_recorded_in_manifest(built):
    _result, conn, pin_id = built
    assert vectors.count_for_pin(conn, pin_id) > 0

    manifest = freshness.load_previous_manifest()["manifest"]
    vlayer = manifest["layers"]["vector"]
    assert vlayer["status"] == "BUILT"
    assert vlayer["rows"] == vectors.count_for_pin(conn, pin_id)
    assert vlayer["digest"] == vectors.digest_for_pin(conn, pin_id)
    assert vlayer["pin_id"] == pin_id
    assert vlayer["semantic_block"]["model"]["id"] == "BAAI/bge-small-en-v1.5"


def test_no_chunk_of_an_l_machine_output_kind_is_embedded(built):
    _result, conn, _pin_id = built
    machine_blobs = conn.execute("SELECT blob_id FROM blob WHERE corpus_rule='L-MACHINE-OUTPUT'").fetchall()
    assert machine_blobs, "fixture must actually contain an L-MACHINE-OUTPUT blob (logs/build.out)"
    for (blob_id,) in machine_blobs:
        chunk_ids = [r[0] for r in conn.execute("SELECT chunk_id FROM chunk WHERE blob_id=?", (blob_id,))]
        assert chunk_ids
        for cid in chunk_ids:
            assert conn.execute("SELECT 1 FROM vector WHERE chunk_id=?", (cid,)).fetchone() is None


def test_a_history_only_blob_is_never_embedded(built):
    _result, conn, _pin_id = built
    history_only = conn.execute(
        """
        SELECT DISTINCT blob_id FROM occurrence
        WHERE ref_name LIKE 'refs/heads/history/%'
          AND blob_id NOT IN (SELECT blob_id FROM occurrence WHERE ref_name NOT LIKE 'refs/heads/history/%')
        """
    ).fetchall()
    assert history_only, "the fixture's history branches must diverge (repobuilder writes distinct NOTES.md text)"
    for (blob_id,) in history_only:
        chunk_ids = [r[0] for r in conn.execute("SELECT chunk_id FROM chunk WHERE blob_id=?", (blob_id,))]
        for cid in chunk_ids:
            assert conn.execute("SELECT 1 FROM vector WHERE chunk_id=?", (cid,)).fetchone() is None


def test_an_admitted_kind_in_an_eligible_ref_is_embedded(built):
    _result, conn, _pin_id = built
    row = conn.execute(
        "SELECT blob_id FROM occurrence WHERE path='docs/NOTES.md' AND ref_name='records'"
    ).fetchone()
    assert row is not None
    (blob_id,) = row
    chunk_ids = [r[0] for r in conn.execute("SELECT chunk_id FROM chunk WHERE blob_id=?", (blob_id,))]
    assert chunk_ids
    for cid in chunk_ids:
        assert conn.execute("SELECT 1 FROM vector WHERE chunk_id=?", (cid,)).fetchone() is not None


def test_throughput_and_seconds_recorded_in_the_build_telemetry_row(built):
    rows = telemetry.read_rows("builds")
    semantic_rows = [r for r in rows if r.get("layer") == "semantic"]
    assert semantic_rows
    row = semantic_rows[-1]
    assert row["wall_seconds"] >= 0
    assert "throughput_chunks_per_s" in row
    assert row["llm_invocations"] == 0
