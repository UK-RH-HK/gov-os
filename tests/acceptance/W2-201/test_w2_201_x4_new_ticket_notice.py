"""W2-201 fix X4 (DEC-1219 (5)): a new ticket that is not a feature is flagged at the landing, never refused.

Planted projects through ``gov queue`` and its ``--dry-run`` (W2-202's and W2-115b's support; the planted runs in
``w2_201_x4_support``). In the notices run four branches land together: A adds a new ticket with no KPI line with a
verify and a blank body; B adds two features (a mapping line with a verify, a string line with ``Verify:``, each with a
body); C edits D's existing ticket file; E adds one new ticket per single missing part and one whose front matter does
not parse. Each notice is ``NEW_TICKET_NOT_FEATURE <id>: <what is missing>`` in the answer's ``ticket_notices``
(``{ticket, id, code, notice}``), the same in ``queue.json``, the dry run's answer and the landed ticket's close record,
and one line on stderr; every branch lands, with the exit code of a landing without it. The plain run's branch adds no
ticket file: ``ticket_notices`` is ``[]``.
"""

from __future__ import annotations

import pytest

import w2_201_x4_support as x4
from w2_201_x4_support import A, B, C, E, base, kit

LANDED = sorted(t.id for t in (A, B, C, E))


@pytest.fixture(scope="session")
def notices(tmp_path_factory):
    return x4.shared(tmp_path_factory, "notices", x4.build_notices)


@pytest.fixture(scope="session")
def plain(tmp_path_factory):
    return x4.shared(tmp_path_factory, "plain", x4.build_plain)


def _landed(landing):
    """The landing's answer: every branch landed, exit 0 (a landing without the notice lands them so)."""
    result = kit.answer(landing.run, kit.EXIT_LANDED)
    assert sorted(result.get("landed") or []) == LANDED, (
        f"the landing did not land every branch: {result.get('landed')!r}\n{kit.describe(landing.run)}")
    return result


def _notices(entries, where):
    return x4.by_id(entries, where)


def test_x4_the_landing_lands_every_branch_and_answers_the_notices(notices):
    result = _landed(notices)
    assert "ticket_notices" in result, f"the answer has no key ticket_notices: {sorted(result)}"
    got = _notices(result["ticket_notices"], "the answer")
    unread = got.pop(x4.UNREAD, None)
    assert got == x4.expected(), f"the answer's ticket_notices:\n{got}\nnot\n{x4.expected()}"
    assert unread is not None, f"no notice for {x4.UNREAD}, whose front matter does not parse"
    assert unread["ticket"] == E.id and unread["code"] == x4.CODE, f"the unreadable ticket's entry: {unread}"
    assert unread["notice"].startswith(f"{x4.CODE} {x4.UNREAD}: ") and x4.UNREADABLE in unread["notice"], (
        f"the unreadable ticket's notice does not say '{x4.UNREADABLE}': {unread['notice']!r}")


def test_x4_a_new_feature_and_an_edited_existing_ticket_give_no_notice(notices):
    result = _landed(notices)
    assert "ticket_notices" in result, f"the answer has no key ticket_notices: {sorted(result)}"
    got = _notices(result["ticket_notices"], "the answer")
    named = sorted(set(got) & {*x4.GOOD, x4.D.id})
    assert not named, f"a feature or an edited ticket file was flagged: {[got[i] for i in named]}"
    assert not [e for e in got.values() if e["ticket"] in (B.id, C.id)], (
        f"B (features only) or C (an edit) has a notice: {got}")


def test_x4_queue_json_holds_the_answer_s_ticket_notices(notices):
    result = _landed(notices)
    held = base.queue_record(notices, result)
    assert "ticket_notices" in held, f"queue.json has no key ticket_notices: {sorted(held)}"
    assert held["ticket_notices"] == result.get("ticket_notices"), (
        f"queue.json's ticket_notices {held['ticket_notices']!r} are not the answer's {result.get('ticket_notices')!r}")


def test_x4_the_dry_run_answers_the_same_notices_and_exit_code(notices):
    landed = _landed(notices)
    dry = notices.extra["dry"]
    assert not notices.extra["dry_moved"], "the dry run moved, committed or wrote something in the project"
    result = kit.answer(dry, kit.EXIT_LANDED)
    assert "ticket_notices" in result, f"the dry run's answer has no key ticket_notices: {sorted(result)}"
    assert _notices(result["ticket_notices"], "the dry run") == _notices(landed.get("ticket_notices"), "the landing"), (
        f"the dry run's ticket_notices differ from the landing's:\n{result['ticket_notices']}\n"
        f"{landed.get('ticket_notices')}")


@pytest.mark.parametrize("ticket", [A, E])
def test_x4_the_landed_ticket_s_close_record_holds_its_notices(notices, ticket):
    result = _landed(notices)
    front = kit.close_record(notices, result["head"], ticket.id)
    assert "ticket_notices" in front, f"{ticket.id}'s close record has no key ticket_notices: {sorted(front)}"
    mine = {i: e for i, e in _notices(result.get("ticket_notices"), "the answer").items() if e["ticket"] == ticket.id}
    assert mine, f"fixture: the answer names no notice of {ticket.id}"
    assert _notices(front["ticket_notices"], f"{ticket.id}'s close record") == mine, (
        f"{ticket.id}'s close record holds {front['ticket_notices']!r}, not its notices {mine!r}")


@pytest.mark.parametrize("ticket", [B, C])
def test_x4_a_close_record_with_no_new_ticket_flagged_holds_no_notice(notices, ticket):
    result = _landed(notices)
    front = kit.close_record(notices, result["head"], ticket.id)
    assert "ticket_notices" in result, f"the answer has no key ticket_notices: {sorted(result)}"
    assert not front.get("ticket_notices"), f"{ticket.id}'s close record holds {front.get('ticket_notices')!r}"


def test_x4_each_notice_is_one_line_on_stderr(notices):
    result = _landed(notices)
    assert "ticket_notices" in result, f"the answer has no key ticket_notices: {sorted(result)}"
    lines = notices.run["stderr"].splitlines()
    for entry in _notices(result["ticket_notices"], "the answer").values():
        found = [line for line in lines if entry["notice"] in line]
        assert len(found) == 1, (f"the notice {entry['notice']!r} is on {len(found)} stderr lines, not one\n"
                                 f"{kit.describe(notices.run)}")


def test_x4_a_branch_that_adds_no_ticket_file_answers_ticket_notices_empty(plain):
    result = kit.answer(plain.run, kit.EXIT_LANDED)
    assert result.get("landed") == [A.id], f"fixture: the plain landing landed {result.get('landed')!r}"
    assert result.get("ticket_notices", "<missing>") == [], (
        f"the answer's ticket_notices is {result.get('ticket_notices', '<missing>')!r}, not []")
    assert base.queue_record(plain, result).get("ticket_notices", "<missing>") == [], "queue.json's ticket_notices"
