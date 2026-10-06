"""KPI success 3 (DEC-407, DEC-409 rule 4): the containment check compares the freeze flag around every Bash call.

"The containment check compares the freeze flag around every Bash call; a flag
removed or emptied during the call is a finding and is restored with its marker
line."

Driven as the containment cases of this folder are: the PreToolUse hook, which
takes the before-snapshot; then a change at the flag's path in the temporary
project, made here in the place of the call's command; then the PostToolUse
hook. The project is W1-03's fixture project, with both hooks installed; it
ignores ``.gov-runtime/``, so ``git status`` says nothing about the flag.

The readings (``w1_50_freeze_README.md``, "Rule 4"):

- a flag is what the guard's own reader reads as frozen. **Removed or
  emptied** means: frozen before the call, and not frozen after it. Then the
  call gets a finding, and the flag is put back with the marker line it had,
  the way ``gov pause`` writes it (a temporary file and a rename, mode 0600);
- a flag that still freezes after the call is no finding, whatever its line
  says now: a second ``gov pause`` during the call writes a new line;
- a flag set during the call is no finding: setting stays open;
- what was no freeze before the call (nothing, or the sandbox's placeholder)
  is not this rule's business;
- this holds for every role, the orchestrator and a session without a role
  included, and for a call that failed (``PostToolUseFailure``).
"""

from __future__ import annotations

import os
import stat

import pytest

import w1_50_freeze_support as support
import w1_50_support as trailers_support

check = trailers_support.check_support        # W1-03's support: one Bash call between its two hooks

FLAG_REL = support.FLAG_REL
ENGINEER, ORCHESTRATOR, DESIGNER = check.ENGINEER, check.ORCHESTRATOR, check.TEST_DESIGNER
TICKET, ORCHESTRATOR_TICKET = check.TICKET_ID, check.ORCHESTRATOR_TICKET_ID
REMEMBERED = "FROZEN orchestrator 2026-10-04T08:15:30Z"      # the line the flag has before the call
COMMAND = "python3 -m pytest tests/unit -q"                  # what the hooks are told; it names no write


def _flag(project):
    return support.flag(project)


def _call(project, sandbox, during, role=ENGINEER, ticket=TICKET, subagent=None, failed=False):
    """One Bash call: the guard lets it through and takes the snapshot, ``during(project)`` stands for what the
    command did, the check runs. Returns the check's result."""
    the_call = check.literal_call(COMMAND)
    seen = len(check.finding_lines(project))
    guard = check.run_guard(project, the_call, sandbox, role=role, ticket=ticket, subagent=subagent)
    check.assert_let_through(guard, the_call)
    during(project)
    return check.run_check(project, the_call, sandbox, role=role, ticket=ticket, subagent=subagent, failed=failed,
                           seen=seen)


def _flag_findings(result, what):
    return [finding for finding in check.new_findings(result, what)
            if any(entry == FLAG_REL for entry in check.finding_paths(result, finding))]


def _assert_found_and_restored(project, sandbox, result, role, ticket, what):
    assert result.returncode == 0, f"{what}: the check failed instead of reporting: {result.describe()}"
    findings = _flag_findings(result, what)
    assert findings, (
        f"{what}: no finding names {FLAG_REL}; findings of this call: {[f['paths'] for f in check.new_findings(result, what)]}"
    )
    for finding in findings:   # the call is named as in every finding (DEC-122): new_findings checked command and session
        assert finding["role"] == (role or "") and finding["ticket"] == (ticket or ""), \
            f"{what}: the finding names {finding['role']!r} on {finding['ticket']!r}, not the caller"
    path = _flag(project)
    assert path.is_file() and not path.is_symlink(), f"{what}: {FLAG_REL} was not put back as a regular file"
    assert support.first_line(path) == REMEMBERED, \
        f"{what}: the flag's first line is {support.first_line(path)!r}, not the marker line it had: {REMEMBERED!r}"
    assert stat.S_IMODE(os.lstat(path).st_mode) == 0o600, \
        f"{what}: the flag was put back with mode {stat.S_IMODE(os.lstat(path).st_mode):o}, not 600"
    left = [name for name in os.listdir(path.parent) if name != path.name and ("freeze" in name or name.startswith("tmp"))]
    assert not left, f"{what}: a temporary file was left beside the flag: {left}"
    frozen = check.run_guard_for_file_tool(project, sandbox, "Write",
                                           {"file_path": str(project / check.SOURCE_FILE), "content": "x\n"},
                                           role=ENGINEER, ticket=TICKET)
    assert frozen.decision == "deny" and "frozen" in frozen.stdout.lower(), \
        f"{what}: after the flag was put back the guard does not read a freeze: {frozen.describe()}"


def _assert_no_flag_finding(result, what):
    assert result.returncode == 0, f"{what}: the check failed: {result.describe()}"
    assert not _flag_findings(result, what), f"{what}: a finding names {FLAG_REL}: {result.new_lines}"


@pytest.fixture()
def frozen(project):
    """The project with a flag as ``gov pause`` leaves it, set by the orchestrator some time ago."""
    support.put_flag(project, REMEMBERED + "\n")
    return project


