"""W2-57, KPI line 3: the route to the nightly, as behaviour of ``gov close`` and of the nightly's form.

DEC-889 item 5: live and real-model tests move to the nightly. In the close, an entry the list routes to the
nightly is collected and left out: deselected from the parallel phase (never ignored, never skipped) and not run in
the serial phase; an entry kept serial runs alone in the serial phase, as today. In the nightly's form (the parallel
run less the list, then every entry alone) the nightly entry's cases run. The route goes through the list, never
through a marker alone: a case that only carries a marker runs in the parallel phase like any other.

Each case builds a project of its own, as W1-30's round-11 cases do: small tests that tell, at every run, the
worker they ran in (none when alone) and the time, and a list in the reworked form (``<entry>  # <route>: <kind>:
<reason>``). ``gov close`` runs from this worktree's ``src/``; nothing of the product is imported or patched.
"""

from __future__ import annotations

import pytest

import w2_57_list_support as support

close_support = support.close_support

KEPT = f"{support.OTHER}/test_kept.py::test_kept"
ROUTED = f"{support.OTHER}/test_routed.py::test_routed"
ROUTED_FILE_NAME = "test_routed_file"
ROUTED_FILE = f"{support.UNIT}/{ROUTED_FILE_NAME}.py"
MARKED = "test_marked_but_unlisted"
MARKERS = "@pytest.mark.nightly\n@pytest.mark.live_session\n@pytest.mark.local_only\n"


@pytest.fixture()
def project(tmp_path):
    return close_support.Project(tmp_path / "project")


def _regression(told):
    """The regression tests: a kept entry, a routed function beside a sibling in its file, a routed whole file,
    a case that carries route-like markers and no entry, and plain cases."""
    routed = support.telling("test_routed", told)
    sibling = support.second_function(support.telling("test_routed_sibling", told))
    return {
        f"{support.OTHER}/test_kept.py": support.telling("test_kept", told),
        f"{support.OTHER}/test_routed.py": routed + sibling,
        ROUTED_FILE: support.telling(ROUTED_FILE_NAME, told),
        f"{support.OTHER}/test_marked.py": support.telling(MARKED, told, decorator=MARKERS),
        f"{support.UNIT}/test_plain.py": support.telling("test_plain", told),
    }


ACCEPTANCE = ("test_first_acceptance", "test_second_acceptance")


def test_a_nightly_entry_is_collected_and_left_out_of_both_phases_and_a_serial_entry_runs_alone(
    project, sandbox, interface, tmp_path,
):
    """One close. The nightly entries (a function, and a whole file) run nowhere in the close, are counted
    nowhere as skipped, and the sibling of the routed function still runs in parallel (the file is collected, not
    ignored); the serial entry runs once, alone, after the parallel run, and is the only case of the serial run;
    the marked case with no entry runs once in a worker. About 4 s."""
    told = tmp_path / "told"
    told.mkdir()
    support.build_closable(project, told, _regression(told),
                           {name: support.telling(name, told) for name in ACCEPTANCE},
                           listed=[(KEPT, support.SERIAL, "latency"), (ROUTED, support.NIGHTLY, "live-session"),
                                   (ROUTED_FILE, support.NIGHTLY, "real-model")])

    run = support.close(project, sandbox)

    result = close_support.result_of(run, interface)
    assert close_support.ticket_status(project.root, support.TICKET) == "closed", run.describe()
    ran = close_support.told_by(told)
    routed_runs = {name: ran[name] for name in ("test_routed", ROUTED_FILE_NAME) if name in ran}
    assert not routed_runs, (
        f"cases the list routes to the nightly ran in the close: {routed_runs} (a run in no worker is the serial "
        f"phase)\n{run.describe()}"
    )
    assert close_support.ran_alone(ran.get("test_kept", [])), (
        f"the entry kept serial did not run exactly once, alone: {ran.get('test_kept')}\n{run.describe()}"
    )
    in_parallel = ("test_routed_sibling", MARKED, "test_plain", *ACCEPTANCE)
    wrong = {name: ran.get(name) for name in in_parallel if not close_support.ran_in_a_worker(ran.get(name, []))}
    assert not wrong, (
        f"cases no entry names did not run exactly once in a worker of the parallel phase (a sibling of a routed "
        f"function, a case with route-like markers and no entry, plain cases): {wrong}\n{run.describe()}"
    )
    stated = close_support.runs_stated_by(result, "the result")
    skipped = [entry for entry in stated if entry["skipped"]]
    assert not skipped, f"a run of the close counts a skip; a routed case is left out, never skipped: {skipped}"
    afterwards = [entry for entry in stated if entry["form"] == close_support.SERIAL_AFTERWARDS]
    assert len(afterwards) == 1 and afterwards[0].get("cases") == [KEPT] and afterwards[0]["passed"] == 1, (
        f"the serial run must hold the kept entry alone, and no entry routed to the nightly: {afterwards}"
    )


def test_a_nightly_entry_whose_file_does_not_collect_still_refuses_the_close(project, sandbox, interface,
                                                                             tmp_path):
    """Collected, never ignored: a routed whole file that cannot be imported is a collection error of the close,
    which refuses it naming the file. About 2 s."""
    told = tmp_path / "told"
    told.mkdir()
    broken = f"{support.OTHER}/test_routed_broken.py"
    regression = {broken: "import w2_57_no_such_module_anywhere\n\n\ndef test_routed_broken():\n    pass\n",
                  f"{support.UNIT}/test_plain.py": support.telling("test_plain", told)}
    support.build_closable(project, told, regression, {name: support.telling(name, told) for name in ACCEPTANCE},
                           listed=[(broken, support.NIGHTLY, "live-session")])

    run = support.close(project, sandbox)

    error = close_support.refused(run, interface, close_support.EXIT_CHECK_FAILED)
    assert "test_routed_broken" in close_support.error_text(error), (
        f"a file routed to the nightly that cannot be collected did not refuse the close by name: it was ignored, "
        f"not collected\n{run.describe()}"
    )


def test_the_nightly_form_runs_every_entry_alone_after_its_parallel_run_less_the_list(tmp_path):
    """The nightly's form on a project of its own: the parallel run, with the close's plugin, runs no entry of
    the list, nightly or serial; then each entry runs alone and its cases pass. About 1 s."""
    root = tmp_path / "nightly"
    told = tmp_path / "told"
    told.mkdir()
    for rel, text in _regression(told).items():
        close_support.write(root, rel, text)
    close_support.write(root, support.LIST_REL, support.list_text(
        [(KEPT, support.SERIAL, "latency"), (ROUTED, support.NIGHTLY, "live-session"),
         (ROUTED_FILE, support.NIGHTLY, "real-model")]))

    runs = support.nightly_form(root)

    failed = [(form, entry, done.stdout[-800:]) for form, entry, done in runs if done.returncode != 0]
    assert not failed, f"a run of the nightly's form failed: {failed}"
    ran = close_support.told_by(told)
    for name in ("test_kept", "test_routed", ROUTED_FILE_NAME):
        assert close_support.ran_alone(ran.get(name, [])), (
            f"{name} (a list entry) did not run exactly once, alone, in the nightly's form: {ran.get(name)}"
        )
    for name in ("test_routed_sibling", MARKED, "test_plain"):
        assert close_support.ran_in_a_worker(ran.get(name, [])), (
            f"{name} (no entry names it) did not run once in the nightly's parallel run: {ran.get(name)}"
        )
