"""Part 1, KPI 1, KPI 2 and failure line 1: a moved file is in the change at both its paths.

The change since the base is every path a move touches: the path the file left and the path it reached. Git's
rename detection pairs the two and, asked for names only, gives the path it reached alone; the path it left must
not be hidden by it (README, "Interface", item 2). From the FULL review of 9174e358. README, "Part 1".
"""

import w2_66_support as support

# The fixture's shared core moved, unchanged, to a gadget path (W2-cc's paths: placed, outside the shared core).
CORE_MOVED_OUT = "src/gov/gadget/core.py"
# A gadget module (W2-cc's paths) that W2-cc's suite loads, moved to a widget path (the closed ticket's paths).
PART_LEFT = "src/gov/gadget/part.py"
PART_REACHED = "src/gov/widget/part.py"
CC_PART = "tests/acceptance/W2-cc/test_cc_part.py::test_cc_part"
# A gadget module moved into the shared core.
GADGET = "src/gov/gadget/other.py"
GADGET_MOVED_IN = "src/gov/close/other.py"


def _changed(evidence):
    changed = evidence.get("changed")
    assert isinstance(changed, list), f"the evidence does not state the change: {evidence}"
    return changed


def test_a_file_moved_out_of_the_shared_core_runs_the_full_regression(fixture, sandbox):
    """The path the file left is under the shared core: the full regression, whatever path it reached."""
    fixture.moved(support.CORE, CORE_MOVED_OUT)
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    evidence = support.assert_full(run, fixture, support.SHARED_CORE, path=support.CORE)
    changed = _changed(evidence)
    assert support.CORE in changed and CORE_MOVED_OUT in changed, \
        f"the change does not name both paths of the move ({support.CORE}, {CORE_MOVED_OUT}): {changed}"


def test_a_file_moved_away_from_another_ticket_s_paths_selects_that_ticket_s_suite(fixture, sandbox):
    """W2-cc's paths hold the path the module left; its suite loads the module there and is red once it moved.
    The overlap rule reads the path the file left: W2-cc's suite runs, and its red refuses the close."""
    body = ("import importlib.util\n"
            "    from pathlib import Path\n"
            f"    where = Path(__file__).resolve().parents[3] / {PART_LEFT!r}\n"
            "    spec = importlib.util.spec_from_file_location('part', where)\n"
            "    module = importlib.util.module_from_spec(spec)\n"
            "    spec.loader.exec_module(module)\n"
            "    assert module.VALUE == 7")
    fixture.based({PART_LEFT: "VALUE = 7\n",
                   CC_PART.split("::")[0]: support._telling("test_cc_part", fixture.told, body=body)},
                  "W2-cc's module and the case that loads it, green at the base")
    fixture.moved(PART_LEFT, PART_REACHED)
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    evidence = support.evidence_of(run)
    assert PART_LEFT in _changed(evidence), f"the change does not name the path the file left: {evidence['changed']}"
    why = [w for w in support.selected_for(evidence, support.suite_of("W2-cc")) if w["reason"] == support.OVERLAP]
    assert any(w.get("ticket") == "PROJ-cccc" and PART_LEFT in (w.get("paths") or []) for w in why), \
        (f"W2-cc is not selected with {support.OVERLAP} naming PROJ-cccc and {PART_LEFT}: "
         f"selected {evidence.get('selected')}, left out {support.left_out_for(evidence, support.suite_of('W2-cc'))}")
    assert fixture.ran("test_cc_part"), "W2-cc's case that loads the moved module did not run"
    support.refused(run)
    failing = [f for f in evidence.get("failures") or [] if support.covers(CC_PART, str(f.get("test")))]
    assert failing, f"W2-cc's red case is not among the failures: {evidence.get('failures')}"


def test_a_file_moved_into_the_shared_core_runs_the_full_regression(fixture, sandbox):
    """The path the file reached is under the shared core: the full regression (green on the base), and the change
    names both paths."""
    fixture.moved(GADGET, GADGET_MOVED_IN)
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    evidence = support.assert_full(run, fixture, support.SHARED_CORE, path=GADGET_MOVED_IN)
    changed = _changed(evidence)
    assert GADGET in changed and GADGET_MOVED_IN in changed, \
        f"the change does not name both paths of the move ({GADGET}, {GADGET_MOVED_IN}): {changed}"
