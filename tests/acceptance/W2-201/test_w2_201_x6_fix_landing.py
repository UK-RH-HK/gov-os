"""W2-201 fix X6 (DEC-1219 (5)): a fix branch under a closed ticket lands through ``gov queue``; a plain branch on a
closed ticket is still refused.

Planted projects through ``gov queue`` and its ``--dry-run`` (W2-202's and W2-115b's support; the planted runs in
``w2_201_x6_support``). A branch is a fix landing when the ticket at the integration head is ``closed`` and a commit of
the branch carries ``Task: <the ticket>`` and ``Fix: <line>``. It runs as any candidate does and lands with no second
close: the ticket stays closed; its close commit (``fix: <ticket> (gov queue landed at <tested12>)``, ``Task:``) appends
one ``fixes`` entry ``{line, branch, tip, tested, landed}`` and one body line ``- fix landed: <line> (<branch> @
<tip12>)`` to ``docs/close/<ticket>/CL-<ticket>.md``, keeping the rest; a ticket with no record gets one with
``fixes``. The answer's ``closes`` entry adds ``fix: true`` and ``fix_line``, as do ``queue.json`` and the dry run.

The fix run: A (closed, with a first close's record) and C (closed, no record) land fixes beside B's feature, after a
dry run of the same three; then a second fix on A. The refusal run: a closed ticket's branch with no ``Fix:``, and one
whose ``Fix:`` is under another ticket's ``Task:``, are refused ``TICKET_CLOSED``; a ``Fix:`` branch on an in_progress
ticket closes it as today. The red run: a fix that breaks a closed ticket's acceptance suite, and one that breaks a
selected unit test, are not landed.
"""

from __future__ import annotations

import pytest

import w2_201_x6_support as x6
from w2_201_x6_support import A, B, C, base, kit


@pytest.fixture(scope="session")
def fix(tmp_path_factory):
    return x6.shared(tmp_path_factory, "fix", x6.build_fix)


@pytest.fixture(scope="session")
def refuse(tmp_path_factory):
    return x6.shared(tmp_path_factory, "refuse", x6.build_refuse)


@pytest.fixture(scope="session")
def red(tmp_path_factory):
    return x6.shared(tmp_path_factory, "red", x6.build_red)


LANDED = sorted(t.id for t in (A, B, C))


def _first(fix):
    """The first fix run's answer: A, B and C landed, exit 0 (a landing of three candidates that all land)."""
    done = fix.extra["first"]
    x6.not_refused_closed(done)
    result = kit.answer(done["run"], kit.EXIT_LANDED)
    assert sorted(result.get("landed") or []) == LANDED, (
        f"the landing did not land A, B and C: {result.get('landed')!r}\n{kit.describe(done['run'])}")
    return result


def _second(fix):
    done = fix.extra["second"]
    x6.not_refused_closed(done)
    result = kit.answer(done["run"], kit.EXIT_LANDED)
    assert result.get("landed") == [A.id], f"the second fix did not land: {result.get('landed')!r}"
    return result


def _entry(line, branch, tip, tested):
    return {"line": line, "branch": branch, "tip": tip, "tested": tested}


def _assert_entry(entry, want, where):
    assert isinstance(entry, dict), f"{where}: a fixes entry is not a map: {entry!r}"
    assert set(entry) == x6.ENTRY_KEYS, f"{where}: the fixes entry's keys are {sorted(entry)}, not " \
                                        f"{sorted(x6.ENTRY_KEYS)}"
    got = {key: entry[key] for key in want}
    assert got == want, f"{where}: the fixes entry holds {got}, not {want}"
    assert x6.is_utc_time(entry["landed"]), f"{where}: landed {entry['landed']!r} is not a UTC time of the landing"


# -- (a) a fix branch lands; the ticket stays closed; the record gains the entry --------------------------------------

def test_x6_a_fix_branch_lands_with_exit_0_and_the_ticket_stays_closed(fix):
    result = _first(fix)
    head = result["head"]
    after = kit.heads(fix.extra["first"]["after"]).get("refs/heads/main")  # main as the first landing left it
    assert after == head, f"main was at {after} after the first landing, not at the answer's head {head}"
    for t in (A, C):
        assert kit.status_at(fix.root, head, t.id) == "closed", f"{t.id} is not closed at the head after its fix"
    assert kit.status_at(fix.root, head, B.id) == "closed", "B's feature did not close as today"


def test_x6_a_fix_landing_runs_its_acceptance_folder_and_the_selected_tests(fix):
    result = _first(fix)
    ran = {a.get("ticket"): a.get("outcome") for a in result.get("acceptance") or []}
    assert ran.get(A.id) == "pass" and ran.get(C.id) == "pass", (
        f"the closed tickets' acceptance folders were not run through the runner of gov accept: {ran}")
    suites = result.get("selection", {}).get("suites") or []
    assert kit.USES_WIDGET[0] in suites, f"A's change to the widget did not select its unit test: {suites}"


