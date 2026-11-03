"""Rows W2-M228 and W2-L219 (S8; DEC-628, DEC-643): the context-reproducibility check's shapes.

A file of the ticket folder that the store holds no record of is named and keeps the check red, and when such files
are the only content the message says so (never "every ticket's context computation failed"); a ticket file whose
name ends otherwise than in lowercase ``.md`` is named, never unseen; two ticket files with one id are named as a
duplicate id, and the check is not green.

Addendum 3's S8a (F3; DEC-1025 item 2): when the check computed at least one ticket's context and every one it
computed refused over the ceiling, no packet was built twice. The check is then not green: it prints a line
beginning ``unmeasured:`` that says no packet was built, keeps each refusal's ``REFUSED:`` line, and exits non-zero.
A tree where at least one packet was built twice alike keeps its result, green with its ``REFUSED:`` lines.

Red reasons, today: a README alone prints "unmeasured: every ticket's context computation failed"; a ``.MD`` or
``.markdown`` ticket is seen by nothing and the check is green without naming it; a duplicate id is not named as
one. The README beside a ticket passes today (it keeps the check red, DEC-628). Tickets over the ceiling never
refuse today, so the check is green with no ``REFUSED:`` line and no ``unmeasured:`` line.
"""

from __future__ import annotations

import re

import pytest

import w2_04_support as s

OK_TICKET = "TK-W204-OK"
FAILED_ALL = "every ticket's context computation failed"
# A charter of about 35,000 tokens: a ticket that cites it is over the default ceiling by its mandatory inputs alone.
BIG_ID, BIG_REL = "CHARTER-W204-BIG", "docs/charter/big.md"
BIG_TEXT = " ".join(f"Clause {n}: every agent sees one packet under its ceiling." for n in range(2400))
OVER_TICKETS = ("TK-W204-OVER-A", "TK-W204-OVER-B")
# "Says no packet was built" (R11): the line names a packet with a negation.
NO_PACKET = re.compile(r"\b(no|none|not)\b.*\bpackets?\b|\bpackets?\b.*\b(none|not)\b", re.IGNORECASE)


def _project(api, root, files):
    base = {"docs/charter/charter.md": s.record(s.CHARTER_ID, "charter", "ACTIVE", s.CHARTER_TEXT)}
    project = s.build_project(root, {**base, **files})
    api.build(project.root, index=False)
    return project


def test_an_unheld_file_alone_is_named_and_the_message_is_accurate(api, tmp_path):
    project = _project(api, tmp_path / "repo", {".tickets/README.md": "# Tickets\n\nThe project's tickets.\n"})
    answer = api.context_check(project.root)
    assert answer.returncode != 0, f"a ticket folder holding only an unheld file is green\n{answer.describe()}"
    assert "README.md" in answer.stdout, f"the unheld file is not named\n{answer.describe()}"
    assert FAILED_ALL not in answer.stdout, \
        f"no ticket's computation ran, yet the check says every one failed\n{answer.describe()}"


def test_an_unheld_file_beside_a_ticket_keeps_the_check_red(api, tmp_path):
    """Passes today (DEC-628: it fails closed)."""
    project = _project(api, tmp_path / "repo", {
        ".tickets/README.md": "# Tickets\n\nThe project's tickets.\n",
        f".tickets/{OK_TICKET}.md": s.ticket(OK_TICKET, "A ticket that is measured", [s.CHARTER_ID])})
    answer = api.context_check(project.root)
    assert answer.returncode != 0 and "README.md" in answer.stdout, answer.describe()


@pytest.mark.parametrize("name", ("TK-W204-ODD.MD", "TK-W204-ODD.markdown"))
def test_a_ticket_file_with_another_ending_is_named_never_unseen(api, tmp_path, name):
    project = _project(api, tmp_path / "repo", {
        f".tickets/{OK_TICKET}.md": s.ticket(OK_TICKET, "A ticket that is measured", [s.CHARTER_ID]),
        f".tickets/{name}": s.ticket("TK-W204-ODD", "A ticket with another ending", [s.CHARTER_ID])})
    answer = api.context_check(project.root)
    assert name in answer.stdout or "TK-W204-ODD" in answer.stdout, \
        f"the ticket file {name} is seen by nothing: the check does not name it\n{answer.describe()}"


