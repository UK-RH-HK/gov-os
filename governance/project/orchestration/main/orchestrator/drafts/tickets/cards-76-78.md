#### W2-76 gov rebuild: per-stage timings, a 30-minute watchdog, one rebuild at a time on the machine (STANDARD, engineer; DEC-939 item 2; rows W2-M408, W2-L451)
- **Why:** a main-tree rebuild took 6 h 39 min on 2026-10-29, against 271 s alone, while a lead rebuilt its own stores. Its output timed only the lexical stage, so the cause could not be found (P1-MORNING-2026-10-29 item 2).
- **Starts:** in block A (DEC-941). Until it lands, every rebuild runs under `flock /tmp/gov-os-rebuild.lock`.
- **Allowed paths:** `src/gov/rebuild/**`, `tests/unit/rebuild/test_w2_76*`; acceptance tests in `tests/acceptance/W2-76/`.
- **KPIs, success:**
  - every stage timed in the output and the record;
  - past 30 minutes, a record of the stages done and of each process's state and wait channel, the rebuild flagged slow and going on;
  - one store rebuild at a time across every session on the machine, a waiting rebuild saying what it waits for;
  - a lock that cannot be taken never ignored;
  - the stores and digest unchanged.
- **KPIs, failure:**
  - two rebuilds at once;
  - a rebuild stopped by the watchdog;
  - a slow rebuild without a record.

#### W2-77 The nightly's clean-up removes only its own clone, by its exact path (FULL, engineer; DEC-939 item 5; row W2-M406)
- **Why:** `gov.close.nightly` ends with a repo-wide `git worktree prune`, so a worktree its process cannot see loses its registration and index (row W2-M406; W2-68's reviewer's F1, reproduced on a fixture). W2-68's batch reaches the nightly, so the batch stays off until this lands and is pinned (P-W2-68-PRUNE (b), DEC-939 item 5).
- **Starts:** first in block A (DEC-941). About 20 lines; FULL because a fault here loses work.
- **Allowed paths:** `src/gov/close/nightly.py` (the clean-up only), `tests/unit/close/test_nightly_cleanup*`; acceptance tests in `tests/acceptance/W2-77/`.
- **KPIs, success:**
  - only its own clone removed, by its exact path, with no repo-wide prune;
  - a hidden or unreadable worktree keeps its registration and index;
  - a failed removal touches only its own entry, or is reported;
  - everything else in the nightly unchanged.
- **KPIs, failure:**
  - any repo-wide prune left;
  - another worktree's registration or index lost.
- **After it:** the next re-pin carries it; the queue then switches to the batch, and the batch's gain is measured on this repository.

#### W2-78 Governance edits stop widening closes: the path map's lists in record files of their own; prompts and briefs record-only (STANDARD, engineer; DEC-941 item 5, P-SCOPE-RECORDS-1 (a))
- **Why:** a governance edit between closes turns the next close into a full run. W2-66's close of 10-27 ran full on records alone: 4,186 s of tests against about 300 s for the scoped closes after it (P-SCOPE-RECORDS-1 §2).
- **Starts:** in block A, after W2-77.
- **Allowed paths:** the judge's list readers (`src/gov/close/ratchet.py`, `history.py`, `gates.py`, `traceability.py`, `select.py`), `governance/project/records/**`, `governance/project/test-map.yaml` (its `record_only` and `record_reading` lists only), `template/governance/kernel/schemas/**`, `tests/unit/close/test_w2_78*`; acceptance tests in `tests/acceptance/W2-78/`.
- **KPIs, success:**
  - the four lists in record files of their own, unchanged entry for entry, read by the judge there;
  - their edits are record-only for the close, with every reader in the record-reading set;
  - prompts and briefs record-only, with their readers in the record-reading set;
  - the ratchet's rules unchanged;
  - the path map's configuration still shared core.
- **KPIs, failure:**
  - an entry lost in the move;
  - a reader missed;
  - a growing entry accepted without the owner's commit.
- **The migration** of entries the owner committed is the owner's commit (an ACT), validated with the pinned readers.
