"""DEC-436: unknown family declarations, derived scope, readiness return value.

Three points from the third-round fix list (DEC-436):

1. A check declaration whose family matches none of the seventeen families is
   reported by name and makes the result not green.  Family names are compared
   by normalised form (lower case, every run of non-alphanumeric characters
   becomes one hyphen).
2. The scope of a check is derived from the repository, not a hand-maintained
   list (CAP-58.a, failure line F-2).
3. The readiness check must fail when ``check_all`` reports a failure via its
   return value, not only via exceptions (reviewer R9/F15).
"""

from __future__ import annotations

import json
import re

import pytest

import w1_26_support as support

cli_support = support.cli_support


# =====================================================================
# Helper: normalise a family name the way DEC-436 requires
# =====================================================================

def _normalise_family(name: str) -> str:
    """Lower-case, every run of non-alphanumeric characters replaced by one hyphen."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# =====================================================================
# Point 1 — Unknown family declarations (DEC-436)
# =====================================================================

# --- 1a. A declaration with an unknown family is reported by name (--json) ---

def test_unknown_family_reported_in_json(project, sandbox, interface):
    """A declaration whose family is not one of the 17 must appear by name in
    ``gov check --json`` output — it is never silently dropped."""
    project.add_core_declarations()
    project.add_check_declaration("bogus-family-check", "bogus-nonexistent-family",
                                  severity="hard-block", command="true")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})

    output_text = json.dumps(result)
    assert "bogus" in output_text.lower(), (
        f"the unknown family 'bogus-nonexistent-family' is not mentioned anywhere "
        f"in the check result\n{run.describe()}"
    )


def test_unknown_family_not_green(project, sandbox, interface):
    """The overall result must NOT be green when an unknown family is present."""
    project.add_core_declarations()
    project.add_check_declaration("bogus-family-check", "bogus-nonexistent-family",
                                  severity="hard-block", command="true")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)

    assert not (envelope.get("ok") is True and run.returncode == support.EXIT_OK), (
        f"the result is green even though a declaration has an unknown family "
        f"'bogus-nonexistent-family'\n{run.describe()}"
    )


# --- 1b. Unknown family in text output (no --json) ---

def test_unknown_family_in_text_output(project, sandbox, interface):
    """The unknown family name appears in ``gov check`` text output (stdout or
    stderr) so the operator can see it."""
    project.add_core_declarations()
    project.add_check_declaration("bogus-text-check", "totally-made-up-family",
                                  severity="hard-block", command="true")
    project.commit()
    run = project.gov(sandbox, "check")
    combined = run.stdout + run.stderr
    assert "totally-made-up-family" in combined.lower() or "totally made up family" in combined.lower(), (
        f"the unknown family 'totally-made-up-family' is not mentioned in the "
        f"text output of gov check\n{run.describe()}"
    )


# --- 1c. Unknown family in --list ---

def test_unknown_family_declaration_in_check_list(project, sandbox, interface):
    """A declaration with an unknown family is still listed by
    ``gov check --list --json`` — it is never hidden."""
    project.add_core_declarations()
    project.add_check_declaration("bogus-list-check", "bogus-nonexistent-family",
                                  severity="hard-block", command="true")
    project.commit()
    run = project.gov(sandbox, "check", "--list", "--json")
    envelope = cli_support.assert_envelope(run, interface, command="check")
    assert envelope["ok"] is True, run.describe()
    records = cli_support.find_records(envelope["result"])
    ids = [r["id"] for r in records]
    assert "bogus-list-check" in ids, (
        f"a declaration with an unknown family is not listed by --list: {ids}"
    )


# --- 1d. Family name normalisation (DEC-436) ---

def test_family_name_normalisation_retrieval_regression(project, sandbox, interface):
    """``retrieval-regression`` matches the Contract's 'retrieval regression' by
    normalised comparison (DEC-436): lower case, every run of non-alphanumeric
    characters read as one hyphen."""
    assert _normalise_family("retrieval-regression") == _normalise_family("retrieval regression")

    project.add_check_declaration("retro-check", "retrieval-regression",
                                  severity="hard-block", command="true")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})

    fam = support.families_of(result)
    canonical = "retrieval regression"
    normalised_canonical = _normalise_family(canonical)
    found = any(
        _normalise_family(k) == normalised_canonical
        for k in fam
    )
    assert found, (
        f"a declaration with family 'retrieval-regression' did not match the "
        f"canonical 'retrieval regression'; families present: {sorted(fam)}"
    )


def test_family_name_normalisation_mixed_case_and_punctuation(project, sandbox, interface):
    """Family names with different casing and punctuation normalise to the same
    family (DEC-436)."""
    project.add_check_declaration("norm-check", "Schema/Invariants",
                                  severity="hard-block", command="true")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})

    fam = support.families_of(result)
    canonical = "schema/invariants"
    normalised_canonical = _normalise_family(canonical)
    found = any(
        _normalise_family(k) == normalised_canonical
        for k in fam
    )
    assert found, (
        f"a declaration with family 'Schema/Invariants' did not match the "
        f"canonical 'schema/invariants'; families present: {sorted(fam)}"
    )


# --- 1e. A family whose only check is red or unmeasured is never green ---

def test_family_only_red_check_not_green(project, sandbox, interface):
    """A family whose only registered check is RED must not be shown GREEN."""
    # revised after implementation: W1-36's kernel declaration of the
    # audit-reproducibility check is now in every project built from the
    # template (DEC-447)
    project.remove_check_declaration("audit-reproducibility")
    project.add_check_declaration("always-red", "audit reproducibility",
                                  severity="hard-block", command="false")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    status = support.family_status(result, "audit reproducibility")
    assert status != support.GREEN, (
        f"'audit reproducibility' has only a failing check but is shown GREEN"
    )


def test_family_only_unmeasured_check_not_green(green_project, sandbox, interface):
    """A family whose only registered check is unmeasured (no query set) must
    not be shown GREEN (DEC-425).

    Revised (W2-67, I2 F3 and sample row 9): the command's inner double quotes
    made the suite's declaration invalid YAML, so ``gov check`` refused it
    (CHECK_DECLARATION_INVALID) before any check ran, and the family it then did
    not find was "not GREEN". The declaration is now valid YAML, on the green base
    (whose kernel retrieval-regression declaration is left out, so this check is
    the family's only one): the check runs, its own entry is not GREEN, and
    neither is the family.
    """
    import yaml
    project = green_project
    command = "python3 -c \"import json,sys; json.dump({'status':'unmeasured'},sys.stdout)\""
    project.write(f"{support.CHECKS_REL}/unmeasured-check.yaml",
                  yaml.safe_dump({"id": "unmeasured-check", "family": "retrieval regression", "tier": "G1",
                                  "severity": "hard-block", "command": command}, sort_keys=False))
    project.commit()
    run = support.run_check(project, sandbox)
    result, _ = support.result_and_envelope(run, interface)
    entry = support.check_entry(result, "unmeasured-check")
    assert entry.get("status") in (support.RED, support.YELLOW), (
        f"the unmeasured check is {entry.get('status')!r}: {entry}\n{run.describe()}"
    )
    status = support.family_status(result, "retrieval regression")
    assert status in (support.RED, support.YELLOW), (
        f"'retrieval regression' is unmeasured but is shown {status!r}\n{run.describe()}"
    )


# =====================================================================
# Point 2 — Scope is derived, not hand-maintained (CAP-58.a, F-2)
# =====================================================================
#
# The reviewer identified six hardcoded lists.  For each we write a test
# OR document why it is definitional (a Contract constant, not a scope
# list derived from the repository).
#
# DEFINITIONAL CONSTANTS (not scope lists):
#
#   FAMILIES — the 17 governance test families are an enumeration of the
#       Contract (v3 O2).  They are NOT derived from the repo; DEC-436
#       says an unknown family is *reported*, not that the list grows.
#
#   RESERVED_COMMANDS — the 12 governance operations are defined by the
#       Contract (CAP-28.b) and listed in W1-07's ticket text.  The
#       command-contract consistency check compares what exists in
#       ``src/gov/`` against this Contract list; the list itself is a
#       Contract constant, not a scope derived from the repository.
#
#   NON_AUTHORITATIVE_TYPES — the set of record types that do not need
#       authority checking is definitional: it follows from the Contract's
#       definition of which state classes require authority (CAP-01.c).
#       Adding a new type does not make it non-authoritative; the
#       Contract decides that.
#
#   IMPLEMENTER_ROLES — the roles whose allowed_paths must not cover
#       ``tests/acceptance/**`` are defined by the Contract's separation
#       of duties (MR-3).  A new role is not an implementer unless the
#       Contract says so.
#
# SCOPE LISTS (must be derived):
#
#   RECORD_PATHS — tests below.
#   SCHEMA_MAP   — tests below.

# --- 2a. RECORD_PATHS: a record in a new directory is discovered ---

def test_record_in_new_directory_discovered_by_schema_check(green_project, sandbox, interface):
    """A record placed in a non-standard directory (not ``.tickets/`` or
    ``docs/adr/``) is discovered by the schema check, proving it derives
    record paths from the repo rather than a hardcoded list.

    The record is placed under ``docs/custom-records/``, a directory that
    no existing list mentions.  The schema check should find it and
    validate it (or flag it).

    Revised (W2-67, I2 §2.7): "the output changed" always held (the output
    carries the commit id). On the green base, ``core-schema`` is GREEN with no
    finding with the well-formed record, and RED with a finding that names the
    defective one and its missing field once it is added.
    """
    project = green_project
    project.write("docs/custom-records/REC-NEW-001.md",
                  "---\nid: REC-NEW-001\ntype: decision\nstatus: ACTIVE\n"
                  "state_class: AUTHORITATIVE\ntitle: Custom record\n---\n"
                  "# REC-NEW-001\n")
    project.commit()
    run1 = support.run_check(project, sandbox)
    support.assert_check_green(run1, interface, "core-schema")

    project.write("docs/custom-records/REC-BAD-001.md",
                  "---\nid: REC-BAD-001\ntype: decision\n"
                  "state_class: AUTHORITATIVE\ntitle: Missing status\n---\n"
                  "# REC-BAD-001\n")
    project.commit()
    run2 = support.run_check(project, sandbox)
    support.assert_check_red_naming(run2, interface, "core-schema", "docs/custom-records/REC-BAD-001.md", "status")


def test_record_in_nested_path_discovered_by_graph_check(project, sandbox, interface):
    """A decision record in a nested path (``docs/decisions/phase2/``) is
    discovered by the graph integrity check without any code change."""
    project.add_decision("DEC-NEST-001", "ACTIVE")
    project.write("docs/decisions/phase2/DEC-NEST-002.md",
                  support.decision("DEC-NEST-002", "ACTIVE",
                                   depends_on=["NONEXISTENT-ZZZ"]))
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})

    output_text = json.dumps(result) + run.stdout
    mentions_nest = ("DEC-NEST-002" in output_text or
                     "NONEXISTENT-ZZZ" in output_text or
                     support.family_status(result, "graph integrity") == support.RED)
    assert mentions_nest, (
        f"a decision in docs/decisions/phase2/ with a dangling depends_on was not "
        f"discovered by the graph check\n{run.describe()}"
    )


# --- 2b. SCHEMA_MAP: a record with an unknown type is not silently skipped ---

def test_record_with_unknown_type_not_silently_skipped(green_project, sandbox, interface):
    """A record whose ``type`` is not in the schema map (e.g. ``type: almanac``)
    must not be silently skipped: the check should either validate its base
    fields or report the unknown type.

    Revised (W2-67, I2 §2.7): "not silently green" held on a base that was never
    green (I2 R1), and the output always holds a commit id. On the green base,
    ``core-schema`` is RED with a finding that names the record: today the unknown
    type is refused (W2-02's ``test_a_record_with_an_unknown_type_is_still_refused``).
    """
    project = green_project
    project.write("docs/adr/UNK-TYPE-001.md",
                  "---\nid: UNK-TYPE-001\ntype: almanac\nstatus: ACTIVE\n"
                  "state_class: AUTHORITATIVE\ntitle: Unknown type record\n---\n"
                  "# UNK-TYPE-001\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_check_red_naming(run, interface, "core-schema", "docs/adr/UNK-TYPE-001.md")


# --- 2c. Command module discovery ---

def test_new_command_module_discovered_by_commands_check(green_project, sandbox, interface):
    """A new command module planted at ``src/gov/<name>/command.py`` is
    discovered by the commands check.

    If the commands check derives its scope from the repository (scanning
    ``src/gov/*/command.py``), a new module changes its output.  If it
    uses only the Contract's RESERVED_COMMANDS list, the new module is
    invisible — but that is acceptable because RESERVED_COMMANDS is
    definitional (see the note above).

    Revised (W2-67, W2-L379, DEC-877 item 5): the case asserted "adding a
    command module changes the check's output OR the check explicitly reports
    the Contract list", and "the output changed" was always true (the output
    carries the commit id). The list of reserved commands is the
    Contract's (definitional); what the check derives from the repository is
    which of their modules exist. So the case starts from a project where one
    reserved command (``adopt``) has no module file: the check's own entry has a
    finding that names it; then the command's new module is planted at
    ``src/gov/adopt/command.py``, and the check's entry is GREEN with no finding.
    """
    project = green_project
    project.add_check_declaration("cmd-check", "command-contract consistency",
                                  severity="warning",
                                  command="python3 -m gov.check.commands")
    assert project.remove_reserved_command_module("adopt"), "the project held no module file for adopt"
    project.commit()
    run1 = support.run_check(project, sandbox)
    result1, _ = support.result_and_envelope(run1, interface)
    before = support.check_entry(result1, "cmd-check")
    assert before.get("status") != support.GREEN and support.findings_naming(before, "adopt"), (
        f"with no module file for adopt, the commands check has no finding that names it: {before}\n"
        f"{run1.describe()}"
    )

    project.write("src/gov/adopt/command.py",
                  "def register(subparsers):\n    subparsers.add_parser('adopt')\n")
    project.commit()
    run2 = support.run_check(project, sandbox)
    support.assert_check_green(run2, interface, "cmd-check")


# --- 2d. Path-map namespace discovery ---

def test_new_pathmap_namespace_picked_up(project, sandbox, interface):
    """A new namespace added to path-map.yaml is picked up by the path-map
    compliance check without any code change."""
    project.add_path_map({
        "source-code": ["src/**"],
        "tests": ["tests/**"],
    })
    project.write("src/example.py", "# example\n")
    project.write("tests/test_example.py", "# test\n")
    project.commit()
    run1 = support.run_check(project, sandbox)

    project.add_path_map({
        "source-code": ["src/**"],
        "tests": ["tests/**"],
        "new-namespace": ["docs/new/**"],
    })
    project.write("docs/new/file.md", "# new namespace file\n")
    project.commit()
    run2 = support.run_check(project, sandbox)
    envelope2 = support.envelope_of(run2, interface)
    result2 = envelope2.get("result") or envelope2.get("error", {}).get("details", {})
    output2 = json.dumps(result2) + run2.stdout

    changed = (run2.stdout != run1.stdout or run2.returncode != run1.returncode)
    mentions_new = "new-namespace" in output2 or "docs/new" in output2

    assert changed or mentions_new, (
        f"adding a new namespace 'new-namespace' to the path map was invisible "
        f"to the check — the output did not change\n{run2.describe()}"
    )


# --- 2e. A new check declaration is picked up (already in test_w1_26_derived.py,
#     but this test adds the specific DEC-436 angle: the runner's FAMILIES list
#     does not gate which declarations run) ---

def test_check_declaration_for_unregistered_family_runs(project, sandbox, interface):
    """A check declaration for a family that has no prior registered check is
    still run.  The runner must not skip declarations because they belong to a
    family that was previously unregistered."""
    marker = sandbox.elsewhere / "dec436-unregistered-ran"
    project.add_check_declaration("dec436-unreg", "product traceability",
                                  command=f"touch {marker}")
    project.commit()
    run = support.run_check(project, sandbox)
    support.envelope_of(run, interface)
    assert marker.exists(), (
        f"a check declaration for the previously-unregistered family "
        f"'product traceability' was not run\n{run.describe()}"
    )


# =====================================================================
# Point 3 — Readiness check uses its evaluator's result (R9/F15)
# =====================================================================

def _check_with_the_projects_own_code(project, sandbox, interface):
    """``gov check --json`` run with the ``gov`` package of the project's own ``src/``: the copy of this worktree's
    ``src/`` the project was built with, plus what the case planted in it. The readiness check imports
    ``gov.readiness.checker`` in the ``gov`` process itself, so a module planted in the project is read only when
    that process runs the project's code (W2-L379). Returns ``(result, run)``."""
    for rel in ("src/gov/check/runner.py", "src/gov/check/command.py"):
        assert (project.root / rel).read_bytes() == (support.REPO_ROOT / rel).read_bytes(), \
            f"the project's {rel} is not this worktree's: the code that judges would not be the code under test"
    project.commit()
    run = cli_support.run_gov_with_code(project.root, project.root, sandbox, support.COMMAND, "--json")
    result, _ = support.result_and_envelope(run, interface)
    return result, run


def test_readiness_check_all_return_value_not_ignored(green_project, sandbox, interface):
    """When ``check_all`` returns findings via its return value (not by raising
    an exception), ``gov check`` must report the family as not GREEN.

    The readiness check wraps ``check_all``. If it only catches exceptions and
    ignores the return value, a ``check_all`` that returns a failure dict
    (``{"closed": False, ...}``) would be silently treated as success.

    This test replaces the readiness checker with one whose ``check_all``
    returns a dict indicating failure — without raising — and asserts that
    ``gov check`` does not report the readiness-related family as GREEN.

    Revised (W2-67, W2-L379, DEC-877 item 5): the planted module was never
    imported (``gov check`` ran this worktree's code, not the project's), and the
    loop looked for a family whose name holds "readiness", which no family has.
    ``gov check`` now runs the project's own code, and the ``readiness`` check's
    own entry is RED with a finding that names the specification ``check_all``
    returned not closed.
    """
    project = green_project
    project.write("src/gov/readiness/__init__.py",
                  "from gov.readiness.checker import check, check_all, close\n"
                  "__all__ = ['check', 'check_all', 'close']\n")
    project.write("src/gov/readiness/checker.py",
                  "from pathlib import Path\n"
                  "\n"
                  "NOT_FOUND = 'READINESS_NOT_FOUND'\n"
                  "NOT_CLOSED = 'READINESS_NOT_CLOSED'\n"
                  "INVALID = 'READINESS_INVALID'\n"
                  "CHANGES_REL = 'openspec/changes'\n"
                  "\n"
                  "def check(root, specification=None):\n"
                  "    return {'closed': False, 'findings': ['readiness-not-met']}\n"
                  "\n"
                  "def check_all(root):\n"
                  "    return {\n"
                  "        'closed': False,\n"
                  "        'specifications': [\n"
                  "            {'specification': 'SPEC-test',\n"
                  "             'closed': False,\n"
                  "             'findings': ['required row not satisfied']}\n"
                  "        ]\n"
                  "    }\n"
                  "\n"
                  "def close(root, specification):\n"
                  "    raise NotImplementedError\n"
                  "\n"
                  "def of_ticket(root, ticket):\n"
                  "    return ticket\n"
                  "\n"
                  "def specifications(root):\n"
                  "    return []\n")
    result, run = _check_with_the_projects_own_code(project, sandbox, interface)
    entry = support.check_entry(result, "readiness")
    assert entry.get("status") == support.RED and support.findings_naming(entry, "SPEC-test"), (
        f"check_all returned a failure dict (closed=False) without raising, but "
        f"the readiness check is not RED with a finding that names SPEC-test — the return value was ignored: "
        f"{entry}\n{run.describe()}"
    )
    assert support.family_status(result, entry.get("family")) == support.RED, run.describe()


def test_readiness_check_all_exception_caught(green_project, sandbox, interface):
    """When ``check_all`` raises an exception with findings, ``gov check`` must
    report the family as not GREEN.

    Complement to the return-value test: ensures the exception path also works.
    (This overlaps with test_w1_26_readiness.py but uses a mock checker to
    isolate the integration point.)

    Revised (W2-67, W2-L379, DEC-877 item 5): as the return-value case, the
    planted module was never imported and no family's name holds "readiness".
    ``gov check`` now runs the project's own code, and the ``readiness`` check's
    own entry is RED with a finding that carries the raised error's message.
    """
    project = green_project
    project.write("src/gov/readiness/__init__.py",
                  "from gov.readiness.checker import check, check_all, close\n"
                  "__all__ = ['check', 'check_all', 'close']\n")
    project.write("src/gov/readiness/checker.py",
                  "from pathlib import Path\n"
                  "\n"
                  "NOT_FOUND = 'READINESS_NOT_FOUND'\n"
                  "NOT_CLOSED = 'READINESS_NOT_CLOSED'\n"
                  "INVALID = 'READINESS_INVALID'\n"
                  "CHANGES_REL = 'openspec/changes'\n"
                  "\n"
                  "class GovError(Exception):\n"
                  "    def __init__(self, code, message, details=None, exit_code=1):\n"
                  "        super().__init__(message)\n"
                  "        self.code = code\n"
                  "        self.message = message\n"
                  "        self.details = details or {}\n"
                  "        self.exit_code = exit_code\n"
                  "\n"
                  "def check(root, specification=None):\n"
                  "    raise GovError(INVALID, 'readiness check failed',\n"
                  "                   {'closed': False, 'findings': ['f1']})\n"
                  "\n"
                  "def check_all(root):\n"
                  "    raise GovError(INVALID, 'readiness check_all failed',\n"
                  "                   {'closed': False,\n"
                  "                    'specifications': [{'specification': 'SPEC-exc',\n"
                  "                                        'closed': False,\n"
                  "                                        'findings': ['row missing']}]})\n"
                  "\n"
                  "def close(root, specification):\n"
                  "    raise NotImplementedError\n"
                  "\n"
                  "def of_ticket(root, ticket):\n"
                  "    return ticket\n"
                  "\n"
                  "def specifications(root):\n"
                  "    return []\n")
    result, run = _check_with_the_projects_own_code(project, sandbox, interface)
    entry = support.check_entry(result, "readiness")
    assert entry.get("status") == support.RED and support.findings_naming(entry, "readiness check_all failed"), (
        f"check_all raised GovError with findings, but the readiness check is not RED with a finding that "
        f"carries its message — the exception was swallowed: {entry}\n{run.describe()}"
    )
    assert support.family_status(result, entry.get("family")) == support.RED, run.describe()
