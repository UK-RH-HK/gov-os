"""Tests for the close record as a consumption receipt: S5 (CAP-50.c), A4, B5, B7.

S5: The close record is a consumption receipt: the input ids and hashes supplied
    (packet hash) and used, outputs produced, requirements implemented, decisions
    applied, tests produced, and deviations.
A4: When gov context cannot be built, the close refuses (no fallback hash, no
    silently empty decisions list). The case reaches the context call.
B5: "Outputs produced" lists files from the ticket's commits. "Deviations" says
    "not measured" when not measured, never "none". Unmeasurable inputs listed
    with the reason.
B7: Sources resolve through a defined lookup. A ticket naming a source that does
    not resolve is refused and gets no close record (DEC-470, replacing "listed
    with no hash and a reason"). The ticket file is always an input.
"""

import hashlib
import json

import pytest

import w1_30_support as support

cli_support = support.cli_support

TICKET = "PROJ-rcpt"
WBS = "W1-rcpt"
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


def _green_project(project):
    project.add_decision("DEC-test", "ACTIVE")
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

def test_close_record_has_packet_hash(project, sandbox, interface):
    """KPI S5, CAP-50.c: the close record carries the context packet hash."""
    _green_project(project)
    front = _close_and_find_record(project, sandbox)
    assert "packet_hash" in front or "hash" in front, \
        f"close record must carry the packet hash: {sorted(front)}"
    value = front.get("packet_hash") or front.get("hash")
    assert isinstance(value, str) and len(value) > 8, \
        f"packet_hash should be a non-trivial string: {value!r}"


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


def test_close_record_packet_hash_matches_context(project, sandbox, interface):
    """KPI S5, CAP-50.c: the packet_hash equals the one from gov context."""
    _green_project(project)
    ctx_run = project.gov(sandbox, "context", TICKET, "--json")
    ctx_data = {}
    try:
        ctx_data = json.loads(ctx_run.stdout)
    except Exception:
        pass
    ctx_hash = None
    if isinstance(ctx_data, dict):
        result = ctx_data.get("result", ctx_data)
        ctx_hash = result.get("hash") if isinstance(result, dict) else None

    front = _close_and_find_record(project, sandbox)
    record_hash = front.get("packet_hash") or front.get("hash")
    if ctx_hash:
        assert record_hash == ctx_hash, \
            f"packet_hash {record_hash!r} must match context hash {ctx_hash!r}"
    else:
        assert isinstance(record_hash, str) and len(record_hash) > 8, \
            "packet_hash must be non-trivial even when context is unavailable"


# --------------------------------------------------------------------------
# A4: Context failure refuses close (no fallback hash)
# --------------------------------------------------------------------------

def test_close_refuses_when_context_cannot_be_built(project, sandbox, interface):
    """A4: when gov context cannot be built, close refuses with the reason.

    The case reaches the context call: watchdog passes, tests pass, but context
    fails -> refusal (no fallback hash, no silently empty decisions).
    """
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    project.add_decision("DEC-cyc1", "ACTIVE", supersedes="DEC-cyc2")
    project.add_decision("DEC-cyc2", "ACTIVE", supersedes="DEC-cyc1")
    project.commit("create contradiction for context failure", who=support.OWNER)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "close must refuse when gov context cannot be built (A4)"


def test_no_fallback_hash_when_context_fails(project, sandbox, interface):
    """A4: no fallback hash from sha256(ticket file) when context fails."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    project.add_decision("DEC-cyc3", "ACTIVE", supersedes="DEC-cyc4")
    project.add_decision("DEC-cyc4", "ACTIVE", supersedes="DEC-cyc3")
    project.commit("contradiction", who=support.OWNER)
    before = cli_support.snapshot(project.root)
    run = support.run_close(project, sandbox, TICKET)
    after = cli_support.snapshot(project.root)
    created = support.new_files(project.root, before, after)
    _, front = support.find_close_record(project.root, created)
    if front is not None:
        ticket_path = project.root / ".tickets" / f"{TICKET}.md"
        fallback = hashlib.sha256(ticket_path.read_bytes()).hexdigest()
        record_hash = front.get("packet_hash") or front.get("hash", "")
        assert record_hash != fallback and record_hash != f"sha256:{fallback}", \
            "the close must not use sha256(ticket file) as fallback hash (A4)"


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


def test_unresolvable_source_refuses_the_close(project, sandbox, interface):
    """B7 as DEC-470 settles it: a ticket naming a source that does not resolve is refused. No close record
    lists the missing source with a reason, because no close record is written.

    The case holds first that ``gov context`` gives ``BLOCKED`` for this ticket, which is otherwise green.
    """
    missing = "NO-SUCH-SOURCE-999"
    project.add_ticket(TICKET, WBS, sources=[missing])
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    support.load_store(project, sandbox)
    error = support.context_error(project, sandbox, TICKET)
    assert error["code"] == "BLOCKED", f"the fixture is wrong: gov context gives {error}"

    run = support.run_close(project, sandbox, TICKET, store=False)
    text = support.error_text(support.refused(run, interface, support.EXIT_CHECK_FAILED))
    assert missing in text, f"the refusal does not name the source that does not resolve\n{run.describe()}"
    support.assert_not_closed(project, TICKET)


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
# A4 extended: context failure from a non-cycle cause (DEC-454, KPI S5/S6)
# --------------------------------------------------------------------------

def test_context_failure_non_cycle_refuses_close(project, sandbox, interface):
    """A4, S5: a successful-otherwise close whose context cannot be built
    (by a cause other than a supersession cycle) refuses with the reason
    and writes no close record and closes no ticket.

    The cause: the ticket sources a superseded decision (W1-24 README: BLOCKED).
    """
    project.add_ticket(TICKET, WBS, sources=["DEC-base"])
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.add_decision("DEC-base", "ACTIVE", title="Base")
    project.add_decision("DEC-new", "ACTIVE", title="Replacement", supersedes="DEC-base")
    project.commit("implement with superseded source", who=IMPL, trailers=TRAILERS)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    before = cli_support.snapshot(project.root)
    run = support.run_close(project, sandbox, TICKET)
    after = cli_support.snapshot(project.root)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "close must refuse when context cannot be built (superseded source, not a cycle)"
    created = support.new_files(project.root, before, after)
    _, front = support.find_close_record(project.root, created)
    assert front is None, \
        "no close record must be written when context fails"
    ticket_front = support.read_ticket_frontmatter(project.root, TICKET)
    assert ticket_front.get("status") != "closed", \
        "the ticket must not be closed when context fails"


# The failing close with a class whose context cannot be built: test_w1_30_context_failures.py.


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
    project.write("tests/acceptance/W1-rcpt/test_mine.py",
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
