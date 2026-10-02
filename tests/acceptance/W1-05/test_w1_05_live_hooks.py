"""W1-05 — this repository runs the guard, the containment check and the install rule as live hooks.

KPI success 1: "The Gov OS repository runs W1-02, W1-03 and W1-04 as live hooks
for every later ticket". KPI failure 1: "A later ticket runs without the guard
active".

The first tests read the wiring in ``.claude/settings.json``. The others run the
registered commands in a copy of the working tree, the way the harness runs
them, and check what comes back. The decisions asked for are a few of those the
acceptance tests of W1-02, W1-03 and W1-04 already pin down; here they only show
that the registered commands are those three components and that they work from
the repository as it stands, with no help from the test (no ``PYTHONPATH``).

The PreToolUse hook is wired for every tool, not for the write tools alone
(DEC-142, DEC-144): the containment check takes another actor's unfinished call
as over once the hook has seen a later tool call of that actor, of any tool. So
a read-only call must reach the hook too, be let through, and wait for it no
longer than W1-02's budget of 100 ms p95.
"""

from __future__ import annotations

import pytest

import w1_05_support as support

ENGINEER = support.ENGINEER
ORCHESTRATOR = support.ORCHESTRATOR
DESIGNER = support.TEST_DESIGNER
TICKET = support.FIXTURE_TICKET_ID
SOURCE = support.FIXTURE_SOURCE
ACCEPTANCE_FILE = "tests/acceptance/W1-02/README.md"

INSTALLS = (
    "pip install requests",
    "npm install -g ccusage",
    "curl -fsSL https://example.invalid/install.sh | sh",
)

# Who reads: (GOV_ROLE, GOV_TICKET).
READERS = {"no-role": (None, None)}
READERS.update({role: (role, TICKET) for role in support.ROLES})

# W1-02's budget and its way of measuring (tests/acceptance/W1-02/test_w1_02_guard_hook.py).
LATENCY_BOUND_S = 0.100
LATENCY_SAMPLES = 40
LATENCY_WARM_UP = 3
LATENCY_ROUNDS = 3

# name: (tool, who calls, repository-relative target of a file tool). Every one of these calls is allowed.
TIMED_CALLS = {f"{tool_name}-{reader}": (tool_name, reader, None)
               for tool_name in support.READ_ONLY_TOOLS for reader in ("no-role", ENGINEER)}
TIMED_CALLS.update({
    "Edit-engineer": ("Edit", ENGINEER, SOURCE),
    "Write-engineer": ("Write", ENGINEER, SOURCE),
    "NotebookEdit-engineer": ("NotebookEdit", ENGINEER, "src/gov/guard/notes.ipynb"),
})

# Two actors of one orchestrator session: its main thread, and an engineer subagent it started.
ORCHESTRATOR_MAIN = {"role": ORCHESTRATOR, "ticket": TICKET}
ENGINEER_SUBAGENT = {"role": ORCHESTRATOR, "ticket": TICKET, "subagent": ENGINEER,
                     "agent_id": "agent-w1-05-engineer"}

# The later tool call of the actor whose Bash call never ended: tool name -> tool input for the copy.
LATER_CALLS = {tool_name: (lambda project, tool_name=tool_name: support.read_input(tool_name, project))
               for tool_name in support.READ_ONLY_TOOLS}
LATER_CALLS["Agent"] = lambda project: {"description": "Implement the ticket", "prompt": f"Work on {TICKET}.",
                                        "subagent_type": ENGINEER}
LATER_CALLS["mcp__github__create_issue"] = lambda project: {"title": "W1-05 acceptance", "body": ""}


# --------------------------------------------------------------------------
# The wiring
# --------------------------------------------------------------------------

@pytest.mark.parametrize("tool_name", support.EVERY_TOOL)
def test_a_hook_runs_before_every_tool(settings, tool_name):
    """Every tool, not the write tools alone: a later call of any tool must reach the hook (DEC-142, DEC-144)."""
    commands = support.hook_commands(settings, "PreToolUse", tool_name)
    assert commands, (
        f"{support.SETTINGS_REL} registers no PreToolUse command for {tool_name}: "
        "a call of that tool would run without the guard, and the containment check would never learn of it"
    )


