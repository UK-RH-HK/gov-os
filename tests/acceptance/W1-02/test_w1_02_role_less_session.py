"""W1-02 — a session with no declared role is read-only.

KPI success 4: "A session with no declared role, or an unknown role, is
read-only: every write is denied [CAP-58.c]".
KPI failure 3: "A session with no or an unknown role can write anywhere".

Only the "no declared role" half is tested here. The "unknown role" half needs
the channel through which a role is declared (KPI dispute KD-1).

Every call runs in a project whose one ticket is in progress for the engineer
role, so each write below would be inside or outside a live ticket's
``allowed_paths``. The session declares no role, and that decides.
"""

from __future__ import annotations

import pytest

import w1_02_support as support

WBS = support.TICKET_WBS_ID

# Repository-relative targets, by what they are to the ticket in progress.
EDIT_TARGETS = {
    "ticket-allowed-source": "src/gov/guard/decide.py",
    "ticket-allowed-new-file": "src/gov/guard/new_module.py",
    "ticket-allowed-unit-test": "tests/unit/guard/test_decide.py",
    "acceptance-test": f"tests/acceptance/{WBS}/test_fixture.py",
    "acceptance-test-new-file": f"tests/acceptance/{WBS}/test_added.py",
    "outside-ticket-source": "src/app/main.py",
    "outside-ticket-docs": "docs/notes.md",
    "outside-ticket-root-file": "README.md",
    "ticket-file": f".tickets/{support.TICKET_ID}.md",
    "session-settings": ".claude/settings.json",
    "new-directory": "brand/new/file.txt",
}

NOTEBOOK_TARGETS = {
    "ticket-allowed-notebook": "src/gov/guard/analysis.ipynb",
    "outside-ticket-notebook": "notes/analysis.ipynb",
}

# Plain shell write forms. {root} is the absolute project path.
BASH_WRITES = {
    "redirect-into-ticket-path": "echo changed > src/gov/guard/decide.py",
    "append-outside-ticket": "echo changed >> README.md",
    "tee-outside-ticket": "printf changed | tee docs/notes.md",
    "touch-acceptance-test": f"touch tests/acceptance/{WBS}/test_added.py",
    "rm-tracked-file": "rm README.md",
    "mv-tracked-file": "mv README.md README.old",
    "cp-into-ticket-path": "cp README.md src/gov/guard/copy.md",
    "mkdir-in-ticket-path": "mkdir -p src/gov/guard/new_package",
    "sed-in-place-in-ticket-path": "sed -i s/1/2/ src/gov/guard/decide.py",
    "cd-then-redirect": "cd src/gov/guard && echo changed > decide.py",
    "redirect-absolute-path": "echo changed > {root}/src/gov/guard/decide.py",
    "redirect-acceptance-test-absolute": "echo changed > {root}/tests/acceptance/" + WBS + "/test_fixture.py",
}

BASH_READS = {
    "ls": "ls -la",
    "cat": "cat README.md",
    "git-status": "git status --porcelain",
}

TICKET_STATES = {
    "no-tickets-directory": {},
    "ticket-open": {f"{support.TICKET_ID}.md": support.ticket_text(status="open")},
    "ticket-in-progress": {f"{support.TICKET_ID}.md": support.ticket_text(status="in_progress")},
    "two-tickets-in-progress": {
        f"{support.TICKET_ID}.md": support.ticket_text(status="in_progress"),
        "DAEO-zz91.md": support.ticket_text(
            ticket_id="DAEO-zz91", wbs_id="W1-91", status="in_progress",
            role="orchestrator", allowed_paths=("**",),
        ),
    },
}


def _assert_denied(result, what):
    assert result.decision == "deny", (
        f"{what} by a session with no declared role was not denied: {result.describe()}"
    )


@pytest.mark.parametrize("tool_name", ["Edit", "Write"])
@pytest.mark.parametrize("target", sorted(EDIT_TARGETS), ids=sorted(EDIT_TARGETS))
def test_role_less_session_cannot_edit_or_write(project, call, tool_name, target):
    relpath = EDIT_TARGETS[target]
    result = call(project, tool_name, support.edit_tool_input(tool_name, project / relpath))
    _assert_denied(result, f"{tool_name} on {relpath}")


@pytest.mark.parametrize("target", sorted(NOTEBOOK_TARGETS), ids=sorted(NOTEBOOK_TARGETS))
def test_role_less_session_cannot_edit_a_notebook(project, call, target):
    relpath = NOTEBOOK_TARGETS[target]
    result = call(project, "NotebookEdit", support.edit_tool_input("NotebookEdit", project / relpath))
    _assert_denied(result, f"NotebookEdit on {relpath}")


@pytest.mark.parametrize("form", sorted(BASH_WRITES), ids=sorted(BASH_WRITES))
def test_role_less_session_cannot_write_through_bash(project, call, form):
    command = BASH_WRITES[form].format(root=project)
    result = call(project, "Bash", support.bash_tool_input(command))
    _assert_denied(result, f"Bash `{command}`")


@pytest.mark.parametrize("state", sorted(TICKET_STATES), ids=sorted(TICKET_STATES))
def test_no_ticket_state_gives_a_role_less_session_write_access(hook, tmp_path, call, state):
    """Whatever the tickets say, a ticket is not a role declaration."""
    project = support.make_project(tmp_path / "project", TICKET_STATES[state])
    relpath = "src/gov/guard/decide.py"
    for tool_name in ("Edit", "Write"):
        result = call(project, tool_name, support.edit_tool_input(tool_name, project / relpath))
        _assert_denied(result, f"{tool_name} on {relpath} with {state}")
    command = f"echo changed > {relpath}"
    _assert_denied(call(project, "Bash", support.bash_tool_input(command)), f"Bash `{command}` with {state}")


def test_role_less_session_can_still_read_with_file_tools(project, call):
    """Read-only is not "no access": the guard denies writes, not reads."""
    attempts = {
        "Read": {"file_path": str(project / "src/gov/guard/decide.py")},
        "Grep": {"pattern": "VALUE", "path": str(project)},
        "Glob": {"pattern": "**/*.py", "path": str(project)},
    }
    for tool_name, tool_input in attempts.items():
        result = call(project, tool_name, tool_input)
        assert result.decision == "allow", (
            f"{tool_name} by a session with no declared role was not let through: {result.describe()}"
        )


@pytest.mark.parametrize("form", sorted(BASH_READS), ids=sorted(BASH_READS))
def test_role_less_session_can_still_read_through_bash(project, call, form):
    command = BASH_READS[form]
    result = call(project, "Bash", support.bash_tool_input(command))
    assert result.decision == "allow", (
        f"Bash `{command}` by a session with no declared role was not let through: {result.describe()}"
    )


def test_deciding_leaves_the_working_tree_unchanged(project, call):
    """The guard decides; it changes nothing git can see."""
    assert support.porcelain(project) == "", "the fixture project must start clean"
    attempts = [
        ("Write", support.edit_tool_input("Write", project / "src/gov/guard/decide.py")),
        ("Edit", support.edit_tool_input("Edit", project / "README.md")),
        ("Bash", support.bash_tool_input("echo changed > README.md")),
        ("Bash", support.bash_tool_input("rm README.md")),
        ("Read", {"file_path": str(project / "README.md")}),
    ]
    for tool_name, tool_input in attempts:
        result = call(project, tool_name, tool_input)
        assert result.decision in ("deny", "allow"), (
            f"the guard gave no decision on {tool_name}: {result.describe()}"
        )
    assert support.porcelain(project) == "", (
        "git status --porcelain changed after the guard's decisions:\n" + support.porcelain(project)
    )
