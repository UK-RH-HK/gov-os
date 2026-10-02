"""W1-03 — a change under ``tests/acceptance/**`` by anyone but the test designer is undone.

KPI success 2: "Changes under tests/acceptance/** by a non-test-designer role are
restored from HEAD and the breach is recorded".
KPI failure 2: "A legitimate in-scope change is reverted".
MR-3: the builder never writes its own acceptance tests.

"Restored from HEAD" is tested as: after the check, ``tests/acceptance`` equals
HEAD. A changed or deleted file has its HEAD content again, a file HEAD does
not hold is gone, and nothing under ``tests/acceptance`` is left staged.

"The breach is recorded" is tested as: the call added a finding with action
``reverted`` that names the path (DEC-122).

Each test makes one whole Bash call (PreToolUse hook, command, PostToolUse hook)
in a project with a clean tree, so every change is the call's own (DEC-124). A
tree that was already dirty before the call is in ``test_w1_03_dirty_tree.py``.
"""

from __future__ import annotations

import pytest

import w1_03_support as support

ENGINEER = support.ENGINEER
ORCHESTRATOR = support.ORCHESTRATOR
PRODUCT_SPEC = support.PRODUCT_SPEC
DESIGNER = support.TEST_DESIGNER
AUDITOR = support.AUDITOR
TICKET = support.TICKET_ID
WBS = support.TICKET_WBS_ID
ACCEPTANCE = support.ACCEPTANCE_REL
ACCEPTANCE_FILE = support.ACCEPTANCE_FILE
SOURCE = support.SOURCE_FILE

# name: (command, path git status shows afterwards)
BREACHES = {
    "file-changed": (f"echo changed >> {ACCEPTANCE_FILE}", ACCEPTANCE_FILE),
    "file-replaced": (f"echo replaced > {ACCEPTANCE_FILE}", ACCEPTANCE_FILE),
    "file-deleted": (f"rm {ACCEPTANCE_FILE}", ACCEPTANCE_FILE),
    "directory-deleted": (f"rm -r {ACCEPTANCE}/{WBS}", ACCEPTANCE_FILE),
    "whole-tree-deleted": (f"rm -r {ACCEPTANCE}", ACCEPTANCE_FILE),
    "file-added": (f"echo new > {ACCEPTANCE}/{WBS}/test_added.py", f"{ACCEPTANCE}/{WBS}/test_added.py"),
    "directory-added": (
        f"mkdir -p {ACCEPTANCE}/W1-77 && echo new > {ACCEPTANCE}/W1-77/test_new.py",
        f"{ACCEPTANCE}/W1-77/test_new.py"),
    "file-moved-out": (f"mv {ACCEPTANCE_FILE} src/gov/guard/moved.py", ACCEPTANCE_FILE),
    "file-moved-in": (f"mv {SOURCE} {ACCEPTANCE}/{WBS}/test_moved.py", f"{ACCEPTANCE}/{WBS}/test_moved.py"),
    "change-staged": (f"echo changed >> {ACCEPTANCE_FILE} && git add {ACCEPTANCE_FILE}", ACCEPTANCE_FILE),
    "new-file-staged": (
        f"echo new > {ACCEPTANCE}/{WBS}/test_added.py && git add {ACCEPTANCE}/{WBS}/test_added.py",
        f"{ACCEPTANCE}/{WBS}/test_added.py"),
    "deletion-staged": (f"git rm -q {ACCEPTANCE_FILE}", ACCEPTANCE_FILE),
}

# name: (GOV_ROLE, GOV_TICKET). Every session but the test designer's.
NOT_THE_DESIGNER = {
    "engineer": (ENGINEER, TICKET),
    "engineer-on-a-ticket-that-names-acceptance-tests": (ENGINEER, support.ACCEPTANCE_NAMING_TICKET_ID),
    "engineer-without-a-ticket": (ENGINEER, None),
    "orchestrator": (ORCHESTRATOR, support.ORCHESTRATOR_TICKET_ID),
    "product-spec": (PRODUCT_SPEC, support.PRODUCT_SPEC_TICKET_ID),
    "auditor": (AUDITOR, support.AUDITOR_TICKET_ID),
    "no-role": (None, TICKET),
    "unknown-role": ("developer", TICKET),
}


