# Brief: independent test designer, DAEO-uw5h (W2-100), run 2 — one case's version reading (a revision of your own suite)

You are a fresh independent test designer (MR-3). Ticket: `DAEO-uw5h` (W2-100), profile STANDARD, class C2. You work
only in the tests worktree `/home/usain/gov-os-worktrees/W2-100-tests` on branch `w2/W2-100-tests` (its head
`d9379baaa`, the suite td-1 wrote); you never write the ticket's worktree `/home/usain/gov-os-worktrees/W2-100`. One
case of `tests/acceptance/W2-100/` pins a reading of the lead's that was too narrow; you revise that case, its README
lines, and nothing else.

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-uw5h','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop there and return (status ESCALATION, with what you saw). Do not delete
  any file (a) made.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-uw5h`),
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-100-tests` and
  `w2/W2-100-tests`), `git rev-parse --short=12 HEAD` (expect `d9379baaa...`) and `git status --short` (expect
  nothing). If anything differs, stop and say so.
- Run everything in the foreground, one command after another. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag,
  no stash, no `git worktree`.
- **Reads (DEC-820):** open, except secrets and keys; the held-out material's contents; **the counterpart's work: you
  never read the skills being written**: nothing under `template/governance/kernel/skills/{backend,api,data,security}/`,
  `.rulesync/skills/{backend,api,data,security}/` or `template/.rulesync/skills/{backend,api,data,security}/` in the
  ticket's worktree `/home/usain/gov-os-worktrees/W2-100` or on branch `w2/W2-100`, by any tool; the hidden half of any
  evaluation set (never open an evaluation set's root or any hidden or memory-verdict folder). Search with the Read and
  Grep tools, naming the folder a search starts at.
- **Command forms the guard can read:** no shell variable or `$(…)` as a write target, no here-document, no backticks,
  no `bash -c '…'`, no long inline `python3 -c` with braces. Edit with the Edit tool at literal absolute paths.
- **Every pytest through the heavy slot**, `TMPDIR` your sandbox's own (never set it, never `--basetemp`):
  `env PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-100-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-100 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=line`
- Install nothing. No subagents that write. Never write `.gov-runtime/**`. Never ask or notify the owner.
- **Refused twice for the same call: stop and say so; no third try.** Never work around a refusal (DEC-1142 (9)).
- Write commit hashes as 12 digits in your return.

## The failing output (the lead's verification run on the ticket branch at b3503e0a3c6d)

```
tests.acceptance.W2-100.test_w2_100_skills::test_the_front_matter_is_the_templates_with_nothing_more[backend] | AssertionError: version is '1.0.1', expected the string 1.0.0 assert '1.0.1' == '1.0.0'
(the same for api, data and security)
```

## Why it is the case, not the skill, that changes (the lead's decision)

The lead's interface reading (td-1's brief) wrote `version: "1.0.0"` and `metadata: {version: "1.0.0"}` for the skills'
front matter, as their first version. The skill template (`template/governance/kernel/templates/skill.md`, its comment:
"A skill whose text changes raises its version", and `metadata.version` repeats `version`, DEC-832 item 2) then
applied during the build: a fix to the skills' text (an earlier suite's case, W2-11's output-class case) raised them to
`1.0.1`, and the real scenario runs were made again at 1.0.1. Pinning the exact first version was the lead's
over-narrow reading; the KPI line (S3) asks for "front matter with name, version and a third-person description". The
reading now is W2-98's (`tests/acceptance/W2-98/README.md`, "Front matter"): `version` is a non-empty string at the
top level, and `metadata` is exactly `{version: <the same string>}`.

## What you change

1. `tests/acceptance/W2-100/test_w2_100_skills.py`, `test_the_front_matter_is_the_templates_with_nothing_more`: the two
   asserts on the exact `"1.0.0"` become: `version` is a non-empty string (a YAML string, not a number) of the form
   `<digits>.<digits>.<digits>`, and `metadata == {"version": <that version>}`. The other asserts of the case stay.
2. `tests/acceptance/W2-100/README.md`, the "Front matter" lines: the same reading, naming the template's rule and this
   revision. Your planted builders (`w2_100_support.py`) and the harness and scenario cases keep `1.0.0` (their own
   planted values): change nothing there.
3. **Bite check:** show once (in your return) that the revised case still fails on a planted front matter whose
   `metadata.version` differs from `version`, and on one with `version: 1.0` unquoted (a number) — by a throw-away
   test file of your own in `$TMPDIR` that imports your support module, never committed.

Run the suite to the end (never `-x`) in your tree and report the counts (the real-tree cases are red there for the
absent skill folders, as before; name any change in the count against td-1's 184 failed, 46 passed).

## Commit

Check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (if one is, stop
and return; never `--no-verify`). Every trailer in the one final block:

    git commit -m "W2-100 tests: the front-matter case reads version as the template does (non-empty, equal to metadata.version), not the first version pinned" --trailer "Task: DAEO-uw5h" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-959, DEC-832" --trailer "Rewrite-Reason: the lead's reading pinned version 1.0.0; the skill template raises a changed skill's version (1.0.1), read as W2-98's suite reads it" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-100/test_w2_100_skills.py tests/acceptance/W2-100/README.md

Then `git log --oneline -2` and `git status --short`.

## Return

Your last message, complete in itself. **The twelve fields first, each a labelled line** ("none" where nothing): the
sandbox check first in `evidence`; the commit's 12-digit hash and trailers; the diff of the case; the bite check; the
suite's counts; the read refusals you met; your scratch figures.

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
