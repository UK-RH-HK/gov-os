# Research brief: W2-40 (DAEO-6ox0), the script round of EXP-002 (the harness's hook limit)

Template: role-research@1.0.0 (`.claude/templates/role-research.md` in your tree; read it). Written by the ticket lead (orchestrator, W2-40), 2026-11-11. Budget: projection_usd 3.

## Who and where
- Role `research`, ticket `DAEO-6ox0` (W2-40), tree `/home/usain/gov-os-worktrees/W2-40`, branch `w2/W2-40`.
- First: `printenv GOV_ROLE GOV_TICKET` (expect `research`, `DAEO-6ox0`) and `git -C /home/usain/gov-os-worktrees/W2-40 rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-40`, `w2/W2-40`). Different: stop and say so.

## Step 0, the sandbox check, before any work, reported first in your return
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-6ox0','w').write('x')"` must FAIL; (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return (the form of `EMG-d4b-launched.md`, copied beside this brief).

## Your writes: one folder only
You write only under `experiments/EXP-002/` (your files and any scratch of yours), never anything else: not `.claude/`, `src/`, `template/`, `tests/`, `.tickets/`, the decision register, `docs/`, `governance/`. You change no product file and no control (settings, hook programs, guard). No installs of any kind (no pip, no npm). Never copy the tree (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`).

## The question, the decision it feeds, the stop rule (state these first in the record)
- **Question:** what does Claude Code (the harness, `~/.local/bin/claude`, version 2.1.322 today: you may run `claude --version` and `claude --help`, which start no session) do with a hook that runs past its configured time limit: is the call allowed, denied or failed, how long does it take, is the hook's process ended or left running; at the limit the repository itself uses (60 s) as well as at 5 s; and what does it do with no limit set and for the post-call and Stop events?
- **Decision it feeds:** DEC-580 and DEC-587: whether the guard's own deadline (20 s) sits below the harness's measured limit, and whether the other hook programs need a deadline of their own (rows W2-H052, W2-M347, W2-L328 in `docs/plan/WAVE_2_LIST.md`).
- **Stop rule:** the five mandatory cases measured twice each (by the lead) and the optional ones once; a case that cannot be measured is "not measured" with its reason, never filled in. Your round stops when the script, its README and the record's skeleton are committed.

## Why the split (read this)
The experiment starts headless `claude -p` sessions, which need the model API and the login. Your sandbox's network is the research allowlist (no model API), so **you never start a `claude -p` session** (if you tried once by mistake, say so; never twice). You write the script, its README and the record's skeleton; your lead runs the cases outside the sandbox; a second, fresh research session writes the record from the results.

## What is known (re-read each in your own tree; cite path and line in the skeleton; do not copy from here)
- The earlier, delegated experiment (DEC-578, 2026-10-09, Claude Code 2.1.288): `docs/research/EXP-hook-time-limit.md`. With a PreToolUse limit of 5 s and a hook that sleeps 25 s, the call was allowed (the refusal the hook would have given is lost). Its script, the model for yours: `/home/usain/gov-os-worktrees/W2-40/.gov-runtime/scratch/lead/ref/exp-hook-timeout.py` (a copy the lead put in your tree; 65 lines, stdlib).
- The repository's hook entries carry `"timeout": 60`: `.claude/settings.json` (five entries) and `template/.rulesync/hooks.jsonc`.
- The guard's PreToolUse program keeps its own deadline of 20 seconds: `.claude/hooks/pretooluse.py` (`signal.alarm(20)` and the deadline's deny answer, "the guard could not decide in 20 seconds, so the call is refused"); `src/gov/guard/decide.py`'s `_LOOKUP_S = 15` sits inside it.
- Decisions to read in `docs/DECISION_REGISTER.md` (grep `### DEC-n`; it is large): DEC-160, DEC-578, DEC-580, DEC-587, DEC-590, DEC-827, DEC-1083.
- Find what you need with the Read and Grep tools (you have no `gov retrieve` in the sandbox, DEC-1065). Search named folders, not the repository root. If a search does not answer, or your answer may be incomplete, search once more in your own, different words; then answer from both with path and lines, or say "not found". Two searches in all.

## What you write
1. **`experiments/EXP-002/run_hook_limit.py`**: Python standard library only, run by `python3 <path>`.
2. **`experiments/EXP-002/README.md`**: the flags, the cases, what each output field means, how to repeat.
3. **`experiments/EXP-002/hook-limit-record.md`**, the record's skeleton: front matter (`type: research`, `status: ACTIVE`, `state_class: EVIDENCE`, `decisions: [DEC-580, DEC-587]`, `sources:` the ids it cites), then the question, the decision it feeds, the stop rule, the method, the commands to be run, the sources, the guard facts with path and line, and empty `Measurements`, `Uncertainty` and `Conclusion` headings. **No number you have not measured.**

### The experiment's design (the script's contract, word for word from the lead's brief)
One throwaway project per case under `--base`, each with its own `.claude/settings.json` that registers one hook and nothing else, outside every git repository; one `claude -p` session per case (`--output-format stream-json --verbose --allowedTools "Bash"` as the earlier run, plus `--setting-sources project` when 2.1.322 has the flag, and the model from `--model`), started with every `CLAUDE*` and `GOV_*` variable removed from its environment (the way W1-46's fixture does, DEC-784), a per-session wall limit of the hook's sleep plus 60 s, in the project's folder; the prompt asks for exactly one bash command that touches `<project>/ran.txt`. The hook is a shell command that, before anything else, appends `started <epoch seconds with fractions>` to `<project>/hook.log`, then appends `tick <epoch>` once a second for its sleep time, then `finished <epoch>` and exits with its code (0, or 2 with a message on stderr). The script records, per case and run, as one JSON line to `<out>/<case>-<run>.json` and to its stdout: the case id, the harness version (from the session's init message), the model, the hook event, the configured limit (the `timeout` key, or "none"), the hook's sleep, the code it would have exited with; the **time from the hook's `started` to the call having run** (the mtime of `ran.txt` less the `started` time, in seconds, or "not run"); the whole session's wall time; whether `finished` appears in the log, the last `tick` time less `started` (so whether the hook's process was ended at the limit or left running, and when), whether `ran.txt` exists, the tool result's `is_error` and the first 300 characters of its text, and the first 300 characters of the session's final result. It never keeps the raw stream. **Cases** (`--case`, each run twice, `--run a` and `--run b`, for the five mandatory ones): `pre-control-5` (PreToolUse, limit 5, the hook refuses at once: exit 2); `pre-allow-5` (PreToolUse, limit 5, sleeps 25 s, would exit 0); `pre-deny-5` (limit 5, sleeps 25 s, would exit 2); `pre-allow-60` (PreToolUse, limit **60**, the repository's own value, sleeps 90 s, would exit 0); `pre-deny-60` (limit 60, sleeps 90 s, would exit 2: the case that matters, a refusal that comes after the limit). Then the optional cases of the rows (one run each, after the mandatory ones are in): `pre-nolimit` (PreToolUse with no `timeout` key, sleeps 130 s: whether the harness's default limit is below or above 130 s); `post-5` (PostToolUse, limit 5, sleeps 25 s); `stop-5` (Stop, limit 5, sleeps 25 s; the prompt is the same). `--dry-run` for every case prints the planned settings and command, no session.