def test_two_ticket_files_with_one_id_are_named_as_a_duplicate_and_not_green(api, tmp_path):
    duplicate = "TK-W204-DUP"
    project = _project(api, tmp_path / "repo", {
        f".tickets/{duplicate}.md": s.ticket(duplicate, "The first copy", [s.CHARTER_ID]),
        f".tickets/{duplicate}-copy.md": s.ticket(duplicate, "The copied file", [s.CHARTER_ID]),
        f".tickets/{OK_TICKET}.md": s.ticket(OK_TICKET, "A ticket that is measured", [s.CHARTER_ID])})
    answer = api.context_check(project.root)
    assert answer.returncode != 0, f"two ticket files with one id, and the check is green\n{answer.describe()}"
    lines = [line for line in answer.stdout.splitlines() if duplicate in line]
    assert any("duplicate" in line.lower() for line in lines), \
        f"the id {duplicate} is not named as a duplicate id\n{answer.describe()}"


# --------------------------------------------------------------------------
# Addendum 3's S8a (F3; DEC-1025 item 2): the check when no packet is built
# --------------------------------------------------------------------------

def _over(ticket_id):
    return s.ticket(ticket_id, f"A ticket over the ceiling, {ticket_id}", [BIG_ID])


def _refused(stdout, ticket_id):
    """The lines of the check's output that carry ``REFUSED:`` and name ``ticket_id``."""
    return [line for line in stdout.splitlines() if "REFUSED:" in line and ticket_id in line]


def _unmeasured(stdout):
    return [line for line in stdout.splitlines() if line.startswith("unmeasured:")]


def test_when_every_ticket_refuses_over_the_ceiling_the_check_is_unmeasured_never_green(api, tmp_path):
    """Addendum 3's S8a. Two tickets, each over the default ceiling by its mandatory inputs alone: every computation
    refuses, so no packet was built twice. Exit non-zero; a line beginning ``unmeasured:`` says no packet was built;
    a ``REFUSED:`` line names each ticket."""
    assert s.tokens(BIG_TEXT) > s.DEFAULT_CEILING, "the fixture is wrong: the charter fits the default ceiling"
    project = _project(api, tmp_path / "repo", {BIG_REL: s.record(BIG_ID, "charter", "ACTIVE", BIG_TEXT),
                                                **{f".tickets/{tid}.md": _over(tid) for tid in OVER_TICKETS}})

    answer = api.context_check(project.root)

    unmeasured = _unmeasured(answer.stdout)
    assert unmeasured, (f"every ticket refuses over the ceiling, so no packet was built, yet no line begins "
                        f"`unmeasured:`\n{answer.describe()}")
    assert any(NO_PACKET.search(line) for line in unmeasured), \
        f"the `unmeasured:` line does not say no packet was built: {unmeasured}\n{answer.describe()}"
    for ticket_id in OVER_TICKETS:
        assert _refused(answer.stdout, ticket_id), \
            f"{ticket_id} refuses over the ceiling, and no `REFUSED:` line names it\n{answer.describe()}"
    assert answer.returncode != 0, f"no packet was built, yet the check exits 0 (green)\n{answer.describe()}"


def test_when_one_ticket_refuses_and_one_fits_the_check_stays_green_with_its_refused_line(api, tmp_path):
    """Addendum 3's S8a, what it keeps: one packet built twice alike keeps the check green (exit 0), with a
    ``REFUSED:`` line for the ticket over the ceiling, none for the one that fits, and no ``unmeasured:`` line."""
    over = OVER_TICKETS[0]
    project = _project(api, tmp_path / "repo", {
        BIG_REL: s.record(BIG_ID, "charter", "ACTIVE", BIG_TEXT), f".tickets/{over}.md": _over(over),
        f".tickets/{OK_TICKET}.md": s.ticket(OK_TICKET, "A ticket that is measured", [s.CHARTER_ID])})

    answer = api.context_check(project.root)

    assert _refused(answer.stdout, over), \
        f"{over} refuses over the ceiling, and no `REFUSED:` line names it\n{answer.describe()}"
    assert not _refused(answer.stdout, OK_TICKET), f"{OK_TICKET} fits, yet a `REFUSED:` line names it\n" \
                                                   f"{answer.describe()}"
    assert not _unmeasured(answer.stdout), \
        f"one packet was built twice alike, yet the check says unmeasured\n{answer.describe()}"
    assert answer.returncode == 0, \
        f"one packet was built twice alike and one ticket refused: the check is not green\n{answer.describe()}"
