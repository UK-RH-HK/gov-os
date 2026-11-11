---
id: EXP-002-hook-limit
type: research
status: ACTIVE
state_class: EVIDENCE
decisions: [DEC-580, DEC-587]
sources: [DEC-160, DEC-164, DEC-578, DEC-580, DEC-587, DEC-590, DEC-784, DEC-827, DEC-1083, EXP-hook-time-limit, W2-H052, W2-M347, W2-L328]
---

# Evidence record: what Claude Code does with a hook that runs past its time limit (EXP-002, hook-limit round)

**Status of this file: skeleton.** Written by the research session of ticket DAEO-6ox0 (W2-40), round 1 (script
round). It holds the question, the method, the commands and the facts read from the repository. **Measurements,
Uncertainty and Conclusion are empty on purpose:** the cases are run by the ticket lead outside the sandbox (the
research sandbox has no model API), and a second, fresh research session fills those headings from the results.
No figure below is measured; every number is a value read from a file, with its path and line.

## Question

What does Claude Code (the harness, `~/.local/bin/claude`, version 2.1.322 on the day of writing) do with a hook
that runs past its configured time limit: is the call allowed, denied or failed; how long does it take; is the
hook's process ended or left running? At 5 s, at the limit this repository uses (60 s), with no limit set, and
for the post-call (PostToolUse) and Stop events.

## Decision it feeds

DEC-580 and DEC-587: whether the guard's own deadline (20 s) sits below the harness's measured limit, and whether
the other hook programs need a deadline of their own. Rows W2-H052 (the harness limit is measured and the guard's
deadline sits below it), W2-M347 (other hook programs keep no deadline) and W2-L328 (a deadline for post-call
programs, after an experiment) of `docs/plan/WAVE_2_LIST.md` (lines 241, 599, 985).

## Stop rule

