"""S13: ``gov close --verify <ticket>`` runs a lead's whole verify: the scoped selection, the parallel phase, then the
serial phase, each in a heavy-job slot; it writes ``select.json``, one JUnit file per phase and one summary line, and
writes its exit file last; exit 0 green, 1 a red, 2 the selection refused, 3 a run that did not complete.

Red on today's code: ``gov close --verify`` does not exist (argparse refuses the option: exit 2, no files).
"""

import json
import xml.etree.ElementTree as ElementTree

import w2_115_support as support

BB_WIDGET = support.node_of("W2-bb", "bb_widget", "test_bb_reads_the_widget")
BB_APART = support.node_of("W2-bb", "bb_apart", "test_bb_apart")
BB_KILL = support.node_of("W2-bb", "bb_kill", "test_bb_kills_its_run")
FILES = ("select.json", "parallel.xml", "serial.xml", "summary.txt", "verify.exit")


def _project(make_project, tmp_path, reds, serial=None):
    told = tmp_path / "project-told"
    files = {node.split("::")[0]: support.telling(node.split("::")[1], told, body) for node, body in reds.items()}
    return make_project(files=files, serial=serial)


def _cases(path):
    """``{name: outcome}`` of the JUnit file's test cases (passed, failure, error or skipped)."""
    found = {}
    for case in ElementTree.parse(path).iter("testcase"):
        outcome = "passed"
        for child in case:
            if child.tag in ("failure", "error", "skipped"):
                outcome = child.tag
        found[case.get("name")] = outcome
    return found


def test_a_red_and_a_serial_entry_exit_1_with_both_junit_files_and_the_summary(make_project, sandbox, tmp_path):
    """S13: a planted tree with one red and one serial entry: exit 1; ``select.json`` equals ``--select``'s set;
    ``parallel.xml`` holds the red, ``serial.xml`` the serial entry; ``summary.txt`` is one line; ``verify.exit``
    holds 1 and is written last."""
    project = _project(make_project, tmp_path, {BB_WIDGET: support.WIDGET_NOT_BROKEN, BB_APART: support.PASS},
                       serial=[BB_APART])
    project.work({support.WIDGET: "# the widget, CHANGED BROKEN\n"})
    project.ready(sandbox)
    out = tmp_path / "verify-out"
    run = project.verify(sandbox, out=out)
    assert run.returncode == support.VERIFY_EXIT_RED, f"a red verify does not exit 1\n{run.describe()}"
    missing = [name for name in FILES if not (out / name).is_file()]
    assert not missing, f"the verify did not write {missing}\n{run.describe()}"
    selected = support.selection(project.select(sandbox))
    assert json.loads((out / "select.json").read_text(encoding="utf-8")) == selected, \
        "select.json is not the set --select prints"
    parallel, serial = _cases(out / "parallel.xml"), _cases(out / "serial.xml")
    assert parallel.get("test_bb_reads_the_widget") in ("failure", "error"), f"the red is not in parallel.xml: {parallel}"
    assert serial.get("test_bb_apart") == "passed", f"the serial entry did not run in the serial phase: {serial}"
    assert "test_bb_apart" not in parallel, f"the serial entry ran in the parallel phase too: {parallel}"
    lines = (out / "summary.txt").read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1, f"summary.txt is not one line: {lines}"
    assert (out / "verify.exit").read_text(encoding="utf-8").strip() == "1", "verify.exit does not hold 1"
    last = (out / "verify.exit").stat().st_mtime_ns
    assert all((out / name).stat().st_mtime_ns <= last for name in FILES), "verify.exit was not written last"


def test_a_green_verify_exits_0_in_the_default_folder(make_project, sandbox):
    """S13: a green tree exits 0 and writes its files under ``.gov-runtime/close/verify/<ticket>/``, with an empty
    serial suite when no serial entry is selected."""
    project = make_project()
    project.work({support.WIDGET: "# the widget, CHANGED\n"})
    project.ready(sandbox)
    run = project.verify(sandbox)
    out = project.root / support.VERIFY_DIR_REL / support.TICKET
    assert run.returncode == support.VERIFY_EXIT_GREEN, f"a green verify does not exit 0\n{run.describe()}"
    missing = [name for name in FILES if not (out / name).is_file()]
    assert not missing, f"the verify did not write {missing} in the default folder\n{run.describe()}"
    assert _cases(out / "serial.xml") == {}, "the serial suite is not empty"
    assert (out / "verify.exit").read_text(encoding="utf-8").strip() == "0"


def test_a_refused_selection_exits_2(make_project, sandbox, tmp_path):
    """S13: a change nothing maps: the selection is refused, exit 2, SELECTION_REFUSED said, ``verify.exit`` holds 2."""
    project = make_project()
    project.merged({support.UNPLACED: "# odd\n"})
    project.work({support.WIDGET: "# the widget, CHANGED\n"})
    project.ready(sandbox)
    out = tmp_path / "verify-out"
    run = project.verify(sandbox, out=out)
    assert run.returncode == support.VERIFY_EXIT_REFUSED, f"a refused selection does not exit 2\n{run.describe()}"
    assert support.SELECTION_REFUSED in run.stdout + run.stderr, f"SELECTION_REFUSED is not said\n{run.describe()}"
    assert (out / "verify.exit").read_text(encoding="utf-8").strip() == "2", "verify.exit does not hold 2"
    assert not (out / "parallel.xml").exists(), "a refused selection ran the parallel phase"


def test_a_killed_run_exits_3(make_project, sandbox, tmp_path):
    """S13: a planted test kills its own test run: the run did not complete: exit 3, ``verify.exit`` holds 3."""
    project = _project(make_project, tmp_path, {BB_KILL: support.KILLS_ITS_RUN})
    project.work({support.WIDGET: "# the widget, CHANGED\n"})
    project.ready(sandbox)
    out = tmp_path / "verify-out"
    run = project.verify(sandbox, out=out)
    assert run.returncode == support.VERIFY_EXIT_INCOMPLETE, f"a killed run does not exit 3\n{run.describe()}"
    assert (out / "verify.exit").read_text(encoding="utf-8").strip() == "3", "verify.exit does not hold 3"