def test_x6_the_fix_s_close_commit_is_named_fix_and_carries_task(fix):
    result = _first(fix)
    found = x6.chain(fix.root, result["tested"], result["head"])
    assert sorted(found) == LANDED, f"the close commits name {sorted(found)}, not {LANDED}"
    tested12 = result["tested"][:12]
    for t in (A, C):
        commit, subject, paths = found[t.id]
        assert subject == f"fix: {t.id} (gov queue landed at {tested12})", f"{t.id}'s close commit is {subject!r}"
        ticket_file, record_dir, checkpoint_dir = x6.OWN_PLACES(t.id)
        stray = [p for p in paths if p != ticket_file and not p.startswith((record_dir, checkpoint_dir))]
        assert not stray, f"{t.id}'s fix commit changes more than its records: {stray}"
        assert x6.close_rel(t.id) in paths, f"{t.id}'s fix commit does not write its close record: {paths}"
    closes = x6.closes_by_ticket(result, "the answer")
    assert {tid: c.get("commit") for tid, c in closes.items()} == {tid: c[0] for tid, c in found.items()}, (
        f"the answer's closes {closes} are not the close commits {found}")


def test_x6_the_close_record_gains_one_fixes_entry_and_one_body_line_and_keeps_the_rest(fix):
    result = _first(fix)
    tip = fix.extra["tips"]["a1"]
    text = x6.record_text(fix.root, result["head"], A.id)
    front, body = x6.split_record(text)
    was_front, was_body = x6.split_record(fix.extra["record_at_base"])
    fixes = front.get("fixes")
    assert isinstance(fixes, list) and len(fixes) == 1, f"A's close record's fixes: {fixes!r}"
    _assert_entry(fixes[0], _entry(x6.FIX_A1, "topic/aa-fix1", tip, result["tested"]), "A's close record")
    rest = {key: value for key, value in front.items() if key != "fixes"}
    assert rest == was_front, f"A's close record's front matter changed beside fixes:\n{rest}\nnot\n{was_front}"
    line = x6.fix_body_line(x6.FIX_A1, "topic/aa-fix1", tip)
    lines = x6.body_lines(body)
    assert lines.count(line) == 1, f"A's close record's body does not hold {line!r} once:\n{body}"
    assert [li for li in lines if li != line] == x6.body_lines(was_body), (
        f"A's close record's body changed beside the fix line:\n{body}")


def test_x6_a_closed_ticket_with_no_close_record_gets_one_with_fixes(fix):
    result = _first(fix)
    assert x6.record_text(fix.root, fix.old_head, C.id) is None, "fixture: C had a close record before the landing"
    tip = fix.extra["tips"]["cc"]
    text = x6.record_text(fix.root, result["head"], C.id)
    assert text is not None, f"C's fix landing wrote no close record {x6.close_rel(C.id)}"
    front, body = x6.split_record(text)
    fixes = front.get("fixes")
    assert isinstance(fixes, list) and len(fixes) == 1, f"C's close record's fixes: {fixes!r}"
    _assert_entry(fixes[0], _entry(x6.FIX_C, "topic/cc-fix", tip, result["tested"]), "C's close record")
    line = x6.fix_body_line(x6.FIX_C, "topic/cc-fix", tip)
    assert x6.body_lines(body).count(line) == 1, f"C's close record's body does not hold {line!r} once:\n{body}"


def test_x6_the_answer_s_closes_entry_carries_fix_and_fix_line_and_a_feature_s_is_as_today(fix):
    result = _first(fix)
    closes = x6.closes_by_ticket(result, "the answer")
    for t, line in ((A, x6.FIX_A1), (C, x6.FIX_C)):
        got = {key: closes.get(t.id, {}).get(key) for key in ("fix", "fix_line")}
        assert got == {"fix": True, "fix_line": line}, f"{t.id}'s closes entry: {closes.get(t.id)}"
    feature = closes.get(B.id) or {}
    assert "fix" not in feature and "fix_line" not in feature, f"B's feature closes entry is not as today: {feature}"
    assert feature.get("close_record") == x6.close_rel(B.id), f"B's closes entry: {feature}"


def test_x6_queue_json_holds_the_answer_s_closes(fix):
    result = _first(fix)
    held = base.queue_record(fix, result)
    assert held.get("closes") == result.get("closes"), (
        f"queue.json's closes {held.get('closes')!r} are not the answer's {result.get('closes')!r}")
    assert x6.fix_marks(held.get("closes")) == {A.id: x6.FIX_A1, C.id: x6.FIX_C}, f"queue.json: {held.get('closes')}"


