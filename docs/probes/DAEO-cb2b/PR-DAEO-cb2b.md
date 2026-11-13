---
type: probe
task: DAEO-cb2b
reviewer_session: 6d107614-a263-414b-a451-cc4375a27ad3
implementer_session: fc61a27f-287b-45f6-b720-e04b2b215863
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: f1f950479641956af20df15f6d6a2d845deabf3d
decisions_applied: DEC-1007, DEC-1010, DEC-1014, DEC-998
---

# Probe record: W2-121 part a, round 2, the last (`gov dispatch tick` and `gov dispatch status`)

A fresh Independent Auditor session (`6d107614-a263-414b-a451-cc4375a27ad3`, claude-opus-5-5, effort high, read-only,
class C2) probed head `f1f950479641` and wrote nothing (`git status --porcelain` was empty and HEAD unchanged at the end).
This is round 2 of 2 (DEC-1010 item 1). Round 1 (`PR-DAEO-cb2b-round-1.md`, head `1ec89f0efdbb`) failed on S4 (F-1, F-2).

The fix round (the CTO's P-W2-121-7 (a)):
- The independent test designer (session `ee7c4828-8ca3-47a4-9a70-36dffb7e2694`) turned F-1 to F-5 into tests, as
  described behaviours: `5045148c8` and `db682531d`, merged by `696d32a93`.
- Engineer `fc61a27f-287b-45f6-b720-e04b2b215863` fixed F-1 to F-4 and F-6: `2f7ecb2a2`.
- Engineer `94d0d611-b8bc-447b-a4f7-f929091dc3e3`, given the one failing acceptance case only, fixed it: `f1f950479`.
  The failing case was a hand-planted inbox item, once deleted, being written again.

The findings are judged against ADR-0001's threat model (DEC-801).

## What was probed

- **Scope.** `git diff --name-only c6ca85d07 f1f950479641` lists only `src/gov/dispatch/**`, `tests/unit/dispatch/**`
  and `tests/acceptance/W2-121/**`. Only the test designer's two commits touch the acceptance tests.
- **S6 grep.** This repository's branches, paths and ids over `src/gov/dispatch/` find 0 lines.
- **Baseline.** `tests/acceptance/W2-121` and `tests/unit/dispatch`, run through heavy_slot.sh: 253 passed.
- **Round 1's findings, re-planted as behaviours:**
  - **F-1: fixed.** None of these is ever written again: a return read and then deleted; one deleted unread; a deleted
    never-ran item; a deleted owner item; an item planted by hand in `inbox/` or `inbox/read/` and then deleted.
  - **F-2: fixed.** Planted: a notifier that exits 1, with `notify_retry_s` 600.
    - It is not called again before the retry time.
    - Every pass shows a problem line naming the item and the failure, with `ok: true` and exit 0.
    - The line goes once the item is read.
    - Timeouts and a notifier that cannot be started are covered by tests that caught the planted mutations.
  - **F-3: fixed.** `notifier_command` is required at load (`config.py:128`).
  - **F-4: fixed.** Untracked and staged-only paths are unresolved. Ignored-and-present paths, committed paths, and
    paths committed then removed all resolve.
  - **F-5: fixed.** A gate shut for load or CPU, with ample memory, refuses every entry by the gate. The acceptance tests
    now catch the gate check's removal.
  - **F-6: fixed for a hung git**, which now writes `unchecked:`. A git that exits with an error is R2-2.
- **12 planted mutations, 12 caught.** Each fix has one mutation or more, run on a mirror under the sandbox's temporary
  folder. Two are caught by the unit tests only: a notifier timeout that does not end the pass's escalations, and
  `unchecked:` written as `unresolved:`.
- **Re-checked and still sound:**
  - the lock, and a losing pass that writes nothing;
  - OFF read before the lock;
  - the start recorded before the spawn;
  - one start per pass, in list order, with every skip named;
  - the room formula, with the gate's floor and working size;
  - S7's round count;
  - no watcher process;
  - the status written whole, a failed pass's `PASS FAILED` top line, and STALE after three minutes;
  - a crash between an item's write and its record, recovered on the next pass.

## What it found

**R2-1 (minor, S4): pass time grows with the square of the number of starts.**
- `state.py:142` re-reads the whole `items-written.txt` record for every start, in every pass.
- Planted: one pass took 0.24 s at 1,000 recorded starts, 2.0 s at 3,000, and 7.5 to 8.4 s at 6,000.
- Ordinary work: yes, over months of use. Consequence: other. Past about 15,000 to 20,000 starts a pass outlasts a
  minute and every other tick exits 4 at the lock, but the status still says STALE and never looks current.
- Smallest fix: read the record and `never-ran.txt` once per pass into a set.
- The lead checked the code at `f1f950479641` and confirms the per-call read.

**R2-2 (minor, S9): a git that exits with an error while resolving reads as "unresolved".**
- At `returns.py:324` and `:338`, a git that exits with an error (not a hang) while resolving names real ids and paths
  as `unresolved:`, where the fix round's reading says `unchecked:`.
- Planted: the worktree's `.git` link removed.
- Ordinary work: no. Consequence: other (a misleading item; nothing starts, nothing is lost).
- Smallest fix: a git exit code other than 0 or 1 raises `CommandFailed`.

Also noted, out of part a: nothing in `src/gov` writes the job history (`history.jsonl`). Until something does, a lead's
peak is the gate's working size.

## Judgement

**Pass.** Every KPI line of part a passes as probed (S1 to S10, and F1's start half). R2-1 and R2-2 are minor and do not
block: neither is a fail-open case, and neither loses work. They are recorded as residuals for a later ticket.

Not judged here: S1's installed host entry, and S6's switch-over. Both are the CTO's ACT at the last part's close
(P-W2-121-4 (a)).
