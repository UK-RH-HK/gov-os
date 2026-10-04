"""W1-47 -- the committed ``Read`` deny rule for the held-out paths, checked statically.

KPI success 3: "The repository's committed .claude/settings.json carries a Read
deny rule with the qualification oracle's absolute path; the oracle path is held
in governance/project/held-out.yaml and in the committed deny rule built from
it, and the acceptance test checks the committed rule statically, by its
presence and its exact path in the file: it reads the configured value from
held-out.yaml and asserts that the committed rule is built from it, so the test
file carries no literal path and opens nothing under that path [...] (DEC-162)
[CAP-49.c]".
KPI failure 3: "The committed Read deny rule is missing from
.claude/settings.json, or its path differs from the oracle's absolute path".
KPI failure 4: "An acceptance test of this ticket reads or names the
qualification oracle".
KPI failure 7: "An implementation file of this ticket [...] names its path
anywhere but governance/project/held-out.yaml and the committed Read deny rule".

DEC-218: the owner wrote ``held-out.yaml``; its key is ``held_out_paths``, a
list of absolute paths. The committed rule is generated from it by a script.
These tests check the committed result, for every path of the list.

These tests compare text with text. They open ``held-out.yaml``,
``.claude/settings.json`` and the ticket's own files, and nothing under a
configured path; they do not ask the file system whether such a path exists. A
value is never shown: each failure has a fixed text, with no value and no count
taken from the list. Whether the values are the oracle's is confirmed by the
owner's commit of the file (DEC-218); no automatic check may name it (DEC-162).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import w1_47_support as support


def test_the_configuration_holds_a_list_of_absolute_paths_under_its_key(configured):
    """KPI success 3, DEC-218: ``held_out_paths`` is a non-empty list of absolute paths (checked by the fixture)."""
    if not configured.values or not all(value.startswith("/") for value in configured.values):
        pytest.fail(f"{support.CONFIG_KEY} of {support.CONFIG_REL} is not a list of absolute paths", pytrace=False)


def test_the_committed_settings_carry_a_read_deny_rule_built_from_every_configured_path(configured, settings):
    """KPI success 3, failure 3 [CAP-49.c]: present, and with exactly the configured path, for each path."""
    if not all(support.held_out_read_rules(settings, value) for value in configured.values):
        pytest.fail(
            f"permissions.deny of {support.SETTINGS_REL} carries no Read rule built from a path of "
            f"{support.CONFIG_KEY} in {support.CONFIG_REL}: the rule is missing, or its path differs from the "
            "configured one. The rule is Read(/<configured absolute path>), with or without a trailing / or /** "
            "(neither value is shown)",
            pytrace=False,
        )


def test_the_read_deny_rule_is_not_an_ask_or_an_allow_rule(configured, settings):
    """KPI failure 3: a rule in another list does not hide the oracle; a configured path is in ``deny`` only."""
    for kind in ("ask", "allow"):
        rules = support.permission_rules(settings, kind)
        if any(value in rule for value in configured.values for rule in rules):
            pytest.fail(f"permissions.{kind} of {support.SETTINGS_REL} names a configured path", pytrace=False)


def test_the_settings_file_names_a_configured_path_in_its_read_deny_rule_only(configured, settings):
    """KPI failure 7: ``.claude/settings.json`` names a path in the Read deny rule built from it and nowhere else."""
    text = (support.REPO_ROOT / support.SETTINGS_REL).read_text(encoding="utf-8")
    for value in configured.values:
        in_rules = sum(rule.count(value) for rule in support.held_out_read_rules(settings, value))
        # One configured path may be the beginning of another: the rules of the longer one hold it too.
        in_longer = sum(rule.count(value)
                        for other in configured.values if other != value and other.startswith(value)
                        for rule in support.held_out_read_rules(settings, other))
        if text.count(value) != in_rules + in_longer:
            pytest.fail(
                f"{support.SETTINGS_REL} names a configured path outside the Read deny rule built from it: the "
                "path may appear in that rule only",
                pytrace=False,
            )


def test_no_implementation_file_names_a_configured_path(configured):
    """KPI failure 7: the guard, the hooks, the template settings and the builder tests do not repeat a path."""
    files = support.files_matching(support.IMPLEMENTATION_GLOBS)
    assert files, "none of the ticket's implementation paths holds a file"
    naming = support.files_naming(files, configured.values)
    if naming:
        names = ", ".join(str(path.relative_to(support.REPO_ROOT)) for path in naming)
        pytest.fail(f"these implementation files name a configured path: {names}", pytrace=False)


def test_no_acceptance_test_of_this_ticket_names_a_configured_path(configured):
    """KPI failure 4, success 3: "the test file carries no literal path"."""
    files = support.files_matching(("**/*",), root=support.SUITE_DIR)
    assert files, "the suite's own files were not found"
    naming = support.files_naming(files, configured.values)
    if naming:
        names = ", ".join(path.name for path in naming)
        pytest.fail(f"these files of tests/acceptance/W1-47/ name a configured path: {names}", pytrace=False)


def test_the_stand_in_configuration_is_built_without_the_committed_file():
    """KPI failure 4: the guard's tests take nothing from the committed file; the stand-in's file is made up.

    The committed ``held-out.yaml`` is read by ``load_configured`` alone, and
    that function is used by the ``configured`` fixture of the static checks
    in this file alone.
    """
    users = []
    for path in support.files_matching(("test_*.py",), root=support.SUITE_DIR):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        takes_fixture = any(isinstance(node, ast.FunctionDef) and "configured" in [a.arg for a in node.args.args]
                            for node in ast.walk(tree))
        calls_loader = any(isinstance(node, ast.Attribute) and node.attr == "load_configured"
                           for node in ast.walk(tree))
        if takes_fixture or calls_loader:
            users.append(path.name)
    assert users == [Path(__file__).name], (
        f"the committed held-out configuration is used outside the static checks: {users}"
    )
