You are a fresh engineer. Ticket: DAEO-e82f (W2-65, "The guard's hook lines refuse a call when the guard program cannot run"), profile LITE. You work only in the worktree `/home/usain/gov-os-worktrees/W2-65` on branch `w2/W2-65`. You implement the ticket until its acceptance tests pass.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-e82f','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-e82f`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-65` and `w2/W2-65`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=/home/usain/gov-os-worktrees/W2-65/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Commit your work before you run any long suite. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree. No push, merge or tag.
- **Reads are open, writes are closed (DEC-820, Policy 2).** You may read the whole repository, git history and other worktrees, except four things:
  - (a) secrets and keys: never print one;
  - (b) the contents of the held-out qualification material (its file names may be seen); never read or name the qualification oracle;
  - (c) **the counterpart's work on this ticket: you never read this ticket's acceptance tests**: nothing under `tests/acceptance/W2-65/`, and not the test designer's revised case in `tests/acceptance/W1-29/test_session_hooks.py` (`TestSubagentStop::test_block_includes_reason_and_is_once`), by any tool (no Read, cat, grep, diff, `git show` or `git log -p` of them). You may run them and read their results: names, pass or fail, and failure messages.
  - (d) the hidden half of any evaluation set, by whoever is measured by it.
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads that Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form of the same read, and search named folders instead. Count every refusal you meet and give the count in your return.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Never read `.claude/settings.json`, in this worktree or anywhere. Never write in `~/gov-os-workbench`, and never list, glob or search it (DEC-723).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository); copy single named files only, never `governance/project/`. A throwaway trial builds a temporary project from scratch in a temporary folder. No clone, copy or programme file under any `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **Never install, regenerate or touch the live hooks or settings:** no `rulesync generate`, no edit of any `.claude/` file, no run against `$HOME/.local/bin/gov` or the real `$HOME`. Your worktree's `.rulesync/hooks.jsonc` is its own copy; the live settings change only at the owner's regeneration after the re-pin. Try a hook line only with `sh -c` in a temporary project with a temporary `HOME`, `CLAUDE_PROJECT_DIR` and `PATH`.
- **A broken guard blocks every tool, yours included, once the lines are live.** They are not live in your session, but never leave a hook program in this worktree broken, even for a moment: plant faults only in temporary copies.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package.
- You never ask or notify the owner (no question box, never `owner-ping`); a question comes back to the lead in your return.
- **Memory (DEC-836, DEC-859, DEC-860):** for what you need to know, use `gov retrieve` first (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-65/src python3 -m gov.cli.main retrieve "<question>" --json`), before reading files at random. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used `gov retrieve` and for what.
- **Disk budget (DEC-898):** your share is 5 GB and 250,000 files and folders outside the tracked tree. Use the temp folder the launcher's sandbox sets (`TMPDIR` as your session has it); do not set `TMPDIR` yourself: `/tmp/gov-os-lead-W2-65` is not writable inside the sandbox, and pytest then falls back to the worktree. If a `pytest-of-*` folder appears in the worktree, stop using that form. The untracked `pytest-of-usain/` already in the worktree is an earlier worker's; leave it, never commit it. Keep pytest's own temp retention: never pass `--basetemp`; pass `-o tmp_path_retention_policy=failed`. Clean up any temp tree you make as soon as it is no longer needed. Passing the budget: stop and return.

## What you read

- The ticket file `.tickets/DAEO-e82f.md` (read-only): its KPI lines and its `allowed_paths`.
- The card: `docs/plan/WAVE_2_WBS.md`, section 2, "W2-65"; section 0.
- The decisions: DEC-880 (item 3), DEC-889 (item 8, P-H-7), DEC-899 (P-IS-5 (a)), DEC-884, DEC-822, DEC-135 (proportion) in `docs/DECISION_REGISTER.md`.
- Claude Code's hook contract (code.claude.com/docs/en/hooks), as the sources state it: a PreToolUse call is blocked only on exit 2 (its stderr goes to the model) or a deny decision on stdout; any other non-zero exit is a non-blocking error and the call goes through. A SubagentStop hook blocks on exit 2 with its reason on stderr, or on exit 0 with `{"decision": "block", "reason": "…"}` on stdout; stdout with exit 2 is not delivered.
- The code the ticket touches: `.rulesync/hooks.jsonc`, `template/.rulesync/hooks.jsonc`, `template/governance/kernel/hooks/subagentstop.py`, `src/gov/hooks/subagentstop.py`, `tests/unit/hooks/`.
- For the weak unit cases: `docs/assessment/2026-10/I-SYNTHESIS.md` (the "Unit hooks" row, about line 443, and the P9 row, about line 209) and `docs/assessment/2026-10/I3-retrieval-context-resume.md` (the rows for `test_w29_hooks.py`, about lines 456 to 460, and the planted faults P9, P10 and P14a).

