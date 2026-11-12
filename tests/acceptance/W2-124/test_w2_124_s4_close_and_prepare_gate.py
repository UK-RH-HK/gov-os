"""S4 (and the gate side of F1): the close and the merge queue's prepare treat a rebuild without its semantic store as failed.

Ticket KPI S4: a planted rebuild result with no semantic store: the close's rebuild check and the merge queue's prepare each
report failed, and the CTO's ``rebuild_slot.sh`` on the same planted result exits 75.

Interface: ``gov.close.rebuild_gate.semantic_failure(result) -> str | None`` (a ``gov rebuild --json`` envelope or its
result; the reason a semantic store that was asked for is not recreated, else None) and ``check(result) -> None`` (raises
``REBUILD_FAILED``, details ``{store: "semantic", reason, stores}``). "The close's rebuild check" is that module; "the merge
queue's prepare" is ``gov rebuild --json`` failing through ``check()`` (S1's cases) and, for the planted result itself,
``rebuild_slot.sh`` with ``GOV_REBUILD_PYTHON`` at a stand-in that prints the planted envelope.
"""

from __future__ import annotations

import importlib
import json
import os
import stat
import subprocess
from pathlib import Path

import pytest

import w2_124_support as support

TOOLS = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools")
REASON = "EMBEDDER_UNAVAILABLE: Ollama is unavailable: semantic retrieval is skipped and results are FTS-only."

# planted results whose semantic store was asked for (no ``requested: false``) and is not recreated
PARTIAL = {
    "not_recreated with a reason": support.planted_result(support.semantic_result(reason=REASON)),
    "not_recreated, requested: true": support.planted_result(
        support.semantic_result(requested=True, reason="Ollama did not embed with qwen3-embedding:0.6b")),
    "no semantic store at all": support.planted_result("absent"),
}
# planted results that are not a failure
WHOLE = {
    "recreated": support.planted_result({"status": "recreated"}),
    "skipped by --no-embeddings": support.planted_result(support.semantic_result(
        requested=False, reason="--no-embeddings was given: the semantic vectors were not asked for")),
}


def _gate():
    try:
        return importlib.import_module("gov.close.rebuild_gate")
    except ModuleNotFoundError as error:
        pytest.fail(f"gov.close.rebuild_gate (the ticket's Interface) cannot be imported: {error}")


@pytest.mark.parametrize("name", sorted(PARTIAL))
@pytest.mark.parametrize("shape", ["result", "envelope"])
def test_s4_the_close_check_reports_a_partial_store_failed(name, shape):
    gate = _gate()
    result = PARTIAL[name]
    given = result if shape == "result" else support.envelope_of(result)
    reason = gate.semantic_failure(given)
    assert isinstance(reason, str) and reason.strip(), f"{name} ({shape}): semantic_failure returned {reason!r}"
    planted_reason = (result["stores"].get("semantic") or {}).get("reason")
    if planted_reason:
        assert planted_reason in reason, f"{name} ({shape}): the reason {reason!r} does not carry {planted_reason!r}"


@pytest.mark.parametrize("name", sorted(PARTIAL))
@pytest.mark.parametrize("shape", ["result", "envelope"])
def test_s4_check_raises_rebuild_failed_naming_the_semantic_store(name, shape):
    gate = _gate()
    from gov.cli.errors import GovError

    result = PARTIAL[name]
    with pytest.raises(GovError) as caught:
        gate.check(result if shape == "result" else support.envelope_of(result))
    error = caught.value
    assert error.code == "REBUILD_FAILED", f"{name} ({shape}): code {error.code}"
    assert error.details.get("store") == "semantic", f"{name} ({shape}): details {error.details}"
    assert isinstance(error.details.get("reason"), str) and error.details["reason"].strip()
    assert isinstance(error.details.get("stores"), dict) and "lexical" in error.details["stores"], \
        f"{name} ({shape}): details.stores is {error.details.get('stores')!r}"
    assert "store: semantic" in str(error), f"{name} ({shape}): the message lacks 'store: semantic': {error!s}"
    assert error.exit_code == 1


