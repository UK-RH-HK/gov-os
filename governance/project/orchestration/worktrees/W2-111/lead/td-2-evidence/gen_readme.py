"""Writes the W2-111 section of the three READMEs from the recorded figures."""
import sys, re
sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-111-tests/.gov-runtime/scratch/td")
import gen_tables as G
D = "/home/usain/gov-os-worktrees/W2-111-tests/.gov-runtime/scratch/td/"
quiet = G.instr([D + "real2-quiet.figs"])
l25 = G.instr([D + f"real2-w3-{x}.figs" for x in "abc"])
l50 = G.instr([D + f"real2-w4-{x}.figs" for x in "abc"])
pl50 = G.instr([D + f"real2-w4-pl-{x}.figs" for x in "abc"], n=8)
fin = G.final(D + "final-quiet.figs")
plamb = G.final(D + "final-planted-amb.figs")

def cell(rounds, rounds_all=True):
    """judged (raw - reference) of each round, in ms"""
    return "; ".join(f"**{x[0]:.0f}** ({x[1]:.0f} - {x[2]:.0f})" for x in rounds) if rounds else "-"
def plcell(rounds):
    return "; ".join(f"{x[0]:.0f} ({x[1]:.0f} - {x[2]:.0f})" for x in rounds) if rounds else "-"

def rows(select):
    out = []
    for t in quiet:
        if not select(t): continue
        nm = G.name(t)
        out.append(f"| `{nm}` | {cell(quiet[t])} | {cell(l25[t])} | {cell(l50[t])} | {plcell(plamb[t])} | {plcell(pl50[t])} |")
    return "\n".join(out)

