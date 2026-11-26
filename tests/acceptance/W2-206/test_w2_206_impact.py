"""IT-1 and IT-2 (plan item 1-9; ``.tickets/DAEO-l2b2.md`` "Fix: the impact trace at the landing"): the landing traces
every record file a candidate's change holds with ``gov impact`` on the tested merge, into the answer, ``queue.json``
and the ticket's first close record; ``--select`` and a dry run carry the same trace; a trace that fails or takes too
long never refuses the landing.

The oracle for each record's tickets, tests and completeness is ``gov impact <id>`` itself, on a scratch clone of the
planted project whose record store is loaded from the landed head (README, "Fix: the impact trace at the landing").
"""

from __future__ import annotations

import pytest

import w2_206_impact_support as impact
import w2_206_support as support
from w2_206_support import A, B, kit


@pytest.fixture(scope="session")
def built(tmp_path_factory):
    return lambda name: impact.shared(tmp_path_factory, name, impact.BUILDS[name])


def _landed(built):
    land = built("main")["land"]
    result = impact.answer(land)
    return land, result, impact.impact_mapping(result, "the answer")


def _a_records(built):
    _, _, mapping = _landed(built)
    assert A.id in mapping, f"impact holds no entry for {A.id}: {mapping}"
    return mapping[A.id], impact.records_by_id(mapping[A.id])


# --------------------------------------------------------------------------
# IT-1: the trace, into the answer, queue.json and the close record
# --------------------------------------------------------------------------

def test_it1_the_answer_and_queue_json_hold_one_entry_for_each_landed_ticket(built):
    land, _, mapping = _landed(built)
    assert set(mapping) == {A.id, B.id}, f"impact's tickets: {sorted(mapping)}"
    held = impact.impact_mapping(land["held"], "queue.json")
    assert held == mapping, f"queue.json's impact {held} is not the answer's {mapping}"


def test_it1_each_ticket_s_first_close_record_holds_its_entry(built):
    land, _, mapping = _landed(built)
    for ticket in (A.id, B.id):
        front = land["close"][ticket]
        assert front is not None, f"no close record for {ticket}"
        assert front.get("impact") == mapping.get(ticket), \
            f"{ticket}'s close record's impact {front.get('impact')!r} is not the answer's {mapping.get(ticket)!r}"


def test_it1_the_records_listed_are_the_change_s_record_files_and_register_entries_and_nothing_else(built):
    _, records = _a_records(built)
    want = {**impact.PRESENT, **impact.REMOVED}
    got = {record_id: entry.get("path") for record_id, entry in records.items()}
    assert got == want, f"the records listed (id: path):\n{got}\nnot\n{want}"


def test_it1_each_record_names_the_tickets_tests_and_completeness_gov_impact_names_on_the_landed_tree(built):
    _, records = _a_records(built)
    oracle = built("main")["oracle"]
    for record_id, path in impact.PRESENT.items():
        entry, said = records.get(record_id), oracle[record_id]
        assert entry is not None, f"{record_id} is not listed: {sorted(records)}"
        assert set(entry) == {"id", "path", "tickets", "tests", "complete"}, f"{record_id}: {entry}"
        got = {"tickets": sorted(entry["tickets"]), "tests": sorted(entry["tests"]), "complete": entry["complete"]}
        assert got == said, f"{record_id} ({path}): the landing says {got}, gov impact says {said}"


def test_it1_a_removed_record_and_a_removed_register_entry_are_unavailable_and_not_complete(built):
    entry, records = _a_records(built)
    for record_id, path in impact.REMOVED.items():
        got = records.get(record_id)
        assert got is not None, f"{record_id} is not listed: {sorted(records)}"
        assert set(got) == {"id", "path", "unavailable", "complete"}, f"{record_id}: {got}"
        assert impact.is_unavailable(got["unavailable"]) and got["complete"] is False and got["path"] == path, got
    assert entry["complete"] is False, f"the entry is complete although a record is not: {entry}"


def test_it1_the_entry_is_complete_only_where_every_record_is_and_a_change_with_no_record_is_empty(built):
    _, _, mapping = _landed(built)
    entry = mapping.get(A.id)
    records = impact.records_by_id(entry)
    assert entry["complete"] is all(r.get("complete") is True for r in records.values()), entry
    assert mapping.get(B.id) == {"records": [], "complete": True}, f"{B.id} changes no record: {mapping.get(B.id)}"