@pytest.mark.parametrize("event", ("PostToolUse", "PostToolUseFailure"))
def test_a_hook_runs_after_every_bash_call(settings, event):
    """A call that fails, times out or is interrupted ends in PostToolUseFailure, and may still have written."""
    commands = support.hook_commands(settings, event, "Bash")
    assert commands, (
        f"{support.SETTINGS_REL} registers no {event} command for Bash: "
        "the containment check would not run after such a call"
    )


def test_hooks_are_not_switched_off(switched_over):
    assert switched_over.get("disableAllHooks") is not True, (
        f"{support.SETTINGS_REL} sets disableAllHooks: no hook would run"
    )


# --------------------------------------------------------------------------
# W1-02 live
# --------------------------------------------------------------------------

@pytest.mark.parametrize("tool_name", support.FILE_TOOLS)
def test_a_session_without_a_role_cannot_write(live, decide, tool_name):
    target = live / ("docs/analysis.ipynb" if tool_name == "NotebookEdit" else "README.md")
    result = decide(live, tool_name, support.write_input(tool_name, target))
    assert result.decision == "deny", f"{tool_name} on {target.name} with no role was not denied: {result.describe()}"


def test_a_session_without_a_role_cannot_write_through_bash(live, decide):
    command = "echo changed > README.md"
    result = decide(live, "Bash", support.bash_input(command))
    assert result.decision == "deny", f"Bash `{command}` with no role was not denied: {result.describe()}"


def test_the_engineer_writes_only_inside_the_ticket_paths(live, decide):
    result = decide(live, "Write", support.write_input("Write", live / SOURCE), ENGINEER, TICKET)
    assert result.decision == "allow", f"Write on {SOURCE} by the engineer on {TICKET}: {result.describe()}"
    result = decide(live, "Bash", support.bash_input(f"echo changed > {SOURCE}"), ENGINEER, TICKET)
    assert result.decision == "allow", f"Bash write to {SOURCE} by the engineer on {TICKET}: {result.describe()}"

    for relpath in ("README.md", ACCEPTANCE_FILE, support.SETTINGS_REL):
        result = decide(live, "Write", support.write_input("Write", live / relpath), ENGINEER, TICKET)
        assert result.decision == "deny", f"Write on {relpath} by the engineer on {TICKET}: {result.describe()}"
        result = decide(live, "Bash", support.bash_input(f"echo changed > {relpath}"), ENGINEER, TICKET)
        assert result.decision == "deny", f"Bash write to {relpath} by the engineer on {TICKET}: {result.describe()}"


def test_the_test_designer_writes_only_acceptance_tests(live, decide):
    """The interim deny rule on ``tests/acceptance/**`` (W1-01) would stop the test designer too."""
    for tool_name in ("Edit", "Write"):
        target = live / support.ACCEPTANCE_REL / "W1-90" / "test_new.py"
        result = decide(live, tool_name, support.write_input(tool_name, target), DESIGNER, TICKET)
        assert result.decision == "allow", (
            f"{tool_name} on tests/acceptance/W1-90/test_new.py by the test designer: {result.describe()}"
        )
    result = decide(live, "Write", support.write_input("Write", live / SOURCE), DESIGNER, TICKET)
    assert result.decision == "deny", f"Write on {SOURCE} by the test designer: {result.describe()}"


def test_ordinary_reads_stay_open(live, decide):
    for command in ("ls -la", "git status --porcelain", "python3 -m pytest tests/unit/guard -q"):
        result = decide(live, "Bash", support.bash_input(command), ENGINEER, TICKET)
        assert result.decision == "allow", f"Bash `{command}` by the engineer on {TICKET}: {result.describe()}"
    result = decide(live, "Read", {"file_path": str(live / "README.md")}, ENGINEER, TICKET)
    assert result.decision == "allow", f"Read on README.md by the engineer: {result.describe()}"


@pytest.mark.parametrize("reader", sorted(READERS), ids=sorted(READERS))
@pytest.mark.parametrize("tool_name", support.READ_ONLY_TOOLS)
def test_a_read_only_tool_goes_through_the_hook_and_is_allowed(live, decide, tool_name, reader):
    """The guard denies writes, not reads: with the hook before every tool, Read, Grep and Glob stay open to all."""
    role, ticket = READERS[reader]
    result = decide(live, tool_name, support.read_input(tool_name, live), role, ticket)
    assert result.ran, f"{tool_name} reached no registered PreToolUse command: {result.describe()}"
    assert result.decision == "allow", f"{tool_name} by {reader} was not allowed: {result.describe()}"


