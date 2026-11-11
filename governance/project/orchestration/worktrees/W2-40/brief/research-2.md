# Research brief: W2-40 (DAEO-6ox0), the record round of EXP-002 (the harness's hook limit)

Template: role-research@1.0.0 (`.claude/templates/role-research.md` in your tree; read it). Written by the ticket lead (orchestrator, W2-40), 2026-11-11. Budget: projection_usd 3. You are a fresh session: the script round's session wrote the script, README and skeleton; the lead ran the cases; you write the record from the results.

## Who and where
- Role `research`, ticket `DAEO-6ox0` (W2-40), tree `/home/usain/gov-os-worktrees/W2-40`, branch `w2/W2-40`.
- First: `printenv GOV_ROLE GOV_TICKET` (expect `research`, `DAEO-6ox0`) and `git -C /home/usain/gov-os-worktrees/W2-40 rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-40`, `w2/W2-40`). Different: stop and say so.

## Step 0, the sandbox check, before any work, reported first in your return
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-6ox0','w').write('x')"` must FAIL; (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return (the form of `EMG-d4b-launched.md`, copied beside this brief). In your return, write any hash `git hash-object` prints as its first 12 digits only (row W2-L423's rule, below).

## Your writes: one folder only
You write only under `experiments/EXP-002/`, never anything else: not `.claude/`, `src/`, `template/`, `tests/`, `.tickets/`, the decision register, `docs/`, `governance/`. You change no product file and no control (settings, hook programs, guard): **a recommendation to change a limit or add a deadline goes in the record as a draft KPI line and in your `proposed_decisions`, never into a file** (controls change by ACT only). You never start a `claude -p` session (your sandbox has no model API; the measurement is done). No installs. Never copy the tree.

