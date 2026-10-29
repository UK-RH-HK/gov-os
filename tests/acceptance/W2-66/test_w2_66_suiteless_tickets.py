"""Part 1, KPI 2 and failure line 1: a path placed only by tickets that have no acceptance suite is not placed.

A changed path that no coupling, no ``record_only`` pattern and no suite folder holds, and that only the
``allowed_paths`` of tickets without an acceptance suite hold (their suite folder, declared or their WBS id's,
holds no test file), maps to no suite: it runs the full regression, ``UNPLACED`` naming it, as a path no mapping
places does (README, "Interface", item 3). From the FULL review of 9174e358. README, "Part 1".
"""

import w2_66_support as support

NOBODY = "src/gov/nobody/n.py"
# Two closed tickets hold the path, neither with a suite: W2-nn declares its WBS id's folder, which does not exist;
# W1-nm declares a folder that holds its README and no test.
NO_FOLDER = ("PROJ-nnnn", "W2-nn", None)
EMPTY_FOLDER = ("PROJ-nmnm", "W1-nm", "tests/acceptance/W1-nx")


def test_a_path_only_suiteless_tickets_hold_runs_the_full_regression(fixture, sandbox):
    files = {NOBODY: "# nobody's suite tests this\n", f"{EMPTY_FOLDER[2]}/README.md": "# W1-nm's folder, no test\n"}
    for ticket, wbs, folder in (NO_FOLDER, EMPTY_FOLDER):
        files[support.close_support.ticket_path(ticket)] = support.close_support.ticket_text(
            ticket, wbs, allowed_paths=["src/gov/nobody/**"], status="closed",
            acceptance=f"{folder}/" if folder else True)
    fixture.based(files, "two closed tickets without an acceptance suite, and their module")
    for folder in (support.suite_of(NO_FOLDER[1]), support.suite_of(EMPTY_FOLDER[1])):
        assert not (fixture.root / folder).exists(), f"the fixture is wrong: {folder} exists"
    assert not list((fixture.root / EMPTY_FOLDER[2]).rglob("test_*.py")), "the fixture is wrong: a test file"
    fixture.merged({NOBODY: "# nobody's suite tests this, changed\n"})
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    support.assert_full(run, fixture, support.UNPLACED, path=NOBODY)