def _assert_acceptance_equals_head(project, what):
    status = support.porcelain(project, ACCEPTANCE)
    assert status == "", f"{what}: tests/acceptance was not restored from HEAD; git status shows:\n{status}"
    path = project / ACCEPTANCE_FILE
    assert path.is_file(), f"{what}: {ACCEPTANCE_FILE} is missing after the check"
    assert path.read_text(encoding="utf-8") == support.head_text(project, ACCEPTANCE_FILE), (
        f"{what}: {ACCEPTANCE_FILE} does not hold its HEAD content"
    )


@pytest.mark.parametrize("case", sorted(BREACHES), ids=sorted(BREACHES))
def test_an_engineer_s_change_under_acceptance_tests_is_restored_from_head(project, after_bash, case):
    command, changed = BREACHES[case]
    result = after_bash(project, command, ENGINEER, TICKET, changed=[changed])
    what = f"`{command}` by the engineer on {TICKET}"
    _assert_acceptance_equals_head(project, what)
    support.assert_caught(result, ACCEPTANCE, what=what, action=support.REVERTED)


@pytest.mark.parametrize("case", sorted(NOT_THE_DESIGNER), ids=sorted(NOT_THE_DESIGNER))
def test_every_session_but_the_test_designer_s_is_restored(project, after_bash, case):
    role, ticket = NOT_THE_DESIGNER[case]
    command = f"echo changed >> {ACCEPTANCE_FILE} && echo new > {ACCEPTANCE}/{WBS}/test_added.py"
    result = after_bash(project, command, role, ticket,
                        changed=[ACCEPTANCE_FILE, f"{ACCEPTANCE}/{WBS}/test_added.py"])
    what = f"`{command}` with GOV_ROLE={role!r} GOV_TICKET={ticket!r}"
    _assert_acceptance_equals_head(project, what)
    support.assert_caught(result, ACCEPTANCE, what=what, action=support.REVERTED)


def test_the_restore_leaves_the_engineer_s_own_work_alone(project, after_bash):
    """One call changes an acceptance test and the engineer's own files. Only the first is undone."""
    command = (f"echo changed >> {SOURCE} && echo new > src/gov/guard/new_module.py "
               f"&& git add src/gov/guard/new_module.py && echo changed >> {ACCEPTANCE_FILE}")
    result = after_bash(project, command, ENGINEER, TICKET, changed=[SOURCE, ACCEPTANCE_FILE])
    what = f"`{command}` by the engineer on {TICKET}"
    _assert_acceptance_equals_head(project, what)
    support.assert_caught(result, ACCEPTANCE_FILE, what=what, action=support.REVERTED)
    support.assert_not_recorded(result, SOURCE, "src/gov/guard/new_module.py", what=what)
    assert (project / SOURCE).read_text(encoding="utf-8").endswith("changed\n"), (
        f"{what}: the in-scope change to {SOURCE} was reverted"
    )
    assert (project / "src/gov/guard/new_module.py").read_text(encoding="utf-8") == "new\n", (
        f"{what}: the in-scope new file src/gov/guard/new_module.py was removed"
    )
    lines = set(support.porcelain_all(project).splitlines())
    assert lines == {f" M {SOURCE}", "A  src/gov/guard/new_module.py"}, (
        f"{what}: git status after the check is not the engineer's own two changes: {sorted(lines)}"
    )
    assert SOURCE not in result.report, f"{what}: the report names the in-scope file {SOURCE}: {result.report!r}"


