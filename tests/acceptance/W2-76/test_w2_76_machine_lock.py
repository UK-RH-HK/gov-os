"""KPI success 3 and failure "two rebuilds running at once on the machine": one store rebuild at a time.

Every rebuild takes one exclusive ``flock`` on the lock path (here a temporary one, set by ``rebuild.yaml``), holds it
to the end and releases it by ending. A rebuild that waits says on standard error, before it waits, what it waits
for (the lock's path and its holder's pid and command line where the machine shows them) and records its wait in
``lock.wait_s``, apart from ``timing``. A rebuild under its caller's own hold (``flock <lock> gov rebuild``,
``flock <lock> timeout <n> gov rebuild``) runs at once, ``held_by_caller: true`` (DEC-939 item 2, row W2-M408).
"""

from __future__ import annotations

import pytest

import w2_76_support as support

pytestmark = support.needs_tools

# The planted stage that keeps a rebuild holding the lock for a while (seconds).
HOLD_S = 4.0


def _span(run):
    part = run.result.get("lock") or {}
    return support.iso(part["taken_at"]), support.iso(part["released_at"])


def _lock_part(run):
    part = run.result.get("lock")
    assert isinstance(part, dict) and all(key in part for key in support.LOCK_KEYS), \
        f"the result has no full lock part\n{run.describe()}"
    return part


def test_two_rebuilds_at_once_run_one_after_the_other(box, lock, env):
    """Two rebuilds started at once, in two repositories sharing one lock path: their spans do not overlap, and the
    second says what it waits for (the first's pid) and records its wait in ``lock.wait_s``, not in ``timing``."""
    projects = [support.make_project(box, f"project-{n}", lock) for n in (1, 2)]
    envs = [support.environment(box, support.slow_gitleaks(box, f"tools-{n}", HOLD_S)) for n in (1, 2)]

    started = [support.Background(projects[n], envs[n], support.rebuild_argv("--no-embeddings"),
                                  box.base / f"out-{n}") for n in (0, 1)]
    runs = [one.finish() for one in started]

    for one in runs:
        assert one.returncode == 0 and one.envelope().get("ok") is True, f"a rebuild failed\n{one.describe()}"
    parts = [_lock_part(one) for one in runs]
    first, second = sorted(range(2), key=lambda n: support.iso(parts[n]["taken_at"]))
    first_span, second_span = _span(runs[first]), _span(runs[second])
    assert second_span[0] >= first_span[1], \
        f"the two rebuilds ran at once: {parts[first]} and {parts[second]}"
    assert parts[second]["wait_s"] >= HOLD_S / 2, f"the second rebuild's wait was not recorded: {parts[second]}"
    assert parts[first]["wait_s"] < parts[second]["wait_s"]
    assert not [key for key in runs[second].result.get("timing", {}) if "wait" in key], "the wait is in timing"
    assert runs[second].result["timing"]["total_s"] <= runs[second].seconds - parts[second]["wait_s"] + 1.5, \
        f"the second's total_s counts its wait: {runs[second].result['timing']} {parts[second]}"
    said = runs[second].stderr
    assert str(lock) in said and str(runs[first].pid) in said, \
        f"the waiting rebuild did not say what it waits for (the lock {lock}, the holder pid {runs[first].pid})\n" \
        f"{runs[second].describe()}"


def test_a_waiting_rebuild_says_before_it_waits_what_it_waits_for(box, lock, env):
    """Another process (not the rebuild's ancestor) holds the lock: the rebuild says, while it still waits, the lock's
    path and the holder's pid and command line; it waits without a time limit, then runs, and records the wait."""
    project = support.make_project(box, "project", lock)
    holder = support.Holder(lock, box.base / "holder")
    background = None
    try:
        background = support.Background(project, env, support.rebuild_argv("--no-embeddings"), box.base / "out")
        said = support.wait_until(lambda: str(lock) in background.stderr_now(), timeout=20)
        still_waiting = background.running()
        early = background.stderr_now()
        support.wait_until(lambda: not background.running(), timeout=2.5)
        waited_past = background.running()
    finally:
        holder.let_go()
    run = background.finish()

    assert said and still_waiting, f"no line naming the lock {lock} while the rebuild waited\n{run.describe()}"
    assert str(holder.pid) in early and "w2_76_holder" in early, \
        f"the waiting rebuild did not name its holder's pid {holder.pid} and command line\nstderr:\n{early}"
    assert waited_past, "the rebuild ran while another process held its lock"
    assert run.returncode == 0, f"the rebuild did not run once the lock was free\n{run.describe()}"
    part = _lock_part(run)
    assert part["wait_s"] >= 2.0 and part["held_by_caller"] is False, f"the wait was not recorded: {part}"
    assert str(holder.pid) in str(part["holder"]), f"the lock part does not name the holder: {part}"


@support.needs_flock
@pytest.mark.parametrize("through_timeout", [False, True], ids=["flock", "flock-timeout"])
def test_a_rebuild_under_its_callers_hold_runs_at_once(box, lock, env, through_timeout):
    """The interim wrapper: ``flock <lock> [timeout <n>] gov rebuild`` ends within the stated bound, with no deadlock;
    it takes no second lock and says ``held_by_caller: true``, ``wait_s`` 0.0."""
    project = support.make_project(box, "project", lock)
    middle = [support.TIMEOUT, "100"] if through_timeout else []
    argv = [support.FLOCK, str(lock), *middle, *support.rebuild_argv("--no-embeddings")]

    run = support.run(project, env, argv, timeout=support.WRAPPED_BOUND_S)

    assert run.returncode is not None, \
        f"the wrapped rebuild did not end within {support.WRAPPED_BOUND_S:.0f} s: it waits on its caller's hold"
    assert run.returncode == 0 and run.envelope().get("ok") is True, run.describe()
    part = _lock_part(run)
    assert part["held_by_caller"] is True and part["wait_s"] == 0.0 and part["path"] == str(lock), \
        f"a rebuild under its caller's hold must say so: {part}"


@support.needs_flock
def test_a_wrapped_and_an_unwrapped_rebuild_never_run_at_once(box, lock):
    """``flock <lock> gov rebuild`` in one repository and a bare rebuild in another, on the same lock path, started
    together: their spans do not overlap."""
    projects = [support.make_project(box, f"project-{n}", lock) for n in (1, 2)]
    envs = [support.environment(box, support.slow_gitleaks(box, f"tools-{n}", HOLD_S)) for n in (1, 2)]
    argvs = [[support.FLOCK, str(lock), *support.rebuild_argv("--no-embeddings")],
             support.rebuild_argv("--no-embeddings")]

    started = [support.Background(projects[n], envs[n], argvs[n], box.base / f"out-{n}") for n in (0, 1)]
    runs = [one.finish(timeout=support.WRAPPED_BOUND_S) for one in started]

    for one in runs:
        assert one.returncode == 0, f"a rebuild failed or did not end\n{one.describe()}"
    parts = [_lock_part(one) for one in runs]
    assert parts[0]["held_by_caller"] is True and parts[1]["held_by_caller"] is False, parts
    spans = sorted([_span(runs[0]), _span(runs[1])])
    assert spans[1][0] >= spans[0][1], f"a wrapped and an unwrapped rebuild ran at once: {parts}"
