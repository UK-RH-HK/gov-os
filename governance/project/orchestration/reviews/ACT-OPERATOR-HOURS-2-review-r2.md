# Review: ACT-OPERATOR-HOURS-2, round 2 of 2 (manifest `7acf024359d6`)

task: DAEO-ktiw
decisions: [DEC-1136, DEC-1141, DEC-1104, DEC-1010, DEC-801, DEC-808, DEC-1014]
Reviewer: an independent auditor, read-only, fresh session, 2026-11-12. Worktree `3b6c5cb79d39`, clean. Sandbox check passed.

**Classification:** F1 in scope, ordinary work yes, loses work (blocks). F2 in scope, ordinary work yes, other (row). F3 in scope, ordinary work no, other (Wave 3 row).

## What I checked
1. **The `exempt` step: right, and it fails closed.**
   - On my own `--no-hardlinks` clone of `w2/integrate` (`4500e87e40bd`), I made commit 1 exactly as section 0 prints it (`296261fefd57`).
   - W1-01 then went **red: 1 failed, 53 passed, 12 deselected**, and the failure names only `296261fefd57`.
   - `exempt` added exactly the two lines at the end of `acceptance_exemptions` (numstat `2 0`, HEAD's full id, mode 644, no temporary file). A second run was a no-op.
   - Commit 2 as printed, then `exempt-verify`: exit 0. W1-01 then went **green: 54 passed, 12 deselected**.
   - On the chain's map (`d50884e3633e`) the result was the same.
   - Refusals that touched nothing: before commit 1; another commit on top; a wrong subject; a committed map that is neither before.
2. **Both befores:** `d50884e3633e` is the after in `ACT-PATHMAP-EXP-1/list.txt` and the hash of its frozen copy. The chain is consistent from `f4029cfb4942` to `d50884e3633e`. Section 0 item 5 states the order plainly.
3. **The undo:** see F1.
4. **Nothing else changed:**
   - `before/`, `after/`, `list.txt` and `keep.txt` are byte for byte round 1's.
   - The log's cases 1-100 are unchanged.
   - Every hash in the manifest and section 8 recomputed equal.
   - Class (O).
5. **Gate (h):** not a blocker. Both commits carry `Task: DAEO-sdxk`, a project ticket, so `_check_unmeasured` never asks `owner_listed` about them. W1-01 reads the entry by full id and decision shape only. The entry citing DEC-1141 is a fair reading.

## Findings
### F1: the undo's `git reset --keep HEAD~N` can drop a landed commit and leave the ACT's commit in place unlisted
- **What I did:** on a clone, I planted a commit on top of commit 1 (`exempt` refused, correctly), then followed section 5's "after the first commit, before the second" bullet: `git reset --keep HEAD~1`. Separately, with both ACT commits in place and a commit landed on top, I ran `git reset --keep HEAD~2`. This is the race between `exempt-verify` and the reset.
- **What happened:** both resets exited 0.
  - The landed commit was on no branch, and its changes were reset out of the working tree.
  - HEAD was left at the ACT's unlisted commit, so W1-01 is red. The HEAD~2 case also dropped the exemption commit.
  - The package's next steps (`apply.sh undo`, then `check` saying "ready") would report success over that state.
- **What should happen:** the undo checks before the reset that HEAD is the ACT's printed id, resets to that id's parent, and checks after the reset that `ORIG_HEAD` is the expected id (if not, `git reset --keep ORIG_HEAD` and tell the CTO). The CTO holds its commits and the merge queue during the undo.
- Ordinary work: yes, because the CTO and the merge queue commit to `w2/integrate` in the shared main tree every few minutes (183 first-parent commits since 11-11 00:00), and the HEAD~1 bullet has no check that HEAD is still the ACT's commit.
- Consequence: loses work.
- **What would reverse it:** proof that nothing commits to the main tree's `w2/integrate` during section 5, or a section 5 that checks the ids before and after the reset.

### F2: a commit landing between step 1 and step 2 leaves W1-01 red with no recovery step
- **Behaviour:** after commit 1, a CTO commit on top makes `exempt` refuse for good (reproduced). W1-01 stays red for every merge until a new ACT is built. The package only says "send its line to the CTO".
- **What should happen:** section 0 asks the CTO to hold its commits and the merge queue from step 1 until the owner sends both ids.
- Ordinary work: yes, because the CTO commits records in the main tree all day.
- Consequence: other (fails closed: a red that blocks landings, nothing lost).
- **What would reverse it:** proof that landings refuse while W1-01 is red, and that the CTO does not commit during an owner apply.

### F3: `exempt` does not check the `Task: DAEO-sdxk` trailer
- **Behaviour:** `exempt` accepts an ACT commit without a `Task:` trailer. Because DEC-1141 names no commit id, gate (h) does not list the commit, so the trailer is what keeps a later close from reading it as work without a task.
- Ordinary work: no, because the owner pastes the printed line, which carries the trailer.
- Consequence: other.
- **What would reverse it:** a close gate that does not depend on the `Task:` trailer for these commits.

## Probed and found sound
- `ex_insert` inserts only when the anchor appears once with a `decision:` line just before it.
- `ex_remove` removes only an exact two-line pair that appears once.
- `ex_verify` rebuilds the map byte for byte.
- The map's mode is kept and temporary files are cleaned up; refusals touch nothing.
- The clean-tree check is scoped to the map; commit 2 is limited to the map by `--`.
- The main tree's freeze gate is idle during an owner apply, and its landing check needs `Role: owner`, which both commits carry.

## Options for the owner (F1; round 2 of 2, DEC-1010)
- **(a) Recommended. Fix the text of the undo, then apply.** The CTO edits section 5 (explicit ids, a check before and after the reset, CTO holds commits and the merge queue) and adds one line to section 0 about holding commits, which also closes F2. The package is not in the manifest, so `yes ACT-OPERATOR-HOURS-2 7acf0243` still matches. Cost: about 10 minutes of the CTO's time.
- **(b) Apply as is, accepting F1 knowingly.** The forward path is verified, and F1 bites only if an undo is run while something commits. Cost: that risk remains if an undo is ever needed.
- **(c) Defer.** Give `apply.sh` an `undo-commits` step that only moves the branch if it is still at the expected id (an atomic compare-and-swap), and rebuild the bundle. Cost: a new sha8 and a build beyond the two-round cap.

Recommendation: (a).

```verdict
{"kpis": [{"kpi": "act-operator-hours-2", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "loses work"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}]}
```

## The CTO, 06:30: F1 and F2 fixed as text (option (a)): section 5 resets by id with checks before and after (ORIG_HEAD), the CTO holds during the apply and any undo; F3 a row. The bytes are unchanged (manifest 7acf0243).
