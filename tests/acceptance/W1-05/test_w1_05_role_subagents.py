"""W1-05 — minimal subagent definitions for the five Wave 1 roles (DEC-119).

KPI success 3 to 7: "A minimal subagent definition for the <role> role exists
under .claude/agents/, with the subagent type name <role>".

DEC-113: the five roles are subagent types, and the type names are the role names.

A definition is a Markdown file under ``.claude/agents/`` whose YAML frontmatter
holds ``name`` (the subagent type name) and ``description``; the harness needs
both to load it.

Rewrite-Reason: EMERGENCY-2 6.1 (the guard / the sandbox retired), DAEO-gr7t. The two cases that ran the guard on a
subagent type name, and the engineer-subagent case, are deleted with the guard; the definitions case stays.
"""

from __future__ import annotations

import pytest

import w1_05_support as support


def _definition(role, root=support.REPO_ROOT):
    found = support.agent_definitions(root).get(role, [])
    assert found, (
        f"no file under {support.AGENTS_REL}/ of {root} defines a subagent with the type name {role!r} "
        "(frontmatter `name:`)"
    )
    names = ", ".join(str(path.relative_to(root)) for path in found)
    assert len(found) == 1, f"the subagent type name {role!r} is defined {len(found)} times: {names}"
    return found[0]


@pytest.mark.parametrize("role", support.ROLES)
def test_a_subagent_definition_exists_for_the_role(role):
    path = _definition(role)
    pairs = support.frontmatter(path.read_text(encoding="utf-8"))
    assert pairs.get("description", "").strip(), (
        f"{path.relative_to(support.REPO_ROOT)} has no `description`; the harness does not load it as a subagent"
    )