def test_it1_one_close_commit_per_ticket_holds_the_trace_and_nothing_follows_it(built):
    from types import SimpleNamespace

    data = built("main")
    land, result, mapping = _landed(built)
    root = data["root"]
    closes = kit.assert_landed_through_close_commits(SimpleNamespace(root=root), result, "main", land["old_head"])
    for ticket, commit in closes.items():
        front = kit.front_matter(kit.show(root, commit, f"docs/close/{ticket}/CL-{ticket}.md"))
        assert front.get("impact") == mapping[ticket], \
            f"{ticket}'s close commit {commit[:12]} holds impact {front.get('impact')!r}"


def test_it1_a_fix_landing_holds_the_trace_in_its_answer_and_queue_json_only(built):
    data = built("fix")
    land = data["land"]
    mapping = impact.impact_mapping(impact.answer(land), "the answer")
    records = impact.records_by_id(mapping.get(A.id))
    assert set(records) == {"SPEC-001"}, f"records: {records}"
    got = records["SPEC-001"]
    said = data["oracle"]["SPEC-001"]
    assert {"tickets": sorted(got["tickets"]), "tests": sorted(got["tests"]), "complete": got["complete"]} == said, \
        f"the landing says {got}, gov impact says {said}"
    assert impact.impact_mapping(land["held"], "queue.json") == mapping, "queue.json's impact is not the answer's"
    front = land["close"]
    assert front is not None, "the fix landing wrote no close record"
    assert set(front) == {"id", "type", "status", "state_class", "task", "created", "fixes"}, \
        f"the fix's close record is not X6's own form: {sorted(front)}"


# --------------------------------------------------------------------------
# IT-1: a trace that fails or takes too long never refuses the landing
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", ("no_register", "limit"))
def test_it1_a_trace_that_fails_or_overruns_lands_with_exit_0_and_says_unavailable(built, name):
    land = built(name)["land"]
    result = impact.answer(land, kit.EXIT_LANDED)
    assert result.get("landed") == [A.id, B.id], kit.describe(land["run"])
    assert land["status"] == {A.id: "closed", B.id: "closed"}, land["status"]
    mapping = impact.impact_mapping(result, "the answer")
    assert impact.is_unavailable(mapping.get(A.id)), f"{A.id}'s entry: {mapping.get(A.id)!r}"
    assert impact.impact_mapping(land["held"], "queue.json") == mapping, "queue.json's impact is not the answer's"
    for ticket in (A.id, B.id):
        front = land["close"][ticket] or {}
        assert front.get("impact") == mapping.get(ticket), \
            f"{ticket}'s close record's impact: {front.get('impact')!r}, the answer's: {mapping.get(ticket)!r}"


# --------------------------------------------------------------------------
# IT-2: --select and the dry run carry the same trace
# --------------------------------------------------------------------------

def test_it2_select_prints_the_impact_the_landing_then_records(built):
    data = built("main")
    mapping = impact.impact_mapping(impact.selected(data["select"]), "--select's object")
    assert set(mapping) == {A.id, B.id}, f"impact's tickets: {sorted(mapping)}"
    for ticket in (A.id, B.id):
        front = data["land"]["close"][ticket] or {}
        assert front.get("impact") is not None, f"{ticket}'s close record holds no impact"
        assert impact.normal(mapping[ticket]) == impact.normal(front["impact"]), \
            f"{ticket}: --select says {mapping[ticket]}, the landing recorded {front['impact']}"


def test_it2_select_with_the_trace_moves_nothing_and_runs_no_test(built):
    taken = built("main")["select"]
    impact.impact_mapping(impact.selected(taken), "--select's object")
    assert taken["after"]["told"] == taken["before"]["told"], "a planted test ran"
    support.moved_nothing(taken)


def test_it2_a_dry_run_s_answer_and_select_json_hold_the_same_impact(built):
    data = built("main")
    dry = data["dry"]
    mapping = impact.impact_mapping(impact.answer(dry, kit.EXIT_LANDED), "the dry run's answer")
    chosen = impact.impact_mapping(support.one_object(dry["select_json"] or ""), "select.json")
    assert chosen == mapping, f"select.json's impact {chosen} is not the answer's {mapping}"
    _, _, landed = _landed(built)
    assert impact.normal(mapping) == impact.normal(landed), \
        f"the dry run says {mapping}, the landing says {landed}"
    assert kit.heads(dry["after"]) == kit.heads(dry["before"]), "a dry run moved a branch"


@pytest.mark.parametrize("name", ("no_register", "limit"))
def test_it2_select_with_a_trace_that_fails_or_overruns_prints_the_string_and_exits_0(built, name):
    taken = built(name)["select"]
    mapping = impact.impact_mapping(impact.selected(taken), "--select's object")
    assert impact.is_unavailable(mapping.get(A.id)), f"{A.id}'s entry: {mapping.get(A.id)!r}"
    support.moved_nothing(taken)