def test_x6_a_second_fix_on_the_same_ticket_appends_a_second_entry(fix):
    first = _first(fix)
    result = _second(fix)
    tips = fix.extra["tips"]
    assert kit.status_at(fix.root, result["head"], A.id) == "closed", "A is not closed after its second fix"
    found = x6.chain(fix.root, result["tested"], result["head"])
    assert found[A.id][1] == f"fix: {A.id} (gov queue landed at {result['tested'][:12]})", found[A.id][1]
    front, body = x6.split_record(x6.record_text(fix.root, result["head"], A.id))
    before, _ = x6.split_record(x6.record_text(fix.root, first["head"], A.id))
    fixes = front.get("fixes")
    assert isinstance(fixes, list) and len(fixes) == 2, f"A's close record's fixes after two fixes: {fixes!r}"
    assert fixes[0] == before["fixes"][0], f"the first entry changed: {before['fixes'][0]} -> {fixes[0]}"
    _assert_entry(fixes[1], _entry(x6.FIX_A2, "topic/aa-fix2", tips["a2"], result["tested"]), "the second entry")
    lines = x6.body_lines(body)
    one = x6.fix_body_line(x6.FIX_A1, "topic/aa-fix1", tips["a1"])
    two = x6.fix_body_line(x6.FIX_A2, "topic/aa-fix2", tips["a2"])
    assert lines.count(one) == 1 and lines.count(two) == 1 and lines.index(one) < lines.index(two), (
        f"the body does not hold the two fix lines once each, in order:\n{body}")
    closes = x6.closes_by_ticket(result, "the second answer")
    assert {k: closes.get(A.id, {}).get(k) for k in ("fix", "fix_line")} == {"fix": True, "fix_line": x6.FIX_A2}


# -- (b) a plain branch, or Fix: under another ticket's Task:, is refused TICKET_CLOSED --------------------------------

@pytest.mark.parametrize("case", ["plain", "other"])
def test_x6_a_closed_ticket_s_branch_without_its_own_fix_trailer_is_refused_ticket_closed(refuse, case):
    """Guard on the base: ``plain`` carries ``Task: A`` and no ``Fix:``; ``other`` carries ``Fix:`` under ``Task: B``."""
    done = refuse.extra[case]
    kit.refusal(done["run"], "TICKET_CLOSED", 1)
    base.unchanged(done["before"], done["after"])


# -- (c) a fix whose change breaks the acceptance folder or a selected test is not landed -----------------------------

@pytest.mark.parametrize("case, ticket, node", [("red_c", C, C.node), ("red_a", A, kit.USES_WIDGET_NODE)],
                         ids=["acceptance-folder", "selected-test"])
def test_x6_a_fix_that_breaks_a_test_is_not_landed(red, case, ticket, node):
    """``red_c`` breaks C's acceptance suite only; ``red_a`` breaks a unit test the widget selects (A's own suite
    passes whatever the widget holds)."""
    done = red.extra[case]
    x6.not_refused_closed(done)
    result = kit.answer(done["run"], kit.EXIT_NOT_ALL_LANDED)
    assert result.get("landed") == [] and result.get("culprits") == [ticket.id], (
        f"landed {result.get('landed')!r}, culprits {result.get('culprits')!r}\n{kit.describe(done['run'])}")
    assert node in (result.get("reds") or []) or any(
        a.get("ticket") == ticket.id and a.get("outcome") != "pass" for a in result.get("acceptance") or []), (
        f"the answer does not name the broken test {node}: reds {result.get('reds')}, acceptance "
        f"{result.get('acceptance')}")
    base.not_moved(red, done["before"], done["after"])
    assert done["after"]["files"] == done["before"]["files"], "a red fix changed a tracked file"
    main = kit.heads(done["after"]).get("refs/heads/main")  # main as this run left it
    assert kit.status_at(red.root, main, ticket.id) == "closed"
    assert x6.record_text(red.root, main, A.id) == red.extra["record_at_base"], "A's close record changed"


# -- (d) the dry run answers the same, changes nothing, appends nothing -----------------------------------------------

def test_x6_the_dry_run_answers_the_same_and_changes_nothing(fix):
    done = fix.extra["dry"]
    x6.not_refused_closed(done)
    result = kit.answer(done["run"], kit.EXIT_LANDED)
    assert sorted(result.get("landed") or []) == LANDED, f"the dry run would land {result.get('landed')!r}"
    assert done["after"] == done["before"], "the dry run moved a ref or changed a file"
    marks = x6.fix_marks(result)
    assert marks == {A.id: x6.FIX_A1, C.id: x6.FIX_C}, (
        f"the dry run's answer does not say fix: true and fix_line for A and C: {marks}\n{result}")


# -- (e) a Fix: trailer on an in_progress ticket's branch closes it as today ------------------------------------------

def test_x6_a_fix_trailer_on_an_in_progress_ticket_closes_it_as_today(refuse):
    """Guard on the base."""
    done = refuse.extra["progress"]
    result = kit.answer(done["run"], kit.EXIT_LANDED)
    assert result.get("landed") == [B.id], f"B did not land: {result.get('landed')!r}"
    head = result["head"]
    assert kit.status_at(refuse.root, head, B.id) == "closed", "B did not close"
    found = x6.chain(refuse.root, result["tested"], head)
    assert found[B.id][1].startswith(f"close: {B.id} "), f"B's close commit is {found[B.id][1]!r}"
    front, _ = x6.split_record(x6.record_text(refuse.root, head, B.id))
    assert not front.get("fixes"), f"B's first close record holds fixes: {front.get('fixes')!r}"
    entry = x6.closes_by_ticket(result, "the answer").get(B.id) or {}
    assert "fix" not in entry and "fix_line" not in entry, f"B's closes entry is not as today: {entry}"
