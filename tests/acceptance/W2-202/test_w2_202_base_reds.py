"""A1 (L2 §3 A1; DEC-1214 L2, Q-CLOSE): a red that is red at the base is recorded, not refused.

Success lines 1 (A1 S1), 2 (A1 S2) and 3 (A1 S3), failure lines 1 (A1 F1) and 2 (A1 F2). README, "The planted runs":
base_red, untrailered, each_breaks, another_way, mixed.
"""

from __future__ import annotations

import pytest

import w2_202_support as support
from w2_202_support import A, B, kit, module_rel

KNOWN = kit.KNOWN_RED_NODE


@pytest.fixture(scope="module")
def base_red(landing):
    return landing("base_red")


@pytest.fixture()
def landed(base_red):
    """The answer of the base-red landing, read in the case itself (on the base it is a refusal)."""
    return lambda: kit.answer(base_red.run, kit.EXIT_LANDED)


# -- success line 1 (A1 S1) ---------------------------------------------------------------------------------------

def test_a_batch_with_a_red_that_is_red_at_the_base_lands_and_exits_0(base_red, landed):
    result = landed()
    assert result.get("landed") == [A.id] and result.get("culprits") == [] and result.get("refused") == []
    closes = kit.assert_landed_through_close_commits(base_red, result, "main", base_red.old_head)
    assert list(closes) == [A.id]
    assert kit.parents(base_red.root, result["tested"]) == [base_red.old_head, base_red.tips[A.id]]
    assert kit.status_at(base_red.root, "main", A.id) == "closed"


def test_the_close_record_lists_the_base_red_with_its_type_and_the_base_commit(base_red, landed):
    result = landed()
    front = support.assert_base_red_recorded(base_red, result, A.id, KNOWN, base_red.old_head)
    assert A.id not in [str(c) for c in front.get("culprits") or []], f"culprits: {front.get('culprits')!r}"
    assert front.get("base") == base_red.old_head


def test_the_answer_and_the_queue_s_record_name_the_base_red(base_red, landed):
    result = landed()
    assert support.ids(result.get("base_reds")) == [KNOWN], f"the answer's base_reds: {result.get('base_reds')!r}"
    held = support.queue_record(base_red, result)
    assert support.ids(held.get("base_reds")) == [KNOWN], f"queue.json's base_reds: {held.get('base_reds')!r}"


def test_the_base_red_ran_on_the_merged_result_and_the_green_tests_too(base_red, landed):
    landed()
    runs = base_red.told_runs("test_known_red")
    with_change = [r for r in runs if (r["seen"][module_rel("widget")] or "").startswith("# CHANGED")]
    assert with_change and not any(r["ok"] for r in runs), f"the known red's runs: {runs}"
    for test in ("test_aa", "test_uses_widget"):
        told = base_red.told_runs(test)
        assert told and all(r["ok"] for r in told), f"{test} did not run green in the landing: {told}"


# -- success line 2 (A1 S2) ---------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def untrailered(landing):
    return landing("untrailered")


def test_a_red_made_by_a_commit_without_a_trailer_is_a_base_red_and_the_ticket_lands(untrailered):
    result = kit.answer(untrailered.run, kit.EXIT_LANDED)
    assert result.get("landed") == [A.id] and result.get("culprits") == [] and result.get("refused") == []
    maker = untrailered.extra["maker"]
    assert untrailered.old_head == maker and kit.trailers(untrailered.root, maker) == []
    support.assert_base_red_recorded(untrailered, result, A.id, KNOWN, maker)
    assert support.ids(result.get("base_reds")) == [KNOWN]
    assert kit.status_at(untrailered.root, "main", A.id) == "closed"


def test_the_commit_without_a_trailer_is_under_the_landed_head_and_nothing_names_it_a_culprit(untrailered):
    result = kit.answer(untrailered.run, kit.EXIT_LANDED)
    maker = untrailered.extra["maker"]
    assert kit.is_ancestor(untrailered.root, maker, result["head"])
    front = kit.close_record(untrailered, result["head"], A.id)
    named = [e for e in front.get("reds") or [] if e.get("verdict") != "base"]
    assert not named and not front.get("culprits"), f"a red or culprit beside the base red: {front.get('reds')!r}"


# -- success line 3 (A1 S3) ---------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def each_breaks(landing):
    return landing("each_breaks")


def test_a_red_green_at_the_base_that_no_single_candidate_explains_is_batch_unexplained(each_breaks):
    error = kit.refusal(each_breaks.run, "BATCH_UNEXPLAINED", kit.EXIT_NOT_ALL_LANDED)
    reds = (error.get("details") or {}).get("reds") or []
    assert support.BOTH_NODE in reds, f"the refusal does not name the red: {error.get('details')}"
    assert not support.ids((error.get("details") or {}).get("base_reds")), "a red green at the base is a base red"
    # the red was judged at the base: run once on a tree holding neither candidate's change, and green there
    at_base = [r for r in each_breaks.told_runs("test_both")
               if not any("CHANGED" in (text or "") for text in r["seen"].values())]
    assert len(at_base) == 1 and at_base[0]["ok"], \
        f"the red was not run once at the base (green there): {len(at_base)} run(s) on the base's tree: {at_base}"