### The lead's additions to the contract (needed to read the numbers and to run it safely)
- **Flags:** `--case <id>` (one case per call), `--run a|b`, `--base <dir>`, `--out <dir>`, `--model <model id>`, `--dry-run`, and `--claude <path>` (default `/home/usain/.local/bin/claude`). The script makes `--base` and `--out` itself (mkdir). It writes nothing outside `--base` and `--out`, and reads no settings file but the throwaway ones it wrote (never `~/.claude/settings.json` or the repository's).
- **`--setting-sources`:** decide at run time from `claude --help`'s text (no session), and record in the JSON line whether the flag was used (`setting_sources_flag: true|false`).
- **A process left running must be seen:** before it reads `hook.log`, the script waits until `started` + the hook's sleep + 3 s has passed (or `finished` is in the log), so a hook process the harness left running has had time to tick on and write `finished`. Record the last tick's offset either way.
- **Stopping by pid:** start the session in its own process group (`start_new_session=True`), print a line `pid <n>` at once and write `<out>/<case>-<run>.pid`, so a hung session can be stopped by its pid; on the per-session wall limit, end that process group and record `"session": "timed out"`.
- **Re-runs:** a case's project folder is emptied of `hook.log` and `ran.txt` before its session (the earlier script's way); the JSON line also carries the session's exit code, the session id (from the init message), the `--base` project path and the epoch start time.
- **No secrets:** keep only extracted fields; never the raw stream, never the environment, never a key.
- **Your own dry runs:** use `--base` and `--out` under your sandbox's temp folder (print `echo $TMPDIR` first and pass its value as a literal path), so nothing of the dry run lands in the tree; run `--dry-run` for every case and quote one plan in your return.

## Rules
- **DEC-732, word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-40/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-40/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. (You run no test and no `gov` command in this round; quote the line anyway.)
- **DEC-820:** reads are open; (a) never read or print secrets or keys; (b) never read the held-out qualification material's contents; (c) the counterpart's work on this ticket (none here: there is no acceptance folder); (d) never read the hidden half of any evaluation set (`~/gov-os-eval`). Never write in `~/gov-os-workbench`.
- **DEC-849:** the guard may refuse some reads (searches from the repository root, `governance/project/`, `.claude/`): take the refusal, never another spelling; search named files instead; count the refusals in your return.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never the full 40, and never write the keywords of the secrets rule that takes a bare 40-hex string for a token.
- **Scratch budget (DEC-898):** your share is 2 GB and 100,000 files and folders; use your sandbox's own temp folder; clean what you make.
- **Command forms the guard reads:** one simple command per Bash call; literal paths (no shell variable as a write target); no here-documents, backticks or `bash -c '...'`; anything longer goes in a script file under `experiments/EXP-002/` (removed before commit if it is not one of your three files) and is run with `python3 <file>`. Write files with the Write and Edit tools and absolute paths.
- **Refused twice for the same call: stop and say so; no third try.** Never work around a refusal: report it.
- **Commit, before any long step, only your three files:**
  `git commit -m "W2-40: EXP-002 hook-limit script, README and record skeleton" --trailer "Task: DAEO-6ox0" --trailer "Role: research" --trailer "Implements: DEC-160, DEC-1083" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- experiments/EXP-002`
  (`git add` the three files first). No amend, no rebase, no merge, no push. `git status --short` empty at the end.

## Return
The twelve fields first, each a labelled line, then the sandbox check result, one `--dry-run` plan quoted, the `gov.__file__` line, whether `--setting-sources` exists in 2.1.322 (from `--help`), and the guard refusals you met (or none).

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
