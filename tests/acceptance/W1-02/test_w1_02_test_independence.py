"""W1-02 — the builder never writes acceptance tests; the test designer writes nothing else.

KPI success 2: "The engineer role is denied every write under tests/acceptance/**;
the independent-test-designer role is allowed only there [CAP-38.c]".

Readings accepted with KD-1:

- every role but the test designer is denied ``tests/acceptance/**``, also when
  a ticket's ``allowed_paths`` name it;
- the test designer may write ``tests/acceptance/**`` and no other repository
  path, whatever the ticket's ``allowed_paths`` say;
- the independent auditor is read-only. Whether an auditor may write inside an
  auditor ticket's own ``allowed_paths`` is open (KD-6) and is not tested.
"""

from __future__ import annotations

import pytest

import w1_02_support as support

ENGINEER = support.ENGINEER
ORCHESTRATOR = support.ORCHESTRATOR
PRODUCT_SPEC = support.PRODUCT_SPEC
DESIGNER = support.TEST_DESIGNER
AUDITOR = support.AUDITOR
TICKET = support.TICKET_ID
WBS = support.TICKET_WBS_ID

FILE_TOOLS = ["Edit", "Write"]

ACCEPTANCE_TARGETS = {
    "existing-test": f"tests/acceptance/{WBS}/test_fixture.py",
    "new-test": f"tests/acceptance/{WBS}/test_added.py",
    "readme": f"tests/acceptance/{WBS}/README.md",
    "nested-data": f"tests/acceptance/{WBS}/data/deep/case.json",
    "another-ticket": "tests/acceptance/W1-91/test_other.py",
    "file-directly-under": "tests/acceptance/conftest.py",
}

# How a builder might reach an acceptance test without naming the directory plainly.
INDIRECT_TARGETS = {
    "dot-dot-from-the-allowed-directory": f"src/gov/guard/../../../tests/acceptance/{WBS}/test_fixture.py",
    "symlink-in-the-allowed-directory": f"src/gov/guard/acceptance_link/{WBS}/test_fixture.py",
    "symlink-new-file": f"src/gov/guard/acceptance_link/{WBS}/test_added.py",
}

TICKET_ROLES = {
    ENGINEER: support.TICKET_ID,
    ORCHESTRATOR: support.ORCHESTRATOR_TICKET_ID,
    PRODUCT_SPEC: support.PRODUCT_SPEC_TICKET_ID,
}

DESIGNER_DENIED = {
    "source-in-the-ticket-paths": "src/gov/guard/decide.py",
    "unit-test-in-the-ticket-paths": "tests/unit/guard/test_decide.py",
    "docs": "docs/notes.md",
    "root-file": "README.md",
    "ticket-file": f".tickets/{TICKET}.md",
    "session-settings": ".claude/settings.json",
    "directory-with-a-similar-name": "tests/acceptance_notes/notes.md",
    "file-with-a-similar-name": "tests/acceptance.md",
    "tests-root": "tests/conftest.py",
    "dot-dot-out-of-acceptance": "tests/acceptance/../unit/guard/test_decide.py",
}

DESIGNER_BASH_ALLOWED = {
    "redirect": f"echo changed > tests/acceptance/{WBS}/test_added.py",
    "touch": f"touch tests/acceptance/{WBS}/test_added.py",
    "mkdir": "mkdir -p tests/acceptance/W1-91",
    "rm": f"rm tests/acceptance/{WBS}/test_fixture.py",
    "cd-then-redirect": f"cd tests/acceptance/{WBS} && echo changed > test_added.py",
}

DESIGNER_BASH_DENIED = {
    "redirect-to-source": "echo changed > src/gov/guard/decide.py",
    "cp-out-of-acceptance": f"cp tests/acceptance/{WBS}/test_fixture.py tests/unit/guard/test_copy.py",
    "mv-out-of-acceptance": f"mv tests/acceptance/{WBS}/test_fixture.py docs/moved.py",
    "mv-source-into-acceptance": f"mv src/gov/guard/decide.py tests/acceptance/{WBS}/decide.py",
    "touch-root": "touch notes.txt",
}


# --------------------------------------------------------------------------
# Builders and the other ticket roles
# --------------------------------------------------------------------------

@pytest.mark.parametrize("tool_name", FILE_TOOLS)
@pytest.mark.parametrize("target", sorted(ACCEPTANCE_TARGETS), ids=sorted(ACCEPTANCE_TARGETS))
def test_engineer_cannot_write_under_acceptance_tests(project, write, tool_name, target):
    relpath = ACCEPTANCE_TARGETS[target]
    result = write(project, relpath, ENGINEER, TICKET, tool_name)
    support.assert_denied(result, f"{tool_name} on {relpath} by the engineer")


@pytest.mark.parametrize("tool_name", FILE_TOOLS)
@pytest.mark.parametrize("target", sorted(INDIRECT_TARGETS), ids=sorted(INDIRECT_TARGETS))
def test_engineer_cannot_reach_acceptance_tests_indirectly(project, write, tool_name, target):
    relpath = INDIRECT_TARGETS[target]
    result = write(project, relpath, ENGINEER, TICKET, tool_name)
    support.assert_denied(result, f"{tool_name} on {relpath} by the engineer")


