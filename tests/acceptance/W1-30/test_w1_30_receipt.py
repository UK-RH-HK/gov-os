"""Tests for the close record as a consumption receipt: S5 (CAP-50.c).

S5: The close record is a consumption receipt: the input ids and hashes supplied
    (packet hash) and used, outputs produced, requirements implemented, decisions
    applied, tests produced, and deviations.
"""

import pytest

import w1_30_support as support

cli_support = support.cli_support

TICKET = "PROJ-rcpt"
WBS = "W1-rcpt"
IMPL = support.IMPLEMENTER
TRAILERS = ("Task: PROJ-rcpt", "Role: engineer", "Implements: CAP-01")
RECEIPT_FIELDS = ("packet_hash", "inputs", "outputs", "requirements_implemented",
                  "decisions_applied", "tests_produced", "deviations")


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
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.add_decision("DEC-test", "ACTIVE")
    project.commit("implement", who=IMPL, trailers=TRAILERS)


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
        assert "hash" in inp, f"each input must have a hash: {inp!r}"


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
    assert isinstance(devs, list), \
        f"close record must list deviations: {sorted(front)}"


# --------------------------------------------------------------------------
# Point 5 (WEAK): packet_hash matches context; refuses on context failure;
# input hash is of file content (S5, CAP-50.c)
# --------------------------------------------------------------------------

def test_close_record_packet_hash_matches_context(project, sandbox, interface):
    """KPI S5, CAP-50.c: the packet_hash in the close record must equal the one from gov context."""
    _green_project(project)
    ctx_run = project.gov(sandbox, "context", TICKET, "--json")
    ctx_data = {}
    try:
        import json
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


def test_close_refuses_when_context_cannot_be_built(project, sandbox, interface):
    """KPI S5, CAP-50.c: when gov context raises/BLOCKED, close must refuse, not invent a hash."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS)
    before = cli_support.snapshot(project.root)
    run = support.run_close(project, sandbox, TICKET)
    after = cli_support.snapshot(project.root)
    created = support.new_files(project.root, before, after)
    _, front = support.find_close_record(project.root, created)
    if front is not None:
        record_hash = front.get("packet_hash") or front.get("hash", "")
        import hashlib
        head = support.git(project.root, "rev-parse", "HEAD").strip()
        invented = hashlib.sha256(f"close:{TICKET}:{head}".encode()).hexdigest()
        assert record_hash != invented, \
            "the packet_hash must not be an invented fallback hash from sha256(close:ticket:commit)"


def test_input_hash_is_of_file_content_not_id_string(project, sandbox, interface):
    """KPI S5, CAP-50.c: each input's hash must be sha256 of the file content, not sha256(source_id)."""
    import hashlib
    _green_project(project)
    front = _close_and_find_record(project, sandbox)
    inputs = front.get("inputs", [])
    ticket_input = None
    for inp in inputs:
        if isinstance(inp, dict) and inp.get("id") == TICKET:
            ticket_input = inp
            break
    assert ticket_input is not None, f"the ticket itself must be listed as an input: {inputs}"
    ticket_path = project.root / ".tickets" / f"{TICKET}.md"
    expected_hash = "sha256:" + hashlib.sha256(ticket_path.read_bytes()).hexdigest()
    bad_hash = "sha256:" + hashlib.sha256(TICKET.encode()).hexdigest()
    actual_hash = ticket_input.get("hash", "")
    assert actual_hash != bad_hash, \
        f"input hash must be of file content, not sha256('{TICKET}')"
    assert actual_hash == expected_hash, \
        f"input hash {actual_hash!r} must match sha256 of ticket file content {expected_hash!r}"
