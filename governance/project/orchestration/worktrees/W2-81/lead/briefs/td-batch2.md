# Batch 2 of 3: the judge and its mutation self-tests (W2-81, DAEO-l78m)

Your batch 1 is committed and checked. Every standing rule of your first brief still holds, word for word: the sandbox, Policy 2 (c) and (d), the guard's command forms, refused twice for the same call stop and say so, the disk share, row W2-L423's rule, `gov retrieve` from the integration branch's store only, the hooks check before your commit, the trailers, the twelve fields first. **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src` set **per command** (never in a session's `--settings` env).

## The lead's notes on batch 1

- **Checked:** commit `e1d40b68d3b2`, its trailers and `Implements:` ids are right; `gitleaks` finds 0 on the suite's files; the tripwire shows changes in this worktree only under `tests/acceptance/W2-81/`.
- **Your interpretation is confirmed:** "never tracked" means never tracked in *this* repository; the large files committed inside the built legacy repository are right (a repository with large files has them in its history; that is what adoption must class).
- **The whole-worktree "this repository unchanged" check:** under the close's parallel run, other suites run in this same tree at the same time, so a comparison of the whole worktree's `git status` can fail W2-81 for another suite's transient file (a false red blamed on this ticket). Keep the guarantee (no W2-81 case writes in this repository) but make the check attributable to this suite: for example, every path the builders, judge, scorer and runner write is resolved and refused when it lies inside this repository, and a case's own write targets are checked to lie outside it; compare the tree only where a W2-81 case could write, or fail only on a new path that is a W2-81 artefact. Do not weaken the guarantee.
- **The record forms you used were read by an Explore subagent whose line references you did not check:** before the judge relies on a record's place or field, read it yourself in `src/gov/adopt/` (and `git show w2/integrate:src/gov/adopt/<file>` for anything newer).
- **Retrieval:** your `gov retrieve` from `W2-00-store` failed in the sandbox (it reached for the network and timed out). Try it once more this batch, for one question; if it fails the same way, say so and read named files instead (refused twice for the same call: stop).
- **The secret in the adoption's outputs:** the judge's check that the value is in no output scans every file the adoption wrote in the built repository and beside it (records, proposals, packages, findings, logs, reports, and the index stores, SQLite and vector files read as bytes), not only a listed set; an output it cannot read rules nothing out, so the secret is then not FOUND_AND_HANDLED (fail closed).
- **NOT_BUILT versus MISSED:** a handling whose stage or capability is not built today (secret scanning, finding states and human gates, CAP-44.g; A7, A10 lite and the lite verdict, CAP-44.f and CAP-44.h) is NOT_BUILT, named with the capability; a handling whose stage is built but whose record does not show it is MISSED. State the rule and today's list in the README.

## The behaviour to build and test (the KPI lines are the authority)

