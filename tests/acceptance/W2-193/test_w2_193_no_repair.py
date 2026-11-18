"""S6 and F1: a base red that no ``accepted_reds`` entry covers opens no repair ticket (EMERGENCY-2 4.2: a known bug
is a fix recorded in its owning ticket's record, not a ticket; CAP-31).

The scoped close proceeds, creates no file in ``.tickets/``, and its close record lists each base red it saw: the
test id, the failure type, a reason that says it was red at the base, ``caused: false`` and ``repair_ticket: null``.
A red the change causes still refuses ``RED_CAUSED``.

Planted projects: the exa-g6db project of ``test_w2_193_examin.py`` (a legacy suite and its kit copy, each with a
failing test and a module that fails to import) and W2-115's known red (``W2-bb``) in the routes the close takes its
base from (``--base`` given, the ticket's parent). ``gov queue`` cannot show this line: it never opens a repair
ticket and judges no red against a base (a red already red at the base is ``BATCH_UNEXPLAINED`` there, W2-115b's
``test_a_red_on_the_base_too_is_batch_unexplained_and_moves_nothing``, unchanged).

Red on the base: the close opens a repair ticket (a new file in ``.tickets/``) for each base red and its record names
it under ``repair_ticket``.
"""

import pytest

import w2_193_support as support

MODULES = {
    "g19_determinism": support.USES_BUILD_TREE_RED,   # red at the base and with the change (AssertionError)
    "g20_layout": support.USES_BUILD_TREE,           # green
    "g22_import": ("import", support.FAILS_TO_IMPORT),  # a module that fails to import, at the base too
}
BASE_REDS = [(support.LEGACY, "g19_determinism", "AssertionError"), (support.KIT, "g19_determinism", "AssertionError"),
             (support.LEGACY, "g22_import", None), (support.KIT, "g22_import", None)]
BB_KNOWN = support.smart.node_of("W2-bb", "bb_known", "test_bb_known")
BB_WIDGET = support.smart.node_of("W2-bb", "bb_widget", "test_bb_reads_the_widget")


def _tickets_dir(made):
    return sorted(p.name for p in (made.root / ".tickets").iterdir())


def _assert_a_plain_base_red(entry):
    """S6: the red's entry in the record: not caused, no repair ticket, a failure type, a reason that says it was red
    at the base."""
    assert entry.get("caused") is False, f"the base red is recorded as the change's: {entry}"
    assert "repair_ticket" in entry and entry["repair_ticket"] is None, \
        f"the base red names a repair ticket (or no repair_ticket key): {entry}"
    assert isinstance(entry.get("failure_type"), str) and entry["failure_type"].strip(), \
        f"the base red has no failure type: {entry}"
    reason = str(entry.get("reason") or "")
    assert "base" in reason.lower(), f"the base red's reason does not say it was red at the base: {entry}"


def test_the_exa_g6db_base_reds_open_no_repair_ticket_and_the_record_lists_each(tmp_path, sandbox):
    """S6: the exa-g6db project, no ``accepted_reds``: ``gov close --json`` exits 0, the ticket closes, ``.tickets/``
    holds exactly the files it held before the close (none new, none named ``repair``), and the record's ``reds``
    lists each of the four base reds (both suites' failing test and module that fails to import) as a plain base
    red; the failing tests' failure type is AssertionError."""
    told = tmp_path / "project-told"
    files = {**support.suite_files(support.LEGACY, "legacy", told, MODULES),
             **support.suite_files(support.KIT, "kit", told, MODULES),
             **support.own_suite_files(told)}
    made = support.project(tmp_path, files=files)
    support.work(made, text="# the widget, CHANGED\n")
    made.ready(sandbox)
    before = _tickets_dir(made)
    run = support.close(made, sandbox)

    assert run.returncode == 0, f"gov close did not exit 0\n{run.describe()}"
    support.assert_closed(made, run)
    assert _tickets_dir(made) == before, f"the close created files in .tickets/: {_tickets_dir(made)} (was {before})"
    texts = [p.read_text(encoding="utf-8") for p in (made.root / ".tickets").glob("*.md")]
    assert not any("repair_of_red" in t for t in texts), "a ticket in .tickets/ is a repair of a red"
    front = support.record(made)
    for folder, stem, failure_type in BASE_REDS:
        entry = support.red_entry_of_module(front, support.module_file(folder, stem))
        _assert_a_plain_base_red(entry)
        if failure_type:
            assert entry["failure_type"] == failure_type, f"the failure type of {stem} in {folder}: {entry}"


@pytest.mark.parametrize("route", ["given", "ticket"])
def test_a_base_red_judged_from_either_base_route_opens_no_repair_ticket(tmp_path, sandbox, route):
    """S6: W2-bb's known red is red at the base with the same failure type. ``given``: ``--base`` the initial commit
    (no green record); ``ticket``: no ``--base``, no green record, the base is the first parent of the ticket's
    oldest own commit. Each closes (exit 0, ticket closed); no new file in ``.tickets/``; the record lists the red
    as a plain base red."""
    told = tmp_path / "project-told"
    rel = BB_KNOWN.split("::")[0]
    made = support.project(tmp_path, files={rel: support.telling(rel, "test_bb_known", told, support.KNOWN_RED,
                                                                name="test_bb_known")})
    base = made.initial
    support.work(made)
    made.ready(sandbox)
    before = _tickets_dir(made)
    args = ("--base", base) if route == "given" else ()
    run = support.close(made, sandbox, *args)

    support.assert_closed(made, run)
    assert _tickets_dir(made) == before, f"the close created files in .tickets/: {_tickets_dir(made)} (was {before})"
    _assert_a_plain_base_red(support.red_entry(support.record(made), BB_KNOWN))


def test_a_red_the_change_brings_still_refuses_beside_a_base_red_and_no_ticket_names_the_base_red(tmp_path,
                                                                                                  sandbox):
    """F1, S6: W2-bb's known red is red at the base; W2-bb's widget test passes at the base and the change breaks
    it. Refused with ``RED_CAUSED`` naming the widget test; the ticket stays open; no repair ticket names either red
    (the caused one is never a repair, the base one no longer); a close record, when the refusal writes one, marks
    the widget test caused and the known red a plain base red."""
    told = tmp_path / "project-told"
    known, widget = BB_KNOWN.split("::")[0], BB_WIDGET.split("::")[0]
    made = support.project(tmp_path, files={
        known: support.telling(known, "test_bb_known", told, support.KNOWN_RED, name="test_bb_known"),
        widget: support.telling(widget, "test_bb_reads_the_widget", told, support.NOT_BROKEN,
                                name="test_bb_reads_the_widget")})
    base = made.initial
    support.work(made, text="# the widget, CHANGED BROKEN\n")
    made.ready(sandbox)
    before = support.tickets(made)
    run = support.close(made, sandbox, "--base", base)

    support.assert_caused(made, run, before, BB_WIDGET)
    assert not support.repair_tickets_naming(made, before, BB_KNOWN), "a repair ticket names the base red"
    if support.has_record(made):
        _assert_a_plain_base_red(support.red_entry(support.record(made), BB_KNOWN))