The five mandatory cases measured twice each (by the lead) and the optional ones once. A case that cannot be
measured is "not measured" with its reason, never filled in. The script round (this file's author) stops when the
script, its README and this skeleton are committed.

## Method

- `run_hook_limit.py` (this folder) builds, per case and run, one throwaway project under `--base` whose
  `.claude/settings.json` registers one hook and nothing else, outside every git repository; starts one
  `claude -p` session (`--output-format stream-json --verbose --allowedTools "Bash"`, plus
  `--setting-sources project` when `claude --help` names it, and `--model`) with every `CLAUDE*` and `GOV_*`
  variable removed (DEC-784's way), a wall limit of the hook's sleep + 60 s, in the project's folder.
- The prompt asks for exactly one bash command: `touch <project>/ran.txt`.
- The hook is a shell command that writes `started <epoch>` to `<project>/hook.log` first, then `tick <epoch>` once
  a second for its sleep time, then `finished <epoch>`, then exits with its code (0, or 2 with a message on stderr).
- Per case and run the script writes one JSON line (fields explained in `README.md`): configuration, harness
  version, the time from the hook's `started` to the call having run (mtime of `ran.txt`), the session's wall
  time, whether `finished` appears and the last tick's offset (hook process ended or left running, and when),
  whether `ran.txt` exists, the tool result's `is_error` and its first 300 characters, the final result's first 300
  characters. The raw stream is never kept.
- Cases (README table): `pre-control-5`, `pre-allow-5`, `pre-deny-5`, `pre-allow-60`, `pre-deny-60` (mandatory,
  runs a and b); `pre-nolimit` (sleep 130 s), `post-5`, `stop-5` (optional, once).
- Reading rule: `hook_process` is derived from the log after a wait of `started` + sleep + 3 s; "ran to its end"
  means the harness did not end the hook, not that the session waited for it.

## Commands to be run (by the lead, outside the sandbox; each one case and run)

```
python3 experiments/EXP-002/run_hook_limit.py --case <case> --run <a|b> --base <dir outside every repository> --out <dir> --model <model id>
```

Mandatory, each with `--run a` then `--run b`: `pre-control-5`, `pre-allow-5`, `pre-deny-5`, `pre-allow-60`,
`pre-deny-60`. Then once with `--run a`: `pre-nolimit`, `post-5`, `stop-5`. `--dry-run` prints a case's plan.
A hung session is stopped by the pid the script printed (`tools/proc.sh`), never by a name match.

Commands actually run, with dates: *(to be filled from the results)*

## Sources

Earlier measurement (the model for this round):

- `docs/research/EXP-hook-time-limit.md` (DEC-578; 2026-10-09; Claude Code 2.1.288): with a PreToolUse limit of 5 s
  and a hook that sleeps 25 s, the call was allowed and the hook's refusal was lost (table at lines 27 to 31; the
  "Limits of this evidence" paragraph at line 47 lists what was not observed: no limit set, several hooks on one
  call, interactive mode, other hook events). Its script: `.gov-runtime/scratch/lead/ref/exp-hook-timeout.py`
  (65 lines; the lead's scratch copy of the orchestrator's working file `exp-hook-timeout.py`, which
  `EXP-hook-time-limit.md:55` says is kept with the orchestrator's working files).

Decisions (`docs/DECISION_REGISTER.md`):

- DEC-578 (line 6219): the delegated experiment, and the order to set an explicit limit.
- DEC-580 (line 6252): the guard's hook program keeps its own deadline of 20 s; hook entries carry
  `"timeout": 60` here and in the kernel template; the `gov doctor` check that the configured limit is above the
  guard's deadline goes on the Wave 2 list (line 6257).
- DEC-587 (line 6318): the programs that run after a tool call get no deadline in Wave 1; package DP-12 (a) puts
  them on the Wave 2 list "with an experiment first on what the harness does at their limit" (line 6324).
- DEC-590 (line 6341): DEC-587 accepted by the owner.
- DEC-160 (line 1457) and DEC-164 (line 1505): EXP-002 is the Wave 2 sandbox experiment id; this round shares the
  folder, not the subject. DEC-827 (line 9042): one experiments folder per research ticket, `experiments/EXP-00n/**`.
- DEC-784 (line 8600): the fixture removes every `CLAUDE*` variable before launching a session.
- DEC-1083 (line 13500): named by the lead's brief for the commit's trailers (`Implements: DEC-160, DEC-1083`).
  Read at lines 13500 to 13527: it decides nothing about hook limits, so no hook-limit claim rests on it.

Claude Code's own documentation on hook time limits was **not read** in this round (the brief asks for the
repository's knowledge and the measurement; `claude --help` for 2.1.322 names `--setting-sources` and
`--include-hook-events` and says nothing of a default hook limit). The second research session may add it.

## Guard facts, read from the files (not measured)

| Fact | Path and line |
|---|---|
| PreToolUse entry of this repository's settings: `"timeout": 60` | `.claude/settings.json:10` |
| The other four entries, each `"timeout": 60`: PreCompact (line 21), SessionStart (line 33), Stop (line 44), SubagentStop (line 55). **No PostToolUse entry** in this settings file (DEC-580 line 6258 names PostToolUse and PostToolUseFailure among the five entries of 2026-10-09) | `.claude/settings.json:21, 33, 44, 55` |
| The kernel template carries `"timeout": 60` on seven entries: preToolUse (8), postToolUse (16), postToolUseFailure (24), sessionStart (32), stop (39), preCompact (46), subagentStop (53) | `template/.rulesync/hooks.jsonc:8, 16, 24, 32, 39, 46, 53` |
| The PreToolUse command is a shell wrapper around the guard program; every failure of the wrapper ends with exit 2 ("refused") | `.claude/settings.json:9`; `template/.rulesync/hooks.jsonc:7` |
| The guard program arms `signal.alarm(20)` first thing in `main()` | `.claude/hooks/pretooluse.py:981-982` |
| The deadline's answer is a deny: "the guard could not decide in 20 seconds, so the call is refused" | `.claude/hooks/pretooluse.py:955-956` |
| The program's docstring: "Fail closed: an error or the 20-second deadline refuses." Note the same docstring says the product's full guard (`template/governance/kernel/hooks/pretooluse.py`, `src/gov/guard/`) is built but **not wired here**; the wired program is this simpler one | `.claude/hooks/pretooluse.py:45-47` |
| The log's own deadline `CALLS_SECONDS = 2`, started after the decision is made | `.claude/hooks/pretooluse.py:105, 215-222` |
| The git look-up inside the guard's decision: `_LOOKUP_S = 15` | `src/gov/guard/decide.py:771, 800` |
| The programs this settings file wires after the PreToolUse one (`precompact.py`, `sessionstart.py`, `stop.py`, `subagentstop.py` under `template/governance/kernel/hooks/`) run through `gov -E` (`exec`), and their commands carry no deadline of their own. `posttooluse.py` is wired only in the template (`hooks.jsonc:15, 23`). Whether any of these programs sets an internal deadline was not searched; DEC-587 says the programs after a call get none in Wave 1 | `.claude/settings.json:20, 32, 43, 54`; `template/.rulesync/hooks.jsonc:15, 23, 31, 38, 45, 52`; DEC-587 line 6324 |

The configured limit (60 s) sits above the guard's deadline (20 s) by 40 s on paper. Whether the harness's real
limit for a hook with `"timeout": 60` is 60 s, how long the harness takes to act at it, and what it does, is what
this experiment measures.

## Measurements

*(empty: to be written from the lead's JSON lines, one row per case and run; estimates marked "est." with how)*

## Uncertainty

*(empty: to be written from the results: one harness version; one tool (Bash); one hook per call; headless mode;
model-dependent retries; clock and load effects; managed settings not switched off by `--setting-sources`)*

## Conclusion

*(empty: the verdict in two lines; draft KPI lines, each with `verify`; residuals)*