HEAD = """## W2-111: the hook-latency case(s) judge the hook's own work against a reference hook timed beside them (DAEO-qvff; `Rewrite-Reason: DEC-979`)

`Rewrite-Reason: DEC-979` (the owner's D2 (a) on CAPACITY-1, P-LATENCY-1; DEC-906, DEC-968). Revised twice by fresh
independent test designers (round 1 and round 2, 2026-11-13); the case ids, their parameters, the 100 ms bound at p95,
the 3 warm-up calls, the 40 samples, the nearest-rank p95 and the three-round repeat are the same as before the
revision; nothing is skipped, marked or removed.

**What it measures.** {WHAT}

**What it counts, and what it does not.** It counts the CPU time (user and system) of the hook's process and of every
process it waited for (its forked decision process, the git it runs), less one reference hook's. It leaves out, once per
call, what any hook costs before it does anything of its own: a fresh interpreter's start and the read of the event
(the reference hook's CPU time: about 15 ms on a quiet machine, about 21 ms with every CPU busy). **This lowers what is
judged by that much**: a hook that spends 100 ms of CPU in all, 85 ms of it its own, is judged at 85 ms and passes; the
ceiling on a hook's total CPU time is about 115 ms quiet and 121 ms loaded. It was chosen over a form that leaves
nothing out because no such form held its verdict under load (below). It does not see a hook that is slow only by
waiting (a sleep, a lock, a network wait): that spends no CPU. It does not remove the effect of load on CPU time: with
every CPU busy the same work costs about 1.4 times the CPU time (a busy sibling thread on the same core), so the judged
figure of a case rises under load (a hook case of 25 ms quiet is judged at 45 to 57 ms at load 25 to 58); the verdict
holds by its margin: the highest judged figure of the 15 cases at load 52 to 59 was 91 ms (the designer's read,
W2-57), against the 100 ms bound, and a hook doing 150 ms of CPU of its own is judged at 173 to 326 ms at every load
measured.

**Why wall time under load is not the measure, and why CPU time alone was not.** A wall clock under load times the
scheduler's queue, not the hook. On 2026-10-31 the 11 cases (then) were traced in three rounds, with W2-106 and without
it: red 8, 0, 1 of 11 with it and 0, 0, 5 without, at loads of 15 to 30, with run times of 34 to 152 s, whatever the
change; they pass alone on a quiet machine. Under load the p95 wall time of one call is 120 to 350 ms at load 25 to 58
for a hook that takes 40 to 60 ms alone. Round 1 judged the CPU time alone (`RUSAGE_CHILDREN`); the CTO's benchmark
(2026-11-13 06:36 to 07:20, load 20 and 50 and more) found it is not load-independent on this machine (an i7-12700F,
20 logical CPUs, two threads per core): 3 of the 15 cases were red at both loads (CPU p95 100 to 186 ms, against 40 to
60 ms quiet), because a CPU time counts time on a CPU, not work done, and the same work takes about 1.4 times as long on
a core whose sibling thread is busy. The reference hook is timed in the same round, in the same CPU share (the same
process, the call before the real one), so what load adds to a trivial hook's CPU time is taken off the real hook's.
(A reference minimum or low percentile as a quiet baseline for a ratio form was measured and does not work: with every
CPU busy the fastest of 60 reference calls is 1.35 to 1.8 times its quiet CPU time, so no quiet figure exists in a run
that is loaded throughout.)

**The reference hook.** A fresh interpreter (`sys.executable -c`) that reads the event on standard input and prints the
"allow" answer, started as the hook is (a child process of the test), its CPU time read from `RUSAGE_CHILDREN` before
and after. It is called once before each timed call and once after each warm-up call, so the 40 calls of a round have
40 reference calls beside them. The round's figure is `p95(40 CPU times) - median(40 reference CPU times)`; the failure
message prints the figure, the raw CPU p95, the reference median and the wall p95 of each round.

**Measured figures.** Cells are the judged figure of the first round in ms (bold), then, in brackets, the raw CPU p95
less the reference median that made it; a case that needed more rounds shows each, separated by semicolons. Judged
figures under 100 pass. Provenance: the quiet, load 23 to 28 and load 52 to 59 columns come from an instrumented run
of the same 15 cases (a scratch plugin outside the repository, `-p td_plugin2`, that times the reference hook before each
call and applies the committed arithmetic; the three shards run together through the heavy slot, `taskset` to the slot's
CPUs): quiet 2026-11-13 07:42, load 1.8 to 2.5; the load windows below. The committed code itself ran, through the heavy
slot, at ambient load about 9 to 11 (2026-11-13 07:57, 15 passed in 43 s; judged 26 to 50 ms) and planted at ambient
load about 5 to 9 (the "planted" column). The committed code was not run at load 23 to 28 or at
52 and more (the four load windows were used on the measures above): the lead's driver (`-p td_plugin`, `TD_FIGURES`,
`TD_PLANT_S`) is the run of the committed code at those loads. The load windows (the lead's `load_window.sh`, unpinned busy loops at nice 0;
a window's loops end by themselves): window 1, N=22, 07:27 (the loops died with the Bash call that started them: no
load was seen, no measure was made); window 2, N=56, 07:32 to 07:37 (experiments outside pytest); window 3, N=24, 07:44
(load 20 at +72 s, shards of the real cases at `/proc/loadavg` 20.2 to 27.7); window 4, N=56, 07:49 (load 50.6 at
+121 s, real shards at 50.6 to 58.6, planted shards at 58.6 to 59.7).

| case (parameter) | quiet (load 1.8 to 2.5) | load 23 to 28 | load 52 to 59 | planted 150 ms hook, committed code, ambient load 5 to 9, 3 rounds | planted 150 ms hook, load 52 to 59, 1 round of 8 calls |
|---|---|---|---|---|---|
{ROWS}

{PLANTED}
"""
PLANTED = """**The planted hook.** A scratch harness (a pytest plugin outside the repository, passed with `-p`; nothing in a committed
test carries a switch, an environment variable or a hook) ran the installed PreToolUse hook behind a launcher that
busy-loops until its own `time.process_time()` reaches 0.150 s and then `exec`s the real hook, so the decision is the
real one and only the latency changes. Every case FAILED on the latency assertion (`AssertionError: p95 CPU time ...`),
never on a decision assertion or a setup error: {NPL}. A plant that is itself a CPU time is not divided by the load
factor here (the reference is subtracted, not divided into it); a fixed-work plant (a loop calibrated to 150 ms of CPU
quiet, 2.1 million iterations) costs 270 to 285 ms of CPU with every CPU busy, so it fails by more. Logs:
`.gov-runtime/scratch/td/final-planted-amb.log` and `real2-w4-pl-{a,b,c}.log` (the figures beside them, `.figs`)."""
WHATS = {
"W1-02": "`test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms` (5 parameters: `no-role-deny`, `engineer-allow-from-ticket-frontmatter`, `engineer-deny-outside-the-ticket`, `test-designer-allow`, `frozen-deny`): the CPU time of the guard's hook process and its children over one write decision (`HookResult.cpu_seconds`, filled by `run_hook_raw`: the `RUSAGE_CHILDREN` difference before and after the one synchronous call), less the median CPU time of a reference hook called just before each of the 40 timed calls, in the same round. The bound is 100 ms at p95.",
"W1-05": "`test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook` (9 parameters: `Edit-engineer`, `Glob-engineer`, `Glob-no-role`, `Grep-engineer`, `Grep-no-role`, `NotebookEdit-engineer`, `Read-engineer`, `Read-no-role`, `Write-engineer`): the CPU time of one call's PreToolUse hooks (every command registered for the tool, started together as the harness starts them, and what each waited for: the `RUSAGE_CHILDREN` difference before and after the call, so the sum of their work, stricter than the wall time of commands that run side by side), less the median CPU time of one reference hook called just before each of the 40 timed calls, in the same round (one reference hook per call, whatever the number of commands). The bound is 100 ms at p95.",
"W2-57": "`test_w2_57_designer_read_p95.py::test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95` (one case): the CPU time of the hook and its children for a test designer's read on a branch with 120 changed files (the git that finds the files the branch changes, Policy 2 (c): `HookResult.cpu_seconds`), less the median CPU time of a reference hook called just before each of the 40 timed reads, in the same round. The bound is 100 ms at p95.",
}
SEL = {"W1-02": lambda t: "W1-02" in t, "W1-05": lambda t: "W1-05" in t, "W2-57": lambda t: "W2-57" in t}
def npl(sel):
    ts = [t for t in plamb if sel(t)]
    lo = min(min(x[0] for x in plamb[t]) for t in ts); hi = max(max(x[0] for x in plamb[t]) for t in ts)
    ts5 = [t for t in pl50 if sel(t)]
    lo5 = min(x[0] for t in ts5 for x in pl50[t]); hi5 = max(x[0] for t in ts5 for x in pl50[t])
    return f"{len(ts)} of {len(ts)} at ambient load (judged figures {lo:.0f} to {hi:.0f} ms in every round), {len(ts5)} of {len(ts5)} at load 52 to 59 (judged {lo5:.0f} to {hi5:.0f} ms)"
for key in ("W1-02", "W1-05", "W2-57"):
    path = f"/home/usain/gov-os-worktrees/W2-111-tests/tests/acceptance/{key}/README.md"
    text = open(path).read()
    i = text.index("## W2-111:")
    section = HEAD.replace("{WHAT}", WHATS[key]).replace("{ROWS}", rows(SEL[key])).replace("{PLANTED}", PLANTED.replace("{NPL}", npl(SEL[key])))
    open(path, "w").write(text[:i] + section)
    print(key, "written", len(section))
