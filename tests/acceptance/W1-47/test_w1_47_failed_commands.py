"""W1-47 -- the containment check runs after a failed command too.

KPI success 2: "The containment check is registered on PostToolUseFailure as
well as PostToolUse, in this repository's settings and in the kernel template; a
command that writes a file and then fails is caught [CAP-58.f]".

A Bash call that fails, times out or is interrupted ends in
``PostToolUseFailure``, not ``PostToolUse``. It may have written files first.

- The registration is read from the two settings files.
- "Is caught" is shown three ways: by the hook in a fixture project, by the
  commands this repository's settings register, run in a wired copy, and for an
  acceptance test, which the check restores from HEAD.
"""

from __future__ import annotations

import pytest

import w1_47_support as support

check_support = support.check_support
live_support = support.live_support

ENGINEER = support.ENGINEER
TICKET = check_support.TICKET_ID
ACCEPTANCE_FILE = check_support.ACCEPTANCE_FILE
EVENTS = ("PostToolUse", "PostToolUseFailure")


# --------------------------------------------------------------------------
# The registration
# --------------------------------------------------------------------------

@pytest.mark.parametrize("event", EVENTS)
def test_this_repository_registers_the_containment_check_after_bash(settings, event):
    """KPI success 2 [CAP-58.f]: ``.claude/settings.json`` of this repository."""
    assert support.containment_commands(settings, event), (
        f"{support.SETTINGS_REL} registers no {event} command for Bash that runs the containment hook"
    )


def test_this_repository_runs_the_same_check_after_a_failed_call(settings):
    """KPI success 2: "as well as": every containment command of PostToolUse is on PostToolUseFailure too."""
    after = support.containment_commands(settings, "PostToolUse")
    failed = support.containment_commands(settings, "PostToolUseFailure")
    assert after and set(after) <= set(failed), (
        f"{support.SETTINGS_REL}: the containment commands of PostToolUse are {after}; "
        f"PostToolUseFailure registers {failed}"
    )


@pytest.mark.parametrize("event", EVENTS)
def test_the_kernel_template_registers_the_containment_check_after_bash(template_settings, event):
    """KPI success 2 [CAP-58.f]: the settings file of the kernel template."""
    assert support.containment_commands(template_settings, event), (
        f"the kernel template's settings file registers no {event} command for Bash that runs the containment hook"
    )


def test_the_kernel_template_runs_the_same_check_after_a_failed_call(template_settings):
    """KPI success 2: "as well as", in the kernel template."""
    after = support.containment_commands(template_settings, "PostToolUse")
    failed = support.containment_commands(template_settings, "PostToolUseFailure")
    assert after and set(after) <= set(failed), (
        f"the kernel template's settings file: the containment commands of PostToolUse are {after}; "
        f"PostToolUseFailure registers {failed}"
    )


# --------------------------------------------------------------------------
# A command that writes a file and then fails is caught
# --------------------------------------------------------------------------

def _failed_call(project, sandbox, command, changed):
    """One whole Bash call that fails: PreToolUse hook, the real command, the hook on PostToolUseFailure."""
    seen = len(check_support.finding_lines(project))
    call = check_support.script_call(sandbox, command)
    before = check_support.run_guard(project, call, sandbox, role=ENGINEER, ticket=TICKET)
    check_support.assert_let_through(before, call)
    bash = check_support.run_bash(project, call.command, sandbox)
    assert bash.returncode != 0, f"the fixture command `{command}` did not fail: exit {bash.returncode}"
    check_support.assert_changed(project, *changed, command=command)
    return check_support.run_check(project, call, sandbox, role=ENGINEER, ticket=TICKET, bash=bash, failed=True,
                                   seen=seen)


FAILING = {
    "exit-code": "echo changed >> README.md; exit 3",
    "missing-command": "echo changed >> README.md; command-that-does-not-exist-w1-47",
    "killed-by-its-own-signal": "echo changed >> README.md; kill -TERM $$",
}


@pytest.mark.parametrize("case", sorted(FAILING))
def test_a_change_left_by_a_failed_command_is_caught(project, sandbox, case):
    """KPI success 2 [CAP-58.f]: reported to the agent and recorded as a finding."""
    command = FAILING[case]
    result = _failed_call(project, sandbox, command, changed=["README.md"])
    check_support.assert_caught(result, "README.md", what=f"`{command}` by the engineer on {TICKET}, which failed,")


def test_a_new_file_left_by_a_failed_command_is_caught(project, sandbox):
    """KPI success 2: "writes a file": a file that did not exist before the call."""
    command = "echo new > docs/left-behind.md; exit 1"
    result = _failed_call(project, sandbox, command, changed=["docs/left-behind.md"])
    check_support.assert_caught(result, "docs/left-behind.md",
                                what=f"`{command}` by the engineer on {TICKET}, which failed,")


def test_an_acceptance_test_changed_by_a_failed_command_is_restored(project, sandbox):
    """KPI success 2: the check does after a failed call what it does after any other (W1-03)."""
    before = check_support.read(project, ACCEPTANCE_FILE)
    command = f"echo changed >> {ACCEPTANCE_FILE}; exit 1"
    result = _failed_call(project, sandbox, command, changed=[ACCEPTANCE_FILE])
    what = f"`{command}` by the engineer on {TICKET}, which failed,"
    check_support.assert_caught(result, ACCEPTANCE_FILE, what=what, action=check_support.REVERTED)
    assert check_support.read(project, ACCEPTANCE_FILE) == before, f"{what}: {ACCEPTANCE_FILE} was not restored"


def test_a_failed_command_that_stays_in_scope_is_left_alone(project, sandbox):
    """The check after a failed call finds what is out of scope, and nothing else."""
    source = check_support.SOURCE_FILE
    command = f"echo changed >> {source}; exit 1"
    result = _failed_call(project, sandbox, command, changed=[source])
    check_support.assert_silent(result, f"`{command}` by the engineer on {TICKET}, which failed,")


def test_a_failed_command_is_caught_through_the_committed_settings(wired, settings, live_sandbox):
    """KPI success 2: through the commands this repository's settings register for PostToolUseFailure."""
    command = "echo changed >> README.md; exit 3"
    report, results = live_support.bash_call(wired, settings, live_sandbox, command, ENGINEER,
                                             live_support.FIXTURE_TICKET_ID, event="PostToolUseFailure",
                                             changed=["README.md"])
    assert results, f"{support.SETTINGS_REL} registers no PostToolUseFailure command for Bash"
    assert "README.md" in report, (
        "the change left by a failed call was not reported to the agent: "
        + "; ".join(result.describe() for result in results)
    )
