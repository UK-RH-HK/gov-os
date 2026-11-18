"""S4: a failed update rolls back to the recorded point."""

from __future__ import annotations

import json

import w2_17_support as support

IGNORED = ".gov-runtime/w2-17-ignored.txt"     # an ignored file of the project, there before the update


def test_failed_adapter_generation_rolls_back_to_the_recorded_point(own_project, sandbox):
    project = own_project
    (project / IGNORED).parent.mkdir(parents=True, exist_ok=True)
    (project / IGNORED).write_text("W2-17: an ignored file the rollback leaves alone\n", encoding="utf-8")
    assert support.porcelain_paths(project) == [], "fixture: the planted ignored file shows in git status"
    before, before_pin = support.tree_state(project), support.pin_state(project)
    failing = support.failing_rulesync(sandbox.bin)

    run = support.update(project, sandbox, first=(failing,))

    assert run.returncode != 0, f"`gov update {support.B}` exited 0 although rulesync failed\n{run.describe()}"
    error = run.error()
    details = error.get("details") or {}
    assert error.get("code") == support.UPDATE_FAILED, f"the failure is not {support.UPDATE_FAILED}\n{run.describe()}"
    told = (str(error.get("message", "")) + " " + json.dumps(details)).lower()
    assert "adapters" in told, f"the failure does not name the failed step (adapters)\n{run.describe()}"
    assert details.get("rolled_back") is True and "roll" in str(error.get("message", "")).lower(), (
        f"the failure does not say it rolled back (details.rolled_back true, the message saying so)\n{run.describe()}")
    after = support.tree_state(project)
    assert after["head"] == before["head"], f"HEAD is not the commit before: {after['head']} != {before['head']}"
    changed = support.tree_difference(before, after)
    assert not changed, f"files outside .git are not byte-identical to before the failed update: {changed[:20]}"
    release = support.lock_release(project) or {}
    assert release.get("version") == support.A, f"the lock does not name {support.A} after the rollback: {release!r}"
    assert support.pin_state(project) == before_pin, (
        f"<common>/gov/ does not hold the pin it held before (none): {support.pin_state(project)!r}")
