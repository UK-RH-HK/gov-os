---
id: EXP-002-hook-limit
type: research
status: ACTIVE
state_class: EVIDENCE
decisions: [DEC-580, DEC-587]
sources: [DEC-160, DEC-164, DEC-578, DEC-580, DEC-587, DEC-590, DEC-784, DEC-827, DEC-1083]
---

# Evidence record: what Claude Code does with a hook that runs past its time limit (EXP-002, hook-limit round)

Ticket DAEO-6ox0 (W2-40). Round 1 (script round) wrote the script, README and a skeleton; the ticket lead ran the
cases outside the sandbox; this is round 2 (record round), written from the thirteen result lines now in
`experiments/EXP-002/results/` (copies, unchanged, of the lead's lines). Every number in the Measurements table is
copied from those lines. Nothing here was measured by the record's author; no session was started.

## Question

What does Claude Code (the harness, `~/.local/bin/claude`, version 2.1.322) do with a hook that runs past its
configured time limit: is the call allowed, denied or failed; how long does it take; is the hook's process ended or
left running? At 5 s, at the limit this repository uses (60 s), with no limit set, and for the post-call
(PostToolUse) and Stop events.

## Decision it feeds

DEC-580 and DEC-587: whether the guard's own deadline (20 s) sits below the harness's measured limit, and whether
the other hook programs need a deadline of their own. Rows W2-H052 (the harness limit is measured and the guard's
deadline sits below it), W2-M347 (other hook programs keep no deadline) and W2-L328 (a deadline for post-call
programs, after an experiment) of `docs/plan/WAVE_2_LIST.md` (lines 241, 599, 985).

## Stop rule

The five mandatory cases measured twice each (by the lead) and the optional ones once. A case that cannot be
measured is "not measured" with its reason, never filled in. All thirteen runs exist; no case is missing.

## Method

- `run_hook_limit.py` (this folder) builds, per case and run, one throwaway project under `--base` whose
  `.claude/settings.json` registers one hook and nothing else, outside every git repository; starts one
  `claude -p` session (`--output-format stream-json --verbose --allowedTools "Bash"`, plus
  `--setting-sources project`, and `--model`) with every `CLAUDE*` and `GOV_*` variable removed (DEC-784's way), a
  wall limit of the hook's sleep + 60 s, in the project's folder. Every line records `setting_sources_flag: true`.
- The prompt asks for exactly one bash command: `touch <project>/ran.txt`.
- The hook is a shell command that writes `started <epoch>` to `<project>/hook.log` first, then `tick <epoch>` once
  a second for its sleep time, then `finished <epoch>`, then exits with its code (0, or 2 with a message on stderr).
- Per case and run the script writes one JSON line (fields explained in `README.md`): the configuration, the
  harness version, the time from the hook's `started` to the call having run (mtime of `ran.txt`), the session's
  wall time, whether `finished` appears and the last tick's offset, whether `ran.txt` exists, the tool result's
  `is_error` and its first 300 characters. The raw stream was never kept.
- Cases: `pre-control-5`, `pre-allow-5`, `pre-deny-5`, `pre-allow-60`, `pre-deny-60` (mandatory, runs a and b);
  `pre-nolimit` (sleep 130 s), `post-5`, `stop-5` (optional, once).
- Reading rule: `hook_process` is derived from the log after a wait of `started` + sleep + 3 s; "ran to its end"
  means the harness did not end the hook, not that the session waited for it.
- **What a line's text fields are worth.** `tool_text_head` is the harness's own tool result and is the evidence of
  allowed or denied. `result_head` is the model's paraphrase of what happened and is not evidence (for example
  `pre-control-5-b.json` has the model saying the hook was "configured in `.../hook.log`", which is not so).

## Commands actually run (by the lead, outside the sandbox)

Date 2026-11-11. The sessions started between 20:56:30 UTC (`pre-control-5` a, `start_epoch` 1794430590.579) and
21:08:19 UTC (`stop-5` a, `start_epoch` 1794431299.475), in this order, one call per case and run: `pre-control-5`
a, b; `pre-allow-5` a, b; `pre-deny-5` a, b; `pre-allow-60` a, b; `pre-deny-60` a, b; then `pre-nolimit` a, `post-5`
a, `stop-5` a. Each command (per the lead's brief; this record's author did not run it):

```
env PYTHONDONTWRITEBYTECODE=1 python3 /home/usain/gov-os-worktrees/W2-40/experiments/EXP-002/run_hook_limit.py --case <case> --run <a|b> --base /tmp/gov-os-lead-W2-40/hook-exp --out /home/usain/gov-os-worktrees/W2-40/.gov-runtime/scratch/lead/exp/results --model claude-haiku-4-5-20251001
```

Start times (UTC, 2026-11-11, converted from `start_epoch`): `pre-control-5` a 20:56:30, b 20:56:41; `pre-allow-5` a
20:56:48, b 20:57:22; `pre-deny-5` a 20:57:53, b 20:58:28; `pre-allow-60` a 20:58:59, b 21:00:39; `pre-deny-60` a
21:02:14, b 21:03:53; `pre-nolimit` a 21:05:30; `post-5` a 21:07:48; `stop-5` a 21:08:19. No case was re-run; no
session failed (every line has `session: completed`, `exit_code: 0`, `stderr_head` empty); no output was edited. The
measured sessions ran in projects outside the repository, with `--setting-sources project`, with every `CLAUDE*`
and `GOV_*` variable removed; the lead's own session ran with the repository's guard hook active. The throwaway
projects were removed afterwards. This record's author ran no suite and no `gov` command; the one check it made
of this worktree: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-40/src python3 -c "import gov; print(gov.__file__)"`
printed `/home/usain/gov-os-worktrees/W2-40/src/gov/__init__.py`.

## Sources

Earlier measurement (the model for this round):

- `docs/research/EXP-hook-time-limit.md` (DEC-578; 2026-10-09; Claude Code 2.1.288): with a PreToolUse limit of 5 s
  and a hook that sleeps 25 s, the call was allowed and the hook's refusal was lost (table at lines 27 to 31); its
  "Limits of this evidence" paragraph (lines 47 to 51) lists what was not observed: no limit set, several hooks on
  one call, interactive mode, other hook events. This round repeats its three cases on 2.1.322 (`pre-allow-5`,
  `pre-deny-5`, `pre-control-5`) and adds the no-limit, 60 s, PostToolUse and Stop cases.

Decisions (`docs/DECISION_REGISTER.md`):

- DEC-578 (line 6219): the delegated experiment, and the order to set an explicit limit.
- DEC-580 (line 6252): the guard's hook program keeps its own deadline of 20 s; hook entries carry
  `"timeout": 60` here and in the kernel template; the `gov doctor` check that the configured limit is above the
  guard's deadline goes on the Wave 2 list (line 6257).
- DEC-587 (line 6318): the programs that run after a tool call get no deadline in Wave 1; package DP-12 (a) puts
  them on the Wave 2 list "with an experiment first on what the harness does at their limit" (line 6324).
- DEC-590 (line 6341): DEC-587 accepted by the owner.
- DEC-160 (line 1457) and DEC-164 (line 1505): EXP-002 is the Wave 2 sandbox experiment id; this round shares the
  folder, not the subject. DEC-827 (line 9042): one experiments folder per research ticket, `experiments/EXP-00n/**`
  (it also says the evidence records move there).
- DEC-784 (line 8600): the fixture removes every `CLAUDE*` variable before launching a session.
- DEC-1083 (line 13500): cited only because the lead's brief names it in the commit's `Implements:` trailer; it
  decides nothing about hook limits, so no hook-limit claim rests on it.

The harness's own documentation, read in this round (round 1 had not read it): `https://code.claude.com/docs/en/hooks`,
fetched 2026-11-11 through WebFetch, which summarises the page with a small model; only the first 100,000 of the
page's 293,021 characters were covered, and the version of the documentation is not stated against 2.1.322. As
summarised: the `timeout` field is "seconds before canceling"; defaults "600 for `command`, `http`, and `mcp_tool`";
Claude Code "cancels a `command` ... hook that reaches its `timeout`, discarding the hook's output, so on most events
a timed-out hook renders no decision"; "on `PreToolUse`, a timed-out `command` ... hook doesn't block the tool call";
and `onFailure: "block"` on a `command` or `http` hook blocks the call when it times out. The measurements below
agree with the first, third and fourth points (and do not contradict the second: no `timeout` was set and the hook
ran 130.26 s). `onFailure` was **not measured** in this experiment.

## Guard facts, read from the files (not measured)

| Fact | Path and line |
|---|---|
| PreToolUse entry of this repository's settings: `"timeout": 60` | `.claude/settings.json:10` |
| The other four entries, each `"timeout": 60`: PreCompact (line 21), SessionStart (line 33), Stop (line 44), SubagentStop (line 55). **No PostToolUse entry** in this settings file (DEC-580 line 6258 names PostToolUse and PostToolUseFailure among the five entries of 2026-10-09) | `.claude/settings.json:21, 33, 44, 55` (entries start at lines 4, 15, 26, 38, 49) |
| The kernel template carries `"timeout": 60` on seven entries: preToolUse (8), postToolUse (16), postToolUseFailure (24), sessionStart (32), stop (39), preCompact (46), subagentStop (53) | `template/.rulesync/hooks.jsonc:8, 16, 24, 32, 39, 46, 53` |
| The PreToolUse command is a shell wrapper around the guard program; every failure of the wrapper ends with exit 2 ("refused") (as read by round 1; line 9 not re-read in round 2) | `.claude/settings.json:9`; `template/.rulesync/hooks.jsonc:7` |
| The guard program arms `signal.alarm(20)` first thing in `main()` | `.claude/hooks/pretooluse.py:981-982` |
| The deadline's answer is a deny: "the guard could not decide in 20 seconds, so the call is refused". The guard's answers (the deny too) are a JSON `permissionDecision` printed with exit 0, not an exit 2 | `.claude/hooks/pretooluse.py:955-956`; `:949-952` |
| The program's docstring: "Fail closed: an error or the 20-second deadline refuses." The same docstring says the product's full guard (`template/governance/kernel/hooks/pretooluse.py`, `src/gov/guard/`) is built but **not wired here**; the wired program is this simpler one | `.claude/hooks/pretooluse.py:45-47` |
| The log's own deadline `CALLS_SECONDS = 2`, started after the decision is made | `.claude/hooks/pretooluse.py:105, 215-222` |
| The git look-up inside the guard's decision: `_LOOKUP_S = 15` | `src/gov/guard/decide.py:771, 800` |
| The programs this settings file wires after the PreToolUse one (`precompact.py`, `sessionstart.py`, `stop.py`, `subagentstop.py` under `template/governance/kernel/hooks/`) run through `gov -E` (`exec`), and their commands carry no deadline of their own. `posttooluse.py` is wired only in the template (`hooks.jsonc:15, 23`). Whether any of these programs sets an internal deadline was not searched; DEC-587 says the programs after a call get none in Wave 1 | `.claude/settings.json:20, 32, 43, 54`; `template/.rulesync/hooks.jsonc:15, 23, 31, 38, 45, 52`; DEC-587 line 6324 |

## Measurements

One row per case and run, every figure copied from the line `results/<case>-<run>.json`. "Time to the call" is the
mtime of `ran.txt` less the hook's `started` (so it includes the `touch` itself, a few hundredths of a second). For
PostToolUse and Stop the hook starts after the call, so the figure is negative and means "the call ran first". The
"hook's process" column gives the last tick's offset for a hook that never wrote `finished`; 4 ticks (5 s cases) or
59 ticks (60 s cases) had been written. "Outcome": allowed = the call ran; denied = the harness refused it.

| Case | Run | Hook event | Limit (s) | Hook sleep (s) | Would exit | Outcome | Time to the call (s) | The hook's process | Session wall (s) |
|---|---|---|---|---|---|---|---|---|---|
| pre-control-5 | a | PreToolUse | 5 | 0 | 2 | denied | not run | ran to its end at 0.0 s | 5.88 |
| pre-control-5 | b | PreToolUse | 5 | 0 | 2 | denied | not run | ran to its end at 0.0 s | 6.48 |
| pre-allow-5 | a | PreToolUse | 5 | 25 | 0 | allowed | 5.05 | ended at 4.01 s | 10.35 |
| pre-allow-5 | b | PreToolUse | 5 | 25 | 0 | allowed | 5.05 | ended at 4.01 s | 10.25 |
| pre-deny-5 | a | PreToolUse | 5 | 25 | 2 | allowed | 5.04 | ended at 4.01 s | 10.15 |
| pre-deny-5 | b | PreToolUse | 5 | 25 | 2 | allowed | 5.05 | ended at 4.01 s | 10.06 |
| pre-allow-60 | a | PreToolUse | 60 | 90 | 0 | allowed | 60.01 | ended at 59.14 s | 64.87 |
| pre-allow-60 | b | PreToolUse | 60 | 90 | 0 | allowed | 60.06 | ended at 59.14 s | 64.38 |
| pre-deny-60 | a | PreToolUse | 60 | 90 | 2 | allowed | 60.07 | ended at 59.13 s | 65.34 |
| pre-deny-60 | b | PreToolUse | 60 | 90 | 2 | allowed | 60.06 | ended at 59.14 s | 65.16 |
| pre-nolimit | a | PreToolUse | none | 130 | 0 | allowed | 130.3 | ran to its end at 130.26 s | 134.96 |
| post-5 | a | PostToolUse | 5 | 25 | 0 | allowed (the call had run) | -0.01 | ended at 4.01 s | 9.78 |
| stop-5 | a | Stop | 5 | 25 | 0 | allowed (the call had run) | -1.92 | ended at 4.01 s | 9.63 |

Other fields of the lines that bear on the reading, the same in all thirteen unless said:

- Harness version `2.1.322`; model `claude-haiku-4-5-20251001` (the model requested and the model the session
  reported are the same); `hook_starts` 1 (the hook ran once in every run, so the offsets are not ambiguous);
  `tool_uses` 1 and `tool_results` 1; `pipes_open_10s_after_exit` false (no process held the session's pipes after it
  ended).
- In the eight runs with a 5 s or 60 s PreToolUse limit and a sleep above it, `tool_is_error` is false and
  `tool_text_head` is "(Bash completed with no output)": the model was given an ordinary result. In the two control
  runs `tool_is_error` is true and the text is "PreToolUse:Bash hook error: [...]: refused by the experiment hook".
- `system_subtypes` holds only `thinking_tokens` in every line: no message of the stream names the timeout.
- The session ended after the hook's start by (`session_end_after_hook_start_s`): control 3.14 and 3.59; 5 s PreToolUse
  7.49 to 7.76; 60 s PreToolUse 62.12 to 62.92; `pre-nolimit` 132.38; `post-5` 7.38; `stop-5` 5.63. With a limit set,
  the session did not wait for the 25 or 90 s the hook would have run; with none set it waited the hook's 130 s.
- Last tick offsets of 4.01 s (5 s cases) and 59.13 to 59.14 s (60 s cases) show that no further tick was written;
  the next tick would have come at about 5.0 s and 60.1 s. Every one of the eight limit runs has `hook_finished`
  false after the log wait of sleep + 3 s.

## Uncertainty

- One harness version (2.1.322); the earlier run (2.1.288) agrees on the 5 s case, so the behaviour held across two
  versions on this machine, but no other version was run.
- One tool (Bash); one model (`claude-haiku-4-5-20251001`); headless `-p` only, not an interactive session.
- One hook per call. Several hooks on one call (whether the limit counts each hook alone or all together, and whether
  an answer from another hook changes the outcome) was not run.
- n = 2 per mandatory case, n = 1 for `pre-nolimit`, `post-5`, `stop-5`. The two runs agree to 0.01 s at 5 s
  (5.04 to 5.05 s) and to 0.06 s at 60 s (60.01 to 60.07 s); the optional cases rest on one run each.
- The hook was a shell loop, not the guard's own program. The guard's program (its start-up time, its decision time,
  how its `signal.alarm` behaves under load) was **not timed** here.
- Tick granularity is one second. "Ended at the limit" is read from the last tick before the limit (4.01 s, 59.14 s)
  and the call's time after it (5.05 s, 60.01 s); the end of the hook's process is therefore placed between the last
  tick and the call, not read to better than that. The "time to the call" is the file's mtime and includes the
  `touch`; the harness's own act at the limit is at or just before it.
- Clock and load: wall times come from one machine, run serially, one case after another; the lead's own session
  and other processes were running; no load was controlled or measured.
- Managed settings (`/etc/claude-code/`) and anything not a setting source are not switched off by
  `--setting-sources project`; the lines do not show whether any such setting applied. The shell hooks' behaviour
  matches the documentation, so none is thought to have mattered, but this is not shown.
- Whether the hook's own child processes (the `sleep` in the loop) survive its shell's end was not measured; only the
  loop's ticks stopping and the pipes being free are measured.
- Not run: several hooks on one call; an interactive session; PreCompact, SessionStart, SubagentStop; `onFailure:
  "block"`; a hook that refuses by JSON output (as the guard does) instead of exit 2; a Stop or PostToolUse hook that
  would refuse (the cases run would exit 0); a default limit above 130 s (`pre-nolimit` bounds it from below only:
  the harness waited the whole 130.26 s, and the documentation, as summarised, says 600 s).

## Conclusion

At its limit the harness (2.1.322, Bash, headless) ends a PreToolUse hook's process and lets the call run, even for a hook that would have refused: the call ran 5.04 to 5.05 s after the hook started with a 5 s limit and 60.01 to 60.07 s with a 60 s limit, in 8 of 8 runs.
With no `timeout` set the harness waited the whole 130 s (the call ran at 130.3 s); a PostToolUse or Stop hook past 5 s was ended at its limit and changed nothing the model saw.

## S1

The measured limit for the repository's value is **60.01 to 60.07 s** from the hook's `started` to the call's
running (`pre-allow-60` a 60.01, b 60.06; `pre-deny-60` a 60.07, b 60.06), beside the guard's own deadline of **20 s**
(`.claude/hooks/pretooluse.py:982`, `signal.alarm(20)`; the refusal it gives, lines 955-956) and the entry limit of
**60 s** (`.claude/settings.json:10`). 20 s is below the measured limit, by about 40 s: **S1 is met.**

## The five-line list for rows W2-H052, W2-M347 and W2-L328

1. **PreToolUse past its limit:** the call is allowed (8 of 8 runs at 5 s and 60 s), the call ran 5.04 to 5.05 s
   (limit 5 s) and 60.01 to 60.07 s (limit 60 s) after the hook began, and the model got an ordinary result with no
   error. A refusal that comes after the limit is lost: the four runs whose hook would have exited 2 (`pre-deny-5`
   a, b; `pre-deny-60` a, b) all ran the call. The control (refusal at once, `pre-control-5`) denied in both runs, so
   the loss comes from the time, not from the hook's refusal being unreadable.
2. **The hook's process:** ended, not left running. In the eight limit runs no `finished` was written (after a wait of
   sleep + 3 s), the ticks stopped at 4.01 s and 59.13 to 59.14 s, and no process held the session's pipes. Not
   measured: the hook's child processes.
3. **No limit set:** the hook ran to its end (130 ticks, `finished` at 130.26 s) and the call ran at 130.3 s, with the
   session ending 132.38 s after the hook began: the harness's default limit, if any, is above 130.26 s. (The
   documentation, as summarised in Sources, says 600 s; not measured here.)
4. **PostToolUse (5 s limit, hook sleeps 25 s):** the call had run before the hook started (-0.01 s); the hook was ended
   at the limit (ticks to 4.01 s, no `finished`); the session ended 7.38 s after the hook began and showed the model
   no error. A hook that would have exited 2 was not run.
5. **Stop (5 s limit, hook sleeps 25 s):** the hook started 1.92 s after the call ran; it was ended at the limit
   (ticks to 4.01 s, no `finished`); the session ended 5.63 s after the hook began, not 25. A hook that would have
   blocked the stop was not run.

## The guard's fail-open reading, in words an owner reads

When a guard decision takes longer than the hook's limit, the harness stops waiting, ends the guard's process, and
lets the call through: it does not refuse. This was measured (for a stand-in hook) in every run with a 5 s and a
60 s limit, including the four where the hook would have said no. That is why this repository's guard keeps its own
20 s deadline, which answers "refuse" first (`.claude/hooks/pretooluse.py:955-956, 981-982`).

What the numbers say about the margin: the harness acted at the limit it was given, to within about 0.1 s, at both 5 s
and 60 s, so a limit of 60 reads as 60. The guard's 20 s deadline is about 40 s below it, and the guard's 15 s git
look-up (`src/gov/guard/decide.py:771`) is below the 20 s. The margin is not a matter of the harness being slow to act.

What they do not say: the guard's own program was not timed here (its start-up before the alarm is armed, its decision
time, and whether its alarm fires on time under load are not measured). The control refused by exit 2; the guard
refuses by printing a JSON decision with exit 0 (`.claude/hooks/pretooluse.py:949-952`), and that form of refusal was
not run against the harness. Several hooks on one call, and an interactive session, were not run.

## Recommendation (draft KPI lines; each is a recommendation for an ACT by the owner, none is a file change made here)

- **R1 (keep the pair).** The guard's deadline stays below the entry limit: `.claude/hooks/pretooluse.py` keeps
  `signal.alarm(20)` and `.claude/settings.json` and `template/.rulesync/hooks.jsonc` keep `"timeout": 60` on the
  PreToolUse entry; `gov doctor`'s check that the entry limit is above the deadline (DEC-580, Wave 2 list) is built.
  `verify:` read the `timeout` of the PreToolUse entry in each file and the `signal.alarm` value of the guard
  program; the entry limit is greater than the alarm value; the doctor check fails when the order is reversed.
- **R2 (a deadline for the programs that can refuse).** Each hook program whose answer can refuse or block (the
  PreToolUse program; any other program the owner names after reading what each can block) carries a deadline of its
  own, below its entry limit, and answers "refuse" at it. A program that cannot refuse a call that has run
  (PostToolUse, PostToolUseFailure, as DEC-587 says) needs no deadline for safety: measured, it is ended at its limit
  and nothing the model sees changes. Whether PreCompact, SubagentStop or Stop can block, and what the harness does
  at their limit if they do, is not measured. `verify:` for each program wired in `.claude/settings.json` and
  `template/.rulesync/hooks.jsonc`, a table of "can block: yes or no" read from the program; each "yes" program has an
  alarm or timeout value below its entry limit, and a test that makes it sleep past it gets a refusal.
- **R3 (an explicit `timeout` on every entry).** Every hook entry carries a `timeout`; none is left to the default.
  Unset, the harness waited the whole 130 s (and the documentation, as summarised, says 600 s), a long time for a
  guard to hold a call and then, at its limit, let it through. `verify:` every entry in `.claude/settings.json` (5
  now) and in `template/.rulesync/hooks.jsonc` (7 now) has a `timeout` key; a `gov check` or doctor line fails on an
  entry without one.
- **R4 (an experiment on `onFailure: "block"` first).** Before any change, a further case (a PreToolUse hook with a
  limit and `onFailure: "block"`, sleeping past it) is run on this harness version to see whether the harness itself
  refuses at the limit; if so, the owner may weigh it for the guard's entry as a second fail-closed layer under the
  guard's own deadline. This needs a new case in `run_hook_limit.py` and a run outside the sandbox; the script has no
  such case now. `verify:` a result line of the same form, `outcome` denied, `ran_txt_exists` false.

## Residuals

- Not measured (see Uncertainty): several hooks on one call; an interactive session; PreCompact, SessionStart,
  SubagentStop; `onFailure: "block"`; a refusal in JSON with exit 0 past the limit; a Stop or PostToolUse hook that
  would refuse; the default limit above 130 s (only bounded from below); the guard's own program timed under the
  harness; the hook's child processes; a harness version other than 2.1.322; another model or tool.
- The documentation was read through a summary of its first 100,000 characters only.
- The record's place is `experiments/EXP-002/` (DEC-827). Still saying `docs/research/EXP-002`: ticket
  `.tickets/DAEO-6ox0.md` line 66 (Allowed paths: `docs/research/EXP-002/**`, `experiments/EXP-002/**`) and line 73
  ("copied to `docs/research/EXP-002/` by the CTO at close"); `docs/plan/WAVE_2_WBS.md` line 987 (the W2-40 card's
  Allowed paths, same two entries). Found by two searches (the ticket folder, then `docs/plan`); other places were not
  searched.
- The rows W2-H052, W2-M347 and W2-L328 can be answered from the five-line list above; whether they close, and
  what the owner decides on R1 to R4, is for the CTO and the owner.
