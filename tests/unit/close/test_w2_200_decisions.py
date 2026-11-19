"""Builder tests for the decisions a close records from the ticket's own sources (W2-200 S3, S5, S6, F1; DEC-1214 M1).

Regression evidence only: each case commits a small register in a temporary repository, as ``gov.util.register.read``
reads it from ``HEAD``, and asks ``gov.close.decisions`` what a ticket's frontmatter cites.
"""
from __future__ import annotations

import hashlib

import pytest

from gov.cli.errors import GovError
from gov.close import decisions

from conftest import TICKET

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
    root = _project(repo, _entry(9) + _entry(10) + _entry(11) + _entry(12))
    front = {"sources": ["DEC-10", "CAP-1", "W2-9", "docs/a/DEC-9x.md", "DEC-10"], "decisions": ["DEC-9", "DEC-11"],
             "kpis": {"success": ["S1 a line [DEC-12; DEC-10]"], "failure": ["F1 never [DEC-11]"]}}
    found = decisions.decisions_of(root, TICKET, front)
    assert found["applied"] == ["DEC-9", "DEC-10", "DEC-11", "DEC-12"]
    assert found["not_standing"] == [] and found["unresolved"] == []
    assert found["inputs"] == [{"id": f"DEC-{n}", "hash": _span_hash(root, n)} for n in (9, 10, 11, 12)]


def test_a_kpi_list_is_read_as_kpi_lines(repo):
    root = _project(repo, _entry(10))
    assert decisions.decisions_of(root, TICKET, {"kpis": ["a line [DEC-10]"]})["applied"] == ["DEC-10"]


def test_a_decision_that_no_longer_stands_is_listed_with_its_state_and_never_applied(repo):
    root = _project(repo, _entry(20) + _entry(21, "SUPERSEDED by DEC-20") + _entry(22, "RETIRED")
                    + _entry(23, "REJECTED") + _entry(24) + _entry(25, more=" · **Supersedes:** DEC-24")
                    + _entry(26, more="\n- **Tags:** domain: close · scope: repository · lands in: none · done"))
    front = {"sources": [f"DEC-{n}" for n in (26, 24, 23, 22, 21, 20)]}
    found = decisions.decisions_of(root, TICKET, front)
    assert found["applied"] == ["DEC-20", "DEC-26"]  # the done-tagged entry stands
    assert found["not_standing"] == [{"id": "DEC-21", "status": "SUPERSEDED"}, {"id": "DEC-22", "status": "RETIRED"},
                                     {"id": "DEC-23", "status": "REJECTED"}, {"id": "DEC-24", "status": "SUPERSEDED"}]
    assert [item["id"] for item in found["inputs"]] == found["applied"]


def test_a_decision_of_sources_or_decisions_the_register_lacks_refuses_naming_each(repo):
    root = _project(repo, _entry(10))
    with pytest.raises(GovError) as refused:
        decisions.decisions_of(root, TICKET, {"sources": ["DEC-99", "DEC-10"], "decisions": ["DEC-98"]})
    assert refused.value.code == decisions.NOT_FOUND == "DECISION_NOT_FOUND"
    assert refused.value.details["missing"] == ["DEC-98", "DEC-99"] and refused.value.details["ticket"] == TICKET
    assert TICKET in refused.value.message and "DEC-98" in refused.value.message and "DEC-99" in refused.value.message


def test_a_decision_only_in_a_kpi_line_the_register_lacks_is_unresolved(repo):
    root = _project(repo, _entry(10))
    found = decisions.decisions_of(root, TICKET, {"sources": ["DEC-10"], "kpis": {"success": ["S1 [DEC-99]"]}})
    assert (found["applied"], found["unresolved"]) == (["DEC-10"], ["DEC-99"])
    assert [item["id"] for item in found["inputs"]] == ["DEC-10"]


def test_without_a_register_nothing_refuses_and_every_id_is_unresolved(repo):
    root = _project(repo, "", register=False)
    found = decisions.decisions_of(root, TICKET, {"sources": ["DEC-11", "DEC-2"], "kpis": {"failure": ["F [DEC-5]"]}})
    assert found == {"applied": [], "not_standing": [], "unresolved": ["DEC-2", "DEC-5", "DEC-11"], "inputs": []}


def test_a_ticket_that_cites_no_decision_applies_none(repo):
    root = _project(repo, _entry(10))
    assert decisions.decisions_of(root, TICKET, {"sources": ["CAP-1"]}) == \
        {"applied": [], "not_standing": [], "unresolved": [], "inputs": []}


def test_the_record_fields_hold_the_tickets_own_entry_first_and_no_packet_hash(repo):
    root = _project(repo, _entry(10) + _entry(11, "RETIRED"))
    ticket = root / ".tickets" / f"{TICKET}.md"
    ticket.parent.mkdir()
    ticket.write_text("---\nid: T-0001\n---\n", encoding="utf-8")
    fields = decisions.record_fields(root, TICKET, {"sources": ["DEC-10", "DEC-11"], "kpis": ["x [DEC-77]"]})
    own = {"id": TICKET, "hash": "sha256:" + hashlib.sha256(ticket.read_bytes()).hexdigest()}
    assert fields == {"inputs": [own, {"id": "DEC-10", "hash": _span_hash(root, 10)}],
                      "decisions_applied": ["DEC-10"],
                      "decisions_not_standing": [{"id": "DEC-11", "status": "RETIRED"}],
                      "decisions_unresolved": ["DEC-77"]}