@pytest.mark.parametrize("tool_name", support.READ_ONLY_TOOLS)
def test_a_read_only_tool_is_allowed_while_frozen(scratch_copy, decide, tool_name):
    """The freeze flag stops writes. Reading goes on."""
    flag = scratch_copy / ".gov-runtime" / "freeze"
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.write_text("", encoding="utf-8")
    result = decide(scratch_copy, tool_name, support.read_input(tool_name, scratch_copy), ENGINEER, TICKET)
    assert result.ran, f"{tool_name} reached no registered PreToolUse command: {result.describe()}"
    assert result.decision == "allow", f"{tool_name} by the engineer while frozen: {result.describe()}"


@pytest.mark.parametrize("name", sorted(TIMED_CALLS))
def test_a_call_waits_under_100_ms_p95_for_the_hook(live, switched_over, sandbox, name):
    """W1-02's budget, "decision in < 100 ms p95", through the wiring, for the read-only tools as well.

    The time is what the call waits: every PreToolUse command registered for the
    tool, started together, from the first start to the last exit. p95 over 40
    calls after a warm-up. A round that misses the bound is repeated, up to
    three rounds, so a single stall of the machine does not fail the test.
    """
    tool_name, reader, relpath = TIMED_CALLS[name]
    role, ticket = READERS[reader]
    if relpath is None:
        tool_input = support.read_input(tool_name, live)
    else:
        tool_input = support.write_input(tool_name, live / relpath)

    def call():
        return support.timed_pre_tool_use(live, switched_over, sandbox, tool_name, tool_input, role, ticket)

    for _ in range(LATENCY_WARM_UP):
        call()
    rounds = []
    for _ in range(LATENCY_ROUNDS):
        samples = []
        for _ in range(LATENCY_SAMPLES):
            result, seconds = call()
            assert result.ran, f"{tool_name} reached no registered PreToolUse command: {result.describe()}"
            assert result.decision == "allow", f"the timed {tool_name} was not allowed: {result.describe()}"
            samples.append(seconds)
        rounds.append(support.p95(samples))
        if rounds[-1] < LATENCY_BOUND_S:
            break
    assert min(rounds) < LATENCY_BOUND_S, (
        f"p95 wait of a {tool_name} call for its PreToolUse hooks, per round (ms): "
        + ", ".join(f"{value * 1000:.1f}" for value in rounds)
        + f"; the bound is {LATENCY_BOUND_S * 1000:.0f} ms"
    )


def test_the_freeze_flag_stops_every_write(scratch_copy, decide):
    result = decide(scratch_copy, "Write", support.write_input("Write", scratch_copy / SOURCE), ENGINEER, TICKET)
    assert result.decision == "allow", f"Write on {SOURCE} before the freeze: {result.describe()}"
    flag = scratch_copy / ".gov-runtime" / "freeze"
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.write_text("", encoding="utf-8")
    result = decide(scratch_copy, "Write", support.write_input("Write", scratch_copy / SOURCE), ENGINEER, TICKET)
    assert result.decision == "deny", f"Write on {SOURCE} while frozen: {result.describe()}"


# --------------------------------------------------------------------------
# W1-04 live
# --------------------------------------------------------------------------

@pytest.mark.parametrize("command", INSTALLS)
def test_an_install_by_the_orchestrator_asks_the_owner(live, decide, command):
    """The interim deny rules on installs (W1-01) would stop the prompt from ever appearing."""
    for mode in ("default", "auto", "acceptEdits"):
        result = decide(live, "Bash", support.bash_input(command), ORCHESTRATOR, permission_mode=mode)
        assert result.decision == "ask", (
            f"Bash `{command}` by the orchestrator in {mode} mode did not ask: {result.describe()}"
        )


@pytest.mark.parametrize("command", INSTALLS)
@pytest.mark.parametrize("role", (ENGINEER, DESIGNER, support.PRODUCT_SPEC, support.AUDITOR))
def test_an_install_by_any_other_role_is_denied(live, decide, command, role):
    result = decide(live, "Bash", support.bash_input(command), role, TICKET)
    assert result.decision == "deny", f"Bash `{command}` by {role} was not denied: {result.describe()}"


