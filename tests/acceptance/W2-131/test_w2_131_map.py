"""W2-131 S2 (DEC-1082 (2), DEC-424): the path-to-record map used for labels and for DEC-424's ahead paths no longer
lets one entry of a many-entry file stand for the file: records that carry a span (the register's entries) are left
out of it, as ``supplementary.py`` does; DEC-424's move still lifts a failure or lesson record in a ticket's closure.

The map is ``retrieve._graph``'s first answer (``path -> id``), the one the ticket names (``retrieve.py:87`` on
``w2/integrate``, DEC-1082 (2)).
"""

from __future__ import annotations

import w2_131_support as support

from gov.retrieval import retrieve as retrieval

AHEAD = {support.FAILURE_PATH, support.LESSON_PATH}


def _map(project):
    assert hasattr(retrieval, "_graph"), "the path-to-record map's builder `_graph` is gone from retrieve.py"
    return retrieval._graph(project)[0]


def test_s2_the_path_to_record_map_holds_no_register_entry_id(project):
    record_of = _map(project)
    assert record_of.get(support.REGISTER) not in support.ENTRY_IDS, (
        f"the map labels the register's path with one entry: {support.REGISTER} -> {record_of.get(support.REGISTER)!r}")
    assert not set(record_of.values()) & support.ENTRY_IDS, f"the map holds a register entry's id: {record_of}"


def test_s2_the_map_keeps_the_record_of_each_record_file(project):
    record_of = _map(project)
    assert {path: record_of.get(path) for path in (support.TICKET_PATH, support.FAILURE_PATH, support.LESSON_PATH)} \
        == {support.TICKET_PATH: support.TICKET, support.FAILURE_PATH: support.FAILURE,
            support.LESSON_PATH: support.LESSON}


def test_s2_dec_424_still_lifts_the_failure_and_lesson_records_of_the_ticket_s_closure(ask, monkeypatch):
    paths = [item["path"] for item in ask("lantern", ticket=support.TICKET)["evidence"]]
    assert AHEAD <= set(paths), f"premise: the failure and the lesson are in the bundle: {paths}"
    held = [path in AHEAD for path in paths]
    assert held == sorted(held, reverse=True), f"a failure or lesson chunk comes after other evidence: {paths}"
    first_page = [item["path"] for item in ask("lantern", ticket=support.TICKET, batch_size=2)["evidence"]]
    assert first_page and set(first_page) <= AHEAD, f"the batched first page is not the lifted records: {first_page}"
    # premise: without the move the order differs, so the lift above is DEC-424's and not the fusion's
    monkeypatch.setattr(retrieval, "AHEAD_TYPES", frozenset())
    unmoved = [item["path"] for item in ask("lantern", ticket=support.TICKET)["evidence"]]
    assert unmoved[0] not in AHEAD, f"premise: without DEC-424's move a failure or lesson still leads: {unmoved}"