def test_the_test_designer_s_changes_stay(project, after_bash):
    command = (f"echo changed >> {ACCEPTANCE_FILE} && echo new > {ACCEPTANCE}/{WBS}/test_added.py "
               f"&& mkdir -p {ACCEPTANCE}/W1-77 && echo new > {ACCEPTANCE}/W1-77/test_new.py "
               f"&& rm {ACCEPTANCE}/{WBS}/README.md")
    result = after_bash(project, command, DESIGNER, TICKET,
                        changed=[ACCEPTANCE_FILE, f"{ACCEPTANCE}/W1-77/test_new.py"])
    what = f"`{command}` by the test designer on {TICKET}"
    support.assert_silent(result, what)
    assert (project / ACCEPTANCE_FILE).read_text(encoding="utf-8").endswith("changed\n"), (
        f"{what}: the test designer's change to {ACCEPTANCE_FILE} was reverted"
    )
    assert (project / ACCEPTANCE / WBS / "test_added.py").is_file(), f"{what}: the new test file was removed"
    assert (project / ACCEPTANCE / "W1-77" / "test_new.py").is_file(), f"{what}: the new test directory was removed"
    assert not (project / ACCEPTANCE / WBS / "README.md").exists(), f"{what}: a deleted file was brought back"


def test_the_test_designer_s_scope_does_not_depend_on_the_ticket_paths(project, after_bash):
    """The designer writes ``tests/acceptance/**`` on an engineer's ticket, whose paths never name it."""
    for ticket in (TICKET, support.DOCS_TICKET_ID):
        command = f"echo changed >> {ACCEPTANCE_FILE}"
        result = after_bash(project, command, DESIGNER, ticket, changed=[ACCEPTANCE_FILE])
        support.assert_silent(result, f"`{command}` by the test designer on {ticket}")
    assert (project / ACCEPTANCE_FILE).read_text(encoding="utf-8").endswith("changed\nchanged\n"), (
        "the test designer's changes were reverted"
    )


# name: (GOV_ROLE, agent_type, restored)
SUBAGENTS = {
    "designer-in-orchestrator-session": (ORCHESTRATOR, DESIGNER, False),
    "designer-in-engineer-session": (ENGINEER, DESIGNER, False),
    "engineer-in-designer-session": (DESIGNER, ENGINEER, True),
    "engineer-in-orchestrator-session": (ORCHESTRATOR, ENGINEER, True),
    "auditor-in-designer-session": (DESIGNER, AUDITOR, True),
    "general-purpose-in-designer-session": (DESIGNER, "general-purpose", True),
    "explore-in-designer-session": (DESIGNER, "Explore", True),
    "designer-in-a-session-without-a-role": (None, DESIGNER, True),
    "designer-in-a-session-with-an-unknown-role": ("developer", DESIGNER, True),
}


@pytest.mark.parametrize("case", sorted(SUBAGENTS), ids=sorted(SUBAGENTS))
def test_inside_a_subagent_the_subagent_s_role_decides_the_restore(project, after_bash, case):
    """DEC-117: the subagent's role governs. DEC-113: a subagent that is not a role has no write.

    DEC-125: in a session with no declared role, a role subagent has no write
    either, the test designer's included.
    """
    session_role, agent_type, restored = SUBAGENTS[case]
    command = f"echo changed >> {ACCEPTANCE_FILE}"
    result = after_bash(project, command, session_role, TICKET, changed=[ACCEPTANCE_FILE], subagent=agent_type)
    what = f"`{command}` by subagent {agent_type} in a session with GOV_ROLE={session_role!r}"
    if restored:
        _assert_acceptance_equals_head(project, what)
        support.assert_caught(result, ACCEPTANCE_FILE, what=what, action=support.REVERTED)
    else:
        support.assert_silent(result, what)
        assert (project / ACCEPTANCE_FILE).read_text(encoding="utf-8").endswith("changed\n"), (
            f"{what}: the test designer's change was reverted"
        )
