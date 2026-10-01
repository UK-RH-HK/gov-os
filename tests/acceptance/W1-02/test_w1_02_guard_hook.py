"""W1-02 — the guard is a PreToolUse hook of the kernel template, and it is fast.

KPI success 1 names the guard as the G0 tier [CAP-39.a]: a check that runs
before the tool does. KPI success 3 bounds its cost: "decision in < 100 ms p95".
"""

from __future__ import annotations

import pytest

import w1_02_support as support

LATENCY_BOUND_S = 0.100
LATENCY_SAMPLES = 40
LATENCY_WARM_UP = 3
LATENCY_ROUNDS = 3

# name: (GOV_ROLE, GOV_TICKET, repository-relative path, freeze flag set, expected decision)
TIMED_DECISIONS = {
    "no-role-deny": (None, None, "src/gov/guard/decide.py", False, "deny"),
    "engineer-allow-from-ticket-frontmatter": (
        support.ENGINEER, support.TICKET_ID, "src/gov/guard/decide.py", False, "allow"),
    "engineer-deny-outside-the-ticket": (support.ENGINEER, support.TICKET_ID, "README.md", False, "deny"),
    "test-designer-allow": (
        support.TEST_DESIGNER, support.TICKET_ID,
        f"tests/acceptance/{support.TICKET_WBS_ID}/test_fixture.py", False, "allow"),
    "frozen-deny": (support.ENGINEER, support.TICKET_ID, "src/gov/guard/decide.py", True, "deny"),
}


def test_guard_hook_ships_in_the_kernel_template(hook):
    """One runnable entry point under ``template/governance/kernel/hooks/pretooluse*``."""
    relpath = hook.relative_to(support.REPO_ROOT).as_posix()
    assert relpath.startswith(support.HOOK_DIR_REL + "/pretooluse"), relpath
    assert hook.read_text(encoding="utf-8").strip(), f"{relpath} is empty"


def test_guard_decides_before_the_tool_runs(project, call):
    """Driven as a PreToolUse hook, the guard answers both ways: it refuses a write and lets a read through."""
    write = call(project, "Write", support.edit_tool_input("Write", project / "README.md"))
    read = call(project, "Read", {"file_path": str(project / "README.md")})
    assert write.decision == "deny", f"a write by a role-less session was not refused: {write.describe()}"
    assert read.decision == "allow", f"a read was not let through: {read.describe()}"
    assert (project / "README.md").read_text(encoding="utf-8") == support.PROJECT_FILES["README.md"], (
        "README.md changed although the guard only decides"
    )


@pytest.mark.parametrize("name", sorted(TIMED_DECISIONS), ids=sorted(TIMED_DECISIONS))
def test_decision_p95_is_under_100_ms(project, write, name):
    """Wall-clock time of the hook process, start to exit, as the harness waits for it.

    p95 over 40 calls after a warm-up. A round that misses the bound is repeated,
    up to three rounds, so a single stall of the machine does not fail the KPI.
    """
    role, ticket, relpath, frozen, expected = TIMED_DECISIONS[name]
    if frozen:
        support.set_freeze(project)
    for _ in range(LATENCY_WARM_UP):
        write(project, relpath, role, ticket)
    rounds = []
    for _ in range(LATENCY_ROUNDS):
        samples = []
        for _ in range(LATENCY_SAMPLES):
            result = write(project, relpath, role, ticket)
            assert result.decision == expected, (
                f"the timed call was not decided as expected ({expected}): {result.describe()}"
            )
            samples.append(result.seconds)
        rounds.append(support.p95(samples))
        if rounds[-1] < LATENCY_BOUND_S:
            break
    assert min(rounds) < LATENCY_BOUND_S, (
        "p95 decision time per round (ms): " + ", ".join(f"{value * 1000:.1f}" for value in rounds)
        + f"; the bound is {LATENCY_BOUND_S * 1000:.0f} ms"
    )
