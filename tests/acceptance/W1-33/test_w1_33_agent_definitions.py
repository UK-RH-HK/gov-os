"""W1-33 -- the definitions under ``.claude/agents/``.

KPI success 4 [CAP-22.a]: "The generated definitions replace the minimal
definitions W1-05 placed under .claude/agents/ (DEC-119, DEC-154); the
orchestrator definition states its write scope, anywhere in the repository
except tests/acceptance/** (DEC-156)".

KPI success 5: "The generated definitions leave the minimal research role of
W1-46 in place where it exists; W1-33 does not redefine it (DEC-163)".

MR-5: "Each Wave 1 role exists as a generated subagent definition with purpose,
allowed-path pattern, tools, model tier, authority level and handoff format".

"Generated" (DEC-066): the kernel role file is the source, and the definition
carries its fields. Until the rulesync adapters exist (W1-38) no command
produces the definition, so agreement is checked field by field: every labelled
field of the role file is in the definition with the same text, and the
definition has no labelled field of its own.

This file holds every test that reads ``.claude/agents/``. A headless session
may be refused a write there (DEC-312, DEC-315), so these definitions may be
placed later than the kernel role files and the roster; this file's result is
reported apart from the other files of the suite.
"""

from __future__ import annotations

import pytest

import w1_33_support as support


def _definition(role):
    return support.read_committed(support.agent_rel(role))


@pytest.mark.parametrize("role", support.ROLES)
def test_the_definition_is_no_longer_the_minimal_one(role):
    """W1-05's definitions end with "W1-33 replaces this minimal definition with the full role definition"."""
    text = _definition(role)
    assert "minimal definition" not in text.lower(), f"{support.agent_rel(role)} is still W1-05's minimal definition"


@pytest.mark.parametrize("role", support.ROLES)
def test_the_definition_keeps_the_subagent_type_name_of_the_role(role):
    """The guard takes the definition's ``name`` as the role (DEC-117); the harness needs a ``description``."""
    pairs = support.live_support.frontmatter(_definition(role)) or {}
    assert pairs.get("name") == role, f"{support.agent_rel(role)} declares name {pairs.get('name')!r}"
    assert pairs.get("description", "").strip(), f"{support.agent_rel(role)} has no description"


@pytest.mark.parametrize("role", support.ROLES)
def test_the_definition_has_the_six_fields(role):
    missing = support.missing_fields(_definition(role))
    assert not missing, f"{support.agent_rel(role)} lacks {missing}"


@pytest.mark.parametrize("role", support.ROLES)
def test_the_definition_agrees_with_its_kernel_role_file(role):
    """Generated from the role file: the same labelled fields, each with the same text."""
    source = support.fields(support.read_committed(support.role_file_rel(role)))
    generated = support.fields(_definition(role))
    assert source, f"{support.role_file_rel(role)} has no labelled field"
    assert sorted(generated) == sorted(source), (
        f"{support.agent_rel(role)} and {support.role_file_rel(role)} do not have the same fields: "
        f"{sorted(set(generated) ^ set(source))}"
    )
    differing = [label for label in source if generated[label] != source[label]]
    assert not differing, f"{support.agent_rel(role)} differs from its role file in {differing}"


@pytest.mark.parametrize("role", support.ROLES)
def test_the_definition_states_what_the_kpis_require_of_the_role(role):
    """The six fields, the acceptance-test pattern, the permission classes, and per role: the orchestrator's scope,
    the read-only auditor, the launcher's network profile."""
    faults = support.role_faults(role, _definition(role))
    assert not faults, f"{support.agent_rel(role)}: {faults}"


def test_the_orchestrator_definition_states_its_write_scope():
    """DEC-156: anywhere in the repository except ``tests/acceptance/**``."""
    faults = support.orchestrator_scope_faults(_definition(support.ORCHESTRATOR))
    assert not faults, f"{support.agent_rel(support.ORCHESTRATOR)}: {faults}"


def test_there_is_one_definition_per_role_and_the_research_one():
    found = support.live_support.agent_definitions()
    wanted = set(support.ROLES + (support.RESEARCH,))
    assert set(found) == wanted, f"the definitions under .claude/agents/ are {sorted(found)}"
    assert all(len(paths) == 1 for paths in found.values()), f"a subagent type name is defined twice: {found}"


def test_the_research_definition_is_unchanged():
    """Green before implementation; it must stay green (DEC-163, DEC-312)."""
    assert support.sha256(support.agent_rel(support.RESEARCH)) == support.RESEARCH_AGENT_SHA256, (
        ".claude/agents/research.md is not the file the owner committed (DEC-312)"
    )


@pytest.mark.parametrize("role", support.ROLES)
def test_a_definition_without_one_required_field_is_found(role):
    """KPI failure 1, on the definition: each of the six fields in turn is taken out."""
    text = _definition(role)
    assert support.missing_fields(text) == [], f"{support.agent_rel(role)} is not complete to begin with"
    for name in support.REQUIRED_FIELDS:
        assert support.missing_fields(support.without_field(text, name)) == [name], (
            f"the definition of {role} without its {name} field was not found to lack exactly that field"
        )
