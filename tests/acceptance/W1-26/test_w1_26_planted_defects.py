"""KPI F-1: a planted defect of any listed family passes.

Each test builds a temporary repository, plants a defect of one family, runs
``gov check --json``, and asserts that the check is RED (not GREEN or absent).

Revised (W2-67, I2 §2.7 R1 and F3): the base project was red before any defect,
so a case that judged its defect by "gov check failed" could not fail. The
revised cases plant their defect on the green base (``green_project``,
``test_w1_26_green_base.py``) and assert the named check's own entry RED with a
finding that names the defect. The two path-map cases ride with the path-map
check's fix (P-I2-4, P-IS-9) and are unchanged here.
"""

from __future__ import annotations

import json

import pytest

import w1_26_support as support

cli_support = support.cli_support


# --------------------------------------------------------------------------
# 1. schema/invariants: a record whose frontmatter fails its schema
# --------------------------------------------------------------------------

def test_planted_schema_defect_ticket_missing_kpis(green_project, sandbox, interface):
    """A ticket without the required ``kpis`` field fails the schema check: ``core-schema`` is RED with a finding
    that names the ticket and the field."""
    project = green_project
    project.write(".tickets/BAD-aaaa.md",
                  "---\nid: BAD-aaaa\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: Bad ticket\nrole: engineer\nallowed_paths:\n- src/**\n---\n# BAD-aaaa\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_check_red_naming(run, interface, "core-schema", ".tickets/BAD-aaaa.md", "kpis")


def test_planted_schema_defect_decision_missing_status(green_project, sandbox, interface):
    """A decision record without ``status`` fails the schema check: ``core-schema`` is RED with a finding that
    names the record and the field."""
    project = green_project
    project.write("docs/adr/BAD-0001.md",
                  "---\nid: BAD-0001\ntype: decision\nstate_class: AUTHORITATIVE\n"
                  "title: Bad decision\n---\n# BAD-0001\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_check_red_naming(run, interface, "core-schema", "docs/adr/BAD-0001.md", "status")


# --------------------------------------------------------------------------
# 2. graph integrity: dangling depends_on, duplicate id, id outside grammar
# --------------------------------------------------------------------------

def test_planted_graph_defect_dangling_depends_on(green_project, sandbox, interface):
    """A record with a depends_on pointing to a nonexistent id fails the graph check: ``core-graph`` is RED with a
    finding that names the record and the missing target."""
    project = green_project
    project.add_decision("DEC-001", "ACTIVE", depends_on=["NONEXISTENT-999"])
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_check_red_naming(run, interface, "core-graph", "DEC-001", "NONEXISTENT-999")


def test_planted_graph_defect_duplicate_id(green_project, sandbox, interface):
    """Two records with the same id fail the graph check: ``core-graph`` is RED with a finding that names the id
    and both files. (The decision checker's own finding of the same pair is
    ``test_w1_26_decisions.py::test_duplicate_id_flagged``.)"""
    project = green_project
    project.add_decision("DEC-001", "ACTIVE")
    project.write("docs/adr/DEC-001-copy.md",
                  support.decision("DEC-001", "PROPOSED"))
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_check_red_naming(run, interface, "core-graph", "DEC-001", "docs/adr/DEC-001.md",
                                    "docs/adr/DEC-001-copy.md")


def test_planted_graph_defect_id_outside_grammar(green_project, sandbox, interface):
    """A record with an id that does not match the grammar fails: ``core-graph`` is RED with a finding that names
    the record and its id."""
    project = green_project
    project.write("docs/adr/bad.md",
                  "---\nid: '!!!INVALID!!!'\ntype: decision\nstatus: ACTIVE\n"
                  "state_class: AUTHORITATIVE\ntitle: Bad id\n---\n# Bad\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_check_red_naming(run, interface, "core-graph", "docs/adr/bad.md", "!!!INVALID!!!")


# --------------------------------------------------------------------------
# 3. authority/role limits: the decision checker's own findings
# --------------------------------------------------------------------------

def test_planted_authority_defect_active_while_superseded(green_project, sandbox, interface):
    """A decision marked ACTIVE that is superseded by another fails: ``core-authority`` is RED with a finding that
    names the superseded decision's file."""
    project = green_project
    project.add_decision("ADR-0001", "ACTIVE", superseded_by="ADR-0002")
    project.add_decision("ADR-0002", "ACTIVE", supersedes=["ADR-0001"])
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_check_red_naming(run, interface, "core-authority", "ADR-0001", "docs/adr/ADR-0001.md")


# --------------------------------------------------------------------------
# 4. mutation scope: implementer allowed_paths covers tests/acceptance/**
# --------------------------------------------------------------------------

def test_planted_mutation_defect_implementer_covers_acceptance(green_project, sandbox, interface):
    """An implementer ticket whose allowed_paths includes tests/acceptance/** fails: ``core-mutation`` is RED with
    a finding that names the ticket and the pattern."""
    project = green_project
    project.write(".tickets/IMPL-aaaa.md",
                  "---\nid: IMPL-aaaa\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: Bad implementer\nclass: implementation\nrole: engineer\n"
                  "allowed_paths:\n- src/**\n- tests/acceptance/**\n"
                  "kpis:\n  success:\n  - works\n  failure: []\n"
                  "---\n# IMPL-aaaa\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_check_red_naming(run, interface, "core-mutation", ".tickets/IMPL-aaaa.md", "tests/acceptance/**")


def test_planted_mutation_defect_implementer_covers_acceptance_subpath(green_project, sandbox, interface):
    """An implementer whose allowed_paths covers a specific acceptance path also fails: ``core-mutation`` is RED
    with a finding that names the ticket and the pattern."""
    project = green_project
    project.write(".tickets/IMPL-bbbb.md",
                  "---\nid: IMPL-bbbb\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: Bad implementer 2\nclass: implementation\nrole: engineer\n"
                  "allowed_paths:\n- src/**\n- tests/acceptance/W1-99/**\n"
                  "kpis:\n  success:\n  - works\n  failure: []\n"
                  "---\n# IMPL-bbbb\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_check_red_naming(run, interface, "core-mutation", ".tickets/IMPL-bbbb.md",
                                    "tests/acceptance/W1-99/**")


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

def test_planted_claims_defect_ticket_dag_cycle(green_project, sandbox, interface):
    """Two tickets whose depends_on form a cycle fail: ``core-claims`` is RED with a finding that names the cycle
    (one of its two tickets, by ticket id or WBS id); the case also holds that ``core-claims`` has no finding on the
    two tickets once the cycle is broken."""
    project = green_project
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
    cycle = ("CYC-aaaa", "CYC-bbbb", "W1-98", "W1-99")
    support.assert_check_red_naming(run, interface, "core-claims", cycle)
    project.write(".tickets/CYC-bbbb.md",
                  "---\nid: CYC-bbbb\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: Cycle B\nrole: engineer\nallowed_paths:\n- src/b/**\n"
                  "wbs_id: W1-99\n"
                  "kpis:\n  success:\n  - works\n  failure: []\n---\n# CYC-bbbb\n")
    project.commit("break the cycle")
    broken = support.run_check(project, sandbox)
    result, _ = support.result_and_envelope(broken, interface)
    assert not support.findings_naming(support.check_entry(result, "core-claims"), cycle), \
        f"core-claims still has a finding on the two tickets once the cycle is broken\n{broken.describe()}"


def test_planted_claims_defect_ticket_missing_required_field(green_project, sandbox, interface):
    """A ticket missing a required field (``role``) fails: ``core-claims`` is RED with a finding that names the
    ticket and the field."""
    project = green_project
    project.write(".tickets/BAD-cccc.md",
                  "---\nid: BAD-cccc\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: No role\nallowed_paths:\n- src/**\n"
                  "kpis:\n  success:\n  - works\n  failure: []\n---\n# BAD-cccc\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_check_red_naming(run, interface, "core-claims", ".tickets/BAD-cccc.md", "role")


# --------------------------------------------------------------------------
# 7. command-contract consistency: reserved command with no module file
# --------------------------------------------------------------------------

# revised after implementation: W1-41 builds ``gov adopt --lite``, the last
# reserved command, so no reserved command lacks a module any more and the
# case plants the defect in its own temporary project (planned: command
# implemented).
COMMANDS_FAMILY = "command-contract consistency"
COMMANDS_CHECK_ID = "w1-26-cmd-check"
UNBUILT_IN_PROJECT = "adopt"


def _declare_commands_check(project):
    project.add_check_declaration(COMMANDS_CHECK_ID, COMMANDS_FAMILY,
                                  severity="hard-block",
                                  command="python3 -m gov.check.commands")


def _commands_check_findings(result):
    """The findings of this case's declared check, as the result reports them."""
    findings = []
    for entry in support.checks_of(result):
        if isinstance(entry, dict) and COMMANDS_CHECK_ID in (entry.get("id"), entry.get("check_id")):
            findings.extend(entry.get("findings") or [])
    return findings


def test_planted_commands_defect_reserved_command_no_module(project, sandbox, interface):
    """A reserved command with no module file raises a finding that names it."""
    _declare_commands_check(project)
    removed = project.remove_reserved_command_module(UNBUILT_IN_PROJECT)
    assert removed, (
        f"the defect was not planted: the project held no module file for "
        f"{UNBUILT_IN_PROJECT!r} to remove"
    )
    assert not project.reserved_command_module_files(UNBUILT_IN_PROJECT)
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    status = support.family_status(result, COMMANDS_FAMILY)
    assert status in (support.RED, support.YELLOW), \
        f"the command-contract check did not flag a missing module: {status}\n{run.describe()}"
    findings = _commands_check_findings(result)
    assert findings, f"the check reports no finding for the missing module\n{run.describe()}"
    assert any(UNBUILT_IN_PROJECT in json.dumps(finding) for finding in findings), (
        f"no finding of the command-contract check names the command "
        f"{UNBUILT_IN_PROJECT!r}: {findings}"
    )
    for name in support.RESERVED_COMMANDS:
        if name == UNBUILT_IN_PROJECT:
            continue
        assert not any(finding.get("command") == name for finding in findings
                       if isinstance(finding, dict)), (
            f"a finding names {name!r}, whose module file is present: {findings}"
        )


def test_commands_check_green_when_every_reserved_command_has_a_module(project, sandbox, interface):
    """With a module file for each reserved command, the family is green for this declaration."""
    _declare_commands_check(project)
    for name in support.RESERVED_COMMANDS:
        assert project.reserved_command_module_files(name), (
            f"the project holds no module file for the reserved command {name!r}"
        )
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    status = support.family_status(result, COMMANDS_FAMILY)
    assert status == support.GREEN, (
        f"every reserved command has a module file but {COMMANDS_FAMILY} is "
        f"{status!r}\n{run.describe()}"
    )
    assert not _commands_check_findings(result), \
        f"the check reports a finding with nothing planted\n{run.describe()}"


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

# revised after implementation (DEC-864 item 1; Rewrite-Reason: DEC-822 item 3,
# DEC-835): the judge runs every declared check with its own interpreter and
# package, never the judged project's ``src/gov``, so the raising checker is
# planted in the judge's own code. The judge runs from an overlay in the
# case's temporary folder: a ``gov`` and a ``gov.decisions`` package whose
# import path continues into this worktree's ``src/``, so every module is this
# worktree's but ``gov.decisions.checker``. That module runs the real
# checker's source, then replaces ``check`` with one that leaves a marker and
# raises. Nothing of the tree is copied; the judged project is as the suite
# builds it.
PLANTED_RAISE = "w1-26 planted decision checker is broken"


def _judge_with_raising_decision_checker(base):
    """The code root of a judge whose own decision checker raises, and its marker folder."""
    judge, markers = base / "judge", base / "judge-markers"
    real = support.SRC / "gov"
    package = judge / "src" / "gov"
    support.write(judge, "pyproject.toml",
                  (support.REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    for folder, rel in ((package, ""), (package / "decisions", "decisions")):
        real_init = real / rel / "__init__.py"
        support.write(folder, "__init__.py",
                      f"__path__.append({str(real / rel)!r})\n"
                      f"exec(compile(open({str(real_init)!r}, encoding='utf-8').read(), "
                      f"{str(real_init)!r}, 'exec'))\n")
    real_checker = real / "decisions" / "checker.py"
    support.write(package / "decisions", "checker.py",
                  f"exec(compile(open({str(real_checker)!r}, encoding='utf-8').read(), "
                  f"{str(real_checker)!r}, 'exec'))\n"
                  "\n\n"
                  "def check(root, *args, **kwargs):\n"
                  "    import os, sys\n"
                  f"    os.makedirs({str(markers)!r}, exist_ok=True)\n"
                  f"    with open(os.path.join({str(markers)!r}, 'raised-%d' % os.getpid()), 'w') as out:\n"
                  "        out.write(' '.join(sys.orig_argv))\n"
                  f"    raise RuntimeError({PLANTED_RAISE!r})\n")
    return judge, markers


def test_planted_authority_defect_decision_checker_exception_not_swallowed(
        project, sandbox, interface, tmp_path):
    """When the decision checker raises, the authority family must not be GREEN.

    The bare ``except Exception: pass`` in authority.py swallows failures and
    lets the family pass silently. The correct behaviour is to report the error
    as a YELLOW or RED finding.
    """
    judge, markers = _judge_with_raising_decision_checker(tmp_path)
    project.commit()
    run = cli_support.run_gov_with_code(judge, project.root, sandbox, support.COMMAND, "--json")
    reached = sorted(markers.glob("raised-*")) if markers.is_dir() else []
    assert reached, (
        f"the planted decision checker was never called by the judge: nothing was planted "
        f"where the judge runs\n{run.describe()}"
    )
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    status = support.family_status(result, "authority/role limits")
    assert status in (support.RED, support.YELLOW), (
        f"the decision checker raised but authority/role limits is {status!r}; "
        f"the exception was silently swallowed (raised in: "
        f"{[path.read_text(encoding='utf-8') for path in reached]})\n{run.describe()}"
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
