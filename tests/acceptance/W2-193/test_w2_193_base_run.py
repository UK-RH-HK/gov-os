"""S4: when a red cannot be judged by its alone runs (absent or unknown on either side), the close runs the selection at
the base and judges the red by that run's result for its node: red there with the same failure type is a base red;
green or not collected there is the change's; a base run that collected zero tests or did not complete refuses
``BASELINE_MISSING`` naming the base commit and those reds, never ``RED_CAUSED`` for them; the record's ``base_run``
says whether it ran, its counts and whether it completed.

The absent red: a test in ``tests/acceptance/W2-bb/whole/`` whose parameter's id is ``whole`` only when a target of
the run is its folder (or a folder above it); run alone by the id the full run gave (``...[whole]``), pytest finds
nothing (exit 4), with the change and at the base.

Red on the base: today's close has no base run; an absent red never matches, so it is the change's (``RED_CAUSED``),
and with no green record there is no base at all.
"""

import re

import w2_193_support as support

RED, GREEN = "bb_whole_red", "bb_whole_green"
ROOT_CONFTEST = "conftest.py"
# At the base, a root conftest.py that deselects every collected test: the base run collects nothing.
COLLECTS_NOTHING = ("def pytest_collection_modifyitems(config, items):\n"
                    "    items.clear()  # the base's selection collects no test\n")


def test_an_absent_red_red_at_the_base_run_is_a_base_red(tmp_path, sandbox):
    """S4: no green record, so the base is the parent of the ticket's oldest own commit (the initial commit). The
    absent red fails there too (AssertionError both ways): the close passes, the red is recorded not caused, it ran
    at the base in the base run (and failed), and the record's ``base_run`` names the run: ``ran: true``, its
    commit the base, ``complete: true``, its counts with at least one red."""
    told = tmp_path / "project-told"
    made = support.project(tmp_path, files=support.whole_files(told, {RED: support.KNOWN_RED}))
    base = made.initial
    support.work(made)
    made.ready(sandbox)
    run = support.close(made, sandbox)

    support.assert_closed(made, run)
    front = support.record(made)
    entry = support.red_entry(front, support.whole_node(RED))
    assert entry.get("caused") is False, f"an absent red that is red at the base run is the change's: {entry}"
    runs = support.calls(support.base_side(support.told_runs(told, RED)))
    assert runs and not any(r["ok"] for r in runs), f"the absent red did not run (and fail) at the base: {runs}"
    base_run = front.get("base_run")
    assert isinstance(base_run, dict), f"the record has no base_run: {base_run!r}"
    missing = [k for k in support.BASE_RUN_KEYS if k not in base_run]
    assert not missing, f"base_run lacks {missing}: {base_run}"
    assert base_run["ran"] is True and base_run["complete"] is True, f"the base run is not named as run: {base_run}"
    assert base_run["commit"] == base, f"the base run's commit is not the base {base}: {base_run}"
    assert int(base_run["failed"]) + int(base_run["errors"]) >= 1, f"the base run counts no red: {base_run}"


def test_an_absent_red_green_at_the_base_run_is_the_change_s(tmp_path, sandbox):
    """S4, F1: the absent red passes at the base (the change breaks the widget it reads): refused with RED_CAUSED
    naming it, the ticket stays open, no repair ticket names it, and it ran at the base, where it passed."""
    told = tmp_path / "project-told"
    made = support.project(tmp_path, files=support.whole_files(told, {GREEN: support.NOT_BROKEN}))
    support.work(made, text="# the widget, CHANGED BROKEN\n")
    made.ready(sandbox)
    before = support.tickets(made)
    run = support.close(made, sandbox)

    support.assert_caused(made, run, before, support.whole_node(GREEN))
    runs = support.calls(support.base_side(support.told_runs(told, GREEN)))
    assert runs and all(r["ok"] for r in runs), f"the absent red did not run at the base, where it passes: {runs}"


def test_a_base_run_that_collects_nothing_refuses_baseline_missing_never_red_caused(tmp_path, sandbox):
    """S4: at the base (the initial commit, the parent of the ticket's own commit) a root ``conftest.py`` deselects
    every test, so the base run collects zero; the ticket's change removes it. The absent red cannot be judged:
    refused with BASELINE_MISSING naming the base commit and the red, never RED_CAUSED; the ticket stays open."""
    told = tmp_path / "project-told"
    files = {**support.whole_files(told, {RED: support.KNOWN_RED}), ROOT_CONFTEST: COLLECTS_NOTHING}
    made = support.project(tmp_path, files=files,
                           test_map=support.test_map(([ROOT_CONFTEST], [support.OWN])))
    base = made.initial
    support.remove(made, ROOT_CONFTEST)
    support.work(made)
    made.ready(sandbox)
    run = support.close(made, sandbox)

    said = support.assert_refused(run, support.BASELINE_MISSING)
    assert support.RED_CAUSED not in said, \
        f"the close refused RED_CAUSED for a red it could not judge\n{run.describe()}"
    named = [h for h in re.findall(r"[0-9a-f]{7,40}", said) if base.startswith(h)]
    assert named, f"the refusal does not name the base commit {base} (by 7 digits or more)\n{run.describe()}"
    node = support.whole_node(RED)
    assert node.split("[")[0] in said, f"the refusal does not name the red {node}\n{run.describe()}"
    assert made.ticket_status() == "in_progress", "the ticket closed on a base run that collected nothing"