@pytest.mark.parametrize("role", support.ROLES)
def test_sudo_is_denied_to_every_role(live, decide, role):
    command = "sudo apt-get install -y jq"
    result = decide(live, "Bash", support.bash_input(command), role, TICKET)
    assert result.decision == "deny", f"Bash `{command}` by {role} was not denied: {result.describe()}"


# --------------------------------------------------------------------------
# W1-03 live
# --------------------------------------------------------------------------

def test_the_containment_check_reports_a_change_outside_the_ticket_paths(scratch_copy, switched_over, sandbox):
    command = "python3 -c \"open('README.md', 'a').write('changed')\""
    support.run_bash(scratch_copy, command, sandbox)
    assert "README.md" in support.git(scratch_copy, "status", "--porcelain"), "the fixture command changed nothing"
    report, results = support.post_bash(scratch_copy, switched_over, sandbox, command, ENGINEER, TICKET)
    assert "README.md" in report, (
        "the change to README.md was not reported to the agent: "
        + "; ".join(result.describe() for result in results)
    )


def test_the_containment_check_restores_an_acceptance_test(scratch_copy, switched_over, sandbox):
    """One whole call through the wiring: the PreToolUse commands, the command, the PostToolUse commands.

    The check restores only what the call changed, and it knows that from the
    before-snapshot it takes in PreToolUse (DEC-124, DEC-126). So this test also
    shows that the snapshot is wired: with the PostToolUse commands alone, the
    check flags the change and leaves it.
    """
    before = (scratch_copy / ACCEPTANCE_FILE).read_text(encoding="utf-8")
    command = f"python3 -c \"open('{ACCEPTANCE_FILE}', 'a').write('changed')\""
    report, results = support.bash_call(scratch_copy, switched_over, sandbox, command, ENGINEER, TICKET,
                                        changed=[ACCEPTANCE_FILE])
    detail = "; ".join(result.describe() for result in results)
    assert (scratch_copy / ACCEPTANCE_FILE).read_text(encoding="utf-8") == before, (
        f"{ACCEPTANCE_FILE} was not restored from HEAD after an engineer's change: {detail}"
    )
    assert ACCEPTANCE_FILE in report, f"the breach was not reported to the agent: {detail}"


def test_the_containment_check_runs_after_a_failed_call(scratch_copy, switched_over, sandbox):
    command = "python3 -c \"open('README.md', 'a').write('changed')\"; exit 3"
    support.run_bash(scratch_copy, command, sandbox)
    report, results = support.post_bash(scratch_copy, switched_over, sandbox, command, ENGINEER, TICKET,
                                        event="PostToolUseFailure")
    assert "README.md" in report, (
        "the change left by a failed call was not reported to the agent: "
        + "; ".join(result.describe() for result in results)
    )


def test_the_containment_check_leaves_in_scope_work_alone(scratch_copy, switched_over, sandbox):
    command = f"python3 -c \"open('{SOURCE}', 'a').write('# changed')\""
    support.run_bash(scratch_copy, command, sandbox)
    report, results = support.post_bash(scratch_copy, switched_over, sandbox, command, ENGINEER, TICKET)
    detail = "; ".join(result.describe() for result in results)
    assert all(result.returncode == 0 for result in results), f"a registered command failed: {detail}"
    assert report == "", f"an in-scope change was reported: {report!r}"
    assert (scratch_copy / SOURCE).read_text(encoding="utf-8").endswith("# changed"), (
        f"the in-scope change to {SOURCE} was reverted"
    )


def _leave_a_bash_call_unfinished(project, settings, sandbox):
    """The orchestrator's main thread starts a Bash call that never ends: the PreToolUse commands run, nothing follows.

    That is a declined permission prompt or an interrupt. Until the call is
    known to be over, it counts as an overlapping call of another actor, and the
    check flags and does not revert (DEC-130).
    """
    before = support.pre_tool_use(project, settings, sandbox, "Bash", support.bash_input("ls -la"),
                                  tool_use_id="toolu_w1_05_unfinished", **ORCHESTRATOR_MAIN)
    assert before.decision == "allow", f"the fixture call `ls -la` was not let through: {before.describe()}"