## What you build

1. **The hook lines' exit mapping** (`.rulesync/hooks.jsonc`): the preToolUse line and the containment lines (the entries that run the containment program, on postToolUse and postToolUseFailure) end with exit 2 whenever their program ends with any exit other than 0 or 2 (a syntax error, an import error, a missing file, a crash), with a message on stderr that names the program. Exit 0 (with its stdout untouched, a deny decision included) and exit 2 (with its stderr) pass through unchanged. Keep W2-59's part of each line: the pinned-judge interpreter lookup and its exit 2 when no interpreter can be found. Every exit-2 refusal of these lines, including those of W2-59's lookup (an interpreter that cannot start), must name the program on stderr; W2-59's acceptance suite must stay green. The preToolUse command must still contain the text `hooks/pretooluse.py` (the launcher recognises the guard by it). The other lines (preCompact, sessionStart, stop, subagentStop) are not this ticket's.
2. **The template's hook source** (`template/.rulesync/hooks.jsonc`): the same mapping for its preToolUse and containment lines, and nothing else changed in it.
3. **P-H-7 (DEC-889 item 8):** the SubagentStop hook gives its block reason as Claude Code reads it (on stderr with exit 2, or `{"decision": "block", "reason": …}` on stdout with exit 0), so a helper whose final message lacks some of the twelve fields learns which are missing. Its fail-closed behaviour on bad input stays (it still blocks). Change `template/governance/kernel/hooks/subagentstop.py`, and keep `src/gov/hooks/subagentstop.py` byte-identical to it (W1-29's `TestHookCopiesIdentical` must stay green).
4. **The weak unit hook cases (P-IS-7 (a)), in `tests/unit/hooks/`:** revise each so it can fail for its fault, and show it: first red against the planted fault in a temporary copy (never in the tree), then green on the head. Lower no expectation.
   - `TestStopHook::test_no_ticket_returns_immediately` (no assertion; PF-6);
   - `TestStopHook::test_stop_hook_active_returns_immediately` (P14a: the guard removed leaves it green);
   - `TestPreCompactCombined::test_checkpoint_failure_reports_systemmessage` (P9: `if out:` lets a silent hook pass; a non-orchestrator's PreCompact that cannot write its checkpoint must say so);
   - `TestPreCompactCombined::test_no_ticket_no_record` (outdated: looks under `docs/checkpoints/`; automatic records go to `.gov-runtime/scratch/checkpoints/` since DEC-444);
   - `TestSessionStartCombined::test_within_cap` (P10: never cut leaves it green).
   If a revised case shows the hook itself is wrong (for example PreCompact really says nothing when the checkpoint fails), do not change that hook (it is outside your paths): leave the case asserting the right behaviour only if it is green on the head; otherwise return it as a package with the evidence.
   Also update any unit case your SubagentStop change makes stale (where the reason goes), lowering nothing else.
- Proportion (DEC-135): about 30 lines in the hook lines and the hook; no code for edge cases beyond the KPI lines. **Never make a guard decision fail open:** each failure KPI must still refuse, and no line may turn exit 0 into a refusal.

## What you write

- Only inside the ticket's `allowed_paths`: `.rulesync/hooks.jsonc`, `template/.rulesync/hooks.jsonc` (the preToolUse and containment lines' exit mapping only), `template/governance/kernel/hooks/subagentstop.py`, `src/gov/hooks/subagentstop.py`, `tests/unit/hooks/**`.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.

## Run

Run each suite to its end, never `-x`, with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-65/src python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`:
- the ticket's acceptance tests: `tests/acceptance/W2-65 tests/acceptance/W1-29`, until they pass;
- the suites that run the hook lines or the hooks: `tests/acceptance/W2-59 tests/acceptance/W1-38 tests/acceptance/W1-46 tests/acceptance/W1-49 tests/acceptance/W2-62 tests/unit/hooks tests/unit/launch`;
- then `PYTHONPATH=/home/usain/gov-os-worktrees/W2-65/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header`: its last line must show no collection error.
Do not run the whole suite; the lead does.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Commit only your paths, `git commit -m "<subject>" -- <paths>`, with the trailers in the final block:

    --trailer "Task: DAEO-e82f" --trailer "Role: engineer" --trailer "Implements: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After each commit, run `git log --oneline -2` and `git status --short` and quote them.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Put in them: the sandbox check's result; your commits' hashes with their trailers; the files changed; the lines added and removed (`git diff --shortstat` against `4ef3293a` for the hook lines and the hook, and for the unit tests); each suite you ran with its counts; each weak unit case with its planted fault, red, then green; the `gov.__file__` line; the collect-only last line; the read refusals you met (count); whether you used `gov retrieve`; any package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

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

Refused twice for the same call: stop and say so; no third try.
