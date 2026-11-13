"""W2-105 (DAEO-zpdj): the template's install block removed (DEC-966 item 1, P-W2-90-1 P1-A (a)).

``template/.rulesync/permissions.jsonc`` denied ``npm install*`` and ``pip install*``. rulesync turns each into a deny
rule of every generated project's ``.claude/settings.json``, and Claude Code refuses a call a deny rule matches before
any hook is asked: the CTO's session could never reach the guard's install rule and ask the owner. This repository
removed the same rules by DEC-172; the guard's install rule stands alone (DEC-957 item 3: the CTO's session is asked,
every other session refused).

What the cases hold, in a project generated from the template (Copier, then rulesync generate):

1. no rule of the template's source or of the generated settings binds ``npm install`` or ``pip install``, in the deny
   list or moved to the ask or allow list (KPI success 1, failure 1);
2. an install by the orchestrator on its coordination ticket reaches the guard and the guard asks; the same installs
   by the engineer, the independent test designer, the independent auditor, product-spec, a session with no role and
   research outside its experiment folder are refused by the guard's own program, not by a settings rule (KPI success
   2, failure 1 and 2, as the lead reads them);
3. every other rule of the source and of the generated settings is the template's before this ticket, by name and
   count; only the two install rules are gone (KPI success 3, failure 3).

``tests/acceptance/W2-105/README.md`` maps each case to its KPI line and its expected result on the base.
"""

from __future__ import annotations

import pytest

import w2_105_support as support

INSTALLS = support.INSTALLS
SUDO = "sudo apt-get install -y jq"


def _sorted(items):
    return sorted(items, key=repr)


# ===================================================================
# KPI success 1, failure 1: no deny rule for the installs in the generated settings
# ===================================================================

@pytest.mark.parametrize("command", INSTALLS)
def test_no_rule_of_the_templates_source_binds_the_install(command):
    """Whatever its value: rulesync generates ``Bash(<pattern>)`` from each ``bash`` rule of the source."""
    found = _sorted((category, pattern, value) for category, pattern, value in support.template_source_rules()
                    if category == "bash"
                    and support.matching_rule([f"Bash({pattern})"], command, support.REPO_ROOT))
    assert not found, (
        f"{support.SOURCE_REL} still gives a rule that binds `{command}`: {found}. rulesync makes it a rule of every "
        f"project generated from the template, and the CTO's session can never ask the owner (DEC-966 item 1)"
    )


@pytest.mark.parametrize("kind", support.RULE_LISTS)
@pytest.mark.parametrize("command", INSTALLS)
def test_no_rule_of_the_generated_settings_binds_the_install(settings, live, command, kind):
    """``deny``: the KPI line itself. ``ask`` and ``allow``: removed, not moved (W1-47's reading of DEC-172): a
    settings rule there would decide the install beside the guard's install rule."""
    rule = support.settings_rule_for(settings, kind, command, live)
    assert rule is None, (
        f"permissions.{kind} of the generated {support.SETTINGS_REL} holds {rule}, which binds `{command}`"
        + (": Claude Code refuses the install before the guard is asked (DEC-966 item 1, DEC-172)"
           if kind == "deny" else ": the guard's install rule no longer decides the install alone (DEC-172)")
    )


# ===================================================================
# KPI success 2, failures 1 and 2: the guard decides, the CTO's session is asked, every other session refused
# ===================================================================

@pytest.mark.parametrize("command", INSTALLS)
def test_an_install_by_the_orchestrator_on_its_coordination_ticket_is_asked_by_the_guard(settings, live, sandbox,
                                                                                         command):
    """The CTO's session (the orchestrator role on its coordination ticket): no settings rule decides, the call
    reaches the guard's install rule, and the guard's program answers ``ask``, in each permission mode."""
    for mode in support.PERMISSION_MODES:
        asked = support.ask(live, settings, sandbox, command, support.ORCHESTRATOR, permission_mode=mode)
        assert asked.asked_by_the_guard, (
            f"the install did not reach the guard's install rule and was not asked (DEC-966 item 1, DEC-957): "
            f"{asked.describe()}"
        )


@pytest.mark.parametrize("command", INSTALLS)
@pytest.mark.parametrize("role", support.OTHER_ROLES)
def test_an_install_by_another_role_is_refused_by_the_guard(settings, live, sandbox, role, command):
    """Refused, and refused by the guard: no settings deny rule refused first, and the guard's own program wrote the
    refusal. A settings rule is not the guard (DEC-172), and an ``ask`` or an allowance is a failure (KPI failure 2)."""
    asked = support.ask(live, settings, sandbox, command, role)
    assert asked.refused_by_the_guard and "ask" not in asked.answers, (
        f"the install by {role} was not refused by the guard (DEC-957 item 3: every session but the CTO's is "
        f"refused by the guard's install rule): {asked.describe()}"
    )


