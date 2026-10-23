# The re-pin plan (DEC-889 item 15, as amended by DEC-896 and DEC-897), for the owner's review

**Today's pin:** `fecb870c` (`~/.local/share/gov-os/pin-fecb870c/`). It predates W2-50's merge and W2-58. Every close is judged by it: `gov close`, `gov check` and the guard hooks. A fix on `w2/integrate` reaches a close only through a re-pin.

## The first re-pin

- **It carries:**
  - W2-58 (Policy 2);
  - W2-59 (the hooks and declared checks run from the pin);
  - W2-65 (hook lines fail closed);
  - W2-66 (scoped selection and evidence);
  - W2-07 (the close by ticket class; the commit gates first);
  - W2-69 (the secrets check reads what the stores hold).
- **Order of work before it:**
  1. **W2-66 and W2-07, built in parallel** (owner, DEC-899 item 2), each to its FULL or STANDARD ladder.
     - **W2-07 merges first.**
     - **Then W2-66** merges `w2/integrate` back, re-verifies, gets a fresh FULL probe on the merged head, and passes its fixture trial.
     - Both edit `src/gov/close/command.py`, so this order keeps a merge from invalidating the other's review.
  2. **W2-69** in a free slot, now that W2-50 is closing. Its tests decide the design question (DEC-897).
  3. **W2-65**, stacked on `w2/W2-59` (built in a free slot), after the P-IS-5 correction to its paths.
  4. **Just before the re-pin, W2-59 and W2-65 merge together.** Each first merges `w2/integrate` back with trailers and is re-verified (DEC-884). An earlier merge of either still needs a package first.
  5. `tools/probe_impact.py` after every merge (DEC-895). A FULL ticket whose probe went stale gets its fresh probe before the re-pin.
- **The owner's acts, in order** (one ACT ping, with the exact commands and their checks):
  0. **The pin's environment includes pytest-timeout 2.4.0** (the same wheel as the leads' install, DEC-892 b), so the close's per-test limit works under the pin.
  1. **The re-pin itself:** build the wheel at the merge commit that holds all six, install it under a new pin folder named for that commit (as `pin-fecb870c` is for today's), and point `~/.local/bin/gov` at it.
  2. **The settings regeneration** (DEC-884). If P-I1-2 is taken, it drops the `docs/source` read-deny rules, which protect a folder that left the tree on 2026-10-01.
  3. **A smoke run** of the pinned `gov check` and one guard decision, which I run and report.
- **What it changes for the closes:**
  - closes become scoped (W2-66);
  - decision-record commits count as measured (W2-07);
  - the commit gates refuse within minutes;
  - DEC-897 (b)'s re-run exception ends (W2-69).
  The merged-not-closed tickets close in the queue after it: W2-58, W2-63 (on W2-07's revision class), and any held this way. Under DEC-896 item 4, nothing closes before it unless gates (a) to (h) all predict a pass.
- **The interim skip guard (DEC-899 item 7)** expects a full regression with 31 skips. With scoped closes after the re-pin, it is restated before the first scoped close: a scoped close that runs W1-38 must show no rulesync skip, until W2-57 lands.
- **Rollback:** the old pin folder stays. Re-pointing `~/.local/bin/gov` at `pin-fecb870c` restores today's judge in one command.

## The second re-pin

- **It carries W2-68** (batching, reuse, the two fingerprints), after its FULL review and its trial (DEC-884 item 4), and whatever else has merged by then.
- **From it on,** queued closes run as batches, and a close on code that already passed reuses its run (DEC-883).

## What waits for which re-pin

| Waits for | Item |
|---|---|
| The first | W2-58's and W2-63's closes; the end of DEC-897 (b); scoped closes; the commit gates in `gov close` |
| The second | Batched closes; reuse; the store fresh by code fingerprint |
| Neither | The nightly full run (now, as a script); W2-57 (its close is judged by whichever pin is current); W2-67 (after W2-66 merges; closes after W2-07 is pinned) |
