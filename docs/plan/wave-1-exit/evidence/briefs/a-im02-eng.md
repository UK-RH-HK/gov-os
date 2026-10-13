# Brief: engineer

You are a fresh engineer. Ticket: ORION-im02, profile STANDARD. You work only in the worktree
`/tmp/claude-1000/-home-usain-gov-os-worktrees-W1-42/1be98491-a02b-4f3c-accf-41da4cc96c6b/scratchpad/clones/a-dev-exit`
on branch `feature/dimension-checked-addition`. You implement the ticket until its acceptance tests pass.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `ORION-im02`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD`. If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean` in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read the settings file of the harness, in this clone or anywhere.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path
  (DEC-525). Never list or read `~/gov-os-workbench/` or anything in it, and nothing under `~/.claude/`.
- Never copy the repository or a folder of it (a recursive copy, a sync, an archive, a second worktree or a clone
  of this repository) anywhere; copy single named files only, never `governance/project/`.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag
  exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write
  and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned
  as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final
  message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a
  package.

## What you read

- The ticket file `.tickets/ORION-im02.md` (read-only): its KPI lines and its `allowed_paths`.
- The ticket's acceptance tests and their README (read-only): `tests/acceptance/W1-34/`.
- The sources: `specs/math/dimensional-analysis.md` (MATH-SPEC-003), section "Compound dimensions";
  `decisions/adr-011.md` (ADR-011, the owner's answer of 2026-10-13).
- The code the ticket touches: `python/orion_ref/dimensions.py`.

## What you write

- Only inside the ticket's `allowed_paths`: `python/orion_ref/dimensions.py`.
- Never the acceptance tests (MR-3), under `tests/acceptance/W1-34/` or `tests/acceptance/W1-02/`. A test you
  think is wrong is returned as a package, never edited and never worked around.
- No builder test is added: `python/orion_ref/tests/test_dimensions.py` stays unchanged, byte for byte (the
  ticket's KPI lines say so, and it is outside your `allowed_paths`).
- Proportion (DEC-135): no code for edge cases beyond the KPI lines. The ticket is one named constant; nothing
  else is added.
- Run the ticket's acceptance tests with `python3 -m pytest tests/acceptance/W1-34 -q -p no:cacheprovider` (from
  the root of the repository) in the foreground, to the end, never stopping at the first failure, until they
  pass. Then, each to its end: `python3 -m pytest tests -q -p no:cacheprovider` (both acceptance folders), and
  the programme's own tests of the reference, `python3 -m pytest python/orion_ref/tests -q -p no:cacheprovider`
  run from the folder `python/` or with `python/` on the import path, as they ran before your change (state how
  you ran them, and their counts before and after).

## Commit

Commit only your path, in one commit, with the trailers in the final block (DEC-182, DEC-476). Name no decision
id of another project's register in the subject:

    git commit -m "<subject>" --trailer "Task: ORION-im02" --trailer "Role: engineer" --trailer "Implements: MATH-SPEC-003" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After the commit run `git log -1 --format='%(trailers)'` and `git show --stat HEAD`, and check that all four
trailers are there and that the commit holds `python/orion_ref/dimensions.py` and nothing else; if a trailer is
missing, amend your own commit (it is the unpushed tip) so that it carries them.

## Return

Your commit's hash; the files changed; the tests you ran with their results; the lines added and removed;
anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility,
cost, recommendation, confidence).

## The twelve-field return

Your last message carries all twelve fields below, each as a label at the start of a line, followed by a colon
and at least one word. No field is left empty: write "none" where there is nothing. The fields frame the return;
they do not shorten it.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | LEAD_CHECKPOINT | BLOCKED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```
