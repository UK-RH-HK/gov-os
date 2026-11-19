"""Tests for the close record as a consumption receipt: S5 (CAP-50.c), A4, B5, B7.

S5: The close record is a consumption receipt: the input ids and hashes supplied
    and used, outputs produced, requirements implemented, decisions applied,
    tests produced, and deviations. Since DEC-1214 M1 (W2-200) the decisions
    applied come from the ticket's own sources, resolved in the register by id,
    each with the hash of its span; the record has no packet hash.
A4: (retired with the context command, DEC-1214 M1: the close builds no packet,
    so no packet can fail; its three cases are deleted.)
B5: "Outputs produced" lists files from the ticket's commits. "Deviations" says
    "not measured" when not measured, never "none". Unmeasurable inputs listed
    with the reason.
B7: Sources resolve through a defined lookup. A ticket naming a decision the
    register does not hold closes, and its close record lists the id as
    unresolved, never as applied (W2-200 S6 as amended at the land). The ticket
    file is always an input.
"""

import hashlib

import pytest

import w1_30_support as support

cli_support = support.cli_support

TICKET = "PROJ-rcpt"
WBS = "W1-935"
IMPL = support.IMPLEMENTER
TRAILERS = ("Task: PROJ-rcpt", "Role: engineer", "Implements: CAP-01")


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _close_and_find_record(project, sandbox):
    """Close the ticket and return the close record frontmatter."""
    before = cli_support.snapshot(project.root)
    support.run_close(project, sandbox, TICKET)
    after = cli_support.snapshot(project.root)
    created = support.new_files(project.root, before, after)
    _, front = support.find_close_record(project.root, created)
    assert front is not None, f"no close record among new files: {created}"
    return front


REGISTER_REL = "docs/DECISION_REGISTER.md"
REGISTER_HEAD = "# Decision register\n\n"
DECISION_ENTRY = "### DEC-9101 — The receipt names its decisions\n- **Status:** ACCEPTED (owner)\n\nIts text.\n"


def _with_register(project, entries=DECISION_ENTRY):
    """The project's path map names a register holding ``entries`` (DEC-1214 M1, W2-200: the close resolves the
    ticket's decisions there)."""
    project.write(support.PATH_MAP_REL,
                  support.path_map_text({**support.SUITE_SETTINGS, "decision_register": REGISTER_REL}))
    project.write(REGISTER_REL, REGISTER_HEAD + entries)
    project.commit("the register", who=support.OWNER)


def _add_ticket_citing(project, *sources):
    """The fixture's ticket with ``sources`` in place of the one source every fixture ticket names: a second
    ``sources`` key beside the first makes the frontmatter unreadable (``core-authority`` RED, the close refused)."""
    project.add_ticket(TICKET, WBS)
    rel = support.ticket_path(TICKET)
    text = (project.root / rel).read_text(encoding="utf-8")
    base = f"sources:\n- {support.BASE_SOURCE}\n"
    assert text.count(base) == 1, f"the fixture ticket no longer names its one source as {base!r}"
    project.write(rel, text.replace(base, "sources:\n" + "".join(f"- {source}\n" for source in sources)))


def _span_hashes(text):
    """The sha256 forms of the one entry's span: with or without the line break that ends it."""
    return {"sha256:" + hashlib.sha256(form.encode("utf-8")).hexdigest()
            for form in (text, text.rstrip("\n"))}


def _green_project(project):
    project.add_decision("DEC-9021", "ACTIVE")
    project.commit("a decision", who=support.OWNER)
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)


# --------------------------------------------------------------------------
# S5: The close record is a consumption receipt (CAP-50.c)
# --------------------------------------------------------------------------

def test_close_record_names_its_decisions_and_has_no_packet_hash(project, sandbox, interface):
    """KPI S5, CAP-50.c: the close record names the decisions it applied, those that no longer stand and those it
    could not resolve, each a list; it carries no packet hash.

    Rewrite-Reason: DEC-1214 M1 (W2-200 S3): was ``test_close_record_has_packet_hash``; the close builds no context
    packet, so the receipt has no ``packet_hash`` and states its decisions in three lists."""
    _green_project(project)
    front = _close_and_find_record(project, sandbox)
    assert "packet_hash" not in front, f"the close record still carries a packet hash: {front.get('packet_hash')!r}"
    for key in ("decisions_applied", "decisions_not_standing", "decisions_unresolved"):
        assert isinstance(front.get(key), list), f"the close record has no list {key}: {sorted(front)}"


def test_close_record_has_input_ids_and_hashes(project, sandbox, interface):
    """KPI S5, CAP-50.c: the close record lists input ids and their hashes."""
    _green_project(project)
    front = _close_and_find_record(project, sandbox)
    inputs = front.get("inputs")
    assert isinstance(inputs, list) and len(inputs) >= 1, \
        f"close record must list inputs: {front}"
    for inp in inputs:
        assert isinstance(inp, dict), f"each input must be a dict: {inp!r}"
        assert "id" in inp, f"each input must have an id: {inp!r}"


