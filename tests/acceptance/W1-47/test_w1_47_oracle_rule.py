"""W1-47 -- the committed ``Read`` deny rule for the qualification oracle, checked statically.

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

These tests compare text with text. They open ``held-out.yaml``,
``.claude/settings.json`` and the ticket's own files, and nothing under the
configured path; they do not ask the file system whether that path exists. The
value is never shown: each failure has a fixed text. Whether the value is the
oracle's path is for the owner to confirm at close; no automatic check may name
it (DEC-162).
"""

from __future__ import annotations

import pytest

import w1_47_support as support


def test_the_oracle_path_is_configured_as_one_absolute_path(configured):
    """KPI success 3: ``held-out.yaml`` exists and holds one absolute path (checked by the fixture)."""
    if not configured.value.startswith("/"):
        pytest.fail(f"the path value of {support.CONFIG_REL} is not absolute", pytrace=False)


def test_the_committed_settings_carry_the_read_deny_rule_built_from_the_configured_path(configured, settings):
    """KPI success 3, failure 3 [CAP-49.c]: present, and with exactly the configured path."""
    if not support.oracle_read_rules(settings, configured):
        pytest.fail(
            f"permissions.deny of {support.SETTINGS_REL} carries no Read rule built from the path in "
            f"{support.CONFIG_REL}: the rule is missing, or its path differs from the configured one. The rule "
            "is Read(/<configured absolute path>), with or without a trailing / or /** (neither value is shown)",
            pytrace=False,
        )


def test_the_read_deny_rule_is_not_an_ask_or_an_allow_rule(configured, settings):
    """KPI failure 3: a rule in another list does not hide the oracle; the configured path is in ``deny`` only."""
    for kind in ("ask", "allow"):
        if any(configured.value.rstrip("/") in rule for rule in support.permission_rules(settings, kind)):
            pytest.fail(f"permissions.{kind} of {support.SETTINGS_REL} names the configured path", pytrace=False)


def test_the_settings_file_names_the_path_in_the_read_deny_rule_only(configured):
    """KPI failure 7: ``.claude/settings.json`` names the path in its Read deny rule and nowhere else."""
    settings = support.load_settings()
    value = configured.value.rstrip("/")
    text = (support.REPO_ROOT / support.SETTINGS_REL).read_text(encoding="utf-8")
    in_rules = sum(rule.count(value) for rule in support.oracle_read_rules(settings, configured))
    if text.count(value) != in_rules:
        pytest.fail(
            f"{support.SETTINGS_REL} names the configured path {text.count(value)} time(s), {in_rules} of them in "
            "its Read deny rule: the path may appear in that rule only",
            pytrace=False,
        )


def test_no_implementation_file_names_the_configured_path(configured):
    """KPI failure 7: the guard, the hooks, the template settings and the builder tests do not repeat the path."""
    files = support.files_matching(support.IMPLEMENTATION_GLOBS)
    assert files, "none of the ticket's implementation paths holds a file"
    naming = support.files_naming(files, configured.value.rstrip("/"))
    if naming:
        names = ", ".join(str(path.relative_to(support.REPO_ROOT)) for path in naming)
        pytest.fail(f"these implementation files name the configured path: {names}", pytrace=False)


def test_no_acceptance_test_of_this_ticket_names_the_configured_path(configured):
    """KPI failure 4, success 3: "the test file carries no literal path"."""
    files = support.files_matching(("**/*",), root=support.SUITE_DIR)
    assert files, "the suite's own files were not found"
    naming = support.files_naming(files, configured.value.rstrip("/"))
    if naming:
        names = ", ".join(path.name for path in naming)
        pytest.fail(f"these files of tests/acceptance/W1-47/ name the configured path: {names}", pytrace=False)
