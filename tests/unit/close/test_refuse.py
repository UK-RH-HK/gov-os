"""The one path of a refused close (DEC-455): counted, a repair ticket, the escalation at the third."""
from __future__ import annotations

import json

import pytest

from gov.cli.errors import GovError
from gov.close.command import EXIT_BLOCKED, EXIT_CHECK_FAILED, _count_path, _read_count, _refuse, run

TICKET = "T-0001"


def _refused(root, findings=("a finding",), **keys):
    with pytest.raises(GovError) as raised:
        _refuse(root, TICKET, "CHECK_FAILED", "refused", list(findings), **keys)
    return raised.value


def _count(root):
    return json.loads(_count_path(root, TICKET).read_text(encoding="utf-8"))


def test_a_refusal_is_counted_and_raised_with_its_finding(root):
    error = _refused(root)
    assert (error.code, error.exit_code) == ("CHECK_FAILED", EXIT_CHECK_FAILED)
    assert error.details["findings"] == ["a finding"]
    assert _count(root)["count"] == 1


def test_every_refusal_counts_whatever_its_finding(root):
    _refused(root, ["a"])
    _refused(root, ["b"])
    assert _count(root)["count"] == 2
    assert [o["failures"] for o in _count(root)["outcomes"]] == [["a"], ["b"]]


def test_a_refusal_opens_a_repair_ticket_and_names_it(root):
    error = _refused(root)
    repair = error.details["repair_ticket"]
    assert (root / ".tickets" / f"{repair}.md").is_file()


def test_the_third_refusal_writes_the_escalation_and_still_gives_its_finding(root):
    for _ in range(2):
        _refused(root)
    assert not (root / ".gov-runtime" / "escalations" / f"{TICKET}.json").exists()
    error = _refused(root, ["the third"])
    assert error.exit_code == EXIT_CHECK_FAILED and error.details["findings"] == ["the third"]
    package = json.loads((root / ".gov-runtime" / "escalations" / f"{TICKET}.json").read_text(encoding="utf-8"))
    assert len(package["outcomes"]) == 3 and package["reason"]
    assert set(package["options"]) == {"fix_differently", "narrow", "split", "defer", "delete", "continue"}


def test_the_exit_code_given_is_kept(root):
    assert _refused(root, exit_code=1).exit_code == 1


def test_the_owners_decision_stays_with_the_count(root):
    _count_path(root, TICKET).parent.mkdir(parents=True)
    _count_path(root, TICKET).write_text(json.dumps({"count": 0, "outcomes": [], "decision": "DEC-9"}))
    _refused(root)
    assert _count(root) | {"outcomes": []} == {"count": 1, "last_failures": ["a finding"], "outcomes": [],
                                               "decision": "DEC-9"}


def test_no_count_file_is_a_count_of_zero(root):
    assert _read_count(root, TICKET)["count"] == 0


@pytest.mark.parametrize("content", ["not json {{{", '{"count": ', "[1, 2, 3]", '{"count": "x"}',
                                     '{"count": true}', '{"count": 1, "outcomes": "x"}'])
def test_a_count_file_that_cannot_be_read_refuses(root, content):
    _count_path(root, TICKET).parent.mkdir(parents=True)
    _count_path(root, TICKET).write_text(content, encoding="utf-8")
    with pytest.raises(GovError) as raised:
        _read_count(root, TICKET)
    assert raised.value.code == "ITERATION_CORRUPT"
    with pytest.raises(GovError) as raised:
        _refuse(root, TICKET, "CHECK_FAILED", "refused", ["a finding"])
    assert raised.value.code == "ITERATION_CORRUPT"


class _Args:
    ticket = TICKET
    timeout = None
    disposition = None
    owner_decision = None


def test_after_three_refusals_the_next_close_is_blocked_before_anything_runs(root, monkeypatch):
    for _ in range(3):
        _refused(root)
    monkeypatch.setattr("gov.close.command._ticket_commits", lambda *a: pytest.fail("the blocked close ran"))
    with pytest.raises(GovError) as raised:
        run(root, _Args(), {})
    assert (raised.value.code, raised.value.exit_code) == ("ESCALATION_BLOCKED", EXIT_BLOCKED)
    assert len(raised.value.details["outcomes"]) == 1
    assert _count(root)["count"] == 3


def test_an_owner_decision_without_an_escalation_is_refused(root):
    args = _Args()
    args.owner_decision = "DEC-1"
    with pytest.raises(GovError) as raised:
        run(root, args, {})
    assert raised.value.code == "INVALID_DECISION"
