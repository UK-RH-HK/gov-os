"""W1-02 — a session with an unknown role is read-only.

KPI success 4: "A session with no declared role, or an unknown role, is
read-only: every write is denied [CAP-58.c]".
KPI failure 3: "A session with no or an unknown role can write anywhere".

Owner answer to KD-1: the role is ``GOV_ROLE``. The known roles are
``orchestrator``, ``product-spec``, ``independent-test-designer``, ``engineer``
and ``independent-auditor``. Any other value is an unknown role.

Each session below names a live ticket in ``GOV_TICKET``. The role decides.
The session with no role at all is in ``test_w1_02_role_less_session.py``.
"""

from __future__ import annotations

import pytest

import w1_02_support as support

TICKET = support.TICKET_ID
WBS = support.TICKET_WBS_ID

TARGETS = {
    "ticket-allowed-source": "src/gov/guard/decide.py",
    "ticket-allowed-new-file": "src/gov/guard/new_module.py",
    "acceptance-test": f"tests/acceptance/{WBS}/test_fixture.py",
    "outside-ticket-docs": "docs/notes.md",
    "outside-ticket-root-file": "README.md",
    "ticket-file": f".tickets/{TICKET}.md",
}

BASH_WRITES = {
    "redirect-into-ticket-path": "echo changed > src/gov/guard/decide.py",
    "touch-acceptance-test": f"touch tests/acceptance/{WBS}/test_added.py",
    "rm-root-file": "rm README.md",
}


@pytest.mark.parametrize("role", support.UNKNOWN_ROLES)
@pytest.mark.parametrize("target", sorted(TARGETS), ids=sorted(TARGETS))
def test_unknown_role_cannot_edit_or_write(project, write, role, target):
    relpath = TARGETS[target]
    for tool_name in ("Edit", "Write"):
        result = write(project, relpath, role, TICKET, tool_name)
        support.assert_denied(result, f"{tool_name} on {relpath} with GOV_ROLE={role!r}")


@pytest.mark.parametrize("role", support.UNKNOWN_ROLES)
def test_unknown_role_cannot_edit_a_notebook(project, write, role):
    result = write(project, "src/gov/guard/analysis.ipynb", role, TICKET, "NotebookEdit")
    support.assert_denied(result, f"NotebookEdit with GOV_ROLE={role!r}")


@pytest.mark.parametrize("role", support.UNKNOWN_ROLES)
@pytest.mark.parametrize("form", sorted(BASH_WRITES), ids=sorted(BASH_WRITES))
def test_unknown_role_cannot_write_through_bash(project, bash, role, form):
    result = bash(project, BASH_WRITES[form], role, TICKET)
    support.assert_denied(result, f"Bash `{BASH_WRITES[form]}` with GOV_ROLE={role!r}")


@pytest.mark.parametrize("role", support.UNKNOWN_ROLES)
def test_unknown_role_gets_nothing_from_any_ticket(project, write, role):
    """No ticket in the project, of whatever role, opens a path for an unknown role."""
    attempts = [
        (support.TICKET_ID, "src/gov/guard/decide.py"),
        (support.ORCHESTRATOR_TICKET_ID, ".claude/settings.json"),
        (support.PRODUCT_SPEC_TICKET_ID, "docs/spec/feature.md"),
        (support.DOCS_TICKET_ID, "docs/notes.md"),
    ]
    for ticket, relpath in attempts:
        result = write(project, relpath, role, ticket)
        support.assert_denied(result, f"Write on {relpath} with GOV_ROLE={role!r} on {ticket}")


@pytest.mark.parametrize("role", support.UNKNOWN_ROLES)
def test_unknown_role_can_still_read(project, call, bash, role):
    read = call(project, "Read", {"file_path": str(project / "src/gov/guard/decide.py")},
                role=role, ticket=TICKET)
    support.assert_allowed(read, f"Read with GOV_ROLE={role!r}")
    for command in ("ls -la", "cat README.md", "git status --porcelain"):
        support.assert_allowed(bash(project, command, role, TICKET), f"Bash `{command}` with GOV_ROLE={role!r}")
