"""Skipped tests are counted in the close record (DEC-500, fifth behaviour; finding 13).

"Skipped tests are counted in the close record, for the acceptance run and the regression run, beside passed,
failed and errors. They refuse nothing: a skip is ordinary, and it is no longer silent."

The close record states its test counts as an object with ``passed``, ``failed`` and ``errors``
(``tests_run`` today, one object for both runs). No source says whether the two runs get one object or one
each, so the cases hold what both forms share (README, settlement 16): every object of the record that has
``passed`` has ``skipped`` beside it, a whole number; the number planted in one run is the ``skipped`` of at
least one of them; and none of them holds a number that was not planted.

The ticket of each case has a passing acceptance test, so the close measures something and closes
(``test_a_ticket_whose_only_acceptance_test_is_skipped_refuses`` stays: there no test passed). The skipped
tests would fail if they ran.

- two skipped tests in the ticket's acceptance folder, no regression test of the project skipped: closed, 2;
- one skipped test among the project's regression tests, none in the ticket's folder: closed, 1;
- no skipped test anywhere: closed, 0 (the count is stated, not left out).
"""

import w1_30_support as support

cli_support = support.cli_support

TICKET = "PROJ-skps"
WBS = "W1-skps"
COUNTS = ("passed", "failed", "errors")
SKIPPED = "skipped"

TWO_SKIPPED = (
    "import pytest\n\n\n"
    "@pytest.mark.skip(reason='not on this machine')\n"
    "def test_skipped_one():\n    assert False\n\n\n"
    "def test_skipped_two():\n    pytest.skip('not on this machine')\n    assert False\n"
)
ONE_PASSED_ONE_SKIPPED = (
    "import pytest\n\n\n"
    "def test_regression_passes():\n    assert True\n\n\n"
    "@pytest.mark.skip(reason='not on this machine')\n"
    "def test_regression_skipped():\n    assert False\n"
)


def _closed_with_counts(project, sandbox, interface):
    """Close the ticket; returns the ``skipped`` number of every object of the close record that states test
    counts."""
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"
    front = support.the_close_record(project, TICKET)
    counts = [entry for entry in cli_support.find_records(front, key="passed")
              if all(isinstance(entry.get(key), int) for key in COUNTS)]
    assert counts, f"the close record states no test counts: {sorted(front)}"
    for entry in counts:
        assert isinstance(entry.get(SKIPPED), int) and not isinstance(entry.get(SKIPPED), bool), \
            f"the close record states no number of skipped tests beside passed, failed and errors: {entry}"
        assert entry["failed"] == 0 and entry["errors"] == 0 and entry["passed"] >= 0, \
            f"a skipped test was counted as something else: {entry}"
    return [entry[SKIPPED] for entry in counts]


def _engineers_commit(project):
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=support.IMPLEMENTER, trailers=support.trailers_of(TICKET))


def test_skipped_acceptance_tests_are_counted_and_refuse_nothing(project, sandbox, interface):
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write(f"tests/acceptance/{WBS}/test_skipped.py", TWO_SKIPPED)
    _engineers_commit(project)

    skipped = _closed_with_counts(project, sandbox, interface)

    assert 2 in skipped and set(skipped) <= {0, 2}, \
        f"two acceptance tests were skipped; the close record says {skipped}"


def test_skipped_regression_tests_are_counted_and_refuse_nothing(project, sandbox, interface):
    project.write("tests/unit/test_w1_skps_regression.py", ONE_PASSED_ONE_SKIPPED)
    project.commit("a regression test file", who=support.ORCHESTRATOR)
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    _engineers_commit(project)

    skipped = _closed_with_counts(project, sandbox, interface)

    assert 1 in skipped and set(skipped) <= {0, 1}, \
        f"one regression test was skipped; the close record says {skipped}"


def test_a_close_without_skipped_tests_says_zero(project, sandbox, interface):
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    _engineers_commit(project)

    skipped = _closed_with_counts(project, sandbox, interface)

    assert set(skipped) == {0}, f"no test was skipped; the close record says {skipped}"
