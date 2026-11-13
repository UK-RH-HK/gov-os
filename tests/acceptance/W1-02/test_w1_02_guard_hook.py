"""W1-02 — the guard is a PreToolUse hook of the kernel template, and it is fast.

KPI success 1 names the guard as the G0 tier [CAP-39.a]: a check that runs
before the tool does. KPI success 3 bounds its cost: "decision in < 100 ms p95".
"""

from __future__ import annotations

import resource
import statistics
import subprocess
import sys

import pytest

import w1_02_support as support

LATENCY_BOUND_S = 0.100
LATENCY_SAMPLES = 40
LATENCY_WARM_UP = 3
LATENCY_ROUNDS = 3

# The reference hook (W2-111, DEC-979): a hook of trivial work, started as the hook is (a child interpreter), that
# reads the event and answers "allow". Its CPU time, timed beside each real call, is what any hook costs before it
# does anything of its own.
REFERENCE_HOOK = (
    "import json, sys\n"
    "json.load(sys.stdin)\n"
    "print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'allow'}}))\n"
)


def reference_cpu_seconds():
    """CPU time (user and system) of one call of the reference hook: ``RUSAGE_CHILDREN`` before and after it."""
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    subprocess.run([sys.executable, "-c", REFERENCE_HOOK], input="{}", capture_output=True, text=True, check=True)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    return (after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime)


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
    """The hook's own work, p95 under 100 ms: its CPU time over each call, less a reference hook timed beside it.

    Rewrite-Reason: DEC-979 (W2-111, P-LATENCY-1; DEC-906). The case measured the wall time of the hook process;
    under load a wall clock times the scheduler's queue, not the hook (2026-10-31: red 8, 0, 1 of the 11 latency
    cases with W2-106 and 0, 0, 5 without, at loads of 15 to 30; green alone on a quiet machine). A CPU time alone
    was not the measure either (round 1, 2026-11-13: it rises about 1.4 times when every CPU is busy, because a
    busy sibling thread slows the same work; 3 of the 15 cases were red at load 20 and at 50). Each call is now
    judged by the CPU time of the hook and of every process it waited for (``result.cpu_seconds``, from
    ``RUSAGE_CHILDREN``), less the CPU time of a reference hook (a trivial hook: a fresh interpreter that reads the
    event and answers) called just before it, in the same round and the same CPU share. The round's figure is the
    nearest-rank p95 of the 40 calls' CPU times less the median of the 40 reference calls' CPU times. It leaves out
    what any hook costs (the interpreter's start and the event read, about 15 ms quiet, 21 ms loaded), so a hook
    is judged on its work beyond that; the bound (100 ms), the 40 samples, the 3 warm-up calls and the p95 are the
    same, and a round that misses the bound is repeated, up to three rounds, as before. The raw CPU p95, the
    reference's median and the wall p95 are reported beside it, for information.
    """
    role, ticket, relpath, frozen, expected = TIMED_DECISIONS[name]
    if frozen:
        support.set_freeze(project)
    for _ in range(LATENCY_WARM_UP):
        write(project, relpath, role, ticket)
        reference_cpu_seconds()
    rounds = []
    figures = []
    for _ in range(LATENCY_ROUNDS):
        samples = []
        wall_samples = []
        reference_samples = []
        for _ in range(LATENCY_SAMPLES):
            reference_samples.append(reference_cpu_seconds())
            result = write(project, relpath, role, ticket)
            assert result.decision == expected, (
                f"the timed call was not decided as expected ({expected}): {result.describe()}"
            )
            assert result.cpu_seconds is not None, f"the call's CPU time was not measured: {result.describe()}"
            samples.append(result.cpu_seconds)
            wall_samples.append(result.seconds)
        cpu_p95 = support.p95(samples)
        wall_p95 = support.p95(wall_samples)
        reference = statistics.median(reference_samples)
        rounds.append(cpu_p95 - reference)
        figures.append((cpu_p95, reference, wall_p95))
        if rounds[-1] < LATENCY_BOUND_S:
            break
    assert min(rounds) < LATENCY_BOUND_S, (
        "p95 CPU time of the hook and its children per call, less the median CPU time of the reference hook timed "
        "beside it, per round (ms): " + ", ".join(f"{value * 1000:.1f}" for value in rounds)
        + f"; the bound is {LATENCY_BOUND_S * 1000:.0f} ms (per round, for information, ms: raw CPU p95 "
        + ", ".join(f"{cpu * 1000:.1f}" for cpu, _, _ in figures) + "; reference median "
        + ", ".join(f"{ref * 1000:.1f}" for _, ref, _ in figures) + "; wall p95 "
        + ", ".join(f"{wall * 1000:.1f}" for _, _, wall in figures) + ")"
    )