def test_close_record_has_outputs(project, sandbox, interface):
    """KPI S5, CAP-50.c: the close record lists outputs produced."""
    _green_project(project)
    front = _close_and_find_record(project, sandbox)
    outputs = front.get("outputs")
    assert isinstance(outputs, list), f"close record must list outputs: {sorted(front)}"


def test_close_record_has_requirements_implemented(project, sandbox, interface):
    """KPI S5, CAP-50.c: the close record lists requirements implemented."""
    _green_project(project)
    front = _close_and_find_record(project, sandbox)
    reqs = front.get("requirements_implemented")
    assert isinstance(reqs, list), \
        f"close record must list requirements_implemented: {sorted(front)}"


def test_close_record_has_decisions_applied(project, sandbox, interface):
    """KPI S5, CAP-50.c: the close record lists decisions applied."""
    _green_project(project)
    front = _close_and_find_record(project, sandbox)
    decs = front.get("decisions_applied")
    assert isinstance(decs, list), \
        f"close record must list decisions_applied: {sorted(front)}"


def test_close_record_has_tests_and_deviations(project, sandbox, interface):
    """KPI S5, CAP-50.c: the close record lists tests produced and deviations."""
    _green_project(project)
    front = _close_and_find_record(project, sandbox)
    tests = front.get("tests_produced")
    assert isinstance(tests, list), \
        f"close record must list tests_produced: {sorted(front)}"
    devs = front.get("deviations")
    assert devs is not None, \
        f"close record must have a deviations field: {sorted(front)}"


def test_close_record_decisions_come_from_the_ticket_s_sources_with_their_span_hashes(project, sandbox, interface):
    """KPI S5, CAP-50.c: a decision the ticket names in its sources, held by the register, is applied, and the
    inputs name it with the hash of its span of the register at HEAD.

    Rewrite-Reason: DEC-1214 M1 (W2-200 S3): was ``test_close_record_packet_hash_matches_context``, which compared
    the record's packet hash with the retired context command's; the receipt's decisions now come from the ticket's
    own sources, resolved in the register by id, each hashed by its span."""
    _with_register(project)
    _add_ticket_citing(project, "DEC-9101")
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    front = _close_and_find_record(project, sandbox)
    assert front.get("decisions_applied") == ["DEC-9101"], f"decisions_applied: {front.get('decisions_applied')!r}"
    hashes = {item.get("id"): item.get("hash") for item in front.get("inputs", []) if isinstance(item, dict)}
    assert hashes.get("DEC-9101") in _span_hashes(DECISION_ENTRY), \
        f"DEC-9101's input hash is not that of its span: {front.get('inputs')!r}"
    assert "packet_hash" not in front


# --------------------------------------------------------------------------
# B5: Receipt field details
# --------------------------------------------------------------------------

def test_outputs_lists_files_from_ticket_commits(project, sandbox, interface):
    """B5: the outputs field lists files the ticket's commits produced or changed."""
    _green_project(project)
    front = _close_and_find_record(project, sandbox)
    outputs = front.get("outputs", [])
    assert isinstance(outputs, list), "outputs must be a list"
    output_strs = [str(o) for o in outputs]
    all_outputs = " ".join(output_strs)
    assert "feature.py" in all_outputs or "src/example" in all_outputs, \
        f"outputs must include files from the ticket's commits (e.g. feature.py): {outputs}"


def test_deviations_says_not_measured_when_unverified(project, sandbox, interface):
    """B5: deviations says 'not measured' when not measured, never 'none' or empty."""
    _green_project(project)
    front = _close_and_find_record(project, sandbox)
    devs = front.get("deviations")
    if isinstance(devs, list) and len(devs) == 0:
        pytest.fail("deviations must not be an empty list when not measured; use 'not measured'")
    if isinstance(devs, str) and devs.lower() == "none":
        pytest.fail("deviations must say 'not measured', not 'none'")


def test_input_hash_is_of_file_content(project, sandbox, interface):
    """B5, S5: each input's hash is sha256 of the ticket file as supplied to the close,
    before gov close changes its status.

    Revised after implementation: the case hashed the file after close (when the
    status had changed) and so the hash never matched.
    """
    _green_project(project)
    ticket_path = project.root / ".tickets" / f"{TICKET}.md"
    content_before_close = ticket_path.read_bytes()
    expected_hash = "sha256:" + hashlib.sha256(content_before_close).hexdigest()
    bad_hash = "sha256:" + hashlib.sha256(TICKET.encode()).hexdigest()
    front = _close_and_find_record(project, sandbox)
    inputs = front.get("inputs", [])
    ticket_input = None
    for inp in inputs:
        if isinstance(inp, dict) and inp.get("id") == TICKET:
            ticket_input = inp
            break
    assert ticket_input is not None, f"the ticket itself must be listed as an input: {inputs}"
    actual_hash = ticket_input.get("hash", "")
    assert actual_hash != bad_hash, \
        f"input hash must be of file content, not sha256('{TICKET}')"
    assert actual_hash == expected_hash, \
        f"input hash {actual_hash!r} must match sha256 of ticket file content {expected_hash!r}"


