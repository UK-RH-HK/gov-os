"""F4 (and S1's strict half): the strict close is unchanged in every verdict and every refusal.

The planted cases below were run on today's close (w2/integrate at f4f9c3204, before W2-115's change) in a project
with no ``close.yaml``; what it answered (``ok``, the exit code, the refusal's code, the evidence's scope) is recorded
in ``RECORDED``. After the change, a project with ``close: strict`` and a project with no ``close.yaml`` must give
the same answers on the same cases. The W1-30 and W2-07 suites stay the strict close's own tests (README, F4).

Green on today's code by design: today's close is the strict close (README, "Expected red").
"""

import pytest

import w2_115_support as support

CHANGED = "# the widget, CHANGED\n"
BROKEN = "# the widget, CHANGED BROKEN\n"
BB_WIDGET = support.file_of("W2-bb", "bb_widget")
BB_KNOWN = support.file_of("W2-bb", "bb_known")


def _plant(make_project, close, case):
    """The planted project of ``case``: a test planted before the base when the case needs one, and the nightly's
    record on the base (red with the known red's failure for ``unowned_red``)."""
    reds = {}
    if case == "caused_red":
        reds = {"widget": (BB_WIDGET, "test_bb_reads_the_widget", support.WIDGET_NOT_BROKEN)}
    if case == "unowned_red":
        reds = {"known": (BB_KNOWN, "test_bb_known", support.KNOWN_RED)}
    project = make_project(close=close, nightly="green")
    for _, (rel, name, body) in reds.items():
        project.merged({rel: support.telling(name, project.told, body)}, "a test planted before the base")
        project.plant_night(project.head(), [] if case != "unowned_red" else
                            [{"test": support.node_of("W2-bb", "bb_known", "test_bb_known"),
                              "failure_type": "AssertionError"}])
    return project


def _work(project, sandbox, case):
    if case == "shared_core":
        project.work({support.CORE: "# the shared core, CHANGED\n", support.WIDGET: CHANGED})
    elif case == "unplaced":
        project.merged({support.UNPLACED: "# odd\n"})
        project.work({support.WIDGET: CHANGED})
    elif case == "failing_acceptance":
        project.write(support.file_of("W2-aa"), support.telling(support.case_of("W2-aa"), project.told,
                                                                support.KNOWN_RED))
        project.git("add", "-A")
        project._commit("acceptance tests", support.close_support.TEST_DESIGNER,
                        ("Task: PROJ-aaaa", "Role: independent-test-designer", "Implements: CAP-01"))
        project.work({support.WIDGET: CHANGED})
    elif case == "caused_red":
        project.work({support.WIDGET: BROKEN})
    else:
        project.work({support.WIDGET: CHANGED})
    project.ready(sandbox)
    return project.close(sandbox)


def _answer(run):
    env = support.envelope(run)
    holder = env.get("result") if env.get("ok") else (env.get("error") or {}).get("details")
    evidence = (holder or {}).get("evidence") or {}
    return {"ok": env.get("ok"), "exit": run.returncode, "code": (env.get("error") or {}).get("code"),
            "scope": evidence.get("scope")}


# What today's close answered on each planted case (recorded before the change; README, F4).
RECORDED = {
    "green": {"ok": True, "exit": 0, "code": None, "scope": "scoped"},
    "failing_acceptance": {"ok": False, "exit": 3, "code": "CHECK_FAILED", "scope": "scoped"},
    "caused_red": {"ok": False, "exit": 3, "code": "CHECK_FAILED", "scope": "scoped"},
    "unowned_red": {"ok": False, "exit": 3, "code": "CHECK_FAILED", "scope": "scoped"},
    "shared_core": {"ok": True, "exit": 0, "code": None, "scope": "full"},
    "unplaced": {"ok": True, "exit": 0, "code": None, "scope": "full"},
}


@pytest.mark.parametrize("close", [None, support.STRICT], ids=["no_close_yaml", "close_strict"])
@pytest.mark.parametrize("case", sorted(RECORDED))
def test_the_strict_close_gives_the_recorded_verdict(make_project, sandbox, close, case):
    """F4: every verdict and every refusal of the strict close (``close: strict`` or no file) is the recorded one."""
    project = _plant(make_project, close, case)
    run = _work(project, sandbox, case)
    answer = _answer(run)
    assert answer == RECORDED[case], (f"the strict close's answer on {case} changed: {answer} != {RECORDED[case]}\n"
                                      f"{run.describe()}")


@pytest.mark.parametrize("close", [None, support.STRICT], ids=["no_close_yaml", "close_strict"])
def test_the_strict_close_still_runs_the_full_regression_on_a_shared_core_change(make_project, sandbox, close):
    """S1, F4: the strict close keeps every lifted gate built: a shared-core change still runs the full regression
    (the suite no change reaches runs too)."""
    project = _plant(make_project, close, "shared_core")
    run = _work(project, sandbox, "shared_core")
    support.passed(run)
    assert project.ran(support.case_of("W2-dd")), \
        f"the strict close did not run the full regression on a shared-core change\n{run.describe()}"