## Inputs
- **The results:** `/home/usain/gov-os-worktrees/W2-40/.gov-runtime/scratch/lead/exp/results/` (the lead's scratch, inside your tree): thirteen files `<case>-<run>.json`, each one JSON line written by `experiments/EXP-002/run_hook_limit.py`. Read them with the Read tool. The fields are explained in `experiments/EXP-002/README.md`.
- **How they were made:** the lead ran, outside the sandbox, on 2026-11-11 (the `start_epoch` field of each line is the start time; convert it to UTC in the record), one call per case and run, in this order: `pre-control-5` a, b; `pre-allow-5` a, b; `pre-deny-5` a, b; `pre-allow-60` a, b; `pre-deny-60` a, b; then `pre-nolimit` a, `post-5` a, `stop-5` a. The command, for each: `env PYTHONDONTWRITEBYTECODE=1 python3 /home/usain/gov-os-worktrees/W2-40/experiments/EXP-002/run_hook_limit.py --case <case> --run <a|b> --base /tmp/gov-os-lead-W2-40/hook-exp --out /home/usain/gov-os-worktrees/W2-40/.gov-runtime/scratch/lead/exp/results --model claude-haiku-4-5-20251001`. No case needed a re-run; no session failed; no output was edited. The throwaway projects under `/tmp/gov-os-lead-W2-40/hook-exp` were removed afterwards (they are gone; do not look for them). The lead's own session ran with the repository's guard hook active; the measured sessions ran in projects outside the repository with `--setting-sources project` and every `CLAUDE*`/`GOV_*` variable removed.
- **Your starting point:** the skeleton `experiments/EXP-002/hook-limit-record.md` (committed by the script round, `37320b6a5889`). Keep its question, decision, stop rule, method, sources and guard-facts sections; correct what is wrong; fill the empty headings.
- **The facts the record cites:** re-read each in your own tree and cite path and line: `.claude/settings.json` (the `"timeout": 60` entries), `.claude/hooks/pretooluse.py` (`signal.alarm(20)` and the deny answer of the deadline), `template/.rulesync/hooks.jsonc`, `src/gov/guard/decide.py` (`_LOOKUP_S`), `docs/research/EXP-hook-time-limit.md` (the 2026-10-09 run), and in `docs/DECISION_REGISTER.md` (grep `### DEC-n`; it is large) DEC-160, DEC-578, DEC-580, DEC-587, DEC-590, DEC-827, DEC-1083. Rows W2-H052, W2-M347, W2-L328 are in `docs/plan/WAVE_2_LIST.md`.
- Find what you need with the Read and Grep tools (you have no `gov retrieve` in the sandbox, DEC-1065). Search named files and folders, not the repository root. If a search does not answer, or your answer may be incomplete, search once more in your own, different words; then answer from both with path and lines, or say "not found". Two searches in all.

## What you write
1. **`experiments/EXP-002/results/`**: a copy of each of the thirteen result lines, one file per case and run, the same names (`<case>-<run>.json`), contents unchanged (the JSON lines only; no stream). Copy them by reading each and writing it with the Write tool (or one `cp` of the named files into the folder: no recursive copy of anything else).
2. **`experiments/EXP-002/hook-limit-record.md`**, the record, completed:
   - **Front matter:** `type: research`, `status: ACTIVE`, `state_class: EVIDENCE`, `decisions: [DEC-580, DEC-587]`, `sources:` the ids it cites, each resolvable (at least DEC-160, DEC-578, DEC-580, DEC-587, DEC-590, DEC-827, DEC-1083; keep others the skeleton cites only if they resolve in the register; a row id or a file name is not an id here: name those in the text).
   - **Commands actually run:** the lead's command form above, the date and the UTC time range from the lines.
   - **`Measurements`:** one table, one row per case and run: case, run, hook event, limit (s), hook sleep (s), would-exit code, outcome ("allowed" if the call ran, "denied" if the harness refused it, "failed" otherwise), time from the hook's `started` to the call having run (s, or "not run"; note that for PostToolUse and Stop the hook starts after the call, so the figure is negative and means "the call ran first"), the hook's process ("ended at <last tick offset> s" or "ran to its end at <finished offset> s"), the session's wall time (s). Every number comes from the lines, unrounded beyond what the lines hold. A case with no line is "not measured" with its reason.
   - **`Uncertainty`:** one harness version (2.1.322), one tool (Bash), one model (the one the lines name), headless `-p` only (not interactive), one hook per call, n = 2 per mandatory case and n = 1 for the optional ones, a shell hook not the guard's own program, the tick granularity (one second: "ended at the limit" is read from the last tick before the limit and the call's time after it), clock and load, managed settings not switched off by `--setting-sources`, and what was not run (several hooks on one call; an interactive session; PreCompact, SessionStart, SubagentStop; a default limit above 130 s, which `pre-nolimit` only bounds from below).
   - **`Conclusion`:** in two lines: what the harness does at a limit, with the number.
   - **The sentence S1 asks for**, in its own short section headed `S1`: the measured limit for the repository's value (the time from `started` to the call's running in the two 60 s cases, in seconds), beside the guard's deadline read from `.claude/hooks/pretooluse.py` (20 s, path and line) and the entry limit from `.claude/settings.json` (60 s, path and line), and whether 20 s is below the measured limit. If the measured limit were below 20 s, or not measured at 60 s, say so plainly and say S1 is not met; do not call it met.
   - **The rows' five-line list** (W2-H052, W2-M347, W2-L328): (1) what the harness did for a PreToolUse hook past its limit, and so what happens to a refusal that comes after the limit; (2) whether the hook's process is ended or left running; (3) what it did with no limit set; (4) the post-call event (PostToolUse); (5) the Stop event. "Not measured" for anything the lines do not hold.
   - **The guard's fail-open reading, in words an owner reads:** a guard decision slower than the hook's limit lets the call through, and the guard's own 20 s deadline (which refuses) exists to answer first; state what the numbers say about the margin, and what they do not say (the guard's own program was not timed here).
   - **Recommendation**, as draft KPI lines each with its `verify` (never a file change): for example whether the other hook programs (and the post-call ones of the template) should carry a deadline of their own below their entry limit, and whether an explicit `timeout` should always be set (the no-limit case's reading). Mark each as a recommendation for an ACT by the owner.
   - **Residuals:** what is still open (not measured), and anything that still says `docs/research/EXP-002` in the ticket text or the WBS card (the record lives under `experiments/EXP-002/`, DEC-827).
   - **It invents no number.** A claim with no line under it is "not measured".
3. Leave `run_hook_limit.py` and `README.md` as they are, unless one says something the results show to be wrong (then a one-line correction, named in your return).

## Rules
- **DEC-732, word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-40/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-40/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. (You run no test and no `gov` command in this round; quote the line anyway.)
- **DEC-820:** reads are open; (a) never read or print secrets or keys, and never print the contents of any settings file other than what the record cites by path and line; (b) never read the held-out qualification material's contents; (c) the counterpart's work on this ticket (none here: there is no acceptance folder); (d) never read the hidden half of any evaluation set (`~/gov-os-eval`). Never write in `~/gov-os-workbench`.
- **DEC-849:** the guard may refuse some reads (searches from the repository root, `governance/project/`, `.claude/`): take the refusal, never another spelling; read the named file instead; count the refusals in your return.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` and in your return write commit hashes as 12 digits, never the full 40, and never write the keywords of the secrets rule that takes a bare 40-hex string for a token.
- **Scratch budget (DEC-898):** your share is 1 GB and 50,000 files and folders; use your sandbox's own temp folder; clean what you make.
- **Command forms the guard reads:** one simple command per Bash call; literal paths (no shell variable as a write target); no here-documents, backticks or `bash -c '...'`; anything longer goes in a script file under your sandbox's temp folder and is run with `python3 <file>`. Write files with the Write and Edit tools and absolute paths.
- **Refused twice for the same call: stop and say so; no third try.** Never work around a refusal: report it.
- **Commit, only under `experiments/EXP-002`:**
  `git commit -m "W2-40: EXP-002 hook-limit record from the measured results" --trailer "Task: DAEO-6ox0" --trailer "Role: research" --trailer "Implements: DEC-160, DEC-1083" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- experiments/EXP-002`
  (`git add` the files first). No amend, no rebase, no merge, no push. `git status --short` empty at the end.

## Return
The twelve fields first, each a labelled line (`work_completed` holds the verdict in two lines), then the sandbox check result, the S1 sentence quoted from the record, the `gov.__file__` line, and the guard refusals you met (or none).

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```
Refused twice for the same call: stop and say so.
