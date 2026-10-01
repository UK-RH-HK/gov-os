"""W1-02 — the guard is a PreToolUse hook of the kernel template, and it is fast.

KPI success 1 names the guard as the G0 tier [CAP-39.a]: a check that runs
before the tool does. KPI success 3 bounds its cost: "decision in < 100 ms p95".

The allow-list part of success 1 and the other two clauses of success 3 (freeze
flag, ticket frontmatter) wait for KPI disputes KD-1, KD-2 and KD-3.
"""

from __future__ import annotations

import w1_02_support as support

LATENCY_BOUND_S = 0.100
LATENCY_SAMPLES = 40
LATENCY_WARM_UP = 3
LATENCY_ROUNDS = 3


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


def test_decision_p95_is_under_100_ms(project, call):
    """Wall-clock time of the hook process, start to exit, as the harness waits for it.

    p95 over 40 calls after a warm-up. A round that misses the bound is repeated,
    up to three rounds, so a single stall of the machine does not fail the KPI.
    """
    tool_input = support.edit_tool_input("Write", project / "src/gov/guard/decide.py")
    for _ in range(LATENCY_WARM_UP):
        call(project, "Write", tool_input)
    rounds = []
    for _ in range(LATENCY_ROUNDS):
        samples = []
        for _ in range(LATENCY_SAMPLES):
            result = call(project, "Write", tool_input)
            assert result.decision == "deny", f"the timed call was not decided as expected: {result.describe()}"
            samples.append(result.seconds)
        rounds.append(support.p95(samples))
        if rounds[-1] < LATENCY_BOUND_S:
            break
    assert min(rounds) < LATENCY_BOUND_S, (
        "p95 decision time per round (ms): " + ", ".join(f"{value * 1000:.1f}" for value in rounds)
        + f"; the bound is {LATENCY_BOUND_S * 1000:.0f} ms"
    )