# --------------------------------------------------------------------------
# Removed or emptied during the call
# --------------------------------------------------------------------------

# who: (GOV_ROLE, GOV_TICKET, subagent type)
ACTORS = {
    "engineer": (ENGINEER, TICKET, None),
    "independent-test-designer": (DESIGNER, TICKET, None),
    "orchestrator": (ORCHESTRATOR, ORCHESTRATOR_TICKET, None),
    "no-role": (None, None, None),
    "engineer-subagent-of-the-orchestrator": (ORCHESTRATOR, ORCHESTRATOR_TICKET, ENGINEER),
}


@pytest.mark.parametrize("who", sorted(ACTORS))
def test_a_flag_removed_during_a_call_is_a_finding_and_is_put_back(frozen, sandbox, who):
    """No agent session lifts a freeze (DEC-409), so a flag that is gone after any role's call was taken away."""
    role, ticket, subagent = ACTORS[who]

    result = _call(frozen, sandbox, lambda project: _flag(project).unlink(), role=role, ticket=ticket,
                   subagent=subagent)

    _assert_found_and_restored(frozen, sandbox, result, role, ticket, f"a flag removed during the call of {who}")


def _truncate(project):
    _flag(project).write_text("", encoding="utf-8")


def _overwrite(project):
    _flag(project).write_text("lifted by the engineer\n", encoding="utf-8")


def _link_to_an_unmarked_file(project):
    _flag(project).unlink()
    _flag(project).symlink_to(project / "README.md")


def _link_to_dev_null(project):
    _flag(project).unlink()
    _flag(project).symlink_to(os.devnull)


EMPTIED = {
    "truncated": _truncate,
    "overwritten-by-text-without-the-marker": _overwrite,
    "replaced-by-a-link-to-an-unmarked-file": _link_to_an_unmarked_file,
    "replaced-by-a-link-to-dev-null": _link_to_dev_null,
}


@pytest.mark.parametrize("how", sorted(EMPTIED))
def test_a_flag_emptied_during_a_call_is_a_finding_and_is_put_back(frozen, sandbox, how):
    """Emptied: something is still at the path and the guard's reader no longer reads a freeze there."""
    readme = (frozen / "README.md").read_bytes()

    result = _call(frozen, sandbox, EMPTIED[how])

    _assert_found_and_restored(frozen, sandbox, result, ENGINEER, TICKET, f"a flag {how} during the call")
    assert (frozen / "README.md").read_bytes() == readme, \
        "the flag was put back through the link that stood at its path: the link's target changed"


def test_a_flag_removed_during_a_call_that_failed_is_a_finding_and_is_put_back(frozen, sandbox):
    """``PostToolUseFailure`` is checked as ``PostToolUse`` is (W1-03)."""
    result = _call(frozen, sandbox, lambda project: _flag(project).unlink(), failed=True)

    _assert_found_and_restored(frozen, sandbox, result, ENGINEER, TICKET, "a flag removed during a call that failed")


# --------------------------------------------------------------------------
# What this rule leaves alone
# --------------------------------------------------------------------------

def test_a_flag_that_still_freezes_after_the_call_is_no_finding(frozen, sandbox):
    """A second ``gov pause`` during the call (the owner's, or the orchestrator's own) writes a new marker line.
    The freeze holds, so nothing was removed or emptied, and the new line stays."""
    later = "FROZEN owner 2026-10-06T09:00:00Z\n"

    result = _call(frozen, sandbox, lambda project: support.put_flag(project, later), role=ORCHESTRATOR,
                   ticket=ORCHESTRATOR_TICKET)

    _assert_no_flag_finding(result, "a flag paused again during the call")
    assert _flag(frozen).read_text(encoding="utf-8") == later, "the check rewrote a flag that still froze"


def test_a_flag_set_during_a_call_is_no_finding_and_stays(project, sandbox):
    """Setting a freeze stays open to the orchestrator (KPI success 7): its own ``gov pause`` in the call."""
    line = "FROZEN orchestrator 2026-10-06T09:00:00Z\n"

    result = _call(project, sandbox, lambda p: support.put_flag(p, line), role=ORCHESTRATOR,
                   ticket=ORCHESTRATOR_TICKET)

    _assert_no_flag_finding(result, "a flag set during the call")
    assert _flag(project).read_text(encoding="utf-8") == line, "the check changed a flag that was set during the call"


def test_no_flag_before_and_none_after_is_nothing(project, sandbox):
    result = _call(project, sandbox, lambda p: None)

    check.assert_silent(result, "a call with no flag before and none after")
    assert not os.path.lexists(_flag(project)), "the check put a flag where none was"


def test_a_placeholder_that_goes_during_the_call_is_no_finding(project, sandbox):
    """The sandbox's empty placeholder is no freeze (DEC-402): it comes and goes with a launched session's command."""
    support.put_placeholder(project)

    result = _call(project, sandbox, lambda p: _flag(p).unlink())

    _assert_no_flag_finding(result, "a placeholder that went during the call")
    assert not os.path.lexists(_flag(project)), "the check put a flag, or the placeholder, back where no freeze was"
