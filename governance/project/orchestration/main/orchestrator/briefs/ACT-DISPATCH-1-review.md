# The review of ACT-DISPATCH-1 and ACT-IDLE-GUARD-2: the dispatcher's own lead cap, one idle item per cause, the forecast by measured load; the idle guard's F1-F3 (DEC-1140 (1)(a), (2))

You are a fresh, read-only independent reviewer of two ACTs before they go to the owner (DEC-1104 (2): rehearsal, a
READY review and matching hashes). READY is computed by `verdict.py` from your block, one entry per ACT.

## The ACTs
- **ACT-DISPATCH-1:** package `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/dispatch-1/ACT-DISPATCH-1.md`;
  bundle `.../drafts/dispatch-1/acts/ACT-DISPATCH-1/` (manifest sha256 `a20754dd1e9f88db984a467d65bfb2b346e7c94d61cd00b520bca99ac8351070`).
  It changes `governance/project/orchestration/tools/dispatch/dispatcher.py` and `balancer.py` (class (b), row `watchers`)
  and two test files (which make the bundle (O), by hand). Three changes: (1) `why_not` refuses a start at `max_leads`;
  (2) the idle item's cause key is the sorted waiting lines, kept until a real start or a changed key, one item per cause
  plus a 6-hour reminder (DEC-1118 H); (3) **read this first:** a job measured for 5 minutes or more counts in the CPU
  forecast at `min(phase peak, max(its 10-minute max, now, 1.0))` (`jobs-load.json`), RAM and GPU unchanged, `held_load:
  false` switches it off. Tonight the old count refused leads at "25.1 of 18" while 5 of 20 cores were busy.
- **ACT-IDLE-GUARD-2:** package `.../drafts/dispatch-1/ACT-IDLE-GUARD-2.md`; bundle `.../drafts/dispatch-1/acts/ACT-IDLE-GUARD-2/`
  (manifest `531d98c006de973fd4c17c5ca61a1b6c89f8536192036b8dd22f7625da081d0a`): `stop_idle_check.py` (the Stop hook's
  idle check, class (O)): F1-F3 of ACT-IDLE-GUARD-1's review (`governance/project/orchestration/reviews/ACT-IDLE-GUARD-1-review*.md`).
- Both were built and rehearsed by an ACT-preparation helper (`.../drafts/dispatch-1/NOTES.md`, `rehearsal.log`,
  `rehearsal-guard2.log`). The owner's word (11-11 ~23:50): the counting is fixed by this ACT, `cpu_band` stays [14, 18].

## Check
1. **Hashes and scope:** `before/` equals the live files on `w2/integrate` today; `after/` equals the described change
   and nothing else; recompute every hash in the packages, `list.txt` and `manifest.json`; neither touches
   `dispatch/launch_now.sh` (ACT-LOAD-BALANCER-A's file, queued for the operator).
2. **The forecast change (C3 care):** can it admit a lead onto a machine that then runs out of memory or loses work? Read
   the memory admission, the floor, `mem_guard` and `oom_watch` paths and say what still holds. Is the 5-minute and
   10-minute window sound for a slot that sits quiet and then bursts to its 6 workers? Is a CPU over-booking at worst a
   slowdown? One finding per real risk, judged by the two questions.
3. **The cap and the idle item:** the cap refuses only at `max_leads` and never with no cap; a lead that dies at launch
   holds a place for at most 10 minutes; the idle item is never lost for a new cause (the 7-hour idle of 11-10 must not
   recur); the reminder fires.
4. **GUARD-2:** F1-F3 as the review asked; the hook stays within its `timeout: 10` (plan 5 s, branch listing 3 s); it can
   only ever block a turn end less often for a false cause, never more often, and never fails the session.
5. **Rehearsals and class:** the red-then-green counts hold in your own clone (`tests/unit/orchestration` scoped through
   `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, one folder per
   run, `-p no:cacheprovider -o tmp_path_retention_policy=failed`); the dry tick against a planted dispatch folder (never
   the live one) shows the cap, one idle item and the admit; the classes (DISPATCH-1 (O) as built with its tests, (b) if
   code-only; GUARD-2 (O)) and routes are right.
Never start, stop or tick the live dispatcher; never write the live dispatch folder.

KPI ids for the verdict block: `act-dispatch-1` and `act-idle-guard-2`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns these ACTs.

## Write and return
- **You write nothing** in any tree; never a live dispatcher or hook file.
- No GPU, no installs, never the full suite. Single simple Bash commands (DEC-1080). Every wait by pid only
  (`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`).
  Row W2-L423's rule: under `.gov-runtime/`, commit hashes as 12 digits and none of that rule's keywords.
- Scratch budget 30 GB and 2,000,000 files and folders, in your own TMPDIR; remove your clone (`chmod -R u+w` first);
  report `du -sh` and `du -s --inodes` in `evidence`.
- The hidden-half rule holds: never open anything under `~/gov-os-eval/`, or any `hidden`, `memory-verdict` or
  `memory-verdict-2` folder.
- Refused twice for the same call: stop and say so; no third try.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields first (task, status, work_completed, files_changed, evidence, tests, discoveries, risks,
    lessons, proposed_decisions, unresolved, recommended_next_action), the sandbox and `ps` checks in `evidence`;
  - your answers to the checks;
  - every finding, with its two lines and its scope;
  - then `REVIEW_MD_BEGIN`, one review record in markdown covering both ACTs (a section each), `REVIEW_MD_END`;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "act-dispatch-1", ...}, {"kpi": "act-idle-guard-2", ...}]}`, each finding
    `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 40 minutes.