def test_the_refused_batch_leaves_the_integration_branch_and_both_tickets_as_they_were(each_breaks):
    kit.refusal(each_breaks.run, "BATCH_UNEXPLAINED", kit.EXIT_NOT_ALL_LANDED)
    assert any(not r["ok"] for r in each_breaks.told_runs("test_both")), "the planted red never ran"
    after = each_breaks.state()
    support.unchanged(each_breaks.before, after)
    for ticket in (A, B):
        assert kit.status_at(each_breaks.root, "main", ticket.id) == "open"
        assert kit.show(each_breaks.root, "main", f"docs/close/{ticket.id}/CL-{ticket.id}.md") is None
    assert not (each_breaks.root / "docs" / "close").exists()


def test_a_red_at_the_base_that_fails_another_way_with_the_change_is_not_a_base_red(landing):
    """A guard, green on the base by design (README): red at the base is not enough, the failure type must be the
    same. The candidate turns the known red's bare assert into a ``ValueError``: refused, nothing lands."""
    another = landing("another_way")
    error = kit.refusal(another.run, "BATCH_UNEXPLAINED", kit.EXIT_NOT_ALL_LANDED)
    assert not support.ids((error.get("details") or {}).get("base_reds")), f"{error.get('details')}"
    support.unchanged(another.before, another.state())
    assert kit.status_at(another.root, "main", A.id) == "open"


# -- failure line 1 (A1 F1) ---------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def mixed(landing):
    return landing("mixed")


def test_the_candidate_that_breaks_a_green_test_is_the_culprit_and_does_not_land(mixed):
    result = kit.answer(mixed.run, kit.EXIT_NOT_ALL_LANDED)
    assert result.get("culprits") == [B.id], f"culprits: {result.get('culprits')!r}"
    assert result.get("landed") == [A.id], f"landed: {result.get('landed')!r}"
    assert not kit.is_ancestor(mixed.root, mixed.tips[B.id], "main"), "the culprit's work is on main"
    assert kit.status_at(mixed.root, "main", B.id) == "open"
    assert kit.show(mixed.root, "main", f"docs/close/{B.id}/CL-{B.id}.md") is None
    kit.assert_closed_iff_merged(mixed, "main", every=[A.id, B.id])


def test_the_red_the_candidate_causes_is_never_recorded_as_a_base_red(mixed):
    result = kit.answer(mixed.run, kit.EXIT_NOT_ALL_LANDED)
    caused = (support.USES_GADGET_NODE, B.node)
    assert support.ids(result.get("base_reds")) == [KNOWN], f"the answer's base_reds: {result.get('base_reds')!r}"
    front = support.assert_base_red_recorded(mixed, result, A.id, KNOWN, mixed.old_head)
    for node in caused:
        verdicts = [e.get("verdict") for e in support.entries(front, node)]
        assert "base" not in verdicts, f"{node} is recorded as a base red: {front.get('reds')!r}"
        assert node not in support.ids(front.get("base_reds"))
    verdicts = [e.get("verdict") for e in support.entries(front, support.USES_GADGET_NODE)]
    assert verdicts == ["culprit"], f"the caused red's verdict in the record: {front.get('reds')!r}"
    assert [str(c) for c in front.get("culprits") or []] == [B.id], f"culprits: {front.get('culprits')!r}"


# -- failure line 2 (A1 F2) ---------------------------------------------------------------------------------------

def test_a_base_red_creates_no_ticket_file_and_no_line_under_docs_outside_the_close_s_places(base_red, landed):
    result = landed()
    root = base_red.root
    changed = support.changed_between(root, base_red.old_head, result["head"])
    added_tickets = [p for letter, p in changed if p.startswith(".tickets/") and letter != "M"]
    assert not added_tickets, f"the landing added or removed a ticket file: {added_tickets}"
    assert [p for _, p in changed if p.startswith(".tickets/")] == [A.ticket_rel]
    stray = support.stray_record_paths([p for _, p in changed])
    assert not stray, f"the landed head holds lines under docs/ outside docs/close/ and docs/checkpoints/: {stray}"
    now = sorted(path.name for path in (root / ".tickets").iterdir())
    assert now == base_red.extra["tickets_before"], f".tickets/ holds {now}, it held {base_red.extra['tickets_before']}"


def test_the_root_and_the_clone_hold_no_untracked_ticket_or_docs_path_after_the_base_red(base_red, landed):
    landed()
    clone_status = base_red.extra.get("clone_status")
    assert clone_status is not None, "the queue's warm clone is not at .gov-runtime/close/clone"
    for where, porcelain in (("root", kit.git(base_red.root, "status", "--porcelain")), ("clone", clone_status)):
        paths = support.status_paths(porcelain)
        bad = [p for p in paths if p.startswith(".tickets/")] + support.stray_record_paths(paths)
        assert not bad, f"the {where}'s git status shows {bad}"