@pytest.mark.parametrize("role", sorted(TICKET_ROLES))
def test_no_ticket_role_can_write_under_acceptance_tests(project, write, role):
    for relpath in (ACCEPTANCE_TARGETS["existing-test"], ACCEPTANCE_TARGETS["new-test"]):
        for tool_name in FILE_TOOLS:
            result = write(project, relpath, role, TICKET_ROLES[role], tool_name)
            support.assert_denied(result, f"{tool_name} on {relpath} by {role}")


@pytest.mark.parametrize("role", sorted(TICKET_ROLES))
def test_a_ticket_that_names_acceptance_tests_still_gives_no_access(hook, tmp_path, write, bash, role):
    """``allowed_paths`` cannot hand ``tests/acceptance/**`` to a role that is not the test designer."""
    ticket_id = "DAEO-zz93"
    project = support.make_project(tmp_path / "project", {
        f"{ticket_id}.md": support.ticket_text(
            ticket_id=ticket_id, wbs_id="W1-93", role=role,
            allowed_paths=("tests/**", "tests/acceptance/**", f"tests/acceptance/{WBS}/test_fixture.py"),
        ),
    })
    support.assert_allowed(
        write(project, "tests/unit/guard/test_decide.py", role, ticket_id),
        f"Write under tests/unit by {role}, inside the ticket's tests/**,",
    )
    for relpath in sorted(ACCEPTANCE_TARGETS.values()):
        for tool_name in FILE_TOOLS:
            result = write(project, relpath, role, ticket_id, tool_name)
            support.assert_denied(result, f"{tool_name} on {relpath} by {role}, although the ticket names the path,")
    for command in (
        f"echo changed > tests/acceptance/{WBS}/test_fixture.py",
        f"rm tests/acceptance/{WBS}/test_fixture.py",
    ):
        support.assert_denied(bash(project, command, role, ticket_id), f"Bash `{command}` by {role}")


# --------------------------------------------------------------------------
# The independent test designer
# --------------------------------------------------------------------------

@pytest.mark.parametrize("tool_name", FILE_TOOLS)
@pytest.mark.parametrize("target", sorted(ACCEPTANCE_TARGETS), ids=sorted(ACCEPTANCE_TARGETS))
def test_test_designer_can_write_under_acceptance_tests(project, write, tool_name, target):
    relpath = ACCEPTANCE_TARGETS[target]
    result = write(project, relpath, DESIGNER, TICKET, tool_name)
    support.assert_allowed(result, f"{tool_name} on {relpath} by the test designer")


@pytest.mark.parametrize("tool_name", FILE_TOOLS)
@pytest.mark.parametrize("target", sorted(DESIGNER_DENIED), ids=sorted(DESIGNER_DENIED))
def test_test_designer_cannot_write_anywhere_else(project, write, tool_name, target):
    relpath = DESIGNER_DENIED[target]
    result = write(project, relpath, DESIGNER, TICKET, tool_name)
    support.assert_denied(result, f"{tool_name} on {relpath} by the test designer")


def test_test_designer_scope_does_not_depend_on_the_ticket_paths(project, write):
    """On a ticket whose paths are ``docs/**``: still acceptance tests only."""
    ticket = support.DOCS_TICKET_ID
    support.assert_allowed(
        write(project, f"tests/acceptance/{WBS}/test_added.py", DESIGNER, ticket),
        "Write under tests/acceptance by the test designer",
    )
    support.assert_denied(
        write(project, "docs/notes.md", DESIGNER, ticket),
        "Write on docs/notes.md by the test designer, although the ticket lists docs/**,",
    )


@pytest.mark.parametrize("form", sorted(DESIGNER_BASH_ALLOWED), ids=sorted(DESIGNER_BASH_ALLOWED))
def test_test_designer_bash_write_under_acceptance_tests_is_allowed(project, bash, form):
    command = DESIGNER_BASH_ALLOWED[form]
    support.assert_allowed(bash(project, command, DESIGNER, TICKET), f"Bash `{command}` by the test designer")


@pytest.mark.parametrize("form", sorted(DESIGNER_BASH_DENIED), ids=sorted(DESIGNER_BASH_DENIED))
def test_test_designer_bash_write_elsewhere_is_denied(project, bash, form):
    command = DESIGNER_BASH_DENIED[form]
    support.assert_denied(bash(project, command, DESIGNER, TICKET), f"Bash `{command}` by the test designer")


# --------------------------------------------------------------------------
# The independent auditor
# --------------------------------------------------------------------------

@pytest.mark.parametrize("target", [
    "src/gov/guard/decide.py",
    f"tests/acceptance/{WBS}/test_fixture.py",
    "docs/notes.md",
    "README.md",
    f".tickets/{TICKET}.md",
])
def test_auditor_cannot_write_into_another_role_s_work(project, write, bash, target):
    for tool_name in FILE_TOOLS:
        result = write(project, target, AUDITOR, TICKET, tool_name)
        support.assert_denied(result, f"{tool_name} on {target} by the auditor")
    command = f"echo changed > {target}"
    support.assert_denied(bash(project, command, AUDITOR, TICKET), f"Bash `{command}` by the auditor")


def test_auditor_can_still_read(project, call, bash):
    result = call(project, "Read", {"file_path": str(project / "src/gov/guard/decide.py")},
                  role=AUDITOR, ticket=TICKET)
    support.assert_allowed(result, "Read by the auditor")
    support.assert_allowed(bash(project, "git status --porcelain", AUDITOR, TICKET), "Bash read by the auditor")
