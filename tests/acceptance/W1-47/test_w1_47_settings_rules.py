"""W1-47 -- the committed settings carry no install or download ask rule.

KPI success 5: "The committed .claude/settings.json carries no install or
download ask rule: this ticket removes the Bash ask rules for pip, pip3,
python -m pip, python3 -m pip, uv, npm install, cargo install, apt, apt-get,
curl and wget, and leaves the Bash(sudo:*) deny rule and the other deny rules in
place; the guard's install rule then decides install commands alone [...]; an
acceptance test checks the committed file statically, and the acceptance tests
of W1-04 still pass (DEC-172) [CAP-25.f]".
KPI failure 5: "The committed .claude/settings.json still carries an install or
download ask rule, or the Bash(sudo:*) deny rule is gone".

The file is read, nothing is run. "The acceptance tests of W1-04 still pass" is
checked by running ``tests/acceptance/W1-04`` as it stands; this file adds
nothing to that suite.
"""

from __future__ import annotations

import pytest

import w1_47_support as support


@pytest.mark.parametrize("prefix", support.WITHDRAWN_ASK_PREFIXES)
def test_the_committed_settings_carry_no_ask_rule_for(settings, prefix):
    """KPI success 5, failure 5 [CAP-25.f]: one case for each of the eleven rules DEC-172 withdraws."""
    rules = [rule for rule in support.permission_rules(settings, "ask") if support.bash_rule_prefix(rule) == prefix]
    assert not rules, f"permissions.ask of {support.SETTINGS_REL} still carries {rules}"


def test_the_committed_settings_carry_no_install_or_download_ask_rule(settings):
    """KPI failure 5: also a rule on a longer command that begins with one of the eleven (``pip install``)."""
    rules = [rule for rule in support.permission_rules(settings, "ask") if support.is_withdrawn_install_rule(rule)]
    assert not rules, f"permissions.ask of {support.SETTINGS_REL} still carries install or download rules: {rules}"


@pytest.mark.parametrize("kind", ("deny", "allow"))
def test_the_install_rules_were_removed_not_moved(settings, kind):
    """KPI success 5: "the guard's install rule then decides install commands alone".

    A deny rule would stop the orchestrator's approval prompt from ever
    appearing (DEC-083), and an allow rule is a settings rule deciding too.
    """
    rules = [rule for rule in support.permission_rules(settings, kind) if support.is_withdrawn_install_rule(rule)]
    assert not rules, f"permissions.{kind} of {support.SETTINGS_REL} carries install or download rules: {rules}"


def test_the_sudo_deny_rule_is_in_place(settings):
    """KPI success 5, failure 5: ``Bash(sudo:*)`` stays."""
    assert "Bash(sudo:*)" in support.permission_rules(settings, "deny"), (
        f"permissions.deny of {support.SETTINGS_REL} no longer carries Bash(sudo:*)"
    )


@pytest.mark.parametrize("rule", support.KEPT_DENY_RULES)
def test_the_other_deny_rules_are_in_place(settings, rule):
    """KPI success 5: "leaves the Bash(sudo:*) deny rule and the other deny rules in place"."""
    assert rule in support.permission_rules(settings, "deny"), (
        f"permissions.deny of {support.SETTINGS_REL} no longer carries {rule}"
    )


@pytest.mark.parametrize("kind", ("ask", "deny", "allow"))
def test_the_kernel_template_carries_no_install_or_download_rule(template_settings, kind):
    """The ticket's body: "The rules live in this repository's settings only; the kernel template carries none"."""
    rules = [rule for rule in support.permission_rules(template_settings, kind)
             if support.is_withdrawn_install_rule(rule)]
    assert not rules, f"permissions.{kind} of the kernel template's settings file carries {rules}"
