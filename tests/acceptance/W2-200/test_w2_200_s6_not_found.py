"""S6 (as the CTO amended it at the land): a decision the register does not hold is recorded, never refused.

Five fixtures: DEC-999 in ``sources``, DEC-997 in ``decisions`` and DEC-998 in a KPI line, held by no register
(``s6_unresolved``); DEC-199 only inside a KPI line (``s6_kpi_only``); an archived register named by the path map's
``decision_register_archive`` beside the register (``s6_archive``); a path map that names no register
(``s6_no_register``, a register file at the usual path that nothing names); a ticket that cites no decision
(``s6_no_citation``).
"""

from __future__ import annotations

import w2_200_support as s

REFUSAL_OF_BEFORE = "DECISION_NOT_FOUND"


def _record(world) -> dict:
    s.closed(world.run)
    return world.project.record()


def test_s6_an_id_no_register_holds_in_sources_decisions_or_a_kpi_line_is_unresolved_and_the_close_goes_on(s6_unresolved):
    record = _record(s6_unresolved)
    unresolved = record.get("decisions_unresolved")
    assert isinstance(unresolved, list) and sorted(unresolved) == sorted(s.S6_MISSING), \
        f"decisions_unresolved: {unresolved!r}, not {s.S6_MISSING} (sources, decisions, a KPI line)"
    assert record.get("decisions_applied") == ["DEC-110"], f"decisions_applied: {record.get('decisions_applied')!r}"
    assert record.get("decisions_not_standing") == [], f"decisions_not_standing: {record.get('decisions_not_standing')!r}"
    assert set(s.input_hashes(record)) == {s.TICKET, "DEC-110"}, f"inputs: {record.get('inputs')!r}"


def test_s6_the_close_of_a_ticket_citing_an_unknown_id_is_whole_and_no_output_names_the_refusal(s6_unresolved):
    project, run = s6_unresolved.project, s6_unresolved.run
    assert REFUSAL_OF_BEFORE not in run.both, f"the close's output names {REFUSAL_OF_BEFORE}\n{run.describe()}"
    s.closed(run)
    assert project.record_path().is_file(), "the close wrote no close record"
    status = s.front_of((project.root / f".tickets/{s.TICKET}.md").read_text(encoding="utf-8")).get("status")
    assert status == "closed", f"the ticket's status is {status!r} after the close"
    repairs = [path.name for path in project.repair_tickets()]
    assert not repairs, f"the close opened a repair ticket for the unknown ids: {repairs}"


def test_s6_an_id_only_in_a_kpi_line_and_not_in_the_register_is_unresolved_and_the_close_passes(s6_kpi_only):
    s.closed(s6_kpi_only.run)
    record = s6_kpi_only.project.record()
    assert record.get("decisions_unresolved") == [s.S6_KPI_ONLY], f"decisions_unresolved: {record.get('decisions_unresolved')!r}"
    assert record.get("decisions_applied") == ["DEC-110"], f"decisions_applied: {record.get('decisions_applied')!r}"


def test_s6_a_decision_only_the_archived_register_holds_is_not_standing_as_archived_and_never_applied(s6_archive):
    record = _record(s6_archive)
    not_standing = record.get("decisions_not_standing")
    assert isinstance(not_standing, list) and {"id": "DEC-150", "status": "ARCHIVED"} in not_standing, \
        f"decisions_not_standing: {not_standing!r}, without DEC-150 as ARCHIVED"
    assert "DEC-150" not in (record.get("decisions_applied") or []), f"decisions_applied: {record.get('decisions_applied')!r}"
    assert "DEC-150" not in (record.get("decisions_unresolved") or []), \
        f"decisions_unresolved: {record.get('decisions_unresolved')!r}"
    assert "DEC-150" not in s.input_hashes(record), f"inputs: {record.get('inputs')!r}"


def test_s6_an_archived_decision_is_archived_whatever_its_own_status_line_and_wherever_it_is_cited(s6_archive):
    """DEC-151's own status line says SUPERSEDED, DEC-152 has none and is cited from a KPI line: each is history,
    listed as ARCHIVED, sorted by number with DEC-150."""
    record = _record(s6_archive)
    assert record.get("decisions_not_standing") == s.S6_ARCHIVED, \
        f"decisions_not_standing: {record.get('decisions_not_standing')!r}"


def test_s6_beside_an_archive_the_register_s_entry_is_applied_and_an_id_in_neither_is_unresolved(s6_archive):
    """DEC-110 is in both files (a kept entry): it stands by the register, with the hash of the register's span."""
    record = _record(s6_archive)
    assert record.get("decisions_applied") == ["DEC-110"], f"decisions_applied: {record.get('decisions_applied')!r}"
    assert s.input_hashes(record).get("DEC-110") in s.span_hashes(s.PLAIN_REGISTER, ["DEC-110"])["DEC-110"], \
        f"DEC-110's hash is not that of its span of the register: {record.get('inputs')!r}"
    assert record.get("decisions_unresolved") == [s.S6_IN_NEITHER], \
        f"decisions_unresolved: {record.get('decisions_unresolved')!r}"


def test_s6_where_the_path_map_names_no_register_every_cited_id_is_unresolved(s6_no_register):
    s.closed(s6_no_register.run)
    record = s6_no_register.project.record()
    assert record.get("decisions_applied") == [], f"decisions_applied: {record.get('decisions_applied')!r}"
    assert sorted(record.get("decisions_unresolved") or []) == sorted(s.S6_UNNAMED), \
        f"decisions_unresolved: {record.get('decisions_unresolved')!r}"
    assert set(s.input_hashes(record)) == {s.TICKET}, f"inputs: {record.get('inputs')!r}"


def test_s6_a_ticket_citing_no_decision_closes_with_empty_lists(s6_no_citation):
    s.closed(s6_no_citation.run)
    record = s6_no_citation.project.record()
    for key in ("decisions_applied", "decisions_not_standing", "decisions_unresolved"):
        assert record.get(key) == [], f"{key} is {record.get(key)!r}, not []"
    assert record.get("inputs") == [{"id": s.TICKET, "hash": s.ticket_hash(s6_no_citation.project, s6_no_citation.measured)}], record.get("inputs")
