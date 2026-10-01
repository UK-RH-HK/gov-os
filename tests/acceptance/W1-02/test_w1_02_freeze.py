"""W1-02 — the freeze flag denies every write.

KPI success 3, first clause: "The freeze flag (gov pause) denies every write".
CAP-05 acceptance: "After gov pause, the next Edit/Write/Bash write by any role
is denied by the guard, and git status --porcelain is unchanged; gov pause --off
restores writes."

Owner answer to KD-3: until ``gov pause`` (W1-28) exists, the flag is the file
``.gov-runtime/freeze``. It exists: frozen. Its content is not read. While it
exists every write is denied for every role, the test designer and the scratch
set included; reads stay open; removing the file restores writes.
"""

from __future__ import annotations

import pytest

import w1_02_support as support

ENGINEER = support.ENGINEER
TICKET = support.TICKET_ID
WBS = support.TICKET_WBS_ID
SCRATCH = support.SCRATCH_REL

# A write each role may make when nothing is frozen: (ticket, repository-relative path).
NORMAL_WRITE = {
    support.ENGINEER: (support.TICKET_ID, "src/gov/guard/decide.py"),
    support.ORCHESTRATOR: (support.ORCHESTRATOR_TICKET_ID, ".claude/settings.json"),
    support.PRODUCT_SPEC: (support.PRODUCT_SPEC_TICKET_ID, "docs/spec/feature.md"),
    support.TEST_DESIGNER: (support.TICKET_ID, f"tests/acceptance/{WBS}/test_fixture.py"),
    support.AUDITOR: (support.TICKET_ID, f"{SCRATCH}/audit-note.txt"),
}

FLAG_CONTENTS = {
    "empty": "",
    "says-false": "false\n",
    "says-off": "off\n",
    "says-zero": "0\n",
    "json-false": '{"freeze": false}\n',
}

BASH_WRITES = {
    "redirect-inside-the-ticket-paths": "echo changed > src/gov/guard/decide.py",
    "touch-inside-the-ticket-paths": "touch src/gov/guard/new_module.py",
    "rm-inside-the-ticket-paths": "rm src/gov/guard/decide.py",
    "redirect-to-repository-scratch": "echo note > " + SCRATCH + "/out.txt",
    "redirect-to-system-temp": "echo note > {tmp}/out.txt",
    "remove-the-flag": "rm " + support.FREEZE_FLAG_REL,
}


@pytest.mark.parametrize("role", support.KNOWN_ROLES)
def test_freeze_denies_the_write_each_role_could_otherwise_make(project, write, role):
    ticket, relpath = NORMAL_WRITE[role]
    support.assert_allowed(write(project, relpath, role, ticket), f"before the freeze, Write on {relpath} by {role}")

    flag = support.set_freeze(project)
    for tool_name in ("Edit", "Write"):
        result = write(project, relpath, role, ticket, tool_name)
        support.assert_denied(result, f"while frozen, {tool_name} on {relpath} by {role}")

    flag.unlink()
    support.assert_allowed(
        write(project, relpath, role, ticket), f"after the flag was removed, Write on {relpath} by {role}"
    )


@pytest.mark.parametrize("content", sorted(FLAG_CONTENTS), ids=sorted(FLAG_CONTENTS))
def test_the_flag_freezes_by_existing_whatever_it_contains(project, write, content):
    support.set_freeze(project, FLAG_CONTENTS[content])
    result = write(project, "src/gov/guard/decide.py", ENGINEER, TICKET)
    support.assert_denied(result, f"while a flag file holding {FLAG_CONTENTS[content]!r} exists, the engineer's write")


def test_freeze_closes_the_scratch_set(project, write, sandbox):
    support.set_freeze(project)
    for target in (project / SCRATCH / "note.txt", sandbox.tmpdir / "note.txt"):
        for tool_name in ("Edit", "Write"):
            result = write(project, target, ENGINEER, TICKET, tool_name)
            support.assert_denied(result, f"while frozen, {tool_name} on scratch path {target}")


def test_freeze_denies_notebook_edits(project, write):
    support.set_freeze(project)
    result = write(project, "src/gov/guard/analysis.ipynb", ENGINEER, TICKET, "NotebookEdit")
    support.assert_denied(result, "while frozen, NotebookEdit inside the ticket paths")


@pytest.mark.parametrize("form", sorted(BASH_WRITES), ids=sorted(BASH_WRITES))
def test_freeze_denies_bash_writes(project, bash, sandbox, form):
    support.set_freeze(project)
    result = bash(project, BASH_WRITES[form], ENGINEER, TICKET, tmp=sandbox.tmpdir)
    support.assert_denied(result, f"while frozen, Bash `{BASH_WRITES[form]}` by the engineer")


def test_no_agent_role_can_lift_the_freeze(project, write, bash):
    """The flag is outside every allow-list and outside the scratch set, frozen or not."""
    for frozen in (False, True):
        if frozen:
            support.set_freeze(project)
        state = "while frozen" if frozen else "before the freeze"
        for role in support.KNOWN_ROLES:
            ticket = NORMAL_WRITE[role][0]
            for tool_name in ("Edit", "Write"):
                result = write(project, support.FREEZE_FLAG_REL, role, ticket, tool_name)
                support.assert_denied(result, f"{state}, {tool_name} on the freeze flag by {role}")
            command = "rm " + support.FREEZE_FLAG_REL
            support.assert_denied(bash(project, command, role, ticket), f"{state}, Bash `{command}` by {role}")


def test_reads_stay_open_while_frozen(project, call, bash):
    support.set_freeze(project)
    read = call(project, "Read", {"file_path": str(project / "src/gov/guard/decide.py")},
                role=ENGINEER, ticket=TICKET)
    support.assert_allowed(read, "while frozen, Read by the engineer")
    for command in ("git status --porcelain", "cat README.md", "ls -la"):
        support.assert_allowed(bash(project, command, ENGINEER, TICKET), f"while frozen, Bash `{command}`")


def test_freeze_leaves_git_status_unchanged(project, write, bash):
    support.set_freeze(project)
    before = support.porcelain(project)
    for role in support.KNOWN_ROLES:
        ticket, relpath = NORMAL_WRITE[role]
        write(project, relpath, role, ticket)
        bash(project, f"echo changed > {relpath}", role, ticket)
    assert support.porcelain(project) == before, (
        "git status --porcelain changed while frozen:\n" + support.porcelain(project)
    )
