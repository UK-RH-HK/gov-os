"""W2-57, KPI line 5 (I1 F-10): the 100 ms p95 budget covers a test designer's read on a branch with changes.

DEC-149: the guard's decision is under 100 ms at p95, for every tool. Under Policy 2 (c) (DEC-820 (c), DEC-826
Q2) a test designer's every read runs git to find the files its ticket's branch changes against ``w2/integrate``;
no p95 case timed that path (W1-02's times five writes, W1-05's an engineer's and a role-less session's calls).

The world is W1-02's fixture project with the guard installed, its first commit on ``w2/integrate`` and the
ticket's own branch with 120 changed files (real ticket branches held 48 to 318, I1 F-10). That the read takes the
path is shown first: the designer is refused a file the branch changes, and allowed an ordinary one. The timing is
W1-02's: p95 over 40 reads after 3 warm-up reads, a round repeated up to three times as before.

Rewrite-Reason: DEC-979 (W2-111, P-LATENCY-1; DEC-906). The case timed the wall time of the hook process; under
load a wall clock times the scheduler's queue, not the hook (2026-10-31: red 8, 0, 1 of the 11 latency cases with
W2-106 and 0, 0, 5 without, at loads of 15 to 30; green alone on a quiet machine). A CPU time alone was not the
measure either (round 1, 2026-11-13: it rises about 1.4 times when every CPU is busy, because a busy sibling thread
slows the same work; 3 of the 15 cases were red at load 20 and at 50, this one at both). Each read is now judged by
the CPU time (user and system) of the hook process and its children (``result.cpu_seconds``, from
``RUSAGE_CHILDREN``: the hook, its forked decision process and the git it runs), less the CPU time of a reference
hook (a trivial hook: a fresh interpreter that reads the event and answers) called just before it, in the same round
and the same CPU share. The round's figure is the nearest-rank p95 of the 40 reads' CPU times less the median of the
40 reference calls' CPU times. It leaves out what any hook costs (the interpreter's start and the event read, about
15 ms quiet, 21 ms loaded), so a hook is judged on its work beyond that. The bound is the same 100 ms at p95; the raw
CPU p95, the reference's median and the wall p95 are reported beside it, for information.

A latency case: it is kept serial in the close's list (``serial: latency``), alone after the parallel phase. About
2.5 s alone (on a quiet machine a read took a median of 50 ms, p95 55 ms; an engineer's, 45 and 47 ms).
"""

from __future__ import annotations

import re
import resource
import statistics
import subprocess
import sys

import w2_57_list_support as support

guard = support.guard_support

LATENCY_BOUND_S = 0.100
SAMPLES = 40
WARM_UP = 3
ROUNDS = 3
ORDINARY = "README.md"
CHANGED = "src/gov/guard/change_000.py"

# The reference hook (W2-111, DEC-979): a hook of trivial work, started as the hook is (a child interpreter), that
# reads the event and answers "allow". Its CPU time, timed beside each real read, is what any hook costs before it
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


def test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95(tmp_path):
    project, sandbox = support.designer_world(tmp_path)
    refused = support.designer_read(project, sandbox, CHANGED)
    assert refused.decision == "deny" and re.search(r"DEC-820 \(c\)", refused.stdout), (
        f"the fixture is wrong: the test designer is not refused a file its ticket's branch changes, so the read "
        f"does not take Policy 2 (c)'s path: {refused.describe()}"
    )
    for _ in range(WARM_UP):
        support.designer_read(project, sandbox, ORDINARY)
        reference_cpu_seconds()
    rounds = []
    figures = []
    for _ in range(ROUNDS):
        samples = []
        wall_samples = []
        reference_samples = []
        for _ in range(SAMPLES):
            reference_samples.append(reference_cpu_seconds())
            result = support.designer_read(project, sandbox, ORDINARY)
            assert result.decision == "allow", f"the timed read was not allowed: {result.describe()}"
            assert result.cpu_seconds is not None, f"the read's CPU time was not measured: {result.describe()}"
            samples.append(result.cpu_seconds)
            wall_samples.append(result.seconds)
        cpu_p95 = guard.p95(samples)
        wall_p95 = guard.p95(wall_samples)
        reference = statistics.median(reference_samples)
        rounds.append(cpu_p95 - reference)
        figures.append((cpu_p95, reference, wall_p95))
        if rounds[-1] < LATENCY_BOUND_S:
            break
    assert min(rounds) < LATENCY_BOUND_S, (
        "p95 CPU time of the hook and its children for a test designer's read on a branch with changes, less the "
        "median CPU time of the reference hook timed beside it, per round (ms): "
        + ", ".join(f"{value * 1000:.1f}" for value in rounds)
        + f"; the bound is {LATENCY_BOUND_S * 1000:.0f} ms (per round, for information, ms: raw CPU p95 "
        + ", ".join(f"{cpu * 1000:.1f}" for cpu, _, _ in figures) + "; reference median "
        + ", ".join(f"{ref * 1000:.1f}" for _, ref, _ in figures) + "; wall p95 "
        + ", ".join(f"{wall * 1000:.1f}" for _, _, wall in figures) + ")"
    )
