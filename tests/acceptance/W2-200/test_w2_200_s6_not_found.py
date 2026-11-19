"""S6: a decision the register does not hold.

Four fixtures: DEC-199 in ``sources`` and DEC-198 in ``decisions``, neither in the register (``s6_refused``); DEC-199
only inside a KPI line (``s6_kpi_only``); a path map that names no register (``s6_no_register``, a register file at the
usual path that nothing names); a ticket that cites no decision (``s6_no_citation``).
"""

from __future__ import annotations

import json

import w2_200_support as s


def test_s6_a_missing_id_in_sources_or_decisions_refuses_decision_not_found_naming_ticket_and_ids(s6_refused):
    run = s6_refused.run
    error = run.error()
    assert error.get("code") == "DECISION_NOT_FOUND", f"the refusal is {error.get('code')!r}\n{run.describe()}"
    said = error.get("message", "") + json.dumps(error.get("details", {}))
    for name in (s.TICKET, *s.S6_MISSING):
        assert name in said, f"the refusal does not name {name}\n{run.describe()}"
    assert "DEC-110" not in error.get("message", ""), f"the refusal names a decision the register holds\n{run.describe()}"


def test_s6_the_refusal_exits_as_a_close_refusal_of_its_kind(s6_refused):
    reference = s6_refused.unknown
    assert reference.error().get("code") == "TICKET_UNKNOWN", reference.describe()
    assert s6_refused.run.code == reference.code != 0, \
        f"exit {s6_refused.run.code}, not that of the close's TICKET_UNKNOWN refusal ({reference.code})"


def test_s6_the_refusal_writes_nothing(s6_refused):
    project, before = s6_refused.project, s6_refused.before
    assert s6_refused.run.envelope()["ok"] is False, s6_refused.run.describe()
    assert project.head() == before.head, "the refused close made a commit"
    assert project.status() == before.status, f"git status changed:\n{before.status}\n---\n{project.status()}"
    after = s.tree_files(project.root)
    changed = sorted(set(after.items()) ^ set(before.files.items()))
    assert not changed, f"files changed outside .git and .gov-runtime: {sorted({rel for rel, _ in changed})}"
    assert not project.record_path().exists(), "a close record was written"
    assert project.checkpoints() == before.checkpoints, "a checkpoint was written"
    assert project.iteration_file().exists() == before.iteration, "the refusal changed the ticket's iteration count"


def test_s6_an_id_only_in_a_kpi_line_and_not_in_the_register_is_unresolved_and_the_close_passes(s6_kpi_only):
    s.closed(s6_kpi_only.run)
    record = s6_kpi_only.project.record()
    assert record.get("decisions_unresolved") == [s.S6_KPI_ONLY], f"decisions_unresolved: {record.get('decisions_unresolved')!r}"
    assert record.get("decisions_applied") == ["DEC-110"], f"decisions_applied: {record.get('decisions_applied')!r}"


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
    assert record.get("inputs") == [{"id": s.TICKET, "hash": s.ticket_hash(s6_no_citation.project)}], record.get("inputs")
