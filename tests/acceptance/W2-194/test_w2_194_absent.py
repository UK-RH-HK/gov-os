"""S1 and F1 (absent reds): a red whose alone re-run is absent but which is red, with the same failure type, in the base
run's own selection at the base counts as a base red; one green there, red with another failure type there, or not
collected there is the change's.

The absent red is W2-193's planted test that exists only when its folder is collected whole
(``tests/acceptance/W2-bb/whole/``): run alone by the id the full run gave, pytest finds nothing, with the change and
at the base. ``--base`` is given as a full commit id (EXAMIN's close named its base so).

Red on the base: today's close has no base run; an absent red never matches, so it is the change's: ``RED_CAUSED``
for the base red; for the others the refusal is today's too, but the red never ran at the base.
"""

import w2_193_support as support

RED, GREEN, FLIP, LATE = "bb_absent_red", "bb_absent_green", "bb_absent_flip", "bb_absent_late"


def _closed_against_the_initial_commit(tmp_path, sandbox, tests, text="# the widget, CHANGED\n", late=None):
    told = tmp_path / "project-told"
    made = support.project(tmp_path, files=support.whole_files(told, tests))
    base = made.initial
    if late:
        made.merged(support.whole_files(told, late), "another ticket's test, after the base")
    support.work(made, text=text)
    made.ready(sandbox)
    before = support.tickets(made)
    return made, told, before, support.close(made, sandbox, "--base", base)


def test_an_absent_red_red_at_the_base_run_is_not_the_change_s(tmp_path, sandbox):
    """S1: the absent red fails at the base with the same failure type (AssertionError): the close does not refuse
    RED_CAUSED, it passes, the record's entry for the red is ``caused: false``, and the red ran (and failed) at the
    base."""
    made, told, _, run = _closed_against_the_initial_commit(tmp_path, sandbox, {RED: support.KNOWN_RED})
    support.assert_closed(made, run)
    entry = support.red_entry(support.record(made), support.whole_node(RED))
    assert entry.get("caused") is False, f"the absent red, red at the base run, is the change's: {entry}"
    runs = support.calls(support.base_side(support.told_runs(told, RED)))
    assert runs and not any(r["ok"] for r in runs), f"the absent red did not run (and fail) at the base: {runs}"


def test_an_absent_red_green_at_the_base_run_refuses(tmp_path, sandbox):
    """F1: the absent red passes at the base (the change breaks the widget it reads): refused with RED_CAUSED naming
    it, the ticket stays open, and it ran at the base, where it passed."""
    made, told, before, run = _closed_against_the_initial_commit(tmp_path, sandbox, {GREEN: support.NOT_BROKEN},
                                                                 text="# the widget, CHANGED BROKEN\n")
    support.assert_caused(made, run, before, support.whole_node(GREEN))
    runs = support.calls(support.base_side(support.told_runs(told, GREEN)))
    assert runs and all(r["ok"] for r in runs), f"the absent red did not run at the base, where it passes: {runs}"


def test_an_absent_red_with_another_failure_type_at_the_base_run_refuses(tmp_path, sandbox):
    """F1 (S1's same failure type): the absent red is a KeyError on the change and an AssertionError at the base:
    refused with RED_CAUSED naming it, and it ran (and failed) at the base."""
    made, told, before, run = _closed_against_the_initial_commit(tmp_path, sandbox, {FLIP: support.TYPE_FLIP_TO_KEY})
    support.assert_caused(made, run, before, support.whole_node(FLIP))
    runs = support.calls(support.base_side(support.told_runs(told, FLIP)))
    assert runs and not any(r["ok"] for r in runs), f"the absent red did not run at the base: {runs}"


def test_an_absent_red_not_collected_at_the_base_run_refuses(tmp_path, sandbox):
    """F1: the absent red is added after the base (another ticket's merged commit), so the base run does not
    collect it: refused with RED_CAUSED naming it; the ticket stays open. Green on today's code by design (today
    every absent red is the change's); it guards the new base-run route against excusing a red the base lacks."""
    made, _, before, run = _closed_against_the_initial_commit(tmp_path, sandbox, {RED: support.PASS},
                                                              late={LATE: support.KNOWN_RED})
    support.assert_caused(made, run, before, support.whole_node(LATE))