**The judge.** Given one repository's manifest and an adoption's outputs on it (its stage records, path map, proposals, findings, verdict and index), it gives:
- each planted problem **FOUND_AND_HANDLED, MISSED or MISHANDLED**, with the evidence it read (which record, which field);
- each control **CLEAN or FLAGGED**;
- each stage a handling depends on that is **not built** (today A7 and A10 lite and the lite verdict, CAP-44.f and CAP-44.h, until W2-52; and anything else you find absent from the built code, such as CAP-44.g's finding states) **NOT_BUILT, named**, never passed;
- an overall verdict, **READY** only when every planted problem in every repository is FOUND_AND_HANDLED, no control is FLAGGED, no handling it needs is NOT_BUILT, and every question figure meets its floor (the scorer's two figures, built in batch 3: until then the judge takes them as an input, and a missing figure is not met); otherwise **NOT_READY**, naming each reason.
- **It fails closed:** a missing, unreadable or malformed record is MISSED, never handled; a stage not built is NOT_BUILT, never passed; a judge error (an exception, a manifest it cannot read) is an error result, never READY.

**The correct handling of each kind and the record that must show it** (KPI line 3; read the adoption stages as built in `src/gov/adopt/` for where each record lives and its fields):
- **stale spec:** classed historical, or drift flagged naming the newer source; **never cited as governing** (the stale spec cited as the governing source anywhere, such as a path map entry or a retrieval answer, is MISHANDLED);
- **superseded plan:** linked to its successor, out of default results, **never deleted** (deleted or moved away is MISHANDLED);
- **misleading name:** classed by its content and references (the live "old/draft/unused" file classed live; the dead "current" file classed not live); any rename **proposed** as a governed batch or ticket after the A5 review, **never moved by adoption on its own** (CAP-44.j): moved without a proposal reviewed at A5 is MISHANDLED;
- **orphaned test:** reported as a finding naming the test and its missing subject; **never deleted or silently skipped** (deleted, or skipped without a finding, is MISHANDLED);
- **secret:** found in history; reported with the path, a 12-digit commit and the rule only; **its value in no record, index store, log, proposal, report or output** (compare in memory, never print it: the value found anywhere is MISHANDLED even if it was also reported); a finding with a human gate stands (the rewrite or rotation is the owner's), and the verdict cannot be ADOPTED_HEALTHY while it is open (an ADOPTED_HEALTHY verdict with the secret's finding open is MISHANDLED);
- **legacy documents:** classed and extracted or retired as A8 states;
- **large files:** classed and kept out of the semantic index within the budget (a large file in the semantic index is MISHANDLED);
- **controls:** a control classed stale, historical, dead, legacy or superseded, proposed for a move or a retirement, or reported as a finding, is FLAGGED.

Where a stage the handling needs is built, the judge reads its real record form; where it is not built, the judge names NOT_BUILT. State in the README, for each kind, the handling, the record and field the judge reads, and which of those are NOT_BUILT today.

## Mutation self-tests (KPI line 8), as adoption's own mutation check

Build stand-in adoption outputs (records written in a temporary folder in the form the judge reads; no adoption runs):
- a stand-in that handles every planted problem and flags no control, with both figures at their floors or above, is **READY** (a stand-in for the not-built stages is allowed here, in the form you state in the README, so the READY path is tested; the judge on outputs with those stages absent says NOT_BUILT);
- **for every planted problem in every repository, a stand-in that misses exactly that one is NOT_READY naming it**: one killed mutant per planted problem, generated from the manifest (a parametrised case per planted problem id), each **listed in the README** by id;
- stand-ins that **mishandle**: the secret found but its value in a record (and, separately, in an index store and in a log or report); the misleading file moved, not proposed; the superseded plan deleted; the orphaned test deleted; the stale spec cited as governing; a large file in the semantic index; each is **NOT_READY** naming it (MISHANDLED);
- a stand-in that **flags a control** (each control, by the manifest) is NOT_READY naming it;
- fail closed: a missing record, an unreadable one (bad JSON or YAML, a binary), a malformed one (a field of the wrong type, a missing field) is MISSED, never handled; an absent stage is NOT_BUILT and named; a judge error (a manifest that cannot be read, an exception) is an error result whose verdict is not READY;
- a figure below its floor, or one figure missing, gives NOT_READY (the scorer's own stand-ins come in batch 3);
- the judge never prints or writes the secret's value: its evidence names path, 12-digit commit and rule only (check its whole output in memory).

The self-tests stay hermetic, under 120 s alone and fast under `-n auto`, none skipped. Run them to the end, plain and with `-n auto`, time both; run the collect-only check once and quote its last line; `gitleaks` on your suite's files, the finding count only. Update the README (each kind's handling and record; the mutants list; the KPI lines mapped to tests). Commit with your trailers (`Implements:` with the ids this batch implements, for example `DEC-936, DEC-941, DEC-911, CAP-44.b, CAP-44.e, CAP-44.g, CAP-44.h, CAP-44.j`, each checked to exist).

## Return

Your commit's 12-digit hash and trailers; files; test count and timings; collect-only line; gitleaks count; the mutants (count and ids); what is NOT_BUILT today and why; the judge's verdict on a no-output adoption (nothing run) for each repository; retrieval used; guard refusals; temp folder size; anything for batch 3.

Your last message has the twelve fields first, each as a labelled line, with any payload after them. Refused twice for the same call: stop and say so.

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
