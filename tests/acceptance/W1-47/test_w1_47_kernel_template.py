"""W1-47 -- the kernel template's settings file (DEC-217).

KPI success 2: "The containment check is registered on PostToolUseFailure as
well as PostToolUse, in this repository's settings and in the kernel template
[...] [CAP-58.f]".
DEC-217: "The kernel template carries template/governance/kernel/settings.json,
with PreToolUse for every tool and both post-command events, commands through
$CLAUDE_PROJECT_DIR, and a behavioural test."

- The static tests read the file.
- The behavioural tests run the file's commands through the shell, as the
  harness runs them, in a project that has the kernel installed: the fixture
  project of W1-03, with both hooks at ``governance/kernel/hooks/`` (where
  Copier puts them) and the ``gov`` package importable. Nothing is installed by
  a test, so the package is put on Python's path. The project's own ``src/gov``
  is a stub, and its ``template/`` holds no working hook: a command written for
  this repository's layout fails there.

The registration of the two post-command events for Bash is in
``test_w1_47_failed_commands.py``; the template's lack of install rules in
``test_w1_47_settings_rules.py``.
"""

from __future__ import annotations

import re

import pytest

import w1_47_support as support

check_support = support.check_support
live_support = support.live_support

ENGINEER = support.ENGINEER
ORCHESTRATOR = support.ORCHESTRATOR
TICKET = check_support.TICKET_ID
SOURCE_FILE = check_support.SOURCE_FILE
ACCEPTANCE_FILE = check_support.ACCEPTANCE_FILE
EVERY_TOOL = (*live_support.EVERY_TOOL, "ToolAddedAfterThisTicket")
POST_EVENTS = ("PostToolUse", "PostToolUseFailure")


# --------------------------------------------------------------------------
# The file
# --------------------------------------------------------------------------

@pytest.mark.parametrize("tool_name", EVERY_TOOL)
def test_the_template_registers_the_guard_before_every_tool(template_settings, tool_name):
    """DEC-217: "PreToolUse for every tool": the write tools, the read-only tools and any other."""
    commands = [command for command in live_support.hook_commands(template_settings, "PreToolUse", tool_name)
                if support.GUARD_HOOK_STEM in command]
    assert commands, f"{support.TEMPLATE_SETTINGS_REL} registers no PreToolUse command for {tool_name} that runs the guard"


def test_the_template_s_commands_are_written_through_the_project_directory(template_settings):
    """DEC-217: "commands through $CLAUDE_PROJECT_DIR": every hook path starts at that variable."""
    commands = support.every_hook_command(template_settings)
    assert commands, f"{support.TEMPLATE_SETTINGS_REL} registers no hook command"
    variable = re.compile(r"\$(?:%s\b|\{%s\})" % (support.PROJECT_DIR_VARIABLE, support.PROJECT_DIR_VARIABLE))
    for command in commands:
        assert variable.search(command), (
            f"{support.TEMPLATE_SETTINGS_REL}: `{command}` does not find its hook through "
            f"${support.PROJECT_DIR_VARIABLE}"
        )
        assert str(support.REPO_ROOT) not in command, (
            f"{support.TEMPLATE_SETTINGS_REL}: `{command}` names this repository's own directory"
        )


# --------------------------------------------------------------------------
# The guard, through the template's commands
# --------------------------------------------------------------------------

def _decide(installed, project, tool_name, tool_input, role, ticket, **options):
    results = installed(project, "PreToolUse", tool_name, tool_input, role, ticket, **options)
    return support.combined_decision(results), support.describe_all(results)


def test_the_template_s_guard_denies_a_write_outside_the_ticket_paths(project, installed):
    """DEC-217: the guard's behaviour (W1-02): an engineer's write outside ``allowed_paths`` is denied."""
    decision, detail = _decide(installed, project, "Write", support.write_input("Write", f"{project}/README.md"),
                               ENGINEER, TICKET)
    assert decision == "deny", (
        f"Write to README.md by the engineer was not denied by the commands of {support.TEMPLATE_SETTINGS_REL}: "
        f"decision={decision} ({detail})"
    )


def test_the_template_s_guard_denies_a_bash_write_to_an_acceptance_test(project, installed):
    """DEC-217: the guard's behaviour for Bash: a redirect into ``tests/acceptance/`` by the engineer."""
    command = f"echo changed > {ACCEPTANCE_FILE}"
    decision, detail = _decide(installed, project, "Bash", support.bash_input(command), ENGINEER, TICKET)
    assert decision == "deny", (
        f"Bash `{command}` by the engineer was not denied by the commands of {support.TEMPLATE_SETTINGS_REL}: "
        f"decision={decision} ({detail})"
    )


@pytest.mark.parametrize("call", ("Write-inside-the-ticket-paths", "Read", "Grep", "Bash-listing"))
def test_the_template_s_guard_lets_a_call_in_scope_through(project, installed, call):
    """DEC-217: the commands work where the kernel is installed: they run, exit cleanly and allow."""
    tool_name, tool_input = {
        "Write-inside-the-ticket-paths": ("Write", support.write_input("Write", f"{project}/{SOURCE_FILE}")),
        "Read": ("Read", {"file_path": f"{project}/README.md"}),
        "Grep": ("Grep", {"pattern": "guard", "path": f"{project}/src"}),
        "Bash-listing": ("Bash", support.bash_input("ls -la")),
    }[call]
    decision, detail = _decide(installed, project, tool_name, tool_input, ENGINEER, TICKET)
    assert decision == "allow", (
        f"{call} by the engineer was not let through by the commands of {support.TEMPLATE_SETTINGS_REL}: "
        f"decision={decision} ({detail})"
    )


