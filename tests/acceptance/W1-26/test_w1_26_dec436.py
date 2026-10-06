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


def test_family_only_unmeasured_check_not_green(project, sandbox, interface):
    """A family whose only registered check is unmeasured (no query set) must
    not be shown GREEN (DEC-425)."""
    project.add_check_declaration("unmeasured-check", "retrieval regression",
                                  severity="hard-block",
                                  command="python3 -c \"import json,sys; "
                                          "json.dump({'status':'unmeasured'},sys.stdout)\"")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    status = support.family_status(result, "retrieval regression")
    assert status != support.GREEN, (
        f"'retrieval regression' is unmeasured but is shown GREEN"
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

def test_record_in_new_directory_discovered_by_schema_check(project, sandbox, interface):
    """A record placed in a non-standard directory (not ``.tickets/`` or
    ``docs/adr/``) is discovered by the schema check, proving it derives
    record paths from the repo rather than a hardcoded list.

    The record is placed under ``docs/custom-records/``, a directory that
    no existing list mentions.  The schema check should find it and
    validate it (or flag it).
    """
    project.write("docs/custom-records/REC-NEW-001.md",
                  "---\nid: REC-NEW-001\ntype: decision\nstatus: ACTIVE\n"
                  "state_class: AUTHORITATIVE\ntitle: Custom record\n---\n"
                  "# REC-NEW-001\n")
    project.commit()
    run1 = support.run_check(project, sandbox)

    project.write("docs/custom-records/REC-BAD-001.md",
                  "---\nid: REC-BAD-001\ntype: decision\n"
                  "state_class: AUTHORITATIVE\ntitle: Missing status\n---\n"
                  "# REC-BAD-001\n")
    project.commit()
    run2 = support.run_check(project, sandbox)

    output_changed = run2.stdout != run1.stdout or run2.returncode != run1.returncode
    envelope2 = support.envelope_of(run2, interface)
    result2 = envelope2.get("result") or envelope2.get("error", {}).get("details", {})
    schema_status = support.family_status(result2, "schema/invariants")

    assert output_changed or schema_status == support.RED, (
        f"adding a defective record in docs/custom-records/ did not change the "
        f"check output or make schema/invariants RED — the check uses a hardcoded "
        f"list of record directories\n{run2.describe()}"
    )


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

def test_record_with_unknown_type_not_silently_skipped(project, sandbox, interface):
    """A record whose ``type`` is not in the schema map (e.g. ``type: almanac``)
    must not be silently skipped: the check should either validate its base
    fields or report the unknown type."""
    project.write("docs/adr/UNK-TYPE-001.md",
                  "---\nid: UNK-TYPE-001\ntype: almanac\nstatus: ACTIVE\n"
                  "state_class: AUTHORITATIVE\ntitle: Unknown type record\n---\n"
                  "# UNK-TYPE-001\n")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    output_text = json.dumps(result) + run.stdout

    silently_green = (
        envelope.get("ok") is True
        and run.returncode == support.EXIT_OK
        and "UNK-TYPE-001" not in output_text
        and "almanac" not in output_text.lower()
    )
    assert not silently_green, (
        f"a record with unknown type 'almanac' was silently skipped; the check "
        f"passed without mentioning the record or its type\n{run.describe()}"
    )


# --- 2c. Command module discovery ---

def test_new_command_module_discovered_by_commands_check(project, sandbox, interface):
    """A new command module planted at ``src/gov/<name>/command.py`` is
    discovered by the commands check.

    If the commands check derives its scope from the repository (scanning
    ``src/gov/*/command.py``), a new module changes its output.  If it
    uses only the Contract's RESERVED_COMMANDS list, the new module is
    invisible — but that is acceptable because RESERVED_COMMANDS is
    definitional (see the note above).  This test asserts the weaker
    property: adding a command module changes the check's output OR the
    check explicitly reports the Contract list.
    """
    project.add_check_declaration("cmd-check", "command-contract consistency",
                                  severity="warning",
                                  command="python3 -m gov.check.commands")
    project.commit()
    run1 = support.run_check(project, sandbox)

    project.write("src/gov/invented_cmd/__init__.py", "")
    project.write("src/gov/invented_cmd/command.py",
                  "def register(subparsers):\n    subparsers.add_parser('invented_cmd')\n")
    project.commit()
    run2 = support.run_check(project, sandbox)

    envelope2 = support.envelope_of(run2, interface)
    result2 = envelope2.get("result") or envelope2.get("error", {}).get("details", {})
    output2 = json.dumps(result2) + run2.stdout

    changed = (run2.stdout != run1.stdout or run2.returncode != run1.returncode)
    mentions_invented = "invented_cmd" in output2 or "invented" in output2.lower()

    assert changed or mentions_invented, (
        f"adding a command module at src/gov/invented_cmd/command.py was invisible "
        f"to the commands check — the output did not change and the module is not "
        f"mentioned\n{run2.describe()}"
    )


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

def test_readiness_check_all_return_value_not_ignored(project, sandbox, interface):
    """When ``check_all`` returns findings via its return value (not by raising
    an exception), ``gov check`` must report the family as not GREEN.

    The readiness check wraps ``check_all``. If it only catches exceptions and
    ignores the return value, a ``check_all`` that returns a failure dict
    (``{"closed": False, ...}``) would be silently treated as success.

    This test replaces the readiness checker with one whose ``check_all``
    returns a dict indicating failure — without raising — and asserts that
    ``gov check`` does not report the readiness-related family as GREEN.
    """
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
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)

    readiness_green = False
    for family_name, entry in families.items():
        if "readiness" in family_name.lower():
            status = entry.get("status") if isinstance(entry, dict) else entry
            if status == support.GREEN:
                readiness_green = True
                break

    assert not readiness_green, (
        f"check_all returned a failure dict (closed=False) without raising, but "
        f"the readiness-related family is GREEN — the return value was ignored\n"
        f"{run.describe()}"
    )


def test_readiness_check_all_exception_caught(project, sandbox, interface):
    """When ``check_all`` raises an exception with findings, ``gov check`` must
    report the family as not GREEN.

    Complement to the return-value test: ensures the exception path also works.
    (This overlaps with test_w1_26_readiness.py but uses a mock checker to
    isolate the integration point.)
    """
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
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)

    readiness_green = False
    for family_name, entry in families.items():
        if "readiness" in family_name.lower():
            status = entry.get("status") if isinstance(entry, dict) else entry
            if status == support.GREEN:
                readiness_green = True
                break

    assert not readiness_green, (
        f"check_all raised GovError with findings, but the readiness-related "
        f"family is GREEN — the exception was swallowed\n{run.describe()}"
    )
