---
type: probe
task: DAEO-6ox0
reviewer_session: 4b4d039a-3285-4d5f-8dac-6de87558bd60
implementer_session: df631877-f230-437b-91a2-9912883cb87e
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 9f71c6bc42407e3ace234e3625581eb1950a1527
---

# FULL probe of W2-40 (DAEO-6ox0) at 9f71c6bc4240: EXP-002's hook-limit record, review round 1 of at most 2

- **What was probed:** the evidence record `experiments/EXP-002/hook-limit-record.md`, its script, README and thirteen result lines, against the ticket's one live KPI line S1 (the harness's behaviour at a hook's time limit, so that the guard's deadline sits below it; DEC-1083 lifted the other three). The script round's research session wrote the script (`37320b6a5889`); the ticket lead ran the thirteen cases outside the sandbox on 2026-11-11 (Claude Code 2.1.322, `claude-haiku-4-5-20251001`); the record round's research session (`implementer_session` above) wrote the record (`6b01098c505e`); the lead merged `w2/integrate` (W2-105's land, no cited file) into the branch, giving the probed head.
- **Reviewer:** a fresh, read-only independent auditor (Opus 5.5, effort high, class C2), launched sandboxed by the lead with `launch_worker.sh`; brief `.gov-runtime/scratch/lead/briefs/rev-1.md` (with `governance/project/briefs/JUDGEMENT.md` word for word); tripwire clean; sandbox trial file absent. READY computed by `verdict.ready`: True, no blocking finding. The lead's judgement: pass.
- **The reviewer's record follows, as returned.**

**Verdict: S1 passes, with no findings.** I wrote nothing in any tree: `git status --porcelain` is empty, and HEAD was `9f71c6bc4240` at the start and at the end.

```
task: DAEO-6ox0 — independent read-only review (round 1 of ≤2) of W2-40's EXP-002 hook-limit record at 9f71c6bc4240, against S1
status: DONE — S1 passes; no finding blocks, and none was raised
work_completed: sandbox check; identity and HEAD check; read the ticket, the record, the script, the README and all 13 result lines; compared each committed line byte for byte with the lead's raw line; checked every row and figure of Measurements against its line; checked every cited path:line, the DEC heading lines, the Wave 2 list rows and the earlier EXP record at the probed head; checked that the merge 6b01098c505e→9f71c6bc4240 changed no cited file; searched EXP-002 for secrets
files_changed: none
evidence: (1) Sandbox check: (a) the write to /home/usain/gov-os-worktrees/.sandbox-trial-DAEO-6ox0 FAILED ("OSError: [Errno 30] Read-only file system"); (b) `git hash-object -w --stdin` printed 1ae28402a109, and `git update-index --refresh` exited 0. (2) `printenv` → independent-auditor, DAEO-6ox0. (3) HEAD 9f71c6bc4240 at the start and at the end. (4) `PYTHONPATH=/home/usain/gov-os-worktrees/W2-40/src python3 -c "import gov; print(gov.__file__)"` → /home/usain/gov-os-worktrees/W2-40/src/gov/__init__.py. (5) `cmp` of all 13 committed results against .gov-runtime/scratch/lead/exp/results/ → identical; that folder holds exactly 13 files. (6) The ticket's diff against w2/integrate is the 16 paths under experiments/EXP-002/ only. (7) `git diff --stat 6b01098c505e 9f71c6bc4240` over every cited file, the ticket and experiments/ → empty. (8) Commits: 6b01098c505e (Task: DAEO-6ox0, Role: research, Implements: DEC-160, DEC-1083); 9f71c6bc4240 (Task: DAEO-6ox0, Role: orchestrator). (9) Session id 4b4d039a-3285-4d5f-8dac-6de87558bd60, read from the harness's task path. (10) Guard refusals: 0. (11) Searches: one secret-pattern search over experiments/EXP-002/; its only hits were the field name "thinking_tokens". No second search was needed.
tests: none run (a reviewer re-runs nothing; there is no model API)
discoveries: (a) /etc/claude-code/ does not exist on this machine (checked 2026-11-11, same day as the runs). So the record's open point that managed settings might have applied can be narrowed to "none present at review time". (b) DEC-580 line 6258 lists the five entries of 2026-10-09 as PreToolUse, PostToolUse, PostToolUseFailure, PreCompact and SessionStart. Today's .claude/settings.json has PreToolUse, PreCompact, SessionStart, Stop and SubagentStop, and no PostToolUse. The record already notes this; it matters for R3's counts and for which post-call programs W2-L328 covers.
risks: n = 1 for pre-nolimit, post-5 and stop-5; the record says so. The guard's own program was not timed under the harness: its start-up before signal.alarm(20) and a JSON-with-exit-0 refusal past the limit are untested. The record names both; they are not in S1.
lessons: Each line's `last_tick_offset_s` against `session_end_after_hook_start_s` is what proves the hook was ended rather than left behind. The next tick (~5.01 s / ~60.16 s) would have fallen while the session was still alive (7.5 s / 62.1 s), and none was written.
proposed_decisions: none
unresolved: W2-L328's wording ("the post-call programs carry a deadline") and the record's R2 (post-call programs need no deadline for safety) differ. The record leaves the choice to the owner; it is not a defect of S1.
recommended_next_action: ticket lead: S1 passes with nothing blocking; close W2-40 by its usual path, and take R1–R4 and the W2-L328 wording to the owner as ACT candidates.
```

`task: DAEO-6ox0`
`decisions: [DEC-580, DEC-587, DEC-578, DEC-1083, DEC-1010, DEC-1131, DEC-801, DEC-808]`

## (i) S1, word by word
- **A planted hook that sleeps past the limit:** yes. In `run_hook_limit.py`, cases pre-allow and pre-deny sleep 25 s at a 5 s limit and 90 s at a 60 s limit. The hook writes `started` first, then one tick per second.
- **The outcome the harness gave:** allowed, in 8 of 8 runs past the limit. Each line has `ran_txt_exists: true`, `tool_is_error: false` and "(Bash completed with no output)". That includes the four runs whose hook would have exited 2.
- **The time, as a number with its unit:** 5.04–5.05 s at the 5 s limit, and 60.01 / 60.06 / 60.07 / 60.06 s at the 60 s limit, the repository's own value. Each is the time from the hook's start to the call.
- **The guard's deadline recorded below the measured limit:** yes. The record cites `signal.alarm(20)` at `.claude/hooks/pretooluse.py:981-982`, the deny at :955-956 and `"timeout": 60` at `.claude/settings.json:10`. I read each at the probed head and each line is true. 20 s is below 60.01 s.
- **Other cited lines, all true at the probed head:**
  - `hooks.jsonc` 8/16/24/32/39/46/53.
  - `CALLS_SECONDS = 2` at :105 and :215-222.
  - `_LOOKUP_S = 15` at decide.py:771 and :800.
  - DEC heading lines 1457, 1505, 6219, 6252, 6318, 6341, 8600, 9042, 13500.
  - Wave 2 list lines 241, 599, 985; WBS line 987.
  - The earlier record's table at lines 27–31 and its limits at 47–51.

## (ii) A fair test
- **The control refuses and is honoured:** pre-control-5 a and b have `tool_is_error: true`, the text "PreToolUse:Bash hook error … refused by the experiment hook", and no `ran.txt`.
- **The hook really ran past its limit:** 4 and 59 ticks, the last at 4.01 s and 59.13–59.14 s, and `hook_finished: false`. The log is read only after start + sleep + 3 s, so a hook left behind would have kept ticking.
- **Nothing else could influence the setup:**
  - Every line has `setting_sources_flag: true`.
  - `clean_env()` removes every `CLAUDE*` and `GOV_*` variable.
  - The script refuses a `--base` that has a `.git` at or above it.
  - Every line's `project` is under /tmp/gov-os-lead-W2-40/hook-exp.
  - `hook_starts: 1` in every line.
  - No managed settings exist on the machine.
- **n = 2 agrees:** within 0.01 s at 5 s and within 0.06 s at 60 s.
- **Every Measurements row checked against its line:** case, limit, sleep, would-exit, outcome, time to the call, the hook's process and session wall all match. The session-end ranges match: 3.14/3.59; 7.49–7.76; 62.12–62.92; 132.38; 7.38; 5.63. All 13 UTC start times convert correctly from `start_epoch`.

## (iii) The conclusion stays within the numbers
- The Conclusion is limited to one version (2.1.322), Bash and headless mode.
- Uncertainty adds the one model, the shell hook in place of the guard's program, and the untimed guard start-up.
- `result_head` is correctly marked as the model's paraphrase and not evidence.
- R1–R4 are headed "a recommendation for an ACT by the owner, none is a file change made here".

## (iv) The three rows
The five-line list answers W2-H052, W2-M347 and W2-L328. Whatever was not measured is named "not measured": several hooks on one call, an interactive session, PreCompact, SessionStart, SubagentStop, `onFailure`, a JSON refusal, a refusing Stop or PostToolUse hook, the default limit above 130 s, the hook's child processes. Whether the rows close is left to the CTO and the owner.

## (v) What EXP-002 holds
- No secret, key or raw stream.
- The only settings content is the throwaway hook command, inside the control lines' 300-character `tool_text_head`.
- Session ids and pids are not secrets.

## What I probed and found sound
- The script's timing arithmetic: `ran.txt`'s mtime less `started`; wall time taken when the process exits, not when its pipes close.
- The case table against the README.
- The fail-open reading against the earlier 2.1.288 result.
- The merge into the branch: it touched no cited file.

## Findings
None.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}]}
```
