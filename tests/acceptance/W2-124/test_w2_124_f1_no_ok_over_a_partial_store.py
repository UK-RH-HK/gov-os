"""F1: an ok answer, or a close, over a partial semantic store is the failure.

Ticket F1: the planted partial-store cases of S1 and S4: no ``gov rebuild`` run prints ok and no close or prepare check
passes; any ok or pass there is this failure. (The gate side, S4's close and prepare checks, is
``test_w2_124_s4_close_and_prepare_gate.py::test_f1_no_close_or_prepare_check_passes_a_partial_store``; the hung and the
HTTP 500 embedders are S1's in-process cases, which end in a ``REBUILD_FAILED`` and no returned result.)
"""

from __future__ import annotations

import pytest

CASES = {
    "unavailable-json": dict(embedder="dead", args=("--json",)),
    "unavailable-human": dict(embedder="dead", args=()),
    "part-way-json": dict(embedder=("part-way",), args=("--json",)),
    "part-way-human": dict(embedder=("part-way",), args=()),
}


@pytest.mark.parametrize("name", sorted(CASES))
def test_f1_no_gov_rebuild_run_prints_ok_over_a_partial_store(runs, name):
    run, asked, project = runs.rebuild(f"f1-{name}", project_options={"files": 40}, **CASES[name])
    if name.startswith("part-way"):
        assert asked and asked > 1, f"{name}: the stand-in was asked {asked} time(s): the store was not partial"
    assert run.returncode not in (0, None), f"{name}: the rebuild exited 0 over a partial semantic store\n{run.describe()}"
    assert run.envelope().get("ok") is not True, f"{name}: the envelope says ok over a partial store\n{run.describe()}"
    assert '"ok": true' not in run.stdout, f"{name}: the output says ok over a partial store\n{run.describe()}"
    assert "REBUILD_FAILED" in run.stdout + run.stderr and "store: semantic" in run.stdout + run.stderr, \
        f"{name}: the failure is not named (REBUILD_FAILED, store: semantic)\n{run.describe()}"
