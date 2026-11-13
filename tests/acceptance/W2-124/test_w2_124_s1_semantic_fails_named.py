"""S1 (and the CLI side of F1): ``gov rebuild`` fails named when the semantic store was asked for and not recreated.

Ticket KPI S1: ``gov rebuild`` exits non-zero, named (``REBUILD_FAILED``, ``store: semantic``), when the semantic store was
asked for and not recreated (the embedder unavailable, hung or failing part way); only ``--no-embeddings`` skips it;
never an ok answer over a partial store.

The embedder is a stand-in on a loopback port (nothing real is started): unavailable = a port nothing listens on; failing
part way = answers the first embed request, then HTTP 400 (not transient: no retry wait is spent); hung = accepts and
never answers. The hung case and the HTTP 500 case run ``gov.rebuild.command.run`` in-process, with the endpoint timeout
and the retry waits patched short (the real timeout is 120 s, the waits 10 s and 30 s): the timeout is the seam.
"""

from __future__ import annotations

import argparse
import time

import pytest

import w2_124_support as support

PLANT = {"files": 40}   # 40 notes: more than one batch of 32, so a stand-in can fail part way


# ---- the unavailable embedder ---------------------------------------------------------------------------------------

def test_s1_unavailable_embedder_json_exits_1_named_semantic(runs):
    run, _, project = runs.rebuild("s1-unavailable-json", embedder="dead", project_options=PLANT)
    support.assert_named_failure(run, "embedder unavailable")
    assert not (project / support.RECORD_REL).exists(), \
        f"a failed rebuild left a warm-base record at {support.RECORD_REL}\n{run.describe()}"


def test_s1_unavailable_embedder_human_output_names_the_failure(runs):
    run, _, _ = runs.rebuild("s1-unavailable-human", embedder="dead", project_options=PLANT, args=())
    assert run.returncode == 1, f"expected exit code 1, got {run.returncode}\n{run.describe()}"
    assert "gov rebuild: REBUILD_FAILED:" in run.stderr, f"stderr has no 'gov rebuild: REBUILD_FAILED:' line\n{run.describe()}"
    assert "store: semantic" in run.stderr, f"stderr does not hold the literal 'store: semantic'\n{run.describe()}"
    failing = [line for line in run.stderr.splitlines() if "REBUILD_FAILED" in line][0]
    assert "unavailable" in failing.lower() or "EMBEDDER" in failing, \
        f"the failure line does not give the reason (the embedder unavailable): {failing!r}"


# ---- failing part way -----------------------------------------------------------------------------------------------

def test_s1_embedder_failing_part_way_json_exits_1_named_semantic(runs):
    run, asked, project = runs.rebuild("s1-part-way-json", embedder=("part-way", ), project_options=PLANT)
    assert asked is not None and asked > 1, \
        f"the stand-in was asked {asked} embed request(s): the case needs more than one, so that it fails part way"
    support.assert_named_failure(run, "embedder failing part way")
    assert not (project / support.RECORD_REL).exists(), \
        f"a failed rebuild left a warm-base record at {support.RECORD_REL}\n{run.describe()}"


# ---- the hung embedder and the transient failure (in-process, the timeout and waits patched short) -----------------

def _in_process_rebuild(box, project, host, monkeypatch):
    """``gov.rebuild.command.run`` on ``project`` as the close calls it; the endpoint timeout and retry waits short."""
    from gov.config.loader import load_config
    from gov.rebuild import command
    import gov.retrieval.semantic as semantic

    for name, value in support.environment(box, host).items():
        monkeypatch.setenv(name, value)
    monkeypatch.chdir(project)
    monkeypatch.setattr(semantic, "TIMEOUT_S", 1.0)
    monkeypatch.setattr(semantic, "RETRY_WAITS_S", (0.0, 0.0))
    began = time.monotonic()
    try:
        done = command.run(project, argparse.Namespace(no_embeddings=False), load_config(project))
    except Exception as error:   # noqa: BLE001 - the case reads the error's code and details
        return None, error, time.monotonic() - began
    return done, None, time.monotonic() - began


@pytest.mark.parametrize("mode", ["hung", "part-way-500"])
def test_s1_hung_or_transient_failing_embedder_raises_rebuild_failed_semantic(box, monkeypatch, mode):
    stand_in = support.Embedder(mode, good=1)
    try:
        project = support.plant(box, "project", **PLANT)
        done, error, seconds = _in_process_rebuild(box, project, stand_in.host, monkeypatch)
    finally:
        stand_in.close()
    assert error is not None, \
        f"{mode}: the rebuild returned instead of failing; semantic = {((done or {}).get('stores') or {}).get('semantic')}"
    assert getattr(error, "code", None) == "REBUILD_FAILED", f"{mode}: expected GovError REBUILD_FAILED, got {error!r}"
    details = getattr(error, "details", {}) or {}
    assert details.get("store") == "semantic", f"{mode}: details.store is {details.get('store')!r}"
    assert isinstance(details.get("reason"), str) and details["reason"].strip(), f"{mode}: details.reason is empty"
    assert isinstance(details.get("stores"), dict) and "lexical" in details["stores"], \
        f"{mode}: details.stores is {details.get('stores')!r}"
    assert getattr(error, "exit_code", 1) == 1
    assert "store: semantic" in str(error), f"{mode}: the message does not hold 'store: semantic': {error!s}"
    assert seconds < 60, f"{mode}: the rebuild took {seconds:.0f} s: it waited out a real endpoint timeout"
    assert stand_in.asked >= 1, f"{mode}: the stand-in was never asked to embed"
    assert not (project / support.RECORD_REL).exists(), f"{mode}: a failed rebuild left a warm-base record"


# ---- only --no-embeddings skips it -----------------------------------------------------------------------------------

def test_s1_no_embeddings_exits_0_with_the_embedder_unavailable(runs):
    run, _, _ = runs.rebuild("s1-no-embeddings", embedder="dead", project_options=PLANT,
                             args=("--json", "--no-embeddings"))
    assert run.prints_ok, f"--no-embeddings did not print ok\n{run.describe()}"
    semantic = support.semantic_status(run.result)
    assert semantic.get("status") == "not_recreated" and semantic.get("requested") is False, \
        f"stores.semantic is not {{not_recreated, requested: false}}: {semantic}"
    assert "REBUILD_FAILED" not in run.stdout + run.stderr


def test_s1_a_healthy_embedder_recreates_the_semantic_store_and_prints_ok(runs):
    run, asked, project = runs.rebuild("s1-healthy", embedder="healthy", project_options=PLANT)
    assert run.prints_ok, f"the control rebuild (a healthy embedder) did not print ok\n{run.describe()}"
    assert support.semantic_status(run.result).get("status") == "recreated", \
        f"semantic is not recreated with a healthy embedder: {support.semantic_status(run.result)}"
    assert asked and asked >= 1
    assert (project / support.RECORD_REL).is_file(), f"a full ok rebuild wrote no warm-base record at {support.RECORD_REL}"