def test_the_template_s_guard_asks_before_an_install(project, installed):
    """DEC-217: the guard's install rule (W1-04) is reached through the template too."""
    decision, detail = _decide(installed, project, "Bash", support.bash_input("pip install requests"),
                               ORCHESTRATOR, support.TICKET_OF[ORCHESTRATOR])
    assert decision == "ask", (
        f"`pip install requests` by the orchestrator did not ask through the commands of "
        f"{support.TEMPLATE_SETTINGS_REL}: decision={decision} ({detail})"
    )


def test_the_template_s_guard_denies_the_escape_hatch(project, installed):
    """KPI success 1 [CAP-62.a], in a project that has the kernel installed."""
    tool_input = support.bash_input("ls -la", dangerouslyDisableSandbox=True)
    decision, detail = _decide(installed, project, "Bash", tool_input, ORCHESTRATOR, support.TICKET_OF[ORCHESTRATOR])
    assert decision == "deny", (
        f"Bash `ls -la` with dangerouslyDisableSandbox: true was not denied by the commands of "
        f"{support.TEMPLATE_SETTINGS_REL}: decision={decision} ({detail})"
    )


def test_the_template_s_guard_hides_a_held_out_path(project, installed, live_sandbox):
    """KPI success 4 [CAP-49.c], in a project that has the kernel installed, against a stand-in."""
    stand_in = support.make_stand_in(live_sandbox.tmpdir / "held-out-stand-in")
    support.configure_stand_in(project, stand_in)
    decision, detail = _decide(installed, project, "Read", {"file_path": f"{stand_in}/answers.md"}, ORCHESTRATOR,
                               support.TICKET_OF[ORCHESTRATOR])
    assert decision == "deny", (
        f"Read on the stand-in held-out path was not denied by the commands of {support.TEMPLATE_SETTINGS_REL}: "
        f"decision={decision} ({detail})"
    )


# --------------------------------------------------------------------------
# The containment check, through the template's commands
# --------------------------------------------------------------------------

_CALLS = iter(range(1, 1_000_000))


def _bash_call(installed, project, sandbox, command, event, changed):
    """One whole Bash call: the template's PreToolUse commands, the command for real, then ``event``."""
    number = next(_CALLS)
    directory = sandbox.home.parent / "calls"
    directory.mkdir(exist_ok=True)
    script = directory / f"call-{number:04d}.sh"
    script.write_text(command + "\n", encoding="utf-8")
    call = support.bash_input(f"bash {script}")
    tool_use_id = f"toolu_w1_47_template_{number:04d}"
    before = installed(project, "PreToolUse", "Bash", call, ENGINEER, TICKET, tool_use_id=tool_use_id)
    assert support.combined_decision(before) == "allow", (
        f"the PreToolUse commands of {support.TEMPLATE_SETTINGS_REL} did not let the fixture call through, so no "
        f"Bash call would follow: {support.describe_all(before)}"
    )
    live_support.run_bash(project, call["command"], sandbox)
    status = check_support.porcelain_all(project)
    for relpath in changed:
        assert relpath in status, f"the fixture command `{command}` did not change {relpath}:\n{status}"
    after = installed(project, event, "Bash", call, ENGINEER, TICKET, tool_use_id=tool_use_id)
    return support.report_text(after), after


@pytest.mark.parametrize("event", POST_EVENTS)
def test_the_template_s_containment_check_catches_a_change_out_of_scope(project, installed, live_sandbox, event):
    """KPI success 2 [CAP-58.f], DEC-217: after a call that succeeds and after one that fails."""
    command = "echo changed >> README.md" + ("; exit 3" if event == "PostToolUseFailure" else "")
    report, results = _bash_call(installed, project, live_sandbox, command, event, changed=["README.md"])
    assert results, f"{support.TEMPLATE_SETTINGS_REL} registers no {event} command for Bash"
    assert "README.md" in report, (
        f"the change left by `{command}` was not reported to the agent by the {event} commands of "
        f"{support.TEMPLATE_SETTINGS_REL}: {support.describe_all(results)}"
    )


def test_the_template_s_containment_check_restores_an_acceptance_test_after_a_failed_command(project, installed,
                                                                                            live_sandbox):
    """KPI success 2: "a command that writes a file and then fails is caught", in the template's wiring."""
    before = check_support.read(project, ACCEPTANCE_FILE)
    command = f"echo changed >> {ACCEPTANCE_FILE}; exit 1"
    report, results = _bash_call(installed, project, live_sandbox, command, "PostToolUseFailure",
                                 changed=[ACCEPTANCE_FILE])
    assert ACCEPTANCE_FILE in report, (
        f"the change left by `{command}` was not reported to the agent: {support.describe_all(results)}"
    )
    assert check_support.read(project, ACCEPTANCE_FILE) == before, (
        f"{ACCEPTANCE_FILE} was not restored by the PostToolUseFailure commands of {support.TEMPLATE_SETTINGS_REL}"
    )


@pytest.mark.parametrize("event", POST_EVENTS)
def test_the_template_s_containment_check_leaves_a_change_in_scope_alone(project, installed, live_sandbox, event):
    """The check reports what is out of scope, and nothing else."""
    command = f"echo changed >> {SOURCE_FILE}" + ("; exit 3" if event == "PostToolUseFailure" else "")
    report, results = _bash_call(installed, project, live_sandbox, command, event, changed=[SOURCE_FILE])
    assert results, f"{support.TEMPLATE_SETTINGS_REL} registers no {event} command for Bash"
    assert all(result.returncode == 0 for result in results) and not report, (
        f"`{command}` by the engineer, in scope, was reported or failed: {support.describe_all(results)}"
    )
