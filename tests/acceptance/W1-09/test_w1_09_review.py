"""Described behaviours from the review of the implementation (DEC-136), added after implementation.

Three behaviours the first suite missed, each under the KPI line or Contract item it belongs to:

- failure 1 [CAP-23.a]: a release never removes another holder's claim, raced from separate processes (DEC-292);
- failure 2: only a folder of the project, strictly below ``tests/acceptance/``, is an acceptance tests folder
  (DEC-293);
- success 3 [CAP-31.c]: a claim that cannot be inspected counts as a claim.
"""

from __future__ import annotations

import os
import time

import pytest

import w1_09_support as support

A = "TST-a001"
DEAD = "engineer:session-dead"

# ---- failure 1: a release never removes another holder's claim

RELEASES = 4          # the dead session's own release and the orchestrator's, twice over
CLAIMERS = 8
RACE_BATCHES = 6      # times the processes are started
RACE_TICKETS = 12     # tickets every process goes through in one batch; each ticket is one round of the race
RACE_START_S = 1.0


def _batch(api, root, function, tickets, holder, not_before=0.0):
    """One new process that calls ``function(root, ticket, holder)`` for every ticket in turn."""
    return api._start([(support.TASKS_MODULE, function, root, (ticket, holder), {}) for ticket in tickets],
                      not_before)


def _outcomes(api, process, what):
    try:
        return api._finish(process, what)
    except support.TasksMissing:
        raise
    except AssertionError as exc:
        pytest.fail(f"{what} ended with an error that is no GovError, so not {support.CLAIM_NOT_HELD} or "
                    f"{support.CLAIM_HELD}:\n{exc}", pytrace=False)


def test_releases_and_claims_raced_from_separate_processes_never_remove_another_holders_claim(api, project):
    """A dead session holds the tickets. Four releases that name it and eight claims by others start together.

    DEC-292 has the main orchestrator release a dead session's claim by naming its holder, so the session's own
    release and the orchestrator's can overlap, with the next claims right behind them. Per ticket: at most one
    release succeeds and every other fails with CLAIM_NOT_HELD; at most one claim succeeds and every other fails
    with CLAIM_HELD; the claimer that succeeded holds the ticket at the end.
    """
    claimers = [f"engineer:racer-{number}" for number in range(CLAIMERS)]
    batches = [[project.ticket(f"TST-x{batch}{number:02d}", f"W9-x{batch}{number:02d}")
                for number in range(RACE_TICKETS)] for batch in range(RACE_BATCHES)]
    project.settle()
    for tickets in batches:
        held = _outcomes(api, _batch(api, project.root, "claim", tickets, DEAD), "the first claims")
        assert all(outcome.ok for outcome in held), "the first holder could not claim the free tickets"

        not_before = time.time() + RACE_START_S
        processes = [("release", DEAD, _batch(api, project.root, "release", tickets, DEAD, not_before))
                     for _ in range(RELEASES)]
        processes += [("claim", claimer, _batch(api, project.root, "claim", tickets, claimer, not_before))
                      for claimer in claimers]
        raced = [(function, holder, _outcomes(api, process, f"a raced {function} that names {holder}"))
                 for function, holder, process in processes]
        readers = api._start([(support.TASKS_MODULE, "holder", project.root, (ticket,), {}) for ticket in tickets])
        final = [outcome.value for outcome in _outcomes(api, readers, "reading the holders")]

        for index, ticket in enumerate(tickets):
            releases = [outcomes[index] for function, _, outcomes in raced if function == "release"]
            claims = [(holder, outcomes[index]) for function, holder, outcomes in raced if function == "claim"]
            released = [outcome for outcome in releases if outcome.ok]
            winners = [holder for holder, outcome in claims if outcome.ok]
            picture = (f"{ticket}: {len(released)} of {RELEASES} releases and the claims of {winners} succeeded; "
                       f"the holder at the end is {final[index]!r}")

            assert len(winners) <= 1, f"two agents hold the same claim. {picture}"
            assert len(released) <= 1, f"one claim was released more than once. {picture}"
            for outcome in releases:
                if not outcome.ok:
                    support.assert_error(outcome, support.CLAIM_NOT_HELD, f"a release that lost the race on {ticket}")
            for holder, outcome in claims:
                if not outcome.ok:
                    support.assert_error(outcome, support.CLAIM_HELD, f"the claim of {holder} that lost on {ticket}")
            if winners:
                assert len(released) == 1, f"a claim succeeded on a ticket nobody released. {picture}"
                assert final[index] == winners[0], f"a release removed another holder's claim. {picture}"
            else:
                expected = None if released else DEAD
                assert final[index] == expected, f"the holder at the end is not {expected!r}. {picture}"


