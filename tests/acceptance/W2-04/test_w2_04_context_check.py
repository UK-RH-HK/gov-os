"""Rows W2-M228 and W2-L219 (S8; DEC-628, DEC-643): the context-reproducibility check's shapes.

A file of the ticket folder that the store holds no record of is named and keeps the check red, and when such files
are the only content the message says so (never "every ticket's context computation failed"); a ticket file whose
name ends otherwise than in lowercase ``.md`` is named, never unseen; two ticket files with one id are named as a
duplicate id, and the check is not green.

Red reasons, today: a README alone prints "unmeasured: every ticket's context computation failed"; a ``.MD`` or
``.markdown`` ticket is seen by nothing and the check is green without naming it; a duplicate id is not named as
one. The README beside a ticket passes today (it keeps the check red, DEC-628).
"""

from __future__ import annotations

import pytest

import w2_04_support as s

OK_TICKET = "TK-W204-OK"
FAILED_ALL = "every ticket's context computation failed"


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
