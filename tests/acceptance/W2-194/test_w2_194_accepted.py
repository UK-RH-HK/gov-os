"""S3 and F1 (accepted reds): in scoped mode a red that is red at the base and listed by a path-map ``accepted_reds``
entry that counts (an ACCEPTED owner register entry naming it, the entry added by ``Role: owner`` commits, DEC-757's
rule unchanged) is accepted: no RED_CAUSED, the close record's ``accepted_reds`` names it with its decision, no
repair ticket is opened for it; an entry that does not count covers nothing and is named in the record
(``accepted_red_findings``); a listed red green at the base is still the change's.

The planted project (W2-115's ``Smart``): the path map names the register (``decision_register``); the register's
entries are in the initial commit; the ``accepted_reds`` entry is added after it by one commit, the owner's
(``Task: setup``, ``Role: owner`` in its final trailer block) or the orchestrator's. ``--base`` is the initial
commit. The listed red ``test_bb_flip`` is an AssertionError at the base and a ZeroDivisionError with the change, so
the judgement alone calls it the change's.

Red on the base: the scoped close reads no ``accepted_reds`` (S5 of W2-115): the listed red refuses ``RED_CAUSED``
and the record has no ``accepted_reds`` or ``accepted_red_findings``. Two cases are green on today's code by
design, as guards: the entry added without ``Role: owner`` (today's close refuses ``RED_CAUSED`` because it reads no
list; after the change it must refuse because the entry does not count), and the listed red green at the base (F1).
"""

import w2_193_support as support

FLIP = support.smart.node_of("W2-bb", "bb_flip", "test_bb_flip")
KNOWN = support.smart.node_of("W2-bb", "bb_known", "test_bb_known")
WIDGET_TEST = support.smart.node_of("W2-bb", "bb_widget", "test_bb_reads_the_widget")
ACCEPTED, PROPOSED = "DEC-901", "DEC-902"
OWNER_STATUS = "ACCEPTED (owner, 2026-11-16)"


def _test_file(told, node, body):
    rel, name = node.split("::")
    return {rel: support.telling(rel, name, told, body, name=name)}


def _project(tmp_path, sandbox, node, body, entry_by="owner", decision=ACCEPTED, status=OWNER_STATUS,
             text="# the widget, CHANGED\n"):
    """The project, the ``accepted_reds`` entry for ``node`` (decision ``decision``, whose register status is
    ``status``) added by ``entry_by``'s commit, then the ticket's change. Returns ``(made, before, run)``."""
    told = tmp_path / "project-told"
    register = "# The decision register\n" + support.register_entry(decision, status, node)
    files = {**_test_file(told, node, body), support.REGISTER_REL: register}
    made = support.project(tmp_path, files=files, path_map={"decision_register": support.REGISTER_REL})
    base = made.initial
    path_map = {support.PATH_MAP_REL: support.path_map_with(
        made, accepted_reds=[support.accepted_entry(node, decision)])}
    if entry_by == "owner":
        support.owner_commit(made, path_map, "the owner accepts a known red of the project's base")
    else:
        support.orchestrator_commit(made, path_map, "an accepted red, added without the owner's role")
    support.work(made, text=text)
    made.ready(sandbox)
    before = support.tickets(made)
    return made, before, support.close(made, sandbox, "--base", base)


def test_a_listed_red_red_at_the_base_is_accepted_with_its_decision_and_no_repair_ticket(tmp_path, sandbox):
    """S3: the owner's entry counts: the close passes and the ticket closes; the record's ``accepted_reds`` names
    the red with its decision; the red's ``reds`` entry is ``caused: false``, ``accepted: DEC-901``,
    ``repair_ticket: null``; no repair ticket in ``.tickets/`` names it."""
    made, before, run = _project(tmp_path, sandbox, FLIP, support.TYPE_FLIP)

    support.assert_closed(made, run)
    front = support.record(made)
    accepted = front.get("accepted_reds")
    assert isinstance(accepted, list), f"the record has no accepted_reds list: {sorted(front)}"
    named = [a for a in accepted if isinstance(a, dict) and a.get("test") == FLIP]
    assert len(named) == 1 and named[0].get("decision") == ACCEPTED, \
        f"accepted_reds does not name {FLIP} with {ACCEPTED}: {accepted}"
    entry = support.red_entry(front, FLIP)
    assert entry.get("caused") is False, f"the accepted red is recorded as the change's: {entry}"
    assert entry.get("accepted") == ACCEPTED, f"the red's entry does not name its decision: {entry}"
    assert entry.get("repair_ticket") is None, f"the accepted red names a repair ticket: {entry}"
    repairs = support.repair_tickets_naming(made, before, FLIP)
    assert not repairs, f"a repair ticket was opened for the accepted red: {repairs}"


def test_the_same_entry_added_without_role_owner_covers_nothing(tmp_path, sandbox):
    """S3: the same entry, added by the orchestrator's commit (``Role: orchestrator``): it does not count, the red's
    judgement stands: refused with RED_CAUSED naming it, the ticket stays open. Green on today's code by design
    (named in the module's docstring)."""
    made, before, run = _project(tmp_path, sandbox, FLIP, support.TYPE_FLIP, entry_by="orchestrator")
    support.assert_caused(made, run, before, FLIP)


def test_an_entry_whose_decision_is_not_accepted_is_named_in_the_record_and_covers_nothing(tmp_path, sandbox):
    """S3: an entry whose decision is ``PROPOSED`` (not an ACCEPTED owner entry) for a red that is red at the base
    with the same failure type: the close passes (the red is a base red), the record's ``accepted_red_findings``
    names the entry's test, and the red is not accepted (``accepted`` null) and is listed as any other base red,
    with no repair ticket (``repair_ticket`` null, no new file in ``.tickets/``).

    Rewrite-Reason: EMERGENCY-2 4.2, W2-193 S6: a base red opens no repair ticket (it asserted a repair ticket
    for the red)."""
    made, before, run = _project(tmp_path, sandbox, KNOWN, support.KNOWN_RED, decision=PROPOSED, status="PROPOSED")

    support.assert_closed(made, run)
    front = support.record(made)
    findings = front.get("accepted_red_findings")
    assert isinstance(findings, list), f"the record has no accepted_red_findings list: {sorted(front)}"
    assert any(isinstance(f, dict) and f.get("test") == KNOWN and f.get("code") for f in findings), \
        f"accepted_red_findings does not name the entry for {KNOWN}: {findings}"
    accepted = front.get("accepted_reds") or []
    assert not any(isinstance(a, dict) and a.get("test") == KNOWN for a in accepted), \
        f"an entry that does not count accepted the red: {accepted}"
    entry = support.red_entry(front, KNOWN)
    assert entry.get("caused") is False and entry.get("accepted") is None, \
        f"the base red's entry is not a plain base red: {entry}"
    assert entry.get("repair_ticket") is None, f"the base red names a repair ticket: {entry}"
    assert support.tickets(made) == before, f"the close created tickets: {support.tickets(made) - before}"


def test_a_listed_red_green_at_the_base_refuses(tmp_path, sandbox):
    """F1: the owner's entry counts, but its test passes at the base and the change breaks it (new with the
    change): refused with RED_CAUSED naming it, the ticket stays open, no repair ticket. Green on today's code by
    design (today the scoped close reads no list); it guards that a counted entry never excuses a new red."""
    made, before, run = _project(tmp_path, sandbox, WIDGET_TEST, support.NOT_BROKEN,
                                 text="# the widget, CHANGED BROKEN\n")
    support.assert_caused(made, run, before, WIDGET_TEST)