# ---- failure 2: only a folder of the project, below tests/acceptance/, is an acceptance tests folder

def _outside(project, name):
    """A folder with a suite in it, beside the project."""
    return support.write(project.root.parent, f"{name}/README.md", "# acceptance tests outside the project\n").parent


def _absolute(project):
    return {"acceptance": str(_outside(project, "outside"))}


def _named(path, folder=None):
    def build(project):
        if folder:
            support.write(project.root, f"{folder}/README.md", "# a folder of the project\n")
        return {"acceptance": path}
    return build


def _elsewhere(project):
    _outside(project, "elsewhere")
    return {"acceptance": "../elsewhere"}


def _wbs(wbs):
    def build(project):
        support.write(project.root, "tests/acceptance/README.md", "# acceptance tests\n")
        return {"wbs": wbs, "acceptance": False}
    return build


def _link(project):
    link = project.root / "tests" / "acceptance" / "W9-01"
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(_outside(project, "outside"), target_is_directory=True)
    return {}


NOT_AN_ACCEPTANCE_TESTS_FOLDER = [
    pytest.param(_absolute, id="path-absolute-outside-the-project"),
    pytest.param(_named("."), id="path-dot"),
    pytest.param(_named("./"), id="path-dot-slash"),
    pytest.param(_named(".."), id="path-parent"),
    pytest.param(_elsewhere, id="path-parent-elsewhere"),
    pytest.param(_named("src", "src"), id="path-src"),
    pytest.param(_named(".git"), id="path-git-folder"),
    pytest.param(_named("tests/acceptance/", "tests/acceptance"), id="path-tests-acceptance-itself"),
    pytest.param(_wbs("."), id="wbs-id-dot"),
    pytest.param(_wbs("../.."), id="wbs-id-two-parents"),
    pytest.param(_link, id="link-to-a-folder-outside-the-project"),
]


@pytest.mark.parametrize("build", NOT_AN_ACCEPTANCE_TESTS_FOLDER)
def test_a_folder_that_is_not_below_the_projects_acceptance_tests_does_not_count(project, build):
    """The ticket has no acceptance tests folder; what its frontmatter names exists, and is not one."""
    keys = build(project)
    project.ticket(A, keys.pop("wbs", "W9-01"), tests=False, **keys)
    ready, blocked = project.queue()
    assert A not in ready, "a ticket without tests/acceptance/<id>/ appears as READY"
    assert blocked == {A: [support.NO_ACCEPTANCE_TESTS]}


@pytest.mark.parametrize("path", ["tests/acceptance/feature-one/", "tests/acceptance/feature-one"])
def test_a_named_folder_below_the_projects_acceptance_tests_counts(project, path):
    """Kept green: with or without the trailing slash."""
    project.ticket(A, "W9-01", tests=False, acceptance=path)
    project.tests_folder("feature-one")
    ready, blocked = project.queue()
    assert ready == [A]
    assert blocked == {}


# ---- success 3 [CAP-31.c]: a claim that cannot be inspected counts as a claim

@pytest.mark.skipif(os.geteuid() == 0, reason="a folder's mode does not stop the super-user")
def test_a_claim_in_a_claims_folder_that_cannot_be_read_still_holds_the_ticket(project):
    project.ticket(A, "W9-01")
    assert project.claim(A, DEAD).ok
    project.settle()
    claims = project.root / support.CLAIMS_REL
    claims.chmod(0o000)
    try:
        ready = project.ready(settle=False)
        blocked = project.blocked(settle=False)
    finally:
        claims.chmod(0o755)
    assert A not in ready, "a ticket whose claim cannot be inspected appears as READY"
    assert blocked == {A: [support.CLAIMED]}
