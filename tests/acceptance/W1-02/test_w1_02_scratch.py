"""W1-02 — the kernel scratch set.

KPI success 1: "… allowed only inside the active ticket allowed_paths plus the
kernel scratch set, per role".

Owner answer to KD-2: the scratch set is ``.gov-runtime/scratch/**`` plus the
directory returned by Python's ``tempfile.gettempdir()``. It is open to every
known role, the auditor included, and closed to a session with no role or an
unknown role. While the freeze flag is set it is closed to everyone; that case
is in ``test_w1_02_freeze.py``.

The hook process gets ``TMPDIR`` pointing at a directory next to the project, so
``tempfile.gettempdir()`` returns that directory inside the hook.
"""

from __future__ import annotations

import pytest

import w1_02_support as support

ENGINEER = support.ENGINEER
TICKET = support.TICKET_ID
SCRATCH = support.SCRATCH_REL

FILE_TOOLS = ["Edit", "Write"]

# Inside the runtime directory, but not the scratch directory.
RUNTIME_NOT_SCRATCH = {
    "runtime-root": ".gov-runtime/note.txt",
    "freeze-flag": support.FREEZE_FLAG_REL,
    "findings-file": support.FINDINGS_REL,
    "store": ".gov-runtime/store.db",
    "directory-with-a-similar-name": ".gov-runtime/scratch_other/note.txt",
    "dot-dot-out-of-scratch": f"{SCRATCH}/../freeze",
    "dot-dot-into-the-repository": f"{SCRATCH}/../../README.md",
}


def _scratch_targets(project, sandbox):
    return {
        "repository-scratch": project / SCRATCH / "note.txt",
        "repository-scratch-nested": project / SCRATCH / "run-1" / "deep" / "note.txt",
        "system-temp": sandbox.tmpdir / "note.txt",
        "system-temp-nested": sandbox.tmpdir / "run-1" / "deep" / "note.txt",
    }


@pytest.mark.parametrize("role", support.KNOWN_ROLES)
@pytest.mark.parametrize("place", [
    "repository-scratch", "repository-scratch-nested", "system-temp", "system-temp-nested",
])
def test_every_known_role_can_write_to_the_scratch_set(project, write, sandbox, role, place):
    target = _scratch_targets(project, sandbox)[place]
    for tool_name in FILE_TOOLS:
        result = write(project, target, role, TICKET, tool_name)
        support.assert_allowed(result, f"{tool_name} on scratch path {target} by {role}")


def test_scratch_needs_no_ticket(project, write, sandbox):
    for target in _scratch_targets(project, sandbox).values():
        result = write(project, target, ENGINEER, None)
        support.assert_allowed(result, f"Write on scratch path {target} by the engineer with no ticket")


@pytest.mark.parametrize("command", [
    "echo note > " + SCRATCH + "/out.txt",
    "mkdir -p " + SCRATCH + "/run-1",
    "cd " + SCRATCH + " && echo note > out.txt",
    "echo note > {tmp}/out.txt",
    "cp README.md {tmp}/README.copy",
    "rm {tmp}/out.txt",
], ids=["redirect-repository-scratch", "mkdir-repository-scratch", "cd-then-redirect-repository-scratch",
        "redirect-system-temp", "cp-into-system-temp", "rm-in-system-temp"])
def test_bash_write_to_the_scratch_set_is_allowed(project, bash, sandbox, command):
    (project / SCRATCH).mkdir(parents=True)
    result = bash(project, command, ENGINEER, TICKET, tmp=sandbox.tmpdir)
    support.assert_allowed(result, f"Bash `{command}` by the engineer")


@pytest.mark.parametrize("tool_name", FILE_TOOLS)
@pytest.mark.parametrize("target", sorted(RUNTIME_NOT_SCRATCH), ids=sorted(RUNTIME_NOT_SCRATCH))
def test_the_rest_of_the_runtime_directory_is_not_scratch(project, write, tool_name, target):
    relpath = RUNTIME_NOT_SCRATCH[target]
    result = write(project, relpath, ENGINEER, TICKET, tool_name)
    support.assert_denied(result, f"{tool_name} on {relpath} by the engineer")


@pytest.mark.parametrize("where", ["next-to-the-temp-directory", "dot-dot-out-of-the-temp-directory", "home"])
def test_only_the_temp_directory_itself_is_scratch(project, write, sandbox, where):
    target = {
        "next-to-the-temp-directory": sandbox.elsewhere / "note.txt",
        "dot-dot-out-of-the-temp-directory": f"{sandbox.tmpdir}/../elsewhere/note.txt",
        "home": sandbox.home / "note.txt",
    }[where]
    for tool_name in FILE_TOOLS:
        result = write(project, target, ENGINEER, TICKET, tool_name)
        support.assert_denied(result, f"{tool_name} on {target} by the engineer")


@pytest.mark.parametrize("role", [None, *support.UNKNOWN_ROLES], ids=lambda r: r or "no-role")
def test_scratch_is_closed_without_a_known_role(project, write, bash, sandbox, role):
    for target in _scratch_targets(project, sandbox).values():
        result = write(project, target, role, TICKET)
        support.assert_denied(result, f"Write on scratch path {target} with GOV_ROLE={role!r}")
    for command in ("echo note > " + SCRATCH + "/out.txt", "echo note > {tmp}/out.txt"):
        result = bash(project, command, role, TICKET, tmp=sandbox.tmpdir)
        support.assert_denied(result, f"Bash `{command}` with GOV_ROLE={role!r}")