def _engineer_subagent_changes_an_acceptance_test(project, settings, sandbox):
    """One whole Bash call of the engineer subagent. Returns the report and a description of the hook runs."""
    command = f"python3 -c \"open('{ACCEPTANCE_FILE}', 'a').write('changed')\""
    report, results = support.bash_call(project, settings, sandbox, command, changed=[ACCEPTANCE_FILE],
                                        tool_use_id="toolu_w1_05_breach", **ENGINEER_SUBAGENT)
    return report, "; ".join(result.describe() for result in results)


@pytest.mark.parametrize("tool_name", sorted(LATER_CALLS))
def test_a_later_call_of_any_tool_shows_the_actor_s_unfinished_call_is_over(scratch_copy, switched_over, sandbox,
                                                                           tool_name):
    """DEC-142, DEC-144: "the same actor's session has issued a later tool call". The hook must see that call.

    The orchestrator's Bash call never ends. Its next call is not a write: it
    reads, starts a subagent, or uses a tool of an MCP server. Then the engineer
    subagent changes an acceptance test in one whole Bash call. The test is
    restored from HEAD, which it is only if the later call reached the hook.
    """
    before = (scratch_copy / ACCEPTANCE_FILE).read_text(encoding="utf-8")
    _leave_a_bash_call_unfinished(scratch_copy, switched_over, sandbox)
    later = support.pre_tool_use(scratch_copy, switched_over, sandbox, tool_name, LATER_CALLS[tool_name](scratch_copy),
                                 tool_use_id="toolu_w1_05_later", **ORCHESTRATOR_MAIN)
    assert later.ran, f"the orchestrator's later {tool_name} call reached no PreToolUse command: {later.describe()}"
    assert later.decision != "error", f"a PreToolUse command failed on {tool_name}: {later.describe()}"
    report, detail = _engineer_subagent_changes_an_acceptance_test(scratch_copy, switched_over, sandbox)
    assert (scratch_copy / ACCEPTANCE_FILE).read_text(encoding="utf-8") == before, (
        f"{ACCEPTANCE_FILE} was not restored from HEAD after the engineer subagent's change, although the "
        f"orchestrator's unfinished call was followed by a {tool_name} call of the orchestrator: {detail}"
    )
    assert ACCEPTANCE_FILE in report, f"the breach was not reported to the agent: {detail}"


def test_without_a_later_call_the_unfinished_call_still_blocks_the_restore(scratch_copy, switched_over, sandbox):
    """DEC-130: for all the check knows, the orchestrator's call is still running. Flagged, and not reverted.

    The same steps as the test above without the later call. It shows that the
    restore there is owed to the later call.
    """
    _leave_a_bash_call_unfinished(scratch_copy, switched_over, sandbox)
    report, detail = _engineer_subagent_changes_an_acceptance_test(scratch_copy, switched_over, sandbox)
    assert (scratch_copy / ACCEPTANCE_FILE).read_text(encoding="utf-8").endswith("changed"), (
        f"{ACCEPTANCE_FILE} was reverted while another actor's call was still open: {detail}"
    )
    assert ACCEPTANCE_FILE in report, f"the breach was not reported to the agent: {detail}"


# --------------------------------------------------------------------------
# Every later ticket
# --------------------------------------------------------------------------

def _settings_at(commit):
    import json
    text = support.git(support.REPO_ROOT, "show", f"{commit}:{support.SETTINGS_REL}", check=False)
    try:
        data = json.loads(text) if text.strip() else {}
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def test_the_hooks_stay_wired_in_every_later_commit(switched_over):
    """Once a commit wires the hooks, for every tool, no later commit on this branch takes them out."""
    commits = support.git(
        support.REPO_ROOT, "log", "--first-parent", "--reverse", "--format=%H", "--", support.SETTINGS_REL,
    ).split()
    wired = [support.is_wired_for_every_tool(_settings_at(commit)) for commit in commits]
    if True not in wired:
        return   # the switch-over is in the working tree and not committed yet
    first = wired.index(True)
    unwired = [commits[i][:7] for i in range(first, len(commits)) if not wired[i]]
    assert not unwired, (
        f"the hooks were wired for every tool in {commits[first][:7]} and are not in later commits: "
        f"{', '.join(unwired)}"
    )
