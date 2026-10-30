You are the ticket lead for ticket `DAEO-2ds6` (`W2-26`, "EXAMIN profile on the owner's copy (EXP-003's EXAMIN leg)"), profile STANDARD, class research, working only in the worktree `/home/usain/gov-os-worktrees/W2-26` on branch `w2/W2-26`.

**This is run 3: the merge-back (DEC-941 item 2), not a new round.** `git rev-parse --short=12 HEAD` must show `62c4e4778902`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- your run-2 checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md`;
- the ticket file (`.tickets/DAEO-2ds6.md`), the record `docs/research/EXP-003/examin/README.md`, and DEC-735, DEC-736 and DEC-941 (item 2).

## Why you start now

- **W2-26 is finished research,** held since 2026-10-16 only because it "closes after W2-07" (the card). W2-07 closed on 2026-10-29 (`a7376fa6`). The packages of run 2 are decided: P-1 and P-2 by DEC-735 (the indexing measure goes to W2-27; row W2-M357), and DEC-736 corrected DEC-735 item 2.
- **The owner's re-plan (DEC-941, 2026-10-29):** the nine held tickets are merged back, re-verified and closed, those in EXAMIN's minimum first; W2-26 is one of them (item 2). The re-plan puts W2-26 in block E. That block's work, the proving ground's real run and adoption (W2-27 to W2-30), comes after blocks B and C because it relies on memory and the launch path. This record relies on neither: it is evidence only, and it changes no code.
- **Where the branch stands:** 2 commits ahead of `w2/integrate` and 819 behind; merge base `af445b6f3562`. A dry merge (`git merge-tree --write-tree`) reports **no conflict**. The branch changes only `docs/research/EXP-003/examin/**` (12 files) and `docs/checkpoints/DAEO-2ds6/`. Nothing on `w2/integrate` touches either.

## The decisions for this run

1. **Merge `w2/integrate` into `w2/W2-26`** (`git merge --no-ff w2/integrate`, with `Task: DAEO-2ds6`, `Implements: DEC-941` and `Role: orchestrator` in the final trailer block). Never `-s ours`, never drop this ticket's side (DEC-750 item 3).
   - Any conflict: `git merge --abort`, and return PACKAGES naming each file.
   - After the merge, `grep -c '^### DEC-941' docs/DECISION_REGISTER.md` must show 1. If not, stop and return PACKAGES: the trailer gate would refuse every `Implements: DEC-941`.
   - `git diff --name-only w2/integrate HEAD` must list only `docs/research/EXP-003/examin/**` and `docs/checkpoints/DAEO-2ds6/**`. Anything else: stop and return PACKAGES.
2. **Rebuild** from this worktree's code (check `gov.__file__` first), under the machine's rebuild lock. Name every entry or record the load lists as `invalid`; `invalid: []` is expected. The record's 12 files enter the store and the indexes for the first time.
3. **Verification: the record in the merged tree, not a full run.** The merged head changes no code, test or configuration (step 1's check), so its suites are `w2/integrate`'s own; the close's regression is that run.
   - `gov check --json`: name every check that is not green, with its cause. A check made red or yellow by a file of the record is a red of this run.
     - Look hardest at the secrets-indexing check. The record quotes EXAMIN's full 40-hex head. Row W2-L423's gitleaks rule takes a 40-hex string beside a vendor keyword for a token, and W2-71's fix exempts only commits of this repository. If that check flags a file of the record, name the file and the line number only, never the match, and return PACKAGES: the change is a research worker's.
   - `pytest --collect-only -q` over `tests` (DEC-868).
   - `tests/unit`, and `tests/acceptance/W2-07/`: W2-07's gate judges a research ticket by its evidence record.
   - Check the record's front matter. It must say `type: research`, the form W2-07's evidence gate reads, and the record must be committed at HEAD.
   - **The nightly:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists, run no suite. Between 00:30 and 05:30, start no worker and no suite run (DEC-942 item 5). A close queue may be running in the main tree: run your suites only when the 1-minute load is under 20.
   - **Known:** W1-42's accepted reds, if a suite you run reaches them. Any other red is named with its cause.
4. **Repair: none in this run.** You write nothing under `docs/research/**`. If the record needs a change, return PACKAGES naming it.
5. **Reviews: none.** W2-26 is STANDARD: no reviewer before the merge (DEC-498), and no probe record exists to go stale (DEC-895 does not apply).
6. **Not this run's:**
   - DEC-827 moves research records to `experiments/EXP-00n/**`. The ticket's paths still name `docs/research/EXP-003/examin/**`, and the record stays there.
   - The owner's copy and `~/gov-os-workbench` are not read, listed or written. No clone is made.
   - The indexing KPI stays the named gap DEC-735 points to W2-27.
7. **Checkpoint:** `gov checkpoint` at the end (DEC-511), committed with this ticket's trailers.
8. **Your trailers** (LEAD-w2-common, DEC-927 item 2): run `trailer_gate.py` on your worktree before you return.
9. **Return** DONE (ready to merge into `w2/integrate`, then the close queue), or PACKAGES. Carry run 2's residuals in the return as they stand:
   - the folders under `/tmp/gov-os-W2-26/` (`examin`, `EXAMIN APP`, `runs`): name their size, and leave them for the orchestrator;
   - W2-M357;
   - Q-16.

**The park rule (DEC-941 item 2):** if the merge-back needs any change to the record, a conflict, or a fix outside the ticket's paths, stop and return PACKAGES naming the cost. Name what is left, its size in lines and hours, and what waits on it (W2-27's dependency on W2-26, and EXP-003's EXAMIN leg).

**Running beside you:**
- W2-03's lead holds `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**` and `src/gov/check/citations.py`.
- W2-05's lead holds the git-environment lines across `src/gov/**/*.py`, `src/gov/util/gitenv.py` and the lefthook files.
- W2-71 holds `src/gov/secrets/**` and `tests/unit/secrets_check/**`.
- W2-61 holds `src/gov/retrieval/measure.py`.
- W2-60a holds `src/gov/launch/launcher.py`, `role.py` and `record.py`.
- W2-77 holds `src/gov/close/nightly.py`.

Do not touch them. If a fix needs a change there, return PACKAGES.

**Estimate:** about 1.5 hours:
- the merge and the rebuild, about 30 minutes;
- `gov check`, the collection, `tests/unit` and W2-07's suite, about 40 minutes;
- the checkpoint and the return.

---
