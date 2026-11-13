# Brief: independent auditor (read-only), W2-111 (ticket DAEO-qvff), LITE probe

You are a fresh, read-only independent auditor. One ticket: DAEO-qvff (W2-111), profile LITE, class C1, a test revision under the owner's named decision (DEC-979 item 1 D2 (a), P-LATENCY-1; DEC-906; DEC-968). Headless: only your last message is read. **You write nothing**: no file, no commit, no git state change (no checkout, no stash, no worktree). Read and run read-only commands only.

## What to probe
Head `3da7242f4461` on `w2/W2-111` in /home/usain/gov-os-worktrees/W2-111 (the merge of `w2/W2-111-tests`: the test designer's commits `a5bf1c0131b8` (form B) and `e3b1d59d70f6` (DEC-1163 (3) named in the READMEs)). The unrevised files are at `085b4391c` (before round 1) and `8b8b561fc` (round 1).

The 15 cases (11 in DEC-979's count; 15 node ids with parameters, DEC-1157 (12)):
- `tests/acceptance/W1-02/test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms` (5 parameters)
- `tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook` (9 parameters)
- `tests/acceptance/W2-57/test_w2_57_designer_read_p95.py::test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95` (1)

The owner decided the measure: **DEC-1163 (3)** (ACCEPTED, 2026-11-13): "P-W2-111-MEASURE-1 (a): W2-111's cases judge the round's CPU p95 of the hook and its children minus the median CPU of a stub hook timed beside each call, at the same 100 ms (form B, a5bf1c0131b8); the start-up cost left out (~16-21 ms) is accepted under DEC-906." Read it at /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md (grep `### DEC-1163`). Form B's subtraction is therefore decided; do not judge it as a lowering against the ticket's words. Judge whether the code does what DEC-1163 (3) says, and the rest below.

Ticket (read-only): /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-qvff.md. Decisions by id in the register above: DEC-979, DEC-906, DEC-968, DEC-958, DEC-1163.

## Check each, and give each a verdict (holds / fails, with file:line or command output)
1. **S1, the measure.** In each of the three case files, the judged figure is the round's CPU p95 (user + system, `RUSAGE_CHILDREN` of the hook and its children) less the median CPU of a stub reference hook timed beside each call in the same round, against `LATENCY_BOUND_S = 0.100`; 40 samples, 3 warm-up calls, nearest-rank p95 as before. Nothing in a committed test carries a switch, environment variable or hook for planting or recording.
2. **F1, nothing lowered beyond the decision, nothing removed.** `git -C /home/usain/gov-os-worktrees/W2-111 diff 085b4391c 3da7242f4461 -- <the three case files>`: the bound is the same 100 ms; no `skip`, `xfail` or `flaky` mark added; no test id removed. Collect-only: the lead's `.gov-runtime/scratch/lead/log/collect-after-3.txt` against `.gov-runtime/scratch/lead/td-1-evidence/collect-before.txt` (the same 15 ids). You may re-run collect-only yourself (see Running pytest).
3. **S4, the READMEs.** Each of `tests/acceptance/{W1-02,W1-05,W2-57}/README.md`'s W2-111 section states what its case measures, why wall time under load is not the measure, carries `Rewrite-Reason: DEC-979`, names DEC-1163 (3) where it names the measure, and holds measured figures. `git log 085b4391c..3da7242f4461 --format='%h %s%n%(trailers)'`: each commit touching tests/acceptance carries `Task: DAEO-qvff` and `Rewrite-Reason: DEC-979`; `Implements:` only from the ticket's `sources:` (DEC-979, DEC-906, DEC-968, DEC-958); no `Role: owner`, no `Decided-by:`.
4. **S2/S3/F2/F3, from the benchmark's figures** (you run no load): `/home/usain/gov-os-worktrees/W2-111/.gov-runtime/scratch/lead/bench-2/` (`summary.txt`; `{quiet,load20,load20-planted,load50,load50-planted}.{log,figs,figs.ref}`; `bench.sh`, the driver). Check that the summary matches the logs: 15 pass quiet, at load ~20 and at 50+ (loads recorded in each log's start/end lines); the planted 150 ms hook fails all 15 at both loads, on the latency assertion. Note the risk the lead recorded: the planted W2-57 case at load 50 ran after the load loops ended; say whether the logs show that, and whether any other planted case ran without load. Note: bench-2 ran against `a5bf1c013`; `e3b1d59d70f6` changes README text only (verify with `git diff a5bf1c013 e3b1d59d70f6 --stat`), so the figures stand for this head's code.
5. **The figures in the READMEs match bench-2 or the designer's own runs** they cite (spot-check three cells).
6. **Hygiene.** `git diff --name-only 085b4391c 3da7242f4461` names only the ticket's allowed paths (tests/acceptance/W1-02/test_w1_02_guard_hook.py, tests/acceptance/W1-02/README.md, tests/acceptance/W1-05/test_w1_05_live_hooks.py, tests/acceptance/W1-05/README.md, tests/acceptance/W2-57/test_w2_57_designer_read_p95.py, tests/acceptance/W2-57/README.md); compare as paths (`Path.is_relative_to`), not strings.

## Running pytest (optional; read-only)
Only through the heavy slot, with a TMPDIR outside the repository and outside ~/gov-os-runs, for example:
```
env TMPDIR=/tmp/w2-111-au1-tmp PYTHONUSERBASE=/home/usain/.local HOME=/tmp/w2-111-au1-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-111/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <node ids> -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
(create the two /tmp folders first; they are outside the repository). A resource gate's refusal is a wait, not a refusal. The lead's own run on this head: `.gov-runtime/scratch/lead/log/lead-cases-3.log` (15 passed, load ~5.6).

## Rules
- Reads are open (the whole repository, history). Refused: secrets and keys; the held-out qualification material's contents; the hidden half of any evaluation set; never open the evaluation sets' root or any hidden or memory-verdict folder.
- No `gov retrieve`, no `gov context` (you are in the sandbox): search with the Read and Grep tools, and search again once in other words if the first does not answer.
- **A refusal is reported, never worked around** (DEC-1142 (9)): if the guard, the sandbox or a hook refuses an action, do not retry it in another form. Refused twice for the same action: stop and say so.
- Never decide a finding away: report what you see.

## Return (your last message; nothing else is read)
Twelve fields, each a labelled line ("none" where nothing):
task: / status: (DONE or BLOCKED) / work_completed: / files_changed: (none) / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then the verdict block, fenced exactly:
```verdict
verdict: PASS | FAIL
probed_commit: 3da7242f4461
checks: 1 <holds|fails>; 2 ...; 3 ...; 4 ...; 5 ...; 6 ...
findings: none | - <severity> <file:line> <what>
```
Then `guard_refusals: none | - <time> | <command form> | <the reason given> | true or false-positive`.
