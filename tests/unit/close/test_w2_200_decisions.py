"""Builder tests for the decisions a close records from the ticket's own sources (W2-200 S3, S5, S6, F1; DEC-1214 M1).

Regression evidence only: each case commits a small register in a temporary repository, as ``gov.util.register.read``
reads it from ``HEAD``, and asks ``gov.close.decisions`` what a ticket's frontmatter cites.
"""
from __future__ import annotations

import hashlib

from gov.close import decisions

TICKET = "T-0001"

PATH_MAP = "governance/project/path-map.yaml"
REGISTER = "docs/REG.md"


def _entry(number: int, status: str = "ACCEPTED", more: str = "") -> str:
    return f"### DEC-{number} — entry {number}\n- **Status:** {status}{more}\n- **Decision:** text {number}\n\n"


def _project(repo, entries: str, register: bool = True):
    files = {PATH_MAP: f"decision_register: {REGISTER}\n" if register else "namespaces: {}\n"}
    if register:
        files[REGISTER] = "# Register\n\n" + entries
    repo.commit("register", files=files)
    return repo.root


def _span_hash(root, number: int) -> str:
    from gov.util import register
    span = next(e["span"] for e in register.read(root)["entries"] if e["id"] == f"DEC-{number}")
    return "sha256:" + hashlib.sha256(span.encode("utf-8")).hexdigest()


def test_ids_come_from_sources_decisions_and_kpi_lines_each_once_sorted_by_number(repo):
    root = _project(repo, _entry(109) + _entry(110) + _entry(111) + _entry(112))
    front = {"sources": ["DEC-110", "CAP-1", "W2-9", "docs/a/DEC-9x.md", "DEC-110"], "decisions": ["DEC-109", "DEC-111"],
             "kpis": {"success": ["S1 a line [DEC-112; DEC-110]"], "failure": ["F1 never [DEC-111]"]}}
    found = decisions.decisions_of(root, TICKET, front)
    assert found["applied"] == ["DEC-109", "DEC-110", "DEC-111", "DEC-112"]
    assert found["not_standing"] == [] and found["unresolved"] == []
    assert found["inputs"] == [{"id": f"DEC-{n}", "hash": _span_hash(root, n)} for n in (109, 110, 111, 112)]


def test_a_kpi_list_is_read_as_kpi_lines(repo):
    root = _project(repo, _entry(110))
    assert decisions.decisions_of(root, TICKET, {"kpis": ["a line [DEC-110]"]})["applied"] == ["DEC-110"]


def test_a_decision_that_no_longer_stands_is_listed_with_its_state_and_never_applied(repo):
    root = _project(repo, _entry(120) + _entry(121, "SUPERSEDED by DEC-120") + _entry(122, "RETIRED")
                    + _entry(123, "REJECTED") + _entry(124) + _entry(125, more=" · **Supersedes:** DEC-124")
                    + _entry(126, more="\n- **Tags:** domain: close · scope: repository · lands in: none · done"))
    front = {"sources": [f"DEC-{n}" for n in (126, 124, 123, 122, 121, 120)]}
    found = decisions.decisions_of(root, TICKET, front)
    assert found["applied"] == ["DEC-120", "DEC-126"]  # the done-tagged entry stands
    assert found["not_standing"] == [{"id": "DEC-121", "status": "SUPERSEDED"}, {"id": "DEC-122", "status": "RETIRED"},
                                     {"id": "DEC-123", "status": "REJECTED"}, {"id": "DEC-124", "status": "SUPERSEDED"}]
    assert [item["id"] for item in found["inputs"]] == found["applied"]


def test_a_decision_of_sources_or_decisions_the_register_lacks_is_unresolved_and_nothing_refuses(repo):
    root = _project(repo, _entry(110))
    found = decisions.decisions_of(root, TICKET, {"sources": ["DEC-999", "DEC-110"], "decisions": ["DEC-998"]})
    assert found["applied"] == ["DEC-110"] and found["unresolved"] == ["DEC-998", "DEC-999"]
    assert found["not_standing"] == [] and [item["id"] for item in found["inputs"]] == ["DEC-110"]
    assert not hasattr(decisions, "NOT_FOUND")


def test_a_decision_only_in_a_kpi_line_the_register_lacks_is_unresolved(repo):
    root = _project(repo, _entry(110))
    found = decisions.decisions_of(root, TICKET, {"sources": ["DEC-110"], "kpis": {"success": ["S1 [DEC-999]"]}})
    assert (found["applied"], found["unresolved"]) == (["DEC-110"], ["DEC-999"])
    assert [item["id"] for item in found["inputs"]] == ["DEC-110"]


def test_without_a_register_nothing_refuses_and_every_id_is_unresolved(repo):
    root = _project(repo, "", register=False)
    front = {"sources": ["DEC-111", "DEC-102"], "kpis": {"failure": ["F [DEC-105]"]}}
    found = decisions.decisions_of(root, TICKET, front)
    assert found == {"applied": [], "not_standing": [], "unresolved": ["DEC-102", "DEC-105", "DEC-111"], "inputs": []}


def test_a_ticket_that_cites_no_decision_applies_none(repo):
    root = _project(repo, _entry(110))
    assert decisions.decisions_of(root, TICKET, {"sources": ["CAP-1"]}) == \
        {"applied": [], "not_standing": [], "unresolved": [], "inputs": []}


def test_the_record_fields_hold_the_tickets_own_entry_first_and_no_packet_hash(repo):
    root = _project(repo, _entry(110) + _entry(111, "RETIRED"))
    ticket = root / ".tickets" / f"{TICKET}.md"
    ticket.parent.mkdir()
    ticket.write_text("---\nid: T-0001\n---\n", encoding="utf-8")
    fields = decisions.record_fields(root, TICKET, {"sources": ["DEC-110", "DEC-111"], "kpis": ["x [DEC-977]"]})
    own = {"id": TICKET, "hash": "sha256:" + hashlib.sha256(ticket.read_bytes()).hexdigest()}
    assert fields == {"inputs": [own, {"id": "DEC-110", "hash": _span_hash(root, 110)}],
                      "decisions_applied": ["DEC-110"],
                      "decisions_not_standing": [{"id": "DEC-111", "status": "RETIRED"}],
                      "decisions_unresolved": ["DEC-977"]}