@pytest.mark.parametrize("name", sorted(WHOLE))
def test_s4_a_store_recreated_or_not_asked_for_passes_the_check(name):
    gate = _gate()
    assert gate.semantic_failure(WHOLE[name]) is None, f"{name}: semantic_failure named a failure"
    assert gate.semantic_failure(support.envelope_of(WHOLE[name])) is None
    assert gate.check(WHOLE[name]) is None, f"{name}: check did not return None"


def _planted_slot(tmp_path, result):
    """A planted tree, an envelope file and a stand-in for ``python3`` that prints it and exits 0."""
    tree = tmp_path / "tree"
    tree.mkdir()
    envelope = tmp_path / "envelope.json"
    envelope.write_text(json.dumps(support.envelope_of(result)), encoding="utf-8")
    stand_in = tmp_path / "planted-python"
    stand_in.write_text(f'#!/bin/sh\ncat "{envelope}"\nexit 0\n', encoding="utf-8")
    stand_in.chmod(stand_in.stat().st_mode | stat.S_IXUSR)
    return tree, stand_in


def _slot(tmp_path, result):
    if not (TOOLS / "rebuild_slot.sh").is_file():
        pytest.skip(f"{TOOLS}/rebuild_slot.sh is absent on this machine")
    tree, stand_in = _planted_slot(tmp_path, result)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(tmp_path), "TMPDIR": str(scratch),
           "GOV_REBUILD_PYTHON": str(stand_in)}
    try:
        done = subprocess.run(["bash", str(TOOLS / "rebuild_slot.sh"), str(tree)], env=env, capture_output=True,
                              text=True, timeout=120, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        pytest.skip("rebuild_slot.sh got no heavy-job slot within 120 s (the slots are taken): it cannot run here now")
    if done.returncode not in (0, 75):
        pytest.skip(f"rebuild_slot.sh did not run the planted rebuild here (exit {done.returncode}: "
                    f"{done.stderr.strip()[-300:]}): the heavy slot may be refused by the sandbox")
    return done


def test_s4_rebuild_slot_exits_75_on_the_planted_partial_result(tmp_path):
    done = _slot(tmp_path, PARTIAL["not_recreated with a reason"])
    assert done.returncode == 75, f"rebuild_slot.sh exited {done.returncode}, not 75\n{done.stderr}"


def test_s4_rebuild_slot_exits_75_on_the_planted_result_with_no_semantic_store(tmp_path):
    done = _slot(tmp_path, PARTIAL["no semantic store at all"])
    assert done.returncode == 75, f"rebuild_slot.sh exited {done.returncode}, not 75\n{done.stderr}"


def test_s4_rebuild_slot_passes_a_planted_whole_result(tmp_path):
    done = _slot(tmp_path, WHOLE["recreated"])
    assert done.returncode == 0, f"rebuild_slot.sh exited {done.returncode} on a whole result\n{done.stderr}"


# ---- F1, the gate side: no close or prepare check passes over a partial store ------------------------------------------

def test_f1_no_close_or_prepare_check_passes_a_partial_store(runs):
    """No planted partial result passes the close's check; the prepare (``gov rebuild --json``) fails on a real one."""
    gate = _gate()
    from gov.cli.errors import GovError

    for name, result in sorted(PARTIAL.items()):
        assert gate.semantic_failure(result), f"{name}: the close's check passes a partial store"
        with pytest.raises(GovError):
            gate.check(result)
    run, _, _ = runs.rebuild("s1-unavailable-json", embedder="dead", project_options={"files": 40})
    assert not run.prints_ok and run.returncode == 1, f"the prepare (gov rebuild --json) passed a partial store\n{run.describe()}"
