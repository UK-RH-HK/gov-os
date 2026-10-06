"""KPI F-1: a planted defect of any listed family passes.

Each test builds a temporary repository, plants a defect of one family, runs
``gov check --json``, and asserts that the check is RED (not GREEN or absent).
"""

from __future__ import annotations

import json

import pytest

import w1_26_support as support

cli_support = support.cli_support


# --------------------------------------------------------------------------
# 1. schema/invariants: a record whose frontmatter fails its schema
# --------------------------------------------------------------------------

def test_planted_schema_defect_ticket_missing_kpis(project, sandbox, interface):
    """A ticket without the required ``kpis`` field fails the schema check."""
    project.write(".tickets/BAD-aaaa.md",
                  "---\nid: BAD-aaaa\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: Bad ticket\nrole: engineer\nallowed_paths:\n- src/**\n---\n# BAD-aaaa\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


def test_planted_schema_defect_decision_missing_status(project, sandbox, interface):
    """A decision record without ``status`` fails the schema check."""
    project.write("docs/adr/BAD-0001.md",
                  "---\nid: BAD-0001\ntype: decision\nstate_class: AUTHORITATIVE\n"
                  "title: Bad decision\n---\n# BAD-0001\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


# --------------------------------------------------------------------------
# 2. graph integrity: dangling depends_on, duplicate id, id outside grammar
# --------------------------------------------------------------------------

def test_planted_graph_defect_dangling_depends_on(project, sandbox, interface):
    """A record with a depends_on pointing to a nonexistent id fails the graph check."""
    project.add_decision("DEC-001", "ACTIVE", depends_on=["NONEXISTENT-999"])
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


def test_planted_graph_defect_duplicate_id(project, sandbox, interface):
    """Two records with the same id fail the graph check."""
    project.add_decision("DEC-001", "ACTIVE")
    project.write("docs/adr/DEC-001-copy.md",
                  support.decision("DEC-001", "PROPOSED"))
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


def test_planted_graph_defect_id_outside_grammar(project, sandbox, interface):
    """A record with an id that does not match the grammar fails."""
    project.write("docs/adr/bad.md",
                  "---\nid: '!!!INVALID!!!'\ntype: decision\nstatus: ACTIVE\n"
                  "state_class: AUTHORITATIVE\ntitle: Bad id\n---\n# Bad\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


# --------------------------------------------------------------------------
# 3. authority/role limits: the decision checker's own findings
# --------------------------------------------------------------------------

def test_planted_authority_defect_active_while_superseded(project, sandbox, interface):
    """A decision marked ACTIVE that is superseded by another fails."""
    project.add_decision("ADR-0001", "ACTIVE", superseded_by="ADR-0002")
    project.add_decision("ADR-0002", "ACTIVE", supersedes=["ADR-0001"])
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


# --------------------------------------------------------------------------
# 4. mutation scope: implementer allowed_paths covers tests/acceptance/**
# --------------------------------------------------------------------------

def test_planted_mutation_defect_implementer_covers_acceptance(project, sandbox, interface):
    """An implementer ticket whose allowed_paths includes tests/acceptance/** fails."""
    project.write(".tickets/IMPL-aaaa.md",
                  "---\nid: IMPL-aaaa\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: Bad implementer\nclass: implementation\nrole: engineer\n"
                  "allowed_paths:\n- src/**\n- tests/acceptance/**\n"
                  "kpis:\n  success:\n  - works\n  failure: []\n"
                  "---\n# IMPL-aaaa\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


def test_planted_mutation_defect_implementer_covers_acceptance_subpath(project, sandbox, interface):
    """An implementer whose allowed_paths covers a specific acceptance path also fails."""
    project.write(".tickets/IMPL-bbbb.md",
                  "---\nid: IMPL-bbbb\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: Bad implementer 2\nclass: implementation\nrole: engineer\n"
                  "allowed_paths:\n- src/**\n- tests/acceptance/W1-99/**\n"
                  "kpis:\n  success:\n  - works\n  failure: []\n"
                  "---\n# IMPL-bbbb\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


# --------------------------------------------------------------------------
# 5. path-map compliance: tracked file matches no namespace or matches two
# --------------------------------------------------------------------------

def test_planted_pathmap_defect_file_matches_no_namespace(project, sandbox, interface):
    """A tracked file that matches no namespace in the path map fails."""
    project.add_path_map({"src-only": ["src/**"]})
    project.write("orphan-file.txt", "This file has no namespace.\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


def test_planted_pathmap_defect_file_matches_two_namespaces(project, sandbox, interface):
    """A tracked file that matches two namespaces in the path map fails."""
    project.add_path_map({
        "everything": ["**/*"],
        "also-everything": ["**/*"],
    })
    project.write("some-file.txt", "Covered twice.\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


# --------------------------------------------------------------------------
# 6. concurrency/claims: ticket DAG cycle, missing required fields
# --------------------------------------------------------------------------

def test_planted_claims_defect_ticket_dag_cycle(project, sandbox, interface):
    """Two tickets whose depends_on form a cycle fail."""
    project.write(".tickets/CYC-aaaa.md",
                  "---\nid: CYC-aaaa\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: Cycle A\nrole: engineer\nallowed_paths:\n- src/a/**\n"
                  "depends_on:\n- W1-99\nwbs_id: W1-98\n"
                  "kpis:\n  success:\n  - works\n  failure: []\n---\n# CYC-aaaa\n")
    project.write(".tickets/CYC-bbbb.md",
                  "---\nid: CYC-bbbb\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: Cycle B\nrole: engineer\nallowed_paths:\n- src/b/**\n"
                  "depends_on:\n- W1-98\nwbs_id: W1-99\n"
                  "kpis:\n  success:\n  - works\n  failure: []\n---\n# CYC-bbbb\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


def test_planted_claims_defect_ticket_missing_required_field(project, sandbox, interface):
    """A ticket missing a required field (``role``) fails."""
    project.write(".tickets/BAD-cccc.md",
                  "---\nid: BAD-cccc\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: No role\nallowed_paths:\n- src/**\n"
                  "kpis:\n  success:\n  - works\n  failure: []\n---\n# BAD-cccc\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


# --------------------------------------------------------------------------
# 7. command-contract consistency: reserved command with no module file
# --------------------------------------------------------------------------

def test_planted_commands_defect_reserved_command_no_module(project, sandbox, interface):
    """A reserved command with no module file raises a finding."""
    project.add_check_declaration("w1-26-cmd-check", "command-contract consistency",
                                  severity="hard-block",
                                  command="python3 -m gov.check.commands")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    status = support.family_status(result, "command-contract consistency")
    assert status in (support.RED, support.YELLOW), \
        f"the command-contract check did not flag a missing module: {status}"


# --------------------------------------------------------------------------
# 8. fail-open: record without a ``type`` field silently skipped by schema
# --------------------------------------------------------------------------

def test_planted_schema_defect_record_missing_type(project, sandbox, interface):
    """A record file whose frontmatter has no ``type`` field must be flagged, not silently skipped."""
    project.write("docs/adr/NO-TYPE-001.md",
                  "---\nid: NO-TYPE-001\nstatus: ACTIVE\nstate_class: AUTHORITATIVE\n"
                  "title: Missing type field\n---\n# NO-TYPE-001\n")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    status = support.family_status(result, "schema/invariants")
    assert status == support.RED, (
        f"a record without a 'type' field was silently skipped; "
        f"schema/invariants is {status!r}, expected RED\n{run.describe()}"
    )


def test_planted_schema_defect_record_type_null(project, sandbox, interface):
    """A record with ``type: null`` must be flagged, not silently skipped."""
    project.write("docs/adr/NULL-TYPE-001.md",
                  "---\nid: NULL-TYPE-001\ntype: null\nstatus: ACTIVE\n"
                  "state_class: AUTHORITATIVE\ntitle: Null type\n---\n# NULL-TYPE-001\n")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    status = support.family_status(result, "schema/invariants")
    assert status == support.RED, (
        f"a record with 'type: null' was silently skipped; "
        f"schema/invariants is {status!r}, expected RED\n{run.describe()}"
    )


def test_planted_schema_defect_record_type_non_string(project, sandbox, interface):
    """A record with ``type: 42`` (non-string) must be flagged, not silently skipped."""
    project.write("docs/adr/INT-TYPE-001.md",
                  "---\nid: INT-TYPE-001\ntype: 42\nstatus: ACTIVE\n"
                  "state_class: AUTHORITATIVE\ntitle: Integer type\n---\n# INT-TYPE-001\n")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    status = support.family_status(result, "schema/invariants")
    assert status == support.RED, (
        f"a record with 'type: 42' was silently skipped; "
        f"schema/invariants is {status!r}, expected RED\n{run.describe()}"
    )


# --------------------------------------------------------------------------
# 9. fail-open: decision checker exception swallowed by bare except
# --------------------------------------------------------------------------

def test_planted_authority_defect_decision_checker_exception_not_swallowed(
        project, sandbox, interface):
    """When the decision checker raises, the authority family must not be GREEN.

    The bare ``except Exception: pass`` in authority.py swallows failures and
    lets the family pass silently. The correct behaviour is to report the error
    as a YELLOW or RED finding.
    """
    project.write("src/gov/decisions/__init__.py", "")
    project.write("src/gov/decisions/checker.py",
                  "def check(root):\n    raise RuntimeError('checker is broken')\n")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    status = support.family_status(result, "authority/role limits")
    assert status in (support.RED, support.YELLOW), (
        f"the decision checker raised but authority/role limits is {status!r}; "
        f"the exception was silently swallowed\n{run.describe()}"
    )


# --------------------------------------------------------------------------
# 10. fail-open: DAG cycle missed when depends_on uses ticket id vs wbs_id
# --------------------------------------------------------------------------

def test_planted_claims_defect_dag_cycle_ticket_id_vs_wbs_id(project, sandbox, interface):
    """A self-dependency via ticket-id in depends_on vs wbs_id graph keys must be detected.

    The cycle detector uses wbs_id as node keys but adds depends_on targets
    (which may be ticket ids) as raw edge targets without resolving through the
    wbs_to_id mapping, so a cycle involving mixed id spaces goes undetected.
    """
    project.write(".tickets/SELF-aaaa.md",
                  "---\nid: SELF-aaaa\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: Self-dep via ticket id\nrole: engineer\n"
                  "allowed_paths:\n- src/a/**\n"
                  "wbs_id: W1-50\ndepends_on:\n- SELF-aaaa\n"
                  "kpis:\n  success:\n  - works\n  failure: []\n---\n# SELF-aaaa\n")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    status = support.family_status(result, "concurrency/claims")
    assert status == support.RED, (
        f"a ticket depending on itself (by ticket id, graph keyed by wbs_id) was not "
        f"detected as a cycle; concurrency/claims is {status!r}, expected RED\n{run.describe()}"
    )