def test_unmeasurable_inputs_listed_with_reason(project, sandbox, interface):
    """B5: inputs that cannot be measured are listed with 'not measured' reason."""
    _green_project(project)
    front = _close_and_find_record(project, sandbox)
    inputs = front.get("inputs", [])
    for inp in inputs:
        if isinstance(inp, dict):
            h = inp.get("hash")
            if h is None or h == "":
                reason = inp.get("reason") or inp.get("note")
                assert reason is not None, \
                    f"an input with no hash must have a reason: {inp}"


# --------------------------------------------------------------------------
# B7: Source resolution
# --------------------------------------------------------------------------

def test_ticket_file_is_always_an_input(project, sandbox, interface):
    """B7: the ticket file itself is always included as an input."""
    _green_project(project)
    front = _close_and_find_record(project, sandbox)
    inputs = front.get("inputs", [])
    ids = [inp.get("id") for inp in inputs if isinstance(inp, dict)]
    assert TICKET in ids, \
        f"the ticket file must always be listed as an input: {ids}"


def test_unresolvable_source_is_recorded_unresolved_and_the_close_goes_on(project, sandbox, interface):
    """B7 as W2-200 S6 settles it: a ticket naming in its sources a decision the register does not hold closes all
    the same; its close record lists that id as unresolved, and neither applies it nor gives it a hash.

    Rewrite-Reason: DEC-1214 M1 (W2-200 S6 and F1 as the CTO amended them at the land; EMERGENCY-2 2.1): was
    ``test_unresolvable_source_refuses_the_close``, which asked for the refusal ``DECISION_NOT_FOUND``; an id no
    register holds is now recorded in ``decisions_unresolved`` and the close goes on."""
    missing = "DEC-9199"
    _with_register(project)
    _add_ticket_citing(project, "DEC-9101", missing)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)

    run = support.run_close(project, sandbox, TICKET)
    support.result_of(run, interface)
    records = support.close_records(project.root, TICKET)
    assert len(records) == 1, f"the close left {len(records)} close records: {[rel for rel, _ in records]}"
    front = records[0][1]
    assert front.get("decisions_unresolved") == [missing], f"decisions_unresolved: {front.get('decisions_unresolved')!r}"
    assert front.get("decisions_applied") == ["DEC-9101"], f"decisions_applied: {front.get('decisions_applied')!r}"
    hashed = [inp.get("id") for inp in front.get("inputs") or [] if isinstance(inp, dict)]
    assert missing not in hashed, f"{missing}, which the register does not hold, is among the inputs: {hashed}"


def test_sources_resolve_through_defined_lookup(project, sandbox, interface):
    """B7: sources resolve through a defined lookup, not a tree-wide search."""
    _green_project(project)
    front = _close_and_find_record(project, sandbox)
    inputs = front.get("inputs", [])
    assert len(inputs) >= 1, "close record must have at least one input (the ticket)"
    for inp in inputs:
        if isinstance(inp, dict) and inp.get("id") == TICKET:
            h = inp.get("hash", "")
            assert h and len(h) > 8, \
                f"the ticket file input must have a real hash: {inp}"


# --------------------------------------------------------------------------
# B5 extended: tests_produced lists the ticket's own test files (KPI S5)
# --------------------------------------------------------------------------

def test_tests_produced_lists_ticket_own_tests(project, sandbox, interface):
    """KPI S5: 'tests produced' lists the test files the ticket's own commits
    added or changed (and the ticket's acceptance folder), not every test file
    of the project.
    """
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    support.write(project.root, "tests/unit/preexisting/test_other.py",
                  "def test_other():\n    assert True\n")
    project.commit("set up pre-existing tests", who=support.ORCHESTRATOR)
    project.write("tests/acceptance/W1-935/test_mine.py",
                  "def test_mine():\n    assert True\n")
    project.commit("implement and add own test", who=IMPL, trailers=TRAILERS)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    front = _close_and_find_record(project, sandbox)
    tests_produced = front.get("tests_produced", [])
    assert isinstance(tests_produced, list), "tests_produced must be a list"
    produced_str = " ".join(str(t) for t in tests_produced)
    assert "test_other" not in produced_str, \
        f"tests_produced must not include another ticket's pre-existing tests: {tests_produced}"
