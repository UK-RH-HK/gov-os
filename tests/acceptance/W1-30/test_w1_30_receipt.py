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
