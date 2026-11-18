"""S3: with no ``--base`` and no green record on HEAD's line, the scoped close judges each red against the first parent
of the ticket's oldest own (trailered, non-merge) commit; the close record names that commit under ``base`` and says
where it came from under ``base_from`` (``given``, ``green_record`` or ``ticket``); a red already red there with the
same failure type is not the change's; a red green there is.

The planted projects are W2-115's (``Smart``): another ticket's merged commit (``M``) stands between the initial
commit and the ticket's first own commit, so the parent of that commit is ``M``.

Red on the base: with no green record there is no head without the change (DEC-1150 (2)): every red is the
change's, the close refuses ``RED_CAUSED`` and nothing runs off the change; the record has no ``base_from``.
"""

import pytest

import w2_193_support as support

BB_KNOWN = support.smart.node_of("W2-bb", "bb_known", "test_bb_known")
BB_WIDGET = support.smart.node_of("W2-bb", "bb_widget", "test_bb_reads_the_widget")


def _history(made):
    """Another ticket's merged commit M, then two own commits of the ticket, then its checkpoint. Returns M."""
    merged = made.merged({support.smart.GIZMO: "# a gizmo, another ticket's work\n"})
    first = support.work(made)
    support.work(made, text="# the widget, CHANGED again\n")
    assert support.parent(made, first) == merged
    return merged


def test_with_no_green_record_a_red_red_at_the_parent_of_the_oldest_own_commit_is_not_the_change_s(tmp_path,
                                                                                                   sandbox):
    """S3 (and S4's ``base_run`` when no base run is needed): no green record; W2-bb's known red is red at M, the
    parent of the ticket's oldest own commit, with the same failure type. The close passes, the ticket closes, the
    record names ``base: M`` and ``base_from: ticket``, marks the red not caused with a repair ticket, the red ran
    alone at M (and failed there), and ``base_run`` says no base run was made (null, or ``ran: false``)."""
    told = tmp_path / "project-told"
    reds = {BB_KNOWN.split("::")[0]: support.telling(BB_KNOWN.split("::")[0], "test_bb_known", told,
                                                    support.KNOWN_RED, name="test_bb_known")}
    made = support.project(tmp_path, files=reds)
    merged = _history(made)
    made.ready(sandbox)
    before = support.tickets(made)
    run = support.close(made, sandbox)

    support.assert_closed(made, run)
    front = support.record(made)
    assert front.get("base") == merged, f"the record's base is not the parent of the oldest own commit {merged}: " \
                                        f"{front.get('base')!r}"
    assert front.get("base_from") == support.FROM_TICKET, f"base_from is not 'ticket': {front.get('base_from')!r}"
    entry = support.red_entry(front, BB_KNOWN)
    assert entry.get("caused") is False, f"a red already red at the base is recorded as the change's: {entry}"
    assert entry.get("repair_ticket"), f"the base red names no repair ticket: {entry}"
    assert support.repair_tickets_naming(made, before, BB_KNOWN), "no repair ticket names the base red"
    base_runs = support.calls(support.base_side(support.told_runs(told, "test_bb_known")))
    assert base_runs and not any(r["ok"] for r in base_runs), \
        f"the red was not run alone at the base (where it fails): {base_runs}"
    base_run = front.get("base_run", "missing")
    assert base_run is None or (isinstance(base_run, dict) and base_run.get("ran") is False), \
        f"base_run does not say that no base run was needed: {base_run!r}"


def test_with_no_green_record_a_red_green_at_the_parent_of_the_oldest_own_commit_refuses(tmp_path, sandbox):
    """S3, F1: no green record; W2-bb's widget test passes at M and the ticket's change breaks it: refused with
    RED_CAUSED naming it, the ticket stays open, no repair ticket names it, and it ran at M, where it passed."""
    told = tmp_path / "project-told"
    rel = BB_WIDGET.split("::")[0]
    made = support.project(tmp_path, files={rel: support.telling(rel, "test_bb_reads_the_widget", told,
                                                                 support.NOT_BROKEN,
                                                                 name="test_bb_reads_the_widget")})
    made.merged({support.smart.GIZMO: "# a gizmo, another ticket's work\n"})
    support.work(made, text="# the widget, CHANGED BROKEN\n")
    made.ready(sandbox)
    before = support.tickets(made)
    run = support.close(made, sandbox)

    support.assert_caused(made, run, before, BB_WIDGET)
    base_runs = support.calls(support.base_side(support.told_runs(told, "test_bb_reads_the_widget")))
    assert base_runs and all(r["ok"] for r in base_runs), \
        f"the red was not judged against the parent of the oldest own commit, where it passes: {base_runs}"


@pytest.mark.parametrize("source", [support.FROM_GREEN, support.FROM_GIVEN])
def test_the_record_says_where_the_base_came_from(tmp_path, sandbox, source):
    """S3, the order ``--base`` given > the newest green record on HEAD's line > the ticket's parent. A green record
    names the initial commit G; M follows, then the ticket's own commits (so the ticket's parent is M, not G).
    ``green_record``: no ``--base``; the record names ``base: G``, ``base_from: green_record``. ``given``:
    ``--base M`` (its full id) beside the green record; the record names ``base: M``, ``base_from: given``. Nothing
    fails, so the close passes."""
    made = support.project(tmp_path, nightly="green")
    green = made.initial
    merged = _history(made)
    made.ready(sandbox)
    args = ("--base", merged) if source == support.FROM_GIVEN else ()
    run = support.close(made, sandbox, *args)

    support.assert_closed(made, run)
    front = support.record(made)
    expected = merged if source == support.FROM_GIVEN else green
    assert front.get("base") == expected, f"the record's base is {front.get('base')!r}, not {expected}"
    assert front.get("base_from") == source, f"base_from is {front.get('base_from')!r}, not {source!r}"
