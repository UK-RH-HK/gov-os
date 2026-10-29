wbs_id: W2-77
title: 'The nightly''s clean-up removes only its own clone, by its exact path (row W2-M406)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/close/nightly.py
- tests/unit/close/test_nightly_cleanup*
kpis:
  success:
  - 'After its run, gov.close.nightly removes only its own clone, by its exact path (git worktree remove --force <that path>), and never runs a repo-wide git worktree prune [DEC-939 item 5, row W2-M406]'
  - 'A second worktree of the project whose folder is hidden or unreadable while the nightly runs (unmounted, permission-denied, moved and restored) keeps its registration and its staged index afterwards; the fixture that reproduced W2-68''s reviewer''s F1 now keeps them [DEC-939 item 5, P-W2-68-PRUNE]'
  - 'If the removal of its own clone fails, the nightly removes only that clone''s own administrative entry (by its exact name under the common git directory), or reports the failure in its record; it never touches another worktree''s entry [DEC-939 item 5, DEC-866]'
  - 'Everything else the nightly does is unchanged: its selection, its runs, its record and its verdict [DEC-915, DEC-890]'
  failure:
  - Any repo-wide prune left in the nightly; another worktree's registration or index lost; a clone's failed removal hidden.
profile: FULL
sources:
- DEC-939
- DEC-915
- DEC-890
- DEC-803
est_loc: 20
acceptance_tests:
  path: tests/acceptance/W2-77/
  author: independent-test-designer (MR-3); written before implementation
track: A
list_rows: [W2-M406]
---
# W2-77 The nightly's clean-up removes only its own clone, by its exact path

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-77), from P1-MORNING-2026-10-29 item 5 (owner, DEC-939 item 5: P-W2-68-PRUNE (b)).

- **Why:** `gov.close.nightly` ends with a repo-wide `git worktree prune` (`src/gov/close/nightly.py`, its `finally:` block). A worktree whose folder the nightly's process cannot see loses its registration and its index: row W2-M406, and W2-68's reviewer's F1 (reproduced on a fixture). W2-68's batch reaches the nightly, so the batch is switched on only after this fix lands and is pinned.
- **Place:** the next free slot (DEC-939 item 5). Small (about 20 lines); FULL because it is judge code whose fault loses work. One review.
- **After it:** the next re-pin carries it; then `close_queue.sh` switches to the batch, and the batch's gain is measured on this repository and reported (DEC-939 item 5).
