# Brief: engineer, DAEO-drhj (W2-104), run 5 — the harness also leaves `scenario-summaries.md` out of the session

You are a fresh engineer. Ticket: `DAEO-drhj` (W2-104), profile STANDARD, class C2. You work only in the worktree
`/home/usain/gov-os-worktrees/W2-104` on branch `w2/W2-104`. The ticket's harness (`gov skilleval`, in
`src/gov/skilleval/`) is built, verified and landed. The CTO reopened it under DEC-1164 (18) for one small fix (read
the ticket's last paragraph, "Reopened 2026-11-14", in `/home/usain/gov-os-worktrees/W2-104/.tickets/DAEO-drhj.md`).
Your lead has merged `w2/integrate` into the branch as `3ef7c62c4243`. Your task is one commit. Nothing else.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-drhj`),
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-104` and `w2/W2-104`),
  `git rev-parse --short=12 HEAD` (expect `3ef7c62c4243`) and `git status --short` (expect nothing). If anything
  differs, stop and say so.
- Run everything in the foreground, one command after another. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag,
  no stash.
- **The code under test (DEC-732):** every test run and every `gov` command used for verification runs this worktree's
  own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src` set per command. Quote
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src python3 -c "import gov; print(gov.__file__)"` in your return.
- **Every pytest through the heavy slot** with `TMPDIR` your sandbox's own `$TMPDIR` (keep it; never set it, never
  `--basetemp`), `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`:
  `env PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-104/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  A slot gate's refusal or wait is a wait, not a refusal.
- **Reads (DEC-820):** reads are open, except: (a) secrets and keys, never read or printed; (b) the held-out
  qualification material's contents (never read, search, diff or copy it; its file names may be seen); (c) the
  counterpart's work on this ticket: you never read `tests/acceptance/W2-104/` by any tool (your lead runs it through
  `gov accept`); (d) the hidden half of any evaluation set. Never open an evaluation set's root or any hidden or
  memory-verdict folder. You search with the Read and Grep tools, naming the folder a search starts at; if the first
  search does not answer, search once more in different words, then answer from what you read or say "not found"
  (no `gov retrieve`, no `gov context` in the sandbox, DEC-1065).
- **Command forms the guard can read:** no shell variable or `$(…)` as a write target, no here-document, no
  backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Edit with the Edit tool at literal absolute
  paths. Anything longer than one line goes in a script file in your sandbox's `$TMPDIR`.
- **Refused twice for the same call: stop and say so; no third try.** Never work around a refusal by another tool or
  form (DEC-1142 (9)); report it.
- Install nothing. No subagents that write. Never write `.gov-runtime/**`. Never ask or notify the owner.
- Write commit hashes as 12 digits in your return, never the full 40.

## The task (W2-101's review F1, fails open)

`src/gov/skilleval/harness.py` (around lines 165-168, in `run_scenario`) copies the skill's folder into the session's
`.claude/skills/<name>/` with `ignore=shutil.ignore_patterns(SCENARIOS, RECORD)`, where line 34 holds
`SCENARIOS, RECORD = "scenarios.md", "scenario-records.yaml"`. A hand-written `scenario-summaries.md` beside them
(W2-100's and W2-101's interface) is therefore shown to the session under test.

1. **The harness:** add a named constant beside `SCENARIOS` and `RECORD` for `"scenario-summaries.md"` (for example
   `SUMMARIES = "scenario-summaries.md"`, on its own line right after line 34, with a short comment naming W2-100's and
   W2-101's interface), and add it to the `ignore_patterns(...)` call. Nothing else in the harness changes.
2. **One unit case** in `tests/unit/skilleval/test_w2_104_skilleval.py` (the existing file; reuse its `project`
   fixture, `plant_skill`, `skilleval` and `calls` helpers; the stub already logs the session folder's file list as
   `files`). Name it `test_w2_104_session_folder_leaves_out_scenarios_records_and_summaries`. It plants the skill,
   writes all three files beside `SKILL.md` (`scenarios.md` comes from `plant_skill`; write a
   `scenario-records.yaml` that the harness accepts as a prior record — look at how `test_w2_104_records_are_appended`
   or the record reader accepts one, or use the record the first run writes and then run a second time — and a
   `scenario-summaries.md`), runs `gov skilleval`, and asserts the session call's `files` holds `SKILL.md` and none
   of `scenarios.md`, `scenario-records.yaml`, `scenario-summaries.md`. Check the case fails (red) on the harness
   without your step 1 change before you make it, and passes after; say both in your return.
   Nothing else in the test file changes.

Check, to the end, never `-x`, through the heavy slot:
`tests/unit/skilleval tests/unit/check/test_check.py tests/unit/check/test_kernel_followup.py`.
Also `git diff 3ef7c62c4243 --stat` shows only the two files.

Commit only those two files (check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no
`pre-commit` file; if one is there, stop and return; never `--no-verify`). The trailers are in one final paragraph:

    git commit -m "W2-104: the harness also leaves scenario-summaries.md out of the session's skill folder (W2-101's review F1), with one unit case" --trailer "Task: DAEO-drhj" --trailer "Role: engineer" --trailer "Implements: DEC-959, DEC-820" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- src/gov/skilleval/harness.py tests/unit/skilleval/test_w2_104_skilleval.py

(`Implements:` names only the ticket's `sources:`, DEC-959 and DEC-820 (DEC-927).) Use your own model's name in the
`Co-Authored-By` line if it is not Sonnet 5.5.

Then `git log -1 --format='%h %s%n%(trailers)'` and `git status --short` (expect nothing but the sandbox's own
`/dev/null` mount points, if any; name them).

Your lead runs `gov accept` and the wider suites after you return; you do not.

## Return

Your last message, complete in itself. **The twelve fields come first, each a labelled line** ("none" where there is
nothing). Include: the sandbox check's result first in `evidence`; the commit's 12-digit hash and trailers; its diff
stat; the red-then-green of the new case; the tests you ran with their counts; the `gov.__file__` line; the read
refusals you met; your scratch figures (`du -s --inodes` and `du -sh` of your `$TMPDIR` at the end); anything refused
or not settled, as a package (question, options with cost, recommendation, confidence, what it blocks).

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

## Context bundle (`gov context DAEO-drhj --role engineer`, built by your lead outside the sandbox)

The ticket's sources are DEC-959 (ACCEPTED) and DEC-820 (ACCEPTED); the ticket text is in
`/home/usain/gov-os-worktrees/W2-104/.tickets/DAEO-drhj.md` as merged. Its allowed paths: `docs/probes/DAEO-drhj/**`,
`src/gov/skilleval/**`, `tests/unit/skilleval/test_w2_104*`, `governance/project/skill-imports.yaml`,
`src/gov/check/commands.py`. Bundle hash `b58b6fe9219a`.