@pytest.mark.parametrize("command", INSTALLS)
def test_an_install_in_a_session_without_a_role_is_refused_by_the_guard(settings, live, sandbox, command):
    """Another session that is not the CTO's: one started with no ``GOV_ROLE``."""
    asked = support.ask(live, settings, sandbox, command, support.NO_ROLE)
    assert asked.refused_by_the_guard and "ask" not in asked.answers, (
        f"the install in a session without a role was not refused by the guard: {asked.describe()}"
    )


@pytest.mark.parametrize("command", INSTALLS)
def test_a_research_install_outside_its_experiment_folder_is_refused_by_the_guard(settings, live, sandbox, command):
    """Research on its ticket, started in the project's root: outside its experiment folder (DEC-163), its install is
    the guard's to refuse, as every other worker's."""
    asked = support.ask(live, settings, sandbox, command, support.RESEARCH)
    assert asked.refused_by_the_guard and "ask" not in asked.answers, (
        f"the research install outside {support.EXPERIMENT_REL} was not refused by the guard: {asked.describe()}"
    )


# ===================================================================
# KPI success 3, failure 3: every other rule unchanged, by name and count
# ===================================================================

def test_the_comparison_base_gives_the_two_install_rules(base_settings):
    """The base is the template before this ticket: its source gives the two rules and rulesync generates them.
    Green before and after the change; a red here means the comparisons below compare with the wrong base."""
    source = support.base_source_rules()
    generated = support.generated_rules(base_settings)
    assert support.INSTALL_SOURCE_RULES <= source, (
        f"{support.BASE_COMMIT}:{support.SOURCE_REL} does not give {_sorted(support.INSTALL_SOURCE_RULES)}: {source}"
    )
    assert all(generated[rule] == 1 for rule in support.INSTALL_GENERATED_RULES), (
        f"rulesync, given the base source, does not generate {_sorted(support.INSTALL_GENERATED_RULES)} once each: "
        f"{dict(generated)}"
    )


def test_the_templates_source_is_its_base_less_the_two_install_rules():
    before, after = support.base_source_rules(), support.template_source_rules()
    expected = before - support.INSTALL_SOURCE_RULES
    assert after == expected and len(after) == len(before) - 2, (
        f"{support.SOURCE_REL} must give the {len(before)} rules of {support.BASE_COMMIT} less the two install rules "
        f"({len(expected)} rules); it gives {len(after)}. Still there or added: {_sorted(after - expected)}; "
        f"missing: {_sorted(expected - after)}"
    )


def test_no_other_rule_of_the_templates_source_is_added_removed_or_changed():
    """Green before the change; it must stay green. The two install rules aside, the source is its base."""
    names = {(category, pattern) for category, pattern, _value in support.INSTALL_SOURCE_RULES}
    before = {rule for rule in support.base_source_rules() if rule[:2] not in names}
    after = {rule for rule in support.template_source_rules() if rule[:2] not in names}
    assert after == before, (
        f"beside the two install rules, {support.SOURCE_REL} differs from {support.BASE_COMMIT}: "
        f"added or changed {_sorted(after - before)}, removed or changed {_sorted(before - after)}"
    )


def test_the_generated_rules_are_the_base_rules_less_the_two_install_rules(settings, base_settings):
    before, after = support.generated_rules(base_settings), support.generated_rules(settings)
    expected = before - support.INSTALL_GENERATED_RULES
    assert after == expected and sum(after.values()) == sum(before.values()) - 2, (
        f"the generated {support.SETTINGS_REL} must hold the {sum(before.values())} rules generated from the base "
        f"less the two install deny rules ({sum(expected.values())}); it holds {sum(after.values())}. Still there or "
        f"added: {dict(after - expected)}; missing: {dict(expected - after)}"
    )


def test_no_other_generated_rule_is_added_removed_or_changed(settings, base_settings):
    """Green before the change; it must stay green. By name and count in every list of ``permissions``, and every
    entry of ``permissions`` that is not a rule list."""
    before = support.generated_rules(base_settings) - support.INSTALL_GENERATED_RULES
    after = support.generated_rules(settings) - support.INSTALL_GENERATED_RULES
    assert after == before, (
        f"beside the two install deny rules, the generated {support.SETTINGS_REL} differs from what the base "
        f"generates: added {dict(after - before)}, removed {dict(before - after)}"
    )
    assert support.other_permission_entries(settings) == support.other_permission_entries(base_settings), (
        f"an entry of `permissions` other than a rule list changed: "
        f"{support.other_permission_entries(base_settings)} -> {support.other_permission_entries(settings)}"
    )


def test_sudo_is_still_denied_by_the_generated_settings(settings, live):
    """Green before the change; it must stay green. The sudo rule is not an install rule: it stays a deny rule."""
    rule = support.settings_rule_for(settings, "deny", SUDO, live)
    assert rule is not None, (
        f"no deny rule of the generated {support.SETTINGS_REL} binds `{SUDO}`: "
        f"{support.permissions_of(settings).get('deny')}"
    )
