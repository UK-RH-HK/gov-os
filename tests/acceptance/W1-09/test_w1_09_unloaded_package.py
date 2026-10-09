"""The follow-up after W1-41, piece 10: a constraining decision package that the store could not load blocks
READY (DEC-544, DEC-569).

DEC-544: "the READY rule treats a constraining package the store could not load as blocking." Until now such
a file blocked nothing (this suite's residual "packages that do not load block nothing"; W1-32's residual "a
ticket constrained by a package whose record could not load is still listed ``ready``").

The file is in the commit and the store holds no record of it: a required key is absent or is not text, or
the frontmatter cannot be read at all. A ticket it names under ``constrains`` is not READY, and its reasons
name the file. Tickets it does not name stay READY (CAP-34.e).

**Proposed (README, "A package the store could not load").** The reason is written
``DECISION_NOT_LOADED: <the file's path>``, one for each such file, beside the codes of today. A file whose
frontmatter cannot be read far enough to say which tickets it constrains holds every ticket (the stricter
reading; package P-10.2).
"""

from __future__ import annotations

import pytest

import w1_09_support as support

A, B = "TST-a001", "TST-a002"
PACKAGE_REL = "spec/gates/DP-0001.md"
NOT_LOADED = "DECISION_NOT_LOADED"   # proposed


def _package(*lines):
    return "---\n" + "\n".join(lines) + "\n---\n\n# DP-0001\n\nA question for the owner.\n"


HEAD_KEYS = ("state_class: AUTHORITATIVE", "title: A question")
CONSTRAINS = ("constrains:", f"- {A}")

# The file names the ticket A under `constrains`, and the store's load takes no record of it.
NAMES_THE_TICKET = {
    "no status": _package("id: DP-0001", "type: decision-package", *HEAD_KEYS, *CONSTRAINS),
    "a status that is not text": _package("id: DP-0001", "type: decision-package", "status:", "- PROPOSED",
                                          *HEAD_KEYS, *CONSTRAINS),
    "no type": _package("id: DP-0001", "status: PROPOSED", *HEAD_KEYS, *CONSTRAINS),
    "no id": _package("type: decision-package", "status: PROPOSED", *HEAD_KEYS, *CONSTRAINS),
}
# Nothing of the frontmatter can be read, the tickets it constrains included.
NOT_READABLE = {
    "not valid YAML": _package("id: DP-0001", "type: decision-package", "status: PROPOSED", "title: [not closed",
                               *CONSTRAINS),
    "a frontmatter that is not closed": "---\nid: DP-0001\ntype: decision-package\nstatus: PROPOSED\n"
                                        f"constrains:\n- {A}\n\n# DP-0001\n\nA question for the owner.\n",
}


def _queue(project):
    """``(ready, ticket id -> reasons)`` of one settled state; the reasons as the rule gives them."""
    ready = project.ready()
    blocked = project.api.call("blocked", project.root)
    assert isinstance(blocked, dict) and all(isinstance(reasons, list) for reasons in blocked.values()), \
        f"blocked did not return a map of ticket id to reasons: {blocked!r}"
    return ready, blocked


def _fixture_holds(project):
    """The store has no record of the package file: the case would otherwise hold today's rule."""
    records = project.api.call("records", project.root, module="gov.records")
    assert PACKAGE_REL not in [record["path"] for record in records], "the fixture is wrong: the package loaded"


def _assert_held_by_the_file(blocked, ticket):
    reasons = blocked.get(ticket)
    assert reasons, f"{ticket} is in neither list: {blocked}"
    assert f"{NOT_LOADED}: {PACKAGE_REL}" in reasons, \
        f"the reasons of {ticket} do not name the package the store could not load: {reasons}"
    others = sorted(set(reasons) - {f"{NOT_LOADED}: {PACKAGE_REL}"})
    assert not others, f"{ticket} is held by more than the package: {others}"


@pytest.mark.parametrize("shape", sorted(NAMES_THE_TICKET))
def test_a_package_the_store_could_not_load_blocks_the_ticket_it_names(shape, project):
    project.ticket(A, "W9-01")
    project.ticket(B, "W9-02")
    support.write(project.root, PACKAGE_REL, NAMES_THE_TICKET[shape])

    ready, blocked = _queue(project)

    _fixture_holds(project)
    assert A not in ready, f"a ticket constrained by a package the store could not load ({shape}) is READY"
    _assert_held_by_the_file(blocked, A)
    assert ready == [B] and B not in blocked, \
        f"a ticket the package does not name is held with it: ready {ready}, blocked {blocked}"


@pytest.mark.parametrize("shape", sorted(NOT_READABLE))
def test_a_package_whose_frontmatter_cannot_be_read_holds_every_ticket(shape, project):
    """The stricter reading: which tickets the file constrains is not known, so none is READY beside it."""
    project.ticket(A, "W9-01")
    project.ticket(B, "W9-02")
    support.write(project.root, PACKAGE_REL, NOT_READABLE[shape])

    ready, blocked = _queue(project)

    _fixture_holds(project)
    assert ready == [], f"tickets are READY beside a file that may be an open package ({shape}): {ready}"
    _assert_held_by_the_file(blocked, A)
    _assert_held_by_the_file(blocked, B)


def test_the_ticket_is_ready_again_when_the_package_loads_and_is_closed(project):
    project.ticket(A, "W9-01")
    support.write(project.root, PACKAGE_REL, NAMES_THE_TICKET["no status"])
    held, _ = _queue(project)
    project.record(PACKAGE_REL, "DP-0001", "decision-package", "ACCEPTED", constrains=[A])

    ready, blocked = _queue(project)

    assert held == [], "the fixture is wrong: the ticket was READY while the package could not load"
    assert (ready, blocked) == ([A], {}), f"a package that loads and is closed still holds: {blocked}"


def test_a_package_that_loads_and_is_open_gives_the_reason_of_today(project):
    """Green today: a loaded, open package is DECISION_OPEN, with no file named."""
    project.ticket(A, "W9-01")
    project.record(PACKAGE_REL, "DP-0001", "decision-package", "PROPOSED", constrains=[A])

    ready, blocked = _queue(project)

    assert (ready, blocked) == ([], {A: [support.DECISION_OPEN]})


def test_a_package_that_loads_and_is_closed_does_not_block(project):
    """Green today, and it stays: ACCEPTED, REJECTED and SUPERSEDED packages hold nothing."""
    project.ticket(A, "W9-01")
    project.ticket(B, "W9-02")
    project.record(PACKAGE_REL, "DP-0001", "decision-package", "ACCEPTED", constrains=[A])
    project.record("spec/gates/DP-0002.md", "DP-0002", "decision-package", "REJECTED", constrains=[A, B])
    project.record("spec/gates/DP-0003.md", "DP-0003", "decision-package", "SUPERSEDED", constrains=[B])

    assert _queue(project) == ([A, B], {})


def test_a_file_the_store_could_not_load_that_constrains_nothing_blocks_nothing(project):
    """Green today, and it stays: a file with a readable frontmatter, a missing required key and no
    ``constrains`` (this repository's charter is one) is no package of any ticket."""
    project.ticket(A, "W9-01")
    support.write(project.root, "docs/charter.md", "---\nid: CHARTER\nstatus: ACTIVE\ntitle: A charter\n---\n\nText.\n")
    support.write(project.root, "docs/other.md", _package("id: DP-0009", "type: decision-package", *HEAD_KEYS,
                                                          "constrains: []"))

    assert _queue(project) == ([A], {})
