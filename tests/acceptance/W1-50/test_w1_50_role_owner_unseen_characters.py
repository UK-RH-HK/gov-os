"""W1-50 — ``Role: owner`` with characters around it that do not show is a ``Role: owner`` commit.

Added after implementation, from the review after the suite went green
(DEC-136, DEC-137). The behaviour, as it was passed to the test designer:

    A `Role` value that reads as `owner` once whitespace and control
    characters around it are removed is a `Role: owner` commit, and a
    finding.

KPI success 5 [CAP-58.h]: "A commit carrying a Role: owner trailer that is made
during any agent session's call is a finding (DEC-360)".

DEC-360 (owner): "The owner's approval fact for a decision is the `Role: owner`
trailer on the commit that sets the decision `ACTIVE`." The safeguard is there
so that no agent's call makes a commit that a reader takes for the owner's. A
form feed, a vertical tab, a no-break space, a zero-width space, the byte 0x01
or the byte 0x7f after ``owner`` shows nothing in ``git log`` or in a review:
the trailer reads ``Role: owner``. Git keeps each of them in the trailer's
value.

Every commit here is made in the orchestrator's own call and changes
``README.md``, which the orchestrator may write itself. Its only trailer is the
``Role`` line, so without the safeguard it is judged against the caller
(DEC-267) and passes.

The last test holds ``Owner`` and ``OWNER``.
"""

from __future__ import annotations

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET
OWNER = support.OWNER

# name: the ``Role`` value
UNSEEN = {
    "owner-then-a-form-feed": OWNER + "\x0c",
    "owner-then-a-vertical-tab": OWNER + "\x0b",
    "owner-then-a-no-break-space": OWNER + " ",
    "owner-then-a-zero-width-space": OWNER + "​",
    "owner-then-the-byte-0x01": OWNER + "\x01",
    "owner-then-the-byte-0x7f": OWNER + "\x7f",
    "a-no-break-space-then-owner": " " + OWNER,
}


def _role_owner_commit(project, call, value):
    """One call of the orchestrator that commits README.md with the only trailer ``Role: <value>``."""
    line = f"Role: {value}"
    command = support.commit_changes([support.README], (line,))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    found = support.final_block(project, "HEAD")
    assert found == [line.encode("utf-8")], (
        f"the fixture is wrong: the commit's final block is {found!r}, not the one line {line.encode('utf-8')!r}"
    )
    what = (f"a commit of {support.README} whose only trailer is {line!r}, made in the orchestrator's own call "
            f"on {TICKET}")
    return result, left, what


@pytest.mark.parametrize("case", sorted(UNSEEN), ids=sorted(UNSEEN))
def test_role_owner_with_characters_around_it_that_do_not_show_is_a_finding(project, call, case):
    """KPI success 5, read fail-closed."""
    result, left, what = _role_owner_commit(project, call, UNSEEN[case])
    check_support.assert_caught(result, support.README, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


@pytest.mark.parametrize("value", ("Owner", "OWNER"), ids=("Owner", "OWNER"))
def test_role_owner_in_other_letter_case_is_a_finding(project, call, value):
    """Green when written: the check already takes ``Owner`` and ``OWNER`` for the owner's trailer."""
    result, left, what = _role_owner_commit(project, call, value)
    check_support.assert_caught(result, support.README, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)
