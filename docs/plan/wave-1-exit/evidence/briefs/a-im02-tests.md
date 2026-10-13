# Brief: independent test designer

You are a fresh independent test designer (MR-3). Ticket: ORION-im02, profile STANDARD. You work only in the
worktree `/tmp/claude-1000/-home-usain-gov-os-worktrees-W1-42/1be98491-a02b-4f3c-accf-41da4cc96c6b/scratchpad/clones/a-dev-exit`
on branch `feature/dimension-checked-addition`. You write the ticket's acceptance tests from its KPI lines and
its sources, before the implementation, and you show them red.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `ORION-im02`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD`. If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean` in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read the settings file of the harness, in this clone or anywhere.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path
  (DEC-525). Never list or read `~/gov-os-workbench/` or anything in it, and nothing under `~/.claude/`.
- Never copy the repository or a folder of it (a recursive copy, a sync, an archive, a second worktree or a clone
  of this repository) anywhere. A throwaway stand-in copies single named files, never `governance/project/`; a
  test that needs a repository builds a temporary one.
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

- The ticket file `.tickets/ORION-im02.md` (read-only): its KPI lines, its `allowed_paths` and its sources.
- The sources: `specs/math/dimensional-analysis.md` (MATH-SPEC-003), section "Compound dimensions", the line for
  acceleration; `decisions/adr-011.md` (ADR-011, the owner's answer of 2026-10-13: that section is accepted for
  this one constant, and the name of the constant is `ACCELERATION`).
- The public interface the ticket must work with: what the reference offers to its callers from
  `orion_ref.dimensions`, as its existing tests use it (`python/orion_ref/tests/test_dimensions.py`) and as the
  README of the earlier acceptance tests lists it (`tests/acceptance/W1-02/README.md`): `Dimension`, the eight
  named dimensions, `*`, `/`, `==`, `repr()`, `is_dimensionless()`, `+` and `-`. You read no private part of an
  implementation to learn what a test should expect.

## The behaviour to test

In the words of the KPI lines of ORION-im02 and of its sources:

- The reference offers a named dimension for acceleration under the name `ACCELERATION`, beside its existing
  named dimensions and importable from the same module as they are (ADR-011). Failure: the reference offers no
  dimension under that name.
- `ACCELERATION` equals length divided by time squared: it equals `LENGTH / (TIME * TIME)` and the dimension with
  the exponents L 1 and T -2, as the line `Acceleration = L * T^{-2}` of MATH-SPEC-003, section "Compound
  dimensions", states. Failure: it is another dimension, or it is not a `Dimension` of the reference.
- The eight existing named dimensions (`DIMENSIONLESS`, `LENGTH`, `MASS`, `TIME`, `VELOCITY`, `ENERGY`,
  `MOMENTUM`, `FORCE`) keep the values they have. Failure: an existing named dimension changes its value.
- The five existing tests of `python/orion_ref/tests/test_dimensions.py` pass unchanged. Failure: an existing
  test fails or has to be changed.
- A named dimension other than `ACCELERATION` is not added to the reference by this ticket (the last failure
  line).

The KPI line "the acceptance tests under `tests/acceptance/W1-02/` still pass" is held by that folder itself,
which you do not touch.

## What you write

- Only inside `tests/acceptance/W1-34/` (a new folder). You do not touch `tests/acceptance/W1-02/`. No throwaway
  implementation is left in the tree.
- The two folders are also run together, as one run of `tests/`: give your test files and helper modules names
  that no file of `tests/acceptance/W1-02/` has, and do not rely on importing a module named `conftest`, so that
  `python3 -m pytest tests -q -p no:cacheprovider` collects both folders without an import clash. Check it.
- In proportion to the profile (DEC-221): STANDARD, every KPI line's success and failure plus the key edge
  cases. No combinatorial expansion beyond what a KPI demands.
- Behaviour through public interfaces, never internals. Deterministic, no network. A case that waits for the
  name must fail as a failed case (red), not as a file that cannot be collected: the cases that are green today
  (the eight existing values, the five existing tests) must stay collectable and green before the implementation.
- A README that maps each KPI line to its tests and gives the expected red reason of each.
- Red first: run the tests with `python3 -m pytest tests/acceptance/W1-34 -q -p no:cacheprovider` (from the root
  of the repository, with no environment variable set) to the end; they fail for the reason the README states.
  Then run `python3 -m pytest tests -q -p no:cacheprovider` to the end and state its counts.
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options,
  impact, reversibility, cost, recommendation, confidence).

## Commit

Commit only your test paths, in one commit, with the trailers in the final block (DEC-182, DEC-476). Name no
decision id of another project's register in the subject:

    git commit -m "<subject>" --trailer "Task: ORION-im02" --trailer "Role: independent-test-designer" --trailer "Implements: MATH-SPEC-003" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After the commit run `git log -1 --format='%(trailers)'` and check that all four trailers are there; if one is
missing, amend your own commit (it is the unpushed tip) so that it carries them.

## Return

Your commit's hash; the test count; the KPI lines with their tests; the red reason as you saw it (how many red,
how many green, and why); the counts of the run of the whole of `tests/`; any package.

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
