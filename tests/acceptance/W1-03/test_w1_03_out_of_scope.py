"""W1-03 — after a Bash call, a change outside ``allowed_paths`` is reported and recorded.

KPI success 1: "After every Bash call …, git status --porcelain is compared with
allowed_paths; a change outside them is reported to the agent and recorded as a
containment finding" [CAP-58.a].
KPI failure 1: "Any out-of-scope change survives without a finding".
KPI failure 2: "A legitimate in-scope change is reverted".

Each test makes one whole Bash call in a project with a clean tree: the
PreToolUse hook, the command for real, the PostToolUse hook (DEC-124). The
commands here are ordinary; the forms the guard cannot see are in
``test_w1_03_bash_forms.py`` and ``test_w1_03_i06_forms.py``. A tree that was
already dirty before the call is in ``test_w1_03_dirty_tree.py``.

"Caught" is both halves of the KPI: the report to the agent names the path, and
the call added a finding for it to ``.gov-runtime/findings.jsonl`` (DEC-122).
The fields of the finding are tested in ``test_w1_03_finding_record.py``.
Whether an out-of-scope change outside ``tests/acceptance/**`` is also undone is
left to the implementer; the tests take no side.
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
SOURCE = support.SOURCE_FILE

# name: (command, paths git status shows afterwards, names the report must hold)
OUTSIDE = {
    "tracked-file-changed": ("echo changed >> README.md", ["README.md"], ["README.md"]),
    "new-file": ("echo new > docs/new.md", ["docs/new.md"], ["docs/new.md"]),
    "tracked-file-deleted": ("rm docs/notes.md", ["docs/notes.md"], ["docs/notes.md"]),
    "new-directory": ("mkdir -p tools/x && echo new > tools/x/run.sh", ["tools/x/run.sh"], ["tools/"]),
    "moved-out-of-the-ticket-paths": (
        "mv src/gov/guard/decide.py docs/decide.py", ["docs/decide.py"], ["docs/decide.py"]),
    "staged-change": ("echo changed >> README.md && git add README.md", ["README.md"], ["README.md"]),
    "name-with-a-space": ("echo new > 'docs/my notes.md'", ["docs/my notes.md"], ["docs/my notes.md"]),
    "the-ticket-file": (f"echo changed >> .tickets/{TICKET}.md", [f".tickets/{TICKET}.md"], [f".tickets/{TICKET}.md"]),
    "harness-settings": ("echo changed >> .claude/settings.json", [".claude/settings.json"], [".claude/settings.json"]),
    "the-installed-hook-directory": (
        "echo new > governance/kernel/hooks/extra.py",
        ["governance/kernel/hooks/extra.py"], ["governance/kernel/hooks/extra.py"]),
    "directory-with-a-similar-name": (
        "echo changed >> src/gov/guardian/other.py", ["src/gov/guardian/other.py"], ["src/gov/guardian/other.py"]),
    "same-file-name-in-another-directory": (
        "echo new > docs/pyproject.toml", ["docs/pyproject.toml"], ["docs/pyproject.toml"]),
    "below-a-single-star-pattern": (
        "mkdir -p template/governance/kernel/hooks/sub && echo new > template/governance/kernel/hooks/sub/pretooluse.py",
        ["template/governance/kernel/hooks/sub/pretooluse.py"], ["template/governance/kernel/hooks/sub/"]),
    "another-role-s-paths": ("echo changed >> docs/spec/feature.md", ["docs/spec/feature.md"], ["docs/spec/feature.md"]),
}

# name: (command, path that must hold after the check, its expected state)
#   state: text  -> the file ends with this text;  None -> the file stays deleted
INSIDE = {
    "tracked-file-changed": ("echo changed >> src/gov/guard/decide.py", SOURCE, "changed\n"),
    "new-file": ("echo new > src/gov/guard/new_module.py", "src/gov/guard/new_module.py", "new\n"),
    "new-package": (
        "mkdir -p src/gov/guard/pkg/deep && echo new > src/gov/guard/pkg/deep/mod.py",
        "src/gov/guard/pkg/deep/mod.py", "new\n"),
    "tracked-file-deleted": ("rm src/gov/guard/decide.py", SOURCE, None),
    "staged-change": ("echo changed >> src/gov/guard/decide.py && git add src/gov/guard/decide.py", SOURCE, "changed\n"),
    "renamed-inside": (
        "git mv src/gov/guard/decide.py src/gov/guard/renamed.py", "src/gov/guard/renamed.py", "VALUE = 1\n"),
    "unit-test": ("echo changed >> tests/unit/guard/test_decide.py", "tests/unit/guard/test_decide.py", "changed\n"),
    "single-file-pattern": ("echo changed >> pyproject.toml", "pyproject.toml", "changed\n"),
    "single-star-pattern": (
        "echo new > template/governance/kernel/hooks/pretooluse_guard.sh",
        "template/governance/kernel/hooks/pretooluse_guard.sh", "new\n"),
}


def _state(project, relpath):
    path = project / relpath
    return path.read_text(encoding="utf-8") if path.exists() else None


@pytest.mark.parametrize("case", sorted(OUTSIDE), ids=sorted(OUTSIDE))
def test_a_change_outside_the_ticket_paths_is_reported(project, after_bash, case):
    command, changed, names = OUTSIDE[case]
    result = after_bash(project, command, ENGINEER, TICKET, changed=changed)
    support.assert_caught(result, *names, what=f"`{command}` by the engineer on {TICKET}")


@pytest.mark.parametrize("case", sorted(INSIDE), ids=sorted(INSIDE))
def test_a_change_inside_the_ticket_paths_is_left_alone(project, after_bash, case):
    command, relpath, expected = INSIDE[case]
    result = after_bash(project, command, ENGINEER, TICKET)
    status_after = support.porcelain_all(project)
    support.assert_silent(result, f"`{command}` by the engineer on {TICKET}")
    state = _state(project, relpath)
    if expected is None:
        assert state is None, f"the check brought {relpath} back; the engineer deleted it inside the ticket paths"
    else:
        assert state is not None and state.endswith(expected), (
            f"the check reverted the in-scope change to {relpath}: content is {state!r}"
        )
    assert status_after.strip(), f"the in-scope change of `{command}` is gone from git status"


def test_nothing_is_reported_on_a_clean_tree(project, after_bash):
    for command in ("ls -la", "cat README.md", "git status --porcelain", "git log --oneline -1"):
        result = after_bash(project, command, ENGINEER, TICKET)
        support.assert_silent(result, f"`{command}` by the engineer on {TICKET}")
    assert support.porcelain(project) == "", (
        "the check itself changed the working tree:\n" + support.porcelain(project)
    )


def test_one_call_with_both_kinds_reports_only_the_outside_change(project, after_bash):
    command = "echo changed >> src/gov/guard/decide.py && echo changed >> README.md"
    result = after_bash(project, command, ENGINEER, TICKET, changed=[SOURCE, "README.md"])
    what = f"`{command}` by the engineer on {TICKET}"
    support.assert_caught(result, "README.md", what=what)
    assert SOURCE not in result.report, f"{what}: the report names the in-scope file {SOURCE}: {result.report!r}"
    support.assert_not_recorded(result, SOURCE, what=what)
    assert _state(project, SOURCE).endswith("changed\n"), f"{what}: the in-scope change to {SOURCE} was reverted"


def test_a_new_directory_is_judged_file_by_file(project, after_bash):
    """``git status --porcelain`` shows a new directory as one line. The files inside decide."""
    ticket = support.NEW_DIRECTORY_TICKET_ID   # allowed_paths: tools/guard/**
    command = "mkdir -p tools/guard && echo new > tools/guard/a.py"
    result = after_bash(project, command, ENGINEER, ticket, changed=["tools/guard/a.py"])
    support.assert_silent(result, f"`{command}` by the engineer on {ticket}")
    assert _state(project, "tools/guard/a.py") == "new\n", "the in-scope file tools/guard/a.py was removed"

    command = "mkdir -p tools/other && echo new > tools/other/b.py"
    result = after_bash(project, command, ENGINEER, ticket, changed=["tools/other/b.py"])
    what = f"`{command}` by the engineer on {ticket}"
    support.assert_caught(result, "tools/other", what=what)
    assert "tools/guard" not in result.report, f"{what}: the report names the in-scope directory: {result.report!r}"
    support.assert_not_recorded(result, "tools/guard/a.py", what=what)
    assert _state(project, "tools/guard/a.py") == "new\n", "the in-scope file tools/guard/a.py was removed"


def test_the_comparison_follows_the_active_ticket(project, after_bash):
    docs_ticket = support.DOCS_TICKET_ID   # allowed_paths: docs/**
    command = "echo changed >> docs/notes.md"
    result = after_bash(project, command, ENGINEER, docs_ticket, changed=["docs/notes.md"])
    support.assert_silent(result, f"`{command}` by the engineer on {docs_ticket}")
    assert _state(project, "docs/notes.md").endswith("changed\n"), "the in-scope change to docs/notes.md was reverted"

    command = "echo changed >> src/gov/guard/decide.py"
    result = after_bash(project, command, ENGINEER, docs_ticket, changed=[SOURCE])
    support.assert_caught(result, SOURCE, what=f"`{command}` by the engineer on {docs_ticket}")


# DEC-156 / DEC-171 (W1-45): the orchestrator case is removed; an orchestrator change
# outside its ticket's allowed_paths is a record, not a finding.
# Rewrite: owner correction, DEC-156.
@pytest.mark.parametrize("role, ticket, relpath", [
    (PRODUCT_SPEC, support.PRODUCT_SPEC_TICKET_ID, "docs/spec/feature.md"),
], ids=["product-spec"])
def test_each_ticket_role_is_compared_with_its_own_ticket(project, after_bash, role, ticket, relpath):
    command = f"echo changed >> {relpath}"
    result = after_bash(project, command, role, ticket, changed=[relpath])
    support.assert_silent(result, f"`{command}` by {role} on {ticket}")
    assert _state(project, relpath).endswith("changed\n"), f"the in-scope change to {relpath} was reverted"

    command = "echo changed >> README.md"
    result = after_bash(project, command, role, ticket, changed=["README.md"])
    what = f"`{command}` by {role} on {ticket}"
    support.assert_caught(result, "README.md", what=what)
    assert relpath not in result.report, f"{what}: the report names the in-scope file {relpath}: {result.report!r}"


# name: (GOV_ROLE, GOV_TICKET). None of these sessions has any ticket path.
NO_TICKET_PATHS = {
    "no-role": (None, TICKET),
    "no-role-no-ticket": (None, None),
    "empty-role": ("", TICKET),
    "unknown-role": ("developer", TICKET),
    "engineer-without-a-ticket": (ENGINEER, None),
    "engineer-on-a-ticket-that-does-not-exist": (ENGINEER, "DAEO-none"),
    "engineer-on-the-orchestrator-s-ticket": (ENGINEER, support.ORCHESTRATOR_TICKET_ID),
    "auditor-on-the-engineer-s-ticket": (AUDITOR, TICKET),
    # DEC-156 (W1-45): the orchestrator case is removed; the orchestrator has
    # paths regardless of the active ticket.  Rewrite: owner correction, DEC-156.
}


@pytest.mark.parametrize("case", sorted(NO_TICKET_PATHS), ids=sorted(NO_TICKET_PATHS))
def test_a_session_without_ticket_paths_has_every_change_reported(project, after_bash, case):
    role, ticket = NO_TICKET_PATHS[case]
    for relpath in (SOURCE, ".claude/settings.json"):
        command = f"echo changed >> {relpath}"
        result = after_bash(project, command, role, ticket, changed=[relpath])
        support.assert_caught(result, relpath, what=f"`{command}` with GOV_ROLE={role!r} GOV_TICKET={ticket!r}")


def test_the_test_designer_is_reported_outside_acceptance_tests(project, after_bash):
    command = "echo changed >> src/gov/guard/decide.py"
    result = after_bash(project, command, DESIGNER, TICKET, changed=[SOURCE])
    support.assert_caught(result, SOURCE, what=f"`{command}` by the test designer on {TICKET}")


def test_scratch_writes_are_not_reported(project, after_bash):
    """The kernel scratch set (DEC-108) is outside what git status shows."""
    command = (f"mkdir -p {support.SCRATCH_REL} && echo note > {support.SCRATCH_REL}/note.txt "
               "&& echo note > {tmpdir}/note.txt")
    result = after_bash(project, command, ENGINEER, TICKET)
    support.assert_silent(result, f"`{command}` by the engineer on {TICKET}")
    assert (project / support.SCRATCH_REL / "note.txt").read_text(encoding="utf-8") == "note\n", (
        "the check removed a file from the scratch directory"
    )


def test_a_failed_call_is_checked_too(project, after_bash):
    """"After every Bash call": the harness sends PostToolUseFailure when the call failed."""
    command = "echo changed >> src/gov/guard/decide.py; exit 3"
    result = after_bash(project, command, ENGINEER, TICKET, changed=[SOURCE], failed=True)
    support.assert_silent(result, f"`{command}` (failed call) by the engineer on {TICKET}")
    assert _state(project, SOURCE).endswith("changed\n"), "the in-scope change of a failed call was reverted"

    command = "echo changed >> README.md; exit 3"
    result = after_bash(project, command, ENGINEER, TICKET, changed=["README.md"], failed=True)
    what = f"`{command}` (failed call) by the engineer on {TICKET}"
    support.assert_caught(result, "README.md", what=what)
    assert SOURCE not in result.report, f"{what}: the report names the in-scope file {SOURCE}: {result.report!r}"


# name: (GOV_ROLE, agent_type, GOV_TICKET, path, reported)
SUBAGENTS = {
    "engineer-in-orchestrator-session-inside": (ORCHESTRATOR, ENGINEER, TICKET, SOURCE, False),
    "engineer-in-orchestrator-session-outside": (ORCHESTRATOR, ENGINEER, TICKET, "README.md", True),
    "engineer-in-orchestrator-session-on-the-orchestrator-s-ticket":
        (ORCHESTRATOR, ENGINEER, support.ORCHESTRATOR_TICKET_ID, ".claude/settings.json", True),
    "orchestrator-in-engineer-session-on-its-own-ticket":
        (ENGINEER, ORCHESTRATOR, support.ORCHESTRATOR_TICKET_ID, ".claude/settings.json", False),
    "auditor-in-engineer-session-inside-the-engineer-s-paths": (ENGINEER, AUDITOR, TICKET, SOURCE, True),
    "general-purpose-in-engineer-session": (ENGINEER, "general-purpose", TICKET, SOURCE, True),
    "explore-in-engineer-session": (ENGINEER, "Explore", TICKET, SOURCE, True),
    "engineer-in-a-session-without-a-role": (None, ENGINEER, TICKET, SOURCE, True),
    "engineer-in-a-session-with-an-unknown-role": ("developer", ENGINEER, TICKET, SOURCE, True),
}


@pytest.mark.parametrize("case", sorted(SUBAGENTS), ids=sorted(SUBAGENTS))
def test_inside_a_subagent_the_subagent_s_role_is_compared(project, after_bash, case):
    """DEC-117: the subagent's role governs its calls. DEC-113: a subagent that is not a role has no write.

    DEC-125: in a session with no declared role, a role subagent has no write either.
    """
    session_role, agent_type, ticket, relpath, reported = SUBAGENTS[case]
    command = f"echo changed >> {relpath}"
    result = after_bash(project, command, session_role, ticket, changed=[relpath], subagent=agent_type)
    what = f"`{command}` by subagent {agent_type} in a session with GOV_ROLE={session_role!r} on {ticket}"
    if reported:
        support.assert_caught(result, relpath, what=what)
    else:
        support.assert_silent(result, what)
        assert _state(project, relpath).endswith("changed\n"), f"{what}: the in-scope change was reverted"


def test_the_check_adds_nothing_to_git_status(project, after_bash):
    command = "echo changed >> README.md && echo new > docs/new.md && echo changed >> src/gov/guard/decide.py"
    after_bash(project, command, ENGINEER, TICKET, changed=["README.md", "docs/new.md", SOURCE])
    allowed_lines = {" M README.md", "?? docs/new.md", f" M {SOURCE}"}
    lines = set(support.porcelain_all(project).splitlines())
    assert lines <= allowed_lines, (
        "the check left changes of its own in git status: " + ", ".join(sorted(lines - allowed_lines))
    )
    assert f" M {SOURCE}" in lines, "the in-scope change is gone from git status"
