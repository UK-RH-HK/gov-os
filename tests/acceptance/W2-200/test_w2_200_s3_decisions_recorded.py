"""S3: ``gov close`` records the decisions that govern the change from the ticket's own sources.

The ticket (``s3_world``) cites DEC-1013 and DEC-110 in ``sources``, DEC-111 and DEC-110 again in ``decisions``,
DEC-112 only inside its KPI lines (with DEC-111 again), beside ``CAP-1``, ``W2-9``, a path and a document name in
``sources`` and two look-alikes (``PREDEC-141``, ``DEC-1400x``) that are no whole-word id. The register holds the four
decisions and DEC-150, which nothing cites. The close passes; the record is read from
``docs/close/<ticket>/CL-<ticket>.md``. A clone of the repository at the same commit is closed as well.
"""

from __future__ import annotations

import w2_200_support as s


def _record(world):
    s.closed(world.run)
    return world.project.record()


def test_s3_the_close_passes_and_records_each_cited_decision_once_sorted_by_number(s3_world):
    record = _record(s3_world)
    assert record.get("decisions_applied") == s.S3_APPLIED, \
        f"decisions_applied is {record.get('decisions_applied')!r}, not {s.S3_APPLIED}"


def test_s3_inputs_hold_the_ticket_then_each_applied_decision_with_the_hash_of_its_span(s3_world):
    record = _record(s3_world)
    inputs = record.get("inputs")
    assert isinstance(inputs, list) and inputs, f"no inputs: {sorted(record)}"
    assert inputs[0] == {"id": s.TICKET, "hash": s.ticket_hash(s3_world.project)}, f"the first input is {inputs[0]!r}"
    assert [item.get("id") for item in inputs[1:]] == s.S3_APPLIED, f"the decision inputs are {inputs[1:]!r}"
    expected = s.span_hashes(s.S3_REGISTER, s.S3_APPLIED)
    for item in inputs[1:]:
        assert item.get("hash") in expected[item["id"]], \
            f"{item['id']}'s hash {item.get('hash')!r} is not the sha256 of its span of the register at HEAD"
    assert len({item["hash"] for item in inputs[1:]}) == len(s.S3_APPLIED), "two decisions carry one hash"


def test_s3_ids_of_other_forms_are_not_decisions_and_are_left_alone(s3_world):
    record = _record(s3_world)
    assert record.get("decisions_not_standing") == [], f"decisions_not_standing: {record.get('decisions_not_standing')!r}"
    assert record.get("decisions_unresolved") == [], f"decisions_unresolved: {record.get('decisions_unresolved')!r}"
    listed = set(record.get("decisions_applied") or []) | set(s.input_hashes(record))
    for other in s.S3_NOT_DECISIONS:
        assert other not in listed, f"{other} is listed as a decision or an input: {sorted(listed)}"


def test_s3_the_record_has_no_packet_hash(s3_world):
    result = s.closed(s3_world.run)
    record = s3_world.project.record()
    assert "packet_hash" not in record, "the close record still carries packet_hash"
    assert "packet_hash" not in result, "the close's answer still carries packet_hash"


def test_s3_the_same_ticket_at_the_same_commit_gives_the_same_lists_and_hashes(s3_world):
    first = _record(s3_world)
    s.closed(s3_world.twin_run)
    second = s3_world.twin.record()
    for key in ("decisions_applied", "decisions_not_standing", "decisions_unresolved", "inputs"):
        assert key in first, f"the record has no {key}: {sorted(first)}"
        assert first[key] == second[key], f"{key} differs between two closes at the same commit"
